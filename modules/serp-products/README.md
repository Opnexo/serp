# SERP Products Module

Comprehensive product catalog management for the SimpleERP platform.

## Features

- **Product Types** - Physical goods, services, digital products, bundles
- **Multi-UoM System** - Sell same product in different units (each, box, case)
- **Dynamic Attributes** - Flexible attribute system for any property (weight, color, size, etc.)
- **Unit Conversions** - Automatic conversion between compatible units (kg↔lb, cm↔inch)
- **Product Variants** - Handle product variations (T-Shirt: Blue/Large, Red/Small)
- **Categories** - Hierarchical product categorization
- **Price Lists** - Volume pricing, customer-specific, time-based pricing
- **Bill of Materials** - Product bundles and kits
- **Barcode Support** - Different barcodes per UoM

## Architecture

Following DDD principles with clear aggregate boundaries:

### Aggregates

1. **Product** (AggregateRoot)
   - ProductUoM (owned entities) - different ways to sell/buy
   - ProductAttribute (owned entities) - dynamic properties
   - Product type: PHYSICAL, SERVICE, DIGITAL, BUNDLE
   - Variant support with parent-child relationships

2. **UnitOfMeasure** (AggregateRoot)
   - Unit definitions with conversion factors
   - Categories: UNIT, WEIGHT, VOLUME, LENGTH, TIME, etc.
   - Base unit tracking for conversions

3. **AttributeDefinition** (AggregateRoot)
   - Defines available product attributes
   - Data types: TEXT, NUMERIC, BOOLEAN, DATE, REFERENCE
   - Validation rules and applicable product types

4. **Category** (AggregateRoot)
   - Hierarchical organization
   - Default attributes per category

5. **PriceList** (AggregateRoot)
   - PriceRule (owned entities) - product prices per UoM
   - Volume pricing support
   - Time-based validity

6. **BillOfMaterials** (AggregateRoot)
   - BoMLine (owned entities) - component products
   - Quantity and UoM per component

## Installation

```bash
cd serp
uv pip install -e modules/serp-products
```

## Usage Examples

### Create Physical Product with Multiple UoMs

```python
from serp_products.application.services import ProductService
from serp_products.application.dto import ProductCreateDTO, ProductUoMDTO

# Create product that can be sold as units, boxes, or cases
battery_dto = ProductCreateDTO(
    code="BATT-AA",
    name="AA Battery",
    product_type="PHYSICAL",
    category_id="cat-batteries",
    base_uom_id="EA",
    is_stockable=True,
    can_be_sold=True,
    can_be_purchased=True,
    uoms=[
        ProductUoMDTO(
            uom_id="EA",
            conversion_factor=1,
            can_be_sold=True,
            barcode="123456789"
        ),
        ProductUoMDTO(
            uom_id="BX",
            conversion_factor=4,  # 1 box = 4 batteries
            can_be_sold=True,
            barcode="987654321"
        ),
        ProductUoMDTO(
            uom_id="CS",
            conversion_factor=48,  # 1 case = 48 batteries
            can_be_sold=True,
            can_be_purchased=True,
        ),
    ]
)

battery = product_service.create_product(battery_dto)
```

### Create Service Product

```python
consulting_dto = ProductCreateDTO(
    code="SVC-CONSULTING",
    name="IT Consulting",
    product_type="SERVICE",
    base_uom_id="HR",
    is_stockable=False,  # Services not tracked in inventory
    can_be_sold=True,
    attributes=[
        ProductAttributeDTO(
            attribute_definition_id="EXPERTISE_LEVEL",
            text_value="Senior"
        ),
        ProductAttributeDTO(
            attribute_definition_id="DURATION",
            numeric_value=1.0,
            uom_id="HR"
        ),
    ]
)
```

### Create Product with Dynamic Attributes

```python
laptop_dto = ProductCreateDTO(
    code="LAPTOP-XPS-15",
    name="Dell XPS 15",
    product_type="PHYSICAL",
    attributes=[
        ProductAttributeDTO(
            attribute_definition_id="WEIGHT",
            numeric_value=2.0,
            uom_id="KG"
        ),
        ProductAttributeDTO(
            attribute_definition_id="SCREEN_SIZE",
            numeric_value=15.6,
            uom_id="INCH"
        ),
        ProductAttributeDTO(
            attribute_definition_id="COLOR",
            text_value="Silver"
        ),
    ]
)
```

### Create Product Bundle

```python
# Create BoM for starter kit
bom_dto = BoMCreateDTO(
    product_id=starter_kit.id,
    components=[
        BoMLineDTO(
            component_product_id=battery.id,
            quantity=4,
            uom_id="EA"
        ),
        BoMLineDTO(
            component_product_id=charger.id,
            quantity=1,
            uom_id="EA"
        ),
    ]
)
```

### Price List with Multi-UoM

```python
price_list_dto = PriceListCreateDTO(
    name="Standard Pricing 2025",
    currency="USD",
    is_default=True,
    rules=[
        PriceRuleDTO(
            product_id=battery.id,
            uom_id="EA",
            min_quantity=1,
            unit_price=2.00
        ),
        PriceRuleDTO(
            product_id=battery.id,
            uom_id="BX",  # Box pricing
            min_quantity=1,
            unit_price=7.00  # Discount vs 4× individual
        ),
    ]
)
```

## API Endpoints

### Products
- `POST /api/products` - Create product
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/products/by-code/{code}` - Get by product code
- `GET /api/categories/{id}/products` - Get products in category

### Units of Measure
- `POST /api/uoms` - Create UoM
- `GET /api/uoms` - List UoMs
- `GET /api/uoms/{id}` - Get UoM
- `POST /api/uoms/convert` - Convert between units

### Attribute Definitions
- `POST /api/attributes` - Create attribute definition
- `GET /api/attributes` - List attributes
- `GET /api/attributes/{id}` - Get attribute

### Categories
- `POST /api/categories` - Create category
- `GET /api/categories` - List categories (tree)
- `GET /api/categories/{id}` - Get category

### Price Lists
- `POST /api/pricelists` - Create price list
- `GET /api/pricelists` - List price lists
- `GET /api/pricelists/{id}/price` - Get product price

### Bill of Materials
- `POST /api/bom` - Create BoM
- `GET /api/bom/product/{id}` - Get product BoM
- `GET /api/bom/{id}/cost` - Calculate BoM cost

## Domain Events

- `ProductCreated`, `ProductUpdated`, `ProductDeleted`, `ProductActivated`, `ProductDeactivated`
- `UnitOfMeasureCreated`, `UnitOfMeasureUpdated`
- `AttributeDefinitionCreated`, `AttributeDefinitionUpdated`
- `CategoryCreated`, `CategoryUpdated`
- `PriceListCreated`, `PriceListUpdated`, `PriceRuleUpdated`
- `BillOfMaterialsCreated`, `BillOfMaterialsUpdated`

## Future Enhancements

- Product images and documents
- Advanced search with attribute filters
- Product templates for quick creation
- Automatic variant generation
- Integration with sales for pricing
- Integration with inventory for stock levels
- Product lifecycle management (new, active, obsolete)
- Multi-language support for product names/descriptions
