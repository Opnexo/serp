"""Domain events for Procurement."""

from serp_core.domain.events import DomainEvent


# RFQ Events
class RFQCreated(DomainEvent):
    """RFQ created event."""

    pass


class RFQSent(DomainEvent):
    """RFQ sent to suppliers event."""

    pass


class RFQQuoted(DomainEvent):
    """RFQ quotes received event."""

    pass


class RFQAccepted(DomainEvent):
    """RFQ accepted event."""

    pass


class RFQCancelled(DomainEvent):
    """RFQ cancelled event."""

    pass


# Purchase Order Events
class PurchaseOrderCreated(DomainEvent):
    """Purchase order created event."""

    pass


class PurchaseOrderConfirmed(DomainEvent):
    """Purchase order confirmed event."""

    pass


class PurchaseOrderCancelled(DomainEvent):
    """Purchase order cancelled event."""

    pass


class PurchaseOrderReceived(DomainEvent):
    """Purchase order fully received event."""

    pass


class PurchaseOrderLineReceived(DomainEvent):
    """Purchase order line received event."""

    pass


# Goods Receipt Events
class GoodsReceiptNoteCreated(DomainEvent):
    """Goods receipt note created event."""

    pass


class GoodsReceiptQualityPassed(DomainEvent):
    """Goods passed quality check event."""

    pass


class GoodsReceiptQualityFailed(DomainEvent):
    """Goods failed quality check event."""

    pass


# Purchase Agreement Events
class PurchaseAgreementCreated(DomainEvent):
    """Purchase agreement created event."""

    pass


class PurchaseAgreementUpdated(DomainEvent):
    """Purchase agreement updated event."""

    pass


class PurchaseAgreementActivated(DomainEvent):
    """Purchase agreement activated event."""

    pass


class PurchaseAgreementDeactivated(DomainEvent):
    """Purchase agreement deactivated event."""

    pass
