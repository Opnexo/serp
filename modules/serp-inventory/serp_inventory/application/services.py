"""Application services for inventory."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from serp_core.domain import IEventPublisher

from serp_inventory.application.dto import (
    AdjustmentLineResponseDTO,
    InventoryAdjustmentCreateDTO,
    InventoryAdjustmentDTO,
    LotSerialCreateDTO,
    LotSerialDTO,
    LotTraceDTO,
    ReorderingRuleCreateDTO,
    ReorderingRuleDTO,
    ReorderingRuleUpdateDTO,
    ReorderSuggestionDTO,
    StockAvailabilityDTO,
    StockLevelDTO,
    StockLocationCreateDTO,
    StockLocationDTO,
    StockLocationUpdateDTO,
    StockMoveCreateDTO,
    StockMoveDTO,
    WarehouseCreateDTO,
    WarehouseDTO,
    WarehouseUpdateDTO,
)
from serp_inventory.config import InventorySettings
from serp_inventory.domain import (
    AdjustmentNumber,
    AdjustmentReason,
    IInventoryAdjustmentRepository,
    ILotSerialRepository,
    InventoryAdjustment,
    IReorderingRuleRepository,
    IStockLocationRepository,
    IStockMoveRepository,
    IStockQuantRepository,
    IWarehouseRepository,
    LocationCode,
    LocationType,
    LocationUsage,
    LotSerial,
    LotSerialNumber,
    MovementNumber,
    ReorderingRule,
    ReorderRoute,
    StockLocation,
    StockMove,
    StockMoveState,
    StockMoveType,
    StockQuant,
    Warehouse,
)


class WarehouseService:
    """Service for warehouse management."""

    def __init__(
        self,
        warehouse_repo: IWarehouseRepository,
        event_publisher: IEventPublisher,
    ):
        """Initialize service."""
        self.warehouse_repo = warehouse_repo
        self.event_publisher = event_publisher

    def create_warehouse(self, dto: WarehouseCreateDTO) -> WarehouseDTO:
        """Create a new warehouse."""
        # Check if code already exists
        existing = self.warehouse_repo.get_by_code(dto.code)
        if existing:
            raise ValueError(f"Warehouse with code {dto.code} already exists")

        warehouse = Warehouse.create(
            code=dto.code,
            name=dto.name,
            address=dto.address,
            city=dto.city,
            state=dto.state,
            postal_code=dto.postal_code,
            country=dto.country,
            phone=dto.phone,
            email=dto.email,
        )

        self.warehouse_repo.add(warehouse)
        self.event_publisher.publish_all(warehouse.domain_events)
        warehouse.clear_domain_events()

        return self._map_warehouse_to_dto(warehouse)

    def get_warehouse(self, warehouse_id: UUID) -> WarehouseDTO:
        """Get warehouse by ID."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")
        return self._map_warehouse_to_dto(warehouse)

    def update_warehouse(
        self, warehouse_id: UUID, dto: WarehouseUpdateDTO
    ) -> WarehouseDTO:
        """Update warehouse."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        if dto.name is not None:
            warehouse.name = dto.name
        if dto.address is not None:
            warehouse.address = dto.address
        if dto.city is not None:
            warehouse.city = dto.city
        if dto.state is not None:
            warehouse.state = dto.state
        if dto.postal_code is not None:
            warehouse.postal_code = dto.postal_code
        if dto.country is not None:
            warehouse.country = dto.country
        if dto.phone is not None:
            warehouse.phone = dto.phone
        if dto.email is not None:
            warehouse.email = dto.email

        warehouse.updated_at = datetime.now()
        self.warehouse_repo.update(warehouse)
        return self._map_warehouse_to_dto(warehouse)

    def activate_warehouse(self, warehouse_id: UUID) -> WarehouseDTO:
        """Activate warehouse."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        warehouse.activate()
        self.warehouse_repo.update(warehouse)
        self.event_publisher.publish_all(warehouse.domain_events)
        warehouse.clear_domain_events()

        return self._map_warehouse_to_dto(warehouse)

    def deactivate_warehouse(self, warehouse_id: UUID) -> WarehouseDTO:
        """Deactivate warehouse."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        warehouse.deactivate()
        self.warehouse_repo.update(warehouse)
        self.event_publisher.publish_all(warehouse.domain_events)
        warehouse.clear_domain_events()

        return self._map_warehouse_to_dto(warehouse)

    def list_warehouses(self, active_only: bool = False) -> list[WarehouseDTO]:
        """List all warehouses."""
        warehouses = self.warehouse_repo.list_all(active_only=active_only)
        return [self._map_warehouse_to_dto(w) for w in warehouses]

    def _map_warehouse_to_dto(self, warehouse: Warehouse) -> WarehouseDTO:
        """Map warehouse entity to DTO."""
        return WarehouseDTO(
            id=warehouse.id,
            code=warehouse.code,
            name=warehouse.name,
            is_active=warehouse.is_active,
            address=warehouse.address,
            city=warehouse.city,
            state=warehouse.state,
            postal_code=warehouse.postal_code,
            country=warehouse.country,
            phone=warehouse.phone,
            email=warehouse.email,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )


class StockLocationService:
    """Service for stock location management."""

    def __init__(
        self,
        location_repo: IStockLocationRepository,
        warehouse_repo: IWarehouseRepository,
        event_publisher: IEventPublisher,
    ):
        """Initialize service."""
        self.location_repo = location_repo
        self.warehouse_repo = warehouse_repo
        self.event_publisher = event_publisher

    def create_location(self, dto: StockLocationCreateDTO) -> StockLocationDTO:
        """Create a new stock location."""
        # Validate location code
        location_code = LocationCode(value=dto.location_code)
        existing = self.location_repo.get_by_code(location_code)
        if existing:
            raise ValueError(f"Location with code {dto.location_code} already exists")

        # Validate warehouse exists
        if dto.warehouse_id:
            warehouse = self.warehouse_repo.get(dto.warehouse_id)
            if not warehouse:
                raise ValueError(f"Warehouse {dto.warehouse_id} not found")

        # Validate parent location exists
        if dto.parent_location_id:
            parent = self.location_repo.get(dto.parent_location_id)
            if not parent:
                raise ValueError(f"Parent location {dto.parent_location_id} not found")

        location = StockLocation.create(
            location_code=location_code,
            name=dto.name,
            location_type=LocationType(dto.location_type),
            usage=LocationUsage(dto.usage),
            warehouse_id=dto.warehouse_id,
            parent_location_id=dto.parent_location_id,
            allow_negative_stock=dto.allow_negative_stock,
            capacity=dto.capacity,
            notes=dto.notes,
        )

        self.location_repo.add(location)
        self.event_publisher.publish_all(location.domain_events)
        location.clear_domain_events()

        return self._map_location_to_dto(location)

    def get_location(self, location_id: UUID) -> StockLocationDTO:
        """Get location by ID."""
        location = self.location_repo.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not found")
        return self._map_location_to_dto(location)

    def update_location(
        self, location_id: UUID, dto: StockLocationUpdateDTO
    ) -> StockLocationDTO:
        """Update location."""
        location = self.location_repo.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not found")

        if dto.name is not None:
            location.name = dto.name
        if dto.allow_negative_stock is not None:
            location.allow_negative_stock = dto.allow_negative_stock
        if dto.capacity is not None:
            location.capacity = dto.capacity
        if dto.notes is not None:
            location.notes = dto.notes

        location.updated_at = datetime.now()
        self.location_repo.update(location)
        return self._map_location_to_dto(location)

    def list_by_warehouse(
        self, warehouse_id: UUID, active_only: bool = False
    ) -> list[StockLocationDTO]:
        """List locations in a warehouse."""
        locations = self.location_repo.list_by_warehouse(
            warehouse_id, active_only=active_only
        )
        return [self._map_location_to_dto(loc) for loc in locations]

    def list_children(self, parent_id: UUID) -> list[StockLocationDTO]:
        """List child locations."""
        locations = self.location_repo.list_children(parent_id)
        return [self._map_location_to_dto(loc) for loc in locations]

    def _map_location_to_dto(self, location: StockLocation) -> StockLocationDTO:
        """Map location entity to DTO."""
        return StockLocationDTO(
            id=location.id,
            location_code=str(location.location_code),
            name=location.name,
            location_type=location.location_type.value,
            usage=location.usage.value,
            warehouse_id=location.warehouse_id,
            parent_location_id=location.parent_location_id,
            is_active=location.is_active,
            allow_negative_stock=location.allow_negative_stock,
            capacity=location.capacity,
            notes=location.notes,
            created_at=location.created_at,
            updated_at=location.updated_at,
        )


class StockService:
    """Service for stock quantity management."""

    def __init__(
        self,
        quant_repo: IStockQuantRepository,
        location_repo: IStockLocationRepository,
        event_publisher: IEventPublisher,
    ):
        """Initialize service."""
        self.quant_repo = quant_repo
        self.location_repo = location_repo
        self.event_publisher = event_publisher

    def get_stock_level(
        self,
        product_id: UUID,
        product_code: str,
        product_name: str,
        location_id: UUID,
        location_code: str,
        lot_serial_id: Optional[UUID] = None,
    ) -> StockLevelDTO:
        """Get stock level for product at location."""
        quant = self.quant_repo.get_by_product_location(
            product_id, location_id, lot_serial_id
        )

        if not quant:
            return StockLevelDTO(
                product_id=product_id,
                product_code=product_code,
                product_name=product_name,
                location_id=location_id,
                location_code=location_code,
                on_hand=Decimal("0"),
                reserved=Decimal("0"),
                available=Decimal("0"),
                lot_serial_id=lot_serial_id,
            )

        return StockLevelDTO(
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            location_id=location_id,
            location_code=location_code,
            on_hand=quant.quantity.on_hand,
            reserved=quant.quantity.reserved,
            available=quant.quantity.available,
            lot_serial_id=lot_serial_id,
            unit_cost=quant.unit_cost,
        )

    def get_product_availability(
        self, product_id: UUID, product_code: str, product_name: str
    ) -> StockAvailabilityDTO:
        """Get total availability for a product across all locations."""
        quants = self.quant_repo.list_by_product(product_id)

        total_on_hand = Decimal("0")
        total_reserved = Decimal("0")
        total_available = Decimal("0")
        by_location = []

        for quant in quants:
            location = self.location_repo.get(quant.location_id)
            if not location:
                continue

            total_on_hand += quant.quantity.on_hand
            total_reserved += quant.quantity.reserved
            total_available += quant.quantity.available

            by_location.append(
                StockLevelDTO(
                    product_id=product_id,
                    product_code=product_code,
                    product_name=product_name,
                    location_id=quant.location_id,
                    location_code=str(location.location_code),
                    on_hand=quant.quantity.on_hand,
                    reserved=quant.quantity.reserved,
                    available=quant.quantity.available,
                    lot_serial_id=quant.lot_serial_id,
                    unit_cost=quant.unit_cost,
                )
            )

        return StockAvailabilityDTO(
            product_id=product_id,
            total_on_hand=total_on_hand,
            total_reserved=total_reserved,
            total_available=total_available,
            by_location=by_location,
        )

    def reserve_stock(
        self,
        product_id: UUID,
        location_id: UUID,
        quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ) -> None:
        """Reserve stock quantity."""
        quant = self.quant_repo.get_by_product_location(
            product_id, location_id, lot_serial_id
        )

        if not quant:
            raise ValueError(
                f"No stock found for product {product_id} at location {location_id}"
            )

        quant.reserve_quantity(quantity)
        self.quant_repo.update(quant)
        self.event_publisher.publish_all(quant.domain_events)
        quant.clear_domain_events()

    def unreserve_stock(
        self,
        product_id: UUID,
        location_id: UUID,
        quantity: Decimal,
        lot_serial_id: Optional[UUID] = None,
    ) -> None:
        """Unreserve stock quantity."""
        quant = self.quant_repo.get_by_product_location(
            product_id, location_id, lot_serial_id
        )

        if not quant:
            raise ValueError(
                f"No stock found for product {product_id} at location {location_id}"
            )

        quant.unreserve_quantity(quantity)
        self.quant_repo.update(quant)
        self.event_publisher.publish_all(quant.domain_events)
        quant.clear_domain_events()

    def _get_or_create_quant(
        self,
        product_id: UUID,
        location_id: UUID,
        lot_serial_id: Optional[UUID] = None,
    ) -> StockQuant:
        """Get existing quant or create new one."""
        quant = self.quant_repo.get_by_product_location(
            product_id, location_id, lot_serial_id
        )

        if not quant:
            quant = StockQuant.create(
                product_id=product_id,
                location_id=location_id,
                lot_serial_id=lot_serial_id,
            )
            self.quant_repo.add(quant)
            self.event_publisher.publish_all(quant.domain_events)
            quant.clear_domain_events()

        return quant


class MovementService:
    """Service for stock movement management."""

    def __init__(
        self,
        move_repo: IStockMoveRepository,
        quant_repo: IStockQuantRepository,
        location_repo: IStockLocationRepository,
        event_publisher: IEventPublisher,
        settings: InventorySettings,
    ):
        """Initialize service."""
        self.move_repo = move_repo
        self.quant_repo = quant_repo
        self.location_repo = location_repo
        self.event_publisher = event_publisher
        self.settings = settings
        self._counter = 1

    def create_movement(self, dto: StockMoveCreateDTO) -> StockMoveDTO:
        """Create a new stock movement."""
        # Validate locations exist
        source_loc = self.location_repo.get(dto.source_location_id)
        if not source_loc:
            raise ValueError(f"Source location {dto.source_location_id} not found")

        dest_loc = self.location_repo.get(dto.dest_location_id)
        if not dest_loc:
            raise ValueError(f"Destination location {dto.dest_location_id} not found")

        # Generate movement number
        movement_number = self._generate_movement_number()

        move = StockMove.create(
            movement_number=movement_number,
            product_id=dto.product_id,
            product_code=dto.product_code,
            product_name=dto.product_name,
            quantity=dto.quantity,
            uom_id=dto.uom_id,
            source_location_id=dto.source_location_id,
            dest_location_id=dto.dest_location_id,
            move_type=StockMoveType(dto.move_type),
            lot_serial_id=dto.lot_serial_id,
            reference=dto.reference,
            reference_type=dto.reference_type,
            reference_id=dto.reference_id,
            scheduled_date=dto.scheduled_date,
            notes=dto.notes,
        )

        self.move_repo.add(move)
        self.event_publisher.publish_all(move.domain_events)
        move.clear_domain_events()

        return self._map_move_to_dto(move)

    def confirm_movement(self, move_id: UUID) -> StockMoveDTO:
        """Confirm movement (reserves stock)."""
        move = self.move_repo.get(move_id)
        if not move:
            raise ValueError(f"Movement {move_id} not found")

        # Check if source has available stock
        source_quant = self.quant_repo.get_by_product_location(
            move.product_id, move.source_location_id, move.lot_serial_id
        )

        if not source_quant or source_quant.quantity.available < move.quantity:
            available = (
                source_quant.quantity.available if source_quant else Decimal("0")
            )
            raise ValueError(
                f"Insufficient stock. Need {move.quantity}, have {available} available"
            )

        # Reserve stock at source
        source_quant.reserve_quantity(move.quantity)
        self.quant_repo.update(source_quant)

        # Confirm move
        move.confirm()
        self.move_repo.update(move)

        # Publish events
        self.event_publisher.publish_all(source_quant.domain_events)
        source_quant.clear_domain_events()
        self.event_publisher.publish_all(move.domain_events)
        move.clear_domain_events()

        return self._map_move_to_dto(move)

    def execute_movement(self, move_id: UUID) -> StockMoveDTO:
        """Execute movement (actually moves the stock)."""
        move = self.move_repo.get(move_id)
        if not move:
            raise ValueError(f"Movement {move_id} not found")

        # Get or create quants
        source_quant = self.quant_repo.get_by_product_location(
            move.product_id, move.source_location_id, move.lot_serial_id
        )
        if not source_quant:
            raise ValueError("Source quant not found")

        dest_quant = self.quant_repo.get_by_product_location(
            move.product_id, move.dest_location_id, move.lot_serial_id
        )
        if not dest_quant:
            dest_quant = StockQuant.create(
                product_id=move.product_id,
                location_id=move.dest_location_id,
                lot_serial_id=move.lot_serial_id,
            )
            self.quant_repo.add(dest_quant)

        # Fulfill reservation at source (removes from on_hand and reserved)
        source_quant.fulfill_reservation(move.quantity)
        self.quant_repo.update(source_quant)

        # Add to destination
        dest_quant.add_quantity(move.quantity)
        self.quant_repo.update(dest_quant)

        # Execute move
        move.execute()
        self.move_repo.update(move)

        # Publish events
        self.event_publisher.publish_all(source_quant.domain_events)
        source_quant.clear_domain_events()
        self.event_publisher.publish_all(dest_quant.domain_events)
        dest_quant.clear_domain_events()
        self.event_publisher.publish_all(move.domain_events)
        move.clear_domain_events()

        return self._map_move_to_dto(move)

    def cancel_movement(self, move_id: UUID) -> StockMoveDTO:
        """Cancel movement."""
        move = self.move_repo.get(move_id)
        if not move:
            raise ValueError(f"Movement {move_id} not found")

        # If confirmed, unreserve stock
        if move.state == StockMoveState.CONFIRMED:
            source_quant = self.quant_repo.get_by_product_location(
                move.product_id, move.source_location_id, move.lot_serial_id
            )
            if source_quant:
                source_quant.unreserve_quantity(move.quantity)
                self.quant_repo.update(source_quant)
                self.event_publisher.publish_all(source_quant.domain_events)
                source_quant.clear_domain_events()

        move.cancel()
        self.move_repo.update(move)
        self.event_publisher.publish_all(move.domain_events)
        move.clear_domain_events()

        return self._map_move_to_dto(move)

    def get_movement(self, move_id: UUID) -> StockMoveDTO:
        """Get movement by ID."""
        move = self.move_repo.get(move_id)
        if not move:
            raise ValueError(f"Movement {move_id} not found")
        return self._map_move_to_dto(move)

    def list_movements(
        self, state: Optional[str] = None, product_id: Optional[UUID] = None
    ) -> list[StockMoveDTO]:
        """List movements."""
        if state:
            moves = self.move_repo.list_by_state(StockMoveState(state))
        elif product_id:
            moves = self.move_repo.list_by_product(product_id)
        else:
            moves = self.move_repo.list_by_state(StockMoveState.DRAFT)

        return [self._map_move_to_dto(m) for m in moves]

    def _generate_movement_number(self) -> MovementNumber:
        """Generate unique movement number."""
        prefix = self.settings.movement_number_prefix
        padding = self.settings.movement_number_padding
        number = str(self._counter).zfill(padding)
        self._counter += 1
        return MovementNumber(value=f"{prefix}{number}")

    def _map_move_to_dto(self, move: StockMove) -> StockMoveDTO:
        """Map move entity to DTO."""
        return StockMoveDTO(
            id=move.id,
            movement_number=str(move.movement_number),
            product_id=move.product_id,
            product_code=move.product_code,
            product_name=move.product_name,
            quantity=move.quantity,
            uom_id=move.uom_id,
            source_location_id=move.source_location_id,
            dest_location_id=move.dest_location_id,
            move_type=move.move_type.value,
            state=move.state.value,
            lot_serial_id=move.lot_serial_id,
            reference=move.reference,
            reference_type=move.reference_type,
            reference_id=move.reference_id,
            scheduled_date=move.scheduled_date,
            executed_date=move.executed_date,
            notes=move.notes,
            created_by=move.created_by,
            created_at=move.created_at,
            updated_at=move.updated_at,
        )


class AdjustmentService:
    """Service for inventory adjustment management."""

    def __init__(
        self,
        adjustment_repo: IInventoryAdjustmentRepository,
        quant_repo: IStockQuantRepository,
        event_publisher: IEventPublisher,
        settings: InventorySettings,
    ):
        """Initialize service."""
        self.adjustment_repo = adjustment_repo
        self.quant_repo = quant_repo
        self.event_publisher = event_publisher
        self.settings = settings
        self._counter = 1

    def create_adjustment(
        self, dto: InventoryAdjustmentCreateDTO
    ) -> InventoryAdjustmentDTO:
        """Create inventory adjustment."""
        # Generate adjustment number
        adjustment_number = self._generate_adjustment_number()

        adjustment = InventoryAdjustment.create(
            adjustment_number=adjustment_number,
            reason=AdjustmentReason(dto.reason),
            notes=dto.notes,
        )

        # Add lines
        for line_dto in dto.lines:
            adjustment.add_line(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                product_name=line_dto.product_name,
                location_id=line_dto.location_id,
                theoretical_quantity=line_dto.theoretical_quantity,
                counted_quantity=line_dto.counted_quantity,
                lot_serial_id=line_dto.lot_serial_id,
            )

        self.adjustment_repo.add(adjustment)
        self.event_publisher.publish_all(adjustment.domain_events)
        adjustment.clear_domain_events()

        return self._map_adjustment_to_dto(adjustment)

    def confirm_adjustment(self, adjustment_id: UUID) -> InventoryAdjustmentDTO:
        """Confirm adjustment (applies stock changes)."""
        adjustment = self.adjustment_repo.get(adjustment_id)
        if not adjustment:
            raise ValueError(f"Adjustment {adjustment_id} not found")

        # Apply adjustments to stock
        for line in adjustment.lines:
            quant = self.quant_repo.get_by_product_location(
                line.product_id, line.location_id, line.lot_serial_id
            )

            if not quant:
                quant = StockQuant.create(
                    product_id=line.product_id,
                    location_id=line.location_id,
                    lot_serial_id=line.lot_serial_id,
                )
                self.quant_repo.add(quant)

            # Apply difference
            difference = line.difference
            if difference > 0:
                quant.add_quantity(difference)
            elif difference < 0:
                quant.remove_quantity(abs(difference))

            self.quant_repo.update(quant)
            self.event_publisher.publish_all(quant.domain_events)
            quant.clear_domain_events()

        # Confirm adjustment
        adjustment.confirm()
        self.adjustment_repo.update(adjustment)
        self.event_publisher.publish_all(adjustment.domain_events)
        adjustment.clear_domain_events()

        return self._map_adjustment_to_dto(adjustment)

    def cancel_adjustment(self, adjustment_id: UUID) -> InventoryAdjustmentDTO:
        """Cancel adjustment."""
        adjustment = self.adjustment_repo.get(adjustment_id)
        if not adjustment:
            raise ValueError(f"Adjustment {adjustment_id} not found")

        adjustment.cancel()
        self.adjustment_repo.update(adjustment)
        self.event_publisher.publish_all(adjustment.domain_events)
        adjustment.clear_domain_events()

        return self._map_adjustment_to_dto(adjustment)

    def get_adjustment(self, adjustment_id: UUID) -> InventoryAdjustmentDTO:
        """Get adjustment by ID."""
        adjustment = self.adjustment_repo.get(adjustment_id)
        if not adjustment:
            raise ValueError(f"Adjustment {adjustment_id} not found")
        return self._map_adjustment_to_dto(adjustment)

    def list_adjustments(self) -> list[InventoryAdjustmentDTO]:
        """List all adjustments."""
        adjustments = self.adjustment_repo.list_all()
        return [self._map_adjustment_to_dto(adj) for adj in adjustments]

    def _generate_adjustment_number(self) -> AdjustmentNumber:
        """Generate unique adjustment number."""
        prefix = self.settings.adjustment_number_prefix
        padding = self.settings.adjustment_number_padding
        number = str(self._counter).zfill(padding)
        self._counter += 1
        return AdjustmentNumber(value=f"{prefix}{number}")

    def _map_adjustment_to_dto(
        self, adjustment: InventoryAdjustment
    ) -> InventoryAdjustmentDTO:
        """Map adjustment entity to DTO."""
        return InventoryAdjustmentDTO(
            id=adjustment.id,
            adjustment_number=str(adjustment.adjustment_number),
            reason=adjustment.reason.value,
            state=adjustment.state.value,
            lines=[
                AdjustmentLineResponseDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    product_name=line.product_name,
                    location_id=line.location_id,
                    theoretical_quantity=line.theoretical_quantity,
                    counted_quantity=line.counted_quantity,
                    lot_serial_id=line.lot_serial_id,
                    difference=line.difference,
                )
                for line in adjustment.lines
            ],
            notes=adjustment.notes,
            adjustment_date=adjustment.adjustment_date,
            confirmed_date=adjustment.confirmed_date,
            created_by=adjustment.created_by,
            created_at=adjustment.created_at,
            updated_at=adjustment.updated_at,
        )


class ReorderingRuleService:
    """Service for reordering rule management."""

    def __init__(
        self,
        rule_repo: IReorderingRuleRepository,
        quant_repo: IStockQuantRepository,
        event_publisher: IEventPublisher,
    ):
        """Initialize service."""
        self.rule_repo = rule_repo
        self.quant_repo = quant_repo
        self.event_publisher = event_publisher

    def create_rule(self, dto: ReorderingRuleCreateDTO) -> ReorderingRuleDTO:
        """Create reordering rule."""
        rule = ReorderingRule.create(
            product_id=dto.product_id,
            location_id=dto.location_id,
            min_quantity=dto.min_quantity,
            max_quantity=dto.max_quantity,
            quantity_to_order=dto.quantity_to_order,
            route=ReorderRoute(dto.route),
            lead_time_days=dto.lead_time_days,
            supplier_id=dto.supplier_id,
        )

        self.rule_repo.add(rule)
        self.event_publisher.publish_all(rule.domain_events)
        rule.clear_domain_events()

        return self._map_rule_to_dto(rule)

    def update_rule(
        self, rule_id: UUID, dto: ReorderingRuleUpdateDTO
    ) -> ReorderingRuleDTO:
        """Update reordering rule."""
        rule = self.rule_repo.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        if dto.min_quantity is not None:
            rule.min_quantity = dto.min_quantity
        if dto.max_quantity is not None:
            rule.max_quantity = dto.max_quantity
        if dto.quantity_to_order is not None:
            rule.quantity_to_order = dto.quantity_to_order
        if dto.lead_time_days is not None:
            rule.lead_time_days = dto.lead_time_days
        if dto.supplier_id is not None:
            rule.supplier_id = dto.supplier_id

        rule.updated_at = datetime.now()
        self.rule_repo.update(rule)
        return self._map_rule_to_dto(rule)

    def check_reordering_rules(self) -> list[ReorderSuggestionDTO]:
        """Check all active rules and generate suggestions."""
        rules = self.rule_repo.list_active()
        suggestions = []

        for rule in rules:
            quants = self.quant_repo.list_by_product(rule.product_id)

            # Calculate available quantity at rule location
            location_quant = next(
                (q for q in quants if q.location_id == rule.location_id), None
            )
            available = (
                location_quant.quantity.available if location_quant else Decimal("0")
            )

            # Check if reorder needed
            if rule.should_reorder(available):
                # Get product info (simplified - would normally query product service)
                suggestions.append(
                    ReorderSuggestionDTO(
                        rule_id=rule.id,
                        product_id=rule.product_id,
                        product_code="",  # Would get from product service
                        product_name="",  # Would get from product service
                        location_id=rule.location_id,
                        current_quantity=available,
                        min_quantity=rule.min_quantity,
                        suggested_quantity=rule.quantity_to_order,
                        route=rule.route.value,
                        supplier_id=rule.supplier_id,
                    )
                )

        return suggestions

    def get_rule(self, rule_id: UUID) -> ReorderingRuleDTO:
        """Get rule by ID."""
        rule = self.rule_repo.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        return self._map_rule_to_dto(rule)

    def list_active_rules(self) -> list[ReorderingRuleDTO]:
        """List all active rules."""
        rules = self.rule_repo.list_active()
        return [self._map_rule_to_dto(r) for r in rules]

    def _map_rule_to_dto(self, rule: ReorderingRule) -> ReorderingRuleDTO:
        """Map rule entity to DTO."""
        return ReorderingRuleDTO(
            id=rule.id,
            product_id=rule.product_id,
            location_id=rule.location_id,
            min_quantity=rule.min_quantity,
            max_quantity=rule.max_quantity,
            quantity_to_order=rule.quantity_to_order,
            route=rule.route.value,
            lead_time_days=rule.lead_time_days,
            is_active=rule.is_active,
            supplier_id=rule.supplier_id,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )


class LotSerialService:
    """Service for lot/serial number management."""

    def __init__(
        self,
        lot_repo: ILotSerialRepository,
        move_repo: IStockMoveRepository,
        event_publisher: IEventPublisher,
    ):
        """Initialize service."""
        self.lot_repo = lot_repo
        self.move_repo = move_repo
        self.event_publisher = event_publisher

    def create_lot(self, dto: LotSerialCreateDTO) -> LotSerialDTO:
        """Create lot/serial number."""
        # Check if already exists
        existing = self.lot_repo.get_by_number(dto.lot_serial_number, dto.product_id)
        if existing:
            raise ValueError(
                f"Lot/Serial {dto.lot_serial_number} already exists for product"
            )

        lot = LotSerial.create(
            lot_serial_number=LotSerialNumber(value=dto.lot_serial_number),
            product_id=dto.product_id,
            is_serial=dto.is_serial,
            expiration_date=dto.expiration_date,
            manufacture_date=dto.manufacture_date,
            notes=dto.notes,
        )

        self.lot_repo.add(lot)
        self.event_publisher.publish_all(lot.domain_events)
        lot.clear_domain_events()

        return self._map_lot_to_dto(lot)

    def get_lot(self, lot_id: UUID) -> LotSerialDTO:
        """Get lot/serial by ID."""
        lot = self.lot_repo.get(lot_id)
        if not lot:
            raise ValueError(f"Lot/Serial {lot_id} not found")
        return self._map_lot_to_dto(lot)

    def trace_lot(self, lot_id: UUID) -> LotTraceDTO:
        """Trace lot movements."""
        lot = self.lot_repo.get(lot_id)
        if not lot:
            raise ValueError(f"Lot/Serial {lot_id} not found")

        # Get all movements for this lot
        # (Simplified - would need proper tracing logic)
        movements = []

        return LotTraceDTO(
            lot_id=lot.id,
            lot_serial_number=str(lot.lot_serial_number),
            product_id=lot.product_id,
            movements=movements,
        )

    def list_by_product(
        self, product_id: UUID, exclude_expired: bool = False
    ) -> list[LotSerialDTO]:
        """List lots for a product."""
        lots = self.lot_repo.list_by_product(
            product_id, exclude_expired=exclude_expired
        )
        return [self._map_lot_to_dto(lot) for lot in lots]

    def _map_lot_to_dto(self, lot: LotSerial) -> LotSerialDTO:
        """Map lot entity to DTO."""
        return LotSerialDTO(
            id=lot.id,
            lot_serial_number=str(lot.lot_serial_number),
            product_id=lot.product_id,
            is_serial=lot.is_serial,
            expiration_date=lot.expiration_date,
            manufacture_date=lot.manufacture_date,
            notes=lot.notes,
            created_at=lot.created_at,
            updated_at=lot.updated_at,
        )
