from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from sqlalchemy.orm import Session
from . import CRUDManager
from app.models.chat_message import ChatMessage
from uuid import UUID

class ChatMessageCreate(BaseModel):
    session_id: str = Field(..., description="ID of the chat session")
    query: str = Field(..., description="The user's query message")
    response: Optional[str] = Field(None, description="The AI's response message")

class ChatMessageUpdate(BaseModel):
    session_id: Optional[str] = Field(None, description="ID of the chat session")
    query: Optional[str] = Field(None, description="The user's query message")
    response: Optional[str] = Field(None, description="The AI's response message")

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the chat message")
    session_id: UUID = Field(..., description="ID of the chat session")
    query: str = Field(..., description="The user's query message")
    response: Optional[str] = Field(None, description="The AI's response message")
    created_at: datetime = Field(..., description="Timestamp when the message was created")

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)

    @field_serializer("session_id")
    def serialize_session_id(self, v: UUID) -> str:
        return str(v)

class ChatMessageHandler(CRUDManager[ChatMessage, ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=ChatMessage, response_schema=ChatMessageResponse)

    def create(self, obj_in: ChatMessageCreate) -> ChatMessageResponse:
        return super().create(obj_in)

    def read(self, id: int) -> ChatMessageResponse:
        return super().read(id)
        
    def update(self, id: int, obj_in: ChatMessageUpdate) -> ChatMessageResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: int) -> dict:
        return super().delete(id)
    
    def list_all(self) -> List[ChatMessageResponse]:
        return super().list_all()

    def get_by_session(self, session_id: str) -> List[ChatMessageResponse]:
        """Get all messages in a chat session."""
        messages = (
            self._db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(5)
            .all()
        )

        messages.reverse()
        
        return [self._response_schema.model_validate(msg) for msg in messages]