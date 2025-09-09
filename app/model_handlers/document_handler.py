from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from . import CRUDManager
from app.models.document import Document


class DocumentCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user who owns the document")
    folder_id: Optional[str] = Field(None, description="ID of the folder containing the document")
    filename: str = Field(..., description="Name of the document file")
    vector_collection: str = Field(..., description="Vector collection for the document")

class DocumentUpdate(BaseModel):
    user_id: Optional[str] = Field(None, description="ID of the user who owns the document")
    folder_id: Optional[str] = Field(None, description="ID of the folder containing the document")
    filename: Optional[str] = Field(None, description="Name of the document file")
    vector_collection: Optional[str] = Field(None, description="Vector collection for the document")

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique identifier for the document")
    user_id: str = Field(..., description="ID of the user who owns the document")
    folder_id: Optional[str] = Field(None, description="ID of the folder containing the document")
    filename: str = Field(..., description="Name of the document file")
    vector_collection: str = Field(..., description="Vector collection for the document")
    uploaded_at: datetime = Field(..., description="Timestamp when the document was uploaded")

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
        """Get all documents for a user."""
        documents = self._db.query(Document).filter(Document.user_id == user_id).offset(skip).limit(limit).all()
        return [self._response_schema.model_validate(doc) for doc in documents]

    def get_by_folder(self, folder_id: str) -> List[DocumentResponse]:
        """Get all documents in a folder."""
        documents = self._db.query(Document).filter(Document.folder_id == folder_id).all()
        return [self._response_schema.model_validate(doc) for doc in documents]

    def get_by_vector_collection(self, collection: str) -> List[DocumentResponse]:
        """Get all documents in a vector collection."""
        documents = self._db.query(Document).filter(Document.vector_collection == collection).all()
        return [self._response_schema.model_validate(doc) for doc in documents]
