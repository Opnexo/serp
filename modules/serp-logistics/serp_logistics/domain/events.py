"""Domain events for logistics."""

from serp_core.domain import DomainEvent


# Picking Operation Events
class PickingOperationCreated(DomainEvent):
    """Picking operation created event."""

    pass


class PickingOperationAssigned(DomainEvent):
    """Picking operation assigned event."""

    pass


class PickingOperationStarted(DomainEvent):
    """Picking operation started event."""

    pass


class PickingOperationCompleted(DomainEvent):
    """Picking operation completed event."""

    pass


class PickingOperationCancelled(DomainEvent):
    """Picking operation cancelled event."""

    pass


# Packing Operation Events
class PackingOperationCreated(DomainEvent):
    """Packing operation created event."""

    pass


class PackingOperationStarted(DomainEvent):
    """Packing operation started event."""

    pass


class PackingOperationCompleted(DomainEvent):
    """Packing operation completed event."""

    pass


class PackingOperationShipped(DomainEvent):
    """Packing operation shipped event."""

    pass


# Shipment Events
class ShipmentCreated(DomainEvent):
    """Shipment created event."""

    pass


class ShipmentConfirmed(DomainEvent):
    """Shipment confirmed event."""

    pass


class ShipmentPickedUp(DomainEvent):
    """Shipment picked up event."""

    pass


class ShipmentStatusUpdated(DomainEvent):
    """Shipment status updated event."""

    pass


class ShipmentCancelled(DomainEvent):
    """Shipment cancelled event."""

    pass


# Carrier Events
class CarrierCreated(DomainEvent):
    """Carrier created event."""

    pass


# Delivery Route Events
class DeliveryRouteCreated(DomainEvent):
    """Delivery route created event."""

    pass


class DeliveryRouteStarted(DomainEvent):
    """Delivery route started event."""

    pass


class RouteStopCompleted(DomainEvent):
    """Route stop completed event."""

    pass


class DeliveryRouteCompleted(DomainEvent):
    """Delivery route completed event."""

    pass


# RMA Events
class RMACreated(DomainEvent):
    """RMA created event."""

    pass


class RMAApproved(DomainEvent):
    """RMA approved event."""

    pass


class RMARejected(DomainEvent):
    """RMA rejected event."""

    pass


class RMAShipped(DomainEvent):
    """RMA shipped event."""

    pass


class RMAReceived(DomainEvent):
    """RMA received event."""

    pass


class RMAProcessed(DomainEvent):
    """RMA processed event."""

    pass
