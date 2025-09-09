from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.model_handlers.user_handler import UserHandler, UserUpdate, UserResponse
from app.routes.auth import get_current_user
from app.core.db import get_global_db_session
from app.routes import AppResponse

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/", response_model=AppResponse)
async def get_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_global_db_session)):
    """Get all users with pagination"""
    handler = UserHandler(db)
    return AppResponse(
        status="success",
        message="Users fetched successfully",
        data=handler.list_all(skip, limit)
    )

@user_router.get("/{user_id}", response_model=AppResponse)
async def get_user(user_id: str, db: Session = Depends(get_global_db_session)):
    """Get a specific user by ID"""
    handler = UserHandler(db)
    user = handler.read(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return AppResponse(
        status="success",
        message="User fetched successfully",
        data=user
    )

@user_router.put("/{user_id}", response_model=AppResponse)
async def update_user(user_id: str, user_update: UserUpdate, 
                     current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_global_db_session)):
    """Update a user's information"""
    handler = UserHandler(db)
    user = handler.read(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only allow updating own profile
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return AppResponse(
        status="success",
        message="User updated successfully",
        data=handler.update(user_id, user_update)
    )

@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, 
                     current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_global_db_session)):
    """Delete a user"""
    handler = UserHandler(db)
    user = handler.read(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only allow deleting own account
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    handler.delete(user_id)
    return AppResponse(
        status="success",
        message="User deleted successfully"
    )