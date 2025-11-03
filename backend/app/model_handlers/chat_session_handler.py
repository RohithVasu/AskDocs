from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID
from sqlalchemy.orm import Session
from . import CRUDManager
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from sqlalchemy import func

class ChatSessionCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user associated with this session")
    name: str = Field(..., description="Name of the session")

class ChatSessionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the session")

class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    updated_at: datetime

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

    # def get_by_user(self, user_id: str) -> List[ChatSessionResponse]:
    #     """Get all chat sessions for a user, sorted by last activity."""
    #     sessions = (
    #         self._db.query(ChatSession)
    #         .filter(ChatSession.user_id == user_id)
    #         .order_by(ChatSession.updated_at.desc())  # 👈 newest first
    #         .all()
    #     )
    #     return [self._response_schema.model_validate(session) for session in sessions]

    def get_by_user(self, user_id: str) -> List[ChatSessionResponse]:
        """
        Get all chat sessions for a user sorted by most recent message or session update.
        """
        subq = (
            self._db.query(
                ChatMessage.session_id,
                func.max(ChatMessage.created_at).label("last_message_at")
            )
            .group_by(ChatMessage.session_id)
            .subquery()
        )

        sessions = (
            self._db.query(ChatSession)
            .outerjoin(subq, ChatSession.id == subq.c.session_id)
            .filter(ChatSession.user_id == user_id)
            .order_by(func.coalesce(subq.c.last_message_at, ChatSession.updated_at).desc())
            .all()
        )

        return [self._response_schema.model_validate(s) for s in sessions]

    def get_messages(self, session_id: str) -> List[ChatSessionResponse]:
        """Get all messages in a chat session."""
        try:
            session = self._db.query(ChatSession).filter(ChatSession.id == session_id).one()
            return [self._response_schema.model_validate(msg) for msg in session.messages]
        except NoResultFound:
            return []
