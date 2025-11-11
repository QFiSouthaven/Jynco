"""
Factory for creating video model adapters based on configuration.
"""
from typing import Dict, Any, Optional
import os

from .base import VideoModelInterface
from .runway import RunwayGen3Adapter
from .stability import StabilityAIAdapter
from .mock import MockAIAdapter


class VideoModelFactory:
    """
    Factory class for creating video model adapters.
    Uses the Factory pattern to instantiate the correct adapter based on model name.
    """

    # Registry of available model adapters
    _adapters = {
        "runway-gen3": RunwayGen3Adapter,
        "runway": RunwayGen3Adapter,  # Alias
        "stability-ai": StabilityAIAdapter,
        "stability": StabilityAIAdapter,  # Alias
        "mock-ai": MockAIAdapter,
        "mock": MockAIAdapter  # Alias
    }

    @classmethod
    def create(
        cls,
        model_name: str,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> VideoModelInterface:
        """
        Create a video model adapter instance.

        Args:
            model_name: Name of the model (e.g., "runway-gen3", "stability-ai")
            api_key: API key for the model service (if None, will try to get from env)
            config: Additional configuration for the adapter

        Returns:
            VideoModelInterface instance

        Raises:
            ValueError: If model_name is not supported
            ValueError: If API key is missing and required
        """
        model_name_lower = model_name.lower()

        if model_name_lower not in cls._adapters:
            supported = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unsupported model: {model_name}. "
                f"Supported models: {supported}"
            )

        adapter_class = cls._adapters[model_name_lower]

        # Get API key from environment if not provided
        if api_key is None:
            api_key = cls._get_api_key_from_env(model_name_lower)

        # Mock adapter doesn't require a real API key
        if model_name_lower in ["mock", "mock-ai"]:
            api_key = api_key or "mock_key"

        if not api_key:
            raise ValueError(
                f"API key required for {model_name}. "
                f"Provide via api_key parameter or environment variable."
            )

        return adapter_class(api_key=api_key, config=config)

    @classmethod
    def _get_api_key_from_env(cls, model_name: str) -> Optional[str]:
        """
        Get API key from environment variables based on model name.

        Args:
            model_name: Name of the model

        Returns:
            API key from environment or None
        """
        env_var_map = {
            "runway-gen3": "RUNWAY_API_KEY",
            "runway": "RUNWAY_API_KEY",
            "stability-ai": "STABILITY_API_KEY",
            "stability": "STABILITY_API_KEY",
            "mock": None,
            "mock-ai": None
        }

        env_var = env_var_map.get(model_name)
        if env_var:
            return os.getenv(env_var)

        return None

    @classmethod
    def register_adapter(
        cls,
        model_name: str,
        adapter_class: type[VideoModelInterface]
    ):
        """
        Register a new custom adapter.

        Args:
            model_name: Name to register the adapter under
            adapter_class: Class implementing VideoModelInterface
        """
        if not issubclass(adapter_class, VideoModelInterface):
            raise ValueError(
                f"Adapter class must inherit from VideoModelInterface"
            )

        cls._adapters[model_name.lower()] = adapter_class

    @classmethod
    def list_supported_models(cls) -> list[str]:
        """
        Get list of supported model names.

        Returns:
            List of supported model names
        """
        return list(cls._adapters.keys())
