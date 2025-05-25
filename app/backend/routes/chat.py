from app.backend.routes import ChatRequest, AppResponse
from app.backend.services.chat_service import Chat
from datetime import datetime
from fastapi import APIRouter

chat_router = APIRouter(prefix="/chat")

chat_service = Chat()

@chat_router.post("/chat", response_model=AppResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with the uploaded documents."""
    start_time = datetime.now()

    # Get chat response
    answer, chat_history = chat_service.get_chat_response(
        request.question,
        request.collection_name
    )  

    time_taken = datetime.now() - start_time
    
    return AppResponse(
        time=str(time_taken.total_seconds()) + " seconds",
        data={
            "message": "Chat response generated successfully",
            "question": request.question,
            "answer": answer,
            "chat_history": chat_history
        }
    )