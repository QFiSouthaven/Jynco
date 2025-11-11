"""
Base Agent Class

Abstract base class for all agents in the Video Generation Foundry.
Defines the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class BaseAgent(ABC):
    """
    Abstract base class for all Jynco agents.

    All agents follow these principles:
    - They are stateless and coordinate through the storyboard
    - They wrap external tools and AI models
    - They report their status and errors clearly
    - They operate asynchronously where appropriate
    """

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.

        Args:
            agent_id: Unique identifier for this agent instance
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for this agent."""
        logger = logging.getLogger(f"jynco.agent.{self.agent_id}")
        logger.setLevel(self.config.get("log_level", "INFO"))
        return logger

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            task: Dictionary containing task parameters

        Returns:
            Dictionary containing the result or error information
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.

        Returns:
            Dictionary with agent status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "status": "idle",
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_task(self, task: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that a task contains all required fields.

        Args:
            task: Task dictionary to validate
            required_fields: List of required field names

        Returns:
            True if valid, raises ValueError if invalid
        """
        missing_fields = [field for field in required_fields if field not in task]
        if missing_fields:
            raise ValueError(f"Task missing required fields: {missing_fields}")
        return True

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors consistently across agents.

        Args:
            error: The exception that occurred
            context: Context information about the task

        Returns:
            Standardized error response dictionary
        """
        self.logger.error(f"Error in {self.agent_id}: {str(error)}", exc_info=True)
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "agent_id": self.agent_id,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
