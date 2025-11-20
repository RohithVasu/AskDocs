from fastapi import Depends, APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time

from app.dependencies.auth import get_current_user
from app.services.chat_service import Chat
from app.routes import AppResponse
from app.model_handlers.chat_message_handler import (
    ChatMessageHandler,
    ChatMessageCreate,
)
from app.core.db import get_global_db_session
from app.model_handlers.user_handler import UserResponse


chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    query: str


@chat_router.post("/")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_global_db_session),
    current_user: UserResponse = Depends(get_current_user),
):
    """Send a message and get AI response."""

    user_id = current_user.id
    session_id = request.session_id
    query = request.query

    async def generate_response():
        full_response = ""
        try:
            for chunk in Chat().stream_chat_response(
                user_id=user_id,
                session_id=session_id,
                query=query,
            ):
                full_response += chunk
                yield chunk
            
            # Save message after streaming
            chat_message = ChatMessageCreate(
                session_id=session_id,
                query=query,
                response=full_response
            )
            ChatMessageHandler(db).create(chat_message)
            
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate_response(), media_type="text/plain")