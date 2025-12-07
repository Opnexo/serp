"""
Tests for Invoice and Payment domain services.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from serp_crm.domain.value_objects import Money

from serp_invoicing.domain.entities import Invoice, InvoiceItem, Payment
from serp_invoicing.domain.repositories import IInvoiceRepository, IPaymentRepository
from serp_invoicing.domain.services import (
    InvoiceNumberGenerator,
    OverdueInvoiceService,
    PaymentAllocationService,
)
from serp_invoicing.domain.value_objects import (
    InvoiceNumber,
    InvoiceStatus,
    PaymentMethod,
)
from serp_invoicing.infrastructure.repositories import (
    InMemoryInvoiceRepository,
    InMemoryPaymentRepository,
)


@pytest.fixture
def invoice_repo() -> IInvoiceRepository:
    """Create an invoice repository for testing."""
    return InMemoryInvoiceRepository()


@pytest.fixture
def payment_repo() -> IPaymentRepository:
    """Create a payment repository for testing."""
    return InMemoryPaymentRepository()


def test_invoice_number_generator(invoice_repo: IInvoiceRepository):
    """Test invoice number generation service."""
    generator = InvoiceNumberGenerator(invoice_repo)

    # Generate first invoice number for 2025
    number1 = generator.generate_invoice_number(year=2025)
    assert str(number1) == "INV-2025-0001"

    # Simulate saving invoice with that number
    invoice = Invoice(
        invoice_number=number1,
        partner_id="partner-123",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("500.00"), "USD"),
            )
        ],
    )
    invoice_repo.save(invoice)

    # Generate next invoice number
    number2 = generator.generate_invoice_number(year=2025)
    assert str(number2) == "INV-2025-0002"

    # Generate for different year
    number3 = generator.generate_invoice_number(year=2026)
    assert str(number3) == "INV-2026-0001"


def test_payment_allocation_service(
    invoice_repo: IInvoiceRepository, payment_repo: IPaymentRepository
):
    """Test payment allocation service."""
    # Create and save an invoice
    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0001"),
        partner_id="partner-123",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("1000.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(invoice)

    # Create payment
    payment = Payment(
        invoice_id=invoice.id,
        payment_date=date.today(),
        amount=Money(Decimal("1000.00"), "USD"),
        method=PaymentMethod.TRANSFER,
    )

    # Allocate payment
    service = PaymentAllocationService(invoice_repo, payment_repo)
    service.allocate_payment_to_invoice(payment, invoice)

    # Verify invoice is marked as paid
    updated_invoice = invoice_repo.get_by_id(invoice.id)
    assert updated_invoice is not None
    assert updated_invoice.status == InvoiceStatus.PAID
    assert updated_invoice.paid_at is not None


def test_payment_allocation_partial_payment(
    invoice_repo: IInvoiceRepository, payment_repo: IPaymentRepository
):
    """Test partial payment allocation."""
    # Create invoice for $1000
    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0002"),
        partner_id="partner-456",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("1000.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(invoice)

    # Create partial payment of $600
    payment = Payment(
        invoice_id=invoice.id,
        payment_date=date.today(),
        amount=Money(Decimal("600.00"), "USD"),
        method=PaymentMethod.CASH,
    )

    service = PaymentAllocationService(invoice_repo, payment_repo)
    service.allocate_payment_to_invoice(payment, invoice)

    # Invoice should still be SENT (not fully paid)
    updated_invoice = invoice_repo.get_by_id(invoice.id)
    assert updated_invoice is not None
    assert updated_invoice.status == InvoiceStatus.SENT

    # Get balance
    payment_repo.save(payment)
    balance = service.get_invoice_balance(invoice.id)
    assert balance.amount_paid.amount == Decimal("600.00")
    assert balance.amount_due.amount == Decimal("400.00")


def test_payment_allocation_currency_mismatch(
    invoice_repo: IInvoiceRepository, payment_repo: IPaymentRepository
):
    """Test payment allocation with currency mismatch."""
    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0003"),
        partner_id="partner-789",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("1000.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(invoice)

    # Payment in different currency
    payment = Payment(
        invoice_id=invoice.id,
        payment_date=date.today(),
        amount=Money(Decimal("1000.00"), "EUR"),
        method=PaymentMethod.TRANSFER,
    )

    service = PaymentAllocationService(invoice_repo, payment_repo)

    with pytest.raises(ValueError, match="currency mismatch"):
        service.allocate_payment_to_invoice(payment, invoice)


def test_payment_allocation_overpayment(
    invoice_repo: IInvoiceRepository, payment_repo: IPaymentRepository
):
    """Test payment allocation with overpayment."""
    invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0004"),
        partner_id="partner-abc",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("1000.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(invoice)

    # Payment exceeds invoice total
    payment = Payment(
        invoice_id=invoice.id,
        payment_date=date.today(),
        amount=Money(Decimal("1500.00"), "USD"),
        method=PaymentMethod.CASH,
    )

    service = PaymentAllocationService(invoice_repo, payment_repo)

    with pytest.raises(ValueError, match="exceeds"):
        service.allocate_payment_to_invoice(payment, invoice)


def test_overdue_invoice_service(invoice_repo: IInvoiceRepository):
    """Test overdue invoice detection service."""
    # Create sent invoice with past due date
    overdue_invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0005"),
        partner_id="partner-def",
        invoice_date=date.today() - timedelta(days=60),
        due_date=date.today() - timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("1000.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(overdue_invoice)

    # Create sent invoice not yet due
    current_invoice = Invoice(
        invoice_number=InvoiceNumber("INV-2025-0006"),
        partner_id="partner-ghi",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItem(
                description="Service",
                quantity=Decimal("1"),
                unit_price=Money(Decimal("500.00"), "USD"),
            )
        ],
        status=InvoiceStatus.SENT,
    )
    invoice_repo.save(current_invoice)

    # Run overdue detection
    service = OverdueInvoiceService(invoice_repo)
    updated_count = service.update_overdue_invoices()

    assert updated_count == 1

    # Verify overdue invoice status updated
    updated_invoice = invoice_repo.get_by_id(overdue_invoice.id)
    assert updated_invoice is not None
    assert updated_invoice.status == InvoiceStatus.OVERDUE

    # Verify current invoice unchanged
    unchanged_invoice = invoice_repo.get_by_id(current_invoice.id)
    assert unchanged_invoice is not None
    assert unchanged_invoice.status == InvoiceStatus.SENT
