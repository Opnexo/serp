"""Domain entities for inventory."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from serp_core.domain import AggregateRoot, Entity

from serp_inventory.domain.value_objects import (
    AdjustmentNumber,
    AdjustmentReason,
    AdjustmentState,
    CostingMethod,
    LocationCode,
    LocationType,
    LocationUsage,
    LotSerialNumber,
    MovementNumber,
    ReorderRoute,
    StockMoveState,
    StockMoveType,
    StockQuantity,
)


class Warehouse(AggregateRoot):
    """Warehouse aggregate root."""

    def __init__(
        self,
        id: UUID,
        code: str,
        name: str,
        is_active: bool = True,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize warehouse."""
        super().__init__(id, created_at, updated_at)
        self.code = code
        self.name = name
        self.is_active = is_active
        self.address = address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country
        self.phone = phone
        self.email = email

    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> "Warehouse":
        """Create new warehouse."""
        warehouse = cls(
            id=uuid4(),
            code=code,
            name=name,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            phone=phone,
            email=email,
            created_at=datetime.now(),
        )
        warehouse.add_domain_event(
            "WarehouseCreated",
            {
                "warehouse_id": str(warehouse.id),
                "code": code,
                "name": name,
            },
        )
        return warehouse

    def activate(self) -> None:
        """Activate warehouse."""
        if self.is_active:
            raise ValueError("Warehouse already active")
        self.is_active = True
        self.add_domain_event("WarehouseActivated", {"warehouse_id": str(self.id)})

    def deactivate(self) -> None:
        """Deactivate warehouse."""
        if not self.is_active:
            raise ValueError("Warehouse already inactive")
        self.is_active = False
        self.add_domain_event("WarehouseDeactivated", {"warehouse_id": str(self.id)})


class StockLocation(AggregateRoot):
    """Stock location aggregate root."""

    def __init__(
        self,
        id: UUID,
        location_code: LocationCode,
        name: str,
        location_type: LocationType,
        usage: LocationUsage,
        warehouse_id: Optional[UUID] = None,
        parent_location_id: Optional[UUID] = None,
        is_active: bool = True,
        allow_negative_stock: bool = False,
        capacity: Optional[Decimal] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize stock location."""
        super().__init__(id, created_at, updated_at)
        self.location_code = location_code
        self.name = name
        self.location_type = location_type
        self.usage = usage
        self.warehouse_id = warehouse_id
        self.parent_location_id = parent_location_id
        self.is_active = is_active
        self.allow_negative_stock = allow_negative_stock
        self.capacity = capacity
        self.notes = notes

    @classmethod
    def create(
        cls,
        location_code: LocationCode,
        name: str,
        location_type: LocationType,
        usage: LocationUsage,
        warehouse_id: Optional[UUID] = None,
        parent_location_id: Optional[UUID] = None,
        allow_negative_stock: bool = False,
        capacity: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> "StockLocation":
        """Create new stock location."""
        location = cls(
            id=uuid4(),
            location_code=location_code,
            name=name,
            location_type=location_type,
            usage=usage,
            warehouse_id=warehouse_id,
            parent_location_id=parent_location_id,
            allow_negative_stock=allow_negative_stock,
            capacity=capacity,
            notes=notes,
            created_at=datetime.now(),
        )
        location.add_domain_event(
            "StockLocationCreated",
            {
                "location_id": str(location.id),
                "location_code": str(location_code),
                "name": name,
                "location_type": location_type.value,
            },
        )
        return location


class StockQuant(AggregateRoot):
    """Stock quantity aggregate - represents stock at a specific location."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        location_id: UUID,
        quantity: StockQuantity,
        lot_serial_id: Optional[UUID] = None,
        costing_method: CostingMethod = CostingMethod.FIFO,
        unit_cost: Optional[Decimal] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize stock quant."""
        super().__init__(id, created_at, updated_at)
        self.product_id = product_id
        self.location_id = location_id
        self.quantity = quantity
        self.lot_serial_id = lot_serial_id
        self.costing_method = costing_method
        self.unit_cost = unit_cost

    @classmethod
    def create(
        cls,
        product_id: UUID,
        location_id: UUID,
        initial_quantity: Decimal = Decimal("0"),
        lot_serial_id: Optional[UUID] = None,
        costing_method: CostingMethod = CostingMethod.FIFO,
        unit_cost: Optional[Decimal] = None,
    ) -> "StockQuant":
        """Create new stock quant."""
        quant = cls(
            id=uuid4(),
            product_id=product_id,
            location_id=location_id,
            quantity=StockQuantity(on_hand=initial_quantity),
            lot_serial_id=lot_serial_id,
            costing_method=costing_method,
            unit_cost=unit_cost,
            created_at=datetime.now(),
        )
        if initial_quantity > 0:
            quant.add_domain_event(
                "StockQuantAdded",
                {
                    "quant_id": str(quant.id),
                    "product_id": str(product_id),
                    "location_id": str(location_id),
                    "quantity": str(initial_quantity),
                },
            )
        return quant

    def add_quantity(self, quantity: Decimal) -> None:
        """Add to on_hand quantity."""
        self.quantity = self.quantity.add(quantity)
        self.add_domain_event(
            "StockQuantityAdded",
            {
                "quant_id": str(self.id),
                "product_id": str(self.product_id),
                "location_id": str(self.location_id),
                "quantity": str(quantity),
                "new_on_hand": str(self.quantity.on_hand),
            },
        )

    def remove_quantity(self, quantity: Decimal) -> None:
        """Remove from on_hand quantity."""
        self.quantity = self.quantity.remove(quantity)
        self.add_domain_event(
            "StockQuantityRemoved",
            {
                "quant_id": str(self.id),
                "product_id": str(self.product_id),
                "location_id": str(self.location_id),
                "quantity": str(quantity),
                "new_on_hand": str(self.quantity.on_hand),
            },
        )

    def reserve_quantity(self, quantity: Decimal) -> None:
        """Reserve quantity."""
        self.quantity = self.quantity.reserve(quantity)
        self.add_domain_event(
            "StockQuantityReserved",
            {
                "quant_id": str(self.id),
                "product_id": str(self.product_id),
                "location_id": str(self.location_id),
                "quantity": str(quantity),
                "new_reserved": str(self.quantity.reserved),
            },
        )

    def unreserve_quantity(self, quantity: Decimal) -> None:
        """Unreserve quantity."""
        self.quantity = self.quantity.unreserve(quantity)
        self.add_domain_event(
            "StockQuantityUnreserved",
            {
                "quant_id": str(self.id),
                "product_id": str(self.product_id),
                "location_id": str(self.location_id),
                "quantity": str(quantity),
                "new_reserved": str(self.quantity.reserved),
            },
        )

    def fulfill_reservation(self, quantity: Decimal) -> None:
        """Fulfill reservation by removing from both on_hand and reserved."""
        self.quantity = self.quantity.fulfill_reservation(quantity)
        self.add_domain_event(
            "StockReservationFulfilled",
            {
                "quant_id": str(self.id),
                "product_id": str(self.product_id),
                "location_id": str(self.location_id),
                "quantity": str(quantity),
                "new_on_hand": str(self.quantity.on_hand),
                "new_reserved": str(self.quantity.reserved),
            },
        )


class StockMove(AggregateRoot):
    """Stock movement aggregate root."""

    def __init__(
        self,
        id: UUID,
        movement_number: MovementNumber,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        uom_id: str,
        source_location_id: UUID,
        dest_location_id: UUID,
        move_type: StockMoveType,
        state: StockMoveState = StockMoveState.DRAFT,
        lot_serial_id: Optional[UUID] = None,
        reference: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
        scheduled_date: Optional[datetime] = None,
        executed_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize stock move."""
        super().__init__(id, created_at, updated_at)
        self.movement_number = movement_number
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.quantity = quantity
        self.uom_id = uom_id
        self.source_location_id = source_location_id
        self.dest_location_id = dest_location_id
        self.move_type = move_type
        self.state = state
        self.lot_serial_id = lot_serial_id
        self.reference = reference
        self.reference_type = reference_type
        self.reference_id = reference_id
        self.scheduled_date = scheduled_date
        self.executed_date = executed_date
        self.notes = notes
        self.created_by = created_by

    @classmethod
    def create(
        cls,
        movement_number: MovementNumber,
        product_id: UUID,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        uom_id: str,
        source_location_id: UUID,
        dest_location_id: UUID,
        move_type: StockMoveType,
        lot_serial_id: Optional[UUID] = None,
        reference: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
        scheduled_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> "StockMove":
        """Create new stock move."""
        move = cls(
            id=uuid4(),
            movement_number=movement_number,
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            uom_id=uom_id,
            source_location_id=source_location_id,
            dest_location_id=dest_location_id,
            move_type=move_type,
            lot_serial_id=lot_serial_id,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            scheduled_date=scheduled_date,
            notes=notes,
            created_by=created_by,
            created_at=datetime.now(),
        )
        move.add_domain_event(
            "StockMoveCreated",
            {
                "move_id": str(move.id),
                "movement_number": str(movement_number),
                "product_id": str(product_id),
                "quantity": str(quantity),
                "move_type": move_type.value,
            },
        )
        return move

    def confirm(self) -> None:
        """Confirm stock move (reserves stock)."""
        if self.state != StockMoveState.DRAFT:
            raise ValueError(f"Cannot confirm move in state {self.state}")
        self.state = StockMoveState.CONFIRMED
        self.add_domain_event(
            "StockMoveConfirmed",
            {
                "move_id": str(self.id),
                "movement_number": str(self.movement_number),
            },
        )

    def execute(self) -> None:
        """Execute stock move (actually moves the stock)."""
        if self.state != StockMoveState.CONFIRMED:
            raise ValueError(f"Cannot execute move in state {self.state}")
        self.state = StockMoveState.DONE
        self.executed_date = datetime.now()
        self.add_domain_event(
            "StockMoveExecuted",
            {
                "move_id": str(self.id),
                "movement_number": str(self.movement_number),
                "product_id": str(self.product_id),
                "quantity": str(self.quantity),
                "source_location_id": str(self.source_location_id),
                "dest_location_id": str(self.dest_location_id),
            },
        )

    def cancel(self) -> None:
        """Cancel stock move."""
        if self.state == StockMoveState.DONE:
            raise ValueError("Cannot cancel completed move")
        if self.state == StockMoveState.CANCELLED:
            raise ValueError("Move already cancelled")
        self.state = StockMoveState.CANCELLED
        self.add_domain_event(
            "StockMoveCancelled",
            {
                "move_id": str(self.id),
                "movement_number": str(self.movement_number),
            },
        )


class AdjustmentLine(Entity):
    """Inventory adjustment line (owned entity)."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        product_code: str,
        product_name: str,
        location_id: UUID,
        theoretical_quantity: Decimal,
        counted_quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ):
        """Initialize adjustment line."""
        super().__init__(id)
        self.product_id = product_id
        self.product_code = product_code
        self.product_name = product_name
        self.location_id = location_id
        self.theoretical_quantity = theoretical_quantity
        self.counted_quantity = counted_quantity
        self.lot_serial_id = lot_serial_id

    @property
    def difference(self) -> Decimal:
        """Calculate quantity difference."""
        return self.counted_quantity - self.theoretical_quantity


class InventoryAdjustment(AggregateRoot):
    """Inventory adjustment aggregate root."""

    def __init__(
        self,
        id: UUID,
        adjustment_number: AdjustmentNumber,
        reason: AdjustmentReason,
        state: AdjustmentState = AdjustmentState.DRAFT,
        lines: Optional[list[AdjustmentLine]] = None,
        notes: Optional[str] = None,
        adjustment_date: Optional[datetime] = None,
        confirmed_date: Optional[datetime] = None,
        created_by: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize inventory adjustment."""
        super().__init__(id, created_at, updated_at)
        self.adjustment_number = adjustment_number
        self.reason = reason
        self.state = state
        self.lines = lines or []
        self.notes = notes
        self.adjustment_date = adjustment_date or datetime.now()
        self.confirmed_date = confirmed_date
        self.created_by = created_by

    @classmethod
    def create(
        cls,
        adjustment_number: AdjustmentNumber,
        reason: AdjustmentReason,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> "InventoryAdjustment":
        """Create new inventory adjustment."""
        adjustment = cls(
            id=uuid4(),
            adjustment_number=adjustment_number,
            reason=reason,
            notes=notes,
            created_by=created_by,
            created_at=datetime.now(),
        )
        adjustment.add_domain_event(
            "InventoryAdjustmentCreated",
            {
                "adjustment_id": str(adjustment.id),
                "adjustment_number": str(adjustment_number),
                "reason": reason.value,
            },
        )
        return adjustment

    def add_line(
        self,
        product_id: UUID,
        product_code: str,
        product_name: str,
        location_id: UUID,
        theoretical_quantity: Decimal,
        counted_quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ) -> None:
        """Add adjustment line."""
        if self.state != AdjustmentState.DRAFT:
            raise ValueError("Cannot add lines to non-draft adjustment")

        line = AdjustmentLine(
            id=uuid4(),
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            location_id=location_id,
            theoretical_quantity=theoretical_quantity,
            counted_quantity=counted_quantity,
            lot_serial_id=lot_serial_id,
        )
        self.lines.append(line)

    def confirm(self) -> None:
        """Confirm adjustment (applies changes to stock)."""
        if self.state != AdjustmentState.DRAFT:
            raise ValueError(f"Cannot confirm adjustment in state {self.state}")
        if not self.lines:
            raise ValueError("Cannot confirm adjustment without lines")

        self.state = AdjustmentState.CONFIRMED
        self.confirmed_date = datetime.now()
        self.add_domain_event(
            "InventoryAdjustmentConfirmed",
            {
                "adjustment_id": str(self.id),
                "adjustment_number": str(self.adjustment_number),
                "line_count": len(self.lines),
            },
        )

    def cancel(self) -> None:
        """Cancel adjustment."""
        if self.state == AdjustmentState.CONFIRMED:
            raise ValueError("Cannot cancel confirmed adjustment")
        if self.state == AdjustmentState.CANCELLED:
            raise ValueError("Adjustment already cancelled")

        self.state = AdjustmentState.CANCELLED
        self.add_domain_event(
            "InventoryAdjustmentCancelled",
            {
                "adjustment_id": str(self.id),
                "adjustment_number": str(self.adjustment_number),
            },
        )


class ReorderingRule(AggregateRoot):
    """Reordering rule aggregate root."""

    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        location_id: UUID,
        min_quantity: Decimal,
        max_quantity: Decimal,
        quantity_to_order: Decimal,
        route: ReorderRoute,
        lead_time_days: int = 0,
        is_active: bool = True,
        supplier_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize reordering rule."""
        super().__init__(id, created_at, updated_at)
        self.product_id = product_id
        self.location_id = location_id
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.quantity_to_order = quantity_to_order
        self.route = route
        self.lead_time_days = lead_time_days
        self.is_active = is_active
        self.supplier_id = supplier_id

    @classmethod
    def create(
        cls,
        product_id: UUID,
        location_id: UUID,
        min_quantity: Decimal,
        max_quantity: Decimal,
        quantity_to_order: Decimal,
        route: ReorderRoute,
        lead_time_days: int = 0,
        supplier_id: Optional[UUID] = None,
    ) -> "ReorderingRule":
        """Create new reordering rule."""
        if min_quantity >= max_quantity:
            raise ValueError("Min quantity must be less than max quantity")
        if quantity_to_order <= 0:
            raise ValueError("Quantity to order must be positive")

        rule = cls(
            id=uuid4(),
            product_id=product_id,
            location_id=location_id,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            quantity_to_order=quantity_to_order,
            route=route,
            lead_time_days=lead_time_days,
            supplier_id=supplier_id,
            created_at=datetime.now(),
        )
        rule.add_domain_event(
            "ReorderingRuleCreated",
            {
                "rule_id": str(rule.id),
                "product_id": str(product_id),
                "location_id": str(location_id),
                "min_quantity": str(min_quantity),
            },
        )
        return rule

    def should_reorder(self, available_quantity: Decimal) -> bool:
        """Check if reordering is needed."""
        return self.is_active and available_quantity <= self.min_quantity


class LotSerial(AggregateRoot):
    """Lot/Serial number aggregate root."""

    def __init__(
        self,
        id: UUID,
        lot_serial_number: LotSerialNumber,
        product_id: UUID,
        is_serial: bool = False,
        expiration_date: Optional[date] = None,
        manufacture_date: Optional[date] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize lot/serial."""
        super().__init__(id, created_at, updated_at)
        self.lot_serial_number = lot_serial_number
        self.product_id = product_id
        self.is_serial = is_serial
        self.expiration_date = expiration_date
        self.manufacture_date = manufacture_date
        self.notes = notes

    @classmethod
    def create(
        cls,
        lot_serial_number: LotSerialNumber,
        product_id: UUID,
        is_serial: bool = False,
        expiration_date: Optional[date] = None,
        manufacture_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> "LotSerial":
        """Create new lot/serial."""
        lot = cls(
            id=uuid4(),
            lot_serial_number=lot_serial_number,
            product_id=product_id,
            is_serial=is_serial,
            expiration_date=expiration_date,
            manufacture_date=manufacture_date,
            notes=notes,
            created_at=datetime.now(),
        )
        lot.add_domain_event(
            "LotSerialCreated",
            {
                "lot_id": str(lot.id),
                "lot_serial_number": str(lot_serial_number),
                "product_id": str(product_id),
                "is_serial": is_serial,
            },
        )
        return lot

    def is_expired(self, check_date: Optional[date] = None) -> bool:
        """Check if lot is expired."""
        if not self.expiration_date:
            return False
        check = check_date or date.today()
        return check > self.expiration_date
