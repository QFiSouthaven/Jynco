"""
Video Foundry Security Module

This module implements the three-tier security architecture:
- production: Maximum security for multi-tenant SaaS
- self-hosted-production: Balanced security for enterprise self-hosting
- developer: Flexible security for local development

See docs/SECURITY_PROPOSAL_V3.md for complete architecture details.
"""

from .execution_mode import ExecutionMode, get_execution_mode, SecurityConfig
from .config_validator import validate_security_config, SecurityValidationError

__all__ = [
    "ExecutionMode",
    "get_execution_mode",
    "SecurityConfig",
    "validate_security_config",
    "SecurityValidationError",
]
