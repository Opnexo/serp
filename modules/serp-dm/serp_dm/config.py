"""
Configuration settings for Document Management module.
"""

from pydantic_settings import BaseSettings


class DMSettings(BaseSettings):
    """Document Management module settings."""

    # Module metadata
    module_name: str = "Document Management"
    module_version: str = "0.1.0"

    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/serp"
    database_schema: str = "dm"  # PostgreSQL schema for this module
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Feature flags
    enable_versioning: bool = True
    enable_file_preview: bool = True
    enable_full_text_search: bool = True
    enable_file_compression: bool = False

    # Storage settings
    storage_type: str = "filesystem"  # filesystem, s3, azure
    storage_path: str = "/var/serp/documents"
    max_file_size_mb: int = 100
    allowed_file_types: list[str] = [
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "txt",
        "jpg",
        "jpeg",
        "png",
        "gif",
    ]

    # Document settings
    default_folder_name: str = "My Documents"
    max_folder_depth: int = 10
    enable_folder_permissions: bool = True

    # Security settings
    scan_for_viruses: bool = True
    calculate_checksums: bool = True
    checksum_algorithm: str = "sha256"

    class Config:
        """Pydantic config."""

        env_prefix = "SERP_DM_"
        case_sensitive = False
