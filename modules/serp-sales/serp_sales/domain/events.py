"""
Domain events for Sales module.
"""

from serp_core.domain.events import DomainEvent


class QuoteCreated(DomainEvent):
    """Quote created event."""

    quote_id: str


class QuoteUpdated(DomainEvent):
    """Quote updated event."""

    quote_id: str


class QuoteSent(DomainEvent):
    """Quote sent event."""

    quote_id: str


class QuoteAccepted(DomainEvent):
    """Quote accepted event."""

    quote_id: str


class QuoteRejected(DomainEvent):
    """Quote rejected event."""

    quote_id: str
    reason: str


class QuoteExpired(DomainEvent):
    """Quote expired event."""

    quote_id: str


class SalesOrderCreated(DomainEvent):
    """Sales order created event."""

    order_id: str
    quote_id: str | None = None


class SalesOrderUpdated(DomainEvent):
    """Sales order updated event."""

    order_id: str


class SalesOrderConfirmed(DomainEvent):
    """Sales order confirmed event."""

    order_id: str


class SalesOrderProcessing(DomainEvent):
    """Sales order processing event."""

    order_id: str


class SalesOrderShipped(DomainEvent):
    """Sales order shipped event."""

    order_id: str


class SalesOrderDelivered(DomainEvent):
    """Sales order delivered event."""

    order_id: str


class SalesOrderCancelled(DomainEvent):
    """Sales order cancelled event."""

    order_id: str
    reason: str
