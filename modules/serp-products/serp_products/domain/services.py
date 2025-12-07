"""
Domain services for Products module.
"""

from decimal import Decimal

from serp_products.domain.entities import (
    Product,
)
from serp_products.domain.repositories import (
    IBillOfMaterialsRepository,
    IPriceListRepository,
    IProductRepository,
    IUnitOfMeasureRepository,
)
from serp_products.domain.value_objects import ProductType


class UnitConverter:
    """Service for converting between compatible units of measure."""

    def __init__(self, uom_repository: IUnitOfMeasureRepository):
        self._repository = uom_repository

    def convert(self, value: Decimal, from_uom_code: str, to_uom_code: str) -> Decimal:
        """Convert value between compatible UoMs."""
        if from_uom_code == to_uom_code:
            return value

        from_uom = self._repository.get_by_code(from_uom_code)
        to_uom = self._repository.get_by_code(to_uom_code)

        if not from_uom:
            raise ValueError(f"UoM {from_uom_code} not found")
        if not to_uom:
            raise ValueError(f"UoM {to_uom_code} not found")

        if from_uom.category != to_uom.category:
            raise ValueError(
                f"Cannot convert between {from_uom.category} and {to_uom.category}"
            )

        # Convert to base unit, then to target unit
        base_value = from_uom.convert_to_base(value)
        return to_uom.convert_from_base(base_value)


class ProductVariantGenerator:
    """Service for generating product variants."""

    def __init__(self, product_repository: IProductRepository):
        self._repository = product_repository

    def generate_variants(
        self, parent_product: Product, variant_combinations: list[dict[str, str]]
    ) -> list[Product]:
        """Generate product variants from combinations.

        Example:
        variant_combinations = [
            {"Color": "Blue", "Size": "Small"},
            {"Color": "Blue", "Size": "Large"},
            {"Color": "Red", "Size": "Small"},
        ]
        """
        variants = []

        for combination in variant_combinations:
            # Generate variant code
            variant_code_suffix = "-".join(v[:2].upper() for v in combination.values())
            variant_code = f"{parent_product.code.value}-{variant_code_suffix}"

            # Generate variant name
            variant_name_suffix = ", ".join(f"{k}: {v}" for k, v in combination.items())
            variant_name = f"{parent_product.name} ({variant_name_suffix})"

            # Create variant (would need attribute handling)
            # This is simplified - full implementation would handle attributes properly
            variants.append(
                {
                    "code": variant_code,
                    "name": variant_name,
                    "attributes": combination,
                }
            )

        return variants


class PriceCalculator:
    """Service for calculating product prices."""

    def __init__(
        self,
        price_list_repository: IPriceListRepository,
        product_repository: IProductRepository,
    ):
        self._price_list_repository = price_list_repository
        self._product_repository = product_repository

    def get_product_price(
        self,
        product_id: str,
        uom_id: str,
        quantity: Decimal,
        price_list_id: str | None = None,
    ) -> Decimal | None:
        """Get product price considering quantity breaks."""
        # Get price list
        if price_list_id:
            price_list = self._price_list_repository.get_by_id(price_list_id)
        else:
            price_list = self._price_list_repository.get_default()

        if not price_list or not price_list.is_valid():
            return None

        # Get price from price list
        money = price_list.get_price(product_id, uom_id, quantity)
        return money.amount if money else None

    def calculate_line_total(
        self,
        product_id: str,
        uom_id: str,
        quantity: Decimal,
        price_list_id: str | None = None,
    ) -> Decimal:
        """Calculate total price for quantity."""
        unit_price = self.get_product_price(product_id, uom_id, quantity, price_list_id)

        if unit_price is None:
            raise ValueError("No price found for product")

        return unit_price * quantity


class BoMCostCalculator:
    """Service for calculating bill of materials costs."""

    def __init__(
        self,
        bom_repository: IBillOfMaterialsRepository,
        price_calculator: PriceCalculator,
    ):
        self._repository = bom_repository
        self._price_calculator = price_calculator

    def calculate_bom_cost(
        self, product_id: str, price_list_id: str | None = None
    ) -> Decimal:
        """Calculate total cost of BoM components."""
        bom = self._repository.get_by_product(product_id)
        if not bom:
            raise ValueError(f"No BoM found for product {product_id}")

        total_cost = Decimal("0")

        for component in bom.components:
            component_cost = self._price_calculator.calculate_line_total(
                component.component_product_id,
                component.uom_id,
                component.quantity,
                price_list_id,
            )
            total_cost += component_cost

        return total_cost


class ProductSearchService:
    """Service for advanced product searching."""

    def __init__(self, product_repository: IProductRepository):
        self._repository = product_repository

    def search_products(
        self,
        category_id: str | None = None,
        product_type: ProductType | None = None,
        is_active: bool | None = None,
        can_be_sold: bool | None = None,
        is_stockable: bool | None = None,
    ) -> list[Product]:
        """Search products with filters."""
        if category_id:
            products = self._repository.list_by_category(category_id)
        else:
            products = self._repository.list_all()

        # Apply filters
        if product_type is not None:
            products = [p for p in products if p.product_type == product_type]
        if is_active is not None:
            products = [p for p in products if p.is_active == is_active]
        if can_be_sold is not None:
            products = [p for p in products if p.can_be_sold == can_be_sold]
        if is_stockable is not None:
            products = [p for p in products if p.is_stockable == is_stockable]

        return products
