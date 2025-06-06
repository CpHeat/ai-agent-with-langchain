import os

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from settings import vectorizing_params


def get_vectorstore(embedder) -> Chroma:

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

                    # Extract themes and subthemes from the file structure
                    relative_path = os.path.relpath(file_path, "data")
                    parts = relative_path.split(os.sep)
                    large_theme = parts[0]
                    theme = parts[1]
                    subtheme = parts[2].replace(".txt", "")

                    # Chunk splitting
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
        
        print(f"Vectorstore created with {len(documents)} chunks.")
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
        print(f"Vectorstore retrieved.")
    
    return vectorstore