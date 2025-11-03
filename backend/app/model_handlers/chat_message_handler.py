from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from sqlalchemy.orm import Session
from uuid import UUID
from . import CRUDManager
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession  


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
        """Create a new message and update the session's last activity timestamp."""
        message = ChatMessage(**obj_in.model_dump())
        self._db.add(message)

        # ✅ Update session last activity
        session = self._db.query(ChatSession).filter(ChatSession.id == obj_in.session_id).first()
        if session:
            session.updated_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(message)

        return self._response_schema.model_validate(message)

    def read(self, id: str) -> ChatMessageResponse:
        return super().read(id)

    def update(self, id: str, obj_in: ChatMessageUpdate) -> ChatMessageResponse:
        """Update message and refresh session activity timestamp."""
        message = self._db.query(ChatMessage).filter(ChatMessage.id == id).first()
        if not message:
            raise ValueError("Message not found")

        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(message, field, value)

        # ✅ Touch session on message update
        session = self._db.query(ChatSession).filter(ChatSession.id == message.session_id).first()
        if session:
            session.updated_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(message)

        return self._response_schema.model_validate(message)

    def delete(self, id: str) -> dict:
        return super().delete(id)

    def list_all(self) -> List[ChatMessageResponse]:
        return super().list_all()

    def get_by_session(self, session_id: str) -> List[ChatMessageResponse]:
        """Get recent messages in a chat session (latest 5, ascending order)."""
        messages = (
            self._db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(5)
            .all()
        )
        messages.reverse()
        return [self._response_schema.model_validate(msg) for msg in messages]

    def get_paginated(
        self,
        session_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[dict], int]:
        """
        Paginated fetch for chat UI (infinite scroll).
        Returns (messages, total_count)
        """
        query = (
            self._db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
        )

        total = query.count()

        messages = (
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        results = []
        for msg in messages:
            if msg.query and msg.response:
                results.append({
                    "id": str(msg.id),
                    "role": "user",
                    "content": msg.query,
                    "created_at": msg.created_at.isoformat(),
                })
                results.append({
                    "id": f"{msg.id}-a",
                    "role": "assistant",
                    "content": msg.response,
                    "created_at": msg.created_at.isoformat(),
                })
            elif msg.query:
                results.append({
                    "id": str(msg.id),
                    "role": "user",
                    "content": msg.query,
                    "created_at": msg.created_at.isoformat(),
                })

        grouped = [results[i:i+2] for i in range(0, len(results), 2)]
        grouped.reverse()
        results = [msg for group in grouped for msg in group]

        return results, total

