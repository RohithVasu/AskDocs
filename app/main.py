from fastapi import FastAPI

from app.backend.routes.chat import chat_router
from app.backend.routes.documents_index import index_router
from app.backend.routes.health_check import health_check_router

# Initialize FastAPI app
app = FastAPI(
    root_path="/api/v1",
    title="AskDocs API",
    description="Visit http://0.0.0.0:8000/docs for API documentation",
    version="0.0.1"
)

# Include routes
app.include_router(health_check_router)
app.include_router(index_router)
app.include_router(chat_router)