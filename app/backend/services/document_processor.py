from loguru import logger
import os
from typing import List
from pathlib import Path

from langchain_community.document_loaders import (
    CSVLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.backend.core.settings import settings

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.data.chunk_size,
            chunk_overlap=settings.data.chunk_overlap
        )
        
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create required directories
        os.makedirs(settings.data.vector_store_dir, exist_ok=True)
        os.makedirs(settings.data.documents_dir, exist_ok=True)

    def process_document(self, file_path: str) -> List[Document]:
        """Process a document and return its text chunks."""
        # Get file extension
        file_extension = Path(file_path).suffix.lower()
        
        # Check if we support this file type
        if file_extension not in settings.data.supported_file_types:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Load document
        loader = self._get_loader(file_extension, file_path)
        documents = loader.load()
        
        # Split into chunks
        documents_split = self.text_splitter.transform_documents(documents)
        return documents_split

    def create_vector_store(self, documents: List[Document], file_name: str) -> str:
        """Create a vector store for the document."""
        # Clean the file name to create a valid collection name
        collection_name = f"doc_{file_name.lower().replace(' ', '_').replace('.', '_')}"
        collection_name = collection_name[:50]
        
        logger.debug(f"Creating vector store with collection name: {collection_name}")
        
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.data.vector_store_dir
        )
        
        # Add texts to the vector store
        vector_store.add_documents(documents)

        return collection_name
        

    def _get_loader(self, file_extension: str, file_path: str):
        """Get appropriate document loader based on file type."""
        loaders = {
            ".docx": lambda: UnstructuredWordDocumentLoader(file_path),
            ".csv": lambda: CSVLoader(file_path),
            ".pdf": lambda: PyPDFLoader(file_path),
            ".pptx": lambda: UnstructuredPowerPointLoader(file_path),
            ".ppt": lambda: UnstructuredPowerPointLoader(file_path),
            ".txt": lambda: TextLoader(file_path),
            ".md": lambda: TextLoader(file_path)
        }
        return loaders[file_extension]()
