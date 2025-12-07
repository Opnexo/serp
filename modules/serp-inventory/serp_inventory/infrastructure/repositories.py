"""In-memory repository implementations for inventory."""

from typing import Optional
from uuid import UUID

from serp_inventory.domain import (
    AdjustmentNumber,
    InventoryAdjustment,
    LocationCode,
    LotSerial,
    MovementNumber,
    ReorderingRule,
    StockLocation,
    StockMove,
    StockMoveState,
    StockQuant,
    Warehouse,
)


class InMemoryWarehouseRepository:
    """In-memory warehouse repository."""

    def __init__(self):
        """Initialize repository."""
        self._warehouses: dict[UUID, Warehouse] = {}

    def add(self, warehouse: Warehouse) -> None:
        """Add warehouse."""
        self._warehouses[warehouse.id] = warehouse

    def get(self, id: UUID) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        return self._warehouses.get(id)

    def get_by_code(self, code: str) -> Optional[Warehouse]:
        """Get warehouse by code."""
        return next((w for w in self._warehouses.values() if w.code == code), None)

    def list_all(self, active_only: bool = False) -> list[Warehouse]:
        """List all warehouses."""
        warehouses = list(self._warehouses.values())
        if active_only:
            warehouses = [w for w in warehouses if w.is_active]
        return warehouses

    def update(self, warehouse: Warehouse) -> None:
        """Update warehouse."""
        self._warehouses[warehouse.id] = warehouse


class InMemoryStockLocationRepository:
    """In-memory stock location repository."""

    def __init__(self):
        """Initialize repository."""
        self._locations: dict[UUID, StockLocation] = {}

    def add(self, location: StockLocation) -> None:
        """Add location."""
        self._locations[location.id] = location

    def get(self, id: UUID) -> Optional[StockLocation]:
        """Get location by ID."""
        return self._locations.get(id)

    def get_by_code(self, code: LocationCode) -> Optional[StockLocation]:
        """Get location by code."""
        return next(
            (
                loc
                for loc in self._locations.values()
                if str(loc.location_code) == str(code)
            ),
            None,
        )

    def list_by_warehouse(
        self, warehouse_id: UUID, active_only: bool = False
    ) -> list[StockLocation]:
        """List locations in warehouse."""
        locations = [
            loc for loc in self._locations.values() if loc.warehouse_id == warehouse_id
        ]
        if active_only:
            locations = [loc for loc in locations if loc.is_active]
        return locations

    def list_children(self, parent_id: UUID) -> list[StockLocation]:
        """List child locations."""
        return [
            loc
            for loc in self._locations.values()
            if loc.parent_location_id == parent_id
        ]

    def update(self, location: StockLocation) -> None:
        """Update location."""
        self._locations[location.id] = location


class InMemoryStockQuantRepository:
    """In-memory stock quant repository."""

    def __init__(self):
        """Initialize repository."""
        self._quants: dict[UUID, StockQuant] = {}

    def add(self, quant: StockQuant) -> None:
        """Add stock quant."""
        self._quants[quant.id] = quant

    def get(self, id: UUID) -> Optional[StockQuant]:
        """Get quant by ID."""
        return self._quants.get(id)

    def get_by_product_location(
        self,
        product_id: UUID,
        location_id: UUID,
        lot_serial_id: Optional[UUID] = None,
    ) -> Optional[StockQuant]:
        """Get quant for specific product at location."""
        return next(
            (
                q
                for q in self._quants.values()
                if q.product_id == product_id
                and q.location_id == location_id
                and q.lot_serial_id == lot_serial_id
            ),
            None,
        )

    def list_by_product(self, product_id: UUID) -> list[StockQuant]:
        """List all quants for a product."""
        return [q for q in self._quants.values() if q.product_id == product_id]

    def list_by_location(self, location_id: UUID) -> list[StockQuant]:
        """List all quants in a location."""
        return [q for q in self._quants.values() if q.location_id == location_id]

    def update(self, quant: StockQuant) -> None:
        """Update quant."""
        self._quants[quant.id] = quant


class InMemoryStockMoveRepository:
    """In-memory stock move repository."""

    def __init__(self):
        """Initialize repository."""
        self._moves: dict[UUID, StockMove] = {}

    def add(self, move: StockMove) -> None:
        """Add stock move."""
        self._moves[move.id] = move

    def get(self, id: UUID) -> Optional[StockMove]:
        """Get move by ID."""
        return self._moves.get(id)

    def get_by_number(self, number: MovementNumber) -> Optional[StockMove]:
        """Get move by movement number."""
        return next(
            (m for m in self._moves.values() if str(m.movement_number) == str(number)),
            None,
        )

    def list_by_state(self, state: StockMoveState) -> list[StockMove]:
        """List moves by state."""
        return [m for m in self._moves.values() if m.state == state]

    def list_by_reference(
        self, reference_type: str, reference_id: UUID
    ) -> list[StockMove]:
        """List moves by reference document."""
        return [
            m
            for m in self._moves.values()
            if m.reference_type == reference_type and m.reference_id == reference_id
        ]

    def list_by_product(self, product_id: UUID) -> list[StockMove]:
        """List moves for a product."""
        return [m for m in self._moves.values() if m.product_id == product_id]

    def update(self, move: StockMove) -> None:
        """Update move."""
        self._moves[move.id] = move


class InMemoryInventoryAdjustmentRepository:
    """In-memory inventory adjustment repository."""

    def __init__(self):
        """Initialize repository."""
        self._adjustments: dict[UUID, InventoryAdjustment] = {}

    def add(self, adjustment: InventoryAdjustment) -> None:
        """Add adjustment."""
        self._adjustments[adjustment.id] = adjustment

    def get(self, id: UUID) -> Optional[InventoryAdjustment]:
        """Get adjustment by ID."""
        return self._adjustments.get(id)

    def get_by_number(self, number: AdjustmentNumber) -> Optional[InventoryAdjustment]:
        """Get adjustment by number."""
        return next(
            (
                adj
                for adj in self._adjustments.values()
                if str(adj.adjustment_number) == str(number)
            ),
            None,
        )

    def list_all(self) -> list[InventoryAdjustment]:
        """List all adjustments."""
        return list(self._adjustments.values())

    def update(self, adjustment: InventoryAdjustment) -> None:
        """Update adjustment."""
        self._adjustments[adjustment.id] = adjustment


class InMemoryReorderingRuleRepository:
    """In-memory reordering rule repository."""

    def __init__(self):
        """Initialize repository."""
        self._rules: dict[UUID, ReorderingRule] = {}

    def add(self, rule: ReorderingRule) -> None:
        """Add rule."""
        self._rules[rule.id] = rule

    def get(self, id: UUID) -> Optional[ReorderingRule]:
        """Get rule by ID."""
        return self._rules.get(id)

    def list_by_product(self, product_id: UUID) -> list[ReorderingRule]:
        """List rules for a product."""
        return [r for r in self._rules.values() if r.product_id == product_id]

    def list_active(self) -> list[ReorderingRule]:
        """List all active rules."""
        return [r for r in self._rules.values() if r.is_active]

    def update(self, rule: ReorderingRule) -> None:
        """Update rule."""
        self._rules[rule.id] = rule


class InMemoryLotSerialRepository:
    """In-memory lot/serial repository."""

    def __init__(self):
        """Initialize repository."""
        self._lots: dict[UUID, LotSerial] = {}

    def add(self, lot: LotSerial) -> None:
        """Add lot/serial."""
        self._lots[lot.id] = lot

    def get(self, id: UUID) -> Optional[LotSerial]:
        """Get lot/serial by ID."""
        return self._lots.get(id)

    def get_by_number(self, number: str, product_id: UUID) -> Optional[LotSerial]:
        """Get lot/serial by number and product."""
        return next(
            (
                lot
                for lot in self._lots.values()
                if str(lot.lot_serial_number) == number and lot.product_id == product_id
            ),
            None,
        )

    def list_by_product(
        self, product_id: UUID, exclude_expired: bool = False
    ) -> list[LotSerial]:
        """List lots/serials for a product."""
        lots = [lot for lot in self._lots.values() if lot.product_id == product_id]
        if exclude_expired:
            lots = [lot for lot in lots if not lot.is_expired()]
        return lots

    def update(self, lot: LotSerial) -> None:
        """Update lot/serial."""
        self._lots[lot.id] = lot
