"""
SQLAlchemy models for Document Management module.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DocumentModel(Base):
    """SQLAlchemy model for Document."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_folder_id", "folder_id"),
        Index("idx_documents_name", "name"),
        Index("idx_documents_created_by", "created_by"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    folder_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.folders.id"), nullable=True)
    file_path = Column(String(1024), nullable=False)
    mime_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    checksum = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=False, default="")
    tags = Column(ARRAY(String), nullable=False, default=list)
    metadata = Column(JSON, nullable=False, default=dict)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    folder = relationship("FolderModel", back_populates="documents")


class FolderModel(Base):
    """SQLAlchemy model for Folder."""

    __tablename__ = "folders"
    __table_args__ = (
        Index("idx_folders_parent_id", "parent_id"),
        Index("idx_folders_path", "path"),
        Index("idx_folders_created_by", "created_by"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.folders.id"), nullable=True)
    description = Column(Text, nullable=False, default="")
    path = Column(String(2048), nullable=False, default="/")
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentModel", back_populates="folder")
    children = relationship("FolderModel", backref="parent", remote_side=[id])


class DocumentVersionModel(Base):
    """SQLAlchemy model for DocumentVersion."""

    __tablename__ = "document_versions"
    __table_args__ = (
        Index("idx_document_versions_document_id", "document_id"),
        Index("idx_document_versions_version_number", "document_id", "version_number"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(1024), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    checksum = Column(String(255), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    change_note = Column(Text, nullable=False, default="")
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
