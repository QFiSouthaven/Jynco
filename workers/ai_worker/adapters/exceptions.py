"""
Custom exceptions for AI video generation adapters.
Provides specific error types for better error handling and user feedback.
"""


class AdapterError(Exception):
    """Base exception for all adapter errors."""

    def __init__(self, message: str, is_retryable: bool = False, error_code: str = None):
        """
        Initialize adapter error.

        Args:
            message: Human-readable error message
            is_retryable: Whether this error can be retried
            error_code: Machine-readable error code for frontend
        """
        super().__init__(message)
        self.message = message
        self.is_retryable = is_retryable
        self.error_code = error_code or self.__class__.__name__


class ComfyUIConnectionError(AdapterError):
    """ComfyUI service is not reachable."""

    def __init__(self, message: str = None, url: str = None):
        default_message = "Cannot connect to ComfyUI service"
        if url:
            default_message += f" at {url}"
        default_message += ". Please ensure ComfyUI is running."

        super().__init__(
            message=message or default_message,
            is_retryable=True,
            error_code="COMFYUI_CONNECTION_ERROR"
        )


class ComfyUITimeoutError(AdapterError):
    """ComfyUI request timed out."""

    def __init__(self, message: str = None, timeout: int = None):
        default_message = "Request to ComfyUI timed out"
        if timeout:
            default_message += f" after {timeout}s"
        default_message += ". The service may be overloaded."

        super().__init__(
            message=message or default_message,
            is_retryable=True,
            error_code="COMFYUI_TIMEOUT"
        )


class ComfyUIWorkflowError(AdapterError):
    """Invalid or malformed workflow JSON."""

    def __init__(self, message: str = None, details: str = None):
        default_message = "Invalid workflow configuration"
        if details:
            default_message += f": {details}"

        super().__init__(
            message=message or default_message,
            is_retryable=False,
            error_code="COMFYUI_WORKFLOW_ERROR"
        )


class ComfyUIMissingNodeError(AdapterError):
    """Required node or model is missing in ComfyUI."""

    def __init__(self, message: str = None, node_name: str = None):
        default_message = "Required node or model is missing in ComfyUI"
        if node_name:
            default_message += f": {node_name}"
        default_message += ". Please install the required dependencies."

        super().__init__(
            message=message or default_message,
            is_retryable=False,
            error_code="COMFYUI_MISSING_NODE"
        )


class ComfyUIInvalidParametersError(AdapterError):
    """Invalid parameters provided to ComfyUI."""

    def __init__(self, message: str = None, param_name: str = None):
        default_message = "Invalid parameters provided"
        if param_name:
            default_message += f": {param_name}"

        super().__init__(
            message=message or default_message,
            is_retryable=False,
            error_code="COMFYUI_INVALID_PARAMETERS"
        )


class ComfyUIGenerationError(AdapterError):
    """Error during video generation process."""

    def __init__(self, message: str = None, details: str = None):
        default_message = "Video generation failed"
        if details:
            default_message += f": {details}"

        super().__init__(
            message=message or default_message,
            is_retryable=True,
            error_code="COMFYUI_GENERATION_ERROR"
        )


class ComfyUIOutputError(AdapterError):
    """No valid output was produced by ComfyUI."""

    def __init__(self, message: str = None):
        default_message = message or "No video output was generated. The workflow may not be configured correctly."

        super().__init__(
            message=default_message,
            is_retryable=False,
            error_code="COMFYUI_OUTPUT_ERROR"
        )


# Error code to user-friendly message mapping
ERROR_MESSAGES = {
    "COMFYUI_CONNECTION_ERROR": {
        "user_message": "Cannot connect to video generation service",
        "troubleshooting": "Please try again in a few moments. If the problem persists, contact support."
    },
    "COMFYUI_TIMEOUT": {
        "user_message": "Video generation is taking longer than expected",
        "troubleshooting": "The service may be busy. Please try again later."
    },
    "COMFYUI_WORKFLOW_ERROR": {
        "user_message": "Invalid workflow configuration",
        "troubleshooting": "Please check your settings or contact support."
    },
    "COMFYUI_MISSING_NODE": {
        "user_message": "Required model or component is missing",
        "troubleshooting": "Please contact support to install the required components."
    },
    "COMFYUI_INVALID_PARAMETERS": {
        "user_message": "Invalid generation parameters",
        "troubleshooting": "Please check your prompt and settings."
    },
    "COMFYUI_GENERATION_ERROR": {
        "user_message": "Video generation failed",
        "troubleshooting": "Please try again. If the problem persists, try simplifying your prompt."
    },
    "COMFYUI_OUTPUT_ERROR": {
        "user_message": "No video was generated",
        "troubleshooting": "Please try again or contact support if the problem persists."
    }
}


def get_user_friendly_message(error_code: str) -> dict:
    """
    Get user-friendly error message and troubleshooting for an error code.

    Args:
        error_code: The error code

    Returns:
        Dictionary with user_message and troubleshooting
    """
    return ERROR_MESSAGES.get(error_code, {
        "user_message": "An unexpected error occurred",
        "troubleshooting": "Please try again or contact support."
    })
