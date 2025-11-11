"""
Storyboard Agent

Manages the central storyboard.json state document.
Acts as the single source of truth for project state.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .base_agent import BaseAgent
from ..schemas.storyboard_types import Storyboard, TimelineClip, ClipStatus


class StoryboardAgent(BaseAgent):
    """
    The Storyboard Agent is responsible for:
    - Reading and writing the storyboard.json file
    - Updating clip status, jobIds, and error messages
    - Providing a consistent interface for state mutations
    - Ensuring atomic updates to prevent corruption
    """

    def __init__(self, agent_id: str = "storyboard_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.storyboard_path = Path(config.get("storyboard_path", "storyboard.json"))
        self._lock = asyncio.Lock()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a storyboard operation.

        Supported operations:
        - create: Create a new storyboard
        - read: Read the current storyboard
        - update_clip: Update a clip's status/properties
        - add_clip: Add a new clip to the timeline
        - get_clip: Retrieve a specific clip

        Args:
            task: {
                "operation": "create|read|update_clip|add_clip|get_clip",
                "data": {...}  # Operation-specific data
            }
        """
        try:
            self.validate_task(task, ["operation"])
            operation = task["operation"]

            operations = {
                "create": self._create_storyboard,
                "read": self._read_storyboard,
                "update_clip": self._update_clip,
                "add_clip": self._add_clip,
                "get_clip": self._get_clip,
            }

            if operation not in operations:
                raise ValueError(f"Unknown operation: {operation}")

            return await operations[operation](task.get("data", {}))

        except Exception as e:
            return await self.handle_error(e, task)

    async def _create_storyboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new storyboard."""
        async with self._lock:
            try:
                storyboard = Storyboard(
                    projectId=data.get("projectId", f"proj_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
                    outputSettings=data.get("outputSettings"),
                    timeline=data.get("timeline", []),
                    metadata=data.get("metadata", {})
                )

                await self._write_storyboard(storyboard)

                self.logger.info(f"Created new storyboard: {storyboard.projectId}")
                return {
                    "success": True,
                    "projectId": storyboard.projectId,
                    "storyboard": self._serialize_storyboard(storyboard)
                }
            except Exception as e:
                raise ValueError(f"Failed to create storyboard: {str(e)}")

    async def _read_storyboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Read the current storyboard."""
        async with self._lock:
            if not self.storyboard_path.exists():
                return {
                    "success": False,
                    "error": "Storyboard file not found"
                }

            with open(self.storyboard_path, 'r') as f:
                storyboard_data = json.load(f)

            return {
                "success": True,
                "storyboard": storyboard_data
            }

    async def _update_clip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a clip's properties.

        Required fields in data:
        - clipId: ID of the clip to update

        Optional fields:
        - status: New status
        - jobId: Job ID to associate
        - errorMessage: Error message if failed
        - sourceFile: Path to generated file
        - cacheKey: Cache key for the clip
        """
        async with self._lock:
            self.validate_task(data, ["clipId"])

            storyboard = await self._load_storyboard()
            clip = storyboard.get_clip_by_id(data["clipId"])

            if not clip:
                return {
                    "success": False,
                    "error": f"Clip not found: {data['clipId']}"
                }

            # Update clip properties
            if "status" in data:
                clip.status = ClipStatus(data["status"])
            if "jobId" in data:
                clip.jobId = data["jobId"]
            if "errorMessage" in data:
                clip.errorMessage = data["errorMessage"]
            if "sourceFile" in data:
                clip.sourceFile = data["sourceFile"]
            if "cacheKey" in data:
                clip.cacheKey = data["cacheKey"]

            # Update metadata timestamp
            if isinstance(storyboard.metadata, dict):
                storyboard.metadata["updatedAt"] = datetime.utcnow().isoformat()
            else:
                storyboard.metadata.updatedAt = datetime.utcnow()

            await self._write_storyboard(storyboard)

            self.logger.info(f"Updated clip {data['clipId']}: {data.get('status', 'properties changed')}")

            return {
                "success": True,
                "clipId": data["clipId"],
                "clip": self._serialize_clip(clip)
            }

    async def _add_clip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new clip to the timeline."""
        async with self._lock:
            self.validate_task(data, ["clipId", "motionPrompt"])

            storyboard = await self._load_storyboard()

            # Check for duplicate clipId
            if storyboard.get_clip_by_id(data["clipId"]):
                return {
                    "success": False,
                    "error": f"Clip already exists: {data['clipId']}"
                }

            # Create new clip
            clip = TimelineClip(
                clipId=data["clipId"],
                status=ClipStatus.PENDING,
                motionPrompt=data["motionPrompt"],
                sourceImage=data.get("sourceImage"),
                duration=data.get("duration"),
                startTime=data.get("startTime")
            )

            storyboard.timeline.append(clip)
            # Update metadata timestamp
            if isinstance(storyboard.metadata, dict):
                storyboard.metadata["updatedAt"] = datetime.utcnow().isoformat()
            else:
                storyboard.metadata.updatedAt = datetime.utcnow()

            await self._write_storyboard(storyboard)

            self.logger.info(f"Added clip {clip.clipId} to timeline")

            return {
                "success": True,
                "clipId": clip.clipId,
                "clip": self._serialize_clip(clip)
            }

    async def _get_clip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a specific clip by ID."""
        self.validate_task(data, ["clipId"])

        storyboard = await self._load_storyboard()
        clip = storyboard.get_clip_by_id(data["clipId"])

        if not clip:
            return {
                "success": False,
                "error": f"Clip not found: {data['clipId']}"
            }

        return {
            "success": True,
            "clip": self._serialize_clip(clip)
        }

    async def _load_storyboard(self) -> Storyboard:
        """Load storyboard from disk."""
        if not self.storyboard_path.exists():
            raise FileNotFoundError(f"Storyboard not found at {self.storyboard_path}")

        with open(self.storyboard_path, 'r') as f:
            data = json.load(f)

        # TODO: Implement proper deserialization from dict to Storyboard object
        # For now, return a basic Storyboard
        return Storyboard(**data)

    async def _write_storyboard(self, storyboard: Storyboard) -> None:
        """Write storyboard to disk atomically."""
        temp_path = self.storyboard_path.with_suffix('.tmp')

        with open(temp_path, 'w') as f:
            json.dump(self._serialize_storyboard(storyboard), f, indent=2)

        # Atomic rename
        temp_path.replace(self.storyboard_path)

    def _serialize_storyboard(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Convert Storyboard object to dictionary."""
        def to_dict(obj):
            """Convert object to dict, handling both dict and dataclass types."""
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                        result[key] = to_dict(value)
                    elif isinstance(value, list):
                        result[key] = [to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[key] = value
                return result
            return obj

        return {
            "version": storyboard.version,
            "projectId": storyboard.projectId,
            "outputSettings": to_dict(storyboard.outputSettings),
            "timeline": [self._serialize_clip(clip) for clip in storyboard.timeline],
            "layers": to_dict(storyboard.layers),
            "metadata": to_dict(storyboard.metadata)
        }

    def _serialize_clip(self, clip: TimelineClip) -> Dict[str, Any]:
        """Convert TimelineClip to dictionary."""
        def to_dict(obj):
            """Convert object to dict, handling both dict and dataclass types."""
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                        result[key] = to_dict(value)
                    elif isinstance(value, list):
                        result[key] = [to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[key] = value
                return result
            return obj

        return {
            "clipId": clip.clipId,
            "status": clip.status.value if hasattr(clip.status, 'value') else clip.status,
            "jobId": clip.jobId,
            "errorMessage": clip.errorMessage,
            "sourceFile": clip.sourceFile,
            "motionPrompt": clip.motionPrompt,
            "sourceImage": clip.sourceImage,
            "duration": clip.duration,
            "startTime": clip.startTime,
            "cacheKey": clip.cacheKey,
            "effects": to_dict(clip.effects)
        }
