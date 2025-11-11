"""
AI Model Adapters for Video Generation.

This module implements the Strategy/Adapter pattern to provide
a unified interface for different AI video generation models.
"""
from .base import VideoModelInterface, GenerationStatus
from .runway import RunwayGen3Adapter
from .stability import StabilityAIAdapter
from .mock import MockAIAdapter
from .local_sd import LocalStableDiffusionAdapter
from .factory import VideoModelFactory

__all__ = [
    "VideoModelInterface",
    "GenerationStatus",
    "RunwayGen3Adapter",
    "StabilityAIAdapter",
    "MockAIAdapter",
    "LocalStableDiffusionAdapter",
    "VideoModelFactory"
]
