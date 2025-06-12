import os

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from classes.settings import Settings


class VectorstoreManager:
    """
    Singleton class that manages the vectorstore.

    Handles the vectorstore and retrievers creation.

    Methods
    -------
    initialize(settings)
        Initializes the vectorstore creation/recuperation.
    """
    _instance = None
    _vectorstore = None
    _settings:Settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings):
        """
        Creates or gets the existing vectorstore.

        Parameters
        ----------
        settings: Settings
            The configuration object for the application.

        Returns
        -------
        self
        """
        self._settings = settings
        if self._vectorstore is None:
            self._vectorstore = self._create_vectorstore()
        return self

    def _create_vectorstore(self) -> Chroma:
        """ Creates the vectorstore if not existing or retrieves the one already present. """
        current_dir = os.getcwd()
        data_dir = os.path.join(current_dir, "data")
        db_dir = os.path.join(current_dir, "db")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.vectorizing_params['chunk_size'],
            chunk_overlap=self._settings.vectorizing_params['chunk_overlap']
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
                embedding=self._settings.embedder,
                collection_name="droits",
                persist_directory=db_dir
            )
        else:
            vectorstore = Chroma(
                persist_directory=db_dir,
                embedding_function=self._settings.embedder,
                collection_name="droits"
            )
            print(f"Vectorstore retrieved.")
        return vectorstore

    def get_retriever(self, settings, retriever_filter: dict = None) -> VectorStoreRetriever:
        """ Creates a retriever

        Parameters
        ----------
        settings: Settings
            The configuration object for the application.
        retriever_filter: dict
            The filter for retrieving documents (optional).

        Returns
        -------
        retriever: VectorStoreRetriever
            The retriever to handle data from the vectorstore
        """
        search_kwargs = settings.retriever_params['search_kwargs']
        if retriever_filter:
            search_kwargs['filter'] = retriever_filter

        if self._vectorstore is None:
            raise RuntimeError("Retriever not initialized. Call initialize() first.")
        return self._vectorstore.as_retriever(
            search_type=settings.retriever_params['search_type'],
            search_kwargs=search_kwargs
        )

    @property
    def vectorstore(self) -> Chroma:
        """
        Property to access the vectorstore.

        Returns
        -------
        A Chroma object
        """
        if self._vectorstore is None:
            raise RuntimeError("VectorstoreManager not initialized. Call initialize() first.")
        return self._vectorstore