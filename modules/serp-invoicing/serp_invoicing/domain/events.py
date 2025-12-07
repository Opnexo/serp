"""
Domain events for Invoicing module.
"""

from dataclasses import dataclass
from datetime import date, datetime

from serp_core.domain.events import DomainEvent

# Invoice Events


@dataclass
class InvoiceCreated(DomainEvent):
    """Event raised when an invoice is created."""

    invoice_id: str
    invoice_number: str
    partner_id: str
    total_amount: str
    currency: str
    occurred_at: datetime


@dataclass
class InvoiceUpdated(DomainEvent):
    """Event raised when an invoice is updated."""

    invoice_id: str
    invoice_number: str
    occurred_at: datetime


@dataclass
class InvoiceSent(DomainEvent):
    """Event raised when an invoice is sent to customer."""

    invoice_id: str
    invoice_number: str
    partner_id: str
    total_amount: str
    due_date: date
    occurred_at: datetime


@dataclass
class InvoicePaid(DomainEvent):
    """Event raised when an invoice is fully paid."""

    invoice_id: str
    invoice_number: str
    partner_id: str
    total_amount: str
    occurred_at: datetime


@dataclass
class InvoiceCancelled(DomainEvent):
    """Event raised when an invoice is cancelled."""

    invoice_id: str
    invoice_number: str
    occurred_at: datetime


@dataclass
class InvoiceOverdue(DomainEvent):
    """Event raised when an invoice becomes overdue."""

    invoice_id: str
    invoice_number: str
    partner_id: str
    total_amount: str
    due_date: date
    occurred_at: datetime


# Payment Events


@dataclass
class PaymentCreated(DomainEvent):
    """Event raised when a payment is recorded."""

    payment_id: str
    invoice_id: str
    amount: str
    currency: str
    method: str
    payment_date: date
    occurred_at: datetime


@dataclass
class PaymentDeleted(DomainEvent):
    """Event raised when a payment is deleted."""

    payment_id: str
    invoice_id: str
    amount: str
    occurred_at: datetime
