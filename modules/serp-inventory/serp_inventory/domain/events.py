"""Domain events for inventory."""

from serp_core.domain import DomainEvent


# Warehouse Events
class WarehouseCreated(DomainEvent):
    """Warehouse created event."""

    pass


class WarehouseActivated(DomainEvent):
    """Warehouse activated event."""

    pass


class WarehouseDeactivated(DomainEvent):
    """Warehouse deactivated event."""

    pass


# Location Events
class StockLocationCreated(DomainEvent):
    """Stock location created event."""

    pass


# Stock Quant Events
class StockQuantAdded(DomainEvent):
    """Stock quantity added event."""

    pass


class StockQuantityAdded(DomainEvent):
    """Stock quantity increased event."""

    pass


class StockQuantityRemoved(DomainEvent):
    """Stock quantity decreased event."""

    pass


class StockQuantityReserved(DomainEvent):
    """Stock quantity reserved event."""

    pass


class StockQuantityUnreserved(DomainEvent):
    """Stock quantity unreserved event."""

    pass


class StockReservationFulfilled(DomainEvent):
    """Stock reservation fulfilled event."""

    pass


# Stock Move Events
class StockMoveCreated(DomainEvent):
    """Stock move created event."""

    pass


class StockMoveConfirmed(DomainEvent):
    """Stock move confirmed event."""

    pass


class StockMoveExecuted(DomainEvent):
    """Stock move executed event."""

    pass


class StockMoveCancelled(DomainEvent):
    """Stock move cancelled event."""

    pass


# Inventory Adjustment Events
class InventoryAdjustmentCreated(DomainEvent):
    """Inventory adjustment created event."""

    pass


class InventoryAdjustmentConfirmed(DomainEvent):
    """Inventory adjustment confirmed event."""

    pass


class InventoryAdjustmentCancelled(DomainEvent):
    """Inventory adjustment cancelled event."""

    pass


# Reordering Rule Events
class ReorderingRuleCreated(DomainEvent):
    """Reordering rule created event."""

    pass


class ReorderingRuleTriggered(DomainEvent):
    """Reordering rule triggered event."""

    pass


# Lot/Serial Events
class LotSerialCreated(DomainEvent):
    """Lot/Serial created event."""

    pass
