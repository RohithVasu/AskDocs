from fastapi import FastAPI
from loguru import logger
import uvicorn

from app.backend.core.settings import settings
from app.backend.routes.chat import chat_router
from app.backend.routes.documents_index import index_router


# Initialize FastAPI app
app = FastAPI(
    root_path="/api/v1",
    title="AskDocs API",
    description="Visit http://0.0.0.0:8000/docs for API documentation",
    version="0.0.1"
)

# Include routes
app.include_router(index_router)
app.include_router(chat_router)


def run():
    host = settings.fastapi.host
    port = settings.fastapi.port

    logger.info(f"Starting server at http://{host}:{port}/docs")
    logger.info(f"API docs at http://{host}:{port}/docs")

    uvicorn.run(
        "app.backend.main:app",
        host=host,
        port=port,
        reload_dir="./app/backend",
        workers=1,
        )

if __name__ == "__main__":
    run()
    
