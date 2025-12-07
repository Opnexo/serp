"""
Domain entities for Products module.
"""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from serp_core.domain.entities import AggregateRoot, Entity
from serp_crm.domain.value_objects import Money

from serp_products.domain.value_objects import (
    AttributeDataType,
    AttributeValue,
    Barcode,
    CategoryPath,
    ConversionFactor,
    ProductCode,
    ProductType,
    UoMCategory,
)

if TYPE_CHECKING:
    pass


class UnitOfMeasure(AggregateRoot):
    """Unit of measure aggregate root."""

    def __init__(
        self,
        code: str,
        name: str,
        category: UoMCategory,
        conversion_factor: ConversionFactor = ConversionFactor(Decimal("1")),
        is_base_unit: bool = False,
        symbol: str | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not code or not code.strip():
            raise ValueError("UoM code is required")
        if not name or not name.strip():
            raise ValueError("UoM name is required")

        self.code = code.upper()
        self.name = name
        self.category = category
        self.conversion_factor = conversion_factor
        self.is_base_unit = is_base_unit
        self.symbol = symbol or code

    def convert_to_base(self, value: Decimal) -> Decimal:
        """Convert value to base unit."""
        return self.conversion_factor.convert(value)

    def convert_from_base(self, value: Decimal) -> Decimal:
        """Convert value from base unit."""
        return self.conversion_factor.reverse_convert(value)


class AttributeDefinition(AggregateRoot):
    """Attribute definition aggregate root."""

    def __init__(
        self,
        code: str,
        name: str,
        data_type: AttributeDataType,
        applicable_types: list[ProductType] | None = None,
        default_uom_id: str | None = None,
        is_required: bool = False,
        is_variant_attribute: bool = False,
        description: str | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not code or not code.strip():
            raise ValueError("Attribute code is required")
        if not name or not name.strip():
            raise ValueError("Attribute name is required")

        self.code = code.upper()
        self.name = name
        self.data_type = data_type
        self.applicable_types = applicable_types or list(ProductType)
        self.default_uom_id = default_uom_id
        self.is_required = is_required
        self.is_variant_attribute = is_variant_attribute
        self.description = description

    def is_applicable_to(self, product_type: ProductType) -> bool:
        """Check if attribute applies to product type."""
        return product_type in self.applicable_types


class Category(AggregateRoot):
    """Product category aggregate root."""

    def __init__(
        self,
        code: str,
        name: str,
        parent_id: str | None = None,
        path: CategoryPath | None = None,
        default_attribute_ids: list[str] | None = None,
        description: str | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not code or not code.strip():
            raise ValueError("Category code is required")
        if not name or not name.strip():
            raise ValueError("Category name is required")

        self.code = code.upper()
        self.name = name
        self.parent_id = parent_id
        self.path = path or CategoryPath(f"/{code}")
        self.default_attribute_ids = default_attribute_ids or []
        self.description = description

    def update_path(self, parent_path: CategoryPath | None) -> None:
        """Update category path based on parent."""
        if parent_path:
            self.path = CategoryPath(f"{parent_path.path}/{self.code}")
        else:
            self.path = CategoryPath(f"/{self.code}")


class ProductAttribute(Entity):
    """Product attribute entity (owned by Product)."""

    def __init__(
        self,
        attribute_definition_id: str,
        value: AttributeValue,
        id: str | None = None,
    ):
        super().__init__(id)
        if not attribute_definition_id:
            raise ValueError("Attribute definition is required")

        self.attribute_definition_id = attribute_definition_id
        self.value = value

    def display_value(self) -> str:
        """Get formatted display value."""
        return self.value.display_value()


class ProductUoM(Entity):
    """Product unit of measure entity (owned by Product)."""

    def __init__(
        self,
        uom_id: str,
        conversion_factor: ConversionFactor,
        can_be_sold: bool = True,
        can_be_purchased: bool = True,
        barcode: Barcode | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not uom_id:
            raise ValueError("UoM is required")

        self.uom_id = uom_id
        self.conversion_factor = conversion_factor
        self.can_be_sold = can_be_sold
        self.can_be_purchased = can_be_purchased
        self.barcode = barcode

    def convert_to_base(self, quantity: Decimal) -> Decimal:
        """Convert quantity to base units."""
        return self.conversion_factor.convert(quantity)

    def convert_from_base(self, quantity: Decimal) -> Decimal:
        """Convert quantity from base units."""
        return self.conversion_factor.reverse_convert(quantity)


class Product(AggregateRoot):
    """Product aggregate root."""

    def __init__(
        self,
        code: ProductCode,
        name: str,
        product_type: ProductType,
        base_uom_id: str,
        category_id: str | None = None,
        description: str | None = None,
        is_active: bool = True,
        is_stockable: bool = True,
        can_be_sold: bool = True,
        can_be_purchased: bool = False,
        is_variant: bool = False,
        parent_product_id: str | None = None,
        attributes: list[ProductAttribute] | None = None,
        uoms: list[ProductUoM] | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not name or not name.strip():
            raise ValueError("Product name is required")
        if not base_uom_id:
            raise ValueError("Base UoM is required")
        if product_type == ProductType.SERVICE and is_stockable:
            raise ValueError("Services cannot be stockable")

        self.code = code
        self.name = name
        self.product_type = product_type
        self.base_uom_id = base_uom_id
        self.category_id = category_id
        self.description = description
        self.is_active = is_active
        self.is_stockable = is_stockable
        self.can_be_sold = can_be_sold
        self.can_be_purchased = can_be_purchased
        self.is_variant = is_variant
        self.parent_product_id = parent_product_id
        self.attributes = attributes or []
        self.uoms = uoms or []

    def add_attribute(self, attribute: ProductAttribute) -> None:
        """Add an attribute to the product."""
        # Remove existing attribute with same definition
        self.attributes = [
            a
            for a in self.attributes
            if a.attribute_definition_id != attribute.attribute_definition_id
        ]
        self.attributes.append(attribute)
        self._add_event("ProductUpdated", {"product_id": self.id})

    def remove_attribute(self, attribute_definition_id: str) -> None:
        """Remove an attribute from the product."""
        self.attributes = [
            a
            for a in self.attributes
            if a.attribute_definition_id != attribute_definition_id
        ]
        self._add_event("ProductUpdated", {"product_id": self.id})

    def add_uom(self, product_uom: ProductUoM) -> None:
        """Add a UoM to the product."""
        # Check if UoM already exists
        if any(u.uom_id == product_uom.uom_id for u in self.uoms):
            raise ValueError(f"UoM {product_uom.uom_id} already exists")
        self.uoms.append(product_uom)
        self._add_event("ProductUpdated", {"product_id": self.id})

    def remove_uom(self, uom_id: str) -> None:
        """Remove a UoM from the product."""
        if uom_id == self.base_uom_id:
            raise ValueError("Cannot remove base UoM")
        self.uoms = [u for u in self.uoms if u.uom_id != uom_id]
        self._add_event("ProductUpdated", {"product_id": self.id})

    def get_uom(self, uom_id: str) -> ProductUoM | None:
        """Get product UoM by ID."""
        return next((u for u in self.uoms if u.uom_id == uom_id), None)

    def convert_quantity(
        self, quantity: Decimal, from_uom: str, to_uom: str
    ) -> Decimal:
        """Convert quantity between UoMs."""
        if from_uom == to_uom:
            return quantity

        from_product_uom = self.get_uom(from_uom)
        to_product_uom = self.get_uom(to_uom)

        if not from_product_uom:
            raise ValueError(f"UoM {from_uom} not found")
        if not to_product_uom:
            raise ValueError(f"UoM {to_uom} not found")

        # Convert to base, then to target
        base_quantity = from_product_uom.convert_to_base(quantity)
        return to_product_uom.convert_from_base(base_quantity)

    def activate(self) -> None:
        """Activate the product."""
        if self.is_active:
            raise ValueError("Product is already active")
        self.is_active = True
        self._add_event("ProductActivated", {"product_id": self.id})

    def deactivate(self) -> None:
        """Deactivate the product."""
        if not self.is_active:
            raise ValueError("Product is already inactive")
        self.is_active = False
        self._add_event("ProductDeactivated", {"product_id": self.id})


class PriceRule(Entity):
    """Price rule entity (owned by PriceList)."""

    def __init__(
        self,
        product_id: str,
        uom_id: str,
        unit_price: Money,
        min_quantity: Decimal = Decimal("1"),
        discount_percent: Decimal = Decimal("0"),
        id: str | None = None,
    ):
        super().__init__(id)
        if not product_id:
            raise ValueError("Product is required")
        if not uom_id:
            raise ValueError("UoM is required")
        if unit_price.amount < 0:
            raise ValueError("Unit price cannot be negative")
        if min_quantity <= 0:
            raise ValueError("Minimum quantity must be positive")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100")

        self.product_id = product_id
        self.uom_id = uom_id
        self.unit_price = unit_price
        self.min_quantity = min_quantity
        self.discount_percent = discount_percent

    def get_final_price(self) -> Money:
        """Calculate final price after discount."""
        if self.discount_percent == 0:
            return self.unit_price

        discount_amount = self.unit_price.amount * (
            self.discount_percent / Decimal("100")
        )
        final_amount = self.unit_price.amount - discount_amount
        return Money(final_amount, self.unit_price.currency)


class PriceList(AggregateRoot):
    """Price list aggregate root."""

    def __init__(
        self,
        name: str,
        currency: str,
        is_default: bool = False,
        valid_from: date | None = None,
        valid_to: date | None = None,
        rules: list[PriceRule] | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not name or not name.strip():
            raise ValueError("Price list name is required")
        if not currency:
            raise ValueError("Currency is required")
        if valid_from and valid_to and valid_to < valid_from:
            raise ValueError("Valid to must be after valid from")

        self.name = name
        self.currency = currency
        self.is_default = is_default
        self.valid_from = valid_from or date.today()
        self.valid_to = valid_to
        self.rules = rules or []

    def add_rule(self, rule: PriceRule) -> None:
        """Add a price rule."""
        self.rules.append(rule)
        self._add_event("PriceRuleUpdated", {"price_list_id": self.id})

    def get_price(
        self, product_id: str, uom_id: str, quantity: Decimal
    ) -> Money | None:
        """Get price for product, considering quantity."""
        applicable_rules = [
            r
            for r in self.rules
            if r.product_id == product_id
            and r.uom_id == uom_id
            and r.min_quantity <= quantity
        ]

        if not applicable_rules:
            return None

        # Get rule with highest min_quantity that applies
        best_rule = max(applicable_rules, key=lambda r: r.min_quantity)
        return best_rule.get_final_price()

    def is_valid(self, check_date: date | None = None) -> bool:
        """Check if price list is valid on given date."""
        check_date = check_date or date.today()

        if check_date < self.valid_from:
            return False
        if self.valid_to and check_date > self.valid_to:
            return False
        return True


class BoMLine(Entity):
    """Bill of materials line entity (owned by BillOfMaterials)."""

    def __init__(
        self,
        component_product_id: str,
        quantity: Decimal,
        uom_id: str,
        id: str | None = None,
    ):
        super().__init__(id)
        if not component_product_id:
            raise ValueError("Component product is required")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if not uom_id:
            raise ValueError("UoM is required")

        self.component_product_id = component_product_id
        self.quantity = quantity
        self.uom_id = uom_id


class BillOfMaterials(AggregateRoot):
    """Bill of materials aggregate root."""

    def __init__(
        self,
        product_id: str,
        components: list[BoMLine] | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if not product_id:
            raise ValueError("Product is required")

        self.product_id = product_id
        self.components = components or []

    def add_component(self, component: BoMLine) -> None:
        """Add a component to the BoM."""
        # Check if component already exists
        if any(
            c.component_product_id == component.component_product_id
            for c in self.components
        ):
            raise ValueError("Component already exists in BoM")
        self.components.append(component)
        self._add_event("BillOfMaterialsUpdated", {"bom_id": self.id})

    def remove_component(self, component_product_id: str) -> None:
        """Remove a component from the BoM."""
        self.components = [
            c for c in self.components if c.component_product_id != component_product_id
        ]
        self._add_event("BillOfMaterialsUpdated", {"bom_id": self.id})
