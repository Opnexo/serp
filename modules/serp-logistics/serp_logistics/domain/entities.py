"""Domain entities for logistics."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from serp_core.domain import AggregateRoot, Entity
from serp_crm.domain import Money

from serp_logistics.domain.value_objects import (
    Address,
    PackageDimensions,
    PackingNumber,
    PackingState,
    PickingNumber,
    PickingState,
    PickingStrategy,
    RMAAction,
    RMANumber,
    RMAState,
    RouteNumber,
    RouteState,
    ServiceLevel,
    ShipmentNumber,
    ShipmentState,
    TrackingNumber,
    Weight,
)


class PickingLine(Entity):
    """Picking line (owned entity)."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity_ordered: Decimal,
        quantity_picked: Decimal,
        source_location_id: UUID,
        lot_serial_id: Optional[UUID] = None,
    ):
        """Initialize picking line."""
        super().__init__(id)
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.quantity_ordered = quantity_ordered
        self.quantity_picked = quantity_picked
        self.source_location_id = source_location_id
        self.lot_serial_id = lot_serial_id

    @property
    def quantity_remaining(self) -> Decimal:
        """Calculate remaining quantity."""
        return self.quantity_ordered - self.quantity_picked

    @property
    def is_fully_picked(self) -> bool:
        """Check if line is fully picked."""
        return self.quantity_picked >= self.quantity_ordered

    def pick(self, quantity: Decimal, lot_serial_id: Optional[UUID] = None) -> None:
        """Record picked quantity."""
        if quantity > self.quantity_remaining:
            raise ValueError(
                f"Cannot pick {quantity}, only {self.quantity_remaining} remaining"
            )
        self.quantity_picked += quantity
        if lot_serial_id:
            self.lot_serial_id = lot_serial_id


class PickingOperation(AggregateRoot):
    """Picking operation aggregate root."""

    def __init__(
        self,
        id: UUID,
        picking_number: PickingNumber,
        strategy: PickingStrategy,
        source_document: str,
        source_document_type: str,
        source_document_id: Optional[UUID] = None,
        state: PickingState = PickingState.PENDING,
        lines: Optional[list[PickingLine]] = None,
        assigned_picker_id: Optional[UUID] = None,
        assigned_date: Optional[datetime] = None,
        started_date: Optional[datetime] = None,
        completed_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize picking operation."""
        super().__init__(id, created_at, updated_at)
        self.picking_number = picking_number
        self.strategy = strategy
        self.source_document = source_document
        self.source_document_type = source_document_type
        self.source_document_id = source_document_id
        self.state = state
        self.lines = lines or []
        self.assigned_picker_id = assigned_picker_id
        self.assigned_date = assigned_date
        self.started_date = started_date
        self.completed_date = completed_date
        self.notes = notes

    @classmethod
    def create(
        cls,
        picking_number: PickingNumber,
        strategy: PickingStrategy,
        source_document: str,
        source_document_type: str,
        source_document_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> "PickingOperation":
        """Create new picking operation."""
        picking = cls(
            id=uuid4(),
            picking_number=picking_number,
            strategy=strategy,
            source_document=source_document,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            notes=notes,
            created_at=datetime.now(),
        )
        picking.add_domain_event(
            "PickingOperationCreated",
            {
                "picking_id": str(picking.id),
                "picking_number": str(picking_number),
                "strategy": strategy.value,
                "source_document": source_document,
            },
        )
        return picking

    def add_line(
        self,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity_ordered: Decimal,
        source_location_id: UUID,
        lot_serial_id: Optional[UUID] = None,
    ) -> None:
        """Add picking line."""
        if self.state != PickingState.PENDING:
            raise ValueError("Cannot add lines to non-pending picking")

        line = PickingLine(
            id=uuid4(),
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity_ordered=quantity_ordered,
            quantity_picked=Decimal("0"),
            source_location_id=source_location_id,
            lot_serial_id=lot_serial_id,
        )
        self.lines.append(line)

    def assign(self, picker_id: UUID) -> None:
        """Assign to picker."""
        if self.state != PickingState.PENDING:
            raise ValueError(f"Cannot assign picking in state {self.state}")
        self.assigned_picker_id = picker_id
        self.assigned_date = datetime.now()
        self.state = PickingState.ASSIGNED
        self.add_domain_event(
            "PickingOperationAssigned",
            {
                "picking_id": str(self.id),
                "picking_number": str(self.picking_number),
                "picker_id": str(picker_id),
            },
        )

    def start(self) -> None:
        """Start picking."""
        if self.state != PickingState.ASSIGNED:
            raise ValueError(f"Cannot start picking in state {self.state}")
        self.state = PickingState.IN_PROGRESS
        self.started_date = datetime.now()
        self.add_domain_event(
            "PickingOperationStarted",
            {
                "picking_id": str(self.id),
                "picking_number": str(self.picking_number),
            },
        )

    def complete(self) -> None:
        """Complete picking."""
        if self.state != PickingState.IN_PROGRESS:
            raise ValueError(f"Cannot complete picking in state {self.state}")
        if not all(line.is_fully_picked for line in self.lines):
            raise ValueError("Cannot complete picking with unpicked lines")

        self.state = PickingState.COMPLETED
        self.completed_date = datetime.now()
        self.add_domain_event(
            "PickingOperationCompleted",
            {
                "picking_id": str(self.id),
                "picking_number": str(self.picking_number),
                "line_count": len(self.lines),
            },
        )

    def cancel(self) -> None:
        """Cancel picking."""
        if self.state == PickingState.COMPLETED:
            raise ValueError("Cannot cancel completed picking")
        self.state = PickingState.CANCELLED
        self.add_domain_event(
            "PickingOperationCancelled",
            {
                "picking_id": str(self.id),
                "picking_number": str(self.picking_number),
            },
        )


class PackageItem(Entity):
    """Package item (owned entity)."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ):
        """Initialize package item."""
        super().__init__(id)
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.quantity = quantity
        self.lot_serial_id = lot_serial_id


class Package(Entity):
    """Package (owned entity)."""

    def __init__(
        self,
        id: UUID,
        box_type: str,
        dimensions: PackageDimensions,
        weight: Weight,
        items: Optional[list[PackageItem]] = None,
        tracking_number: Optional[TrackingNumber] = None,
    ):
        """Initialize package."""
        super().__init__(id)
        self.box_type = box_type
        self.dimensions = dimensions
        self.weight = weight
        self.items = items or []
        self.tracking_number = tracking_number

    def add_item(
        self,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ) -> None:
        """Add item to package."""
        item = PackageItem(
            id=uuid4(),
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            lot_serial_id=lot_serial_id,
        )
        self.items.append(item)

    @property
    def total_weight(self) -> Weight:
        """Get total weight (actual weight)."""
        return self.weight

    @property
    def dimensional_weight(self) -> Weight:
        """Calculate dimensional weight."""
        dim_kg = self.dimensions.dimensional_weight_kg()
        return Weight(kg=dim_kg)

    @property
    def billable_weight(self) -> Weight:
        """Get billable weight (max of actual and dimensional)."""
        return (
            self.weight
            if self.weight.kg > self.dimensional_weight.kg
            else self.dimensional_weight
        )


class PackingOperation(AggregateRoot):
    """Packing operation aggregate root."""

    def __init__(
        self,
        id: UUID,
        packing_number: PackingNumber,
        picking_operation_id: UUID,
        state: PackingState = PackingState.PENDING,
        packages: Optional[list[Package]] = None,
        packer_id: Optional[UUID] = None,
        started_date: Optional[datetime] = None,
        completed_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize packing operation."""
        super().__init__(id, created_at, updated_at)
        self.packing_number = packing_number
        self.picking_operation_id = picking_operation_id
        self.state = state
        self.packages = packages or []
        self.packer_id = packer_id
        self.started_date = started_date
        self.completed_date = completed_date
        self.notes = notes

    @classmethod
    def create(
        cls,
        packing_number: PackingNumber,
        picking_operation_id: UUID,
        packer_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> "PackingOperation":
        """Create new packing operation."""
        packing = cls(
            id=uuid4(),
            packing_number=packing_number,
            picking_operation_id=picking_operation_id,
            packer_id=packer_id,
            notes=notes,
            created_at=datetime.now(),
        )
        packing.add_domain_event(
            "PackingOperationCreated",
            {
                "packing_id": str(packing.id),
                "packing_number": str(packing_number),
                "picking_operation_id": str(picking_operation_id),
            },
        )
        return packing

    def add_package(
        self,
        box_type: str,
        dimensions: PackageDimensions,
        weight: Weight,
        tracking_number: Optional[TrackingNumber] = None,
    ) -> Package:
        """Add package to packing."""
        package = Package(
            id=uuid4(),
            box_type=box_type,
            dimensions=dimensions,
            weight=weight,
            tracking_number=tracking_number,
        )
        self.packages.append(package)
        return package

    def start(self) -> None:
        """Start packing."""
        if self.state != PackingState.PENDING:
            raise ValueError(f"Cannot start packing in state {self.state}")
        self.state = PackingState.IN_PROGRESS
        self.started_date = datetime.now()
        self.add_domain_event(
            "PackingOperationStarted",
            {
                "packing_id": str(self.id),
                "packing_number": str(self.packing_number),
            },
        )

    def complete(self) -> None:
        """Complete packing."""
        if self.state != PackingState.IN_PROGRESS:
            raise ValueError(f"Cannot complete packing in state {self.state}")
        if not self.packages:
            raise ValueError("Cannot complete packing without packages")

        self.state = PackingState.COMPLETED
        self.completed_date = datetime.now()
        self.add_domain_event(
            "PackingOperationCompleted",
            {
                "packing_id": str(self.id),
                "packing_number": str(self.packing_number),
                "package_count": len(self.packages),
            },
        )

    def mark_shipped(self) -> None:
        """Mark as shipped."""
        if self.state != PackingState.COMPLETED:
            raise ValueError("Can only ship completed packing")
        self.state = PackingState.SHIPPED
        self.add_domain_event(
            "PackingOperationShipped",
            {
                "packing_id": str(self.id),
                "packing_number": str(self.packing_number),
            },
        )


class Shipment(AggregateRoot):
    """Shipment aggregate root."""

    def __init__(
        self,
        id: UUID,
        shipment_number: ShipmentNumber,
        packing_operation_id: UUID,
        carrier_id: UUID,
        service_level: ServiceLevel,
        delivery_address: Address,
        state: ShipmentState = ShipmentState.DRAFT,
        tracking_number: Optional[TrackingNumber] = None,
        shipping_cost: Optional[Money] = None,
        insurance_value: Optional[Money] = None,
        require_signature: bool = False,
        confirmed_date: Optional[datetime] = None,
        pickup_date: Optional[datetime] = None,
        delivery_date: Optional[datetime] = None,
        delivery_proof: Optional[str] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize shipment."""
        super().__init__(id, created_at, updated_at)
        self.shipment_number = shipment_number
        self.packing_operation_id = packing_operation_id
        self.carrier_id = carrier_id
        self.service_level = service_level
        self.delivery_address = delivery_address
        self.state = state
        self.tracking_number = tracking_number
        self.shipping_cost = shipping_cost
        self.insurance_value = insurance_value
        self.require_signature = require_signature
        self.confirmed_date = confirmed_date
        self.pickup_date = pickup_date
        self.delivery_date = delivery_date
        self.delivery_proof = delivery_proof
        self.notes = notes

    @classmethod
    def create(
        cls,
        shipment_number: ShipmentNumber,
        packing_operation_id: UUID,
        carrier_id: UUID,
        service_level: ServiceLevel,
        delivery_address: Address,
        insurance_value: Optional[Money] = None,
        require_signature: bool = False,
        notes: Optional[str] = None,
    ) -> "Shipment":
        """Create new shipment."""
        shipment = cls(
            id=uuid4(),
            shipment_number=shipment_number,
            packing_operation_id=packing_operation_id,
            carrier_id=carrier_id,
            service_level=service_level,
            delivery_address=delivery_address,
            insurance_value=insurance_value,
            require_signature=require_signature,
            notes=notes,
            created_at=datetime.now(),
        )
        shipment.add_domain_event(
            "ShipmentCreated",
            {
                "shipment_id": str(shipment.id),
                "shipment_number": str(shipment_number),
                "carrier_id": str(carrier_id),
            },
        )
        return shipment

    def confirm(self, tracking_number: TrackingNumber, shipping_cost: Money) -> None:
        """Confirm shipment with tracking and cost."""
        if self.state != ShipmentState.DRAFT:
            raise ValueError(f"Cannot confirm shipment in state {self.state}")
        self.tracking_number = tracking_number
        self.shipping_cost = shipping_cost
        self.state = ShipmentState.CONFIRMED
        self.confirmed_date = datetime.now()
        self.add_domain_event(
            "ShipmentConfirmed",
            {
                "shipment_id": str(self.id),
                "shipment_number": str(self.shipment_number),
                "tracking_number": str(tracking_number),
            },
        )

    def mark_picked_up(self) -> None:
        """Mark as picked up by carrier."""
        if self.state != ShipmentState.CONFIRMED:
            raise ValueError("Can only mark confirmed shipments as picked up")
        self.state = ShipmentState.PICKED_UP
        self.pickup_date = datetime.now()
        self.add_domain_event(
            "ShipmentPickedUp",
            {"shipment_id": str(self.id), "tracking_number": str(self.tracking_number)},
        )

    def update_tracking_status(self, new_state: ShipmentState) -> None:
        """Update tracking status."""
        old_state = self.state
        self.state = new_state

        if new_state == ShipmentState.DELIVERED:
            self.delivery_date = datetime.now()

        self.add_domain_event(
            "ShipmentStatusUpdated",
            {
                "shipment_id": str(self.id),
                "old_state": old_state.value,
                "new_state": new_state.value,
            },
        )

    def cancel(self) -> None:
        """Cancel shipment."""
        if self.state in [ShipmentState.DELIVERED, ShipmentState.RETURNED]:
            raise ValueError(f"Cannot cancel shipment in state {self.state}")
        self.state = ShipmentState.CANCELLED
        self.add_domain_event(
            "ShipmentCancelled",
            {"shipment_id": str(self.id), "shipment_number": str(self.shipment_number)},
        )


class Carrier(AggregateRoot):
    """Carrier aggregate root."""

    def __init__(
        self,
        id: UUID,
        code: str,
        name: str,
        is_active: bool = True,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        account_number: Optional[str] = None,
        tracking_url_template: Optional[str] = None,
        supports_labels: bool = False,
        supports_tracking: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize carrier."""
        super().__init__(id, created_at, updated_at)
        self.code = code
        self.name = name
        self.is_active = is_active
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.account_number = account_number
        self.tracking_url_template = tracking_url_template
        self.supports_labels = supports_labels
        self.supports_tracking = supports_tracking

    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        account_number: Optional[str] = None,
        tracking_url_template: Optional[str] = None,
        supports_labels: bool = False,
        supports_tracking: bool = False,
    ) -> "Carrier":
        """Create new carrier."""
        carrier = cls(
            id=uuid4(),
            code=code,
            name=name,
            api_endpoint=api_endpoint,
            api_key=api_key,
            account_number=account_number,
            tracking_url_template=tracking_url_template,
            supports_labels=supports_labels,
            supports_tracking=supports_tracking,
            created_at=datetime.now(),
        )
        carrier.add_domain_event(
            "CarrierCreated",
            {"carrier_id": str(carrier.id), "code": code, "name": name},
        )
        return carrier

    def get_tracking_url(self, tracking_number: str) -> Optional[str]:
        """Generate tracking URL."""
        if not self.tracking_url_template:
            return None
        return self.tracking_url_template.replace("{tracking_number}", tracking_number)


class RouteStop(Entity):
    """Route stop (owned entity)."""

    def __init__(
        self,
        id: UUID,
        shipment_id: UUID,
        delivery_address: Address,
        sequence: int,
        estimated_arrival: Optional[datetime] = None,
        actual_arrival: Optional[datetime] = None,
        completed: bool = False,
        notes: Optional[str] = None,
    ):
        """Initialize route stop."""
        super().__init__(id)
        self.shipment_id = shipment_id
        self.delivery_address = delivery_address
        self.sequence = sequence
        self.estimated_arrival = estimated_arrival
        self.actual_arrival = actual_arrival
        self.completed = completed
        self.notes = notes

    def complete(self) -> None:
        """Mark stop as completed."""
        self.completed = True
        self.actual_arrival = datetime.now()


class DeliveryRoute(AggregateRoot):
    """Delivery route aggregate root."""

    def __init__(
        self,
        id: UUID,
        route_number: RouteNumber,
        route_date: date,
        driver_id: UUID,
        vehicle_id: Optional[str] = None,
        state: RouteState = RouteState.PLANNED,
        stops: Optional[list[RouteStop]] = None,
        started_date: Optional[datetime] = None,
        completed_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize delivery route."""
        super().__init__(id, created_at, updated_at)
        self.route_number = route_number
        self.route_date = route_date
        self.driver_id = driver_id
        self.vehicle_id = vehicle_id
        self.state = state
        self.stops = stops or []
        self.started_date = started_date
        self.completed_date = completed_date
        self.notes = notes

    @classmethod
    def create(
        cls,
        route_number: RouteNumber,
        route_date: date,
        driver_id: UUID,
        vehicle_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "DeliveryRoute":
        """Create new delivery route."""
        route = cls(
            id=uuid4(),
            route_number=route_number,
            route_date=route_date,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            notes=notes,
            created_at=datetime.now(),
        )
        route.add_domain_event(
            "DeliveryRouteCreated",
            {
                "route_id": str(route.id),
                "route_number": str(route_number),
                "driver_id": str(driver_id),
            },
        )
        return route

    def add_stop(
        self,
        shipment_id: UUID,
        delivery_address: Address,
        sequence: int,
        estimated_arrival: Optional[datetime] = None,
    ) -> None:
        """Add stop to route."""
        if self.state != RouteState.PLANNED:
            raise ValueError("Can only add stops to planned routes")

        stop = RouteStop(
            id=uuid4(),
            shipment_id=shipment_id,
            delivery_address=delivery_address,
            sequence=sequence,
            estimated_arrival=estimated_arrival,
        )
        self.stops.append(stop)

    def start(self) -> None:
        """Start route."""
        if self.state != RouteState.PLANNED:
            raise ValueError(f"Cannot start route in state {self.state}")
        self.state = RouteState.IN_PROGRESS
        self.started_date = datetime.now()
        self.add_domain_event(
            "DeliveryRouteStarted",
            {"route_id": str(self.id), "route_number": str(self.route_number)},
        )

    def complete_stop(self, stop_id: UUID) -> None:
        """Complete a stop."""
        stop = next((s for s in self.stops if s.id == stop_id), None)
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")
        stop.complete()
        self.add_domain_event(
            "RouteStopCompleted",
            {"route_id": str(self.id), "stop_id": str(stop_id)},
        )

    def complete(self) -> None:
        """Complete route."""
        if self.state != RouteState.IN_PROGRESS:
            raise ValueError(f"Cannot complete route in state {self.state}")
        if not all(stop.completed for stop in self.stops):
            raise ValueError("Cannot complete route with incomplete stops")

        self.state = RouteState.COMPLETED
        self.completed_date = datetime.now()
        self.add_domain_event(
            "DeliveryRouteCompleted",
            {"route_id": str(self.id), "route_number": str(self.route_number)},
        )


class RMALine(Entity):
    """RMA line (owned entity)."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        reason: str,
        condition: Optional[str] = None,
    ):
        """Initialize RMA line."""
        super().__init__(id)
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.quantity = quantity
        self.reason = reason
        self.condition = condition


class ReturnAuthorization(AggregateRoot):
    """Return authorization (RMA) aggregate root."""

    def __init__(
        self,
        id: UUID,
        rma_number: RMANumber,
        original_shipment_id: UUID,
        customer_id: UUID,
        state: RMAState = RMAState.REQUESTED,
        action: Optional[RMAAction] = None,
        lines: Optional[list[RMALine]] = None,
        return_address: Optional[Address] = None,
        return_tracking_number: Optional[TrackingNumber] = None,
        requested_date: Optional[datetime] = None,
        approved_date: Optional[datetime] = None,
        received_date: Optional[datetime] = None,
        processed_date: Optional[datetime] = None,
        refund_amount: Optional[Money] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize RMA."""
        super().__init__(id, created_at, updated_at)
        self.rma_number = rma_number
        self.original_shipment_id = original_shipment_id
        self.customer_id = customer_id
        self.state = state
        self.action = action
        self.lines = lines or []
        self.return_address = return_address
        self.return_tracking_number = return_tracking_number
        self.requested_date = requested_date or datetime.now()
        self.approved_date = approved_date
        self.received_date = received_date
        self.processed_date = processed_date
        self.refund_amount = refund_amount
        self.notes = notes

    @classmethod
    def create(
        cls,
        rma_number: RMANumber,
        original_shipment_id: UUID,
        customer_id: UUID,
        action: RMAAction,
        notes: Optional[str] = None,
    ) -> "ReturnAuthorization":
        """Create new RMA."""
        rma = cls(
            id=uuid4(),
            rma_number=rma_number,
            original_shipment_id=original_shipment_id,
            customer_id=customer_id,
            action=action,
            notes=notes,
            created_at=datetime.now(),
        )
        rma.add_domain_event(
            "RMACreated",
            {
                "rma_id": str(rma.id),
                "rma_number": str(rma_number),
                "customer_id": str(customer_id),
            },
        )
        return rma

    def add_line(
        self,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        reason: str,
        condition: Optional[str] = None,
    ) -> None:
        """Add RMA line."""
        if self.state != RMAState.REQUESTED:
            raise ValueError("Can only add lines to requested RMA")

        line = RMALine(
            id=uuid4(),
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            reason=reason,
            condition=condition,
        )
        self.lines.append(line)

    def approve(self, return_address: Address) -> None:
        """Approve RMA."""
        if self.state != RMAState.REQUESTED:
            raise ValueError(f"Cannot approve RMA in state {self.state}")
        self.state = RMAState.APPROVED
        self.approved_date = datetime.now()
        self.return_address = return_address
        self.add_domain_event(
            "RMAApproved",
            {"rma_id": str(self.id), "rma_number": str(self.rma_number)},
        )

    def reject(self, reason: str) -> None:
        """Reject RMA."""
        if self.state != RMAState.REQUESTED:
            raise ValueError(f"Cannot reject RMA in state {self.state}")
        self.state = RMAState.REJECTED
        self.notes = f"{self.notes or ''}\nRejection reason: {reason}"
        self.add_domain_event(
            "RMARejected",
            {"rma_id": str(self.id), "rma_number": str(self.rma_number)},
        )

    def mark_shipped(self, tracking_number: TrackingNumber) -> None:
        """Mark RMA as shipped by customer."""
        if self.state != RMAState.APPROVED:
            raise ValueError("Can only mark approved RMA as shipped")
        self.state = RMAState.SHIPPED
        self.return_tracking_number = tracking_number
        self.add_domain_event(
            "RMAShipped",
            {
                "rma_id": str(self.id),
                "rma_number": str(self.rma_number),
                "tracking_number": str(tracking_number),
            },
        )

    def receive(self) -> None:
        """Receive returned items."""
        if self.state != RMAState.SHIPPED:
            raise ValueError("Can only receive shipped RMA")
        self.state = RMAState.RECEIVED
        self.received_date = datetime.now()
        self.add_domain_event(
            "RMAReceived",
            {"rma_id": str(self.id), "rma_number": str(self.rma_number)},
        )

    def process(self, refund_amount: Optional[Money] = None) -> None:
        """Process RMA (refund/exchange)."""
        if self.state != RMAState.RECEIVED:
            raise ValueError("Can only process received RMA")
        self.state = RMAState.PROCESSED
        self.processed_date = datetime.now()
        if refund_amount:
            self.refund_amount = refund_amount
        self.add_domain_event(
            "RMAProcessed",
            {
                "rma_id": str(self.id),
                "rma_number": str(self.rma_number),
                "action": self.action.value if self.action else None,
            },
        )
