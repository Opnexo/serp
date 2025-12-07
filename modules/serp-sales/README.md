# SERP Sales Module

Sales order management for the SimpleERP platform.

## Features

- **Quotes** - Create sales quotes with pricing, validity periods, convert to orders
- **Sales Orders** - Manage customer orders with order lines, fulfillment tracking
- **Order Fulfillment** - Track order status from draft to delivered
- **Pricing** - Line-item pricing with discounts, taxes, and totals
- **Stock Reservation** - Reserve inventory when orders are confirmed (integration point)
- **Partner Integration** - Link orders to CRM partners

## Architecture

Following DDD principles with clear aggregate boundaries:

### Aggregates

1. **Quote** (AggregateRoot)
   - QuoteLine (owned entities)
   - Lifecycle: DRAFT → SENT → ACCEPTED/REJECTED/EXPIRED
   - Can be converted to Sales Order

2. **SalesOrder** (AggregateRoot)
   - OrderLine (owned entities)
   - Lifecycle: DRAFT → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
   - References: Partner (CRM), Quote (optional)
   - Future: Stock reservation integration

### Domain Services

- **QuoteNumberGenerator** - Generate sequential quote numbers (QT-YYYY-NNNN)
- **OrderNumberGenerator** - Generate sequential order numbers (SO-YYYY-NNNN)
- **QuoteToOrderConverter** - Convert accepted quotes to sales orders
- **OrderTotalCalculator** - Calculate order totals with discounts and taxes

## Installation

```bash
cd serp
uv pip install -e modules/serp-sales
```

## Usage

### Create Quote

```python
from serp_sales.application.services import QuoteService
from serp_sales.application.dto import QuoteCreateDTO, QuoteLineDTO

quote_dto = QuoteCreateDTO(
    partner_id="partner-123",
    quote_date=date.today(),
    valid_until=date.today() + timedelta(days=30),
    currency="USD",
    lines=[
        QuoteLineDTO(
            product_code="PRD-001",
            description="Software License",
            quantity=Decimal("5"),
            unit_price=Decimal("299.00"),
            discount_percent=Decimal("10"),
            tax_rate=Decimal("0.08"),
        )
    ],
)

quote = quote_service.create_quote(quote_dto)
```

### Create Sales Order

```python
from serp_sales.application.services import SalesOrderService
from serp_sales.application.dto import SalesOrderCreateDTO, OrderLineDTO

order_dto = SalesOrderCreateDTO(
    partner_id="partner-123",
    order_date=date.today(),
    requested_delivery_date=date.today() + timedelta(days=7),
    currency="USD",
    lines=[
        OrderLineDTO(
            product_code="PRD-002",
            description="Professional Services",
            quantity=Decimal("40"),
            unit_price=Decimal("150.00"),
            tax_rate=Decimal("0.10"),
        )
    ],
)

order = order_service.create_order(order_dto)
```

### Convert Quote to Order

```python
# Accept quote
accepted_quote = quote_service.accept_quote(quote.id)

# Convert to sales order
order = order_service.create_order_from_quote(accepted_quote.id)
```

## API Endpoints

### Quotes
- `POST /api/sales/quotes` - Create quote
- `GET /api/sales/quotes` - List quotes
- `GET /api/sales/quotes/{id}` - Get quote details
- `PUT /api/sales/quotes/{id}` - Update quote (draft only)
- `POST /api/sales/quotes/{id}/send` - Send quote to customer
- `POST /api/sales/quotes/{id}/accept` - Accept quote
- `POST /api/sales/quotes/{id}/reject` - Reject quote
- `DELETE /api/sales/quotes/{id}` - Delete quote (draft only)

### Sales Orders
- `POST /api/sales/orders` - Create order
- `POST /api/sales/orders/from-quote/{quote_id}` - Create order from quote
- `GET /api/sales/orders` - List orders
- `GET /api/sales/orders/{id}` - Get order details
- `PUT /api/sales/orders/{id}` - Update order (draft only)
- `POST /api/sales/orders/{id}/confirm` - Confirm order
- `POST /api/sales/orders/{id}/process` - Start processing
- `POST /api/sales/orders/{id}/ship` - Mark as shipped
- `POST /api/sales/orders/{id}/deliver` - Mark as delivered
- `POST /api/sales/orders/{id}/cancel` - Cancel order
- `DELETE /api/sales/orders/{id}` - Delete order (draft only)

### Analytics
- `GET /api/sales/quotes/summary` - Quote statistics
- `GET /api/sales/orders/summary` - Order statistics

## Domain Events

- `QuoteCreated`, `QuoteUpdated`, `QuoteSent`, `QuoteAccepted`, `QuoteRejected`, `QuoteExpired`
- `SalesOrderCreated`, `SalesOrderUpdated`, `SalesOrderConfirmed`, `SalesOrderProcessing`, `SalesOrderShipped`, `SalesOrderDelivered`, `SalesOrderCancelled`

## Future Enhancements

- Stock reservation on order confirmation
- Automatic invoice generation from delivered orders
- Batch order processing
- Shipping integration (tracking numbers, carriers)
- Advanced pricing rules (volume discounts, customer-specific pricing)
- Sales analytics and forecasting
