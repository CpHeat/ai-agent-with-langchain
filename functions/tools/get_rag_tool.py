from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import Tool


def get_rag_tool(model, retriever) -> Tool:

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        return_source_documents=True
    )

    chat_history = [
        SystemMessage(content="Tu es un assistant qui aide à trouver des informations concernant les droits disponibles en utilisant les documents qui lui sont fournis.")
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

        #chat_history.append(HumanMessage(content=query))

        result = qa_chain.invoke({"question": input_message, "chat_history": chat_history})
        chat_history.append((query, result["answer"]))

        print("chat_history:", chat_history)
        sources = result["source_documents"]

        for doc in sources:
            print(doc.metadata["source"])
        return result["answer"]

    rag_tool = Tool(
        name="consult_droit",
        func=ask_rag,
        description="Répond à des questions sur les droits sociaux. Fournit des réponses fiables extraites de documents organisés par thème.",
        return_direct=True
    )

    return rag_tool