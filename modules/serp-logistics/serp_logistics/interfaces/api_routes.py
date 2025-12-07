"""API routes for logistics module."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from serp_core.application import get_event_publisher
from serp_core.domain import DomainEventPublisher
from serp_users.interfaces import require_permissions

from ..application import (
    RMADTO,
    CarrierCreateDTO,
    CarrierDTO,
    CarrierService,
    CarrierUpdateDTO,
    PackageCreateDTO,
    PackageItemAddDTO,
    PackingCreateDTO,
    PackingDTO,
    PackingService,
    PickingAssignDTO,
    PickingCreateDTO,
    PickingDTO,
    PickingPickDTO,
    PickingService,
    RMAApproveDTO,
    RMACreateDTO,
    RMAProcessDTO,
    RMARejectDTO,
    RMAService,
    RMAShipDTO,
    RouteCompleteStopDTO,
    RouteCreateDTO,
    RouteDTO,
    RouteService,
    RouteStopCreateDTO,
    ShipmentConfirmDTO,
    ShipmentCreateDTO,
    ShipmentDTO,
    ShipmentService,
    ShipmentUpdateStatusDTO,
)
from ..infrastructure import (
    InMemoryCarrierRepository,
    InMemoryDeliveryRouteRepository,
    InMemoryPackingOperationRepository,
    InMemoryPickingOperationRepository,
    InMemoryReturnAuthorizationRepository,
    InMemoryShipmentRepository,
)
from .permissions import (
    CARRIER_CREATE,
    CARRIER_UPDATE,
    CARRIER_VIEW,
    PACKING_COMPLETE,
    PACKING_CREATE,
    PACKING_EXECUTE,
    PACKING_VIEW,
    PICKING_ASSIGN,
    PICKING_CANCEL,
    PICKING_COMPLETE,
    PICKING_CREATE,
    PICKING_EXECUTE,
    PICKING_VIEW,
    RMA_APPROVE,
    RMA_CREATE,
    RMA_PROCESS,
    RMA_REJECT,
    RMA_VIEW,
    ROUTE_CREATE,
    ROUTE_EXECUTE,
    ROUTE_UPDATE,
    ROUTE_VIEW,
    SHIPMENT_CANCEL,
    SHIPMENT_CONFIRM,
    SHIPMENT_CREATE,
    SHIPMENT_UPDATE,
    SHIPMENT_VIEW,
)

# Create routers
picking_router = APIRouter(prefix="/picking", tags=["picking"])
packing_router = APIRouter(prefix="/packing", tags=["packing"])
shipment_router = APIRouter(prefix="/shipments", tags=["shipments"])
carrier_router = APIRouter(prefix="/carriers", tags=["carriers"])
route_router = APIRouter(prefix="/routes", tags=["routes"])
rma_router = APIRouter(prefix="/rma", tags=["rma"])

# Repository singletons (would be replaced with proper DI in production)
_picking_repo = InMemoryPickingOperationRepository()
_packing_repo = InMemoryPackingOperationRepository()
_shipment_repo = InMemoryShipmentRepository()
_carrier_repo = InMemoryCarrierRepository()
_route_repo = InMemoryDeliveryRouteRepository()
_rma_repo = InMemoryReturnAuthorizationRepository()


def get_picking_service(
    event_publisher: DomainEventPublisher = Depends(get_event_publisher),
) -> PickingService:
    """Get picking service dependency."""
    return PickingService(_picking_repo, event_publisher)


def get_packing_service(
    event_publisher: DomainEventPublisher = Depends(get_event_publisher),
) -> PackingService:
    """Get packing service dependency."""
    return PackingService(_packing_repo, event_publisher)


def get_shipment_service(
    event_publisher: DomainEventPublisher = Depends(get_event_publisher),
) -> ShipmentService:
    """Get shipment service dependency."""
    return ShipmentService(_shipment_repo, event_publisher)


def get_carrier_service() -> CarrierService:
    """Get carrier service dependency."""
    return CarrierService(_carrier_repo)


def get_route_service(
    event_publisher: DomainEventPublisher = Depends(get_event_publisher),
) -> RouteService:
    """Get route service dependency."""
    return RouteService(_route_repo, event_publisher)


def get_rma_service(
    event_publisher: DomainEventPublisher = Depends(get_event_publisher),
) -> RMAService:
    """Get RMA service dependency."""
    return RMAService(_rma_repo, event_publisher)


# ===== Picking Routes =====


@picking_router.post(
    "/",
    response_model=PickingDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PICKING_CREATE))],
)
def create_picking(
    dto: PickingCreateDTO,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Create new picking operation."""
    return service.create_picking(dto)


@picking_router.get(
    "/{picking_id}",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_VIEW))],
)
def get_picking(
    picking_id: UUID,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Get picking operation by ID."""
    return service.get_picking(picking_id)


@picking_router.post(
    "/{picking_id}/assign",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_ASSIGN))],
)
def assign_picker(
    picking_id: UUID,
    dto: PickingAssignDTO,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Assign picker to operation."""
    return service.assign_picker(picking_id, dto)


@picking_router.post(
    "/{picking_id}/start",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_EXECUTE))],
)
def start_picking(
    picking_id: UUID,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Start picking operation."""
    return service.start_picking(picking_id)


@picking_router.post(
    "/{picking_id}/pick",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_EXECUTE))],
)
def pick_line(
    picking_id: UUID,
    dto: PickingPickDTO,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Pick line quantity."""
    return service.pick_line(picking_id, dto)


@picking_router.post(
    "/{picking_id}/complete",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_COMPLETE))],
)
def complete_picking(
    picking_id: UUID,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Complete picking operation."""
    return service.complete_picking(picking_id)


@picking_router.post(
    "/{picking_id}/cancel",
    response_model=PickingDTO,
    dependencies=[Depends(require_permissions(PICKING_CANCEL))],
)
def cancel_picking(
    picking_id: UUID,
    service: PickingService = Depends(get_picking_service),
) -> PickingDTO:
    """Cancel picking operation."""
    return service.cancel_picking(picking_id)


# ===== Packing Routes =====


@packing_router.post(
    "/",
    response_model=PackingDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PACKING_CREATE))],
)
def create_packing(
    dto: PackingCreateDTO,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Create new packing operation."""
    return service.create_packing(dto)


@packing_router.get(
    "/{packing_id}",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_VIEW))],
)
def get_packing(
    packing_id: UUID,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Get packing operation by ID."""
    return service.get_packing(packing_id)


@packing_router.post(
    "/{packing_id}/packages",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_EXECUTE))],
)
def add_package(
    packing_id: UUID,
    dto: PackageCreateDTO,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Add package to packing operation."""
    return service.add_package(packing_id, dto)


@packing_router.post(
    "/{packing_id}/packages/{package_id}/items",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_EXECUTE))],
)
def add_item_to_package(
    packing_id: UUID,
    package_id: UUID,
    dto: PackageItemAddDTO,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Add item to package."""
    return service.add_item_to_package(packing_id, package_id, dto)


@packing_router.post(
    "/{packing_id}/start",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_EXECUTE))],
)
def start_packing(
    packing_id: UUID,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Start packing operation."""
    return service.start_packing(packing_id)


@packing_router.post(
    "/{packing_id}/complete",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_COMPLETE))],
)
def complete_packing(
    packing_id: UUID,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Complete packing operation."""
    return service.complete_packing(packing_id)


@packing_router.post(
    "/{packing_id}/shipped",
    response_model=PackingDTO,
    dependencies=[Depends(require_permissions(PACKING_COMPLETE))],
)
def mark_packing_shipped(
    packing_id: UUID,
    service: PackingService = Depends(get_packing_service),
) -> PackingDTO:
    """Mark packing as shipped."""
    return service.mark_shipped(packing_id)


# ===== Shipment Routes =====


@shipment_router.post(
    "/",
    response_model=ShipmentDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(SHIPMENT_CREATE))],
)
def create_shipment(
    dto: ShipmentCreateDTO,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Create new shipment."""
    return service.create_shipment(dto)


@shipment_router.get(
    "/{shipment_id}",
    response_model=ShipmentDTO,
    dependencies=[Depends(require_permissions(SHIPMENT_VIEW))],
)
def get_shipment(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Get shipment by ID."""
    return service.get_shipment(shipment_id)


@shipment_router.post(
    "/{shipment_id}/confirm",
    response_model=ShipmentDTO,
    dependencies=[Depends(require_permissions(SHIPMENT_CONFIRM))],
)
def confirm_shipment(
    shipment_id: UUID,
    dto: ShipmentConfirmDTO,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Confirm shipment with tracking."""
    return service.confirm_shipment(shipment_id, dto)


@shipment_router.post(
    "/{shipment_id}/pickup",
    response_model=ShipmentDTO,
    dependencies=[Depends(require_permissions(SHIPMENT_UPDATE))],
)
def mark_shipment_picked_up(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Mark shipment picked up."""
    return service.mark_picked_up(shipment_id)


@shipment_router.post(
    "/{shipment_id}/status",
    response_model=ShipmentDTO,
    dependencies=[Depends(require_permissions(SHIPMENT_UPDATE))],
)
def update_shipment_status(
    shipment_id: UUID,
    dto: ShipmentUpdateStatusDTO,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Update shipment tracking status."""
    return service.update_status(shipment_id, dto)


@shipment_router.post(
    "/{shipment_id}/cancel",
    response_model=ShipmentDTO,
    dependencies=[Depends(require_permissions(SHIPMENT_CANCEL))],
)
def cancel_shipment(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Cancel shipment."""
    return service.cancel_shipment(shipment_id)


# ===== Carrier Routes =====


@carrier_router.post(
    "/",
    response_model=CarrierDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(CARRIER_CREATE))],
)
def create_carrier(
    dto: CarrierCreateDTO,
    service: CarrierService = Depends(get_carrier_service),
) -> CarrierDTO:
    """Create new carrier."""
    return service.create_carrier(dto)


@carrier_router.get(
    "/{carrier_id}",
    response_model=CarrierDTO,
    dependencies=[Depends(require_permissions(CARRIER_VIEW))],
)
def get_carrier(
    carrier_id: UUID,
    service: CarrierService = Depends(get_carrier_service),
) -> CarrierDTO:
    """Get carrier by ID."""
    return service.get_carrier(carrier_id)


@carrier_router.put(
    "/{carrier_id}",
    response_model=CarrierDTO,
    dependencies=[Depends(require_permissions(CARRIER_UPDATE))],
)
def update_carrier(
    carrier_id: UUID,
    dto: CarrierUpdateDTO,
    service: CarrierService = Depends(get_carrier_service),
) -> CarrierDTO:
    """Update carrier."""
    return service.update_carrier(carrier_id, dto)


@carrier_router.get(
    "/",
    response_model=list[CarrierDTO],
    dependencies=[Depends(require_permissions(CARRIER_VIEW))],
)
def list_active_carriers(
    service: CarrierService = Depends(get_carrier_service),
) -> list[CarrierDTO]:
    """List active carriers."""
    return service.list_active_carriers()


# ===== Route Routes =====


@route_router.post(
    "/",
    response_model=RouteDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(ROUTE_CREATE))],
)
def create_route(
    dto: RouteCreateDTO,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Create new delivery route."""
    return service.create_route(dto)


@route_router.get(
    "/{route_id}",
    response_model=RouteDTO,
    dependencies=[Depends(require_permissions(ROUTE_VIEW))],
)
def get_route(
    route_id: UUID,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Get delivery route by ID."""
    return service.get_route(route_id)


@route_router.post(
    "/{route_id}/stops",
    response_model=RouteDTO,
    dependencies=[Depends(require_permissions(ROUTE_UPDATE))],
)
def add_route_stop(
    route_id: UUID,
    dto: RouteStopCreateDTO,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Add stop to route."""
    return service.add_stop(route_id, dto)


@route_router.post(
    "/{route_id}/start",
    response_model=RouteDTO,
    dependencies=[Depends(require_permissions(ROUTE_EXECUTE))],
)
def start_route(
    route_id: UUID,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Start delivery route."""
    return service.start_route(route_id)


@route_router.post(
    "/{route_id}/stops/{stop_id}/complete",
    response_model=RouteDTO,
    dependencies=[Depends(require_permissions(ROUTE_EXECUTE))],
)
def complete_route_stop(
    route_id: UUID,
    stop_id: UUID,
    dto: RouteCompleteStopDTO,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Complete route stop."""
    return service.complete_stop(route_id, stop_id, dto)


@route_router.post(
    "/{route_id}/complete",
    response_model=RouteDTO,
    dependencies=[Depends(require_permissions(ROUTE_EXECUTE))],
)
def complete_route(
    route_id: UUID,
    service: RouteService = Depends(get_route_service),
) -> RouteDTO:
    """Complete delivery route."""
    return service.complete_route(route_id)


# ===== RMA Routes =====


@rma_router.post(
    "/",
    response_model=RMADTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(RMA_CREATE))],
)
def create_rma(
    dto: RMACreateDTO,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Create new return authorization."""
    return service.create_rma(dto)


@rma_router.get(
    "/{rma_id}",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_VIEW))],
)
def get_rma(
    rma_id: UUID,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Get return authorization by ID."""
    return service.get_rma(rma_id)


@rma_router.post(
    "/{rma_id}/approve",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_APPROVE))],
)
def approve_rma(
    rma_id: UUID,
    dto: RMAApproveDTO,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Approve return authorization."""
    return service.approve_rma(rma_id, dto)


@rma_router.post(
    "/{rma_id}/reject",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_REJECT))],
)
def reject_rma(
    rma_id: UUID,
    dto: RMARejectDTO,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Reject return authorization."""
    return service.reject_rma(rma_id, dto)


@rma_router.post(
    "/{rma_id}/ship",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_VIEW))],
)
def mark_rma_shipped(
    rma_id: UUID,
    dto: RMAShipDTO,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Mark RMA shipped by customer."""
    return service.mark_rma_shipped(rma_id, dto)


@rma_router.post(
    "/{rma_id}/receive",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_VIEW))],
)
def receive_rma(
    rma_id: UUID,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Receive return shipment."""
    return service.receive_rma(rma_id)


@rma_router.post(
    "/{rma_id}/process",
    response_model=RMADTO,
    dependencies=[Depends(require_permissions(RMA_PROCESS))],
)
def process_rma(
    rma_id: UUID,
    dto: RMAProcessDTO,
    service: RMAService = Depends(get_rma_service),
) -> RMADTO:
    """Process return (refund/exchange)."""
    return service.process_rma(rma_id, dto)


__all__ = [
    "picking_router",
    "packing_router",
    "shipment_router",
    "carrier_router",
    "route_router",
    "rma_router",
]
