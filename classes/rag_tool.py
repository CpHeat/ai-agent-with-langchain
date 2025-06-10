from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool

from classes.settings import Settings


class RagTool:

    _instance = None
    _rag_tool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings, retriever):
        if self._rag_tool is None:
            self._rag_tool = self._create_rag_tool(settings, retriever)
        return self._rag_tool

    def _get_qa_chain(self, model, retriever):
        return ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=retriever,
            return_source_documents=True
        )

    def _create_rag_tool(self, settings:Settings, retriever):
        qa_chain = self._get_qa_chain(settings.rag_model, retriever)

        chat_history = [
            SystemMessage(
                content="Tu es un assistant qui aide à trouver des informations concernant les droits disponibles en utilisant uniquement les documents qui te sont fournis.")
        ]

        def ask_rag(query: str) -> str:
            relevant_chunks = retriever.invoke(query)

            input_message = (
                    "Voici des documents qui vont t'aider à répondre à la question : "
                    + query
                    + "\n\nDocuments pertinents : \n"
                    + "\n\n".join([chunk.page_content for chunk in relevant_chunks])
                    + "\n\nDonne une réponse basée uniquement sur les documents qui te sont fournis."
            )

            # chat_history.append(HumanMessage(content=query))

            result = qa_chain.invoke({"question": input_message, "chat_history": chat_history})
            chat_history.append((query, result["answer"]))

            # print("chat_history:", chat_history)
            sources = result["source_documents"]

            for doc in sources:
                settings.params['debug_query'] = query
                settings.params['debug_log'].append({
                    "document_source": doc.metadata["source"],
                    "document_large_theme": doc.metadata["large_theme"],
                    "document_theme": doc.metadata["theme"],
                    "document_content": doc.page_content
                })

            return result["answer"]

        rag_tool = Tool(
            name="consult_droit",
            func=ask_rag,
            description="Répond à des questions sur les droits sociaux. Fournit des réponses fiables extraites de documents organisés par thème.",
            return_direct=True
        )

        return rag_tool

    @property
    def rag_tool(self):
        if self._rag_tool is None:
            raise RuntimeError("RAG tool not initialized. Call initialize) first.")
        return self._rag_tool