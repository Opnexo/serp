"""
Tests for Invoice and Payment entities.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from serp_crm.domain.value_objects import Money

from serp_invoicing.domain.entities import Invoice, InvoiceItem, Payment
from serp_invoicing.domain.value_objects import (
    InvoiceNumber,
    InvoiceStatus,
    PaymentMethod,
    PaymentReference,
)


def test_invoice_number_generation():
    """Test invoice number generation."""
    number = InvoiceNumber.generate(2025, 1)
    assert str(number) == "INV-2025-0001"

    number = InvoiceNumber.generate(2025, 42, "BILL")
    assert str(number) == "BILL-2025-0042"


def test_create_invoice_item():
    """Test creating an invoice line item."""
    item = InvoiceItem(
        description="Software License",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("1000.00"), "USD"),
        tax_rate=Decimal("0.10"),
    )

    assert item.description == "Software License"
    assert item.line_subtotal.amount == Decimal("1000.00")
    assert item.tax_amount.amount == Decimal("100.00")
    assert item.line_total.amount == Decimal("1100.00")


def test_create_invoice():
    """Test creating an invoice."""
    item = InvoiceItem(
        description="Consulting",
        quantity=Decimal("10"),
        unit_price=Money(Decimal("150.00"), "USD"),
        tax_rate=Decimal("0.08"),
    )

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0001"),
        partner_id="partner-123",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[item],
    )

    assert invoice.invoice_number.value == "INV-2025-0001"
    assert invoice.status == InvoiceStatus.DRAFT
    assert invoice.subtotal.amount == Decimal("1500.00")  # 10 × 150
    assert invoice.tax_amount.amount == Decimal("120.00")  # 1500 × 0.08
    assert invoice.total_amount.amount == Decimal("1620.00")


def test_invoice_with_multiple_items():
    """Test invoice with multiple line items."""
    items = [
        InvoiceItem(
            description="Item 1",
            quantity=Decimal("2"),
            unit_price=Money(Decimal("100.00"), "USD"),
            tax_rate=Decimal("0.10"),
        ),
        InvoiceItem(
            description="Item 2",
            quantity=Decimal("3"),
            unit_price=Money(Decimal("50.00"), "USD"),
            tax_rate=Decimal("0.10"),
        ),
    ]

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0002"),
        partner_id="partner-456",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=items,
    )

    # Subtotal: (2 × 100) + (3 × 50) = 200 + 150 = 350
    assert invoice.subtotal.amount == Decimal("350.00")
    # Tax: 350 × 0.10 = 35
    assert invoice.tax_amount.amount == Decimal("35.00")
    # Total: 350 + 35 = 385
    assert invoice.total_amount.amount == Decimal("385.00")


def test_invoice_status_transitions():
    """Test invoice status transitions."""
    item = InvoiceItem(
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0003"),
        partner_id="partner-789",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[item],
    )

    # Initial status
    assert invoice.status == InvoiceStatus.DRAFT

    # Send invoice
    invoice.send()
    assert invoice.status == InvoiceStatus.SENT
    assert invoice.sent_at is not None

    # Mark as paid
    invoice.mark_as_paid()
    assert invoice.status == InvoiceStatus.PAID
    assert invoice.paid_at is not None


def test_cannot_modify_sent_invoice():
    """Test that sent invoices cannot be modified."""
    item = InvoiceItem(
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0004"),
        partner_id="partner-abc",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[item],
    )

    invoice.send()

    # Cannot add items to sent invoice
    new_item = InvoiceItem(
        description="Another service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("100.00"), "USD"),
    )

    with pytest.raises(ValueError, match="non-draft"):
        invoice.add_line_item(new_item)


def test_invoice_overdue_detection():
    """Test overdue invoice detection."""
    item = InvoiceItem(
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    # Create invoice with past due date
    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0005"),
        partner_id="partner-def",
        invoice_date=date.today() - timedelta(days=60),
        due_date=date.today() - timedelta(days=30),
        currency="USD",
        line_items=[item],
        status=InvoiceStatus.SENT,
    )

    assert invoice.is_overdue is True


def test_create_payment():
    """Test creating a payment."""
    payment = Payment(
        invoice_id="invoice-123",
        payment_date=date.today(),
        amount=Money(Decimal("1500.00"), "USD"),
        method=PaymentMethod.TRANSFER,
        reference=PaymentReference("TXN-12345"),
    )

    assert payment.invoice_id == "invoice-123"
    assert payment.amount.amount == Decimal("1500.00")
    assert payment.method == PaymentMethod.TRANSFER
    assert str(payment.reference) == "TXN-12345"


def test_payment_amount_validation():
    """Test payment amount validation."""
    with pytest.raises(ValueError, match="positive"):
        Payment(
            invoice_id="invoice-456",
            payment_date=date.today(),
            amount=Money(Decimal("0"), "USD"),
            method=PaymentMethod.CASH,
        )


def test_invoice_cancel():
    """Test cancelling an invoice."""
    item = InvoiceItem(
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0006"),
        partner_id="partner-ghi",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[item],
    )

    invoice.cancel()
    assert invoice.status == InvoiceStatus.CANCELLED
    assert invoice.cancelled_at is not None


def test_cannot_cancel_paid_invoice():
    """Test that paid invoices cannot be cancelled."""
    item = InvoiceItem(
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0007"),
        partner_id="partner-jkl",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[item],
    )

    invoice.send()
    invoice.mark_as_paid()

    with pytest.raises(ValueError, match="Cannot cancel paid"):
        invoice.cancel()
