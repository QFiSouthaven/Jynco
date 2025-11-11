# Getting Started with Jynco

## Overview

This guide will help you set up and run your first video generation project using Jynco, the Video Generation Foundry.

## Prerequisites

- Python 3.9+
- FFmpeg (for video rendering)
- Optional: Redis (for production caching)
- Optional: RabbitMQ (for production job queue)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Jynco
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Quick Start

### Example 1: Create a Project

```python
import asyncio
from src.agents import StoryboardAgent, QuartermasterAgent
from src.schemas import Storyboard, OutputSettings, Resolution, VideoCodec

async def create_project():
    # Initialize agents
    quartermaster = QuartermasterAgent(config={
        "base_dir": "./projects"
    })

    storyboard_agent = StoryboardAgent(config={
        "storyboard_path": "./projects/proj_demo/storyboard.json"
    })

    # Create project directory
    await quartermaster.execute({
        "operation": "create_project",
        "data": {"projectId": "proj_demo"}
    })

    # Create storyboard
    await storyboard_agent.execute({
        "operation": "create",
        "data": {
            "projectId": "proj_demo",
            "outputSettings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "codec": "h264"
            }
        }
    })

    print("✓ Project created: proj_demo")

asyncio.run(create_project())
```

### Example 2: Add Clips to Timeline

```python
async def add_clips():
    storyboard_agent = StoryboardAgent(config={
        "storyboard_path": "./projects/proj_demo/storyboard.json"
    })

    # Add first clip
    await storyboard_agent.execute({
        "operation": "add_clip",
        "data": {
            "clipId": "clip_001",
            "motionPrompt": "camera slowly pans from left to right",
            "sourceImage": "./projects/proj_demo/assets/images/scene1.jpg",
            "duration": 3.0,
            "startTime": 0.0
        }
    })

    # Add second clip
    await storyboard_agent.execute({
        "operation": "add_clip",
        "data": {
            "clipId": "clip_002",
            "motionPrompt": "gentle zoom in on subject",
            "sourceImage": "./projects/proj_demo/assets/images/scene2.jpg",
            "duration": 3.0,
            "startTime": 3.0
        }
    })

    print("✓ Added 2 clips to timeline")

asyncio.run(add_clips())
```

### Example 3: Generate Project (Orchestrated)

```python
async def generate_project():
    from src.agents import ArchitectAgent, StoryboardAgent, MotionAgent
    from src.infrastructure import create_cache

    # Set up infrastructure
    cache = create_cache(cache_type="local", cache_dir="./cache")

    # Initialize agents
    storyboard_agent = StoryboardAgent(config={
        "storyboard_path": "./projects/proj_demo/storyboard.json"
    })

    motion_agent = MotionAgent(config={
        "ai_model": "runway_gen3"
    })
    motion_agent.set_cache(cache)

    architect = ArchitectAgent(config={
        "max_retries": 3,
        "retry_delay_base": 2.0
    })
    architect.set_storyboard_agent(storyboard_agent)
    architect.set_motion_agent(motion_agent)

    # Generate all clips
    result = await architect.execute({
        "operation": "generate_project",
        "projectId": "proj_demo"
    })

    if result["success"]:
        print(f"✓ Generated {result['successful']}/{result['totalClips']} clips")
    else:
        print(f"⚠ Generation completed with {result['failed']} failures")

# Note: This requires AI model integration
# asyncio.run(generate_project())
```

### Example 4: Render Final Video

```python
async def render_video():
    from src.agents import ArchitectAgent
    from src.infrastructure import create_job_queue

    # Set up job queue
    job_queue = create_job_queue(queue_type="memory")

    # Initialize architect
    architect = ArchitectAgent()
    architect.set_job_queue(job_queue)

    # Submit render job
    result = await architect.execute({
        "operation": "render_final",
        "projectId": "proj_demo"
    })

    print(f"✓ Render job submitted: {result['jobId']}")

asyncio.run(render_video())
```

## Configuration

### Development Configuration

Create `config/development.json`:

```json
{
  "cache": {
    "type": "local",
    "cache_dir": "./cache"
  },
  "job_queue": {
    "type": "memory"
  },
  "agents": {
    "architect": {
      "max_retries": 3,
      "retry_delay_base": 2.0
    },
    "motion": {
      "ai_model": "mock"
    },
    "render": {
      "ffmpeg_path": "ffmpeg",
      "output_dir": "./output"
    },
    "quartermaster": {
      "base_dir": "./projects",
      "cache_dir": "./cache",
      "temp_dir": "./temp"
    }
  }
}
```

### Production Configuration

Create `config/production.json`:

```json
{
  "cache": {
    "type": "redis",
    "redis_url": "redis://cache.example.com:6379"
  },
  "job_queue": {
    "type": "rabbitmq",
    "rabbitmq_url": "amqp://queue.example.com"
  },
  "agents": {
    "motion": {
      "ai_model": "runway_gen3",
      "api_key": "${RUNWAY_API_KEY}"
    }
  }
}
```

## Architecture Overview

```
User Request
    ↓
Architect Agent (Coordinator)
    ↓
├── Storyboard Agent → storyboard.json
├── Motion Agent → Cache → AI Model
├── Render Agent ← Job Queue
└── Quartermaster Agent → File System
```

## Key Concepts

### 1. Storyboard

The central state document (`storyboard.json`) contains:
- Project configuration
- Timeline of clips
- Clip status and job IDs
- Output settings
- Audio/text layers

### 2. Agent System

- **Architect**: Orchestrates the entire pipeline
- **Storyboard**: Manages state
- **Motion**: Generates video from images
- **Render**: Composes final video
- **Quartermaster**: Handles files

### 3. Caching

Cache keys are computed as:
```
SHA-256(image_content + motion_prompt + model_version)
```

Benefits:
- Instant retrieval on cache hit
- Cost savings (avoid re-generation)
- Platform-wide sharing

### 4. Job Queue

Priority levels:
- **HIGH**: Preview renders (< 5s)
- **NORMAL**: Final exports
- **LOW**: Batch processing

## Testing

```bash
# Run tests (once implemented)
pytest tests/

# Run specific test
pytest tests/test_storyboard_agent.py

# Run with coverage
pytest --cov=src tests/
```

## Development Workflow

1. **Create Project Structure**
   ```python
   quartermaster.create_project()
   ```

2. **Upload Assets**
   ```python
   quartermaster.upload_asset(image)
   ```

3. **Build Timeline**
   ```python
   storyboard_agent.add_clip()
   ```

4. **Generate Clips**
   ```python
   architect.generate_project()
   ```

5. **Render Final Video**
   ```python
   architect.render_final()
   ```

6. **Monitor Progress**
   ```python
   storyboard_agent.read()  # Check clip statuses
   job_queue.get_status(job_id)
   ```

## Troubleshooting

### Cache Not Working

```python
# Clear cache
cache = create_cache("local")
await cache.clear_all()

# Check cache stats
stats = await cache.get_stats()
print(stats)
```

### Job Queue Stuck

```python
# Check queue stats
queue = create_job_queue("memory")
stats = await queue.get_stats()
print(f"Pending: {stats['pending']}, Running: {stats['running']}")
```

### FFmpeg Errors

```bash
# Test FFmpeg installation
ffmpeg -version

# Check codec support
ffmpeg -codecs | grep h264
```

## Next Steps

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design
2. Explore [API_REFERENCE.md](./API_REFERENCE.md) for complete API documentation
3. Check [EXAMPLES.md](./EXAMPLES.md) for more use cases
4. Review `src/schemas/storyboard_schema_v1_2.json` for schema details

## Support

- GitHub Issues: <repository-url>/issues
- Documentation: `docs/`
- Examples: `examples/`

## License

[License information]
