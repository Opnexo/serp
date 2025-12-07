# SERP Procurement Module

Purchase order management and supplier procurement for SimpleERP.

## Features

- **Request for Quotation (RFQ)**
  - Create RFQs and send to multiple suppliers
  - Compare supplier quotes
  - Convert RFQ to Purchase Order

- **Purchase Orders**
  - Multi-line orders with product references
  - Multi-UoM support (from serp-products)
  - Order states: DRAFT → CONFIRMED → RECEIVED → INVOICED → CANCELLED
  - Partial receipts supported
  - Purchase order amendments and cancellations

- **Goods Receipt Notes**
  - Record incoming goods from suppliers
  - Link to purchase orders
  - Quality control status
  - Partial receipts with backorders
  - Creates inventory movements (integration point for serp-inventory)

- **Purchase Agreements**
  - Blanket orders with suppliers
  - Volume commitments and pricing
  - Call-off orders against agreements

- **Supplier Management**
  - Extends serp-crm Partner (type=SUPPLIER)
  - Payment terms
  - Lead times
  - Preferred products

## Domain Model

### Aggregates

- **RFQ** (Request for Quotation)
  - RFQLine (owned entity)
  - States: DRAFT, SENT, QUOTED, ACCEPTED, CANCELLED

- **PurchaseOrder**
  - PurchaseOrderLine (owned entity)
  - States: DRAFT, CONFIRMED, RECEIVED, INVOICED, CANCELLED
  - Tracks expected vs received quantities

- **GoodsReceiptNote**
  - GRNLine (owned entity)
  - Links to PurchaseOrder
  - Quality status: PENDING, PASSED, FAILED
  - Creates stock movements

- **PurchaseAgreement**
  - AgreementLine (owned entity)
  - Valid from/to dates
  - Volume commitments

### Value Objects

- `PurchaseOrderNumber`: Unique PO identifier
- `PurchaseOrderState`: Order lifecycle states
- `ReceiptStatus`: Goods receipt states
- `QualityStatus`: Quality control results
- `DeliveryTerms`: Incoterms (FOB, CIF, EXW, etc.)
- `PaymentTerms`: Payment conditions

## API Endpoints

### RFQs
- `POST /api/v1/procurement/rfqs` - Create RFQ
- `GET /api/v1/procurement/rfqs/{id}` - Get RFQ
- `PUT /api/v1/procurement/rfqs/{id}` - Update RFQ
- `POST /api/v1/procurement/rfqs/{id}/send` - Send to suppliers
- `POST /api/v1/procurement/rfqs/{id}/convert` - Convert to PO
- `GET /api/v1/procurement/rfqs` - List RFQs

### Purchase Orders
- `POST /api/v1/procurement/pos` - Create PO
- `GET /api/v1/procurement/pos/{id}` - Get PO
- `PUT /api/v1/procurement/pos/{id}` - Update PO
- `POST /api/v1/procurement/pos/{id}/confirm` - Confirm order
- `POST /api/v1/procurement/pos/{id}/cancel` - Cancel order
- `GET /api/v1/procurement/pos` - List POs
- `GET /api/v1/procurement/pos/supplier/{supplier_id}` - List by supplier

### Goods Receipt Notes
- `POST /api/v1/procurement/grns` - Create GRN
- `GET /api/v1/procurement/grns/{id}` - Get GRN
- `POST /api/v1/procurement/grns/{id}/quality-check` - Update quality status
- `GET /api/v1/procurement/grns` - List GRNs
- `GET /api/v1/procurement/grns/po/{po_id}` - List by PO

### Purchase Agreements
- `POST /api/v1/procurement/agreements` - Create agreement
- `GET /api/v1/procurement/agreements/{id}` - Get agreement
- `PUT /api/v1/procurement/agreements/{id}` - Update agreement
- `GET /api/v1/procurement/agreements` - List agreements

## Integration Points

### serp-crm
- Suppliers are Partners with `partner_type=SUPPLIER`
- Uses `Money` value object for pricing

### serp-products
- References `Product` entities
- Multi-UoM support for ordering (order in EA, receive in BX)
- Product information for PO lines

### serp-inventory (future)
- GoodsReceiptNote creates stock movements
- Updates inventory levels on receipt
- Lot/Serial tracking integration

### serp-invoicing
- Purchase orders link to vendor invoices
- 3-way match: PO ↔ GRN ↔ Invoice

## Business Rules

1. **RFQ to PO Conversion**: RFQ must be in QUOTED or ACCEPTED state
2. **PO Confirmation**: Cannot confirm without supplier and lines
3. **Goods Receipt**: Can only receive confirmed POs
4. **Partial Receipts**: Track received vs ordered quantities
5. **Quality Control**: Failed quality creates return process
6. **Order Cancellation**: Can only cancel DRAFT or CONFIRMED orders
7. **Agreement Usage**: Call-off orders must reference active agreement

## Example Usage

```python
from serp_procurement import (
    PurchaseOrderService,
    PurchaseOrderCreateDTO,
    PurchaseOrderLineDTO,
)

# Create purchase order
po_dto = PurchaseOrderCreateDTO(
    supplier_id="SUP001",
    order_date=date.today(),
    expected_delivery_date=date.today() + timedelta(days=14),
    payment_terms="NET30",
    delivery_terms="FOB",
    lines=[
        PurchaseOrderLineDTO(
            product_id="PROD001",
            product_code="BATTERY-AA",
            description="AA Batteries",
            quantity=Decimal("100"),
            uom_id="BX",  # Order in boxes
            unit_price=Decimal("7.50"),
            currency="USD",
        )
    ],
)

po = po_service.create_purchase_order(po_dto)

# Confirm the order
po_service.confirm_purchase_order(po.id)

# Receive goods
grn_dto = GoodsReceiptNoteCreateDTO(
    purchase_order_id=po.id,
    receipt_date=date.today(),
    lines=[
        GRNLineDTO(
            po_line_id=po.lines[0].id,
            received_quantity=Decimal("100"),
            uom_id="BX",
        )
    ],
)

grn = receipt_service.create_receipt(grn_dto)
```

## Development

```bash
# Run tests
pytest serp_procurement/

# Type checking
mypy serp_procurement/

# Linting
ruff check serp_procurement/
```
