import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama, OllamaEmbeddings


load_dotenv(override=True)


# model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
# rag_model = ChatOllama(model="llama3", temperature=0)
tool_model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
agent_model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
# Modèle spécialisé pour convertir du texte en vecteurs (https://ollama.com/library/nomic-embed-text).
# Il existe d'autres modèles d'embeddings (comme "all-MiniLM-L6-v2", "text-embedding-ada-002", etc.)
# avec des performances et dimensions variées selon les cas d’usage (recherche sémantique, classification, etc.).
embedder = OllamaEmbeddings(model="nomic-embed-text")

# General parameters
params = {
    'debug': True,
    'debug_log': [],
    'debug_query': ''
}
# data vectorizing parameters
vectorizing_params = {
    'chunk_size': 1000,
    'chunk_overlap': 0
}
# Retriever parameters
"""
search_type can be similarity, mmr or similarity_threshold
if search_type == similarity, search_kwargs must be like {
    'k': 10 (how many documents tu return)
}
if search_type == mmr, search_kwargs must be like {
    "k": 10, (how many documents to actually return)
    "fetch_k": 20, (how many documents should the search considerate)
    "lambda_mult": 0.5 (ponderation between diversity and similarity, 0 = max diversity, 1 = max similarity)
}
if search_type == similarity_threshold, search_kwargs must be like {
    "score_threshold": 0.8, (minimum threshold of similarity (between 0 and 1)
    "k": 10 (maximum documents number to actually return - optional)
}
optional paramater : "filter" to filter chunks using metadata:
{
    'k': 10 (how many documents tu return),
    "filter": {
        "source": "my-file.txt"
    }
}
"""
retriever_params = {
    'search_type': 'similarity',
    'search_kwargs': {
        "k": 10
    }
}