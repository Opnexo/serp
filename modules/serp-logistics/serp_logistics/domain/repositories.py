"""Domain repository interfaces for logistics."""

from typing import Optional, Protocol
from uuid import UUID

from serp_logistics.domain.entities import (
    Carrier,
    DeliveryRoute,
    PackingOperation,
    PickingOperation,
    ReturnAuthorization,
    Shipment,
)
from serp_logistics.domain.value_objects import (
    PackingNumber,
    PickingNumber,
    PickingState,
    RMANumber,
    RouteNumber,
    ShipmentNumber,
    ShipmentState,
)


class IPickingOperationRepository(Protocol):
    """Picking operation repository interface."""

    def add(self, picking: PickingOperation) -> None:
        """Add picking operation."""
        ...

    def get(self, id: UUID) -> Optional[PickingOperation]:
        """Get picking by ID."""
        ...

    def get_by_number(self, number: PickingNumber) -> Optional[PickingOperation]:
        """Get picking by number."""
        ...

    def list_by_state(self, state: PickingState) -> list[PickingOperation]:
        """List pickings by state."""
        ...

    def list_by_picker(self, picker_id: UUID) -> list[PickingOperation]:
        """List pickings for a picker."""
        ...

    def update(self, picking: PickingOperation) -> None:
        """Update picking."""
        ...


class IPackingOperationRepository(Protocol):
    """Packing operation repository interface."""

    def add(self, packing: PackingOperation) -> None:
        """Add packing operation."""
        ...

    def get(self, id: UUID) -> Optional[PackingOperation]:
        """Get packing by ID."""
        ...

    def get_by_number(self, number: PackingNumber) -> Optional[PackingOperation]:
        """Get packing by number."""
        ...

    def get_by_picking(self, picking_id: UUID) -> Optional[PackingOperation]:
        """Get packing by picking operation."""
        ...

    def list_all(self) -> list[PackingOperation]:
        """List all packings."""
        ...

    def update(self, packing: PackingOperation) -> None:
        """Update packing."""
        ...


class IShipmentRepository(Protocol):
    """Shipment repository interface."""

    def add(self, shipment: Shipment) -> None:
        """Add shipment."""
        ...

    def get(self, id: UUID) -> Optional[Shipment]:
        """Get shipment by ID."""
        ...

    def get_by_number(self, number: ShipmentNumber) -> Optional[Shipment]:
        """Get shipment by number."""
        ...

    def get_by_tracking(self, tracking_number: str) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        ...

    def list_by_state(self, state: ShipmentState) -> list[Shipment]:
        """List shipments by state."""
        ...

    def list_by_carrier(self, carrier_id: UUID) -> list[Shipment]:
        """List shipments for a carrier."""
        ...

    def update(self, shipment: Shipment) -> None:
        """Update shipment."""
        ...


class ICarrierRepository(Protocol):
    """Carrier repository interface."""

    def add(self, carrier: Carrier) -> None:
        """Add carrier."""
        ...

    def get(self, id: UUID) -> Optional[Carrier]:
        """Get carrier by ID."""
        ...

    def get_by_code(self, code: str) -> Optional[Carrier]:
        """Get carrier by code."""
        ...

    def list_active(self) -> list[Carrier]:
        """List active carriers."""
        ...

    def update(self, carrier: Carrier) -> None:
        """Update carrier."""
        ...


class IDeliveryRouteRepository(Protocol):
    """Delivery route repository interface."""

    def add(self, route: DeliveryRoute) -> None:
        """Add route."""
        ...

    def get(self, id: UUID) -> Optional[DeliveryRoute]:
        """Get route by ID."""
        ...

    def get_by_number(self, number: RouteNumber) -> Optional[DeliveryRoute]:
        """Get route by number."""
        ...

    def list_by_driver(self, driver_id: UUID) -> list[DeliveryRoute]:
        """List routes for a driver."""
        ...

    def list_all(self) -> list[DeliveryRoute]:
        """List all routes."""
        ...

    def update(self, route: DeliveryRoute) -> None:
        """Update route."""
        ...


class IReturnAuthorizationRepository(Protocol):
    """Return authorization repository interface."""

    def add(self, rma: ReturnAuthorization) -> None:
        """Add RMA."""
        ...

    def get(self, id: UUID) -> Optional[ReturnAuthorization]:
        """Get RMA by ID."""
        ...

    def get_by_number(self, number: RMANumber) -> Optional[ReturnAuthorization]:
        """Get RMA by number."""
        ...

    def list_by_customer(self, customer_id: UUID) -> list[ReturnAuthorization]:
        """List RMAs for a customer."""
        ...

    def list_all(self) -> list[ReturnAuthorization]:
        """List all RMAs."""
        ...

    def update(self, rma: ReturnAuthorization) -> None:
        """Update RMA."""
        ...
