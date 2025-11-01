from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.db import get_global_db_session
from app.model_handlers.chat_session_documents_handler import (
    ChatSessionDocumentHandler, 
    ChatSessionDocumentCreate,
)
from app.model_handlers.chat_session_handler import (
    ChatSessionHandler, 
    ChatSessionCreate, 
    ChatSessionUpdate,
)
from app.model_handlers.chat_message_handler import (
    ChatMessageHandler,
    ChatMessageResponse
)
from app.routes import AppResponse
from app.dependencies.auth import get_current_user
from app.model_handlers.user_handler import UserResponse

session_router = APIRouter(prefix="/sessions", tags=["sessions"])

@session_router.post("/", response_model=AppResponse)
def create_session(
    session_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    return AppResponse(
        status="success",
        message="Chat session created successfully",
        data={"data": ChatSessionHandler(db).create(
            ChatSessionCreate(
                user_id=str(current_user.id),
                name=session_name,
            )
        )}
    )

@session_router.get("/", response_model=AppResponse)
def list_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_global_db_session)
):
    return AppResponse(
        status="success",
        message="Chat sessions fetched successfully",
        data=ChatSessionHandler(db).get_by_user(current_user.id)
    )


@session_router.get("/{session_id}", response_model=AppResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_global_db_session)
):
    return AppResponse(
        status="success",
        message="Chat session fetched successfully",
        data=ChatSessionHandler(db).read(session_id)
    )


@session_router.patch("/{session_id}", response_model=AppResponse)
def update_session(
    session_id: str,
    name: str,
    db: Session = Depends(get_global_db_session)
):
    return AppResponse(
        status="success",
        message="Chat session updated successfully",
        data=ChatSessionHandler(db).update(session_id, ChatSessionUpdate(name=name))
    )


@session_router.delete("/{session_id}", response_model=AppResponse)
def delete_session(
    session_id: str,
    db: Session = Depends(get_global_db_session)
):
    return AppResponse(
        status="success",
        message="Chat session deleted successfully",
        data=ChatSessionHandler(db).delete(session_id)
    )

@session_router.post("/add_documents", response_model=AppResponse)
def add_documents_to_session(
    obj_in: ChatSessionDocumentCreate,
    db: Session = Depends(get_global_db_session)
):
    """Attach one or more documents to a session."""
    
    return AppResponse(
        status="success",
        message="Documents added to session successfully",
        data=ChatSessionDocumentHandler(db).create(obj_in)
    )


@session_router.get("/{session_id}/documents", response_model=AppResponse)
def list_session_documents(
    session_id: str,
    db: Session = Depends(get_global_db_session)
):
    """List all documents in a session."""
    return AppResponse(
        status="success",
        message="Documents fetched successfully",
        data=ChatSessionDocumentHandler(db).get_by_session(session_id)
    )


@session_router.delete("/{session_id}/documents/{doc_id}", response_model=AppResponse)
def remove_document_from_session(
    session_id: str,
    doc_id: str,
    db: Session = Depends(get_global_db_session)
):
    """Remove a single document from a session."""
    handler = ChatSessionDocumentHandler(db)
    records = handler.get_by_session(session_id)
    record = next((r for r in records if str(r.document_id) == doc_id), None)

    if not record:
        raise HTTPException(status_code=404, detail="Document not linked to session")
        
    return AppResponse(
        status="success",
        message="Document removed from session successfully",
        data=handler.delete(record.id)
    )

@session_router.get("/{session_id}/messages")
def list_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_global_db_session)
) -> Dict[str, Any]:
    """Get paginated messages for a session."""
    handler = ChatMessageHandler(db)
    data, total = handler.get_paginated(session_id, page, page_size)

    return {
        "data": data,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next_page": (page * page_size) < total
        }
    }