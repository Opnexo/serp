"""
In-memory repository implementations for Invoicing domain.

These are simple in-memory implementations for development/testing.
Production implementations would use SQL databases.
"""

from datetime import date

from serp_invoicing.domain.entities import Invoice, Payment
from serp_invoicing.domain.repositories import IInvoiceRepository, IPaymentRepository


class InMemoryInvoiceRepository(IInvoiceRepository):
    """In-memory implementation of Invoice repository."""

    def __init__(self) -> None:
        self._invoices: dict[str, Invoice] = {}
        self._sequence_counters: dict[int, int] = {}  # year -> sequence

    async def get_by_id(self, invoice_id: str) -> Invoice | None:
        """Get invoice by ID."""
        return self._invoices.get(invoice_id)

    async def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        """Get invoice by invoice number."""
        for invoice in self._invoices.values():
            if str(invoice.invoice_number) == invoice_number:
                return invoice
        return None

    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Invoice]:
        """Get invoices for a specific partner."""
        invoices = [
            inv for inv in self._invoices.values() if inv.partner_id == partner_id
        ]
        invoices.sort(key=lambda x: x.invoice_date, reverse=True)
        return invoices[skip : skip + limit]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        partner_id: str | None = None,
    ) -> list[Invoice]:
        """List invoices with optional filters."""
        invoices = list(self._invoices.values())

        if status is not None:
            invoices = [inv for inv in invoices if inv.status.value == status]
        if partner_id is not None:
            invoices = [inv for inv in invoices if inv.partner_id == partner_id]

        invoices.sort(key=lambda x: x.invoice_date, reverse=True)
        return invoices[skip : skip + limit]

    async def get_overdue_invoices(self) -> list[Invoice]:
        """Get all overdue invoices."""
        today = date.today()
        return [
            inv
            for inv in self._invoices.values()
            if inv.due_date < today and inv.status.value in ("SENT", "OVERDUE")
        ]

    async def save(self, invoice: Invoice) -> Invoice:
        """Save (create or update) invoice."""
        self._invoices[invoice.id] = invoice
        return invoice

    async def delete(self, invoice_id: str) -> bool:
        """Delete invoice."""
        if invoice_id in self._invoices:
            del self._invoices[invoice_id]
            return True
        return False

    async def count(
        self, status: str | None = None, partner_id: str | None = None
    ) -> int:
        """Count invoices with optional filters."""
        invoices = list(self._invoices.values())

        if status is not None:
            invoices = [inv for inv in invoices if inv.status.value == status]
        if partner_id is not None:
            invoices = [inv for inv in invoices if inv.partner_id == partner_id]

        return len(invoices)

    async def get_next_sequence_number(self, year: int) -> int:
        """Get next sequence number for invoice numbering."""
        if year not in self._sequence_counters:
            self._sequence_counters[year] = 0
        self._sequence_counters[year] += 1
        return self._sequence_counters[year]


class InMemoryPaymentRepository(IPaymentRepository):
    """In-memory implementation of Payment repository."""

    def __init__(self) -> None:
        self._payments: dict[str, Payment] = {}

    async def get_by_id(self, payment_id: str) -> Payment | None:
        """Get payment by ID."""
        return self._payments.get(payment_id)

    async def get_by_invoice_id(self, invoice_id: str) -> list[Payment]:
        """Get all payments for a specific invoice."""
        payments = [p for p in self._payments.values() if p.invoice_id == invoice_id]
        payments.sort(key=lambda x: x.payment_date, reverse=True)
        return payments

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Payment]:
        """List payments with optional filters."""
        payments = list(self._payments.values())

        if from_date is not None:
            payments = [p for p in payments if p.payment_date >= from_date]
        if to_date is not None:
            payments = [p for p in payments if p.payment_date <= to_date]

        payments.sort(key=lambda x: x.payment_date, reverse=True)
        return payments[skip : skip + limit]

    async def save(self, payment: Payment) -> Payment:
        """Save (create or update) payment."""
        self._payments[payment.id] = payment
        return payment

    async def delete(self, payment_id: str) -> bool:
        """Delete payment."""
        if payment_id in self._payments:
            del self._payments[payment_id]
            return True
        return False

    async def count(self, invoice_id: str | None = None) -> int:
        """Count payments, optionally for a specific invoice."""
        if invoice_id:
            return len(
                [p for p in self._payments.values() if p.invoice_id == invoice_id]
            )
        return len(self._payments)

    async def get_total_paid_amount(self, invoice_id: str) -> tuple[str, str]:
        """
        Get total amount paid for an invoice.

        Returns: (amount, currency)
        """
        payments = await self.get_by_invoice_id(invoice_id)
        if not payments:
            return ("0", "USD")

        total = sum(p.amount.amount for p in payments)
        currency = payments[0].amount.currency

        return (str(total), currency)
