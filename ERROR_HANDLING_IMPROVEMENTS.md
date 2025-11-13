# ComfyUI Error Handling Improvements

## Overview

This document summarizes the comprehensive error handling improvements made to the ComfyUI integration, providing better user feedback and a more robust video generation experience.

## Summary of Changes

### 1. Custom Exception Classes

**File:** `/home/user/Jynco/workers/ai_worker/adapters/exceptions.py`

Created specific exception classes for different error types:

- `AdapterError` - Base exception with error code and retryability flag
- `ComfyUIConnectionError` - Service not reachable
- `ComfyUITimeoutError` - Request/generation timeout
- `ComfyUIWorkflowError` - Invalid workflow JSON
- `ComfyUIMissingNodeError` - Missing models/nodes
- `ComfyUIInvalidParametersError` - Invalid parameters
- `ComfyUIGenerationError` - Generation process failure
- `ComfyUIOutputError` - No valid output produced

Each exception includes:
- Human-readable error message
- `is_retryable` flag to distinguish transient vs permanent failures
- `error_code` for machine-readable frontend integration
- User-friendly message mapping with troubleshooting tips

### 2. Enhanced ComfyUIAdapter

**File:** `/home/user/Jynco/workers/ai_worker/adapters/comfyui.py`

Improvements:
- **Retry Logic**: Added `@retry` decorator with exponential backoff for transient failures (connection errors, timeouts)
- **Detailed Logging**: Added structured logging at INFO, DEBUG, and ERROR levels
- **Health Check Method**: New `health_check()` method to verify ComfyUI connectivity
- **Timeout Configuration**: Separate timeouts for requests (30s) and generation (300s)
- **Error Detection**: Intelligent error type detection from ComfyUI responses
- **Specific Error Handling**: Catches and raises appropriate exception types based on error content

Key methods improved:
- `initiate_generation()` - Better error handling with retry logic
- `get_status()` - More robust status checking
- `get_result()` - Enhanced error parsing and output validation
- `cancel_generation()` - Added logging

### 3. Improved AI Worker Error Handling

**File:** `/home/user/Jynco/workers/ai_worker/worker.py`

Improvements:
- **Structured Error Handling**: New `_handle_segment_failure()` method for centralized error processing
- **Error Code Storage**: Stores both user-friendly messages and error codes in database
- **Retryability Detection**: Automatically determines if errors are retryable based on error codes
- **Better Exception Handling**: Separate handling for `AdapterError`, `TimeoutError`, and generic exceptions
- **Detailed Logging**: Context-rich error logging with segment ID, error code, and retryability info

Error codes tracked:
- `COMFYUI_CONNECTION_ERROR` (retryable)
- `COMFYUI_TIMEOUT` (retryable)
- `COMFYUI_GENERATION_ERROR` (retryable)
- `COMFYUI_WORKFLOW_ERROR` (not retryable)
- `COMFYUI_MISSING_NODE` (not retryable)
- `COMFYUI_INVALID_PARAMETERS` (not retryable)
- `COMFYUI_OUTPUT_ERROR` (not retryable)
- `INTERNAL_ERROR` (not retryable)

### 4. Database Schema Updates

**Files:**
- `/home/user/Jynco/backend/models/segment.py`
- `/home/user/Jynco/backend/schemas/segment.py`
- `/home/user/Jynco/backend/migrations/001_add_error_code_to_segments.sql`

Added `error_code` field to Segment model:
- Stores machine-readable error codes
- Added to both SQLAlchemy model and Pydantic schema
- Indexed for faster queries
- Migration script provided for database upgrade

### 5. Health Check Endpoint

**File:** `/home/user/Jynco/backend/api/health.py`

New endpoints:
- `GET /api/health/comfyui` - Check ComfyUI service health
- `GET /api/health/` - Overall system health including all components

Returns:
- Service status (healthy/unhealthy/unavailable)
- Connection details
- System stats when available

### 6. Retry Segment API Endpoint

**File:** `/home/user/Jynco/backend/api/segments.py`

New endpoint:
- `POST /api/segments/{segment_id}/retry` - Retry a failed segment

Features:
- Only allows retry for failed segments
- Resets segment to pending state
- Clears error information
- Allows re-processing by render jobs

### 7. Frontend Error Display Improvements

**Files:**
- `/home/user/Jynco/frontend/src/utils/errorMessages.ts` - Error message utilities
- `/home/user/Jynco/frontend/src/api/projects.ts` - Added retry API method
- `/home/user/Jynco/frontend/src/features/timeline/SegmentCard.tsx` - Enhanced UI
- `/home/user/Jynco/frontend/src/features/timeline/TimelineEditor.tsx` - Retry integration

Improvements:
- **User-Friendly Messages**: Maps error codes to user-friendly messages
- **Troubleshooting Hints**: Provides actionable troubleshooting steps
- **Retry Button**: Shows for retryable errors with loading state
- **Better Visual Design**: Red-themed error card with clear information hierarchy
- **Error Code Display**: Shows technical error code for debugging

UI Features:
- Error icon with user-friendly message
- Troubleshooting guidance
- Error code in monospace font
- Retry button (only for retryable errors)
- Loading state during retry

## User Experience Improvements

### Before
- Generic error messages: "Failed to generate video"
- No guidance on what to do next
- No way to retry without deleting and recreating segment
- No visibility into whether errors are temporary or permanent

### After
- Specific error messages: "Cannot connect to video generation service"
- Clear troubleshooting guidance: "Please try again in a few moments..."
- One-click retry for transient failures
- Visual distinction between retryable and permanent failures
- Error codes for technical support

## Error Flow Example

1. **Error Occurs**: ComfyUI service is temporarily unavailable
2. **Adapter**: Catches `httpx.ConnectError`, raises `ComfyUIConnectionError`
3. **Worker**: Catches exception, stores error message and code in database
4. **Frontend**: Displays user-friendly message with retry button
5. **User**: Clicks retry button
6. **Backend**: Resets segment to pending, re-queues for processing
7. **Worker**: Picks up segment again, succeeds if service is back

## Testing Recommendations

### Backend Testing
```bash
# Test health check
curl http://localhost:8000/api/health/comfyui

# Test retry endpoint
curl -X POST http://localhost:8000/api/segments/{segment_id}/retry
```

### Frontend Testing
1. Create a segment with ComfyUI model
2. Stop ComfyUI service to trigger connection error
3. Verify error message appears with retry button
4. Start ComfyUI service
5. Click retry button and verify segment regenerates

### Integration Testing
1. Test various error scenarios:
   - ComfyUI service down (connection error)
   - Invalid workflow JSON (workflow error)
   - Missing nodes (missing node error)
   - Invalid parameters (parameter error)
   - Generation timeout (timeout error)
2. Verify correct error codes are stored
3. Verify retry button appears only for retryable errors
4. Verify retry functionality works end-to-end

## Migration Instructions

### Database Migration

Run the migration to add the `error_code` field:

```bash
# Using psql
psql -h localhost -U your_user -d your_database -f backend/migrations/001_add_error_code_to_segments.sql

# Or using Docker
docker exec -i postgres_container psql -U postgres -d jynco < backend/migrations/001_add_error_code_to_segments.sql
```

### Dependencies

Ensure these packages are installed:
- `tenacity` - For retry logic (already in requirements)
- `httpx` - For async HTTP (already in requirements)

No additional dependencies required.

## Configuration

### ComfyUI Adapter Configuration

```python
config = {
    "comfyui_url": "http://comfyui:8188",
    "request_timeout": 30.0,  # seconds
    "generation_timeout": 300.0,  # seconds
    "default_workflow": {...}  # optional
}

adapter = ComfyUIAdapter(config=config)
```

### Worker Configuration

No additional configuration required. Error handling is automatic.

## Monitoring and Logging

### Log Levels

- **INFO**: Successful operations, job start/completion
- **DEBUG**: Detailed flow information (status checks, etc.)
- **WARNING**: Recoverable issues (timeouts on status check)
- **ERROR**: Failures requiring attention

### Log Examples

```
INFO - Initiating ComfyUI generation with prompt: A cat walking...
ERROR - ComfyUI job abc123 failed: Missing required node: VideoLinearCFGGuidance (code: COMFYUI_MISSING_NODE, retryable: False)
INFO - ComfyUI job def456 completed successfully
```

### Metrics to Monitor

- Error rate by error code
- Retry success rate
- Average time to failure
- Health check response times

## Important Notes

### Security
- Error messages shown to users don't expose internal details
- Detailed technical errors are logged server-side
- Error codes are safe to expose to frontend

### Performance
- Retry logic uses exponential backoff (2s, 4s, 8s)
- Health checks have 5s timeout
- Status checks are non-blocking

### Scalability
- Error handling is stateless
- Retry logic in adapter doesn't affect other jobs
- Database indexes added for error_code queries

## Future Enhancements

Potential improvements:
1. **Automatic Retry**: Automatically retry transient failures a few times before marking as failed
2. **Error Analytics**: Track error patterns and rates in dashboard
3. **Smart Throttling**: Reduce request rate when service is overloaded
4. **Error Notifications**: Email/Slack notifications for persistent errors
5. **Circuit Breaker**: Temporarily stop sending requests to failing services
6. **Error Recovery Suggestions**: AI-powered suggestions for fixing errors

## Files Modified/Created

### Backend
- ✨ Created: `workers/ai_worker/adapters/exceptions.py`
- 📝 Modified: `workers/ai_worker/adapters/comfyui.py`
- 📝 Modified: `workers/ai_worker/worker.py`
- 📝 Modified: `backend/models/segment.py`
- 📝 Modified: `backend/schemas/segment.py`
- ✨ Created: `backend/api/health.py`
- 📝 Modified: `backend/api/segments.py`
- 📝 Modified: `backend/main.py`
- ✨ Created: `backend/migrations/001_add_error_code_to_segments.sql`
- ✨ Created: `backend/migrations/README.md`

### Frontend
- ✨ Created: `frontend/src/utils/errorMessages.ts`
- 📝 Modified: `frontend/src/api/projects.ts`
- 📝 Modified: `frontend/src/features/timeline/SegmentCard.tsx`
- 📝 Modified: `frontend/src/features/timeline/TimelineEditor.tsx`

### Documentation
- ✨ Created: `ERROR_HANDLING_IMPROVEMENTS.md` (this file)

## Support

For questions or issues related to error handling:
1. Check logs for detailed error information
2. Verify ComfyUI service is running: `GET /api/health/comfyui`
3. Review error codes in database
4. Check frontend console for API errors

## Conclusion

These improvements provide a robust error handling system that:
- ✅ Gives users clear, actionable feedback
- ✅ Distinguishes between retryable and permanent failures
- ✅ Provides easy retry functionality
- ✅ Logs detailed information for debugging
- ✅ Maintains service health visibility
- ✅ Improves overall user experience

The system is production-ready and designed for maintainability and extensibility.
