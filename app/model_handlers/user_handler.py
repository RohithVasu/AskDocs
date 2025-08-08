from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import CRUDManager
from app.models.user import User


class UserCreate(BaseModel):
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's name")

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, description="User's email address")
    name: Optional[str] = Field(None, description="User's name")

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique identifier for the user")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's name")
    created_at: datetime = Field(..., description="Timestamp of user creation")

class UserHandler(CRUDManager[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=User, response_schema=UserResponse)

    def create(self, obj_in: UserCreate) -> UserResponse:
        return super().create(obj_in)

    def read(self, id: int) -> UserResponse:
        return super().read(id)
        
    def update(self, id: int, obj_in: UserUpdate) -> UserResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: int) -> dict:
        return super().delete(id)
    
    def list_all(self) -> List[UserResponse]:
        return super().list_all()

    def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            user = self._db.query(User).filter(User.email == email).one()
            return self._response_schema.model_validate(user)
        except NoResultFound:
            return None

    def get_chat_sessions(self, user_id: str) -> List[UserResponse]:
        """Get all chat sessions for a user."""
        try:
            user = self._db.query(User).filter(User.id == user_id).one()
            return [self._response_schema.model_validate(session) for session in user.chat_sessions]
        except NoResultFound:
            return []

    def get_documents(self, user_id: str) -> List[UserResponse]:
        """Get all documents for a user."""
        try:
            user = self._db.query(User).filter(User.id == user_id).one()
            return [self._response_schema.model_validate(doc) for doc in user.documents]
        except NoResultFound:
            return []
