"""
Configuration for Sales module.
"""

from pydantic_settings import BaseSettings


class SalesSettings(BaseSettings):
    """Sales module configuration settings."""

    # Quote settings
    quote_prefix: str = "QT"
    quote_default_validity_days: int = 30

    # Order settings
    order_prefix: str = "SO"
    order_default_delivery_days: int = 7

    # Currency settings
    default_currency: str = "USD"

    # Feature flags
    allow_negative_stock: bool = False
    require_shipping_info: bool = True
    auto_mark_expired_quotes: bool = True

    class Config:
        env_prefix = "SALES_"
