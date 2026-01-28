"""
SQLAlchemy models for Document Management module.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# Document Type Configuration
# =============================================================================


class DocumentTypeModel(Base):
    """
    Configurable document type classification.

    Stored in database for runtime configuration (no hardcoded enums).
    """

    __tablename__ = "document_types"
    __table_args__ = (
        Index("idx_doctypes_code", "code", unique=True),
        Index("idx_doctypes_category", "category"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(20), nullable=False, unique=True)  # DRAW, CALC, TP
    name = Column(String(100), nullable=False)  # Drawings, Calculations
    description = Column(Text, default="")
    category = Column(String(50), default="general")  # engineering, logistics, finance
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentModel", back_populates="document_type")


# =============================================================================
# Storage Templates
# =============================================================================


class StorageTemplateModel(Base):
    """Storage template defining folder structure for projects."""

    __tablename__ = "storage_templates"
    __table_args__ = ({"schema": "dm"},)

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    folders = relationship(
        "TemplateFolderModel",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class TemplateFolderModel(Base):
    """Folder definition within a storage template."""

    __tablename__ = "template_folders"
    __table_args__ = (
        Index("idx_template_folders_template_id", "template_id"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dm.storage_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    path = Column(String(500), nullable=False)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.template_folders.id"), nullable=True)
    description = Column(Text, default="")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    template = relationship("StorageTemplateModel", back_populates="folders")


# =============================================================================
# Stages (Kanban)
# =============================================================================


class StageModel(Base):
    """Document workflow stage (Kanban column) per project."""

    __tablename__ = "stages"
    __table_args__ = (
        Index("idx_stages_project_id", "project_id"),
        Index("idx_stages_order", "project_id", "order_index"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK to pm.projects
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    order_index = Column(Integer, default=0)
    color = Column(String(7), default="#6B7280")  # Hex color
    is_default = Column(Boolean, default=False)  # New documents start here
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentModel", back_populates="stage")


# =============================================================================
# Folders (Project-specific, from template)
# =============================================================================


class FolderModel(Base):
    """Folder for organizing documents within a project."""

    __tablename__ = "folders"
    __table_args__ = (
        Index("idx_folders_project_id", "project_id"),
        Index("idx_folders_parent_id", "parent_id"),
        Index("idx_folders_path", "project_id", "path"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK to pm.projects
    name = Column(String(255), nullable=False)
    path = Column(String(1024), nullable=False, default="/")
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.folders.id"), nullable=True)
    description = Column(Text, default="")
    is_archived = Column(Boolean, default=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentModel", back_populates="folder")
    children = relationship("FolderModel", backref="parent", remote_side=[id])


# =============================================================================
# Document (Main Entity)
# =============================================================================


class DocumentModel(Base):
    """Document aggregate - registered document in the DRMS."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_project_id", "project_id"),
        Index("idx_documents_document_number", "document_number", unique=True),
        Index("idx_documents_folder_id", "folder_id"),
        Index("idx_documents_stage_id", "stage_id"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_document_type_id", "document_type_id"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Project binding
    project_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK to pm.projects

    # Identification
    title = Column(String(255), nullable=False)  # User-facing name
    document_number = Column(String(100), nullable=True, unique=True)  # Auto-generated

    # Classification
    document_type_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dm.document_types.id"),
        nullable=False,
    )

    # Organization
    folder_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.folders.id"), nullable=True)
    stage_id = Column(PG_UUID(as_uuid=True), ForeignKey("dm.stages.id"), nullable=True)

    # Versioning
    version_scheme = Column(String(20), default="semantic")  # sequential, semantic, simple
    current_version = Column(String(20), nullable=True)  # Latest version string

    # Status
    status = Column(String(30), default="DRAFT")  # DocumentStatus enum value

    # Content
    description = Column(Text, default="")
    tags = Column(ARRAY(String), default=list)
    metadata_ = Column("metadata", JSON, default=dict)
    external_references = Column(ARRAY(String), default=list)  # Contract/PO numbers

    # Audit
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    folder = relationship("FolderModel", back_populates="documents")
    stage = relationship("StageModel", back_populates="documents")
    document_type = relationship("DocumentTypeModel", back_populates="documents")
    versions = relationship(
        "DocumentVersionModel",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="desc(DocumentVersionModel.created_at)",
    )
    approval_requests = relationship(
        "ApprovalRequestModel",
        back_populates="document",
        cascade="all, delete-orphan",
    )


# =============================================================================
# Document Version (Immutable)
# =============================================================================


class DocumentVersionModel(Base):
    """
    Immutable version record for a document.

    Each version has its own physical file stored in MinIO.
    """

    __tablename__ = "document_versions"
    __table_args__ = (
        Index("idx_versions_document_id", "document_id"),
        Index("idx_versions_version_string", "document_id", "version_string"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dm.documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Version info (supports all schemes)
    version_string = Column(String(20), nullable=False)  # "0001", "1.0.0", "1.0"
    major = Column(Integer, default=0)
    minor = Column(Integer, default=0)
    patch = Column(Integer, default=0)
    sequence = Column(Integer, default=1)

    # File storage
    storage_key = Column(String(500), nullable=False)  # MinIO key
    original_filename = Column(String(255), nullable=False)
    generated_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False)  # SHA-256

    # Metadata
    change_note = Column(Text, default="")

    # Audit (immutable)
    uploaded_by = Column(PG_UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("DocumentModel", back_populates="versions")


# =============================================================================
# Approval Workflow
# =============================================================================


class ApprovalRequestModel(Base):
    """Approval workflow request for a document."""

    __tablename__ = "approval_requests"
    __table_args__ = (
        Index("idx_approvals_document_id", "document_id"),
        Index("idx_approvals_assigned_to", "assigned_to"),
        Index("idx_approvals_status", "status"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("dm.documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_string = Column(String(20), nullable=False)  # Version at time of request
    requested_by = Column(PG_UUID(as_uuid=True), nullable=False)
    assigned_to = Column(PG_UUID(as_uuid=True), nullable=False)  # Approver
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED, RETURNED
    request_note = Column(Text, default="")
    decision_note = Column(Text, default="")
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("DocumentModel", back_populates="approval_requests")


# =============================================================================
# Audit Log (Append-only)
# =============================================================================


class AuditLogModel(Base):
    """
    Immutable audit log entry.

    Never modified or deleted - compliance requirement.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_action", "action"),
        {"schema": "dm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    action = Column(String(100), nullable=False)  # document.created, version.uploaded
    entity_type = Column(String(50), nullable=False)  # document, version, approval
    entity_id = Column(PG_UUID(as_uuid=True), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(JSON, default=dict)  # Additional context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
