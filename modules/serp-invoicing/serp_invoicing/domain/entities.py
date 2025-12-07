"""
Domain entities for Invoicing module.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from serp_core.domain.entities import AggregateRoot, Entity
from serp_crm.domain.value_objects import Money

from serp_invoicing.domain.value_objects import (
    InvoiceNumber,
    InvoiceStatus,
    PaymentMethod,
    PaymentReference,
)


@dataclass
class InvoiceItem(Entity):
    """
    Invoice line item entity.

    Owned by Invoice aggregate. Cannot exist independently.
    """

    description: str
    quantity: Decimal
    unit_price: Money
    tax_rate: Decimal = Decimal("0")  # Tax rate as decimal (e.g., 0.10 = 10%)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.description:
            raise ValueError("Line item description is required")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.tax_rate < 0 or self.tax_rate > 1:
            raise ValueError("Tax rate must be between 0 and 1")

    @property
    def line_subtotal(self) -> Money:
        """Calculate line subtotal (quantity × unit_price)."""
        amount = self.quantity * self.unit_price.amount
        return Money(amount, self.unit_price.currency)

    @property
    def tax_amount(self) -> Money:
        """Calculate tax amount for this line."""
        tax = self.line_subtotal.amount * self.tax_rate
        return Money(tax, self.unit_price.currency)

    @property
    def line_total(self) -> Money:
        """Calculate line total (subtotal + tax)."""
        total = self.line_subtotal.amount + self.tax_amount.amount
        return Money(total, self.unit_price.currency)

    def update_quantity(self, quantity: Decimal) -> None:
        """Update quantity."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantity = quantity
        self.updated_at = datetime.now()

    def update_price(self, unit_price: Money) -> None:
        """Update unit price."""
        self.unit_price = unit_price
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "quantity": str(self.quantity),
            "unit_price": str(self.unit_price),
            "tax_rate": str(self.tax_rate),
            "line_subtotal": str(self.line_subtotal),
            "tax_amount": str(self.tax_amount),
            "line_total": str(self.line_total),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Invoice(AggregateRoot):
    """
    Invoice aggregate root.

    Represents a bill/invoice sent to a customer.
    Owns InvoiceItem entities.
    """

    invoice_number: InvoiceNumber
    partner_id: str  # References Partner (customer) from serp-crm
    invoice_date: date
    due_date: date
    status: InvoiceStatus = InvoiceStatus.DRAFT
    currency: str = "USD"

    # Line items (owned entities)
    line_items: list[InvoiceItem] = field(default_factory=list)

    # Metadata
    notes: str | None = None
    terms: str | None = None  # Payment terms
    reference: str | None = None  # Customer reference/PO number

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sent_at: datetime | None = None
    paid_at: datetime | None = None
    cancelled_at: datetime | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.due_date < self.invoice_date:
            raise ValueError("Due date cannot be before invoice date")
        if not self.line_items:
            raise ValueError("Invoice must have at least one line item")

    @property
    def subtotal(self) -> Money:
        """Calculate invoice subtotal (sum of line subtotals)."""
        if not self.line_items:
            return Money(Decimal("0"), self.currency)
        total = sum(item.line_subtotal.amount for item in self.line_items)
        return Money(total, self.currency)

    @property
    def tax_amount(self) -> Money:
        """Calculate total tax amount."""
        if not self.line_items:
            return Money(Decimal("0"), self.currency)
        total = sum(item.tax_amount.amount for item in self.line_items)
        return Money(total, self.currency)

    @property
    def total_amount(self) -> Money:
        """Calculate invoice total (subtotal + tax)."""
        total = self.subtotal.amount + self.tax_amount.amount
        return Money(total, self.currency)

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            return False
        return date.today() > self.due_date

    def add_line_item(self, item: InvoiceItem) -> None:
        """Add a line item to the invoice."""
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("Cannot modify non-draft invoice")
        if item.unit_price.currency != self.currency:
            raise ValueError(f"Line item currency must be {self.currency}")
        self.line_items.append(item)
        self.updated_at = datetime.now()

    def remove_line_item(self, item_id: str) -> None:
        """Remove a line item from the invoice."""
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("Cannot modify non-draft invoice")
        self.line_items = [item for item in self.line_items if item.id != item_id]
        if not self.line_items:
            raise ValueError("Invoice must have at least one line item")
        self.updated_at = datetime.now()

    def send(self) -> None:
        """Mark invoice as sent."""
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be sent")
        self.status = InvoiceStatus.SENT
        self.sent_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_paid(self) -> None:
        """Mark invoice as paid."""
        if self.status == InvoiceStatus.CANCELLED:
            raise ValueError("Cannot mark cancelled invoice as paid")
        if self.status == InvoiceStatus.PAID:
            raise ValueError("Invoice is already paid")
        self.status = InvoiceStatus.PAID
        self.paid_at = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the invoice."""
        if self.status == InvoiceStatus.PAID:
            raise ValueError("Cannot cancel paid invoice")
        if self.status == InvoiceStatus.CANCELLED:
            raise ValueError("Invoice is already cancelled")
        self.status = InvoiceStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()

    def update_status_if_overdue(self) -> None:
        """Update status to OVERDUE if applicable."""
        if self.is_overdue and self.status == InvoiceStatus.SENT:
            self.status = InvoiceStatus.OVERDUE
            self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "invoice_number": str(self.invoice_number),
            "partner_id": self.partner_id,
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "status": self.status.value,
            "currency": self.currency,
            "line_items": [item.to_dict() for item in self.line_items],
            "subtotal": str(self.subtotal),
            "tax_amount": str(self.tax_amount),
            "total_amount": str(self.total_amount),
            "is_overdue": self.is_overdue,
            "notes": self.notes,
            "terms": self.terms,
            "reference": self.reference,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "cancelled_at": self.cancelled_at.isoformat()
            if self.cancelled_at
            else None,
        }


@dataclass
class Payment(AggregateRoot):
    """
    Payment aggregate root.

    Represents a payment made against an invoice.
    Separate aggregate from Invoice to allow independent lifecycle.
    """

    invoice_id: str  # References Invoice
    payment_date: date
    amount: Money
    method: PaymentMethod = PaymentMethod.TRANSFER
    reference: PaymentReference | None = None
    notes: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.amount.amount <= 0:
            raise ValueError("Payment amount must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "payment_date": self.payment_date.isoformat(),
            "amount": str(self.amount),
            "method": self.method.value,
            "reference": str(self.reference) if self.reference else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
