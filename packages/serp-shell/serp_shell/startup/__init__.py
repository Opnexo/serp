"""
Startup package initialization
"""

from serp_shell.startup.bootstrap import bootstrap_application
from serp_shell.startup.config import get_settings

__all__ = ["bootstrap_application", "get_settings"]
