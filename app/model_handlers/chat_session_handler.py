from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID
from sqlalchemy.orm import Session
from . import CRUDManager
from app.models.chat_session import ChatSession


class ChatSessionCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user associated with this session")
    name: str = Field(..., description="Name of the session")

class ChatSessionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the session")

class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the chat session")
    name: str = Field(..., description="Name of the session")

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)

class ChatSessionHandler(CRUDManager[ChatSession, ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=ChatSession, response_schema=ChatSessionResponse)

    def create(self, obj_in: ChatSessionCreate) -> ChatSessionResponse:
        return super().create(obj_in)

    def read(self, id: int) -> ChatSessionResponse:
        return super().read(id)
        
    def update(self, id: int, obj_in: ChatSessionUpdate) -> ChatSessionResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: int) -> dict:
        return super().delete(id)
    
    def list_all(self) -> List[ChatSessionResponse]:
        return super().list_all()

    def get_by_user(self, user_id: str) -> List[ChatSessionResponse]:
        """Get all chat sessions for a user."""
        sessions = self._db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
        return [self._response_schema.model_validate(session) for session in sessions]

    def get_messages(self, session_id: str) -> List[ChatSessionResponse]:
        """Get all messages in a chat session."""
        try:
            session = self._db.query(ChatSession).filter(ChatSession.id == session_id).one()
            return [self._response_schema.model_validate(msg) for msg in session.messages]
        except NoResultFound:
            return []
