"""Permissions for Products module."""

# UoM permissions
PERMISSION_UOM_CREATE = "products:uom:create"
PERMISSION_UOM_READ = "products:uom:read"
PERMISSION_UOM_UPDATE = "products:uom:update"
PERMISSION_UOM_DELETE = "products:uom:delete"
PERMISSION_UOM_LIST = "products:uom:list"

# Attribute permissions
PERMISSION_ATTRIBUTE_CREATE = "products:attribute:create"
PERMISSION_ATTRIBUTE_READ = "products:attribute:read"
PERMISSION_ATTRIBUTE_UPDATE = "products:attribute:update"
PERMISSION_ATTRIBUTE_DELETE = "products:attribute:delete"
PERMISSION_ATTRIBUTE_LIST = "products:attribute:list"

# Category permissions
PERMISSION_CATEGORY_CREATE = "products:category:create"
PERMISSION_CATEGORY_READ = "products:category:read"
PERMISSION_CATEGORY_UPDATE = "products:category:update"
PERMISSION_CATEGORY_DELETE = "products:category:delete"
PERMISSION_CATEGORY_LIST = "products:category:list"

# Product permissions
PERMISSION_PRODUCT_CREATE = "products:product:create"
PERMISSION_PRODUCT_READ = "products:product:read"
PERMISSION_PRODUCT_UPDATE = "products:product:update"
PERMISSION_PRODUCT_DELETE = "products:product:delete"
PERMISSION_PRODUCT_LIST = "products:product:list"
PERMISSION_PRODUCT_ACTIVATE = "products:product:activate"
PERMISSION_PRODUCT_DEACTIVATE = "products:product:deactivate"
PERMISSION_PRODUCT_SEARCH = "products:product:search"

# Price List permissions
PERMISSION_PRICELIST_CREATE = "products:pricelist:create"
PERMISSION_PRICELIST_READ = "products:pricelist:read"
PERMISSION_PRICELIST_UPDATE = "products:pricelist:update"
PERMISSION_PRICELIST_DELETE = "products:pricelist:delete"
PERMISSION_PRICELIST_LIST = "products:pricelist:list"
PERMISSION_PRICE_GET = "products:price:get"

# BoM permissions
PERMISSION_BOM_CREATE = "products:bom:create"
PERMISSION_BOM_READ = "products:bom:read"
PERMISSION_BOM_UPDATE = "products:bom:update"
PERMISSION_BOM_DELETE = "products:bom:delete"
PERMISSION_BOM_COST = "products:bom:cost"

# Utility permissions
PERMISSION_UNIT_CONVERT = "products:unit:convert"

# Permission groups
ADMIN_PERMISSIONS = [
    # UoM
    PERMISSION_UOM_CREATE,
    PERMISSION_UOM_READ,
    PERMISSION_UOM_UPDATE,
    PERMISSION_UOM_DELETE,
    PERMISSION_UOM_LIST,
    # Attributes
    PERMISSION_ATTRIBUTE_CREATE,
    PERMISSION_ATTRIBUTE_READ,
    PERMISSION_ATTRIBUTE_UPDATE,
    PERMISSION_ATTRIBUTE_DELETE,
    PERMISSION_ATTRIBUTE_LIST,
    # Categories
    PERMISSION_CATEGORY_CREATE,
    PERMISSION_CATEGORY_READ,
    PERMISSION_CATEGORY_UPDATE,
    PERMISSION_CATEGORY_DELETE,
    PERMISSION_CATEGORY_LIST,
    # Products
    PERMISSION_PRODUCT_CREATE,
    PERMISSION_PRODUCT_READ,
    PERMISSION_PRODUCT_UPDATE,
    PERMISSION_PRODUCT_DELETE,
    PERMISSION_PRODUCT_LIST,
    PERMISSION_PRODUCT_ACTIVATE,
    PERMISSION_PRODUCT_DEACTIVATE,
    PERMISSION_PRODUCT_SEARCH,
    # Price Lists
    PERMISSION_PRICELIST_CREATE,
    PERMISSION_PRICELIST_READ,
    PERMISSION_PRICELIST_UPDATE,
    PERMISSION_PRICELIST_DELETE,
    PERMISSION_PRICELIST_LIST,
    PERMISSION_PRICE_GET,
    # BoM
    PERMISSION_BOM_CREATE,
    PERMISSION_BOM_READ,
    PERMISSION_BOM_UPDATE,
    PERMISSION_BOM_DELETE,
    PERMISSION_BOM_COST,
    # Utilities
    PERMISSION_UNIT_CONVERT,
]

USER_PERMISSIONS = [
    # UoM - read only
    PERMISSION_UOM_READ,
    PERMISSION_UOM_LIST,
    # Attributes - read only
    PERMISSION_ATTRIBUTE_READ,
    PERMISSION_ATTRIBUTE_LIST,
    # Categories - read only
    PERMISSION_CATEGORY_READ,
    PERMISSION_CATEGORY_LIST,
    # Products - read and search
    PERMISSION_PRODUCT_READ,
    PERMISSION_PRODUCT_LIST,
    PERMISSION_PRODUCT_SEARCH,
    # Price Lists - read and get price
    PERMISSION_PRICELIST_READ,
    PERMISSION_PRICELIST_LIST,
    PERMISSION_PRICE_GET,
    # BoM - read only
    PERMISSION_BOM_READ,
    PERMISSION_BOM_COST,
    # Utilities
    PERMISSION_UNIT_CONVERT,
]
