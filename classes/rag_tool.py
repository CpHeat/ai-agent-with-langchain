from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool
import streamlit as st

from classes.settings import Settings
from classes.vectorstore_manager import VectorstoreManager


class RagTool:

    def __init__(self, settings:Settings, vectorstore_manager:VectorstoreManager, tool_prompt:str, retriever_filter:dict, name:str, description:str):
        self._name = name
        self._description = description
        self._prompt = tool_prompt
        self._filter = retriever_filter

        self._rag_tool = self._create_rag_tool(vectorstore_manager, settings)

    def _get_qa_chain(self, model, retriever):
        return ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=retriever,
            return_source_documents=True
        )

    def _create_rag_tool(self, vectorstore_manager:VectorstoreManager, settings:Settings):
        retriever = vectorstore_manager.get_retriever(settings, self._filter)

        qa_chain = self._get_qa_chain(settings.rag_model, retriever)
        chat_history = [
            SystemMessage(
                content=self._prompt)
        ]

        def ask_rag(query: str) -> str:

            if 'debug_used_tool' not in st.session_state:
                st.session_state.debug_used_tool = None
            if 'debug_log' not in st.session_state:
                st.session_state.debug_log = []
            if 'debug_query' not in st.session_state:
                st.session_state.debug_query = None

            st.session_state.debug_used_tool = f"Tool used: {self._name}"
            st.session_state.debug_query = query

            relevant_chunks = retriever.invoke(query)
            input_message = (
                    "Voici des documents qui vont t'aider à répondre à la question : "
                    + query
                    + "\n\nDocuments pertinents : \n"
                    + "\n\n".join([chunk.page_content for chunk in relevant_chunks])
                    + "\n\nDonne une réponse basée uniquement sur les documents qui te sont fournis."
            )

            result = qa_chain.invoke({"question": input_message, "chat_history": chat_history})
            chat_history.append((query, result["answer"]))

            sources = result["source_documents"]
            for doc in sources:
                st.session_state.debug_log.append({
                    "document_source": doc.metadata["source"],
                    "document_large_theme": doc.metadata["large_theme"],
                    "document_theme": doc.metadata["theme"],
                    "document_content": doc.page_content
                })

            return result["answer"]

        rag_tool = Tool(
            name=self._name,
            func=ask_rag,
            description=self._description,
            return_direct=True
        )

        return rag_tool

    @property
    def rag_tool(self):
        return self._rag_tool