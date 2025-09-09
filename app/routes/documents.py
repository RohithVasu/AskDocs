from loguru import logger
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from pathlib import Path
from sqlalchemy.orm import Session
import os

from app.routes import AppResponse
from app.routes.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.core.settings import settings
from app.model_handlers.document_handler import DocumentHandler, DocumentUpdate
from app.model_handlers.user_handler import UserResponse
from app.core.db import get_global_db_session
from app.core.redis import task_queue


document_router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize services
document_processor = DocumentProcessor()
db_session = get_global_db_session()
document_handler = DocumentHandler(db_session)

@document_router.post("/upload", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: UserResponse = Depends(get_current_user),
):
    """Upload and process a document."""
    logger.info(f"Processing document: {file.filename} for user: {user.id}")

    start_time = datetime.now()
    # Save uploaded file
    file_path = os.path.join(
        settings.data.documents_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process document
    job = task_queue.enqueue(document_processor.process_document, file_path, user.id, db)
    
    time_taken = datetime.now() - start_time

    return AppResponse(
        status="success",
        message="Document queued for processing",
        data={
            "collection_name": user.id + "_" + Path(file_path).stem,
            "redis_job_id": job.id,
            "time_taken": str(time_taken.total_seconds()) + " seconds"
        }
    )

@document_router.get("/{document_id}", response_model=AppResponse)
async def get_document(document_id: str):
    """Get document details by ID."""
    try:
        document = document_handler.read(document_id)
        return AppResponse(
            status="success",
            message="Document fetched successfully",
            data=document
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@document_router.put("/{document_id}", response_model=AppResponse)
async def update_document(document_id: str, document_update: DocumentUpdate):
    """Update document details."""
    try:
        updated_document = document_handler.update(document_id, document_update)
        return AppResponse(
            status="success",
            message="Document updated successfully",
            data=updated_document
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@document_router.delete("/{document_id}", response_model=AppResponse)
async def delete_document(document_id: str):
    """Delete document by ID."""
    try:
        document_handler.delete(document_id)
        return AppResponse(
            status="success",
            message="Document deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@document_router.get("/user/{user_id}", response_model=AppResponse)
async def get_documents_by_user(user_id: str, skip: int = 0, limit: int = 20):
    """Get all documents for a user."""
    try:
        documents = document_handler.get_by_user(user_id, skip, limit)
        return AppResponse(
            status="success",
            message="Documents fetched successfully",
            data=documents
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching documents: {str(e)}")

@document_router.get("/folder/{folder_id}", response_model=AppResponse)
async def get_documents_by_folder(folder_id: str):
    """Get all documents in a folder."""
    try:
        documents = document_handler.get_by_folder(folder_id)
        return AppResponse(
            status="success",
            message="Documents fetched successfully",
            data=documents
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Folder not found: {str(e)}")