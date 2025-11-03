from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from sqlalchemy.orm import Session
from uuid import UUID

from . import CRUDManager
from app.models.document import Document


class DocumentCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user who owns the document")
    filename: str = Field(..., description="Name of the document file")
    file_path: str = Field(..., description="Path to the document file")
    vector_collection: str = Field(..., description="Vector collection for the document")
    status: str = Field(..., description="Status of the document")

class DocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, description="Name of the document file")
    vector_collection: Optional[str] = Field(None, description="Vector collection for the document")
    status: Optional[str] = Field(None, description="Status of the document")
    job_id: Optional[str] = Field(None, description="ID of the job processing the document")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Name of the document file")
    vector_collection: str = Field(..., description="Vector collection for the document")
    status: str = Field(..., description="Status of the document")
    job_id: Optional[str] = Field(None, description="ID of the job processing the document")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    created_at: datetime = Field(..., description="Timestamp when the document was created")

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)

class DocumentHandler(CRUDManager[Document, DocumentCreate, DocumentUpdate, DocumentResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=Document, response_schema=DocumentResponse)

    def create(self, obj_in: DocumentCreate) -> DocumentResponse:
        return super().create(obj_in)

    def read(self, id: str) -> DocumentResponse:
        return super().read(id)
        
    def update(self, id: str, obj_in: DocumentUpdate) -> DocumentResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: str) -> dict:
        return super().delete(id)
    
    def list_all(self) -> List[DocumentResponse]:
        return super().list_all()

    def get_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[DocumentResponse]:
        """Get all documents for a user, sorted by latest updated_at."""
        documents = (
            self._db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._response_schema.model_validate(doc) for doc in documents]

    def get_by_vector_collection(self, collection: str) -> List[DocumentResponse]:
        """Get all documents in a vector collection."""
        documents = self._db.query(Document).filter(Document.vector_collection == collection).all()
        return [self._response_schema.model_validate(doc) for doc in documents]
