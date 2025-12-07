"""
Repository interfaces for Sales module.
"""

from abc import abstractmethod
from typing import Protocol

from serp_sales.domain.entities import Quote, SalesOrder


class IQuoteRepository(Protocol):
    """Quote repository interface."""

    @abstractmethod
    def save(self, quote: Quote) -> None:
        """Save a quote."""
        ...

    @abstractmethod
    def get_by_id(self, quote_id: str) -> Quote | None:
        """Get a quote by ID."""
        ...

    @abstractmethod
    def get_by_quote_number(self, quote_number: str) -> Quote | None:
        """Get a quote by quote number."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Quote]:
        """List all quotes."""
        ...

    @abstractmethod
    def get_by_partner(self, partner_id: str) -> list[Quote]:
        """Get all quotes for a partner."""
        ...

    @abstractmethod
    def delete(self, quote_id: str) -> None:
        """Delete a quote."""
        ...

    @abstractmethod
    def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for quote numbering."""
        ...


class ISalesOrderRepository(Protocol):
    """Sales order repository interface."""

    @abstractmethod
    def save(self, order: SalesOrder) -> None:
        """Save a sales order."""
        ...

    @abstractmethod
    def get_by_id(self, order_id: str) -> SalesOrder | None:
        """Get an order by ID."""
        ...

    @abstractmethod
    def get_by_order_number(self, order_number: str) -> SalesOrder | None:
        """Get an order by order number."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[SalesOrder]:
        """List all orders."""
        ...

    @abstractmethod
    def get_by_partner(self, partner_id: str) -> list[SalesOrder]:
        """Get all orders for a partner."""
        ...

    @abstractmethod
    def get_by_quote(self, quote_id: str) -> SalesOrder | None:
        """Get order created from a quote."""
        ...

    @abstractmethod
    def delete(self, order_id: str) -> None:
        """Delete an order."""
        ...

    @abstractmethod
    def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for order numbering."""
        ...
