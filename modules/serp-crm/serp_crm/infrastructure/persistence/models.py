"""
SQLAlchemy models for CRM entities.

All tables are created in the 'crm' PostgreSQL schema by default.
This can be configured via SERP_CRM_DATABASE_SCHEMA environment variable.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from serp_crm.config import CRMSettings
from serp_crm.domain.entities import (
    ActivityType,
    LeadStatus,
    OpportunityStage,
    PartnerType,
)

# Get schema from settings
_settings = CRMSettings()
CRM_SCHEMA = _settings.database_schema

# Create metadata with schema
metadata = MetaData(schema=CRM_SCHEMA)


class Base(DeclarativeBase):
    """Base class for all CRM SQLAlchemy models."""

    metadata = metadata


class PartnerModel(Base):
    """SQLAlchemy model for Partner entity."""

    __tablename__ = "partners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    partner_type: Mapped[PartnerType] = mapped_column(
        Enum(PartnerType, schema=CRM_SCHEMA), nullable=False
    )

    is_customer: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Contact info
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    website: Mapped[str | None] = mapped_column(String(255))

    # Billing Address (stored as JSON)
    billing_address: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Shipping Address (stored as JSON)
    shipping_address: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Tax & Legal
    tax_id_value: Mapped[str | None] = mapped_column(String(50))
    tax_id_country: Mapped[str | None] = mapped_column(String(2))
    company_registry: Mapped[str | None] = mapped_column(String(100))

    # Business details
    industry: Mapped[str | None] = mapped_column(String(100))
    employee_count: Mapped[int | None] = mapped_column(Integer)
    annual_revenue_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    annual_revenue_currency: Mapped[str | None] = mapped_column(String(3))

    # Internal tracking
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    contacts: Mapped[list["ContactModel"]] = relationship(
        "ContactModel", back_populates="partner", cascade="all, delete-orphan"
    )
    opportunities: Mapped[list["OpportunityModel"]] = relationship(
        "OpportunityModel", back_populates="partner", cascade="all, delete-orphan"
    )


class ContactModel(Base):
    """SQLAlchemy model for Contact entity."""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    partner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Contact info
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    mobile: Mapped[str | None] = mapped_column(String(50))

    # Position
    job_title: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))

    # Address (stored as JSON)
    address: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Internal tracking
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    partner: Mapped["PartnerModel"] = relationship(
        "PartnerModel", back_populates="contacts"
    )


class LeadModel(Base):
    """SQLAlchemy model for Lead entity."""

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, schema=CRM_SCHEMA),
        default=LeadStatus.NEW,
        nullable=False,
        index=True,
    )

    # Contact info
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))

    # Qualification
    source: Mapped[str | None] = mapped_column(String(100))
    score: Mapped[int] = mapped_column(Integer, default=0)
    interest_level: Mapped[str | None] = mapped_column(String(20))

    # Conversion
    converted_to_partner_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.partners.id", ondelete="SET NULL"),
    )
    converted_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Internal tracking
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class OpportunityModel(Base):
    """SQLAlchemy model for Opportunity entity."""

    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    partner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, schema=CRM_SCHEMA),
        default=OpportunityStage.PROSPECTING,
        nullable=False,
        index=True,
    )

    # Financial
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    probability: Mapped[int] = mapped_column(Integer, default=0)

    # Timeline
    expected_close_date: Mapped[date | None] = mapped_column(Date)
    actual_close_date: Mapped[date | None] = mapped_column(Date)

    # Tracking
    source: Mapped[str | None] = mapped_column(String(100))
    campaign: Mapped[str | None] = mapped_column(String(100))

    # Internal tracking
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    partner: Mapped["PartnerModel"] = relationship(
        "PartnerModel", back_populates="opportunities"
    )


class ActivityModel(Base):
    """SQLAlchemy model for Activity entity."""

    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    partner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.contacts.id", ondelete="SET NULL"),
        index=True,
    )
    opportunity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(f"{CRM_SCHEMA}.opportunities.id", ondelete="SET NULL"),
        index=True,
    )

    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, schema=CRM_SCHEMA), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)

    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Attribution
    performed_by: Mapped[str | None] = mapped_column(String(36))  # User ID

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
