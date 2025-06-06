import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama, OllamaEmbeddings

from functions.interface import interface
from settings import retriever_params
from functions.data.get_vectorstore import get_vectorstore
from functions.tools.get_rag_tool import get_rag_tool


if __name__ == "__main__":
    load_dotenv(override=True)

    model = ChatOllama(model="llama3.2", temperature=0)
    #model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

    # Modèle spécialisé pour convertir du texte en vecteurs (https://ollama.com/library/nomic-embed-text).
    # Il existe d'autres modèles d'embeddings (comme "all-MiniLM-L6-v2", "text-embedding-ada-002", etc.)
    # avec des performances et dimensions variées selon les cas d’usage (recherche sémantique, classification, etc.).
    embedder = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = get_vectorstore(embedder)

    retriever = vectorstore.as_retriever(
        search_type=retriever_params['search_type'],
        search_kwargs=retriever_params['search_kwargs']
    )

    rag_tool = get_rag_tool(model, retriever)

    tools=[
        rag_tool
    ]

    interface(model, tools)




    # executor = get_executor(model, tools)




    # while True:
    #     user_input = input("Vous : ")
    #     clear_output(wait=True)                         # Efface l'affichage précédent
    #     display(Markdown(f"**Vous :** {user_input}"))   # Affiche la requête de l'utilisateur
    #
    #     if user_input.lower() in ["stop", "exit", "quit"]:
    #         print("Fin de la conversation.")
    #         break
    #
    #     response = executor.invoke({"input": user_input})
    #     display(Markdown(response["output"]))