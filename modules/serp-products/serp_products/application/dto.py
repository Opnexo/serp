"""Data Transfer Objects for Products module."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from serp_products.domain.value_objects import (
    AttributeDataType,
    ProductType,
    UoMCategory,
)


# UoM DTOs
class UoMCreateDTO(BaseModel):
    """Create Unit of Measure."""

    code: str = Field(max_length=20)
    name: str = Field(max_length=100)
    category: UoMCategory
    conversion_factor: Decimal = Field(default=Decimal("1.0"), gt=0)
    is_base_unit: bool = False
    symbol: str | None = Field(default=None, max_length=10)


class UoMUpdateDTO(BaseModel):
    """Update Unit of Measure."""

    name: str | None = Field(default=None, max_length=100)
    symbol: str | None = Field(default=None, max_length=10)


class UoMDTO(BaseModel):
    """Unit of Measure response."""

    id: str
    code: str
    name: str
    category: UoMCategory
    conversion_factor: Decimal
    is_base_unit: bool
    symbol: str | None
    created_at: datetime
    updated_at: datetime | None


# Attribute DTOs
class AttributeDefinitionCreateDTO(BaseModel):
    """Create Attribute Definition."""

    code: str = Field(max_length=50)
    name: str = Field(max_length=100)
    data_type: AttributeDataType
    applicable_types: list[ProductType] = Field(default_factory=list)
    default_uom_id: str | None = None
    is_required: bool = False
    is_variant_attribute: bool = False


class AttributeDefinitionUpdateDTO(BaseModel):
    """Update Attribute Definition."""

    name: str | None = Field(default=None, max_length=100)
    applicable_types: list[ProductType] | None = None
    default_uom_id: str | None = None
    is_required: bool | None = None
    is_variant_attribute: bool | None = None


class AttributeDefinitionDTO(BaseModel):
    """Attribute Definition response."""

    id: str
    code: str
    name: str
    data_type: AttributeDataType
    applicable_types: list[ProductType]
    default_uom_id: str | None
    is_required: bool
    is_variant_attribute: bool
    created_at: datetime
    updated_at: datetime | None


class AttributeValueDTO(BaseModel):
    """Attribute value (polymorphic)."""

    text_value: str | None = None
    numeric_value: Decimal | None = None
    boolean_value: bool | None = None
    date_value: date | None = None
    reference_id: str | None = None
    uom_id: str | None = None


class ProductAttributeDTO(BaseModel):
    """Product attribute."""

    attribute_definition_id: str
    value: AttributeValueDTO


# Category DTOs
class CategoryCreateDTO(BaseModel):
    """Create Category."""

    code: str = Field(max_length=50)
    name: str = Field(max_length=100)
    parent_id: str | None = None
    default_attribute_ids: list[str] = Field(default_factory=list)


class CategoryUpdateDTO(BaseModel):
    """Update Category."""

    name: str | None = Field(default=None, max_length=100)
    parent_id: str | None = None
    default_attribute_ids: list[str] | None = None


class CategoryDTO(BaseModel):
    """Category response."""

    id: str
    code: str
    name: str
    parent_id: str | None
    path: str
    default_attribute_ids: list[str]
    created_at: datetime
    updated_at: datetime | None


# Product DTOs
class ProductUoMDTO(BaseModel):
    """Product Unit of Measure."""

    uom_id: str
    conversion_factor: Decimal = Field(gt=0)
    can_be_sold: bool = True
    can_be_purchased: bool = True
    barcode: str | None = Field(default=None, max_length=100)


class ProductCreateDTO(BaseModel):
    """Create Product."""

    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    product_type: ProductType
    base_uom_id: str
    category_id: str
    is_active: bool = True
    is_stockable: bool = True
    can_be_sold: bool = True
    can_be_purchased: bool = True
    is_variant: bool = False
    parent_product_id: str | None = None
    attributes: list[ProductAttributeDTO] = Field(default_factory=list)
    uoms: list[ProductUoMDTO] = Field(default_factory=list)


class ProductUpdateDTO(BaseModel):
    """Update Product."""

    name: str | None = Field(default=None, max_length=200)
    category_id: str | None = None
    is_active: bool | None = None
    can_be_sold: bool | None = None
    can_be_purchased: bool | None = None


class ProductDTO(BaseModel):
    """Product response."""

    id: str
    code: str
    name: str
    product_type: ProductType
    base_uom_id: str
    category_id: str
    is_active: bool
    is_stockable: bool
    can_be_sold: bool
    can_be_purchased: bool
    is_variant: bool
    parent_product_id: str | None
    attributes: list[ProductAttributeDTO]
    uoms: list[ProductUoMDTO]
    created_at: datetime
    updated_at: datetime | None


# Price List DTOs
class PriceRuleDTO(BaseModel):
    """Price Rule."""

    product_id: str
    uom_id: str
    unit_price: Decimal = Field(gt=0)
    currency: str = Field(max_length=3)
    min_quantity: Decimal = Field(default=Decimal("1.0"), gt=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class PriceListCreateDTO(BaseModel):
    """Create Price List."""

    name: str = Field(max_length=100)
    currency: str = Field(max_length=3)
    is_default: bool = False
    valid_from: date | None = None
    valid_to: date | None = None
    rules: list[PriceRuleDTO] = Field(default_factory=list)


class PriceListUpdateDTO(BaseModel):
    """Update Price List."""

    name: str | None = Field(default=None, max_length=100)
    is_default: bool | None = None
    valid_from: date | None = None
    valid_to: date | None = None


class PriceListDTO(BaseModel):
    """Price List response."""

    id: str
    name: str
    currency: str
    is_default: bool
    valid_from: date | None
    valid_to: date | None
    rules: list[PriceRuleDTO]
    created_at: datetime
    updated_at: datetime | None


# Bill of Materials DTOs
class BoMLineDTO(BaseModel):
    """Bill of Materials Line."""

    component_product_id: str
    quantity: Decimal = Field(gt=0)
    uom_id: str


class BoMCreateDTO(BaseModel):
    """Create Bill of Materials."""

    product_id: str
    components: list[BoMLineDTO] = Field(default_factory=list)


class BoMUpdateDTO(BaseModel):
    """Update Bill of Materials."""

    components: list[BoMLineDTO]


class BoMDTO(BaseModel):
    """Bill of Materials response."""

    id: str
    product_id: str
    components: list[BoMLineDTO]
    created_at: datetime
    updated_at: datetime | None


# Search and Query DTOs
class ProductSearchDTO(BaseModel):
    """Product search criteria."""

    category_id: str | None = None
    product_type: ProductType | None = None
    is_active: bool | None = None
    can_be_sold: bool | None = None
    is_stockable: bool | None = None
    search_text: str | None = None


class UnitConversionRequestDTO(BaseModel):
    """Unit conversion request."""

    value: Decimal
    from_uom_code: str
    to_uom_code: str


class UnitConversionResponseDTO(BaseModel):
    """Unit conversion response."""

    original_value: Decimal
    original_uom: str
    converted_value: Decimal
    converted_uom: str


class ProductPriceRequestDTO(BaseModel):
    """Product price request."""

    product_id: str
    uom_id: str
    quantity: Decimal = Field(gt=0)
    price_list_id: str | None = None


class ProductPriceResponseDTO(BaseModel):
    """Product price response."""

    product_id: str
    uom_id: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    currency: str
    price_list_id: str | None


class BoMCostRequestDTO(BaseModel):
    """BoM cost request."""

    product_id: str
    price_list_id: str | None = None


class BoMCostResponseDTO(BaseModel):
    """BoM cost response."""

    product_id: str
    total_cost: Decimal
    currency: str
    price_list_id: str | None
    component_costs: list[dict[str, Decimal]]
