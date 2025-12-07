"""
Repository interfaces for Invoicing domain.
"""

from abc import ABC, abstractmethod
from datetime import date

from serp_invoicing.domain.entities import Invoice, Payment


class IInvoiceRepository(ABC):
    """Repository interface for Invoice aggregate."""

    @abstractmethod
    async def get_by_id(self, invoice_id: str) -> Invoice | None:
        """Get invoice by ID."""
        pass

    @abstractmethod
    async def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        """Get invoice by invoice number."""
        pass

    @abstractmethod
    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Invoice]:
        """Get invoices for a specific partner."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        partner_id: str | None = None,
    ) -> list[Invoice]:
        """List invoices with optional filters."""
        pass

    @abstractmethod
    async def get_overdue_invoices(self) -> list[Invoice]:
        """Get all overdue invoices."""
        pass

    @abstractmethod
    async def save(self, invoice: Invoice) -> Invoice:
        """Save (create or update) invoice."""
        pass

    @abstractmethod
    async def delete(self, invoice_id: str) -> bool:
        """Delete invoice."""
        pass

    @abstractmethod
    async def count(
        self, status: str | None = None, partner_id: str | None = None
    ) -> int:
        """Count invoices with optional filters."""
        pass

    @abstractmethod
    async def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for invoice numbering."""
        pass


class IPaymentRepository(ABC):
    """Repository interface for Payment aggregate."""

    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Payment | None:
        """Get payment by ID."""
        pass

    @abstractmethod
    async def get_by_invoice_id(self, invoice_id: str) -> list[Payment]:
        """Get all payments for a specific invoice."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Payment]:
        """List payments with optional filters."""
        pass

    @abstractmethod
    async def save(self, payment: Payment) -> Payment:
        """Save (create or update) payment."""
        pass

    @abstractmethod
    async def delete(self, payment_id: str) -> bool:
        """Delete payment."""
        pass

    @abstractmethod
    async def count(self, invoice_id: str | None = None) -> int:
        """Count payments, optionally for a specific invoice."""
        pass

    @abstractmethod
    async def get_total_paid_amount(self, invoice_id: str) -> tuple[str, str]:
        """
        Get total amount paid for an invoice.

        Returns: (amount, currency)
        """
        pass
