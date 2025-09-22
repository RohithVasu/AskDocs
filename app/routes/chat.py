from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.chat_service import Chat
from app.routes import AppResponse
from app.model_handlers.chat_message_handler import (
    ChatMessageHandler,
    ChatMessageCreate,
)
from app.core.db import get_global_db_session

chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    query: str


@chat_router.post("/", response_model=AppResponse)
def chat(
    request: ChatRequest, 
    db: Session = Depends(get_global_db_session)
):
    """Send a message and get AI response."""

    response = Chat().get_chat_response(
        request.session_id,
        request.query,
    )

    chat_message = ChatMessageCreate(
        session_id=request.session_id,
        query=request.query,
        response=response
    )
    ChatMessageHandler(db).create(chat_message)
    
    return AppResponse(
        status="success",
        message="Response received successfully",
        data={"query": request.query, "response": response}
    )