"""
SERP Invoicing Module

Invoice management and payment tracking.
"""

from serp_invoicing.application.services import InvoiceService, PaymentService
from serp_invoicing.domain.entities import Invoice, InvoiceItem, Payment
from serp_invoicing.domain.value_objects import InvoiceNumber, PaymentMethod

__version__ = "0.1.0"

MODULE_INFO = {
    "module_id": "invoicing",
    "module_name": "Invoicing & Payments",
    "version": __version__,
    "description": "Invoice management, payment tracking, and billing",
    "author": "SERP Team",
    "permissions": [
        "invoicing:invoices:list",
        "invoicing:invoices:read",
        "invoicing:invoices:create",
        "invoicing:invoices:update",
        "invoicing:invoices:delete",
        "invoicing:payments:list",
        "invoicing:payments:read",
        "invoicing:payments:create",
        "invoicing:payments:delete",
    ],
}

__all__ = [
    "Invoice",
    "InvoiceItem",
    "Payment",
    "InvoiceNumber",
    "PaymentMethod",
    "InvoiceService",
    "PaymentService",
    "MODULE_INFO",
]
