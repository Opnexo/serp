"""
SQLAlchemy models for serp-common module.

All tables are created in the 'common' PostgreSQL schema.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from serp_common.config import get_settings

# Get schema from settings
_settings = get_settings()
COMMON_SCHEMA = _settings.database_schema

# Create metadata with schema
metadata = MetaData(schema=COMMON_SCHEMA)


class Base(DeclarativeBase):
    """Base class for all models."""

    metadata = metadata


class AddressModel(Base):
    """SQLAlchemy model for addresses."""

    __tablename__ = "addresses"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Required fields
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)

    # Optional fields
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="OTHER",
    )

    # Owner reference
    owner_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    owner_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Flags
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_addresses_owner", "owner_type", "owner_id"),
        Index("ix_addresses_country", "country"),
        Index("ix_addresses_city", "city"),
        Index("ix_addresses_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<AddressModel(id={self.id}, label={self.label}, city={self.city})>"
