"""
In-memory repository implementations for Sales module.
"""

from collections import defaultdict

from serp_sales.domain.entities import Quote, SalesOrder
from serp_sales.domain.repositories import IQuoteRepository, ISalesOrderRepository


class InMemoryQuoteRepository(IQuoteRepository):
    """In-memory implementation of quote repository."""

    def __init__(self):
        self._quotes: dict[str, Quote] = {}
        self._sequence_counters: dict[int, int] = defaultdict(int)

    def save(self, quote: Quote) -> None:
        """Save a quote."""
        self._quotes[quote.id] = quote

    def get_by_id(self, quote_id: str) -> Quote | None:
        """Get a quote by ID."""
        return self._quotes.get(quote_id)

    def get_by_quote_number(self, quote_number: str) -> Quote | None:
        """Get a quote by quote number."""
        for quote in self._quotes.values():
            if str(quote.quote_number) == quote_number:
                return quote
        return None

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Quote]:
        """List all quotes."""
        quotes = list(self._quotes.values())
        return quotes[skip : skip + limit]

    def get_by_partner(self, partner_id: str) -> list[Quote]:
        """Get all quotes for a partner."""
        return [q for q in self._quotes.values() if q.partner_id == partner_id]

    def delete(self, quote_id: str) -> None:
        """Delete a quote."""
        if quote_id in self._quotes:
            del self._quotes[quote_id]

    def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for quote numbering."""
        self._sequence_counters[year] += 1
        return self._sequence_counters[year]


class InMemorySalesOrderRepository(ISalesOrderRepository):
    """In-memory implementation of sales order repository."""

    def __init__(self):
        self._orders: dict[str, SalesOrder] = {}
        self._sequence_counters: dict[int, int] = defaultdict(int)

    def save(self, order: SalesOrder) -> None:
        """Save a sales order."""
        self._orders[order.id] = order

    def get_by_id(self, order_id: str) -> SalesOrder | None:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def get_by_order_number(self, order_number: str) -> SalesOrder | None:
        """Get an order by order number."""
        for order in self._orders.values():
            if str(order.order_number) == order_number:
                return order
        return None

    def list_all(self, skip: int = 0, limit: int = 100) -> list[SalesOrder]:
        """List all orders."""
        orders = list(self._orders.values())
        return orders[skip : skip + limit]

    def get_by_partner(self, partner_id: str) -> list[SalesOrder]:
        """Get all orders for a partner."""
        return [o for o in self._orders.values() if o.partner_id == partner_id]

    def get_by_quote(self, quote_id: str) -> SalesOrder | None:
        """Get order created from a quote."""
        for order in self._orders.values():
            if order.quote_id == quote_id:
                return order
        return None

    def delete(self, order_id: str) -> None:
        """Delete an order."""
        if order_id in self._orders:
            del self._orders[order_id]

    def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for order numbering."""
        self._sequence_counters[year] += 1
        return self._sequence_counters[year]
