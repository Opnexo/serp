"""
Repository interfaces for Products module.
"""

from abc import abstractmethod
from typing import Protocol

from serp_products.domain.entities import (
    AttributeDefinition,
    BillOfMaterials,
    Category,
    PriceList,
    Product,
    UnitOfMeasure,
)


class IUnitOfMeasureRepository(Protocol):
    """Unit of measure repository interface."""

    @abstractmethod
    def save(self, uom: UnitOfMeasure) -> None:
        """Save a unit of measure."""
        ...

    @abstractmethod
    def get_by_id(self, uom_id: str) -> UnitOfMeasure | None:
        """Get a UoM by ID."""
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> UnitOfMeasure | None:
        """Get a UoM by code."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[UnitOfMeasure]:
        """List all UoMs."""
        ...

    @abstractmethod
    def list_by_category(self, category: str) -> list[UnitOfMeasure]:
        """List UoMs by category."""
        ...

    @abstractmethod
    def delete(self, uom_id: str) -> None:
        """Delete a UoM."""
        ...


class IAttributeDefinitionRepository(Protocol):
    """Attribute definition repository interface."""

    @abstractmethod
    def save(self, attribute: AttributeDefinition) -> None:
        """Save an attribute definition."""
        ...

    @abstractmethod
    def get_by_id(self, attribute_id: str) -> AttributeDefinition | None:
        """Get an attribute by ID."""
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> AttributeDefinition | None:
        """Get an attribute by code."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[AttributeDefinition]:
        """List all attributes."""
        ...

    @abstractmethod
    def delete(self, attribute_id: str) -> None:
        """Delete an attribute."""
        ...


class ICategoryRepository(Protocol):
    """Category repository interface."""

    @abstractmethod
    def save(self, category: Category) -> None:
        """Save a category."""
        ...

    @abstractmethod
    def get_by_id(self, category_id: str) -> Category | None:
        """Get a category by ID."""
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> Category | None:
        """Get a category by code."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Category]:
        """List all categories."""
        ...

    @abstractmethod
    def get_children(self, parent_id: str) -> list[Category]:
        """Get child categories."""
        ...

    @abstractmethod
    def delete(self, category_id: str) -> None:
        """Delete a category."""
        ...


class IProductRepository(Protocol):
    """Product repository interface."""

    @abstractmethod
    def save(self, product: Product) -> None:
        """Save a product."""
        ...

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product | None:
        """Get a product by ID."""
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> Product | None:
        """Get a product by code."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """List all products."""
        ...

    @abstractmethod
    def list_by_category(self, category_id: str) -> list[Product]:
        """List products in a category."""
        ...

    @abstractmethod
    def list_by_type(self, product_type: str) -> list[Product]:
        """List products by type."""
        ...

    @abstractmethod
    def get_variants(self, parent_product_id: str) -> list[Product]:
        """Get product variants."""
        ...

    @abstractmethod
    def delete(self, product_id: str) -> None:
        """Delete a product."""
        ...


class IPriceListRepository(Protocol):
    """Price list repository interface."""

    @abstractmethod
    def save(self, price_list: PriceList) -> None:
        """Save a price list."""
        ...

    @abstractmethod
    def get_by_id(self, price_list_id: str) -> PriceList | None:
        """Get a price list by ID."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[PriceList]:
        """List all price lists."""
        ...

    @abstractmethod
    def get_default(self) -> PriceList | None:
        """Get default price list."""
        ...

    @abstractmethod
    def delete(self, price_list_id: str) -> None:
        """Delete a price list."""
        ...


class IBillOfMaterialsRepository(Protocol):
    """Bill of materials repository interface."""

    @abstractmethod
    def save(self, bom: BillOfMaterials) -> None:
        """Save a BoM."""
        ...

    @abstractmethod
    def get_by_id(self, bom_id: str) -> BillOfMaterials | None:
        """Get a BoM by ID."""
        ...

    @abstractmethod
    def get_by_product(self, product_id: str) -> BillOfMaterials | None:
        """Get BoM for a product."""
        ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[BillOfMaterials]:
        """List all BoMs."""
        ...

    @abstractmethod
    def delete(self, bom_id: str) -> None:
        """Delete a BoM."""
        ...
