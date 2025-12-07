# SERP Logistics Module

Fulfillment, picking, packing, and shipping management for SimpleERP.

## Features

- **Picking Operations**
  - Wave picking (batch orders)
  - Batch picking (multiple orders at once)
  - Zone picking (by warehouse area)
  - Single order picking
  - Pick list generation
  - Pick confirmation with lot/serial tracking

- **Packing Operations**
  - Package selection and optimization
  - Multi-package shipments
  - Weight and dimension tracking
  - Packing list generation
  - Package validation

- **Shipping Management**
  - Multi-carrier support
  - Rate shopping
  - Label generation
  - Tracking number management
  - Delivery status updates
  - Proof of delivery

- **Carrier Integration**
  - Carrier profiles (API credentials)
  - Service levels (Standard, Express, Overnight)
  - Rate calculation
  - Label printing
  - Tracking webhooks

- **Delivery Routes**
  - Route planning
  - Stop sequencing
  - Driver assignment
  - Route optimization
  - Delivery windows

- **Returns (RMA)**
  - Return authorization
  - Return receiving
  - Restocking or disposal
  - Refund/exchange processing

## Domain Model

### Aggregates

- **PickingOperation**
  - Picking strategy (wave, batch, zone, single)
  - Pick lines (product, quantity, location)
  - Assigned picker
  - States: PENDING → ASSIGNED → IN_PROGRESS → COMPLETED → CANCELLED

- **PackingOperation**
  - Links to picking operation
  - Packages (box selection, contents)
  - Packing materials
  - States: PENDING → IN_PROGRESS → COMPLETED → SHIPPED

- **Package**
  - Box type and dimensions
  - Weight (actual vs dimensional)
  - Contents (packed items)
  - Carrier and service level
  - Tracking number

- **Shipment**
  - Customer and delivery address
  - Packages
  - Carrier and service
  - Shipping cost
  - Tracking information
  - States: DRAFT → CONFIRMED → PICKED_UP → IN_TRANSIT → DELIVERED → RETURNED

- **Carrier**
  - Name and code
  - API credentials
  - Supported services
  - Rate calculation method
  - Label format preferences

- **DeliveryRoute**
  - Route date and driver
  - Stops (customer, address, packages)
  - Sequence optimization
  - States: PLANNED → IN_PROGRESS → COMPLETED

- **ReturnAuthorization (RMA)**
  - Original shipment reference
  - Return reason
  - Items to return
  - Return shipping label
  - States: REQUESTED → APPROVED → SHIPPED → RECEIVED → PROCESSED

## API Endpoints

### Picking Operations
- `POST /api/v1/logistics/pickings` - Create picking operation
- `GET /api/v1/logistics/pickings/{id}` - Get picking
- `POST /api/v1/logistics/pickings/{id}/assign` - Assign picker
- `POST /api/v1/logistics/pickings/{id}/start` - Start picking
- `POST /api/v1/logistics/pickings/{id}/complete` - Complete picking
- `POST /api/v1/logistics/pickings/{id}/cancel` - Cancel picking
- `GET /api/v1/logistics/pickings` - List pickings

### Packing Operations
- `POST /api/v1/logistics/packings` - Create packing operation
- `GET /api/v1/logistics/packings/{id}` - Get packing
- `POST /api/v1/logistics/packings/{id}/add-package` - Add package
- `POST /api/v1/logistics/packings/{id}/complete` - Complete packing
- `GET /api/v1/logistics/packings` - List packings

### Packages
- `POST /api/v1/logistics/packages` - Create package
- `GET /api/v1/logistics/packages/{id}` - Get package
- `PUT /api/v1/logistics/packages/{id}` - Update package
- `POST /api/v1/logistics/packages/{id}/weigh` - Record weight

### Shipments
- `POST /api/v1/logistics/shipments` - Create shipment
- `GET /api/v1/logistics/shipments/{id}` - Get shipment
- `POST /api/v1/logistics/shipments/{id}/confirm` - Confirm shipment
- `POST /api/v1/logistics/shipments/{id}/get-rates` - Get carrier rates
- `POST /api/v1/logistics/shipments/{id}/create-label` - Generate label
- `POST /api/v1/logistics/shipments/{id}/track` - Update tracking
- `GET /api/v1/logistics/shipments` - List shipments

### Carriers
- `POST /api/v1/logistics/carriers` - Create carrier
- `GET /api/v1/logistics/carriers/{id}` - Get carrier
- `PUT /api/v1/logistics/carriers/{id}` - Update carrier
- `GET /api/v1/logistics/carriers` - List carriers
- `POST /api/v1/logistics/carriers/{id}/test` - Test connection

### Delivery Routes
- `POST /api/v1/logistics/routes` - Create route
- `GET /api/v1/logistics/routes/{id}` - Get route
- `POST /api/v1/logistics/routes/{id}/optimize` - Optimize stops
- `POST /api/v1/logistics/routes/{id}/start` - Start route
- `POST /api/v1/logistics/routes/{id}/complete-stop` - Complete stop
- `GET /api/v1/logistics/routes` - List routes

### Returns (RMA)
- `POST /api/v1/logistics/rmas` - Create RMA
- `GET /api/v1/logistics/rmas/{id}` - Get RMA
- `POST /api/v1/logistics/rmas/{id}/approve` - Approve RMA
- `POST /api/v1/logistics/rmas/{id}/receive` - Receive return
- `POST /api/v1/logistics/rmas/{id}/process` - Process return
- `GET /api/v1/logistics/rmas` - List RMAs

## Integration Points

### serp-sales
- SalesOrder → PickingOperation (order fulfillment)
- Shipment → Updates order delivery status

### serp-inventory
- PickingOperation → StockMove (picks from locations)
- PackingOperation → Creates outbound stock moves
- RMA → StockMove (returns to stock)

### serp-crm
- Customer addresses for shipping
- Partner carriers

## Business Rules

1. **Picking Rules**:
   - Wave picking batches orders by timeframe
   - Zone picking assigns by warehouse area
   - FIFO/FEFO for lot selection
   - Backorder handling for insufficient stock

2. **Packing Rules**:
   - Package weight must not exceed carrier limits
   - Dimensional weight calculation
   - Fragile items require special packaging
   - Hazmat restrictions

3. **Shipping Rules**:
   - Address validation before label generation
   - Insurance for high-value shipments
   - Signature required based on value
   - Weekend delivery restrictions

4. **Carrier Rules**:
   - Service level selection (speed vs cost)
   - Dimensional weight pricing
   - Residential vs commercial rates
   - International customs forms

## Example Usage

```python
from serp_logistics import PickingService, PackingService, ShipmentService

# Create picking from sales order
picking = picking_service.create_picking(
    PickingCreateDTO(
        source_document="SO000123",
        source_document_type="SALES_ORDER",
        strategy=PickingStrategy.SINGLE,
        lines=[
            PickingLineDTO(
                product_id=product_id,
                quantity=Decimal("5"),
                source_location_id=location_id,
            )
        ],
    )
)

# Assign and complete picking
picking_service.assign_picker(picking.id, picker_id=user_id)
picking_service.start_picking(picking.id)
picking_service.complete_picking(picking.id)

# Create packing operation
packing = packing_service.create_packing(
    PackingCreateDTO(
        picking_operation_id=picking.id,
        packages=[
            PackageDTO(
                box_type="MEDIUM",
                weight_kg=Decimal("2.5"),
                items=[...],
            )
        ],
    )
)

# Create shipment and get rates
shipment = shipment_service.create_shipment(
    ShipmentCreateDTO(
        packing_operation_id=packing.id,
        carrier_id=carrier_id,
        service_level="STANDARD",
        delivery_address=address,
    )
)

rates = shipment_service.get_rates(shipment.id)
label = shipment_service.create_label(shipment.id, rate_id=rates[0].id)
```

## Development

```bash
# Run tests
pytest serp_logistics/

# Type checking
mypy serp_logistics/

# Linting
ruff check serp_logistics/
```
