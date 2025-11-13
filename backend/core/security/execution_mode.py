"""
Execution Mode Configuration

Defines the three-tier security model and mode-specific settings.
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """
    Three-tier security execution modes.

    PRODUCTION: Maximum security for multi-tenant SaaS deployments
    SELF_HOSTED_PRODUCTION: Balanced security for single-tenant enterprise
    DEVELOPER: Flexible security for local development and research
    """

    PRODUCTION = "production"
    SELF_HOSTED_PRODUCTION = "self-hosted-production"
    DEVELOPER = "developer"

    @classmethod
    def from_env(cls, default: "ExecutionMode" = None) -> "ExecutionMode":
        """
        Get execution mode from environment variable.

        Args:
            default: Default mode if not specified (defaults to PRODUCTION for safety)

        Returns:
            ExecutionMode enum value

        Raises:
            ValueError: If invalid mode specified
        """
        mode_str = os.getenv("JYNCO_EXECUTION_MODE", "").lower()

        if not mode_str:
            if default is None:
                default = cls.PRODUCTION
                logger.warning(
                    f"JYNCO_EXECUTION_MODE not set, defaulting to {default.value} (most secure)"
                )
            return default

        try:
            return cls(mode_str)
        except ValueError:
            valid_modes = ", ".join([m.value for m in cls])
            raise ValueError(
                f"Invalid execution mode: '{mode_str}'. "
                f"Must be one of: {valid_modes}"
            )


@dataclass
class SecurityConfig:
    """
    Mode-specific security configuration.

    Attributes:
        mode: The execution mode
        require_vault: Whether secrets vault is required
        require_cloud_storage: Whether cloud storage (S3) is required
        require_iam: Whether IAM/authentication is required
        allow_internet_egress: Whether workers can access internet
        workflow_vetting_strict: Whether workflow vetting uses strict allow-list
        enable_sandboxing: Whether kernel-level sandboxing is enabled
        enable_audit_logging: Whether comprehensive audit logging is enabled
        allow_custom_nodes: Whether custom ComfyUI nodes are permitted
    """

    mode: ExecutionMode
    require_vault: bool
    require_cloud_storage: bool
    require_iam: bool
    allow_internet_egress: bool
    workflow_vetting_strict: bool
    enable_sandboxing: bool
    enable_audit_logging: bool
    allow_custom_nodes: bool

    @classmethod
    def for_mode(cls, mode: ExecutionMode) -> "SecurityConfig":
        """
        Create security configuration for the specified execution mode.

        Args:
            mode: The execution mode

        Returns:
            SecurityConfig with mode-appropriate settings
        """
        if mode == ExecutionMode.PRODUCTION:
            return cls(
                mode=mode,
                require_vault=True,
                require_cloud_storage=True,
                require_iam=True,
                allow_internet_egress=False,
                workflow_vetting_strict=True,
                enable_sandboxing=True,
                enable_audit_logging=True,
                allow_custom_nodes=False,  # Only pre-approved nodes
            )

        elif mode == ExecutionMode.SELF_HOSTED_PRODUCTION:
            return cls(
                mode=mode,
                require_vault=True,
                require_cloud_storage=False,  # Admin can choose
                require_iam=True,
                allow_internet_egress=True,  # But restricted to approved sources
                workflow_vetting_strict=False,  # Admin-configurable
                enable_sandboxing=True,
                enable_audit_logging=True,
                allow_custom_nodes=True,  # Admin-approved
            )

        elif mode == ExecutionMode.DEVELOPER:
            return cls(
                mode=mode,
                require_vault=False,  # Can use .env for ease
                require_cloud_storage=False,  # Use local storage
                require_iam=False,  # Single user
                allow_internet_egress=True,  # Full access (but logged)
                workflow_vetting_strict=False,  # Log and warn only
                enable_sandboxing=True,  # Still sandboxed for safety
                enable_audit_logging=False,  # Basic logging only
                allow_custom_nodes=True,  # Full flexibility
            )

        else:
            raise ValueError(f"Unknown execution mode: {mode}")

    def get_security_warnings(self) -> list[str]:
        """
        Get list of security warnings for this configuration.

        Returns:
            List of warning strings
        """
        warnings = []

        if self.mode == ExecutionMode.DEVELOPER:
            warnings.append(
                "⚠️  DEVELOPER MODE: This configuration is NOT suitable for production use!"
            )
            warnings.append(
                "⚠️  Security controls are relaxed for development flexibility."
            )

        if not self.require_vault:
            warnings.append(
                "⚠️  Secrets vault not required. Credentials may be stored insecurely."
            )

        if not self.require_cloud_storage:
            warnings.append("⚠️  Using local storage. Ensure proper backup procedures.")

        if not self.require_iam:
            warnings.append(
                "⚠️  IAM/Authentication disabled. Not suitable for multi-user deployments."
            )

        if self.allow_internet_egress:
            if self.mode == ExecutionMode.DEVELOPER:
                warnings.append(
                    "⚠️  Workers have internet access. Only use on trusted networks."
                )
            elif self.mode == ExecutionMode.SELF_HOSTED_PRODUCTION:
                warnings.append(
                    "ℹ️  Worker internet access restricted to administrator-approved sources."
                )

        if not self.workflow_vetting_strict:
            warnings.append(
                "⚠️  Workflow vetting is not in strict mode. Review workflows carefully."
            )

        return warnings

    def display_info(self) -> str:
        """
        Get formatted information about this security configuration.

        Returns:
            Multi-line string with configuration details
        """
        info_lines = [
            "=" * 60,
            f"Video Foundry - Execution Mode: {self.mode.value.upper()}",
            "=" * 60,
            "",
            "Security Configuration:",
            f"  🔐 Secrets Vault Required:     {'✅ Yes' if self.require_vault else '❌ No'}",
            f"  ☁️  Cloud Storage Required:     {'✅ Yes' if self.require_cloud_storage else '❌ No'}",
            f"  👤 IAM/Auth Required:          {'✅ Yes' if self.require_iam else '❌ No'}",
            f"  🌐 Internet Egress:            {'✅ Allowed' if self.allow_internet_egress else '❌ Blocked'}",
            f"  🔍 Strict Workflow Vetting:   {'✅ Enabled' if self.workflow_vetting_strict else '⚠️  Relaxed'}",
            f"  📦 Kernel Sandboxing:          {'✅ Enabled' if self.enable_sandboxing else '❌ Disabled'}",
            f"  📊 Audit Logging:              {'✅ Full' if self.enable_audit_logging else '⚠️  Basic'}",
            f"  🔧 Custom Nodes:               {'✅ Allowed' if self.allow_custom_nodes else '❌ Pre-approved only'}",
        ]

        warnings = self.get_security_warnings()
        if warnings:
            info_lines.extend(["", "Security Warnings:"])
            info_lines.extend([f"  {w}" for w in warnings])

        info_lines.append("=" * 60)

        return "\n".join(info_lines)


# Global configuration instance
_execution_mode: Optional[ExecutionMode] = None
_security_config: Optional[SecurityConfig] = None


def get_execution_mode() -> ExecutionMode:
    """
    Get the current execution mode (cached).

    Returns:
        ExecutionMode enum value
    """
    global _execution_mode
    if _execution_mode is None:
        _execution_mode = ExecutionMode.from_env()
    return _execution_mode


def get_security_config() -> SecurityConfig:
    """
    Get the current security configuration (cached).

    Returns:
        SecurityConfig for the current execution mode
    """
    global _security_config
    if _security_config is None:
        mode = get_execution_mode()
        _security_config = SecurityConfig.for_mode(mode)
    return _security_config


def display_security_info():
    """
    Display security configuration information.
    Should be called at application startup.
    """
    config = get_security_config()
    logger.info("\n" + config.display_info())

    # Print to stdout as well for visibility
    print(config.display_info())
