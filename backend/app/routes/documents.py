from loguru import logger
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from rq import Retry
import os
from typing import List
import aiofiles

from app.routes import AppResponse
from app.dependencies.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.core.settings import settings
from app.core.qdrant import get_qdrant_client
from app.model_handlers.document_handler import DocumentCreate, DocumentHandler, DocumentUpdate
from app.model_handlers.user_handler import UserResponse
from app.core.db import get_global_db_session
from app.core.redis import queue

document_router = APIRouter(prefix="/documents", tags=["documents"])

def process_document_task(file_path: str, user_id: str, document_id: str):
    processor = DocumentProcessor()
    return processor.process_document(file_path, user_id, document_id)

def delete_document_task(doc_name: str, collection_name: str):
    qdrant_client = get_qdrant_client()
    return qdrant_client.delete_document(doc_name, collection_name)


@document_router.post("/", response_model=AppResponse)
async def upload_document(
    files: List[UploadFile] = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """
    Upload one or more documents.
    Unsupported formats are skipped.
    Files are queued for background processing.
    """
    supported_formats = settings.data.supported_file_types
    skipped_files, processed_jobs = [], []

    start_time = datetime.now()
    user_dir = os.path.join(settings.data.documents_dir, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    document_handler = DocumentHandler(db)

    for file in files:
        try:
            extension = file.filename.split(".")[-1].lower()
            if extension not in supported_formats:
                skipped_files.append(file.filename)
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue

            file_path = os.path.join(user_dir, file.filename)

            async with aiofiles.open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    await buffer.write(chunk)

            # Attempt to create document record
            try:
                document = document_handler.create(DocumentCreate(
                    user_id=str(current_user.id),
                    filename=file.filename,
                    file_path=file_path,
                    vector_collection=str(current_user.id),
                    status="processing",
                ))
            except IntegrityError as e:
                db.rollback()  # rollback the session
                if "unique_filename_per_user" in str(e.orig):
                    logger.warning(f"Duplicate document upload: {file.filename}")
                    return AppResponse(
                        status="error",
                        message="A document with same name already exists for this user.",
                        data={"filename": file.filename},
                    )
                raise  # re-raise other DB errors

            # Enqueue background job
            document_job = queue.enqueue(
                process_document_task,
                args=(file_path, current_user.id, document.id),
                retry=Retry(max=3, interval=[10, 30, 60]),
            )

            document_handler.update(document.id, DocumentUpdate(job_id=document_job.id))

            processed_jobs.append({
                "file": file.filename,
                "job_id": document_job.id,
            })

        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            skipped_files.append(file.filename)

    time_taken = (datetime.now() - start_time).total_seconds()
    return AppResponse(
        status="success",
        message="Documents uploaded and queued for processing.",
        data={
            "processed_files": processed_jobs,
            "skipped_files": skipped_files,
            "time_taken": f"{time_taken:.2f} seconds"
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
        doc_name = document_handler.read(document_id).filename
        collection_name = document_handler.read(document_id).vector_collection

        document_delete_job = queue.enqueue(
            delete_document_task,
            args=(doc_name, collection_name),
            retry=Retry(max=3, interval=[10, 30, 60])
        )
        document_handler.delete(document_id)

        return AppResponse(
            status="success",
            message="Document deleted successfully",
            data={"job_id": document_delete_job.id}
        )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")
