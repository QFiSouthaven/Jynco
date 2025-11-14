"""
Security Configuration Validator

Validates that required services and configurations are present
based on the execution mode.
"""

import os
import logging
from typing import List, Tuple
from .execution_mode import ExecutionMode, SecurityConfig, get_security_config

logger = logging.getLogger(__name__)


class SecurityValidationError(Exception):
    """Raised when security configuration validation fails."""

    pass


def validate_vault_config(config: SecurityConfig) -> Tuple[bool, List[str]]:
    """
    Validate secrets vault configuration.

    Args:
        config: Security configuration

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not config.require_vault:
        return True, []

    errors = []

    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")

    if not vault_addr:
        errors.append(
            f"VAULT_ADDR environment variable is required in {config.mode.value} mode"
        )

    if not vault_token and not os.getenv("VAULT_ROLE_ID"):
        errors.append(
            f"VAULT_TOKEN or VAULT_ROLE_ID is required in {config.mode.value} mode"
        )

    return len(errors) == 0, errors


def validate_storage_config(config: SecurityConfig) -> Tuple[bool, List[str]]:
    """
    Validate storage configuration.

    Args:
        config: Security configuration

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not config.require_cloud_storage:
        return True, []

    errors = []

    s3_bucket = os.getenv("S3_BUCKET")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not s3_bucket:
        errors.append(
            f"S3_BUCKET environment variable is required in {config.mode.value} mode"
        )

    # Check if we have credentials (unless using IAM roles)
    if not aws_access_key or not aws_secret_key:
        # Check if we're in an environment that supports IAM roles
        if not os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            errors.append(
                f"AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required "
                f"in {config.mode.value} mode (unless using IAM roles)"
            )

    return len(errors) == 0, errors


def validate_iam_config(config: SecurityConfig) -> Tuple[bool, List[str]]:
    """
    Validate IAM/authentication configuration.

    Args:
        config: Security configuration

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not config.require_iam:
        return True, []

    errors = []

    oidc_provider = os.getenv("OIDC_PROVIDER_URL")
    oidc_client_id = os.getenv("OIDC_CLIENT_ID")
    oidc_client_secret = os.getenv("OIDC_CLIENT_SECRET")

    if not oidc_provider:
        errors.append(
            f"OIDC_PROVIDER_URL is required in {config.mode.value} mode. "
            "Please configure an OpenID Connect identity provider."
        )

    if not oidc_client_id:
        errors.append(f"OIDC_CLIENT_ID is required in {config.mode.value} mode")

    if not oidc_client_secret:
        errors.append(f"OIDC_CLIENT_SECRET is required in {config.mode.value} mode")

    # Check if database RLS is enabled
    enable_rls = os.getenv("ENABLE_DATABASE_RLS", "").lower() == "true"
    if not enable_rls:
        errors.append(
            f"ENABLE_DATABASE_RLS must be set to 'true' in {config.mode.value} mode "
            "for proper data isolation"
        )

    return len(errors) == 0, errors


def validate_sandbox_config(config: SecurityConfig) -> Tuple[bool, List[str]]:
    """
    Validate sandboxing configuration.

    Args:
        config: Security configuration

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not config.enable_sandboxing:
        return True, []

    errors = []

    sandbox_type = os.getenv("SANDBOX_TYPE", "docker")

    valid_sandboxes = ["docker", "gvisor", "firecracker"]
    if sandbox_type not in valid_sandboxes:
        errors.append(
            f"SANDBOX_TYPE must be one of {valid_sandboxes}, got: {sandbox_type}"
        )

    if config.mode == ExecutionMode.PRODUCTION and sandbox_type == "docker":
        errors.append(
            f"SANDBOX_TYPE='docker' is not sufficient for {config.mode.value} mode. "
            "Use 'gvisor' or 'firecracker' for kernel-level isolation."
        )

    return len(errors) == 0, errors


def validate_network_config(config: SecurityConfig) -> Tuple[bool, List[str]]:
    """
    Validate network configuration.

    Args:
        config: Security configuration

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    network_egress = os.getenv("NETWORK_EGRESS", "allowed").lower()

    if config.mode == ExecutionMode.PRODUCTION:
        if network_egress != "blocked":
            errors.append(
                f"NETWORK_EGRESS must be 'blocked' in {config.mode.value} mode"
            )

    elif config.mode == ExecutionMode.SELF_HOSTED_PRODUCTION:
        if network_egress == "blocked":
            warnings.append(
                "NETWORK_EGRESS is 'blocked' but self-hosted mode typically needs "
                "access to approved sources. Consider 'restricted' mode."
            )

        egress_proxy = os.getenv("EGRESS_PROXY_URL")
        if network_egress == "restricted" and not egress_proxy:
            warnings.append(
                "EGRESS_PROXY_URL should be configured for restricted network access"
            )

    # Log warnings but don't fail validation
    for warning in warnings:
        logger.warning(warning)

    return len(errors) == 0, errors


def validate_security_config(
    config: SecurityConfig = None, fail_fast: bool = True
) -> bool:
    """
    Validate the complete security configuration.

    Args:
        config: Security configuration to validate (uses current if not provided)
        fail_fast: If True, raise exception on first error. If False, collect all errors.

    Returns:
        True if valid

    Raises:
        SecurityValidationError: If validation fails and fail_fast is True
    """
    if config is None:
        config = get_security_config()

    logger.info(f"Validating security configuration for {config.mode.value} mode...")

    all_errors = []

    # Run all validators
    validators = [
        ("Secrets Vault", validate_vault_config),
        ("Storage", validate_storage_config),
        ("IAM/Authentication", validate_iam_config),
        ("Sandboxing", validate_sandbox_config),
        ("Network", validate_network_config),
    ]

    for name, validator in validators:
        is_valid, errors = validator(config)
        if not is_valid:
            all_errors.extend([f"[{name}] {error}" for error in errors])
            if fail_fast:
                raise SecurityValidationError(
                    f"Security validation failed:\n  " + "\n  ".join(errors)
                )

    if all_errors:
        error_msg = (
            f"Security validation failed for {config.mode.value} mode:\n  "
            + "\n  ".join(all_errors)
        )
        raise SecurityValidationError(error_msg)

    logger.info("✅ Security configuration validation passed")
    return True


def validate_or_warn(config: SecurityConfig = None) -> bool:
    """
    Validate security configuration, but only warn on errors instead of failing.
    Useful for development mode.

    Args:
        config: Security configuration to validate

    Returns:
        True if valid, False if invalid (but doesn't raise)
    """
    try:
        validate_security_config(config, fail_fast=False)
        return True
    except SecurityValidationError as e:
        logger.warning(f"Security validation warnings:\n{e}")
        logger.warning("Proceeding anyway (not recommended for production)")
        return False


def get_missing_config_help(config: SecurityConfig) -> str:
    """
    Generate helpful message about what configuration is missing.

    Args:
        config: Security configuration

    Returns:
        Formatted help string
    """
    help_lines = [
        f"\nConfiguration Help for {config.mode.value.upper()} mode:",
        "=" * 60,
    ]

    if config.require_vault:
        help_lines.extend(
            [
                "\n🔐 Secrets Vault (Required):",
                "  export VAULT_ADDR=https://vault.example.com",
                "  export VAULT_TOKEN=hvs.xxxxx",
                "  # Or use AppRole authentication:",
                "  export VAULT_ROLE_ID=xxxxx",
                "  export VAULT_SECRET_ID=xxxxx",
            ]
        )

    if config.require_cloud_storage:
        help_lines.extend(
            [
                "\n☁️  Cloud Storage (Required):",
                "  export S3_BUCKET=my-video-foundry-bucket",
                "  export AWS_ACCESS_KEY_ID=AKIAxxxx",
                "  export AWS_SECRET_ACCESS_KEY=xxxxx",
                "  export AWS_REGION=us-east-1",
            ]
        )

    if config.require_iam:
        help_lines.extend(
            [
                "\n👤 IAM/Authentication (Required):",
                "  export OIDC_PROVIDER_URL=https://auth.example.com",
                "  export OIDC_CLIENT_ID=video-foundry",
                "  export OIDC_CLIENT_SECRET=xxxxx",
                "  export ENABLE_DATABASE_RLS=true",
            ]
        )

    if config.enable_sandboxing:
        help_lines.extend(
            [
                "\n📦 Sandboxing:",
                "  export SANDBOX_TYPE=gvisor  # or firecracker",
            ]
        )

    if config.mode == ExecutionMode.PRODUCTION:
        help_lines.extend(
            [
                "\n🌐 Network (Production):",
                "  export NETWORK_EGRESS=blocked",
            ]
        )
    elif config.mode == ExecutionMode.SELF_HOSTED_PRODUCTION:
        help_lines.extend(
            [
                "\n🌐 Network (Self-Hosted):",
                "  export NETWORK_EGRESS=restricted",
                "  export EGRESS_PROXY_URL=http://proxy.internal:3128",
                "  export APPROVED_GIT_REPOS=github.com/myorg/*,gitlab.internal/*",
            ]
        )

    help_lines.extend(
        [
            "\n💡 Tip: Copy .env.example to .env and edit with your values",
            "=" * 60,
        ]
    )

    return "\n".join(help_lines)
