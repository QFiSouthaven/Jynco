"""
Simple Workflow Example

A simplified example showing basic Jynco workflow without full parallel initialization.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import StoryboardAgent, QuartermasterAgent


async def simple_demo():
    """Simple demo of creating a project and adding clips."""
    print("🎬 Jynco Simple Workflow Demo\n")

    # Step 1: Create project
    print("Creating project...")
    quartermaster = QuartermasterAgent(config={"base_dir": "./projects"})

    result = await quartermaster.execute({
        "operation": "create_project",
        "data": {"projectId": "proj_simple_demo"}
    })

    if result["success"]:
        print(f"✓ Project created at: {result['projectDir']}\n")
    else:
        print(f"✗ Failed: {result['error']}")
        return

    # Step 2: Initialize storyboard
    print("Initializing storyboard...")
    storyboard_agent = StoryboardAgent(config={
        "storyboard_path": "./projects/proj_simple_demo/storyboard.json"
    })

    result = await storyboard_agent.execute({
        "operation": "create",
        "data": {
            "projectId": "proj_simple_demo",
            "outputSettings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "codec": "h264"
            }
        }
    })

    if result["success"]:
        print(f"✓ Storyboard created\n")
    else:
        print(f"✗ Failed: {result['error']}")
        return

    # Step 3: Add clips
    print("Adding clips...")
    clips = [
        ("clip_001", "camera pans left slowly"),
        ("clip_002", "zoom in on subject"),
        ("clip_003", "rotate around center")
    ]

    for clip_id, prompt in clips:
        result = await storyboard_agent.execute({
            "operation": "add_clip",
            "data": {
                "clipId": clip_id,
                "motionPrompt": prompt,
                "sourceImage": f"./assets/{clip_id}.jpg",
                "duration": 3.0
            }
        })

        if result["success"]:
            print(f"  ✓ Added {clip_id}: {prompt}")
        else:
            print(f"  ✗ Failed {clip_id}: {result['error']}")

    # Step 4: Read back storyboard
    print("\nReading storyboard...")
    result = await storyboard_agent.execute({
        "operation": "read",
        "data": {}
    })

    if result["success"]:
        storyboard = result["storyboard"]
        print(f"\n📊 Storyboard Summary:")
        print(f"  Project ID: {storyboard['projectId']}")
        print(f"  Clips: {len(storyboard['timeline'])}")
        print(f"  Resolution: {storyboard['outputSettings']['resolution']['width']}x{storyboard['outputSettings']['resolution']['height']}")
        print(f"  FPS: {storyboard['outputSettings']['fps']}")

    print("\n✅ Simple demo completed!")
    print("\n💡 Check ./projects/proj_simple_demo/storyboard.json to see the result")


if __name__ == "__main__":
    asyncio.run(simple_demo())
