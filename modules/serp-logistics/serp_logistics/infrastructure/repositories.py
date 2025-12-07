"""In-memory repository implementations for logistics module."""

from typing import Optional
from uuid import UUID

from ..domain import (
    Carrier,
    DeliveryRoute,
    ICarrierRepository,
    IDeliveryRouteRepository,
    IPackingOperationRepository,
    IPickingOperationRepository,
    IReturnAuthorizationRepository,
    IShipmentRepository,
    PackingOperation,
    PickingOperation,
    PickingState,
    ReturnAuthorization,
    RouteNumber,
    Shipment,
    ShipmentNumber,
    ShipmentState,
    TrackingNumber,
)


class InMemoryPickingOperationRepository(IPickingOperationRepository):
    """In-memory implementation of picking repository."""

    def __init__(self) -> None:
        self._pickings: dict[UUID, PickingOperation] = {}

    def add(self, picking: PickingOperation) -> None:
        """Add picking operation."""
        self._pickings[picking.id] = picking

    def get(self, picking_id: UUID) -> PickingOperation:
        """Get picking operation by ID."""
        if picking_id not in self._pickings:
            raise ValueError(f"Picking operation {picking_id} not found")
        return self._pickings[picking_id]

    def get_by_number(self, picking_number: str) -> PickingOperation:
        """Get picking operation by number."""
        for picking in self._pickings.values():
            if picking.picking_number.value == picking_number:
                return picking
        raise ValueError(f"Picking operation {picking_number} not found")

    def list_by_state(self, state: PickingState) -> list[PickingOperation]:
        """List picking operations by state."""
        return [p for p in self._pickings.values() if p.state == state]

    def list_by_picker(self, picker_id: UUID) -> list[PickingOperation]:
        """List picking operations by picker."""
        return [p for p in self._pickings.values() if p.assigned_picker_id == picker_id]

    def update(self, picking: PickingOperation) -> None:
        """Update picking operation."""
        if picking.id not in self._pickings:
            raise ValueError(f"Picking operation {picking.id} not found")
        self._pickings[picking.id] = picking


class InMemoryPackingOperationRepository(IPackingOperationRepository):
    """In-memory implementation of packing repository."""

    def __init__(self) -> None:
        self._packings: dict[UUID, PackingOperation] = {}

    def add(self, packing: PackingOperation) -> None:
        """Add packing operation."""
        self._packings[packing.id] = packing

    def get(self, packing_id: UUID) -> PackingOperation:
        """Get packing operation by ID."""
        if packing_id not in self._packings:
            raise ValueError(f"Packing operation {packing_id} not found")
        return self._packings[packing_id]

    def get_by_number(self, packing_number: str) -> PackingOperation:
        """Get packing operation by number."""
        for packing in self._packings.values():
            if packing.packing_number.value == packing_number:
                return packing
        raise ValueError(f"Packing operation {packing_number} not found")

    def get_by_picking(self, picking_id: UUID) -> Optional[PackingOperation]:
        """Get packing operation by picking operation."""
        for packing in self._packings.values():
            if packing.picking_operation_id == picking_id:
                return packing
        return None

    def list_all(self) -> list[PackingOperation]:
        """List all packing operations."""
        return list(self._packings.values())

    def update(self, packing: PackingOperation) -> None:
        """Update packing operation."""
        if packing.id not in self._packings:
            raise ValueError(f"Packing operation {packing.id} not found")
        self._packings[packing.id] = packing


class InMemoryShipmentRepository(IShipmentRepository):
    """In-memory implementation of shipment repository."""

    def __init__(self) -> None:
        self._shipments: dict[UUID, Shipment] = {}

    def add(self, shipment: Shipment) -> None:
        """Add shipment."""
        self._shipments[shipment.id] = shipment

    def get(self, shipment_id: UUID) -> Shipment:
        """Get shipment by ID."""
        if shipment_id not in self._shipments:
            raise ValueError(f"Shipment {shipment_id} not found")
        return self._shipments[shipment_id]

    def get_by_number(self, shipment_number: ShipmentNumber) -> Shipment:
        """Get shipment by number."""
        for shipment in self._shipments.values():
            if shipment.shipment_number == shipment_number:
                return shipment
        raise ValueError(f"Shipment {shipment_number.value} not found")

    def get_by_tracking(self, tracking_number: TrackingNumber) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        for shipment in self._shipments.values():
            if shipment.tracking_number == tracking_number:
                return shipment
        return None

    def list_by_state(self, state: ShipmentState) -> list[Shipment]:
        """List shipments by state."""
        return [s for s in self._shipments.values() if s.state == state]

    def list_by_carrier(self, carrier_id: UUID) -> list[Shipment]:
        """List shipments by carrier."""
        return [s for s in self._shipments.values() if s.carrier_id == carrier_id]

    def update(self, shipment: Shipment) -> None:
        """Update shipment."""
        if shipment.id not in self._shipments:
            raise ValueError(f"Shipment {shipment.id} not found")
        self._shipments[shipment.id] = shipment


class InMemoryCarrierRepository(ICarrierRepository):
    """In-memory implementation of carrier repository."""

    def __init__(self) -> None:
        self._carriers: dict[UUID, Carrier] = {}

    def add(self, carrier: Carrier) -> None:
        """Add carrier."""
        self._carriers[carrier.id] = carrier

    def get(self, carrier_id: UUID) -> Carrier:
        """Get carrier by ID."""
        if carrier_id not in self._carriers:
            raise ValueError(f"Carrier {carrier_id} not found")
        return self._carriers[carrier_id]

    def get_by_code(self, code: str) -> Carrier:
        """Get carrier by code."""
        for carrier in self._carriers.values():
            if carrier.code == code:
                return carrier
        raise ValueError(f"Carrier {code} not found")

    def list_active(self) -> list[Carrier]:
        """List active carriers."""
        return [c for c in self._carriers.values() if c.is_active]

    def update(self, carrier: Carrier) -> None:
        """Update carrier."""
        if carrier.id not in self._carriers:
            raise ValueError(f"Carrier {carrier.id} not found")
        self._carriers[carrier.id] = carrier


class InMemoryDeliveryRouteRepository(IDeliveryRouteRepository):
    """In-memory implementation of route repository."""

    def __init__(self) -> None:
        self._routes: dict[UUID, DeliveryRoute] = {}

    def add(self, route: DeliveryRoute) -> None:
        """Add delivery route."""
        self._routes[route.id] = route

    def get(self, route_id: UUID) -> DeliveryRoute:
        """Get route by ID."""
        if route_id not in self._routes:
            raise ValueError(f"Delivery route {route_id} not found")
        return self._routes[route_id]

    def get_by_number(self, route_number: RouteNumber) -> DeliveryRoute:
        """Get route by number."""
        for route in self._routes.values():
            if route.route_number == route_number:
                return route
        raise ValueError(f"Delivery route {route_number.value} not found")

    def list_by_driver(self, driver_id: UUID) -> list[DeliveryRoute]:
        """List routes by driver."""
        return [r for r in self._routes.values() if r.driver_id == driver_id]

    def list_all(self) -> list[DeliveryRoute]:
        """List all routes."""
        return list(self._routes.values())

    def update(self, route: DeliveryRoute) -> None:
        """Update route."""
        if route.id not in self._routes:
            raise ValueError(f"Delivery route {route.id} not found")
        self._routes[route.id] = route


class InMemoryReturnAuthorizationRepository(IReturnAuthorizationRepository):
    """In-memory implementation of RMA repository."""

    def __init__(self) -> None:
        self._rmas: dict[UUID, ReturnAuthorization] = {}

    def add(self, rma: ReturnAuthorization) -> None:
        """Add return authorization."""
        self._rmas[rma.id] = rma

    def get(self, rma_id: UUID) -> ReturnAuthorization:
        """Get RMA by ID."""
        if rma_id not in self._rmas:
            raise ValueError(f"Return authorization {rma_id} not found")
        return self._rmas[rma_id]

    def get_by_number(self, rma_number: str) -> ReturnAuthorization:
        """Get RMA by number."""
        for rma in self._rmas.values():
            if rma.rma_number.value == rma_number:
                return rma
        raise ValueError(f"Return authorization {rma_number} not found")

    def list_by_customer(self, customer_id: UUID) -> list[ReturnAuthorization]:
        """List RMAs by customer."""
        return [r for r in self._rmas.values() if r.customer_id == customer_id]

    def list_all(self) -> list[ReturnAuthorization]:
        """List all RMAs."""
        return list(self._rmas.values())

    def update(self, rma: ReturnAuthorization) -> None:
        """Update RMA."""
        if rma.id not in self._rmas:
            raise ValueError(f"Return authorization {rma.id} not found")
        self._rmas[rma.id] = rma
