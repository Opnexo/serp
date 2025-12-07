# SERP Invoicing Module

Invoice management and payment tracking for the SERP platform.

## Features

- **Invoice Management**: Create, update, and track invoices
- **Line Items**: Detailed invoice line items with quantities, prices, and taxes
- **Tax Calculation**: Automatic tax calculation at line and total level
- **Payment Tracking**: Record and track payments (full/partial)
- **Invoice Status**: Draft, Sent, Paid, Overdue, Cancelled
- **Auto-numbering**: Automatic invoice number generation
- **Due Date Management**: Track due dates and overdue invoices
- **Multiple Payment Methods**: Cash, card, transfer, check
- **Payment Allocation**: Allocate payments to specific invoices

## Installation

```bash
uv add serp-invoicing
```

## Quick Start

```python
from decimal import Decimal
from datetime import date, timedelta
from serp_invoicing.application.services import InvoiceService, PaymentService
from serp_invoicing.application.dto import InvoiceCreateDTO, InvoiceItemDTO, PaymentCreateDTO

# Create invoice service
invoice_service = InvoiceService(invoice_repo)

# Create an invoice
invoice_dto = InvoiceCreateDTO(
    partner_id="customer-123",
    invoice_date=date.today(),
    due_date=date.today() + timedelta(days=30),
    line_items=[
        InvoiceItemDTO(
            description="Software License",
            quantity=Decimal("1"),
            unit_price=Decimal("1000.00"),
            tax_rate=Decimal("0.10"),  # 10% tax
        ),
        InvoiceItemDTO(
            description="Support Services",
            quantity=Decimal("12"),
            unit_price=Decimal("50.00"),
            tax_rate=Decimal("0.10"),
        ),
    ],
    notes="Annual software license and support",
    currency="USD",
)

invoice = await invoice_service.create_invoice(invoice_dto)
print(f"Invoice {invoice.invoice_number} created")
print(f"Total: {invoice.total_amount}")

# Record a payment
payment_dto = PaymentCreateDTO(
    invoice_id=invoice.id,
    amount=Decimal("1760.00"),  # Full amount
    payment_date=date.today(),
    method="TRANSFER",
    reference="BANK-TXN-12345",
)

payment = await payment_service.create_payment(payment_dto)
print(f"Payment recorded: {payment.amount}")
```

## API Endpoints

All endpoints are registered at `/api/invoicing/*`:

### Invoices
- `GET /api/invoicing/invoices` - List invoices
- `GET /api/invoicing/invoices/{id}` - Get invoice
- `POST /api/invoicing/invoices` - Create invoice
- `PUT /api/invoicing/invoices/{id}` - Update invoice
- `DELETE /api/invoicing/invoices/{id}` - Delete invoice
- `POST /api/invoicing/invoices/{id}/send` - Mark invoice as sent
- `POST /api/invoicing/invoices/{id}/cancel` - Cancel invoice

### Payments
- `GET /api/invoicing/payments` - List payments
- `GET /api/invoicing/payments/{id}` - Get payment
- `POST /api/invoicing/payments` - Create payment
- `DELETE /api/invoicing/payments/{id}` - Delete payment
- `GET /api/invoicing/invoices/{id}/payments` - Get invoice payments

## Permissions

Module permissions follow the pattern `invoicing:<resource>:<action>`:

- `invoicing:invoices:list` - List invoices
- `invoicing:invoices:read` - Read invoice details
- `invoicing:invoices:create` - Create invoices
- `invoicing:invoices:update` - Update invoices
- `invoicing:invoices:delete` - Delete invoices
- `invoicing:payments:*` - Payment permissions

## Domain Model

### Invoice (Aggregate Root)

```python
@dataclass
class Invoice(AggregateRoot):
    invoice_number: str  # Auto-generated (e.g., INV-2025-0001)
    partner_id: str  # Customer reference
    invoice_date: date
    due_date: date
    status: InvoiceStatus  # DRAFT | SENT | PAID | OVERDUE | CANCELLED
    
    # Line items (owned entities)
    line_items: list[InvoiceItem]
    
    # Amounts
    subtotal: Money
    tax_amount: Money
    total_amount: Money
    paid_amount: Money
    
    # Metadata
    notes: str | None
    terms: str | None
```

### InvoiceItem (Entity, owned by Invoice)

```python
@dataclass
class InvoiceItem(Entity):
    description: str
    quantity: Decimal
    unit_price: Money
    tax_rate: Decimal
    line_total: Money
    tax_amount: Money
    total: Money
```

### Payment (Aggregate Root)

```python
@dataclass
class Payment(AggregateRoot):
    invoice_id: str  # References Invoice
    payment_date: date
    amount: Money
    method: PaymentMethod  # CASH | CARD | TRANSFER | CHECK
    reference: str | None
```

## Business Rules

1. **Invoice Numbers**: Auto-generated, sequential, unique (INV-YYYY-NNNN)
2. **Line Item Totals**: Calculated automatically from quantity × unit_price
3. **Tax Calculation**: Applied at line item level, summed for total
4. **Payment Allocation**: Payments reduce invoice balance
5. **Overdue Detection**: Auto-detected based on due_date
6. **Status Transitions**: DRAFT → SENT → PAID (or CANCELLED)

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy serp_invoicing

# Linting
uv run ruff check serp_invoicing
```

## License

MIT License - See LICENSE file for details
