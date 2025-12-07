"""
Domain services for Invoicing module.
"""

from datetime import date
from decimal import Decimal

from serp_crm.domain.value_objects import Money

from serp_invoicing.domain.entities import Invoice, Payment
from serp_invoicing.domain.repositories import IInvoiceRepository, IPaymentRepository
from serp_invoicing.domain.value_objects import InvoiceNumber


class InvoiceNumberGenerator:
    """
    Domain service for generating invoice numbers.

    Ensures unique, sequential invoice numbers.
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        self.invoice_repository = invoice_repository

    async def generate_invoice_number(
        self, year: int | None = None, prefix: str = "INV"
    ) -> InvoiceNumber:
        """
        Generate next invoice number.

        Format: PREFIX-YYYY-NNNN (e.g., INV-2025-0001)
        """
        if year is None:
            year = date.today().year

        sequence = await self.invoice_repository.get_next_sequence_number(year)
        return InvoiceNumber.generate(year, sequence, prefix)


class PaymentAllocationService:
    """
    Domain service for allocating payments to invoices.

    Handles payment tracking and invoice status updates.
    """

    def __init__(
        self,
        invoice_repository: IInvoiceRepository,
        payment_repository: IPaymentRepository,
    ):
        self.invoice_repository = invoice_repository
        self.payment_repository = payment_repository

    async def allocate_payment(self, invoice: Invoice, payment: Payment) -> Invoice:
        """
        Allocate a payment to an invoice and update status.

        Args:
            invoice: The invoice to apply payment to
            payment: The payment to allocate

        Returns:
            Updated invoice

        Raises:
            ValueError: If payment amount exceeds invoice balance or currency mismatch
        """
        # Validate currency match
        if payment.amount.currency != invoice.currency:
            raise ValueError(
                f"Payment currency {payment.amount.currency} does not match invoice currency {invoice.currency}"
            )

        # Get total paid amount so far
        amount_str, currency = await self.payment_repository.get_total_paid_amount(
            invoice.id
        )
        total_paid = Decimal(amount_str) if amount_str != "0" else Decimal("0")

        # Add new payment
        new_total_paid = total_paid + payment.amount.amount

        # Check if overpayment
        if new_total_paid > invoice.total_amount.amount:
            raise ValueError(
                f"Payment amount {payment.amount} would exceed invoice balance. "
                f"Invoice total: {invoice.total_amount}, Already paid: {Money(total_paid, currency)}"
            )

        # Mark invoice as paid if fully paid
        if new_total_paid >= invoice.total_amount.amount:
            invoice.mark_as_paid()

        # Save invoice
        invoice = await self.invoice_repository.save(invoice)

        return invoice

    async def get_invoice_balance(self, invoice: Invoice) -> Money:
        """
        Calculate remaining balance for an invoice.

        Args:
            invoice: The invoice to calculate balance for

        Returns:
            Remaining balance as Money
        """
        amount_str, currency = await self.payment_repository.get_total_paid_amount(
            invoice.id
        )
        total_paid = Decimal(amount_str) if amount_str != "0" else Decimal("0")

        balance = invoice.total_amount.amount - total_paid
        return Money(balance, invoice.currency)

    async def is_invoice_fully_paid(self, invoice: Invoice) -> bool:
        """
        Check if an invoice is fully paid.

        Args:
            invoice: The invoice to check

        Returns:
            True if fully paid, False otherwise
        """
        balance = await self.get_invoice_balance(invoice)
        return balance.amount <= Decimal("0")


class OverdueInvoiceService:
    """Domain service for managing overdue invoices."""

    def __init__(self, invoice_repository: IInvoiceRepository):
        self.invoice_repository = invoice_repository

    async def update_overdue_invoices(self) -> list[Invoice]:
        """
        Update status of overdue invoices.

        Returns:
            List of invoices that were marked as overdue
        """
        overdue_invoices = await self.invoice_repository.get_overdue_invoices()

        updated = []
        for invoice in overdue_invoices:
            if invoice.status.value == "SENT":  # Only update SENT invoices
                invoice.update_status_if_overdue()
                await self.invoice_repository.save(invoice)
                updated.append(invoice)

        return updated
