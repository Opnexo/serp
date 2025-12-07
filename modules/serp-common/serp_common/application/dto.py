"""
Data Transfer Objects for serp-common module.

DTOs are used for API request/response serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddressCreateDTO(BaseModel):
    """DTO for creating an address."""

    label: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    address_type: str = Field(
        default="OTHER",
        pattern="^(BILLING|SHIPPING|OFFICE|HOME|OTHER)$",
    )
    owner_type: Optional[str] = Field(None, max_length=50)
    owner_id: Optional[str] = Field(None, max_length=36)
    is_primary: bool = False
    notes: Optional[str] = Field(None, max_length=500)


class AddressUpdateDTO(BaseModel):
    """DTO for updating an address."""

    label: Optional[str] = Field(None, min_length=1, max_length=100)
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    address_type: Optional[str] = Field(
        None,
        pattern="^(BILLING|SHIPPING|OFFICE|HOME|OTHER)$",
    )
    is_primary: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class AddressDTO(BaseModel):
    """DTO for address response."""

    id: str
    label: str
    street: str
    city: str
    country: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    address_type: str
    owner_type: Optional[str] = None
    owner_id: Optional[str] = None
    is_primary: bool
    is_active: bool
    notes: Optional[str] = None
    single_line: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddressListDTO(BaseModel):
    """DTO for paginated address list."""

    items: list[AddressDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        return self.skip + len(self.items) < self.total
