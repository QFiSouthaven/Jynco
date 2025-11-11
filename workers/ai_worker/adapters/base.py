"""
Base interface for AI video generation models.
Implements the Strategy pattern for pluggable model adapters.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class GenerationStatus(str, Enum):
    """Status of video generation task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationResult:
    """Result of video generation."""
    status: GenerationStatus
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    external_job_id: Optional[str] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VideoModelInterface(ABC):
    """
    Abstract base class for AI video generation models.

    This interface defines the contract that all video generation
    model adapters must implement, following the Strategy pattern.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the video model adapter.

        Args:
            api_key: API key for the video generation service
            config: Additional configuration options
        """
        self.api_key = api_key
        self.config = config or {}

    @abstractmethod
    async def initiate_generation(
        self,
        prompt: str,
        model_params: Dict[str, Any]
    ) -> str:
        """
        Initiate video generation with the AI model.

        Args:
            prompt: Text prompt describing the video to generate
            model_params: Model-specific parameters (duration, resolution, etc.)

        Returns:
            external_job_id: Job ID from the external AI service

        Raises:
            Exception: If generation fails to start
        """
        pass

    @abstractmethod
    async def get_status(self, external_job_id: str) -> GenerationStatus:
        """
        Check the status of a generation job.

        Args:
            external_job_id: Job ID from the external AI service

        Returns:
            Current status of the generation job

        Raises:
            Exception: If status check fails
        """
        pass

    @abstractmethod
    async def get_result(self, external_job_id: str) -> GenerationResult:
        """
        Retrieve the result of a completed generation job.

        Args:
            external_job_id: Job ID from the external AI service

        Returns:
            GenerationResult with video URL and metadata

        Raises:
            Exception: If retrieval fails or job is not complete
        """
        pass

    @abstractmethod
    async def cancel_generation(self, external_job_id: str) -> bool:
        """
        Cancel an in-progress generation job.

        Args:
            external_job_id: Job ID from the external AI service

        Returns:
            True if cancellation succeeded, False otherwise
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name/identifier of this model."""
        pass

    def validate_params(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize model parameters.
        Can be overridden by subclasses for model-specific validation.

        Args:
            model_params: Raw model parameters

        Returns:
            Validated and normalized parameters

        Raises:
            ValueError: If parameters are invalid
        """
        return model_params
