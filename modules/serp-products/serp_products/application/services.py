"""Application services for Products module."""

from typing import Any

from serp_core.application.events import EventBus
from serp_crm.domain import Money

from serp_products.application.dto import (
    BoMCostRequestDTO,
    BoMCostResponseDTO,
    BoMCreateDTO,
    BoMDTO,
    BoMLineDTO,
    BoMUpdateDTO,
    CategoryCreateDTO,
    CategoryDTO,
    CategoryUpdateDTO,
    PriceListCreateDTO,
    PriceListDTO,
    PriceListUpdateDTO,
    PriceRuleDTO,
    ProductCreateDTO,
    ProductDTO,
    ProductPriceRequestDTO,
    ProductPriceResponseDTO,
    ProductSearchDTO,
    ProductUpdateDTO,
    UnitConversionRequestDTO,
    UnitConversionResponseDTO,
    UoMCreateDTO,
    UoMDTO,
    UoMUpdateDTO,
)
from serp_products.domain.entities import (
    BillOfMaterials,
    BoMLine,
    Category,
    PriceList,
    PriceRule,
    Product,
    ProductAttribute,
    ProductUoM,
    UnitOfMeasure,
)
from serp_products.domain.events import (
    BillOfMaterialsCreated,
    BillOfMaterialsUpdated,
    CategoryCreated,
    CategoryUpdated,
    PriceListCreated,
    PriceListUpdated,
    ProductActivated,
    ProductCreated,
    ProductDeactivated,
    ProductDeleted,
    ProductUpdated,
    UnitOfMeasureCreated,
    UnitOfMeasureUpdated,
)
from serp_products.domain.repositories import (
    IBillOfMaterialsRepository,
    ICategoryRepository,
    IPriceListRepository,
    IProductRepository,
    IUnitOfMeasureRepository,
)
from serp_products.domain.services import (
    BoMCostCalculator,
    PriceCalculator,
    ProductSearchService,
    UnitConverter,
)
from serp_products.domain.value_objects import (
    AttributeValue,
    Barcode,
    CategoryPath,
    ConversionFactor,
    ProductCode,
)


class UnitOfMeasureService:
    """Application service for Unit of Measure operations."""

    def __init__(self, repository: IUnitOfMeasureRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus
        self._converter = UnitConverter(repository)

    def create_uom(self, dto: UoMCreateDTO) -> UoMDTO:
        """Create a new unit of measure."""
        # Check for duplicate code
        existing = self._repository.get_by_code(dto.code)
        if existing:
            raise ValueError(f"UoM with code {dto.code} already exists")

        # Create entity
        uom = UnitOfMeasure.create(
            code=dto.code,
            name=dto.name,
            category=dto.category,
            conversion_factor=ConversionFactor(dto.conversion_factor),
            is_base_unit=dto.is_base_unit,
            symbol=dto.symbol,
        )

        # Save and publish event
        self._repository.add(uom)
        self._event_bus.publish(UnitOfMeasureCreated(aggregate_id=uom.id))

        return self._map_to_dto(uom)

    def update_uom(self, uom_id: str, dto: UoMUpdateDTO) -> UoMDTO:
        """Update unit of measure."""
        uom = self._repository.get_by_id(uom_id)
        if not uom:
            raise ValueError(f"UoM {uom_id} not found")

        if dto.name is not None:
            uom.name = dto.name
        if dto.symbol is not None:
            uom.symbol = dto.symbol

        self._repository.update(uom)
        self._event_bus.publish(UnitOfMeasureUpdated(aggregate_id=uom.id))

        return self._map_to_dto(uom)

    def get_uom(self, uom_id: str) -> UoMDTO | None:
        """Get unit of measure by ID."""
        uom = self._repository.get_by_id(uom_id)
        return self._map_to_dto(uom) if uom else None

    def list_uoms(self, category: str | None = None) -> list[UoMDTO]:
        """List all units of measure."""
        if category:
            from serp_products.domain.value_objects import UoMCategory

            uoms = self._repository.list_by_category(UoMCategory(category))
        else:
            uoms = self._repository.list_all()

        return [self._map_to_dto(uom) for uom in uoms]

    def convert_units(self, dto: UnitConversionRequestDTO) -> UnitConversionResponseDTO:
        """Convert between units."""
        converted_value = self._converter.convert(
            dto.value, dto.from_uom_code, dto.to_uom_code
        )

        return UnitConversionResponseDTO(
            original_value=dto.value,
            original_uom=dto.from_uom_code,
            converted_value=converted_value,
            converted_uom=dto.to_uom_code,
        )

    def _map_to_dto(self, uom: UnitOfMeasure) -> UoMDTO:
        """Map entity to DTO."""
        return UoMDTO(
            id=uom.id,
            code=uom.code,
            name=uom.name,
            category=uom.category,
            conversion_factor=uom.conversion_factor.factor,
            is_base_unit=uom.is_base_unit,
            symbol=uom.symbol,
            created_at=uom.created_at,
            updated_at=uom.updated_at,
        )


class CategoryService:
    """Application service for Category operations."""

    def __init__(self, repository: ICategoryRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus

    def create_category(self, dto: CategoryCreateDTO) -> CategoryDTO:
        """Create a new category."""
        existing = self._repository.get_by_code(dto.code)
        if existing:
            raise ValueError(f"Category with code {dto.code} already exists")

        # Calculate path
        path = CategoryPath(f"/{dto.code}")
        if dto.parent_id:
            parent = self._repository.get_by_id(dto.parent_id)
            if not parent:
                raise ValueError(f"Parent category {dto.parent_id} not found")
            path = CategoryPath(f"{parent.path.path}/{dto.code}")

        category = Category.create(
            code=dto.code,
            name=dto.name,
            parent_id=dto.parent_id,
            path=path,
            default_attribute_ids=dto.default_attribute_ids,
        )

        self._repository.add(category)
        self._event_bus.publish(CategoryCreated(aggregate_id=category.id))

        return self._map_to_dto(category)

    def update_category(self, category_id: str, dto: CategoryUpdateDTO) -> CategoryDTO:
        """Update category."""
        category = self._repository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")

        if dto.name is not None:
            category.name = dto.name
        if dto.parent_id is not None:
            category.parent_id = dto.parent_id
            # Recalculate path
            if dto.parent_id:
                parent = self._repository.get_by_id(dto.parent_id)
                if parent:
                    new_path = CategoryPath(f"{parent.path.path}/{category.code}")
                    category.update_path(new_path)
        if dto.default_attribute_ids is not None:
            category.default_attribute_ids = dto.default_attribute_ids

        self._repository.update(category)
        self._event_bus.publish(CategoryUpdated(aggregate_id=category.id))

        return self._map_to_dto(category)

    def get_category(self, category_id: str) -> CategoryDTO | None:
        """Get category by ID."""
        category = self._repository.get_by_id(category_id)
        return self._map_to_dto(category) if category else None

    def list_categories(self, parent_id: str | None = None) -> list[CategoryDTO]:
        """List categories."""
        if parent_id:
            categories = self._repository.get_children(parent_id)
        else:
            categories = self._repository.list_all()

        return [self._map_to_dto(cat) for cat in categories]

    def _map_to_dto(self, category: Category) -> CategoryDTO:
        """Map entity to DTO."""
        return CategoryDTO(
            id=category.id,
            code=category.code,
            name=category.name,
            parent_id=category.parent_id,
            path=category.path.path,
            default_attribute_ids=category.default_attribute_ids,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )


class ProductService:
    """Application service for Product operations."""

    def __init__(self, repository: IProductRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus
        self._search_service = ProductSearchService(repository)

    def create_product(self, dto: ProductCreateDTO) -> ProductDTO:
        """Create a new product."""
        existing = self._repository.get_by_code(dto.code)
        if existing:
            raise ValueError(f"Product with code {dto.code} already exists")

        # Create product
        product = Product.create(
            code=ProductCode(dto.code),
            name=dto.name,
            product_type=dto.product_type,
            base_uom_id=dto.base_uom_id,
            category_id=dto.category_id,
            is_active=dto.is_active,
            is_stockable=dto.is_stockable,
            can_be_sold=dto.can_be_sold,
            can_be_purchased=dto.can_be_purchased,
            is_variant=dto.is_variant,
            parent_product_id=dto.parent_product_id,
        )

        # Add attributes
        for attr_dto in dto.attributes:
            value = self._create_attribute_value(attr_dto.value)
            attribute = ProductAttribute(
                attribute_definition_id=attr_dto.attribute_definition_id,
                value=value,
            )
            product.add_attribute(attribute)

        # Add UoMs
        for uom_dto in dto.uoms:
            product_uom = ProductUoM(
                uom_id=uom_dto.uom_id,
                conversion_factor=ConversionFactor(uom_dto.conversion_factor),
                can_be_sold=uom_dto.can_be_sold,
                can_be_purchased=uom_dto.can_be_purchased,
                barcode=(Barcode(uom_dto.barcode) if uom_dto.barcode else None),
            )
            product.add_uom(product_uom)

        self._repository.add(product)
        self._event_bus.publish(ProductCreated(aggregate_id=product.id))

        return self._map_to_dto(product)

    def update_product(self, product_id: str, dto: ProductUpdateDTO) -> ProductDTO:
        """Update product."""
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if dto.name is not None:
            product.name = dto.name
        if dto.category_id is not None:
            product.category_id = dto.category_id
        if dto.is_active is not None:
            if dto.is_active and not product.is_active:
                product.activate()
            elif not dto.is_active and product.is_active:
                product.deactivate()
        if dto.can_be_sold is not None:
            product.can_be_sold = dto.can_be_sold
        if dto.can_be_purchased is not None:
            product.can_be_purchased = dto.can_be_purchased

        self._repository.update(product)
        self._event_bus.publish(ProductUpdated(aggregate_id=product.id))

        return self._map_to_dto(product)

    def delete_product(self, product_id: str) -> None:
        """Delete product."""
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        self._repository.remove(product_id)
        self._event_bus.publish(ProductDeleted(aggregate_id=product_id))

    def activate_product(self, product_id: str) -> ProductDTO:
        """Activate product."""
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        product.activate()
        self._repository.update(product)
        self._event_bus.publish(ProductActivated(aggregate_id=product.id))

        return self._map_to_dto(product)

    def deactivate_product(self, product_id: str) -> ProductDTO:
        """Deactivate product."""
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        product.deactivate()
        self._repository.update(product)
        self._event_bus.publish(ProductDeactivated(aggregate_id=product.id))

        return self._map_to_dto(product)

    def get_product(self, product_id: str) -> ProductDTO | None:
        """Get product by ID."""
        product = self._repository.get_by_id(product_id)
        return self._map_to_dto(product) if product else None

    def search_products(self, dto: ProductSearchDTO) -> list[ProductDTO]:
        """Search products."""
        products = self._search_service.search_products(
            category_id=dto.category_id,
            product_type=dto.product_type,
            is_active=dto.is_active,
            can_be_sold=dto.can_be_sold,
            is_stockable=dto.is_stockable,
        )

        return [self._map_to_dto(p) for p in products]

    def _create_attribute_value(self, value_dto: Any) -> AttributeValue:
        """Create attribute value from DTO."""
        if value_dto.text_value is not None:
            return AttributeValue.from_text(value_dto.text_value)
        elif value_dto.numeric_value is not None:
            return AttributeValue.from_numeric(
                value_dto.numeric_value, value_dto.uom_id
            )
        elif value_dto.boolean_value is not None:
            return AttributeValue.from_boolean(value_dto.boolean_value)
        elif value_dto.date_value is not None:
            return AttributeValue.from_date(value_dto.date_value)
        elif value_dto.reference_id is not None:
            return AttributeValue.from_reference(value_dto.reference_id)
        else:
            raise ValueError("Invalid attribute value")

    def _map_to_dto(self, product: Product) -> ProductDTO:
        """Map entity to DTO."""
        from serp_products.application.dto import (
            ProductAttributeDTO,
            ProductUoMDTO,
        )

        return ProductDTO(
            id=product.id,
            code=product.code.value,
            name=product.name,
            product_type=product.product_type,
            base_uom_id=product.base_uom_id,
            category_id=product.category_id,
            is_active=product.is_active,
            is_stockable=product.is_stockable,
            can_be_sold=product.can_be_sold,
            can_be_purchased=product.can_be_purchased,
            is_variant=product.is_variant,
            parent_product_id=product.parent_product_id,
            attributes=[
                ProductAttributeDTO(
                    attribute_definition_id=attr.attribute_definition_id,
                    value=self._map_attribute_value_to_dto(attr.value),
                )
                for attr in product.attributes
            ],
            uoms=[
                ProductUoMDTO(
                    uom_id=uom.uom_id,
                    conversion_factor=uom.conversion_factor.factor,
                    can_be_sold=uom.can_be_sold,
                    can_be_purchased=uom.can_be_purchased,
                    barcode=uom.barcode.code if uom.barcode else None,
                )
                for uom in product.uoms
            ],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def _map_attribute_value_to_dto(self, value: AttributeValue) -> "AttributeValueDTO":
        """Map attribute value to DTO."""
        from serp_products.application.dto import AttributeValueDTO

        return AttributeValueDTO(
            text_value=value.text_value,
            numeric_value=value.numeric_value,
            boolean_value=value.boolean_value,
            date_value=value.date_value,
            reference_id=value.reference_id,
            uom_id=value.uom_id,
        )


class PriceListService:
    """Application service for Price List operations."""

    def __init__(
        self,
        repository: IPriceListRepository,
        product_repository: IProductRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._product_repository = product_repository
        self._event_bus = event_bus
        self._calculator = PriceCalculator(repository, product_repository)

    def create_price_list(self, dto: PriceListCreateDTO) -> PriceListDTO:
        """Create a new price list."""
        price_list = PriceList.create(
            name=dto.name,
            currency=dto.currency,
            is_default=dto.is_default,
            valid_from=dto.valid_from,
            valid_to=dto.valid_to,
        )

        # Add rules
        for rule_dto in dto.rules:
            rule = PriceRule(
                product_id=rule_dto.product_id,
                uom_id=rule_dto.uom_id,
                unit_price=Money(rule_dto.unit_price, rule_dto.currency),
                min_quantity=rule_dto.min_quantity,
                discount_percent=rule_dto.discount_percent,
            )
            price_list.add_rule(rule)

        self._repository.add(price_list)
        self._event_bus.publish(PriceListCreated(aggregate_id=price_list.id))

        return self._map_to_dto(price_list)

    def update_price_list(
        self, price_list_id: str, dto: PriceListUpdateDTO
    ) -> PriceListDTO:
        """Update price list."""
        price_list = self._repository.get_by_id(price_list_id)
        if not price_list:
            raise ValueError(f"Price list {price_list_id} not found")

        if dto.name is not None:
            price_list.name = dto.name
        if dto.is_default is not None:
            price_list.is_default = dto.is_default
        if dto.valid_from is not None:
            price_list.valid_from = dto.valid_from
        if dto.valid_to is not None:
            price_list.valid_to = dto.valid_to

        self._repository.update(price_list)
        self._event_bus.publish(PriceListUpdated(aggregate_id=price_list.id))

        return self._map_to_dto(price_list)

    def get_price_list(self, price_list_id: str) -> PriceListDTO | None:
        """Get price list by ID."""
        price_list = self._repository.get_by_id(price_list_id)
        return self._map_to_dto(price_list) if price_list else None

    def list_price_lists(self) -> list[PriceListDTO]:
        """List all price lists."""
        price_lists = self._repository.list_all()
        return [self._map_to_dto(pl) for pl in price_lists]

    def get_product_price(self, dto: ProductPriceRequestDTO) -> ProductPriceResponseDTO:
        """Get product price."""
        unit_price = self._calculator.get_product_price(
            dto.product_id, dto.uom_id, dto.quantity, dto.price_list_id
        )

        if unit_price is None:
            raise ValueError("No price found for product")

        total_price = unit_price * dto.quantity

        # Get currency from price list
        if dto.price_list_id:
            price_list = self._repository.get_by_id(dto.price_list_id)
        else:
            price_list = self._repository.get_default()

        currency = price_list.currency if price_list else "USD"

        return ProductPriceResponseDTO(
            product_id=dto.product_id,
            uom_id=dto.uom_id,
            quantity=dto.quantity,
            unit_price=unit_price,
            total_price=total_price,
            currency=currency,
            price_list_id=dto.price_list_id,
        )

    def _map_to_dto(self, price_list: PriceList) -> PriceListDTO:
        """Map entity to DTO."""
        return PriceListDTO(
            id=price_list.id,
            name=price_list.name,
            currency=price_list.currency,
            is_default=price_list.is_default,
            valid_from=price_list.valid_from,
            valid_to=price_list.valid_to,
            rules=[
                PriceRuleDTO(
                    product_id=rule.product_id,
                    uom_id=rule.uom_id,
                    unit_price=rule.unit_price.amount,
                    currency=rule.unit_price.currency,
                    min_quantity=rule.min_quantity,
                    discount_percent=rule.discount_percent,
                )
                for rule in price_list.rules
            ],
            created_at=price_list.created_at,
            updated_at=price_list.updated_at,
        )


class BillOfMaterialsService:
    """Application service for Bill of Materials operations."""

    def __init__(
        self,
        repository: IBillOfMaterialsRepository,
        price_list_repository: IPriceListRepository,
        product_repository: IProductRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._event_bus = event_bus
        self._calculator = BoMCostCalculator(
            repository,
            PriceCalculator(price_list_repository, product_repository),
        )

    def create_bom(self, dto: BoMCreateDTO) -> BoMDTO:
        """Create a new bill of materials."""
        existing = self._repository.get_by_product(dto.product_id)
        if existing:
            raise ValueError(f"BoM for product {dto.product_id} already exists")

        bom = BillOfMaterials.create(product_id=dto.product_id)

        for line_dto in dto.components:
            line = BoMLine(
                component_product_id=line_dto.component_product_id,
                quantity=line_dto.quantity,
                uom_id=line_dto.uom_id,
            )
            bom.add_component(line)

        self._repository.add(bom)
        self._event_bus.publish(BillOfMaterialsCreated(aggregate_id=bom.id))

        return self._map_to_dto(bom)

    def update_bom(self, bom_id: str, dto: BoMUpdateDTO) -> BoMDTO:
        """Update bill of materials."""
        bom = self._repository.get_by_id(bom_id)
        if not bom:
            raise ValueError(f"BoM {bom_id} not found")

        # Replace all components
        bom.components = []
        for line_dto in dto.components:
            line = BoMLine(
                component_product_id=line_dto.component_product_id,
                quantity=line_dto.quantity,
                uom_id=line_dto.uom_id,
            )
            bom.add_component(line)

        self._repository.update(bom)
        self._event_bus.publish(BillOfMaterialsUpdated(aggregate_id=bom.id))

        return self._map_to_dto(bom)

    def get_bom(self, bom_id: str) -> BoMDTO | None:
        """Get bill of materials by ID."""
        bom = self._repository.get_by_id(bom_id)
        return self._map_to_dto(bom) if bom else None

    def get_bom_by_product(self, product_id: str) -> BoMDTO | None:
        """Get bill of materials for a product."""
        bom = self._repository.get_by_product(product_id)
        return self._map_to_dto(bom) if bom else None

    def calculate_bom_cost(self, dto: BoMCostRequestDTO) -> BoMCostResponseDTO:
        """Calculate bill of materials cost."""
        total_cost = self._calculator.calculate_bom_cost(
            dto.product_id, dto.price_list_id
        )

        # Get currency from price list
        if dto.price_list_id:
            # Would need price list repository injected
            currency = "USD"  # Simplified
        else:
            currency = "USD"

        return BoMCostResponseDTO(
            product_id=dto.product_id,
            total_cost=total_cost,
            currency=currency,
            price_list_id=dto.price_list_id,
            component_costs=[],  # Could be enhanced to return breakdown
        )

    def _map_to_dto(self, bom: BillOfMaterials) -> BoMDTO:
        """Map entity to DTO."""
        return BoMDTO(
            id=bom.id,
            product_id=bom.product_id,
            components=[
                BoMLineDTO(
                    component_product_id=line.component_product_id,
                    quantity=line.quantity,
                    uom_id=line.uom_id,
                )
                for line in bom.components
            ],
            created_at=bom.created_at,
            updated_at=bom.updated_at,
        )
