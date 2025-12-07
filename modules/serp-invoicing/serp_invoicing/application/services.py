"""
Application services for Invoicing module.

Application services orchestrate domain logic, manage transactions,
and handle DTO conversions.
"""

from datetime import datetime
from decimal import Decimal

from serp_crm.domain.value_objects import Money

from serp_invoicing.application.dto import (
    InvoiceBalanceDTO,
    InvoiceCreateDTO,
    InvoiceDTO,
    InvoiceItemResponseDTO,
    InvoiceListDTO,
    InvoiceSummaryDTO,
    InvoiceUpdateDTO,
    PaymentCreateDTO,
    PaymentDTO,
    PaymentListDTO,
)
from serp_invoicing.domain.entities import Invoice, InvoiceItem, Payment
from serp_invoicing.domain.repositories import IInvoiceRepository, IPaymentRepository
from serp_invoicing.domain.services import (
    InvoiceNumberGenerator,
    OverdueInvoiceService,
    PaymentAllocationService,
)
from serp_invoicing.domain.value_objects import (
    InvoiceStatus,
    PaymentMethod,
    PaymentReference,
)


class InvoiceService:
    """Application service for Invoice management."""

    def __init__(self, invoice_repository: IInvoiceRepository, partner_repository=None):
        self.invoice_repository = invoice_repository
        self.partner_repository = partner_repository
        self.number_generator = InvoiceNumberGenerator(invoice_repository)

    async def create_invoice(self, dto: InvoiceCreateDTO) -> InvoiceDTO:
        """Create a new invoice."""
        # Generate invoice number
        invoice_number = await self.number_generator.generate_invoice_number()

        # Create line items
        line_items = []
        for item_dto in dto.line_items:
            item = InvoiceItem(
                description=item_dto.description,
                quantity=item_dto.quantity,
                unit_price=Money(item_dto.unit_price, dto.currency),
                tax_rate=item_dto.tax_rate,
            )
            line_items.append(item)

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            partner_id=dto.partner_id,
            invoice_date=dto.invoice_date,
            due_date=dto.due_date,
            currency=dto.currency,
            line_items=line_items,
            notes=dto.notes,
            terms=dto.terms,
            reference=dto.reference,
        )

        # Save
        invoice = await self.invoice_repository.save(invoice)

        return self._to_dto(invoice)

    async def get_invoice(self, invoice_id: str) -> InvoiceDTO | None:
        """Get invoice by ID."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        return self._to_dto(invoice) if invoice else None

    async def get_invoice_by_number(self, invoice_number: str) -> InvoiceDTO | None:
        """Get invoice by invoice number."""
        invoice = await self.invoice_repository.get_by_invoice_number(invoice_number)
        return self._to_dto(invoice) if invoice else None

    async def list_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        partner_id: str | None = None,
    ) -> InvoiceListDTO:
        """List invoices with filters."""
        invoices = await self.invoice_repository.list_all(
            skip=skip, limit=limit, status=status, partner_id=partner_id
        )
        total = await self.invoice_repository.count(
            status=status, partner_id=partner_id
        )

        return InvoiceListDTO(
            invoices=[self._to_dto(inv) for inv in invoices],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_partner_invoices(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> InvoiceListDTO:
        """Get all invoices for a partner."""
        invoices = await self.invoice_repository.get_by_partner_id(
            partner_id, skip=skip, limit=limit
        )
        total = await self.invoice_repository.count(partner_id=partner_id)

        return InvoiceListDTO(
            invoices=[self._to_dto(inv) for inv in invoices],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_invoice(
        self, invoice_id: str, dto: InvoiceUpdateDTO
    ) -> InvoiceDTO | None:
        """Update an existing invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return None

        # Can only update draft invoices
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be updated")

        # Update fields
        if dto.due_date is not None:
            invoice.due_date = dto.due_date
        if dto.notes is not None:
            invoice.notes = dto.notes
        if dto.terms is not None:
            invoice.terms = dto.terms
        if dto.reference is not None:
            invoice.reference = dto.reference

        # Update line items if provided
        if dto.line_items is not None:
            new_items = []
            for item_dto in dto.line_items:
                item = InvoiceItem(
                    description=item_dto.description,
                    quantity=item_dto.quantity,
                    unit_price=Money(item_dto.unit_price, invoice.currency),
                    tax_rate=item_dto.tax_rate,
                )
                new_items.append(item)
            invoice.line_items = new_items

        invoice.updated_at = datetime.now()

        # Save
        invoice = await self.invoice_repository.save(invoice)

        return self._to_dto(invoice)

    async def send_invoice(self, invoice_id: str) -> InvoiceDTO | None:
        """Mark invoice as sent."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return None

        invoice.send()
        invoice = await self.invoice_repository.save(invoice)

        return self._to_dto(invoice)

    async def cancel_invoice(self, invoice_id: str) -> InvoiceDTO | None:
        """Cancel an invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return None

        invoice.cancel()
        invoice = await self.invoice_repository.save(invoice)

        return self._to_dto(invoice)

    async def delete_invoice(self, invoice_id: str) -> bool:
        """Delete an invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return False

        # Only allow deleting draft invoices
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be deleted")

        return await self.invoice_repository.delete(invoice_id)

    async def get_invoice_summary(self, currency: str = "USD") -> InvoiceSummaryDTO:
        """Get invoice summary statistics."""
        all_invoices = await self.invoice_repository.list_all(skip=0, limit=10000)

        draft_count = sum(
            1 for inv in all_invoices if inv.status == InvoiceStatus.DRAFT
        )
        sent_count = sum(1 for inv in all_invoices if inv.status == InvoiceStatus.SENT)
        paid_count = sum(1 for inv in all_invoices if inv.status == InvoiceStatus.PAID)
        overdue_count = sum(
            1 for inv in all_invoices if inv.status == InvoiceStatus.OVERDUE
        )
        cancelled_count = sum(
            1 for inv in all_invoices if inv.status == InvoiceStatus.CANCELLED
        )

        # Calculate outstanding (sent + overdue)
        outstanding = sum(
            inv.total_amount.amount
            for inv in all_invoices
            if inv.status in (InvoiceStatus.SENT, InvoiceStatus.OVERDUE)
            and inv.currency == currency
        )

        return InvoiceSummaryDTO(
            total_invoices=len(all_invoices),
            draft_count=draft_count,
            sent_count=sent_count,
            paid_count=paid_count,
            overdue_count=overdue_count,
            cancelled_count=cancelled_count,
            total_outstanding=str(outstanding),
            currency=currency,
        )

    async def update_overdue_invoices(self) -> list[InvoiceDTO]:
        """Update overdue invoice statuses."""
        service = OverdueInvoiceService(self.invoice_repository)
        updated = await service.update_overdue_invoices()
        return [self._to_dto(inv) for inv in updated]

    def _to_dto(self, invoice: Invoice) -> InvoiceDTO:
        """Convert entity to DTO."""
        data = invoice.to_dict()
        data["line_items"] = [
            InvoiceItemResponseDTO(**item) for item in data["line_items"]
        ]
        return InvoiceDTO(**data)


class PaymentService:
    """Application service for Payment management."""

    def __init__(
        self,
        payment_repository: IPaymentRepository,
        invoice_repository: IInvoiceRepository,
    ):
        self.payment_repository = payment_repository
        self.invoice_repository = invoice_repository
        self.allocation_service = PaymentAllocationService(
            invoice_repository, payment_repository
        )

    async def create_payment(self, dto: PaymentCreateDTO) -> PaymentDTO:
        """Create a new payment and allocate to invoice."""
        # Verify invoice exists
        invoice = await self.invoice_repository.get_by_id(dto.invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {dto.invoice_id} not found")

        # Verify invoice is not cancelled or draft
        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValueError("Cannot create payment for cancelled invoice")
        if invoice.status == InvoiceStatus.DRAFT:
            raise ValueError("Cannot create payment for draft invoice")

        # Create payment
        reference = PaymentReference(dto.reference) if dto.reference else None
        payment = Payment(
            invoice_id=dto.invoice_id,
            payment_date=dto.payment_date,
            amount=Money(dto.amount, dto.currency),
            method=PaymentMethod(dto.method),
            reference=reference,
            notes=dto.notes,
        )

        # Save payment first
        payment = await self.payment_repository.save(payment)

        # Allocate payment to invoice (updates invoice status if needed)
        try:
            await self.allocation_service.allocate_payment(invoice, payment)
        except ValueError as e:
            # Rollback payment if allocation fails
            await self.payment_repository.delete(payment.id)
            raise e

        return self._to_dto(payment)

    async def get_payment(self, payment_id: str) -> PaymentDTO | None:
        """Get payment by ID."""
        payment = await self.payment_repository.get_by_id(payment_id)
        return self._to_dto(payment) if payment else None

    async def get_invoice_payments(self, invoice_id: str) -> PaymentListDTO:
        """Get all payments for an invoice."""
        payments = await self.payment_repository.get_by_invoice_id(invoice_id)
        total = await self.payment_repository.count(invoice_id=invoice_id)

        return PaymentListDTO(
            payments=[self._to_dto(p) for p in payments],
            total=total,
            skip=0,
            limit=len(payments),
        )

    async def list_payments(self, skip: int = 0, limit: int = 100) -> PaymentListDTO:
        """List all payments."""
        payments = await self.payment_repository.list_all(skip=skip, limit=limit)
        total = await self.payment_repository.count()

        return PaymentListDTO(
            payments=[self._to_dto(p) for p in payments],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def delete_payment(self, payment_id: str) -> bool:
        """Delete a payment."""
        payment = await self.payment_repository.get_by_id(payment_id)
        if not payment:
            return False

        # Get invoice and revert status if needed
        invoice = await self.invoice_repository.get_by_id(payment.invoice_id)
        if invoice and invoice.status == InvoiceStatus.PAID:
            # Check if still fully paid after deleting this payment
            amount_str, _ = await self.payment_repository.get_total_paid_amount(
                invoice.id
            )
            total_paid = Decimal(amount_str) if amount_str != "0" else Decimal("0")
            remaining_paid = total_paid - payment.amount.amount

            if remaining_paid < invoice.total_amount.amount:
                # No longer fully paid, revert to SENT
                invoice.status = InvoiceStatus.SENT
                invoice.paid_at = None
                invoice.updated_at = datetime.now()
                await self.invoice_repository.save(invoice)

        return await self.payment_repository.delete(payment_id)

    async def get_invoice_balance(self, invoice_id: str) -> InvoiceBalanceDTO | None:
        """Get balance information for an invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            return None

        balance = await self.allocation_service.get_invoice_balance(invoice)
        is_fully_paid = await self.allocation_service.is_invoice_fully_paid(invoice)

        amount_str, currency = await self.payment_repository.get_total_paid_amount(
            invoice_id
        )

        return InvoiceBalanceDTO(
            invoice_id=invoice.id,
            invoice_number=str(invoice.invoice_number),
            total_amount=str(invoice.total_amount),
            paid_amount=amount_str,
            balance=str(balance),
            currency=invoice.currency,
            is_fully_paid=is_fully_paid,
        )

    def _to_dto(self, payment: Payment) -> PaymentDTO:
        """Convert entity to DTO."""
        return PaymentDTO(**payment.to_dict())
