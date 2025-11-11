#!/usr/bin/env python3
"""
Video Foundry - Test Workflow Script

This script demonstrates the complete workflow:
1. Create a project
2. Add video segments with prompts
3. Start a render job
4. Monitor progress

Run with: python test_workflow.py
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def create_project(name: str, description: str = "") -> Dict[str, Any]:
    """Create a new video project"""
    print(f"Creating project: '{name}'...")

    response = requests.post(
        f"{API_BASE_URL}/api/projects/",
        headers=HEADERS,
        json={"name": name, "description": description}
    )
    response.raise_for_status()

    project = response.json()
    print(f"✓ Project created with ID: {project['id']}")
    return project

def add_segment(project_id: str, order: int, prompt: str) -> Dict[str, Any]:
    """Add a video segment to the project"""
    print(f"Adding segment {order + 1}: '{prompt[:50]}...'")

    response = requests.post(
        f"{API_BASE_URL}/api/projects/{project_id}/segments",
        headers=HEADERS,
        json={
            "order_index": order,
            "prompt": prompt,
            "model_params": {
                "model": "comfyui",
                "duration": 5,
                "aspect_ratio": "16:9",
                "fps": 24
            }
        }
    )
    response.raise_for_status()

    segment = response.json()
    print(f"✓ Segment added with ID: {segment['id']}")
    return segment

def start_render(project_id: str) -> Dict[str, Any]:
    """Start rendering the project"""
    print(f"Starting render job...")

    response = requests.post(f"{API_BASE_URL}/api/projects/{project_id}/render")
    response.raise_for_status()

    render_job = response.json()
    print(f"✓ Render job started with ID: {render_job['id']}")
    print(f"  Status: {render_job['status']}")
    print(f"  Total segments: {render_job['segments_total']}")
    return render_job

def get_render_status(render_job_id: str) -> Dict[str, Any]:
    """Get current render job status"""
    response = requests.get(f"{API_BASE_URL}/api/render-jobs/{render_job_id}")
    response.raise_for_status()
    return response.json()

def monitor_render(render_job_id: str, max_wait: int = 300):
    """Monitor render progress until completion or timeout"""
    print(f"\nMonitoring render progress...")
    print("(Press Ctrl+C to stop monitoring)\n")

    start_time = time.time()
    last_completed = 0

    try:
        while True:
            # Check timeout
            if time.time() - start_time > max_wait:
                print(f"\n⚠ Timeout reached ({max_wait}s). Render may still be in progress.")
                break

            # Get status
            status = get_render_status(render_job_id)

            # Show progress
            completed = status['segments_completed']
            total = status['segments_total']
            percentage = (completed / total * 100) if total > 0 else 0

            # Show update if progress changed
            if completed != last_completed:
                print(f"Progress: {completed}/{total} segments ({percentage:.1f}%) - Status: {status['status']}")
                last_completed = completed

            # Check if done
            if status['status'] in ['completed', 'failed']:
                print(f"\n✓ Render {status['status']}!")
                if status.get('s3_final_url'):
                    print(f"  Final video: {status['s3_final_url']}")
                if status.get('error_message'):
                    print(f"  Error: {status['error_message']}")
                break

            # Wait before next check
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Render continues in background.")
        print(f"Check status: curl {API_BASE_URL}/api/render-jobs/{render_job_id}")

def main():
    """Run the complete workflow demonstration"""

    print_section("Video Foundry - Test Workflow")

    print("This script will:")
    print("1. Create a new video project")
    print("2. Add multiple video segments with AI prompts")
    print("3. Start a render job")
    print("4. Monitor the rendering progress")
    print("\nMake sure the backend is running at:", API_BASE_URL)

    input("\nPress Enter to continue...")

    try:
        # Step 1: Create Project
        print_section("Step 1: Create Project")
        project = create_project(
            name="Demo AI Video",
            description="A test video showcasing different AI-generated scenes"
        )
        project_id = project['id']

        # Step 2: Add Segments
        print_section("Step 2: Add Video Segments")

        segments = [
            "A serene mountain landscape at sunrise with mist rolling over the peaks",
            "A futuristic city with flying cars and neon lights reflecting on wet streets at night",
            "A peaceful forest scene with sunlight filtering through tall trees and birds flying",
            "An underwater scene with colorful coral reefs and tropical fish swimming gracefully",
            "A time-lapse of clouds moving across a bright blue sky over rolling hills"
        ]

        for idx, prompt in enumerate(segments):
            add_segment(project_id, idx, prompt)
            time.sleep(0.5)  # Small delay to avoid overwhelming the API

        print(f"\n✓ Added {len(segments)} segments to the project")

        # Step 3: Start Render
        print_section("Step 3: Start Rendering")
        render_job = start_render(project_id)
        render_job_id = render_job['id']

        # Step 4: Monitor Progress
        print_section("Step 4: Monitor Progress")
        monitor_render(render_job_id)

        # Final Summary
        print_section("Workflow Complete!")
        print(f"Project ID: {project_id}")
        print(f"Render Job ID: {render_job_id}")
        print(f"\nView in browser:")
        print(f"  Project: http://localhost:5173/projects/{project_id}")
        print(f"  Dashboard: http://localhost:5173/dashboard")
        print(f"\nAPI Endpoints:")
        print(f"  Project: {API_BASE_URL}/api/projects/{project_id}")
        print(f"  Render Job: {API_BASE_URL}/api/render-jobs/{render_job_id}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API")
        print(f"   Make sure the backend is running at {API_BASE_URL}")
        print("   Run: start.bat (Windows) or ./start.sh (Linux/Mac)")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        print(f"   Response: {e.response.text}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
