from loguru import logger
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pathlib import Path
from rq import Queue, Retry
from redis import Redis
import os

from app.routes import AppResponse
from app.routes.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.core.settings import settings
from app.model_handlers.document_handler import DocumentHandler, DocumentUpdate
from app.model_handlers.user_handler import UserResponse
from app.core.db import get_global_db_session

document_router = APIRouter(prefix="/documents", tags=["documents"])

redis_conn = Redis(host=settings.redis.host, port=settings.redis.port)
queue = Queue(connection=redis_conn)

def process_document_task(file_path: str, user_id: str):
    processor = DocumentProcessor()
    return processor.process_document(file_path, user_id)


@document_router.post("/", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload and process a document."""
    logger.info(f"Processing document: {file.filename} for user: {current_user.id}")

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
    document_job = queue.enqueue(
        process_document_task,
        args=(file_path, current_user.id),
        retry=Retry(max=3, interval=[10, 30, 60])
    )

    time_taken = datetime.now() - start_time

    return AppResponse(
        status="success",
        message="Document queued for processing",
        data={
            "collection_name": str(current_user.id) + "_" + str(Path(file_path).stem),
            "job_id": document_job.id,
            "time_taken": str(time_taken.total_seconds()) + " seconds"
        }
    )

@document_router.get("/", response_model=AppResponse)
async def get_documents_by_user(
    current_user: UserResponse = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_global_db_session)
):
    """Get all documents for a user."""
    try:
        document_handler = DocumentHandler(db)
        documents = document_handler.get_by_user(current_user.id, skip, limit)
        return AppResponse(
            status="success",
            message="Documents fetched successfully",
            data=documents
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching documents: {str(e)}")
    

@document_router.get("/{document_id}", response_model=AppResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Get document details by ID."""
    try:
        document_handler = DocumentHandler(db)
        document = document_handler.read(document_id)
        return AppResponse(
            status="success",
            message="Document fetched successfully",
            data=document
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@document_router.patch("/{document_id}", response_model=AppResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_global_db_session)
):
    """Update document details."""
    try:
        document_handler = DocumentHandler(db)
        updated_document = document_handler.update(document_id, document_update)
        return AppResponse(
            status="success",
            message="Document updated successfully",
            data=updated_document
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@document_router.delete("/{document_id}", response_model=AppResponse)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Delete document by ID."""
    try:
        document_handler = DocumentHandler(db)
        document_handler.delete(document_id)
        return AppResponse(
            status="success",
            message="Document deleted successfully",
            data={}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")


@document_router.get("/folder/{folder_id}", response_model=AppResponse)
async def get_documents_by_folder(
    folder_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Get all documents in a folder."""
    try:
        document_handler = DocumentHandler(db)
        documents = document_handler.get_by_folder(folder_id)
        return AppResponse(
            status="success",
            message="Documents fetched successfully",
            data=documents
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Folder not found: {str(e)}")