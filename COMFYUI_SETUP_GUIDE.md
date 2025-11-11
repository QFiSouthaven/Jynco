# ComfyUI Integration Setup Guide

This guide will help you set up Video Foundry with ComfyUI for local AI video generation.

## What We've Done

We've integrated ComfyUI into the Video Foundry system:

1. **Created ComfyUI Adapter** (`workers/ai_worker/adapters/comfyui.py`)
   - Implements the VideoModelInterface for ComfyUI
   - Communicates with ComfyUI's REST API
   - Handles video generation workflows

2. **Updated Factory** (`workers/ai_worker/adapters/factory.py`)
   - Registered ComfyUI adapter with aliases "comfyui" and "comfy"
   - Added environment variable mapping for COMFYUI_URL

3. **Added ComfyUI Service** (docker-compose.yml)
   - Uses `yanwk/comfyui-boot:latest` Docker image
   - Exposes port 8188 for ComfyUI interface
   - Includes GPU support via NVIDIA drivers
   - Persistent volumes for models, input, and output

4. **Updated Configuration**
   - Added COMFYUI_URL to .env.example and .env
   - Updated AI worker environment to include ComfyUI URL
   - Added ComfyUI as a dependency for AI workers

## Prerequisites

Before starting, ensure you have:

- **Docker** and **Docker Compose** installed
- **NVIDIA GPU** with drivers installed (for GPU acceleration)
- **nvidia-docker2** installed (for GPU support in containers)
- At least **20GB** of free disk space (for models)

### Installing NVIDIA Docker Support

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Starting the Services

### 1. Start All Services

```bash
cd /home/user/Jynco
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, management UI on 15672)
- Backend API (port 8000)
- Frontend (port 3000)
- AI Workers (2 replicas)
- Composition Worker
- **ComfyUI (port 8188)** ✨

### 2. Check Service Status

```bash
docker-compose ps
```

All services should show as "Up" or "healthy".

### 3. View Logs

```bash
# View all logs
docker-compose logs -f

# View ComfyUI logs specifically
docker-compose logs -f comfyui

# View AI worker logs
docker-compose logs -f ai_worker
```

### 4. Access the Services

Once all services are running:

- **ComfyUI Interface**: http://127.0.0.1:8188/
- **Video Foundry Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Using ComfyUI with Video Foundry

### Option 1: Via API (Programmatic)

When creating a video segment via the Video Foundry API, specify ComfyUI as the model:

```python
import requests

# Create a project segment with ComfyUI
response = requests.post(
    "http://localhost:8000/api/projects/{project_id}/segments",
    json={
        "prompt": "A serene sunset over mountains with flowing clouds",
        "model_name": "comfyui",
        "model_params": {
            "workflow": {
                # Your ComfyUI workflow JSON here
                # You can export this from the ComfyUI interface
            },
            "duration": 5,
            "width": 1024,
            "height": 576
        },
        "duration": 5,
        "order": 0
    }
)
```

### Option 2: Via Frontend

1. Go to http://localhost:3000
2. Create a new project
3. Add a segment
4. Select **"ComfyUI"** as the model
5. Provide your prompt and parameters
6. Click "Generate"

### Option 3: Direct ComfyUI Usage

You can also use ComfyUI directly:

1. Open http://127.0.0.1:8188/
2. Design your workflow in the node-based interface
3. Export the workflow JSON
4. Use that workflow in Video Foundry API calls

## ComfyUI Workflow Configuration

The ComfyUI adapter expects a workflow JSON structure. Here's a minimal example:

```json
{
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "YOUR_PROMPT_HERE",
      "clip": ["4", 1]
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    }
  }
  // ... more nodes
}
```

### Workflow Tips

1. **Export from ComfyUI**: Design your workflow in the ComfyUI interface, then use "Save (API Format)" to get the JSON
2. **Prompt Node**: The adapter will inject your text prompt into node "6" by default (configurable via `prompt_node_id`)
3. **Parameters**: You can specify `sampler_node_id`, `width`, `height` in `model_params` to override values

## Troubleshooting

### ComfyUI Not Starting

```bash
# Check ComfyUI logs
docker-compose logs comfyui

# Common issues:
# 1. GPU not available - ComfyUI will fall back to CPU (slower)
# 2. Port 8188 already in use - stop other services or change port
# 3. Insufficient memory - ensure at least 8GB RAM available
```

### No GPU Support

If you don't have an NVIDIA GPU, you can modify the docker-compose.yml to remove GPU requirements:

```yaml
# Comment out or remove this section from the comfyui service:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```

ComfyUI will run on CPU, but generation will be much slower.

### Connection Refused

If you get "Connection refused" when accessing http://127.0.0.1:8188/:

1. Wait 1-2 minutes for ComfyUI to fully start (it downloads models on first run)
2. Check if the container is running: `docker ps | grep comfyui`
3. Check logs: `docker-compose logs comfyui`

### Models Not Downloading

On first start, ComfyUI downloads required models. This can take 10-30 minutes depending on your internet speed. Monitor progress:

```bash
docker-compose logs -f comfyui
```

## Advanced Configuration

### Custom Models

To add custom models to ComfyUI:

```bash
# Models are stored in a Docker volume
# You can also mount a local directory:
# In docker-compose.yml, under comfyui volumes, add:
# - /path/to/your/models:/home/runner/ComfyUI/models

# Or copy models into the running container:
docker cp your-model.safetensors vf_comfyui:/home/runner/ComfyUI/models/checkpoints/
```

### Scaling Workers

To add more AI workers for parallel processing:

```bash
# Edit docker-compose.yml, change replicas:
# deploy:
#   replicas: 4  # Increase from 2 to 4

docker-compose up -d --scale ai_worker=4
```

### Memory Limits

If you have limited RAM, you can set memory limits:

```yaml
# In docker-compose.yml, under comfyui:
deploy:
  resources:
    limits:
      memory: 8G
```

## Testing the Integration

### 1. Health Check

```bash
# Check if ComfyUI is responding
curl http://localhost:8188/

# Should return the ComfyUI web interface HTML
```

### 2. Test Video Generation

```bash
# Use the mock adapter first to test the pipeline
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test ComfyUI Project",
    "description": "Testing ComfyUI integration"
  }'

# Note the project_id from response, then add a segment:
curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "model_name": "comfyui",
    "duration": 5,
    "order": 0
  }'
```

## Next Steps

1. **Design Workflows**: Open ComfyUI at http://127.0.0.1:8188/ and create your video generation workflows
2. **Export Workflows**: Save workflows in API format for use with Video Foundry
3. **Create Videos**: Use the Video Foundry frontend to create multi-segment videos with ComfyUI
4. **Monitor**: Watch the RabbitMQ management UI to see tasks being processed

## Useful Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Restart ComfyUI only
docker-compose restart comfyui

# View resource usage
docker stats

# Execute command in ComfyUI container
docker exec -it vf_comfyui bash
```

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f comfyui`
2. Verify all services are healthy: `docker-compose ps`
3. Ensure ports are not in use: `netstat -tuln | grep 8188`
4. Check Docker disk space: `docker system df`

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│  (Port 3000)    │
└────────┬────────┘
         │
         v
┌─────────────────┐         ┌─────────────────┐
│   Backend API   │────────>│   RabbitMQ      │
│  (Port 8000)    │         │  (Port 5672)    │
└─────────────────┘         └────────┬────────┘
                                     │
                                     v
                            ┌─────────────────┐
                            │   AI Workers    │
                            │   (x2)          │
                            └────────┬────────┘
                                     │
                        ┌────────────┼────────────┐
                        v            v            v
                  ┌─────────┐  ┌─────────┐  ┌──────────┐
                  │ Runway  │  │Stability│  │ ComfyUI  │
                  │   API   │  │   API   │  │(Port 8188│
                  └─────────┘  └─────────┘  └──────────┘
```

## Benefits of ComfyUI Integration

1. **Local Generation**: No API costs for video generation
2. **Full Control**: Customize workflows with nodes
3. **Privacy**: All processing happens locally
4. **Flexibility**: Support for any ComfyUI-compatible models
5. **Community**: Access to thousands of community workflows and models

Happy video generating! 🎥✨
