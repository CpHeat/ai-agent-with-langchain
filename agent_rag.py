import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_deepseek import ChatDeepSeek
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import ConversationalRetrievalChain
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from settings import vectorizing_params, retriever_params

load_dotenv(override=True)

# Choisir ton modèle ici :
model = ChatOllama(model="llama3.2", temperature=0)
# model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

# Embeddings pour le vectorstore
embedder = OllamaEmbeddings(model="nomic-embed-text")

# Chargement des documents
current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "data")
db_dir = os.path.join(current_dir, "db")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=vectorizing_params['chunk_size'],
    chunk_overlap=vectorizing_params['chunk_overlap']
)

documents = []

if not os.path.exists(db_dir):
    print("📦 Initialisation du vectorstore...")

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    full_text = f.read()

                relative_path = os.path.relpath(file_path, data_dir)
                parts = relative_path.split(os.sep)
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
else:
    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=embedder,
        collection_name="droits"
    )

print(f"✅ Vectorstore prêt ({len(documents)} chunks indexés)" if documents else "✅ Vectorstore chargé.")

# Créer le retriever
retriever = vectorstore.as_retriever(
    search_type=retriever_params['search_type'],
    search_kwargs=retriever_params['search_kwargs']
)

# Chaîne RAG
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    retriever=retriever
)

# Fonction utilisée par l'outil RAG
def ask_rag(inputs) -> str:
    if isinstance(inputs, str):
        query = inputs
        chat_history = []
    elif isinstance(inputs, dict):
        query = inputs.get("input", "")
        chat_history_raw = inputs.get("chat_history", []) or []
        # Convertir liste de tuples [(q,a), ...] en format attendu [(q, a), ...] ou string si nécessaire
        chat_history = [(str(q), str(a)) for q, a in chat_history_raw]
    else:
        return "❌ Format de requête non pris en charge."

    result = qa_chain({
        "question": query,
        "chat_history": chat_history
    })

    if isinstance(result, dict):
        return result.get("answer", "Aucune réponse trouvée.")
    return str(result)


# Outil RAG pour l'agent
rag_tool = Tool(
    name="consult_droit",
    func=ask_rag,
    description="🔎 Répond à des questions sur les aides sociales et droits en s'appuyant sur les documents officiels (APL, RSA, etc.)."
)

# Autres outils personnalisés si tu veux en ajouter
def data_right_disability(query):
    return "Voici les droits pour les personnes en situation de handicap."

def data_right_child(query):
    return "Voici les aides pour les enfants et familles."

def data_right_accommodation(query):
    return "Voici les aides liées au logement."

# Outil fallback si rien ne correspond
def error_handle_message(query):
    return "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?"

# Regroupe tous les outils
tools = [
    rag_tool,
    Tool(name="right_disability", func=data_right_disability, description="Infos sur les droits handicap"),
    Tool(name="right_child", func=data_right_child, description="Infos sur les aides enfants/familles"),
    Tool(name="right_accommodation", func=data_right_accommodation, description="Aides au logement"),
    Tool(name="generate_message", func=error_handle_message, description="Message d'erreur par défaut")
]

# Création de l'agent avec mémoire et prompt
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

# Utilisation possible en mode CLI
if __name__ == "__main__":
    from IPython.display import display, Markdown, clear_output

    while True:
        user_input = input("Vous : ")
        if user_input.lower() in ["stop", "exit", "quit"]:
            print("Fin de la conversation.")
            break

        clear_output(wait=True)
        display(Markdown(f"**Vous :** {user_input}"))
        response = executor.invoke({"input": user_input})
        display(Markdown(f"**Réponse :** {response['output']}"))
