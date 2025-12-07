"""Domain repository interfaces for inventory."""

from typing import Optional, Protocol
from uuid import UUID

from serp_inventory.domain.entities import (
    InventoryAdjustment,
    LotSerial,
    ReorderingRule,
    StockLocation,
    StockMove,
    StockQuant,
    Warehouse,
)
from serp_inventory.domain.value_objects import (
    AdjustmentNumber,
    LocationCode,
    MovementNumber,
    StockMoveState,
)


class IWarehouseRepository(Protocol):
    """Warehouse repository interface."""

    def add(self, warehouse: Warehouse) -> None:
        """Add warehouse."""
        ...

    def get(self, id: UUID) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        ...

    def get_by_code(self, code: str) -> Optional[Warehouse]:
        """Get warehouse by code."""
        ...

    def list_all(self, active_only: bool = False) -> list[Warehouse]:
        """List all warehouses."""
        ...

    def update(self, warehouse: Warehouse) -> None:
        """Update warehouse."""
        ...


class IStockLocationRepository(Protocol):
    """Stock location repository interface."""

    def add(self, location: StockLocation) -> None:
        """Add location."""
        ...

    def get(self, id: UUID) -> Optional[StockLocation]:
        """Get location by ID."""
        ...

    def get_by_code(self, code: LocationCode) -> Optional[StockLocation]:
        """Get location by code."""
        ...

    def list_by_warehouse(
        self, warehouse_id: UUID, active_only: bool = False
    ) -> list[StockLocation]:
        """List locations in warehouse."""
        ...

    def list_children(self, parent_id: UUID) -> list[StockLocation]:
        """List child locations."""
        ...

    def update(self, location: StockLocation) -> None:
        """Update location."""
        ...


class IStockQuantRepository(Protocol):
    """Stock quantity repository interface."""

    def add(self, quant: StockQuant) -> None:
        """Add stock quant."""
        ...

    def get(self, id: UUID) -> Optional[StockQuant]:
        """Get quant by ID."""
        ...

    def get_by_product_location(
        self,
        product_id: UUID,
        location_id: UUID,
        lot_serial_id: Optional[UUID] = None,
    ) -> Optional[StockQuant]:
        """Get quant for specific product at location."""
        ...

    def list_by_product(self, product_id: UUID) -> list[StockQuant]:
        """List all quants for a product."""
        ...

    def list_by_location(self, location_id: UUID) -> list[StockQuant]:
        """List all quants in a location."""
        ...

    def update(self, quant: StockQuant) -> None:
        """Update quant."""
        ...


class IStockMoveRepository(Protocol):
    """Stock move repository interface."""

    def add(self, move: StockMove) -> None:
        """Add stock move."""
        ...

    def get(self, id: UUID) -> Optional[StockMove]:
        """Get move by ID."""
        ...

    def get_by_number(self, number: MovementNumber) -> Optional[StockMove]:
        """Get move by movement number."""
        ...

    def list_by_state(self, state: StockMoveState) -> list[StockMove]:
        """List moves by state."""
        ...

    def list_by_reference(
        self, reference_type: str, reference_id: UUID
    ) -> list[StockMove]:
        """List moves by reference document."""
        ...

    def list_by_product(self, product_id: UUID) -> list[StockMove]:
        """List moves for a product."""
        ...

    def update(self, move: StockMove) -> None:
        """Update move."""
        ...


class IInventoryAdjustmentRepository(Protocol):
    """Inventory adjustment repository interface."""

    def add(self, adjustment: InventoryAdjustment) -> None:
        """Add adjustment."""
        ...

    def get(self, id: UUID) -> Optional[InventoryAdjustment]:
        """Get adjustment by ID."""
        ...

    def get_by_number(self, number: AdjustmentNumber) -> Optional[InventoryAdjustment]:
        """Get adjustment by number."""
        ...

    def list_all(self) -> list[InventoryAdjustment]:
        """List all adjustments."""
        ...

    def update(self, adjustment: InventoryAdjustment) -> None:
        """Update adjustment."""
        ...


class IReorderingRuleRepository(Protocol):
    """Reordering rule repository interface."""

    def add(self, rule: ReorderingRule) -> None:
        """Add rule."""
        ...

    def get(self, id: UUID) -> Optional[ReorderingRule]:
        """Get rule by ID."""
        ...

    def list_by_product(self, product_id: UUID) -> list[ReorderingRule]:
        """List rules for a product."""
        ...

    def list_active(self) -> list[ReorderingRule]:
        """List all active rules."""
        ...

    def update(self, rule: ReorderingRule) -> None:
        """Update rule."""
        ...


class ILotSerialRepository(Protocol):
    """Lot/Serial repository interface."""

    def add(self, lot: LotSerial) -> None:
        """Add lot/serial."""
        ...

    def get(self, id: UUID) -> Optional[LotSerial]:
        """Get lot/serial by ID."""
        ...

    def get_by_number(self, number: str, product_id: UUID) -> Optional[LotSerial]:
        """Get lot/serial by number and product."""
        ...

    def list_by_product(
        self, product_id: UUID, exclude_expired: bool = False
    ) -> list[LotSerial]:
        """List lots/serials for a product."""
        ...

    def update(self, lot: LotSerial) -> None:
        """Update lot/serial."""
        ...
