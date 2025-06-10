import os
import subprocess
import sys
from turtle import st

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama, OllamaEmbeddings

from functions.interface import interface
from settings import retriever_params
from functions.data.get_vectorstore import get_vectorstore
from functions.tools.get_rag_tool import get_rag_tool


def app():
    st.title("Ma super app Streamlit")
    st.write("Bienvenue !")

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