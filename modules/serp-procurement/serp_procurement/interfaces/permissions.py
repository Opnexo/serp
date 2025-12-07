"""Permissions for Procurement module."""

# RFQ permissions
PERMISSION_RFQ_CREATE = "procurement:rfq:create"
PERMISSION_RFQ_READ = "procurement:rfq:read"
PERMISSION_RFQ_UPDATE = "procurement:rfq:update"
PERMISSION_RFQ_DELETE = "procurement:rfq:delete"
PERMISSION_RFQ_LIST = "procurement:rfq:list"
PERMISSION_RFQ_SEND = "procurement:rfq:send"
PERMISSION_RFQ_QUOTE = "procurement:rfq:quote"
PERMISSION_RFQ_ACCEPT = "procurement:rfq:accept"
PERMISSION_RFQ_CANCEL = "procurement:rfq:cancel"
PERMISSION_RFQ_CONVERT = "procurement:rfq:convert"

# Purchase Order permissions
PERMISSION_PO_CREATE = "procurement:po:create"
PERMISSION_PO_READ = "procurement:po:read"
PERMISSION_PO_UPDATE = "procurement:po:update"
PERMISSION_PO_DELETE = "procurement:po:delete"
PERMISSION_PO_LIST = "procurement:po:list"
PERMISSION_PO_CONFIRM = "procurement:po:confirm"
PERMISSION_PO_CANCEL = "procurement:po:cancel"

# Goods Receipt Note permissions
PERMISSION_GRN_CREATE = "procurement:grn:create"
PERMISSION_GRN_READ = "procurement:grn:read"
PERMISSION_GRN_LIST = "procurement:grn:list"
PERMISSION_GRN_QUALITY = "procurement:grn:quality"

# Purchase Agreement permissions
PERMISSION_AGREEMENT_CREATE = "procurement:agreement:create"
PERMISSION_AGREEMENT_READ = "procurement:agreement:read"
PERMISSION_AGREEMENT_UPDATE = "procurement:agreement:update"
PERMISSION_AGREEMENT_DELETE = "procurement:agreement:delete"
PERMISSION_AGREEMENT_LIST = "procurement:agreement:list"
PERMISSION_AGREEMENT_ACTIVATE = "procurement:agreement:activate"
PERMISSION_AGREEMENT_DEACTIVATE = "procurement:agreement:deactivate"

# Permission groups
ADMIN_PERMISSIONS = [
    # RFQ
    PERMISSION_RFQ_CREATE,
    PERMISSION_RFQ_READ,
    PERMISSION_RFQ_UPDATE,
    PERMISSION_RFQ_DELETE,
    PERMISSION_RFQ_LIST,
    PERMISSION_RFQ_SEND,
    PERMISSION_RFQ_QUOTE,
    PERMISSION_RFQ_ACCEPT,
    PERMISSION_RFQ_CANCEL,
    PERMISSION_RFQ_CONVERT,
    # Purchase Orders
    PERMISSION_PO_CREATE,
    PERMISSION_PO_READ,
    PERMISSION_PO_UPDATE,
    PERMISSION_PO_DELETE,
    PERMISSION_PO_LIST,
    PERMISSION_PO_CONFIRM,
    PERMISSION_PO_CANCEL,
    # Goods Receipts
    PERMISSION_GRN_CREATE,
    PERMISSION_GRN_READ,
    PERMISSION_GRN_LIST,
    PERMISSION_GRN_QUALITY,
    # Agreements
    PERMISSION_AGREEMENT_CREATE,
    PERMISSION_AGREEMENT_READ,
    PERMISSION_AGREEMENT_UPDATE,
    PERMISSION_AGREEMENT_DELETE,
    PERMISSION_AGREEMENT_LIST,
    PERMISSION_AGREEMENT_ACTIVATE,
    PERMISSION_AGREEMENT_DEACTIVATE,
]

BUYER_PERMISSIONS = [
    # RFQ - full access
    PERMISSION_RFQ_CREATE,
    PERMISSION_RFQ_READ,
    PERMISSION_RFQ_UPDATE,
    PERMISSION_RFQ_LIST,
    PERMISSION_RFQ_SEND,
    PERMISSION_RFQ_QUOTE,
    PERMISSION_RFQ_ACCEPT,
    PERMISSION_RFQ_CONVERT,
    # Purchase Orders - full access
    PERMISSION_PO_CREATE,
    PERMISSION_PO_READ,
    PERMISSION_PO_UPDATE,
    PERMISSION_PO_LIST,
    PERMISSION_PO_CONFIRM,
    # Goods Receipts - read only
    PERMISSION_GRN_READ,
    PERMISSION_GRN_LIST,
    # Agreements - full access
    PERMISSION_AGREEMENT_CREATE,
    PERMISSION_AGREEMENT_READ,
    PERMISSION_AGREEMENT_UPDATE,
    PERMISSION_AGREEMENT_LIST,
]

WAREHOUSE_PERMISSIONS = [
    # RFQ - read only
    PERMISSION_RFQ_READ,
    PERMISSION_RFQ_LIST,
    # Purchase Orders - read only
    PERMISSION_PO_READ,
    PERMISSION_PO_LIST,
    # Goods Receipts - full access
    PERMISSION_GRN_CREATE,
    PERMISSION_GRN_READ,
    PERMISSION_GRN_LIST,
    PERMISSION_GRN_QUALITY,
    # Agreements - read only
    PERMISSION_AGREEMENT_READ,
    PERMISSION_AGREEMENT_LIST,
]
