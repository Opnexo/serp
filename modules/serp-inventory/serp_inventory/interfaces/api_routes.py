"""API routes for inventory module."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from serp_core.auth import require_permissions

from serp_inventory.application import (
    AdjustmentService,
    InventoryAdjustmentCreateDTO,
    InventoryAdjustmentDTO,
    LotSerialCreateDTO,
    LotSerialDTO,
    LotSerialService,
    LotTraceDTO,
    MovementService,
    ReorderingRuleCreateDTO,
    ReorderingRuleDTO,
    ReorderingRuleService,
    ReorderingRuleUpdateDTO,
    ReorderSuggestionDTO,
    StockAvailabilityDTO,
    StockLocationCreateDTO,
    StockLocationDTO,
    StockLocationService,
    StockLocationUpdateDTO,
    StockMoveCreateDTO,
    StockMoveDTO,
    StockService,
    WarehouseCreateDTO,
    WarehouseDTO,
    WarehouseService,
    WarehouseUpdateDTO,
)
from serp_inventory.interfaces.permissions import (
    ADJUSTMENT_CANCEL,
    ADJUSTMENT_CONFIRM,
    ADJUSTMENT_CREATE,
    ADJUSTMENT_READ,
    LOCATION_CREATE,
    LOCATION_READ,
    LOCATION_UPDATE,
    LOT_CREATE,
    LOT_READ,
    LOT_TRACE,
    MOVEMENT_CANCEL,
    MOVEMENT_CONFIRM,
    MOVEMENT_CREATE,
    MOVEMENT_EXECUTE,
    MOVEMENT_READ,
    REORDER_CHECK,
    REORDER_RULE_CREATE,
    REORDER_RULE_READ,
    REORDER_RULE_UPDATE,
    STOCK_READ,
    STOCK_RESERVE,
    STOCK_UNRESERVE,
    WAREHOUSE_ACTIVATE,
    WAREHOUSE_CREATE,
    WAREHOUSE_DEACTIVATE,
    WAREHOUSE_READ,
    WAREHOUSE_UPDATE,
)

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


# Warehouse endpoints
@router.post(
    "/warehouses",
    response_model=WarehouseDTO,
    dependencies=[Depends(require_permissions(WAREHOUSE_CREATE))],
)
async def create_warehouse(
    dto: WarehouseCreateDTO, service: WarehouseService = Depends()
) -> WarehouseDTO:
    """Create a new warehouse."""
    return service.create_warehouse(dto)


@router.get(
    "/warehouses/{warehouse_id}",
    response_model=WarehouseDTO,
    dependencies=[Depends(require_permissions(WAREHOUSE_READ))],
)
async def get_warehouse(
    warehouse_id: UUID, service: WarehouseService = Depends()
) -> WarehouseDTO:
    """Get warehouse by ID."""
    return service.get_warehouse(warehouse_id)


@router.put(
    "/warehouses/{warehouse_id}",
    response_model=WarehouseDTO,
    dependencies=[Depends(require_permissions(WAREHOUSE_UPDATE))],
)
async def update_warehouse(
    warehouse_id: UUID,
    dto: WarehouseUpdateDTO,
    service: WarehouseService = Depends(),
) -> WarehouseDTO:
    """Update warehouse."""
    return service.update_warehouse(warehouse_id, dto)


@router.post(
    "/warehouses/{warehouse_id}/activate",
    response_model=WarehouseDTO,
    dependencies=[Depends(require_permissions(WAREHOUSE_ACTIVATE))],
)
async def activate_warehouse(
    warehouse_id: UUID, service: WarehouseService = Depends()
) -> WarehouseDTO:
    """Activate warehouse."""
    return service.activate_warehouse(warehouse_id)


@router.post(
    "/warehouses/{warehouse_id}/deactivate",
    response_model=WarehouseDTO,
    dependencies=[Depends(require_permissions(WAREHOUSE_DEACTIVATE))],
)
async def deactivate_warehouse(
    warehouse_id: UUID, service: WarehouseService = Depends()
) -> WarehouseDTO:
    """Deactivate warehouse."""
    return service.deactivate_warehouse(warehouse_id)


@router.get(
    "/warehouses",
    response_model=list[WarehouseDTO],
    dependencies=[Depends(require_permissions(WAREHOUSE_READ))],
)
async def list_warehouses(
    active_only: bool = Query(False), service: WarehouseService = Depends()
) -> list[WarehouseDTO]:
    """List all warehouses."""
    return service.list_warehouses(active_only=active_only)


# Stock Location endpoints
@router.post(
    "/locations",
    response_model=StockLocationDTO,
    dependencies=[Depends(require_permissions(LOCATION_CREATE))],
)
async def create_location(
    dto: StockLocationCreateDTO, service: StockLocationService = Depends()
) -> StockLocationDTO:
    """Create a new stock location."""
    return service.create_location(dto)


@router.get(
    "/locations/{location_id}",
    response_model=StockLocationDTO,
    dependencies=[Depends(require_permissions(LOCATION_READ))],
)
async def get_location(
    location_id: UUID, service: StockLocationService = Depends()
) -> StockLocationDTO:
    """Get location by ID."""
    return service.get_location(location_id)


@router.put(
    "/locations/{location_id}",
    response_model=StockLocationDTO,
    dependencies=[Depends(require_permissions(LOCATION_UPDATE))],
)
async def update_location(
    location_id: UUID,
    dto: StockLocationUpdateDTO,
    service: StockLocationService = Depends(),
) -> StockLocationDTO:
    """Update location."""
    return service.update_location(location_id, dto)


@router.get(
    "/locations",
    response_model=list[StockLocationDTO],
    dependencies=[Depends(require_permissions(LOCATION_READ))],
)
async def list_locations(
    warehouse_id: Optional[UUID] = Query(None),
    active_only: bool = Query(False),
    service: StockLocationService = Depends(),
) -> list[StockLocationDTO]:
    """List locations, optionally filtered by warehouse."""
    if warehouse_id:
        return service.list_by_warehouse(warehouse_id, active_only=active_only)
    return []


@router.get(
    "/locations/{location_id}/children",
    response_model=list[StockLocationDTO],
    dependencies=[Depends(require_permissions(LOCATION_READ))],
)
async def list_child_locations(
    location_id: UUID, service: StockLocationService = Depends()
) -> list[StockLocationDTO]:
    """List child locations."""
    return service.list_children(location_id)


# Stock Level endpoints
@router.get(
    "/stock/product/{product_id}",
    response_model=StockAvailabilityDTO,
    dependencies=[Depends(require_permissions(STOCK_READ))],
)
async def get_product_stock(
    product_id: UUID,
    product_code: str = Query(...),
    product_name: str = Query(...),
    service: StockService = Depends(),
) -> StockAvailabilityDTO:
    """Get stock levels for a product across all locations."""
    return service.get_product_availability(product_id, product_code, product_name)


@router.post(
    "/stock/reserve",
    dependencies=[Depends(require_permissions(STOCK_RESERVE))],
)
async def reserve_stock(
    product_id: UUID = Query(...),
    location_id: UUID = Query(...),
    quantity: float = Query(..., gt=0),
    lot_serial_id: Optional[UUID] = Query(None),
    service: StockService = Depends(),
) -> dict:
    """Reserve stock quantity."""
    from decimal import Decimal

    service.reserve_stock(
        product_id, location_id, Decimal(str(quantity)), lot_serial_id
    )
    return {"status": "reserved"}


@router.post(
    "/stock/unreserve",
    dependencies=[Depends(require_permissions(STOCK_UNRESERVE))],
)
async def unreserve_stock(
    product_id: UUID = Query(...),
    location_id: UUID = Query(...),
    quantity: float = Query(..., gt=0),
    lot_serial_id: Optional[UUID] = Query(None),
    service: StockService = Depends(),
) -> dict:
    """Unreserve stock quantity."""
    from decimal import Decimal

    service.unreserve_stock(
        product_id, location_id, Decimal(str(quantity)), lot_serial_id
    )
    return {"status": "unreserved"}


# Stock Movement endpoints
@router.post(
    "/moves",
    response_model=StockMoveDTO,
    dependencies=[Depends(require_permissions(MOVEMENT_CREATE))],
)
async def create_movement(
    dto: StockMoveCreateDTO, service: MovementService = Depends()
) -> StockMoveDTO:
    """Create a new stock movement."""
    return service.create_movement(dto)


@router.get(
    "/moves/{move_id}",
    response_model=StockMoveDTO,
    dependencies=[Depends(require_permissions(MOVEMENT_READ))],
)
async def get_movement(
    move_id: UUID, service: MovementService = Depends()
) -> StockMoveDTO:
    """Get movement by ID."""
    return service.get_movement(move_id)


@router.post(
    "/moves/{move_id}/confirm",
    response_model=StockMoveDTO,
    dependencies=[Depends(require_permissions(MOVEMENT_CONFIRM))],
)
async def confirm_movement(
    move_id: UUID, service: MovementService = Depends()
) -> StockMoveDTO:
    """Confirm movement (reserves stock)."""
    return service.confirm_movement(move_id)


@router.post(
    "/moves/{move_id}/execute",
    response_model=StockMoveDTO,
    dependencies=[Depends(require_permissions(MOVEMENT_EXECUTE))],
)
async def execute_movement(
    move_id: UUID, service: MovementService = Depends()
) -> StockMoveDTO:
    """Execute movement (moves the stock)."""
    return service.execute_movement(move_id)


@router.post(
    "/moves/{move_id}/cancel",
    response_model=StockMoveDTO,
    dependencies=[Depends(require_permissions(MOVEMENT_CANCEL))],
)
async def cancel_movement(
    move_id: UUID, service: MovementService = Depends()
) -> StockMoveDTO:
    """Cancel movement."""
    return service.cancel_movement(move_id)


@router.get(
    "/moves",
    response_model=list[StockMoveDTO],
    dependencies=[Depends(require_permissions(MOVEMENT_READ))],
)
async def list_movements(
    state: Optional[str] = Query(None),
    product_id: Optional[UUID] = Query(None),
    service: MovementService = Depends(),
) -> list[StockMoveDTO]:
    """List movements."""
    return service.list_movements(state=state, product_id=product_id)


# Inventory Adjustment endpoints
@router.post(
    "/adjustments",
    response_model=InventoryAdjustmentDTO,
    dependencies=[Depends(require_permissions(ADJUSTMENT_CREATE))],
)
async def create_adjustment(
    dto: InventoryAdjustmentCreateDTO, service: AdjustmentService = Depends()
) -> InventoryAdjustmentDTO:
    """Create inventory adjustment."""
    return service.create_adjustment(dto)


@router.get(
    "/adjustments/{adjustment_id}",
    response_model=InventoryAdjustmentDTO,
    dependencies=[Depends(require_permissions(ADJUSTMENT_READ))],
)
async def get_adjustment(
    adjustment_id: UUID, service: AdjustmentService = Depends()
) -> InventoryAdjustmentDTO:
    """Get adjustment by ID."""
    return service.get_adjustment(adjustment_id)


@router.post(
    "/adjustments/{adjustment_id}/confirm",
    response_model=InventoryAdjustmentDTO,
    dependencies=[Depends(require_permissions(ADJUSTMENT_CONFIRM))],
)
async def confirm_adjustment(
    adjustment_id: UUID, service: AdjustmentService = Depends()
) -> InventoryAdjustmentDTO:
    """Confirm adjustment (applies stock changes)."""
    return service.confirm_adjustment(adjustment_id)


@router.post(
    "/adjustments/{adjustment_id}/cancel",
    response_model=InventoryAdjustmentDTO,
    dependencies=[Depends(require_permissions(ADJUSTMENT_CANCEL))],
)
async def cancel_adjustment(
    adjustment_id: UUID, service: AdjustmentService = Depends()
) -> InventoryAdjustmentDTO:
    """Cancel adjustment."""
    return service.cancel_adjustment(adjustment_id)


@router.get(
    "/adjustments",
    response_model=list[InventoryAdjustmentDTO],
    dependencies=[Depends(require_permissions(ADJUSTMENT_READ))],
)
async def list_adjustments(
    service: AdjustmentService = Depends(),
) -> list[InventoryAdjustmentDTO]:
    """List all adjustments."""
    return service.list_adjustments()


# Reordering Rule endpoints
@router.post(
    "/reordering-rules",
    response_model=ReorderingRuleDTO,
    dependencies=[Depends(require_permissions(REORDER_RULE_CREATE))],
)
async def create_reordering_rule(
    dto: ReorderingRuleCreateDTO, service: ReorderingRuleService = Depends()
) -> ReorderingRuleDTO:
    """Create reordering rule."""
    return service.create_rule(dto)


@router.get(
    "/reordering-rules/{rule_id}",
    response_model=ReorderingRuleDTO,
    dependencies=[Depends(require_permissions(REORDER_RULE_READ))],
)
async def get_reordering_rule(
    rule_id: UUID, service: ReorderingRuleService = Depends()
) -> ReorderingRuleDTO:
    """Get reordering rule by ID."""
    return service.get_rule(rule_id)


@router.put(
    "/reordering-rules/{rule_id}",
    response_model=ReorderingRuleDTO,
    dependencies=[Depends(require_permissions(REORDER_RULE_UPDATE))],
)
async def update_reordering_rule(
    rule_id: UUID,
    dto: ReorderingRuleUpdateDTO,
    service: ReorderingRuleService = Depends(),
) -> ReorderingRuleDTO:
    """Update reordering rule."""
    return service.update_rule(rule_id, dto)


@router.get(
    "/reordering-rules",
    response_model=list[ReorderingRuleDTO],
    dependencies=[Depends(require_permissions(REORDER_RULE_READ))],
)
async def list_reordering_rules(
    service: ReorderingRuleService = Depends(),
) -> list[ReorderingRuleDTO]:
    """List all active reordering rules."""
    return service.list_active_rules()


@router.post(
    "/reordering-rules/check",
    response_model=list[ReorderSuggestionDTO],
    dependencies=[Depends(require_permissions(REORDER_CHECK))],
)
async def check_reordering_rules(
    service: ReorderingRuleService = Depends(),
) -> list[ReorderSuggestionDTO]:
    """Check reordering rules and get suggestions."""
    return service.check_reordering_rules()


# Lot/Serial endpoints
@router.post(
    "/lots",
    response_model=LotSerialDTO,
    dependencies=[Depends(require_permissions(LOT_CREATE))],
)
async def create_lot(
    dto: LotSerialCreateDTO, service: LotSerialService = Depends()
) -> LotSerialDTO:
    """Create lot/serial number."""
    return service.create_lot(dto)


@router.get(
    "/lots/{lot_id}",
    response_model=LotSerialDTO,
    dependencies=[Depends(require_permissions(LOT_READ))],
)
async def get_lot(lot_id: UUID, service: LotSerialService = Depends()) -> LotSerialDTO:
    """Get lot/serial by ID."""
    return service.get_lot(lot_id)


@router.get(
    "/lots/product/{product_id}",
    response_model=list[LotSerialDTO],
    dependencies=[Depends(require_permissions(LOT_READ))],
)
async def list_product_lots(
    product_id: UUID,
    exclude_expired: bool = Query(False),
    service: LotSerialService = Depends(),
) -> list[LotSerialDTO]:
    """List lots for a product."""
    return service.list_by_product(product_id, exclude_expired=exclude_expired)


@router.get(
    "/lots/{lot_id}/trace",
    response_model=LotTraceDTO,
    dependencies=[Depends(require_permissions(LOT_TRACE))],
)
async def trace_lot(lot_id: UUID, service: LotSerialService = Depends()) -> LotTraceDTO:
    """Trace lot movements."""
    return service.trace_lot(lot_id)
