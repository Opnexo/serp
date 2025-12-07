"""Domain layer exports."""

from serp_sales.domain.entities import OrderLine, Quote, QuoteLine, SalesOrder
from serp_sales.domain.events import (
    QuoteAccepted,
    QuoteCreated,
    QuoteExpired,
    QuoteRejected,
    QuoteSent,
    QuoteUpdated,
    SalesOrderCancelled,
    SalesOrderConfirmed,
    SalesOrderCreated,
    SalesOrderDelivered,
    SalesOrderProcessing,
    SalesOrderShipped,
    SalesOrderUpdated,
)
from serp_sales.domain.repositories import IQuoteRepository, ISalesOrderRepository
from serp_sales.domain.services import (
    ExpiredQuoteService,
    OrderNumberGenerator,
    QuoteNumberGenerator,
    QuoteToOrderConverter,
)
from serp_sales.domain.value_objects import (
    Discount,
    OrderNumber,
    OrderStatus,
    QuoteNumber,
    QuoteStatus,
    ShippingInfo,
    TaxRate,
)

__all__ = [
    # Entities
    "Quote",
    "QuoteLine",
    "SalesOrder",
    "OrderLine",
    # Value Objects
    "QuoteNumber",
    "OrderNumber",
    "QuoteStatus",
    "OrderStatus",
    "Discount",
    "TaxRate",
    "ShippingInfo",
    # Repositories
    "IQuoteRepository",
    "ISalesOrderRepository",
    # Services
    "QuoteNumberGenerator",
    "OrderNumberGenerator",
    "QuoteToOrderConverter",
    "ExpiredQuoteService",
    # Events
    "QuoteCreated",
    "QuoteUpdated",
    "QuoteSent",
    "QuoteAccepted",
    "QuoteRejected",
    "QuoteExpired",
    "SalesOrderCreated",
    "SalesOrderUpdated",
    "SalesOrderConfirmed",
    "SalesOrderProcessing",
    "SalesOrderShipped",
    "SalesOrderDelivered",
    "SalesOrderCancelled",
]
