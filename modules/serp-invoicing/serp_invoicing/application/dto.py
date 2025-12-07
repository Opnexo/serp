"""
Data Transfer Objects (DTOs) for Invoicing module.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

# Invoice DTOs


class InvoiceItemDTO(BaseModel):
    """DTO for invoice line item."""

    id: str | None = None
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    tax_rate: Decimal = Field(Decimal("0"), ge=0, le=1)


class InvoiceItemResponseDTO(BaseModel):
    """DTO for invoice line item response."""

    id: str
    description: str
    quantity: str
    unit_price: str
    tax_rate: str
    line_subtotal: str
    tax_amount: str
    line_total: str
    created_at: str
    updated_at: str


class InvoiceCreateDTO(BaseModel):
    """DTO for creating an invoice."""

    partner_id: str
    invoice_date: date
    due_date: date
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    line_items: list[InvoiceItemDTO] = Field(min_length=1)
    notes: str | None = None
    terms: str | None = None
    reference: str | None = None


class InvoiceUpdateDTO(BaseModel):
    """DTO for updating an invoice."""

    due_date: date | None = None
    notes: str | None = None
    terms: str | None = None
    reference: str | None = None
    line_items: list[InvoiceItemDTO] | None = None


class InvoiceDTO(BaseModel):
    """DTO for invoice representation."""

    id: str
    invoice_number: str
    partner_id: str
    invoice_date: date
    due_date: date
    status: str
    currency: str
    line_items: list[InvoiceItemResponseDTO]
    subtotal: str
    tax_amount: str
    total_amount: str
    is_overdue: bool
    notes: str | None
    terms: str | None
    reference: str | None
    created_at: str
    updated_at: str
    sent_at: str | None
    paid_at: str | None
    cancelled_at: str | None


class InvoiceListDTO(BaseModel):
    """DTO for listing invoices."""

    invoices: list[InvoiceDTO]
    total: int
    skip: int
    limit: int


class InvoiceSummaryDTO(BaseModel):
    """DTO for invoice summary statistics."""

    total_invoices: int
    draft_count: int
    sent_count: int
    paid_count: int
    overdue_count: int
    cancelled_count: int
    total_outstanding: str
    currency: str


# Payment DTOs


class PaymentCreateDTO(BaseModel):
    """DTO for creating a payment."""

    invoice_id: str
    payment_date: date
    amount: Decimal = Field(gt=0)
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    method: str = Field(pattern="^(CASH|CARD|TRANSFER|CHECK|OTHER)$")
    reference: str | None = None
    notes: str | None = None


class PaymentDTO(BaseModel):
    """DTO for payment representation."""

    id: str
    invoice_id: str
    payment_date: date
    amount: str
    method: str
    reference: str | None
    notes: str | None
    created_at: str


class PaymentListDTO(BaseModel):
    """DTO for listing payments."""

    payments: list[PaymentDTO]
    total: int
    skip: int
    limit: int


class InvoiceBalanceDTO(BaseModel):
    """DTO for invoice balance information."""

    invoice_id: str
    invoice_number: str
    total_amount: str
    paid_amount: str
    balance: str
    currency: str
    is_fully_paid: bool
