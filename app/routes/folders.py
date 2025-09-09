from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.model_handlers.folder_handler import FolderHandler, FolderCreate, FolderUpdate
from app.routes.auth import get_current_user
from app.core.db import get_global_db_session
from app.routes import AppResponse
from app.model_handlers.user_handler import UserResponse

folder_router = APIRouter(prefix="/folders", tags=["folders"])

@folder_router.post("/", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder: FolderCreate,
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
                user_id=str(current_user.id),
                name=folder.name,
            )
        )
    )

@folder_router.get("/", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def get_folders(
    skip: int = 0, 
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Get all folders for the current user"""
    handler = FolderHandler(db)
    return AppResponse(
        status="success",
        message="Folders fetched successfully",
        data=handler.get_by_user(str(current_user.id))
    )

@folder_router.get("/{folder_id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def get_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Get a specific folder by ID"""
    handler = FolderHandler(db)
    folder = handler.read(int(folder_id))
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Check ownership
    if folder.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return AppResponse(
        status="success",
        message="Folder fetched successfully",
        data=folder
    )

@folder_router.put("/{folder_id}", response_model=AppResponse)
async def update_folder(
    folder_id: str,
    folder_update: FolderUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Update a folder"""
    handler = FolderHandler(db)
    folder = handler.read(int(folder_id))
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Check ownership
    if folder.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return AppResponse(
        status="success",
        message="Folder updated successfully",
        data=handler.update(int(folder_id), folder_update)
    )

@folder_router.delete("/{folder_id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def delete_folder(
    folder_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    """Delete a folder"""
    handler = FolderHandler(db)
    folder = handler.read(int(folder_id))
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Check ownership
    if folder.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    handler.delete(int(folder_id))
    return AppResponse(
        status="success",
        message="Folder deleted successfully"
    )
