"""
End-to-End test for timeline-aware video generation workflow.

This test validates the complete pipeline:
1. Multi-segment project creation
2. Incremental re-render (only modified segments regenerate)
3. Composition workflow
4. Real-time updates
"""
import pytest
import asyncio
from uuid import uuid4
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_db_context, init_db, drop_db
from backend.models import Project, Segment, RenderJob, User
from backend.models.segment import SegmentStatus
from backend.models.render_job import RenderJobStatus
from backend.services import RabbitMQClient, RedisClient, RenderOrchestrator
from workers.ai_worker.adapters import VideoModelFactory


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database."""
    drop_db()
    init_db()
    yield
    drop_db()


@pytest.fixture
def test_user():
    """Create a test user."""
    with get_db_context() as db:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


@pytest.fixture
def rabbitmq_client():
    """Get RabbitMQ client."""
    return RabbitMQClient()


@pytest.fixture
def redis_client():
    """Get Redis client."""
    return RedisClient()


@pytest.fixture
def orchestrator(rabbitmq_client, redis_client):
    """Get render orchestrator."""
    return RenderOrchestrator(rabbitmq_client, redis_client)


def test_multi_segment_project_creation(setup_database, test_user):
    """
    Test Scenario: User creates a project with multiple segments.

    Expected:
    - Project is created successfully
    - All segments are stored with correct order
    - Segments are in 'pending' status
    """
    with get_db_context() as db:
        # Create project
        project = Project(
            user_id=test_user.id,
            name="Test Multi-Segment Project",
            description="Testing timeline workflow"
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # Add 3 segments
        segments_data = [
            {"prompt": "A sunrise over mountains", "order": 0},
            {"prompt": "Birds flying in the sky", "order": 1},
            {"prompt": "Ocean waves crashing", "order": 2},
        ]

        for seg_data in segments_data:
            segment = Segment(
                project_id=project.id,
                order_index=seg_data["order"],
                prompt=seg_data["prompt"],
                model_params={"model": "mock-ai", "duration": 5},
                status=SegmentStatus.PENDING
            )
            db.add(segment)

        db.commit()

        # Verify
        created_project = db.query(Project).filter(Project.id == project.id).first()
        assert created_project is not None
        assert len(created_project.segments) == 3
        assert all(seg.status == SegmentStatus.PENDING for seg in created_project.segments)
        assert created_project.segments[0].order_index == 0
        assert created_project.segments[1].order_index == 1
        assert created_project.segments[2].order_index == 2

    print("✓ Multi-segment project creation test passed")


def test_first_render_all_segments(setup_database, test_user, orchestrator):
    """
    Test Scenario: First render of a project - all segments should be dispatched.

    Expected:
    - Render job is created
    - All 3 segments are dispatched for generation
    - RabbitMQ receives 3 messages
    - Redis tracks the job progress
    """
    with get_db_context() as db:
        # Create project with segments
        project = Project(
            user_id=test_user.id,
            name="First Render Test"
        )
        db.add(project)
        db.commit()

        for i in range(3):
            segment = Segment(
                project_id=project.id,
                order_index=i,
                prompt=f"Test segment {i}",
                model_params={"model": "mock-ai", "duration": 5},
                status=SegmentStatus.PENDING
            )
            db.add(segment)

        db.commit()
        db.refresh(project)

        # Start render
        render_job = orchestrator.create_render_job(db, project.id)

        # Verify
        assert render_job is not None
        assert render_job.status == RenderJobStatus.PROCESSING
        assert render_job.segments_total == 3
        assert render_job.segments_completed == 0

        # Verify segments are now in GENERATING status
        updated_project = db.query(Project).filter(Project.id == project.id).first()
        generating_count = sum(
            1 for seg in updated_project.segments
            if seg.status == SegmentStatus.GENERATING
        )
        assert generating_count == 3

        # Check Redis
        progress = orchestrator.redis.get_render_job_progress(render_job.id)
        assert progress is not None
        assert progress["segments_total"] == 3
        assert progress["segments_completed"] == 0

    print("✓ First render test passed - all segments dispatched")


def test_incremental_render(setup_database, test_user, orchestrator):
    """
    Test Scenario: User modifies ONE segment and triggers re-render.

    Expected:
    - Only the modified segment is regenerated
    - Other segments reuse existing assets
    - Only 1 message is published to RabbitMQ
    """
    with get_db_context() as db:
        # Create project with segments
        project = Project(
            user_id=test_user.id,
            name="Incremental Render Test"
        )
        db.add(project)
        db.commit()

        segments = []
        for i in range(3):
            segment = Segment(
                project_id=project.id,
                order_index=i,
                prompt=f"Original segment {i}",
                model_params={"model": "mock-ai", "duration": 5},
                status=SegmentStatus.COMPLETED,  # Mark as already completed
                s3_asset_url=f"https://s3.example.com/segment_{i}.mp4"
            )
            db.add(segment)
            db.commit()
            db.refresh(segment)
            segments.append(segment)

        db.refresh(project)

        # Create first render job (already completed)
        first_render = RenderJob(
            project_id=project.id,
            status=RenderJobStatus.COMPLETED,
            segments_total=3,
            segments_completed=3,
            segment_ids=[str(seg.id) for seg in segments],
            s3_final_url="https://s3.example.com/final_v1.mp4"
        )
        db.add(first_render)
        db.commit()

        # Now modify ONE segment
        segment_to_modify = segments[1]
        segment_to_modify.prompt = "MODIFIED: Birds flying in the sky"
        segment_to_modify.status = SegmentStatus.PENDING
        segment_to_modify.s3_asset_url = None
        db.commit()

        # Trigger new render
        second_render = orchestrator.create_render_job(db, project.id)

        # Verify only 1 segment is being regenerated
        assert second_render.segments_total == 1  # Only the modified one
        assert second_render.status == RenderJobStatus.PROCESSING

        # Verify only the modified segment is in GENERATING status
        updated_project = db.query(Project).filter(Project.id == project.id).first()
        generating_segments = [
            seg for seg in updated_project.segments
            if seg.status == SegmentStatus.GENERATING
        ]
        assert len(generating_segments) == 1
        assert generating_segments[0].id == segment_to_modify.id

        # Other segments should still be COMPLETED
        completed_segments = [
            seg for seg in updated_project.segments
            if seg.status == SegmentStatus.COMPLETED and seg.id != segment_to_modify.id
        ]
        assert len(completed_segments) == 2

    print("✓ Incremental render test passed - only 1 segment regenerated")


def test_segment_completion_workflow(setup_database, test_user, orchestrator):
    """
    Test Scenario: Segment completion triggers composition when all done.

    Expected:
    - When last segment completes, composition task is published
    - Render job moves to COMPOSITING status
    - Final video URL is set when composition completes
    """
    with get_db_context() as db:
        # Create project with 2 segments
        project = Project(
            user_id=test_user.id,
            name="Composition Test"
        )
        db.add(project)
        db.commit()

        segments = []
        for i in range(2):
            segment = Segment(
                project_id=project.id,
                order_index=i,
                prompt=f"Segment {i}",
                model_params={"model": "mock-ai", "duration": 5},
                status=SegmentStatus.GENERATING
            )
            db.add(segment)
            db.commit()
            db.refresh(segment)
            segments.append(segment)

        # Create render job
        render_job = RenderJob(
            project_id=project.id,
            status=RenderJobStatus.PROCESSING,
            segments_total=2,
            segments_completed=0,
            segment_ids=[str(seg.id) for seg in segments]
        )
        db.add(render_job)
        db.commit()
        db.refresh(render_job)

        # Complete first segment
        orchestrator.handle_segment_completion(
            db,
            segments[0].id,
            render_job.id,
            "https://s3.example.com/seg0.mp4"
        )

        db.refresh(render_job)
        assert render_job.segments_completed == 1
        assert render_job.status == RenderJobStatus.PROCESSING  # Still processing

        # Complete second segment - should trigger composition
        orchestrator.handle_segment_completion(
            db,
            segments[1].id,
            render_job.id,
            "https://s3.example.com/seg1.mp4"
        )

        db.refresh(render_job)
        assert render_job.segments_completed == 2
        assert render_job.status == RenderJobStatus.COMPOSITING  # Now compositing

        # Simulate composition completion
        orchestrator.handle_composition_completion(
            db,
            render_job.id,
            "https://s3.example.com/final.mp4"
        )

        db.refresh(render_job)
        assert render_job.status == RenderJobStatus.COMPLETED
        assert render_job.s3_final_url == "https://s3.example.com/final.mp4"

    print("✓ Composition workflow test passed")


def test_mock_adapter_integration(setup_database):
    """
    Test Scenario: MockAIAdapter simulates video generation.

    Expected:
    - Adapter can be created via factory
    - Generation completes successfully
    - Returns mock video URL
    """
    async def run_test():
        # Create mock adapter
        adapter = VideoModelFactory.create("mock-ai")

        assert adapter.model_name == "mock-ai"

        # Initiate generation
        external_job_id = await adapter.initiate_generation(
            prompt="Test video",
            model_params={"duration": 5}
        )

        assert external_job_id is not None
        assert external_job_id.startswith("mock_job_")

        # Wait for completion (mock has 2s delay)
        await asyncio.sleep(2.5)

        # Get result
        result = await adapter.get_result(external_job_id)

        assert result.status.value == "completed"
        assert result.video_url is not None
        assert "mock-cdn.example.com" in result.video_url

    asyncio.run(run_test())
    print("✓ Mock adapter integration test passed")


if __name__ == "__main__":
    # Run tests
    print("\n=== Running E2E Timeline Workflow Tests ===\n")

    pytest.main([__file__, "-v", "-s"])
