"""In-memory repository implementations."""

from serp_products.domain.entities import (
    AttributeDefinition,
    BillOfMaterials,
    Category,
    PriceList,
    Product,
    UnitOfMeasure,
)
from serp_products.domain.repositories import (
    IAttributeDefinitionRepository,
    IBillOfMaterialsRepository,
    ICategoryRepository,
    IPriceListRepository,
    IProductRepository,
    IUnitOfMeasureRepository,
)
from serp_products.domain.value_objects import ProductType, UoMCategory


class InMemoryUnitOfMeasureRepository(IUnitOfMeasureRepository):
    """In-memory implementation of UnitOfMeasureRepository."""

    def __init__(self):
        self._storage: dict[str, UnitOfMeasure] = {}

    def add(self, entity: UnitOfMeasure) -> None:
        """Add a new UnitOfMeasure."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> UnitOfMeasure | None:
        """Get UnitOfMeasure by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: UnitOfMeasure) -> None:
        """Update an existing UnitOfMeasure."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a UnitOfMeasure."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[UnitOfMeasure]:
        """List all UnitOfMeasures."""
        return list(self._storage.values())

    def get_by_code(self, code: str) -> UnitOfMeasure | None:
        """Get UnitOfMeasure by code."""
        for uom in self._storage.values():
            if uom.code == code:
                return uom
        return None

    def list_by_category(self, category: UoMCategory) -> list[UnitOfMeasure]:
        """List UnitOfMeasures by category."""
        return [uom for uom in self._storage.values() if uom.category == category]


class InMemoryAttributeDefinitionRepository(IAttributeDefinitionRepository):
    """In-memory implementation of AttributeDefinitionRepository."""

    def __init__(self):
        self._storage: dict[str, AttributeDefinition] = {}

    def add(self, entity: AttributeDefinition) -> None:
        """Add a new AttributeDefinition."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> AttributeDefinition | None:
        """Get AttributeDefinition by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: AttributeDefinition) -> None:
        """Update an existing AttributeDefinition."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove an AttributeDefinition."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[AttributeDefinition]:
        """List all AttributeDefinitions."""
        return list(self._storage.values())

    def get_by_code(self, code: str) -> AttributeDefinition | None:
        """Get AttributeDefinition by code."""
        for attr in self._storage.values():
            if attr.code == code:
                return attr
        return None


class InMemoryCategoryRepository(ICategoryRepository):
    """In-memory implementation of CategoryRepository."""

    def __init__(self):
        self._storage: dict[str, Category] = {}

    def add(self, entity: Category) -> None:
        """Add a new Category."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> Category | None:
        """Get Category by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: Category) -> None:
        """Update an existing Category."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a Category."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[Category]:
        """List all Categories."""
        return list(self._storage.values())

    def get_by_code(self, code: str) -> Category | None:
        """Get Category by code."""
        for cat in self._storage.values():
            if cat.code == code:
                return cat
        return None

    def get_children(self, parent_id: str) -> list[Category]:
        """Get child categories of a parent."""
        return [cat for cat in self._storage.values() if cat.parent_id == parent_id]


class InMemoryProductRepository(IProductRepository):
    """In-memory implementation of ProductRepository."""

    def __init__(self):
        self._storage: dict[str, Product] = {}

    def add(self, entity: Product) -> None:
        """Add a new Product."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> Product | None:
        """Get Product by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: Product) -> None:
        """Update an existing Product."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a Product."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[Product]:
        """List all Products."""
        return list(self._storage.values())

    def get_by_code(self, code: str) -> Product | None:
        """Get Product by code."""
        for product in self._storage.values():
            if product.code.value == code:
                return product
        return None

    def list_by_category(self, category_id: str) -> list[Product]:
        """List products in a category."""
        return [p for p in self._storage.values() if p.category_id == category_id]

    def list_by_type(self, product_type: ProductType) -> list[Product]:
        """List products by type."""
        return [p for p in self._storage.values() if p.product_type == product_type]

    def get_variants(self, parent_product_id: str) -> list[Product]:
        """Get all variants of a product."""
        return [
            p
            for p in self._storage.values()
            if p.parent_product_id == parent_product_id
        ]


class InMemoryPriceListRepository(IPriceListRepository):
    """In-memory implementation of PriceListRepository."""

    def __init__(self):
        self._storage: dict[str, PriceList] = {}

    def add(self, entity: PriceList) -> None:
        """Add a new PriceList."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> PriceList | None:
        """Get PriceList by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: PriceList) -> None:
        """Update an existing PriceList."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a PriceList."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[PriceList]:
        """List all PriceLists."""
        return list(self._storage.values())

    def get_default(self) -> PriceList | None:
        """Get the default price list."""
        for pl in self._storage.values():
            if pl.is_default:
                return pl
        return None


class InMemoryBillOfMaterialsRepository(IBillOfMaterialsRepository):
    """In-memory implementation of BillOfMaterialsRepository."""

    def __init__(self):
        self._storage: dict[str, BillOfMaterials] = {}

    def add(self, entity: BillOfMaterials) -> None:
        """Add a new BillOfMaterials."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> BillOfMaterials | None:
        """Get BillOfMaterials by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: BillOfMaterials) -> None:
        """Update an existing BillOfMaterials."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a BillOfMaterials."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[BillOfMaterials]:
        """List all BillOfMaterials."""
        return list(self._storage.values())

    def get_by_product(self, product_id: str) -> BillOfMaterials | None:
        """Get BillOfMaterials for a product."""
        for bom in self._storage.values():
            if bom.product_id == product_id:
                return bom
        return None
