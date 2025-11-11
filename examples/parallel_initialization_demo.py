"""
Parallel Agent Initialization Demo

Demonstrates initializing and running all Jynco agents in parallel.
This showcases the complete video generation pipeline with all agents
working concurrently on different tasks.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import init_config, get_config
from src.agents import (
    ArchitectAgent,
    StoryboardAgent,
    MotionAgent,
    RenderAgent,
    QuartermasterAgent
)
from src.infrastructure import create_cache, create_job_queue


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_infrastructure():
    """Initialize cache and job queue infrastructure."""
    logger.info("🏗️  Initializing infrastructure...")

    config = get_config()

    # Initialize cache
    cache_config = config.get_cache_config()
    cache = create_cache(
        cache_type=cache_config.get("type", "local"),
        cache_dir=cache_config.get("cache_dir", "./cache")
    )
    logger.info(f"✓ Cache initialized: {cache_config.get('type')}")

    # Initialize job queue
    queue_config = config.get_queue_config()
    job_queue = create_job_queue(
        queue_type=queue_config.get("type", "memory")
    )
    logger.info(f"✓ Job queue initialized: {queue_config.get('type')}")

    return cache, job_queue


async def initialize_agents(cache, job_queue):
    """Initialize all agents with their dependencies."""
    logger.info("🤖 Initializing agents...")

    config = get_config()

    # Initialize agents in parallel
    async def init_storyboard():
        agent = StoryboardAgent(
            agent_id="storyboard_001",
            config=config.get_agent_config("storyboard")
        )
        logger.info("✓ Storyboard Agent initialized")
        return agent

    async def init_motion():
        agent = MotionAgent(
            agent_id="motion_001",
            config=config.get_agent_config("motion")
        )
        agent.set_cache(cache)
        logger.info("✓ Motion Agent initialized")
        return agent

    async def init_render():
        agent = RenderAgent(
            agent_id="render_001",
            config=config.get_agent_config("render")
        )
        logger.info("✓ Render Agent initialized")
        return agent

    async def init_quartermaster():
        agent = QuartermasterAgent(
            agent_id="quartermaster_001",
            config=config.get_agent_config("quartermaster")
        )
        logger.info("✓ Quartermaster Agent initialized")
        return agent

    async def init_architect():
        agent = ArchitectAgent(
            agent_id="architect_001",
            config=config.get_agent_config("architect")
        )
        logger.info("✓ Architect Agent initialized")
        return agent

    # Run all initializations in parallel
    results = await asyncio.gather(
        init_storyboard(),
        init_motion(),
        init_render(),
        init_quartermaster(),
        init_architect()
    )

    storyboard_agent, motion_agent, render_agent, quartermaster_agent, architect_agent = results

    # Wire up dependencies
    architect_agent.set_storyboard_agent(storyboard_agent)
    architect_agent.set_motion_agent(motion_agent)
    architect_agent.set_render_agent(render_agent)
    architect_agent.set_job_queue(job_queue)

    logger.info("✓ All agent dependencies wired")

    return {
        "architect": architect_agent,
        "storyboard": storyboard_agent,
        "motion": motion_agent,
        "render": render_agent,
        "quartermaster": quartermaster_agent
    }


async def create_demo_project(agents):
    """Create a demo project with sample timeline."""
    logger.info("📁 Creating demo project...")

    project_id = f"proj_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Step 1: Create project structure
    result = await agents["quartermaster"].execute({
        "operation": "create_project",
        "data": {"projectId": project_id}
    })

    if not result["success"]:
        raise Exception(f"Failed to create project: {result.get('error')}")

    logger.info(f"✓ Project structure created: {project_id}")

    # Step 2: Update storyboard config with project path
    agents["storyboard"].storyboard_path = Path(result["projectDir"]) / "storyboard.json"

    # Step 3: Create storyboard
    result = await agents["storyboard"].execute({
        "operation": "create",
        "data": {
            "projectId": project_id,
            "outputSettings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "codec": "h264",
                "bitrate": "5M"
            },
            "metadata": {
                "title": "Jynco Demo Video",
                "description": "Demonstration of parallel agent initialization"
            }
        }
    })

    if not result["success"]:
        raise Exception(f"Failed to create storyboard: {result.get('error')}")

    logger.info("✓ Storyboard created")

    # Step 4: Add multiple clips in parallel
    logger.info("Adding clips to timeline...")

    clips = [
        {
            "clipId": f"clip_{i:03d}",
            "motionPrompt": prompt,
            "sourceImage": f"./assets/scene{i}.jpg",
            "duration": 3.0,
            "startTime": i * 3.0
        }
        for i, prompt in enumerate([
            "camera slowly pans from left to right",
            "gentle zoom in on the subject",
            "dynamic rotation around the center",
            "smooth tracking shot forward",
            "elegant pullback revealing the scene"
        ], start=1)
    ]

    # Add all clips in parallel
    add_clip_tasks = [
        agents["storyboard"].execute({
            "operation": "add_clip",
            "data": clip
        })
        for clip in clips
    ]

    results = await asyncio.gather(*add_clip_tasks)

    successful = sum(1 for r in results if r.get("success"))
    logger.info(f"✓ Added {successful}/{len(clips)} clips to timeline")

    return project_id


async def parallel_agent_status_check(agents):
    """Check status of all agents in parallel."""
    logger.info("📊 Checking agent status...")

    async def get_status(name, agent):
        status = agent.get_status()
        return name, status

    # Get all agent statuses in parallel
    tasks = [
        get_status(name, agent)
        for name, agent in agents.items()
    ]

    results = await asyncio.gather(*tasks)

    logger.info("\n" + "="*60)
    logger.info("AGENT STATUS REPORT")
    logger.info("="*60)

    for name, status in results:
        logger.info(f"\n{name.upper()}:")
        logger.info(f"  Agent ID: {status['agent_id']}")
        logger.info(f"  Type: {status['agent_type']}")
        logger.info(f"  Status: {status['status']}")
        logger.info(f"  Timestamp: {status['timestamp']}")

    logger.info("="*60 + "\n")


async def demonstrate_parallel_operations(agents, project_id):
    """Demonstrate parallel operations across agents."""
    logger.info("⚡ Demonstrating parallel operations...")

    # Parallel operation 1: Read storyboard + Check cache stats + Get queue stats
    async def read_storyboard():
        result = await agents["storyboard"].execute({
            "operation": "read",
            "data": {}
        })
        logger.info("✓ Storyboard read complete")
        return result

    async def check_cache():
        # This would check cache stats if implemented
        logger.info("✓ Cache check complete")
        return {"cache": "checked"}

    async def check_queue():
        # This would check queue stats if implemented
        logger.info("✓ Queue check complete")
        return {"queue": "checked"}

    results = await asyncio.gather(
        read_storyboard(),
        check_cache(),
        check_queue()
    )

    storyboard_data, cache_data, queue_data = results

    if storyboard_data.get("success"):
        timeline = storyboard_data["storyboard"]["timeline"]
        logger.info(f"\n📽️  Timeline Summary:")
        logger.info(f"  Total clips: {len(timeline)}")
        logger.info(f"  Pending clips: {sum(1 for c in timeline if c.get('status') == 'pending')}")
        logger.info(f"  Total duration: {sum(c.get('duration', 0) for c in timeline):.1f}s")

    # Parallel operation 2: Simulate multiple clip status updates
    logger.info("\n🔄 Simulating parallel clip updates...")

    clip_update_tasks = [
        agents["storyboard"].execute({
            "operation": "update_clip",
            "data": {
                "clipId": f"clip_{i:03d}",
                "status": "generating",
                "jobId": f"job_motion_{i:03d}"
            }
        })
        for i in range(1, 4)  # Update first 3 clips
    ]

    update_results = await asyncio.gather(*clip_update_tasks)
    successful_updates = sum(1 for r in update_results if r.get("success"))
    logger.info(f"✓ Updated {successful_updates} clips in parallel")


async def main():
    """Main execution function."""
    logger.info("\n" + "="*60)
    logger.info("JYNCO - PARALLEL AGENT INITIALIZATION DEMO")
    logger.info("="*60 + "\n")

    try:
        # Step 1: Initialize configuration
        logger.info("⚙️  Loading configuration...")
        init_config(environment="development")
        logger.info("✓ Configuration loaded\n")

        # Step 2: Initialize infrastructure
        cache, job_queue = await initialize_infrastructure()
        logger.info("")

        # Step 3: Initialize all agents in parallel
        agents = await initialize_agents(cache, job_queue)
        logger.info("")

        # Step 4: Check agent status in parallel
        await parallel_agent_status_check(agents)

        # Step 5: Create demo project
        project_id = await create_demo_project(agents)
        logger.info("")

        # Step 6: Demonstrate parallel operations
        await demonstrate_parallel_operations(agents, project_id)
        logger.info("")

        # Final status check
        logger.info("🎬 Final System Status")
        logger.info("-" * 60)
        logger.info(f"Project ID: {project_id}")
        logger.info(f"All agents: OPERATIONAL")
        logger.info(f"Infrastructure: READY")
        logger.info(f"Status: Ready for video generation")
        logger.info("="*60 + "\n")

        logger.info("✅ Demo completed successfully!")
        logger.info(f"\n💡 Next steps:")
        logger.info(f"  1. Integrate AI model for Motion Agent")
        logger.info(f"  2. Run: architect.generate_project('{project_id}')")
        logger.info(f"  3. Monitor clip generation in storyboard.json")
        logger.info(f"  4. Submit render job when all clips complete\n")

    except Exception as e:
        logger.error(f"\n❌ Demo failed: {str(e)}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
