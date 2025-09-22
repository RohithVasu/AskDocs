from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID
from sqlalchemy.orm import Session

from . import CRUDManager
from app.models.folder import Folder


class FolderCreate(BaseModel):
    user_id: UUID = Field(..., description="ID of the user who owns the folder")
    name: str = Field(..., description="Name of the folder")

    @field_serializer("user_id")
    def serialize_user_id(self, v: UUID) -> str:
        return str(v)

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the folder")

class FolderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the folder")
    user_id: UUID = Field(..., description="ID of the user who owns the folder")
    name: str = Field(..., description="Name of the folder")
    created_at: datetime = Field(..., description="Timestamp when the folder was created")

    @field_serializer("user_id")
    def serialize_user_id(self, v: UUID) -> str:
        return str(v)

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)

class FolderHandler(CRUDManager[Folder, FolderCreate, FolderUpdate, FolderResponse]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=Folder, response_schema=FolderResponse)

    def create(self, obj_in: FolderCreate) -> FolderResponse:
        return super().create(obj_in)

    def read(self, id: int) -> FolderResponse:
        return super().read(id)
        
    def update(self, id: int, obj_in: FolderUpdate) -> FolderResponse:
        return super().update(id, obj_in)
        
    def delete(self, id: int) -> dict:
        return super().delete(id)
    
    def list_all(self) -> List[FolderResponse]:
        return super().list_all()

    def get_by_user(self, user_id: str) -> List[FolderResponse]:
        """Get all folders for a user."""
        folders = self._db.query(Folder).filter(Folder.user_id == user_id).all()
        return [self._response_schema.model_validate(folder) for folder in folders]

    def get_documents(self, folder_id: str) -> List[FolderResponse]:
        """Get all documents in a folder."""
        try:
            folder = self._db.query(Folder).filter(Folder.id == folder_id).one()
            return [self._response_schema.model_validate(doc) for doc in folder.documents]
        except NoResultFound:
            return []
