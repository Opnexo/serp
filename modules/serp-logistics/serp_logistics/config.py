"""Configuration for Logistics module."""

from pydantic_settings import BaseSettings


class LogisticsSettings(BaseSettings):
    """Logistics module settings."""

    # Picking settings
    picking_number_prefix: str = "PICK"
    picking_number_padding: int = 8
    default_picking_strategy: str = "SINGLE"  # WAVE, BATCH, ZONE, SINGLE

    # Packing settings
    packing_number_prefix: str = "PACK"
    packing_number_padding: int = 8
    require_weight_verification: bool = True
    dimensional_weight_divisor: int = 5000  # cm³ to kg

    # Shipment settings
    shipment_number_prefix: str = "SHIP"
    shipment_number_padding: int = 8
    default_insurance_threshold: float = 500.0  # Currency value
    require_signature_threshold: float = 1000.0

    # Package settings
    max_package_weight_kg: float = 30.0
    max_package_dimension_cm: float = 120.0

    # Route settings
    route_number_prefix: str = "ROUTE"
    route_number_padding: int = 6
    max_stops_per_route: int = 50

    # RMA settings
    rma_number_prefix: str = "RMA"
    rma_number_padding: int = 8
    rma_approval_required: bool = True
    rma_default_validity_days: int = 30

    # Carrier integration
    enable_carrier_api: bool = False
    carrier_timeout_seconds: int = 30

    class Config:
        """Pydantic config."""

        env_prefix = "LOGISTICS_"
