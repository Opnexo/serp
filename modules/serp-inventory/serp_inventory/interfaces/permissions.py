"""Permissions for inventory module."""

from serp_core.auth import Permission

# Warehouse permissions
WAREHOUSE_CREATE = Permission("inventory.warehouse.create")
WAREHOUSE_READ = Permission("inventory.warehouse.read")
WAREHOUSE_UPDATE = Permission("inventory.warehouse.update")
WAREHOUSE_ACTIVATE = Permission("inventory.warehouse.activate")
WAREHOUSE_DEACTIVATE = Permission("inventory.warehouse.deactivate")

# Stock location permissions
LOCATION_CREATE = Permission("inventory.location.create")
LOCATION_READ = Permission("inventory.location.read")
LOCATION_UPDATE = Permission("inventory.location.update")

# Stock level permissions
STOCK_READ = Permission("inventory.stock.read")
STOCK_RESERVE = Permission("inventory.stock.reserve")
STOCK_UNRESERVE = Permission("inventory.stock.unreserve")

# Stock movement permissions
MOVEMENT_CREATE = Permission("inventory.movement.create")
MOVEMENT_READ = Permission("inventory.movement.read")
MOVEMENT_CONFIRM = Permission("inventory.movement.confirm")
MOVEMENT_EXECUTE = Permission("inventory.movement.execute")
MOVEMENT_CANCEL = Permission("inventory.movement.cancel")

# Inventory adjustment permissions
ADJUSTMENT_CREATE = Permission("inventory.adjustment.create")
ADJUSTMENT_READ = Permission("inventory.adjustment.read")
ADJUSTMENT_CONFIRM = Permission("inventory.adjustment.confirm")
ADJUSTMENT_CANCEL = Permission("inventory.adjustment.cancel")

# Reordering rule permissions
REORDER_RULE_CREATE = Permission("inventory.reorder.create")
REORDER_RULE_READ = Permission("inventory.reorder.read")
REORDER_RULE_UPDATE = Permission("inventory.reorder.update")
REORDER_CHECK = Permission("inventory.reorder.check")

# Lot/Serial permissions
LOT_CREATE = Permission("inventory.lot.create")
LOT_READ = Permission("inventory.lot.read")
LOT_TRACE = Permission("inventory.lot.trace")

# Permission groups
ADMIN_PERMISSIONS = [
    WAREHOUSE_CREATE,
    WAREHOUSE_READ,
    WAREHOUSE_UPDATE,
    WAREHOUSE_ACTIVATE,
    WAREHOUSE_DEACTIVATE,
    LOCATION_CREATE,
    LOCATION_READ,
    LOCATION_UPDATE,
    STOCK_READ,
    STOCK_RESERVE,
    STOCK_UNRESERVE,
    MOVEMENT_CREATE,
    MOVEMENT_READ,
    MOVEMENT_CONFIRM,
    MOVEMENT_EXECUTE,
    MOVEMENT_CANCEL,
    ADJUSTMENT_CREATE,
    ADJUSTMENT_READ,
    ADJUSTMENT_CONFIRM,
    ADJUSTMENT_CANCEL,
    REORDER_RULE_CREATE,
    REORDER_RULE_READ,
    REORDER_RULE_UPDATE,
    REORDER_CHECK,
    LOT_CREATE,
    LOT_READ,
    LOT_TRACE,
]

WAREHOUSE_MANAGER_PERMISSIONS = [
    WAREHOUSE_READ,
    LOCATION_READ,
    LOCATION_UPDATE,
    STOCK_READ,
    STOCK_RESERVE,
    STOCK_UNRESERVE,
    MOVEMENT_CREATE,
    MOVEMENT_READ,
    MOVEMENT_CONFIRM,
    MOVEMENT_EXECUTE,
    MOVEMENT_CANCEL,
    ADJUSTMENT_CREATE,
    ADJUSTMENT_READ,
    ADJUSTMENT_CONFIRM,
    LOT_CREATE,
    LOT_READ,
    LOT_TRACE,
]

WAREHOUSE_OPERATOR_PERMISSIONS = [
    WAREHOUSE_READ,
    LOCATION_READ,
    STOCK_READ,
    MOVEMENT_READ,
    MOVEMENT_EXECUTE,
    ADJUSTMENT_READ,
    LOT_READ,
]

INVENTORY_ANALYST_PERMISSIONS = [
    WAREHOUSE_READ,
    LOCATION_READ,
    STOCK_READ,
    MOVEMENT_READ,
    ADJUSTMENT_READ,
    REORDER_RULE_READ,
    REORDER_CHECK,
    LOT_READ,
    LOT_TRACE,
]
