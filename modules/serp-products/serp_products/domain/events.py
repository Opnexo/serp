"""
Domain events for Products module.
"""

from serp_core.domain.events import DomainEvent


class UnitOfMeasureCreated(DomainEvent):
    """Unit of measure created event."""

    uom_id: str


class UnitOfMeasureUpdated(DomainEvent):
    """Unit of measure updated event."""

    uom_id: str


class AttributeDefinitionCreated(DomainEvent):
    """Attribute definition created event."""

    attribute_id: str


class AttributeDefinitionUpdated(DomainEvent):
    """Attribute definition updated event."""

    attribute_id: str


class CategoryCreated(DomainEvent):
    """Category created event."""

    category_id: str


class CategoryUpdated(DomainEvent):
    """Category updated event."""

    category_id: str


class ProductCreated(DomainEvent):
    """Product created event."""

    product_id: str


class ProductUpdated(DomainEvent):
    """Product updated event."""

    product_id: str


class ProductDeleted(DomainEvent):
    """Product deleted event."""

    product_id: str


class ProductActivated(DomainEvent):
    """Product activated event."""

    product_id: str


class ProductDeactivated(DomainEvent):
    """Product deactivated event."""

    product_id: str


class PriceListCreated(DomainEvent):
    """Price list created event."""

    price_list_id: str


class PriceListUpdated(DomainEvent):
    """Price list updated event."""

    price_list_id: str


class PriceRuleUpdated(DomainEvent):
    """Price rule updated event."""

    price_list_id: str


class BillOfMaterialsCreated(DomainEvent):
    """Bill of materials created event."""

    bom_id: str


class BillOfMaterialsUpdated(DomainEvent):
    """Bill of materials updated event."""

    bom_id: str
