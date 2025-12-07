"""Configuration for Procurement module."""

from pydantic_settings import BaseSettings


class ProcurementSettings(BaseSettings):
    """Procurement module settings."""

    # Purchase Order settings
    po_number_prefix: str = "PO"
    po_number_padding: int = 6
    allow_partial_receipts: bool = True
    require_quality_check: bool = False

    # RFQ settings
    rfq_number_prefix: str = "RFQ"
    rfq_number_padding: int = 6
    rfq_validity_days: int = 30

    # GRN settings
    grn_number_prefix: str = "GRN"
    grn_number_padding: int = 6

    # Agreement settings
    agreement_number_prefix: str = "AGR"
    agreement_number_padding: int = 6

    class Config:
        """Pydantic config."""

        env_prefix = "PROCUREMENT_"
