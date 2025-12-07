"""Configuration for Inventory module."""

from pydantic_settings import BaseSettings


class InventorySettings(BaseSettings):
    """Inventory module settings."""

    # Warehouse settings
    default_warehouse_code: str = "WH01"
    allow_negative_stock: bool = False

    # Location settings
    location_code_prefix: str = "LOC"
    location_code_padding: int = 6

    # Movement settings
    movement_number_prefix: str = "STK"
    movement_number_padding: int = 8
    require_lot_for_tracked_products: bool = True

    # Adjustment settings
    adjustment_number_prefix: str = "ADJ"
    adjustment_number_padding: int = 6
    require_approval_threshold: float = 1000.0  # Currency value

    # Reordering settings
    auto_create_procurement: bool = True
    reorder_check_frequency_hours: int = 24

    # Valuation methods
    default_costing_method: str = "FIFO"  # FIFO, LIFO, AVERAGE

    class Config:
        """Pydantic config."""

        env_prefix = "INVENTORY_"
