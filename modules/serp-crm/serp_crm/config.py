"""
Configuration settings for CRM module.
"""

from pydantic_settings import BaseSettings


class CRMSettings(BaseSettings):
    """CRM module settings."""

    # Module metadata
    module_name: str = "CRM"
    module_version: str = "0.1.0"

    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/serp"
    database_schema: str = "crm"  # PostgreSQL schema for this module
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Feature flags
    enable_partner_merge: bool = True
    enable_lead_scoring: bool = True
    enable_opportunity_forecast: bool = True

    # Business rules
    max_contacts_per_partner: int = 100
    default_currency: str = "USD"
    default_country: str = "US"

    # Lead scoring thresholds
    lead_score_high: int = 75
    lead_score_medium: int = 50
    lead_score_low: int = 25

    # Opportunity stages
    default_opportunity_stage: str = "PROSPECTING"
    won_stage: str = "WON"
    lost_stage: str = "LOST"

    class Config:
        """Pydantic config."""

        env_prefix = "SERP_CRM_"
        case_sensitive = False
