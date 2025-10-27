from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time

from app.routes.auth import get_current_user
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


@chat_router.post("/", response_model=AppResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_global_db_session),
    current_user: UserResponse = Depends(get_current_user),
):
    """Send a message and get AI response."""

    start_time = time.time()

    user_id = current_user.id
    session_id = request.session_id
    query = request.query

    response = Chat().get_chat_response(
        user_id=user_id,
        session_id=session_id,
        query=query,
    )

    chat_message = ChatMessageCreate(
        session_id=request.session_id,
        query=request.query,
        response=response
    )
    ChatMessageHandler(db).create(chat_message)
    
    end_time = time.time()
    
    return AppResponse(
        status="success",
        message="Response received successfully",
        data={"time": end_time - start_time, "query": request.query, "response": response}
    )