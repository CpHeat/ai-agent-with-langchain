import os

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub

from settings import vectorizing_params, retriever_params

load_dotenv(override=True)

model = ChatOllama(model="llama3.2", temperature=0)
embedder = OllamaEmbeddings(model="nomic-embed-text")

current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "data")
db_dir = os.path.join(current_dir, "db")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=vectorizing_params['chunk_size'],
    chunk_overlap=vectorizing_params['chunk_overlap']
)

documents = []

if not os.path.exists(db_dir):
    print("Initializing vector store...")

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    full_text = f.read()

                parts = os.path.relpath(file_path, data_dir).split(os.sep)
                large_theme = parts[0] if len(parts) > 0 else "unknown"
                theme = parts[1] if len(parts) > 1 else "unknown"
                subtheme = parts[2].replace(".txt", "") if len(parts) > 2 else "unknown"

                chunks = text_splitter.split_text(full_text)
                for i, chunk in enumerate(chunks):
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "large_theme": large_theme,
                                "theme": theme,
                                "subtheme": subtheme,
                                "chunk_id": i,
                                "source": file_path
                            }
                        )
                    )

    vectorstore = Chroma.from_documents(
        documents,
        embedding=embedder,
        collection_name="droits",
        persist_directory=db_dir
    )
    print(f"Vectorstore initialized with {len(documents)} chunks.")
else:
    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=embedder,
        collection_name="droits"
    )
    print("Vectorstore loaded from disk.")

retriever = vectorstore.as_retriever(
    search_type=retriever_params['search_type'],
    search_kwargs=retriever_params['search_kwargs']
)

qa_chain = ConversationalRetrievalChain.from_llm(llm=model, retriever=retriever)

def ask_rag(inputs) -> str:
    if isinstance(inputs, str):
        query = inputs
        chat_history = []
    elif isinstance(inputs, dict):
        query = inputs.get("input", "")
        chat_history = inputs.get("chat_history", []) or []
    else:
        return "❌ Format de requête non pris en charge."

    result = qa_chain({
        "question": query,
        "chat_history": chat_history
    })

    if isinstance(result, dict):
        return result.get("answer", "Aucune réponse trouvée.")
    return str(result)

rag_tool = Tool(
    name="consult_droit",
    func=ask_rag,
    description="Répond à des questions sur les droits sociaux (APL, RSA, etc.). Fournit des réponses fiables extraites de documents organisés par thème."
)

tools = [rag_tool]

def initialize_agent(model, tools):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    prompt = hub.pull("hwchase17/react-chat")

    agent = create_react_agent(
        llm=model,
        tools=tools,
        prompt=prompt,
        stop_sequence=True
    )

    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    return executor

executor = initialize_agent(model, tools)

if __name__ == "__main__":
    from IPython.display import display, Markdown, clear_output
    while True:
        user_input = input("Vous : ")
        clear_output(wait=True)
        display(Markdown(f"**Vous :** {user_input}"))

        if user_input.lower() in ["stop", "exit", "quit"]:
            print("Fin de la conversation.")
            break

        response = executor.invoke({"input": user_input, "chat_history": []})
        display(Markdown(response["output"]))
