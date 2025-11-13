/**
 * User-friendly error messages and troubleshooting tips for video generation errors.
 */

interface ErrorInfo {
  userMessage: string
  troubleshooting: string
}

const ERROR_MESSAGES: Record<string, ErrorInfo> = {
  COMFYUI_CONNECTION_ERROR: {
    userMessage: 'Cannot connect to video generation service',
    troubleshooting: 'Please try again in a few moments. If the problem persists, contact support.',
  },
  COMFYUI_TIMEOUT: {
    userMessage: 'Video generation is taking longer than expected',
    troubleshooting: 'The service may be busy. Please try again later.',
  },
  COMFYUI_WORKFLOW_ERROR: {
    userMessage: 'Invalid workflow configuration',
    troubleshooting: 'Please check your settings or contact support.',
  },
  COMFYUI_MISSING_NODE: {
    userMessage: 'Required model or component is missing',
    troubleshooting: 'Please contact support to install the required components.',
  },
  COMFYUI_INVALID_PARAMETERS: {
    userMessage: 'Invalid generation parameters',
    troubleshooting: 'Please check your prompt and settings.',
  },
  COMFYUI_GENERATION_ERROR: {
    userMessage: 'Video generation failed',
    troubleshooting: 'Please try again. If the problem persists, try simplifying your prompt.',
  },
  COMFYUI_OUTPUT_ERROR: {
    userMessage: 'No video was generated',
    troubleshooting: 'Please try again or contact support if the problem persists.',
  },
  INTERNAL_ERROR: {
    userMessage: 'An unexpected error occurred',
    troubleshooting: 'Please try again or contact support.',
  },
}

/**
 * Get user-friendly error information for an error code.
 * Falls back to generic message if error code is unknown.
 */
export function getErrorInfo(errorCode?: string | null): ErrorInfo {
  if (!errorCode) {
    return {
      userMessage: 'An error occurred during video generation',
      troubleshooting: 'Please try again or contact support if the problem persists.',
    }
  }

  return (
    ERROR_MESSAGES[errorCode] || {
      userMessage: 'An error occurred during video generation',
      troubleshooting: 'Please try again or contact support if the problem persists.',
    }
  )
}

/**
 * Check if an error is retryable based on error code.
 */
export function isRetryableError(errorCode?: string | null): boolean {
  if (!errorCode) return true

  const retryableErrors = [
    'COMFYUI_CONNECTION_ERROR',
    'COMFYUI_TIMEOUT',
    'COMFYUI_GENERATION_ERROR',
  ]

  return retryableErrors.includes(errorCode)
}
