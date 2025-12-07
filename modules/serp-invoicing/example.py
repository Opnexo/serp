"""
Example usage of the Invoicing module.

This script demonstrates:
- Creating invoices with line items
- Generating invoice numbers
- Recording payments
- Checking invoice balances
- Handling overdue invoices
"""

from datetime import date, timedelta
from decimal import Decimal

from serp_invoicing.application.dto import (
    InvoiceCreateDTO,
    InvoiceItemDTO,
    PaymentCreateDTO,
)
from serp_invoicing.application.services import InvoiceService, PaymentService
from serp_invoicing.domain.services import (
    InvoiceNumberGenerator,
    OverdueInvoiceService,
    PaymentAllocationService,
)
from serp_invoicing.domain.value_objects import PaymentMethod
from serp_invoicing.infrastructure.repositories import (
    InMemoryInvoiceRepository,
    InMemoryPaymentRepository,
)


def main():
    """Run example workflow."""
    # Initialize repositories
    invoice_repo = InMemoryInvoiceRepository()
    payment_repo = InMemoryPaymentRepository()

    # Initialize domain services
    invoice_number_gen = InvoiceNumberGenerator(invoice_repo)
    payment_allocation = PaymentAllocationService(invoice_repo, payment_repo)
    overdue_service = OverdueInvoiceService(invoice_repo)

    # Initialize application services
    invoice_service = InvoiceService(invoice_repo, invoice_number_gen)
    payment_service = PaymentService(
        payment_repo, invoice_repo, invoice_number_gen, payment_allocation
    )

    print("=" * 60)
    print("INVOICING MODULE - EXAMPLE WORKFLOW")
    print("=" * 60)

    # 1. Create first invoice
    print("\n1. Creating invoice for consulting services...")
    invoice1_dto = InvoiceCreateDTO(
        partner_id="partner-123",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItemDTO(
                description="Software Development Consulting",
                quantity=Decimal("40"),  # hours
                unit_price=Decimal("150.00"),
                tax_rate=Decimal("0.10"),  # 10% tax
            ),
            InvoiceItemDTO(
                description="Project Management",
                quantity=Decimal("10"),
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("0.10"),
            ),
        ],
    )

    invoice1 = invoice_service.create_invoice(invoice1_dto)
    print(f"  ✓ Invoice created: {invoice1.invoice_number}")
    print(f"    Subtotal: ${invoice1.subtotal:.2f}")
    print(f"    Tax: ${invoice1.tax_amount:.2f}")
    print(f"    Total: ${invoice1.total_amount:.2f}")
    print(f"    Status: {invoice1.status}")

    # 2. Send invoice
    print(f"\n2. Sending invoice {invoice1.invoice_number}...")
    sent_invoice = invoice_service.send_invoice(invoice1.id)
    print(f"  ✓ Invoice sent on {sent_invoice.sent_at}")
    print(f"    Due date: {sent_invoice.due_date}")

    # 3. Create second invoice
    print("\n3. Creating invoice for software licenses...")
    invoice2_dto = InvoiceCreateDTO(
        partner_id="partner-456",
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=15),
        currency="USD",
        line_items=[
            InvoiceItemDTO(
                description="Annual Software License - Pro Plan",
                quantity=Decimal("5"),
                unit_price=Decimal("299.00"),
                tax_rate=Decimal("0.08"),  # 8% tax
            ),
        ],
    )

    invoice2 = invoice_service.create_invoice(invoice2_dto)
    print(f"  ✓ Invoice created: {invoice2.invoice_number}")
    print(f"    Total: ${invoice2.total_amount:.2f}")

    invoice_service.send_invoice(invoice2.id)

    # 4. Record partial payment for invoice 1
    print(f"\n4. Recording partial payment for {invoice1.invoice_number}...")
    payment1_dto = PaymentCreateDTO(
        invoice_id=invoice1.id,
        payment_date=date.today(),
        amount=Decimal("3500.00"),  # Partial payment
        method=PaymentMethod.TRANSFER,
        reference="TXN-001-2025",
    )

    payment1 = payment_service.create_payment(payment1_dto)
    print(f"  ✓ Payment recorded: ${payment1.amount:.2f}")
    print(f"    Method: {payment1.method}")

    # Check balance
    balance1 = payment_service.get_invoice_balance(invoice1.id)
    print(f"    Balance remaining: ${balance1.amount_due:.2f}")

    # 5. Record full payment for invoice 2
    print(f"\n5. Recording full payment for {invoice2.invoice_number}...")
    payment2_dto = PaymentCreateDTO(
        invoice_id=invoice2.id,
        payment_date=date.today(),
        amount=invoice2.total_amount,
        method=PaymentMethod.CARD,
        reference="CC-4242-2025",
    )

    payment2 = payment_service.create_payment(payment2_dto)
    print(f"  ✓ Payment recorded: ${payment2.amount:.2f}")

    # Verify invoice is paid
    paid_invoice = invoice_service.get_invoice(invoice2.id)
    print(f"    Invoice status: {paid_invoice.status}")
    print(f"    Paid at: {paid_invoice.paid_at}")

    # 6. List all invoices
    print("\n6. Listing all invoices...")
    all_invoices = invoice_service.list_invoices(skip=0, limit=10)
    print(f"  Total invoices: {all_invoices.total}")
    for inv in all_invoices.items:
        print(f"    - {inv.invoice_number}: ${inv.total_amount:.2f} [{inv.status}]")

    # 7. Get invoice summary
    print("\n7. Getting invoice summary...")
    summary = invoice_service.get_invoice_summary()
    print(f"  Total invoices: {summary.total_count}")
    print(f"  Draft: {summary.draft_count}")
    print(f"  Sent: {summary.sent_count}")
    print(f"  Paid: {summary.paid_count}")
    print(f"  Overdue: {summary.overdue_count}")
    print(f"  Total amount: ${summary.total_amount:.2f}")
    print(f"  Amount paid: ${summary.amount_paid:.2f}")
    print(f"  Amount outstanding: ${summary.amount_outstanding:.2f}")

    # 8. Create overdue invoice (backdated)
    print("\n8. Creating overdue invoice scenario...")
    overdue_dto = InvoiceCreateDTO(
        partner_id="partner-789",
        invoice_date=date.today() - timedelta(days=60),
        due_date=date.today() - timedelta(days=30),
        currency="USD",
        line_items=[
            InvoiceItemDTO(
                description="Past Due Service",
                quantity=Decimal("1"),
                unit_price=Decimal("500.00"),
            ),
        ],
    )

    overdue_invoice = invoice_service.create_invoice(overdue_dto)
    invoice_service.send_invoice(overdue_invoice.id)
    print(f"  ✓ Created backdated invoice: {overdue_invoice.invoice_number}")

    # Update overdue status
    updated_count = invoice_service.update_overdue_invoices()
    print(f"  ✓ Updated {updated_count} overdue invoice(s)")

    # Check final summary
    final_summary = invoice_service.get_invoice_summary()
    print(f"  Overdue invoices: {final_summary.overdue_count}")

    # 9. Complete payment for invoice 1
    print(f"\n9. Completing payment for {invoice1.invoice_number}...")
    remaining_balance = payment_service.get_invoice_balance(invoice1.id)
    print(f"  Outstanding: ${remaining_balance.amount_due:.2f}")

    final_payment_dto = PaymentCreateDTO(
        invoice_id=invoice1.id,
        payment_date=date.today(),
        amount=remaining_balance.amount_due,
        method=PaymentMethod.CASH,
        reference="CASH-2025-001",
    )

    final_payment = payment_service.create_payment(final_payment_dto)
    print(f"  ✓ Final payment recorded: ${final_payment.amount:.2f}")

    fully_paid = invoice_service.get_invoice(invoice1.id)
    print(f"    Invoice status: {fully_paid.status}")

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
