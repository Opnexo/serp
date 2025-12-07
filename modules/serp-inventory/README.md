# SERP Inventory Module

Warehouse management and stock tracking for SimpleERP.

## Features

- **Multi-Warehouse Support**
  - Multiple warehouses with hierarchical locations
  - Zone, aisle, bin location tracking
  - Location types: STOCK, TRANSIT, CUSTOMER, SUPPLIER, PRODUCTION, SCRAP

- **Stock Management**
  - Real-time stock quantities by product and location
  - Multi-UoM tracking (integrates with serp-products)
  - Lot/Serial number tracking
  - Reserved vs available quantities
  - Stock valuation (FIFO, LIFO, Average Cost)

- **Stock Movements**
  - Receipt (from purchase orders)
  - Delivery (to customers)
  - Internal transfers
  - Manufacturing consumption/production
  - Stock adjustments
  - Movement states: DRAFT → CONFIRMED → DONE → CANCELLED

- **Inventory Adjustments**
  - Cycle counts
  - Physical inventory
  - Stock corrections
  - Reason tracking

- **Reordering Rules**
  - Min/Max quantities
  - Safety stock levels
  - Automatic procurement suggestions
  - Lead time consideration

- **Lot & Serial Tracking**
  - Expiration dates
  - Traceability (upstream/downstream)
  - Batch management

## Domain Model

### Aggregates

- **Warehouse**
  - Multiple locations hierarchy
  - Active/inactive status
  - Address and contact info

- **StockLocation**
  - Hierarchical structure (parent-child)
  - Location types
  - Capacity limits
  - Usage: INTERNAL, EXTERNAL, VIEW (virtual)

- **StockQuant**
  - Product + Location + Lot/Serial
  - Quantity on hand
  - Reserved quantity
  - Available quantity (on_hand - reserved)

- **StockMove**
  - Source location → Destination location
  - Product + Quantity + UoM
  - Reference document (PO, SO, Transfer)
  - Picking/packing operations
  - States: DRAFT, CONFIRMED, DONE, CANCELLED

- **InventoryAdjustment**
  - Stock counts and corrections
  - Theoretical vs counted quantities
  - Adjustment reasons
  - Approval workflow

- **ReorderingRule**
  - Product + Location
  - Min/Max quantities
  - Route (buy vs manufacture)
  - Lead time days

- **LotSerial**
  - Unique identifier
  - Product reference
  - Expiration date
  - Notes/attributes

## API Endpoints

### Warehouses
- `POST /api/v1/inventory/warehouses` - Create warehouse
- `GET /api/v1/inventory/warehouses/{id}` - Get warehouse
- `PUT /api/v1/inventory/warehouses/{id}` - Update warehouse
- `GET /api/v1/inventory/warehouses` - List warehouses

### Stock Locations
- `POST /api/v1/inventory/locations` - Create location
- `GET /api/v1/inventory/locations/{id}` - Get location
- `PUT /api/v1/inventory/locations/{id}` - Update location
- `GET /api/v1/inventory/locations` - List locations
- `GET /api/v1/inventory/locations/{id}/children` - List child locations

### Stock Levels
- `GET /api/v1/inventory/stock` - Query stock levels
- `GET /api/v1/inventory/stock/product/{product_id}` - Stock by product
- `GET /api/v1/inventory/stock/location/{location_id}` - Stock by location
- `GET /api/v1/inventory/stock/available` - Available stock (on_hand - reserved)

### Stock Movements
- `POST /api/v1/inventory/moves` - Create movement
- `GET /api/v1/inventory/moves/{id}` - Get movement
- `POST /api/v1/inventory/moves/{id}/confirm` - Confirm movement
- `POST /api/v1/inventory/moves/{id}/execute` - Execute movement
- `POST /api/v1/inventory/moves/{id}/cancel` - Cancel movement
- `GET /api/v1/inventory/moves` - List movements

### Inventory Adjustments
- `POST /api/v1/inventory/adjustments` - Create adjustment
- `GET /api/v1/inventory/adjustments/{id}` - Get adjustment
- `POST /api/v1/inventory/adjustments/{id}/confirm` - Confirm adjustment
- `GET /api/v1/inventory/adjustments` - List adjustments

### Reordering Rules
- `POST /api/v1/inventory/reordering-rules` - Create rule
- `GET /api/v1/inventory/reordering-rules/{id}` - Get rule
- `PUT /api/v1/inventory/reordering-rules/{id}` - Update rule
- `GET /api/v1/inventory/reordering-rules` - List rules
- `POST /api/v1/inventory/reordering-rules/check` - Check and suggest orders

### Lot/Serial Numbers
- `POST /api/v1/inventory/lots` - Create lot
- `GET /api/v1/inventory/lots/{id}` - Get lot
- `GET /api/v1/inventory/lots/product/{product_id}` - Lots by product
- `GET /api/v1/inventory/lots/{id}/trace` - Trace lot movements

## Integration Points

### serp-products
- Product references with multi-UoM support
- Stockable flag determines if tracked
- Product types (PHYSICAL tracked, SERVICE not tracked)

### serp-procurement
- GoodsReceiptNote → StockMove (receipt from supplier)
- PurchaseOrder → Reserve stock location

### serp-sales (future)
- SalesOrder → Reserve stock
- Delivery order → StockMove (delivery to customer)

### serp-logistics (future)
- Picking operations
- Packing operations
- Shipping integration

## Business Rules

1. **Stock Availability**: Available = On Hand - Reserved
2. **Negative Stock**: Configurable per location (allow/disallow)
3. **Lot Tracking**: Required for products with lot_tracked=True
4. **Serial Tracking**: One serial = quantity of 1
5. **FIFO/LIFO**: Applies to lot selection and valuation
6. **Location Hierarchy**: Stock in child locations included in parent totals
7. **Movement Validation**: Source must have available stock
8. **Adjustment Approval**: May require approval based on threshold

## Example Usage

```python
from serp_inventory import StockService, StockMoveCreateDTO

# Create stock movement (goods receipt)
move_dto = StockMoveCreateDTO(
    product_id="PROD001",
    product_code="BATTERY-AA",
    quantity=Decimal("100"),
    uom_id="BX",
    source_location_id="LOC-SUPPLIER",
    dest_location_id="LOC-STOCK-A1",
    reference="GRN000001",
    reference_type="GOODS_RECEIPT",
)

move = stock_service.create_movement(move_dto)
stock_service.confirm_movement(move.id)
stock_service.execute_movement(move.id)

# Check available stock
available = stock_service.get_available_stock(
    product_id="PROD001",
    location_id="LOC-STOCK-A1"
)
# Returns: on_hand=100, reserved=0, available=100

# Reserve stock (for sales order)
stock_service.reserve_stock(
    product_id="PROD001",
    location_id="LOC-STOCK-A1",
    quantity=Decimal("20")
)
# Now: on_hand=100, reserved=20, available=80
```

## Development

```bash
# Run tests
pytest serp_inventory/

# Type checking
mypy serp_inventory/

# Linting
ruff check serp_inventory/
```
