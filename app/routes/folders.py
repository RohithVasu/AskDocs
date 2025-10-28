from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from rq import Retry

from app.model_handlers.document_handler import DocumentHandler
from app.model_handlers.folder_handler import FolderHandler, FolderCreate, FolderUpdate
from app.dependencies.auth import get_current_user
from app.core.db import get_global_db_session
from app.routes import AppResponse
from app.model_handlers.user_handler import UserResponse
from app.core.qdrant import get_qdrant_client
from app.core.redis import queue

folder_router = APIRouter(prefix="/folders", tags=["folders"])

def delete_document_task(doc_name: str, collection_name: str):
    qdrant_client = get_qdrant_client()
    return qdrant_client.delete_document(doc_name, collection_name)

@folder_router.post("/", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Create a new folder"""
    handler = FolderHandler(db)
    return AppResponse(
        status="success",
        message="Folder created successfully",
        data=handler.create(
            FolderCreate(
                user_id=current_user.id,
                name=folder_name,
            )
        )
    )

@folder_router.get("/", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def get_folders(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Get all folders for the current user"""
    try:
        folder_handler = FolderHandler(db)
        folders = folder_handler.get_by_user(current_user.id)
        return AppResponse(
            status="success",
            message="Folders fetched successfully",
            data=folders
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching folders: {str(e)}")

@folder_router.get("/{folder_id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def get_folder(
    folder_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Get a specific folder by ID"""
    handler = FolderHandler(db)
    folder = handler.read(folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return AppResponse(
        status="success",
        message="Folder fetched successfully",
        data=folder
    )

@folder_router.patch("/{folder_id}", response_model=AppResponse)
async def update_folder(
    folder_id: str,
    folder_update: FolderUpdate,
    db: Session = Depends(get_global_db_session)
):
    """Update a folder"""
    handler = FolderHandler(db)
    folder = handler.read(folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return AppResponse(
        status="success",
        message="Folder updated successfully",
        data=handler.update(folder_id, folder_update)
    )

@folder_router.delete("/{folder_id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def delete_folder(
    folder_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Delete a folder"""
    handler = FolderHandler(db)
    folder = handler.read(folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder_id = folder.id
    
    document_handler = DocumentHandler(db)
    documents = document_handler.get_by_folder(folder_id)

    if documents:
        job_ids = []
        for document in documents:
            job_ids.append(
                queue.enqueue(
                    delete_document_task,
                    args=(document.filename, document.vector_collection),
                    retry=Retry(max=3, interval=[10, 30, 60])
                )
            )
    
    handler.delete(folder_id)
    return AppResponse(
        status="success",
        message="Folder deleted successfully",
        data={"job_ids": job_ids}
    )