"""
Unit Tests for Jynco Agents

Basic tests demonstrating agent functionality.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import (
    StoryboardAgent,
    QuartermasterAgent,
    MotionAgent,
    RenderAgent,
    ArchitectAgent
)
from src.schemas import ClipStatus


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.mark.asyncio
async def test_quartermaster_create_project(temp_dir):
    """Test Quartermaster can create project structure."""
    agent = QuartermasterAgent(config={"base_dir": str(temp_dir)})

    result = await agent.execute({
        "operation": "create_project",
        "data": {"projectId": "proj_test_001"}
    })

    assert result["success"] is True
    assert "projectDir" in result

    project_dir = Path(result["projectDir"])
    assert project_dir.exists()
    assert (project_dir / "clips").exists()
    assert (project_dir / "assets" / "images").exists()
    assert (project_dir / "assets" / "audio").exists()
    assert (project_dir / "exports").exists()


@pytest.mark.asyncio
async def test_storyboard_create_and_read(temp_dir):
    """Test Storyboard creation and reading."""
    storyboard_path = temp_dir / "storyboard.json"

    agent = StoryboardAgent(config={"storyboard_path": str(storyboard_path)})

    # Create storyboard
    create_result = await agent.execute({
        "operation": "create",
        "data": {
            "projectId": "proj_test_002",
            "outputSettings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "codec": "h264"
            }
        }
    })

    assert create_result["success"] is True
    assert storyboard_path.exists()

    # Read storyboard
    read_result = await agent.execute({
        "operation": "read",
        "data": {}
    })

    assert read_result["success"] is True
    assert read_result["storyboard"]["projectId"] == "proj_test_002"
    assert read_result["storyboard"]["version"] == "1.2"


@pytest.mark.asyncio
async def test_storyboard_add_clip(temp_dir):
    """Test adding clips to timeline."""
    storyboard_path = temp_dir / "storyboard.json"
    agent = StoryboardAgent(config={"storyboard_path": str(storyboard_path)})

    # Create storyboard first
    await agent.execute({
        "operation": "create",
        "data": {
            "projectId": "proj_test_003",
            "outputSettings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "codec": "h264"
            }
        }
    })

    # Add clip
    clip_result = await agent.execute({
        "operation": "add_clip",
        "data": {
            "clipId": "clip_001",
            "motionPrompt": "test motion",
            "sourceImage": "/test/image.jpg",
            "duration": 3.0
        }
    })

    assert clip_result["success"] is True
    assert clip_result["clipId"] == "clip_001"

    # Verify clip was added
    read_result = await agent.execute({
        "operation": "read",
        "data": {}
    })

    timeline = read_result["storyboard"]["timeline"]
    assert len(timeline) == 1
    assert timeline[0]["clipId"] == "clip_001"
    assert timeline[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_storyboard_update_clip_status(temp_dir):
    """Test updating clip status."""
    storyboard_path = temp_dir / "storyboard.json"
    agent = StoryboardAgent(config={"storyboard_path": str(storyboard_path)})

    # Setup
    await agent.execute({
        "operation": "create",
        "data": {"projectId": "proj_test_004"}
    })

    await agent.execute({
        "operation": "add_clip",
        "data": {
            "clipId": "clip_001",
            "motionPrompt": "test",
            "duration": 3.0
        }
    })

    # Update status
    update_result = await agent.execute({
        "operation": "update_clip",
        "data": {
            "clipId": "clip_001",
            "status": "generating",
            "jobId": "job_motion_123"
        }
    })

    assert update_result["success"] is True

    # Verify update
    read_result = await agent.execute({
        "operation": "read",
        "data": {}
    })

    clip = read_result["storyboard"]["timeline"][0]
    assert clip["status"] == "generating"
    assert clip["jobId"] == "job_motion_123"


@pytest.mark.asyncio
async def test_motion_agent_cache_key_generation(temp_dir):
    """Test Motion Agent generates consistent cache keys."""
    agent = MotionAgent(config={"ai_model": "mock"})

    # Create a test image file
    test_image = temp_dir / "test.jpg"
    test_image.write_text("test image content")

    # Generate cache key
    key1 = agent._compute_cache_key(str(test_image), "test prompt")
    key2 = agent._compute_cache_key(str(test_image), "test prompt")

    # Same inputs should generate same key
    assert key1 == key2
    assert len(key1) == 64  # SHA-256 produces 64 hex chars

    # Different prompt should generate different key
    key3 = agent._compute_cache_key(str(test_image), "different prompt")
    assert key1 != key3


@pytest.mark.asyncio
async def test_agent_parallel_initialization():
    """Test that multiple agents can be initialized in parallel."""
    async def init_agent(agent_class, agent_id, config=None):
        agent = agent_class(agent_id=agent_id, config=config or {})
        return agent

    # Initialize multiple agents in parallel
    agents = await asyncio.gather(
        init_agent(StoryboardAgent, "storyboard_1"),
        init_agent(MotionAgent, "motion_1"),
        init_agent(RenderAgent, "render_1"),
        init_agent(QuartermasterAgent, "quartermaster_1"),
        init_agent(ArchitectAgent, "architect_1")
    )

    assert len(agents) == 5
    assert all(agent is not None for agent in agents)
    assert agents[0].agent_id == "storyboard_1"
    assert agents[1].agent_id == "motion_1"


@pytest.mark.asyncio
async def test_agent_error_handling(temp_dir):
    """Test agent error handling."""
    agent = StoryboardAgent(config={"storyboard_path": str(temp_dir / "test.json")})

    # Try to read non-existent storyboard
    result = await agent.execute({
        "operation": "read",
        "data": {}
    })

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_quartermaster_store_and_retrieve_clip(temp_dir):
    """Test storing and retrieving clips."""
    agent = QuartermasterAgent(config={"base_dir": str(temp_dir)})

    # Create project
    await agent.execute({
        "operation": "create_project",
        "data": {"projectId": "proj_test_005"}
    })

    # Create a test clip file
    temp_clip = temp_dir / "temp_clip.mp4"
    temp_clip.write_text("fake video data")

    # Store clip
    store_result = await agent.execute({
        "operation": "store_clip",
        "data": {
            "projectId": "proj_test_005",
            "clipId": "clip_001",
            "sourceFile": str(temp_clip)
        }
    })

    assert store_result["success"] is True
    assert "storedPath" in store_result

    # Retrieve clip
    retrieve_result = await agent.execute({
        "operation": "retrieve_clip",
        "data": {
            "projectId": "proj_test_005",
            "clipId": "clip_001"
        }
    })

    assert retrieve_result["success"] is True
    assert Path(retrieve_result["filePath"]).exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
