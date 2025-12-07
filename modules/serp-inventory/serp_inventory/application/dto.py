"""Application DTOs for inventory."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Warehouse DTOs
class WarehouseCreateDTO(BaseModel):
    """DTO for creating a warehouse."""

    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class WarehouseUpdateDTO(BaseModel):
    """DTO for updating a warehouse."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class WarehouseDTO(BaseModel):
    """DTO for warehouse response."""

    id: UUID
    code: str
    name: str
    is_active: bool
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Stock Location DTOs
class StockLocationCreateDTO(BaseModel):
    """DTO for creating a stock location."""

    location_code: str = Field(..., min_length=3, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    location_type: str  # LocationType enum value
    usage: str  # LocationUsage enum value
    warehouse_id: Optional[UUID] = None
    parent_location_id: Optional[UUID] = None
    allow_negative_stock: bool = False
    capacity: Optional[Decimal] = None
    notes: Optional[str] = None


class StockLocationUpdateDTO(BaseModel):
    """DTO for updating a stock location."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    allow_negative_stock: Optional[bool] = None
    capacity: Optional[Decimal] = None
    notes: Optional[str] = None


class StockLocationDTO(BaseModel):
    """DTO for stock location response."""

    id: UUID
    location_code: str
    name: str
    location_type: str
    usage: str
    warehouse_id: Optional[UUID] = None
    parent_location_id: Optional[UUID] = None
    is_active: bool
    allow_negative_stock: bool
    capacity: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Stock Level DTOs
class StockLevelDTO(BaseModel):
    """DTO for stock level information."""

    product_id: UUID
    product_code: str
    product_name: str
    location_id: UUID
    location_code: str
    on_hand: Decimal
    reserved: Decimal
    available: Decimal
    lot_serial_id: Optional[UUID] = None
    lot_serial_number: Optional[str] = None
    unit_cost: Optional[Decimal] = None


class StockAvailabilityDTO(BaseModel):
    """DTO for stock availability query."""

    product_id: UUID
    total_on_hand: Decimal
    total_reserved: Decimal
    total_available: Decimal
    by_location: list[StockLevelDTO]


# Stock Move DTOs
class StockMoveCreateDTO(BaseModel):
    """DTO for creating a stock move."""

    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal = Field(..., gt=0)
    uom_id: str
    source_location_id: UUID
    dest_location_id: UUID
    move_type: str  # StockMoveType enum value
    lot_serial_id: Optional[UUID] = None
    reference: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None


class StockMoveDTO(BaseModel):
    """DTO for stock move response."""

    id: UUID
    movement_number: str
    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal
    uom_id: str
    source_location_id: UUID
    dest_location_id: UUID
    move_type: str
    state: str
    lot_serial_id: Optional[UUID] = None
    reference: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    executed_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Inventory Adjustment DTOs
class AdjustmentLineDTO(BaseModel):
    """DTO for adjustment line."""

    product_id: UUID
    product_code: str
    product_name: str
    location_id: UUID
    theoretical_quantity: Decimal
    counted_quantity: Decimal
    lot_serial_id: Optional[UUID] = None


class AdjustmentLineResponseDTO(AdjustmentLineDTO):
    """DTO for adjustment line response with calculated fields."""

    id: UUID
    difference: Decimal


class InventoryAdjustmentCreateDTO(BaseModel):
    """DTO for creating an inventory adjustment."""

    reason: str  # AdjustmentReason enum value
    lines: list[AdjustmentLineDTO]
    notes: Optional[str] = None


class InventoryAdjustmentDTO(BaseModel):
    """DTO for inventory adjustment response."""

    id: UUID
    adjustment_number: str
    reason: str
    state: str
    lines: list[AdjustmentLineResponseDTO]
    notes: Optional[str] = None
    adjustment_date: datetime
    confirmed_date: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Reordering Rule DTOs
class ReorderingRuleCreateDTO(BaseModel):
    """DTO for creating a reordering rule."""

    product_id: UUID
    location_id: UUID
    min_quantity: Decimal = Field(..., ge=0)
    max_quantity: Decimal = Field(..., gt=0)
    quantity_to_order: Decimal = Field(..., gt=0)
    route: str  # ReorderRoute enum value
    lead_time_days: int = Field(default=0, ge=0)
    supplier_id: Optional[UUID] = None


class ReorderingRuleUpdateDTO(BaseModel):
    """DTO for updating a reordering rule."""

    min_quantity: Optional[Decimal] = Field(None, ge=0)
    max_quantity: Optional[Decimal] = Field(None, gt=0)
    quantity_to_order: Optional[Decimal] = Field(None, gt=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    supplier_id: Optional[UUID] = None


class ReorderingRuleDTO(BaseModel):
    """DTO for reordering rule response."""

    id: UUID
    product_id: UUID
    location_id: UUID
    min_quantity: Decimal
    max_quantity: Decimal
    quantity_to_order: Decimal
    route: str
    lead_time_days: int
    is_active: bool
    supplier_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReorderSuggestionDTO(BaseModel):
    """DTO for reorder suggestion."""

    rule_id: UUID
    product_id: UUID
    product_code: str
    product_name: str
    location_id: UUID
    current_quantity: Decimal
    min_quantity: Decimal
    suggested_quantity: Decimal
    route: str
    supplier_id: Optional[UUID] = None


# Lot/Serial DTOs
class LotSerialCreateDTO(BaseModel):
    """DTO for creating a lot/serial."""

    lot_serial_number: str = Field(..., min_length=1, max_length=50)
    product_id: UUID
    is_serial: bool = False
    expiration_date: Optional[date] = None
    manufacture_date: Optional[date] = None
    notes: Optional[str] = None


class LotSerialDTO(BaseModel):
    """DTO for lot/serial response."""

    id: UUID
    lot_serial_number: str
    product_id: UUID
    is_serial: bool
    expiration_date: Optional[date] = None
    manufacture_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class LotTraceDTO(BaseModel):
    """DTO for lot traceability."""

    lot_id: UUID
    lot_serial_number: str
    product_id: UUID
    movements: list[StockMoveDTO]
