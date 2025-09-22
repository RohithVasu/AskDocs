from loguru import logger
import os
from typing import List
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client.http import models
from sqlalchemy.orm import Session
import uuid

from app.core.settings import settings
from app.core.qdrant import Qdrant
from app.services.document_loader import UniversalDocumentLoader
from app.model_handlers.document_handler import DocumentHandler, DocumentCreate
from app.core.db import get_global_db_session

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.data.chunk_size,
            chunk_overlap=settings.data.chunk_overlap
        )
        
        # Initialize embeddings model
        self.qdrant = Qdrant()
        
        # Initialize document loader
        self.document_loader = UniversalDocumentLoader()
        
        # Create required directories
        os.makedirs(settings.data.documents_dir, exist_ok=True)

    def process_document(self, file_path: str, user_id: str):
        """Process a document and return its text chunks."""

        with next(get_global_db_session()) as db:
            collection_name = str(user_id) + "_" + str(Path(file_path).stem)
            document_handler = DocumentHandler(db)
            try:
                # Load document
                logger.info(f"Loading document: {file_path} for user: {user_id}")
                documents = self.document_loader.load(file_path)

                # Split into chunks
                text_chunks = self.text_splitter.split_documents(documents)

                # Prepare points for Qdrant
                points = []
                for chunk in text_chunks:
                    payload = {
                        **chunk.metadata,         
                        "source": Path(file_path).name,
                        "page_content": chunk.page_content
                    }

                    embedding = self.qdrant._get_embedding(chunk.page_content)

                    points.append(
                        models.PointStruct(
                            id=str(uuid.uuid4()),
                            vector=embedding,
                            payload=payload
                        )
                    )


                # Don’t upsert if nothing was generated
                if not points:
                    logger.warning(f"No points generated for {file_path}, skipping Qdrant upsert")
                    return

                # Bulk insert for speed
                self.qdrant._ensure_collection(collection_name)
                self.qdrant.client.upsert(
                    collection_name=collection_name,
                    points=points
                )

                logger.info(f"Upserted {len(points)} points for {file_path}")

                # Create document record
                document_handler.create(DocumentCreate(
                    user_id=str(user_id),
                    filename=Path(file_path).name,
                    file_path=file_path,
                    vector_collection=collection_name
                ))
                
            except Exception as e:
                logger.error(f"Error processing document {file_path}: {str(e)}")
                raise