"""
Jynco Storyboard Schema Type Definitions (v1.2)

Python type definitions for the Video Generation Foundry storyboard schema.
Provides strong typing and validation for storyboard data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Literal
from datetime import datetime
from enum import Enum


class ClipStatus(str, Enum):
    """Status of a clip in the generation pipeline."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoCodec(str, Enum):
    """Supported video codecs."""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"


class TransitionType(str, Enum):
    """Video transition types."""
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    NONE = "none"


class FilterType(str, Enum):
    """Post-processing filter types."""
    BLUR = "blur"
    SHARPEN = "sharpen"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"


@dataclass
class Resolution:
    """Video resolution settings."""
    width: int
    height: int

    def __post_init__(self):
        if self.width < 1 or self.height < 1:
            raise ValueError("Resolution dimensions must be positive integers")


@dataclass
class OutputSettings:
    """Output video configuration settings."""
    resolution: Resolution
    fps: int
    codec: VideoCodec
    bitrate: Optional[str] = None

    def __post_init__(self):
        if not 1 <= self.fps <= 120:
            raise ValueError("FPS must be between 1 and 120")


@dataclass
class Transition:
    """Transition effects for a clip."""
    in_transition: TransitionType = TransitionType.NONE
    out_transition: TransitionType = TransitionType.NONE


@dataclass
class Filter:
    """Post-processing filter definition."""
    type: FilterType
    intensity: float = 0.5

    def __post_init__(self):
        if not 0 <= self.intensity <= 1:
            raise ValueError("Filter intensity must be between 0 and 1")


@dataclass
class Effects:
    """Post-processing effects for a clip."""
    transitions: Optional[Transition] = None
    filters: List[Filter] = field(default_factory=list)


@dataclass
class TimelineClip:
    """
    A single video clip in the timeline.

    Represents both the generation state and the final clip properties.
    Supports the resilient generation pipeline with status tracking.
    """
    clipId: str
    status: ClipStatus
    motionPrompt: str
    sourceImage: Optional[str] = None
    jobId: Optional[str] = None
    errorMessage: Optional[str] = None
    sourceFile: Optional[str] = None
    duration: Optional[float] = None
    startTime: Optional[float] = None
    effects: Effects = field(default_factory=Effects)
    cacheKey: Optional[str] = None

    def __post_init__(self):
        if not self.clipId.startswith("clip_"):
            raise ValueError("clipId must start with 'clip_'")
        if self.jobId and not (self.jobId.startswith("job_motion_") or self.jobId.startswith("job_render_")):
            raise ValueError("jobId must start with 'job_motion_' or 'job_render_'")
        if self.status == ClipStatus.FAILED and not self.errorMessage:
            raise ValueError("errorMessage is required when status is 'failed'")


@dataclass
class Position:
    """2D position coordinates."""
    x: float
    y: float


@dataclass
class TextStyle:
    """Styling for text overlays."""
    fontSize: int = 24
    fontFamily: str = "Arial"
    color: str = "#FFFFFF"


@dataclass
class TextLayer:
    """Text overlay layer."""
    layerId: str
    content: str
    startTime: float = 0.0
    duration: Optional[float] = None
    position: Optional[Position] = None
    style: TextStyle = field(default_factory=TextStyle)


@dataclass
class AudioLayer:
    """Audio track layer."""
    layerId: str
    sourceFile: str
    startTime: float = 0.0
    duration: Optional[float] = None
    volume: float = 1.0

    def __post_init__(self):
        if not 0 <= self.volume <= 1:
            raise ValueError("Volume must be between 0 and 1")


@dataclass
class Layers:
    """Additional layers for composition."""
    audio: List[AudioLayer] = field(default_factory=list)
    text: List[TextLayer] = field(default_factory=list)


@dataclass
class Metadata:
    """Project metadata."""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Storyboard:
    """
    Complete storyboard representation for a video project.

    This is the central state document for the Video Generation Foundry.
    All agents read from and write to this structure to coordinate work.
    """
    version: Literal["1.2"] = "1.2"
    projectId: str = ""
    outputSettings: Optional[OutputSettings] = None
    timeline: List[TimelineClip] = field(default_factory=list)
    layers: Layers = field(default_factory=Layers)
    metadata: Metadata = field(default_factory=Metadata)

    def __post_init__(self):
        if not self.projectId.startswith("proj_"):
            raise ValueError("projectId must start with 'proj_'")

    def get_clip_by_id(self, clip_id: str) -> Optional[TimelineClip]:
        """Retrieve a clip by its ID."""
        for clip in self.timeline:
            if clip.clipId == clip_id:
                return clip
        return None

    def update_clip_status(self, clip_id: str, status: ClipStatus,
                          job_id: Optional[str] = None,
                          error_message: Optional[str] = None) -> bool:
        """
        Update the status of a clip.

        Returns True if the clip was found and updated, False otherwise.
        """
        clip = self.get_clip_by_id(clip_id)
        if clip:
            clip.status = status
            if job_id:
                clip.jobId = job_id
            if error_message:
                clip.errorMessage = error_message
            return True
        return False

    def get_pending_clips(self) -> List[TimelineClip]:
        """Get all clips with pending status."""
        return [clip for clip in self.timeline if clip.status == ClipStatus.PENDING]

    def get_failed_clips(self) -> List[TimelineClip]:
        """Get all clips with failed status."""
        return [clip for clip in self.timeline if clip.status == ClipStatus.FAILED]

    def is_complete(self) -> bool:
        """Check if all clips have completed successfully."""
        return all(clip.status == ClipStatus.COMPLETED for clip in self.timeline)
