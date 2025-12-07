"""REST API routes for Products module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from serp_products.application import (
    BillOfMaterialsService,
    BoMCostRequestDTO,
    BoMCostResponseDTO,
    BoMCreateDTO,
    BoMDTO,
    BoMUpdateDTO,
    CategoryCreateDTO,
    CategoryDTO,
    CategoryUpdateDTO,
    PriceListCreateDTO,
    PriceListDTO,
    PriceListUpdateDTO,
    ProductCreateDTO,
    ProductDTO,
    ProductPriceRequestDTO,
    ProductPriceResponseDTO,
    ProductSearchDTO,
    ProductService,
    ProductUpdateDTO,
    UnitConversionRequestDTO,
    UnitConversionResponseDTO,
    UnitOfMeasureService,
    UoMCreateDTO,
    UoMDTO,
    UoMUpdateDTO,
)

# These would be injected from serp_shell
CategoryServiceDep = Annotated["CategoryService", Depends(lambda: None)]  # Placeholder
UoMServiceDep = Annotated["UnitOfMeasureService", Depends(lambda: None)]  # Placeholder
ProductServiceDep = Annotated["ProductService", Depends(lambda: None)]  # Placeholder
PriceListServiceDep = Annotated[
    "PriceListService", Depends(lambda: None)
]  # Placeholder
BoMServiceDep = Annotated[
    "BillOfMaterialsService", Depends(lambda: None)
]  # Placeholder

# Router setup
router = APIRouter(prefix="/api/v1/products", tags=["products"])


# UoM Routes
@router.post(
    "/uoms",
    response_model=UoMDTO,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permission(PERMISSION_UOM_CREATE))],
)
async def create_uom(dto: UoMCreateDTO, service: UoMServiceDep) -> UoMDTO:
    """Create a new unit of measure."""
    try:
        return service.create_uom(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/uoms/{uom_id}",
    response_model=UoMDTO,
    # dependencies=[Depends(require_permission(PERMISSION_UOM_READ))],
)
async def get_uom(uom_id: str, service: UoMServiceDep) -> UoMDTO:
    """Get unit of measure by ID."""
    uom = service.get_uom(uom_id)
    if not uom:
        raise HTTPException(status_code=404, detail="UoM not found")
    return uom


@router.put(
    "/uoms/{uom_id}",
    response_model=UoMDTO,
    # dependencies=[Depends(require_permission(PERMISSION_UOM_UPDATE))],
)
async def update_uom(uom_id: str, dto: UoMUpdateDTO, service: UoMServiceDep) -> UoMDTO:
    """Update unit of measure."""
    try:
        return service.update_uom(uom_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/uoms",
    response_model=list[UoMDTO],
    # dependencies=[Depends(require_permission(PERMISSION_UOM_LIST))],
)
async def list_uoms(
    category: str | None = None, service: UoMServiceDep = None
) -> list[UoMDTO]:
    """List all units of measure."""
    return service.list_uoms(category)


@router.post(
    "/uoms/convert",
    response_model=UnitConversionResponseDTO,
    # dependencies=[Depends(require_permission(PERMISSION_UNIT_CONVERT))],
)
async def convert_units(
    dto: UnitConversionRequestDTO, service: UoMServiceDep
) -> UnitConversionResponseDTO:
    """Convert between units."""
    try:
        return service.convert_units(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Category Routes
@router.post(
    "/categories",
    response_model=CategoryDTO,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permission(PERMISSION_CATEGORY_CREATE))],
)
async def create_category(
    dto: CategoryCreateDTO, service: CategoryServiceDep
) -> CategoryDTO:
    """Create a new category."""
    try:
        return service.create_category(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories/{category_id}",
    response_model=CategoryDTO,
    # dependencies=[Depends(require_permission(PERMISSION_CATEGORY_READ))],
)
async def get_category(category_id: str, service: CategoryServiceDep) -> CategoryDTO:
    """Get category by ID."""
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put(
    "/categories/{category_id}",
    response_model=CategoryDTO,
    # dependencies=[Depends(require_permission(PERMISSION_CATEGORY_UPDATE))],
)
async def update_category(
    category_id: str, dto: CategoryUpdateDTO, service: CategoryServiceDep
) -> CategoryDTO:
    """Update category."""
    try:
        return service.update_category(category_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories",
    response_model=list[CategoryDTO],
    # dependencies=[Depends(require_permission(PERMISSION_CATEGORY_LIST))],
)
async def list_categories(
    parent_id: str | None = None, service: CategoryServiceDep = None
) -> list[CategoryDTO]:
    """List categories."""
    return service.list_categories(parent_id)


# Product Routes
@router.post(
    "/",
    response_model=ProductDTO,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_CREATE))],
)
async def create_product(
    dto: ProductCreateDTO, service: ProductServiceDep
) -> ProductDTO:
    """Create a new product."""
    try:
        return service.create_product(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{product_id}",
    response_model=ProductDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_READ))],
)
async def get_product(product_id: str, service: ProductServiceDep) -> ProductDTO:
    """Get product by ID."""
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put(
    "/{product_id}",
    response_model=ProductDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_UPDATE))],
)
async def update_product(
    product_id: str, dto: ProductUpdateDTO, service: ProductServiceDep
) -> ProductDTO:
    """Update product."""
    try:
        return service.update_product(product_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_DELETE))],
)
async def delete_product(product_id: str, service: ProductServiceDep) -> None:
    """Delete product."""
    try:
        service.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{product_id}/activate",
    response_model=ProductDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_ACTIVATE))],
)
async def activate_product(product_id: str, service: ProductServiceDep) -> ProductDTO:
    """Activate product."""
    try:
        return service.activate_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{product_id}/deactivate",
    response_model=ProductDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_DEACTIVATE))],
)
async def deactivate_product(product_id: str, service: ProductServiceDep) -> ProductDTO:
    """Deactivate product."""
    try:
        return service.deactivate_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/search",
    response_model=list[ProductDTO],
    # dependencies=[Depends(require_permission(PERMISSION_PRODUCT_SEARCH))],
)
async def search_products(
    dto: ProductSearchDTO, service: ProductServiceDep
) -> list[ProductDTO]:
    """Search products."""
    return service.search_products(dto)


# Price List Routes
@router.post(
    "/pricelists",
    response_model=PriceListDTO,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permission(PERMISSION_PRICELIST_CREATE))],
)
async def create_pricelist(
    dto: PriceListCreateDTO, service: PriceListServiceDep
) -> PriceListDTO:
    """Create price list."""
    try:
        return service.create_price_list(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/pricelists/{pricelist_id}",
    response_model=PriceListDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRICELIST_READ))],
)
async def get_pricelist(
    pricelist_id: str, service: PriceListServiceDep
) -> PriceListDTO:
    """Get price list."""
    pricelist = service.get_price_list(pricelist_id)
    if not pricelist:
        raise HTTPException(status_code=404, detail="Price list not found")
    return pricelist


@router.put(
    "/pricelists/{pricelist_id}",
    response_model=PriceListDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRICELIST_UPDATE))],
)
async def update_pricelist(
    pricelist_id: str,
    dto: PriceListUpdateDTO,
    service: PriceListServiceDep,
) -> PriceListDTO:
    """Update price list."""
    try:
        return service.update_price_list(pricelist_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/pricelists",
    response_model=list[PriceListDTO],
    # dependencies=[Depends(require_permission(PERMISSION_PRICELIST_LIST))],
)
async def list_pricelists(
    service: PriceListServiceDep,
) -> list[PriceListDTO]:
    """List price lists."""
    return service.list_price_lists()


@router.post(
    "/price",
    response_model=ProductPriceResponseDTO,
    # dependencies=[Depends(require_permission(PERMISSION_PRICE_GET))],
)
async def get_price(
    dto: ProductPriceRequestDTO, service: PriceListServiceDep
) -> ProductPriceResponseDTO:
    """Get product price."""
    try:
        return service.get_product_price(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# BoM Routes
@router.post(
    "/bom",
    response_model=BoMDTO,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permission(PERMISSION_BOM_CREATE))],
)
async def create_bom(dto: BoMCreateDTO, service: BoMServiceDep) -> BoMDTO:
    """Create bill of materials."""
    try:
        return service.create_bom(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/bom/{bom_id}",
    response_model=BoMDTO,
    # dependencies=[Depends(require_permission(PERMISSION_BOM_READ))],
)
async def get_bom(bom_id: str, service: BoMServiceDep) -> BoMDTO:
    """Get bill of materials."""
    bom = service.get_bom(bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BoM not found")
    return bom


@router.get(
    "/bom/product/{product_id}",
    response_model=BoMDTO,
    # dependencies=[Depends(require_permission(PERMISSION_BOM_READ))],
)
async def get_bom_by_product(product_id: str, service: BoMServiceDep) -> BoMDTO:
    """Get bill of materials for a product."""
    bom = service.get_bom_by_product(product_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BoM not found for product")
    return bom


@router.put(
    "/bom/{bom_id}",
    response_model=BoMDTO,
    # dependencies=[Depends(require_permission(PERMISSION_BOM_UPDATE))],
)
async def update_bom(bom_id: str, dto: BoMUpdateDTO, service: BoMServiceDep) -> BoMDTO:
    """Update bill of materials."""
    try:
        return service.update_bom(bom_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bom/cost",
    response_model=BoMCostResponseDTO,
    # dependencies=[Depends(require_permission(PERMISSION_BOM_COST))],
)
async def calculate_bom_cost(
    dto: BoMCostRequestDTO, service: BoMServiceDep
) -> BoMCostResponseDTO:
    """Calculate bill of materials cost."""
    try:
        return service.calculate_bom_cost(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
