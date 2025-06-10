from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama, OllamaEmbeddings

from functions.interface import interface
from settings import retriever_params, embedder, tool_model, agent_model
from functions.data.get_vectorstore import get_vectorstore
from functions.tools.get_rag_tool import get_rag_tool


if __name__ == "__main__":

    vectorstore = get_vectorstore(embedder)

    retriever = vectorstore.as_retriever(
        search_type=retriever_params['search_type'],
        search_kwargs=retriever_params['search_kwargs']
    )

    rag_tool = get_rag_tool(tool_model, retriever)

    tools=[
        rag_tool
    ]

    interface(agent_model, tools)