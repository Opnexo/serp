"""
SQLAlchemy models for Project Management module.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


class ProjectModel(Base):
    """SQLAlchemy model for Project."""

    __tablename__ = "projects"
    __table_args__ = (
        Index("idx_projects_owner_id", "owner_id"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_project_type", "project_type"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    project_type = Column(String(50), nullable=False, default="generic")
    description = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="PLANNING")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), nullable=True)
    team_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.teams.id"), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)  # 'metadata' is reserved in SQLAlchemy
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("TeamModel", back_populates="projects")
    tasks = relationship("TaskModel", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("MilestoneModel", back_populates="project", cascade="all, delete-orphan")


class TaskModel(Base):
    """SQLAlchemy model for Task."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_project_id", "project_id"),
        Index("idx_tasks_assigned_to", "assigned_to"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_priority", "priority"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="OPEN")
    priority = Column(String(20), nullable=False, default="MEDIUM")
    assigned_to = Column(PG_UUID(as_uuid=True), nullable=True)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.tasks.id"), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=list)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("ProjectModel", back_populates="tasks")
    subtasks = relationship("TaskModel", backref=backref("parent", remote_side=[id]))


class TeamModel(Base):
    """SQLAlchemy model for Team."""

    __tablename__ = "teams"
    __table_args__ = (
        Index("idx_teams_project_id", "project_id"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    project_id = Column(PG_UUID(as_uuid=True), nullable=True)  # Optional link to project
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("TeamMemberModel", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("ProjectModel", back_populates="team")


class TeamMemberModel(Base):
    """SQLAlchemy model for TeamMember."""

    __tablename__ = "team_members"
    __table_args__ = (
        Index("idx_team_members_team_id", "team_id"),
        Index("idx_team_members_user_id", "user_id"),
        {"schema": "pm"},
    )

    team_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.teams.id"), primary_key=True)
    user_id = Column(PG_UUID(as_uuid=True), primary_key=True)
    role = Column(String(50), nullable=False, default="MEMBER")
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    team = relationship("TeamModel", back_populates="members")


class MilestoneModel(Base):
    """SQLAlchemy model for Milestone."""

    __tablename__ = "milestones"
    __table_args__ = (
        Index("idx_milestones_project_id", "project_id"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    due_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("ProjectModel", back_populates="milestones")


class CommentModel(Base):
    """SQLAlchemy model for Comment."""

    __tablename__ = "comments"
    __table_args__ = (
        Index("idx_comments_entity", "entity_type", "entity_id"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(50), nullable=False)  # "project" or "task"
    entity_id = Column(PG_UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(PG_UUID(as_uuid=True), nullable=False)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("pm.comments.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    replies = relationship("CommentModel", backref=backref("parent", remote_side=[id]))


class AttachmentModel(Base):
    """SQLAlchemy model for Attachment."""

    __tablename__ = "attachments"
    __table_args__ = (
        Index("idx_attachments_entity", "entity_type", "entity_id"),
        {"schema": "pm"},
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(50), nullable=False)  # "project" or "task"
    entity_id = Column(PG_UUID(as_uuid=True), nullable=False)
    document_id = Column(PG_UUID(as_uuid=True), nullable=False)  # Reference to dm.documents
    uploaded_by = Column(PG_UUID(as_uuid=True), nullable=False)
    description = Column(String(255), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
