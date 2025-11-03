from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base
import uuid


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    vector_collection = Column(String, nullable=False)
    status = Column(String, nullable=False, default="processing", index=True)
    job_id = Column(String, nullable=True, index=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="documents")
    document_sessions = relationship("ChatSessionDocument", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_documents_user_status", "user_id", "status"),  # 🔹 Composite index
        Index("idx_documents_user_filename", "user_id", "filename"),
    )
