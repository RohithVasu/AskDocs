from loguru import logger
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.settings import settings
from app.core.qdrant import get_qdrant_client
from app.services.document_loader import UniversalDocumentLoader
from app.model_handlers.document_handler import DocumentHandler, DocumentUpdate
from app.core.db import get_global_db_session

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.data.chunk_size,
            chunk_overlap=settings.data.chunk_overlap
        )
        
        # Initialize embeddings model
        self.qdrant = get_qdrant_client()
        
        # Initialize document loader
        self.document_loader = UniversalDocumentLoader()
        
        # Create required directories
        os.makedirs(settings.data.documents_dir, exist_ok=True)

    def process_document(self, file_path: str, user_id: str, document_id: str):
        """Process a document and return its text chunks."""

        logger.info(f"Processing document: {file_path} for user: {user_id}")

        with next(get_global_db_session()) as db:
            collection_name = user_id
            document_handler = DocumentHandler(db)
            try:
                # Load document
                logger.info(f"Loading document: {file_path} for user: {user_id}")
                documents = self.document_loader.load(file_path)

                # Split into chunks
                text_chunks = self.text_splitter.split_documents(documents)

                # Add documents to qdrant
                self.qdrant.add_document(
                    text_chunks=text_chunks,
                    collection_name=collection_name,
                    file_path=file_path
                )

                # Create document record
                document_handler.update(document_id, DocumentUpdate(
                    status="completed"
                ))
                
            except Exception as e:
                logger.error(f"Error processing document {file_path}: {str(e)}")
                document_handler.update(document_id, DocumentUpdate(
                    status="failed",
                    error_message=str(e)
                ))
                raise