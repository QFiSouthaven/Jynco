"""
Workflow Vetting Service - Three-Tier Security Model

This service validates ComfyUI workflows before execution, enforcing security
policies based on the execution mode (production, self-hosted-production, developer).
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import yaml
import hashlib

from config import get_settings

logger = logging.getLogger(__name__)


class SecurityViolation(Exception):
    """Raised when a workflow violates security policies."""
    pass


class WorkflowResource:
    """Represents a resource referenced in a workflow (node, model, repository)."""

    def __init__(self, resource_type: str, identifier: str, metadata: Optional[Dict] = None):
        self.resource_type = resource_type  # 'node', 'model', 'repository'
        self.identifier = identifier
        self.metadata = metadata or {}

    def __repr__(self):
        return f"WorkflowResource(type={self.resource_type}, id={self.identifier})"


class WorkflowVettingPolicy(ABC):
    """Base class for workflow vetting policies."""

    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    def validate(self, workflow: Dict[str, Any]) -> bool:
        """
        Validate a workflow against the policy.

        Args:
            workflow: The ComfyUI workflow JSON

        Returns:
            True if workflow is allowed

        Raises:
            SecurityViolation: If workflow violates policy
        """
        pass

    def extract_resources(self, workflow: Dict[str, Any]) -> List[WorkflowResource]:
        """Extract all resources (nodes, models, repos) from a workflow."""
        resources = []

        # Extract nodes
        if isinstance(workflow, dict):
            for node_id, node_data in workflow.items():
                if isinstance(node_data, dict) and "class_type" in node_data:
                    node_type = node_data["class_type"]
                    resources.append(WorkflowResource("node", node_type, node_data))

                    # Check for model references in inputs
                    if "inputs" in node_data:
                        for input_key, input_value in node_data["inputs"].items():
                            if "model" in input_key.lower() and isinstance(input_value, str):
                                resources.append(WorkflowResource("model", input_value))

                    # Check for custom node repository requirements
                    if node_data.get("_meta", {}).get("custom_repo"):
                        repo_url = node_data["_meta"]["custom_repo"]
                        resources.append(WorkflowResource("repository", repo_url))

        return resources


class ProductionVettingPolicy(WorkflowVettingPolicy):
    """
    PRODUCTION MODE: Strict allow-list enforcement.

    - Only platform-approved nodes allowed
    - Only vetted models from internal repository
    - NO custom node repositories permitted
    - Violations = immediate rejection
    """

    def __init__(self, settings):
        super().__init__(settings)
        self.allowlist = self._load_platform_allowlist()
        logger.info("🔒 Production vetting policy loaded (strict allow-list)")

    def _load_platform_allowlist(self) -> Dict[str, Any]:
        """Load the platform-maintained allow-list."""
        allowlist_path = Path(self.settings.workflow_allowlist_path)

        if not allowlist_path.exists():
            logger.warning(f"Allowlist not found at {allowlist_path}, using empty list")
            return {"nodes": [], "models": [], "repositories": []}

        try:
            with open(allowlist_path, 'r') as f:
                data = yaml.safe_load(f)

                # Filter for production mode entries
                if isinstance(data, list):
                    # Multi-document YAML
                    for doc in data:
                        if doc.get("execution_mode") == "production":
                            return doc
                elif data.get("execution_mode") == "production":
                    return data

                logger.warning("No production allowlist found, using empty list")
                return {"nodes": [], "models": [], "repositories": []}

        except Exception as e:
            logger.error(f"Failed to load allowlist: {e}")
            raise SecurityViolation(f"Cannot load security allowlist: {e}")

    def validate(self, workflow: Dict[str, Any]) -> bool:
        """Validate workflow against strict allow-list."""
        logger.info(f"🔍 Vetting workflow in PRODUCTION mode")

        resources = self.extract_resources(workflow)
        violations = []

        # Validate nodes
        allowed_nodes = {node["type"]: node for node in self.allowlist.get("nodes", [])}
        for resource in resources:
            if resource.resource_type == "node":
                if resource.identifier not in allowed_nodes:
                    violations.append(
                        f"Node '{resource.identifier}' is not in the approved list"
                    )
                else:
                    logger.debug(f"✓ Node '{resource.identifier}' approved")

        # Validate models
        allowed_models = {model["identifier"]: model for model in self.allowlist.get("models", [])}
        for resource in resources:
            if resource.resource_type == "model":
                if resource.identifier not in allowed_models:
                    violations.append(
                        f"Model '{resource.identifier}' is not vetted for production"
                    )
                else:
                    logger.debug(f"✓ Model '{resource.identifier}' vetted")

        # NO custom repositories allowed in production
        for resource in resources:
            if resource.resource_type == "repository":
                violations.append(
                    f"Custom repository '{resource.identifier}' not allowed in production mode"
                )

        if violations:
            violation_msg = "Workflow security violations:\n" + "\n".join(f"  - {v}" for v in violations)
            logger.error(f"❌ {violation_msg}")
            raise SecurityViolation(violation_msg)

        logger.info(f"✅ Workflow approved (production mode)")
        return True


class SelfHostedVettingPolicy(WorkflowVettingPolicy):
    """
    SELF-HOSTED PRODUCTION MODE: Admin-configurable allow-list.

    - Administrator can approve specific nodes, models, repositories
    - Custom node repositories allowed if admin-approved
    - Model sources must be in admin allow-list
    - Violations = rejection
    """

    def __init__(self, settings):
        super().__init__(settings)
        self.allowlist = self._load_admin_allowlist()
        logger.info("🔒 Self-hosted vetting policy loaded (admin-configurable)")

    def _load_admin_allowlist(self) -> Dict[str, Any]:
        """Load the administrator-configured allow-list."""
        allowlist_path = Path(self.settings.workflow_allowlist_path)

        if not allowlist_path.exists():
            logger.warning(f"Admin allowlist not found at {allowlist_path}, using defaults")
            return self._get_default_allowlist()

        try:
            with open(allowlist_path, 'r') as f:
                docs = list(yaml.safe_load_all(f))

                # Find self-hosted-production config
                for doc in docs:
                    if doc and doc.get("execution_mode") == "self-hosted-production":
                        logger.info(f"Loaded admin allowlist: {len(doc.get('nodes', []))} nodes, "
                                    f"{len(doc.get('models', []))} models, "
                                    f"{len(doc.get('repositories', []))} repositories")
                        return doc

                logger.warning("No self-hosted allowlist found, using defaults")
                return self._get_default_allowlist()

        except Exception as e:
            logger.error(f"Failed to load admin allowlist: {e}")
            return self._get_default_allowlist()

    def _get_default_allowlist(self) -> Dict[str, Any]:
        """Get default allowlist for self-hosted mode."""
        return {
            "execution_mode": "self-hosted-production",
            "nodes": [
                {"type": "LoadImage", "approved_by": "system", "approved_at": datetime.now().isoformat()},
                {"type": "SaveImage", "approved_by": "system", "approved_at": datetime.now().isoformat()},
            ],
            "models": [],
            "repositories": []
        }

    def validate(self, workflow: Dict[str, Any]) -> bool:
        """Validate workflow against admin-configured allow-list."""
        logger.info(f"🔍 Vetting workflow in SELF-HOSTED PRODUCTION mode")

        resources = self.extract_resources(workflow)
        violations = []

        # Validate nodes
        allowed_nodes = {node["type"]: node for node in self.allowlist.get("nodes", [])}
        for resource in resources:
            if resource.resource_type == "node":
                if resource.identifier not in allowed_nodes:
                    violations.append(
                        f"Node '{resource.identifier}' not approved by administrator"
                    )
                else:
                    logger.debug(f"✓ Node '{resource.identifier}' approved by admin")

        # Validate models
        allowed_models = {model["identifier"]: model for model in self.allowlist.get("models", [])}
        for resource in resources:
            if resource.resource_type == "model":
                if resource.identifier not in allowed_models:
                    violations.append(
                        f"Model '{resource.identifier}' not approved by administrator"
                    )
                else:
                    logger.debug(f"✓ Model '{resource.identifier}' approved by admin")

        # Validate repositories (allowed if admin-approved)
        allowed_repos = {repo["url"]: repo for repo in self.allowlist.get("repositories", [])}
        for resource in resources:
            if resource.resource_type == "repository":
                if resource.identifier not in allowed_repos:
                    violations.append(
                        f"Repository '{resource.identifier}' not approved by administrator"
                    )
                else:
                    logger.debug(f"✓ Repository '{resource.identifier}' approved by admin")

        if violations:
            violation_msg = "Workflow security violations:\n" + "\n".join(f"  - {v}" for v in violations)
            logger.error(f"❌ {violation_msg}")
            raise SecurityViolation(violation_msg)

        logger.info(f"✅ Workflow approved (self-hosted mode)")
        return True


class DeveloperVettingPolicy(WorkflowVettingPolicy):
    """
    DEVELOPER MODE: Log-and-warn (permissive).

    - All nodes allowed (but logged)
    - All models allowed (but logged)
    - Custom repositories allowed (but logged with security warning)
    - No rejections, only warnings
    """

    def __init__(self, settings):
        super().__init__(settings)
        logger.info("⚠️  Developer vetting policy loaded (log-and-warn mode)")

    def validate(self, workflow: Dict[str, Any]) -> bool:
        """Log all resources but always allow execution."""
        logger.warning("🔍 Vetting workflow in DEVELOPER mode (permissive)")

        resources = self.extract_resources(workflow)

        if not resources:
            logger.info("No external resources detected in workflow")
            return True

        logger.warning("⚠️  DEVELOPER MODE: The following potentially unsafe resources will be executed:")

        for resource in resources:
            if resource.resource_type == "node":
                logger.warning(f"   - Node: {resource.identifier}")

            elif resource.resource_type == "model":
                logger.warning(f"   - Model: {resource.identifier}")

            elif resource.resource_type == "repository":
                logger.warning(f"   - ⚠️  UNTRUSTED REPOSITORY: {resource.identifier}")
                logger.warning(f"      This could execute arbitrary code!")

        logger.warning("⚠️  Workflow will be executed despite security risks (developer mode)")
        logger.info("✅ Workflow allowed (developer mode - NOT secure)")

        return True


class WorkflowVettingService:
    """
    Main service for workflow vetting.

    Selects the appropriate policy based on execution mode and validates workflows.
    """

    def __init__(self):
        self.settings = get_settings()
        self.policy = self._get_policy()

    def _get_policy(self) -> WorkflowVettingPolicy:
        """Select the appropriate vetting policy based on execution mode."""
        mode = self.settings.jynco_execution_mode

        if mode == "production":
            return ProductionVettingPolicy(self.settings)
        elif mode == "self-hosted-production":
            return SelfHostedVettingPolicy(self.settings)
        else:  # developer
            return DeveloperVettingPolicy(self.settings)

    def vet_workflow(self, workflow: Dict[str, Any], workflow_id: Optional[str] = None) -> bool:
        """
        Vet a workflow before execution.

        Args:
            workflow: The ComfyUI workflow JSON
            workflow_id: Optional workflow identifier for logging

        Returns:
            True if workflow is allowed to execute

        Raises:
            SecurityViolation: If workflow violates security policy
        """
        workflow_id = workflow_id or self._compute_workflow_hash(workflow)

        logger.info(f"Vetting workflow {workflow_id}")

        try:
            result = self.policy.validate(workflow)
            self._log_vetting_result(workflow_id, True, None)
            return result

        except SecurityViolation as e:
            self._log_vetting_result(workflow_id, False, str(e))
            raise

    def _compute_workflow_hash(self, workflow: Dict[str, Any]) -> str:
        """Compute a hash of the workflow for identification."""
        import json
        workflow_json = json.dumps(workflow, sort_keys=True)
        return hashlib.sha256(workflow_json.encode()).hexdigest()[:12]

    def _log_vetting_result(self, workflow_id: str, approved: bool, reason: Optional[str]):
        """Log the vetting result for audit purposes."""
        # TODO: Store in audit log table
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_id,
            "execution_mode": self.settings.jynco_execution_mode,
            "approved": approved,
            "reason": reason
        }

        if approved:
            logger.info(f"Audit: Workflow {workflow_id} approved")
        else:
            logger.warning(f"Audit: Workflow {workflow_id} rejected - {reason}")


# Singleton instance
_vetting_service: Optional[WorkflowVettingService] = None


def get_vetting_service() -> WorkflowVettingService:
    """Get the singleton vetting service instance."""
    global _vetting_service
    if _vetting_service is None:
        _vetting_service = WorkflowVettingService()
    return _vetting_service
