"""
Configuration settings for Invoicing module.
"""

from pydantic_settings import BaseSettings


class InvoicingSettings(BaseSettings):
    """Invoicing module settings."""

    # Module metadata
    module_name: str = "Invoicing"
    module_version: str = "0.1.0"

    # Invoice numbering
    invoice_prefix: str = "INV"
    invoice_number_format: str = "{prefix}-{year}-{sequence:04d}"

    # Defaults
    default_currency: str = "USD"
    default_payment_terms_days: int = 30
    default_tax_rate: float = 0.0

    # Business rules
    allow_partial_payments: bool = True
    allow_overpayment: bool = False
    auto_mark_paid_threshold: float = 0.99  # 99% paid = fully paid

    # Overdue settings
    overdue_warning_days: int = 7  # Days before due date to send warning
    auto_mark_overdue: bool = True

    class Config:
        """Pydantic config."""

        env_prefix = "SERP_INVOICING_"
        case_sensitive = False
