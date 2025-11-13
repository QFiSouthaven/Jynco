"""
API routes for health checks and system status.
"""
from fastapi import APIRouter, status
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try importing ComfyUI adapter
try:
    from workers.ai_worker.adapters.comfyui import ComfyUIAdapter
    from workers.ai_worker.adapters.exceptions import AdapterError
    COMFYUI_AVAILABLE = True
except ImportError:
    COMFYUI_AVAILABLE = False
    ComfyUIAdapter = None

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/comfyui", response_model=Dict[str, Any])
async def check_comfyui_health():
    """
    Check ComfyUI service health and connectivity.

    Returns:
        Health status information including connectivity and system stats
    """
    if not COMFYUI_AVAILABLE:
        return {
            "status": "unavailable",
            "error": "ComfyUI adapter not available",
            "details": None
        }

    try:
        # Create ComfyUI adapter instance
        adapter = ComfyUIAdapter()

        # Perform health check
        health_info = await adapter.health_check()

        # Clean up
        await adapter.close()

        return health_info

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "details": None
        }


@router.get("/", response_model=Dict[str, Any])
async def check_system_health():
    """
    Check overall system health including all components.

    Returns:
        Comprehensive health status for all system components
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }

    # Check ComfyUI
    comfyui_health = await check_comfyui_health()
    health_status["components"]["comfyui"] = comfyui_health

    # Determine overall status
    if comfyui_health["status"] in ["unhealthy", "error"]:
        health_status["status"] = "degraded"
    elif comfyui_health["status"] == "unavailable":
        health_status["status"] = "partial"

    return health_status
