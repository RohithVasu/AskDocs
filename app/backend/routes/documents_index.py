from app.backend.routes import AppResponse
from fastapi import APIRouter, UploadFile, File
import os
from datetime import datetime
from app.backend.services.document_processor import DocumentProcessor
from app.backend.core.settings import settings

index_router = APIRouter(prefix="/documents")

# Initialize services
document_processor = DocumentProcessor()

@index_router.post("/upload", response_model=AppResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    start_time = datetime.now()
    # Save uploaded file
    file_path = os.path.join(
        settings.data.documents_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process document
    texts = document_processor.process_document(file_path)
    collection_name =document_processor.create_vector_store(texts, file.filename)
    
    time_taken = datetime.now() - start_time
    return AppResponse(
        time=str(time_taken.total_seconds()) + " seconds",
        data={
            "message": "Document uploaded and indexed successfully",
            "collection_name": collection_name
        }
    )