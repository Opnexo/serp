"""Application DTOs for logistics module."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from serp_crm.domain import Money

from ..domain import (
    PackingState,
    PickingState,
    PickingStrategy,
    RMAAction,
    RMAState,
    RouteState,
    ServiceLevel,
    ShipmentState,
)


# ===== Picking DTOs =====
class PickingLineCreateDTO(BaseModel):
    """DTO for creating picking line."""

    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal
    source_location_id: UUID


class PickingLineDTO(PickingLineCreateDTO):
    """DTO for picking line."""

    id: UUID
    quantity_ordered: Decimal
    quantity_picked: Decimal
    quantity_remaining: Decimal
    lot_serial_id: Optional[UUID] = None
    is_fully_picked: bool


class PickingCreateDTO(BaseModel):
    """DTO for creating picking operation."""

    strategy: PickingStrategy
    source_document_type: str
    source_document_id: UUID
    lines: list[PickingLineCreateDTO]


class PickingAssignDTO(BaseModel):
    """DTO for assigning picker."""

    picker_id: UUID


class PickingPickDTO(BaseModel):
    """DTO for picking line."""

    line_id: UUID
    quantity: Decimal
    lot_serial_id: Optional[UUID] = None


class PickingDTO(BaseModel):
    """DTO for picking operation."""

    id: UUID
    picking_number: str
    strategy: PickingStrategy
    source_document_type: str
    source_document_id: UUID
    lines: list[PickingLineDTO]
    assigned_picker_id: Optional[UUID] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state: PickingState
    created_at: datetime
    updated_at: datetime


# ===== Packing DTOs =====
class PackageItemDTO(BaseModel):
    """DTO for package item."""

    id: UUID
    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal
    lot_serial_id: Optional[UUID] = None


class PackageDimensionsDTO(BaseModel):
    """DTO for package dimensions."""

    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    volume_cm3: Decimal


class PackageDTO(BaseModel):
    """DTO for package."""

    id: UUID
    box_type: str
    dimensions: PackageDimensionsDTO
    weight_kg: Decimal
    items: list[PackageItemDTO]
    tracking_number: Optional[str] = None
    total_weight: Decimal
    dimensional_weight: Decimal
    billable_weight: Decimal


class PackageCreateDTO(BaseModel):
    """DTO for creating package."""

    box_type: str
    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    weight_kg: Decimal


class PackageItemAddDTO(BaseModel):
    """DTO for adding item to package."""

    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal
    lot_serial_id: Optional[UUID] = None


class PackingCreateDTO(BaseModel):
    """DTO for creating packing operation."""

    picking_operation_id: UUID
    packer_id: UUID


class PackingDTO(BaseModel):
    """DTO for packing operation."""

    id: UUID
    packing_number: str
    picking_operation_id: UUID
    packages: list[PackageDTO]
    packer_id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state: PackingState
    created_at: datetime
    updated_at: datetime


# ===== Shipment DTOs =====
class AddressDTO(BaseModel):
    """DTO for address."""

    name: str
    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_residential: bool = False


class ShipmentCreateDTO(BaseModel):
    """DTO for creating shipment."""

    packing_operation_id: UUID
    carrier_id: UUID
    service_level: ServiceLevel
    delivery_address: AddressDTO
    insurance_value: Optional[Decimal] = None
    require_signature: bool = False


class ShipmentConfirmDTO(BaseModel):
    """DTO for confirming shipment."""

    tracking_number: str
    shipping_cost: Decimal
    currency: str


class ShipmentUpdateStatusDTO(BaseModel):
    """DTO for updating shipment status."""

    new_state: ShipmentState
    delivery_proof: Optional[str] = None


class ShipmentDTO(BaseModel):
    """DTO for shipment."""

    id: UUID
    shipment_number: str
    packing_operation_id: UUID
    carrier_id: UUID
    service_level: ServiceLevel
    delivery_address: AddressDTO
    tracking_number: Optional[str] = None
    shipping_cost: Optional[Money] = None
    insurance_value: Optional[Decimal] = None
    require_signature: bool
    confirmed_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_proof: Optional[str] = None
    state: ShipmentState
    created_at: datetime
    updated_at: datetime


# ===== Carrier DTOs =====
class CarrierCreateDTO(BaseModel):
    """DTO for creating carrier."""

    code: str
    name: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    account_number: Optional[str] = None
    tracking_url_template: Optional[str] = None
    supports_labels: bool = False
    supports_tracking: bool = False


class CarrierUpdateDTO(BaseModel):
    """DTO for updating carrier."""

    name: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    account_number: Optional[str] = None
    tracking_url_template: Optional[str] = None
    supports_labels: Optional[bool] = None
    supports_tracking: Optional[bool] = None
    is_active: Optional[bool] = None


class CarrierDTO(BaseModel):
    """DTO for carrier."""

    id: UUID
    code: str
    name: str
    is_active: bool
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    account_number: Optional[str] = None
    tracking_url_template: Optional[str] = None
    supports_labels: bool
    supports_tracking: bool
    created_at: datetime
    updated_at: datetime


# ===== Route DTOs =====
class RouteStopDTO(BaseModel):
    """DTO for route stop."""

    id: UUID
    shipment_id: UUID
    delivery_address: AddressDTO
    sequence: int
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    completed: bool
    notes: Optional[str] = None


class RouteStopCreateDTO(BaseModel):
    """DTO for creating route stop."""

    shipment_id: UUID
    delivery_address: AddressDTO
    estimated_arrival: Optional[datetime] = None


class RouteCreateDTO(BaseModel):
    """DTO for creating delivery route."""

    route_date: date
    driver_id: UUID
    vehicle_id: Optional[UUID] = None
    stops: list[RouteStopCreateDTO] = Field(default_factory=list)


class RouteCompleteStopDTO(BaseModel):
    """DTO for completing stop."""

    notes: Optional[str] = None


class RouteDTO(BaseModel):
    """DTO for delivery route."""

    id: UUID
    route_number: str
    route_date: date
    driver_id: UUID
    vehicle_id: Optional[UUID] = None
    stops: list[RouteStopDTO]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state: RouteState
    created_at: datetime
    updated_at: datetime


# ===== RMA DTOs =====
class RMALineCreateDTO(BaseModel):
    """DTO for creating RMA line."""

    product_id: UUID
    product_code: str
    product_name: str
    quantity: Decimal
    reason: str
    condition: str


class RMALineDTO(RMALineCreateDTO):
    """DTO for RMA line."""

    id: UUID


class RMACreateDTO(BaseModel):
    """DTO for creating RMA."""

    original_shipment_id: UUID
    customer_id: UUID
    action: RMAAction
    lines: list[RMALineCreateDTO]


class RMAApproveDTO(BaseModel):
    """DTO for approving RMA."""

    return_address: AddressDTO


class RMARejectDTO(BaseModel):
    """DTO for rejecting RMA."""

    reason: str


class RMAShipDTO(BaseModel):
    """DTO for marking RMA shipped."""

    tracking_number: str


class RMAProcessDTO(BaseModel):
    """DTO for processing RMA."""

    refund_amount: Decimal
    currency: str


class RMADTO(BaseModel):
    """DTO for RMA."""

    id: UUID
    rma_number: str
    original_shipment_id: UUID
    customer_id: UUID
    action: RMAAction
    lines: list[RMALineDTO]
    return_address: Optional[AddressDTO] = None
    return_tracking_number: Optional[str] = None
    requested_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    refund_amount: Optional[Money] = None
    state: RMAState
    created_at: datetime
    updated_at: datetime
