from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from uuid import UUID

from . import CRUDManager
from app.models.user import User


class UserCreate(BaseModel):
    email: str = Field(..., description="User's email address")
    firstname: str = Field(..., description="User's firstname")
    lastname: str = Field(..., description="User's lastname")
    password: str = Field(..., description="User's password")

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, description="User's email address")
    firstname: Optional[str] = Field(None, description="User's firstname")
    lastname: Optional[str] = Field(None, description="User's lastname")
    password: Optional[str] = Field(None, description="User's password")

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the user")
    email: str = Field(..., description="User's email address")
    firstname: str = Field(..., description="User's firstname")
    lastname: str = Field(..., description="User's lastname")
    password: Optional[str] = Field(None, description="User's password")
    created_at: datetime = Field(..., description="Timestamp of user creation")

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)


class UserHandler(CRUDManager[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=User, response_schema=UserResponse)

    def create(self, obj_in: UserCreate) -> UserResponse:
        return super().create(obj_in)

    def read(self, id: str) -> UserResponse:
        return super().read(id)
        
    def update(self, id: str, obj_in: UserUpdate) -> UserResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: str) -> dict:
        return super().delete(id)
    
    def list_all(self, skip: int = 0, limit: int = 20) -> List[UserResponse]:
        return super().list_all(skip, limit)

    def get_by_email(self, email: str, with_password: bool = False) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            user = self._db.query(User).filter(User.email == email).one()
            user_data = self._response_schema.model_validate(user).model_dump()

            if not with_password:
                user_data.pop("password", None)

            return UserResponse(**user_data)
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
