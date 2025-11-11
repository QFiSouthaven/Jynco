# ComfyUI Quick Start Guide

ComfyUI is now properly configured and ready to use! This guide will help you get started.

## What Was Changed

✅ ComfyUI service is now **active** in `docker-compose.yml`
✅ Using official Docker image: `yanwk/comfyui-boot:latest`
✅ Proper volume mounts for models, input, and output
✅ Health checks configured
✅ Ready for GPU acceleration (optional)

## Starting ComfyUI

### 1. Start All Services

```bash
cd /home/user/Jynco
docker-compose up -d
```

This will start:
- PostgreSQL, Redis, RabbitMQ
- Backend API (port 8000)
- Frontend (port 3000)
- AI Workers (2 replicas)
- Composition Worker
- **ComfyUI (port 8188)** ✨

### 2. Wait for ComfyUI to Initialize

ComfyUI takes ~30-60 seconds to start up on first run:

```bash
# Watch ComfyUI logs
docker-compose logs -f comfyui

# Check service status
docker-compose ps comfyui
```

Look for messages like:
```
Starting server on 0.0.0.0:8188
To see the GUI go to: http://0.0.0.0:8188
```

### 3. Access ComfyUI

Once running, access ComfyUI at:
- **Web Interface**: http://localhost:8188
- **API**: http://localhost:8188/api

## Using ComfyUI with Video Foundry

### Option 1: Via API (Automatic)

When creating a video project, specify ComfyUI as the model:

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Video Project",
    "segments": [{
      "prompt": "A beautiful sunset over mountains",
      "duration": 5,
      "model": "comfyui"
    }]
  }'
```

### Option 2: Via Frontend

1. Go to http://localhost:3000
2. Create a new project
3. Add segments with prompts
4. **Important**: The system will automatically use ComfyUI if it's available

## GPU Support (Optional)

For faster generation with NVIDIA GPUs:

1. Install nvidia-docker2:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

2. Uncomment GPU section in `docker-compose.yml`:
```yaml
comfyui:
  # ... other config ...
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

3. Restart ComfyUI:
```bash
docker-compose restart comfyui
```

## Troubleshooting

### ComfyUI Won't Start

```bash
# Check logs
docker-compose logs comfyui

# Restart service
docker-compose restart comfyui

# Full rebuild
docker-compose down
docker-compose up -d
```

### Workers Still Using Mock Adapter

The system uses ComfyUI automatically when:
1. ComfyUI service is healthy
2. `COMFYUI_URL` is set (default: `http://comfyui:8188`)
3. Model parameter is set to "comfyui" or "comfy"

To verify configuration:
```bash
# Check worker environment
docker-compose exec ai_worker env | grep COMFYUI

# Expected output: COMFYUI_URL=http://comfyui:8188
```

### Port Already in Use

If port 8188 is already taken:

1. Edit `docker-compose.yml`:
```yaml
comfyui:
  ports:
    - "8189:8188"  # Use different external port
```

2. Update `COMFYUI_URL`:
```yaml
ai_worker:
  environment:
    COMFYUI_URL: http://comfyui:8188  # Keep internal port the same
```

## Next Steps

- **Custom Models**: Add models to `comfyui_models` volume
- **Custom Workflows**: Update workflow JSON in `workers/ai_worker/adapters/comfyui.py`
- **Scaling**: Increase worker replicas in `docker-compose.yml`

For detailed documentation, see:
- [COMFYUI_SETUP_GUIDE.md](./COMFYUI_SETUP_GUIDE.md) - Full setup guide
- [DOCKER_TESTING_GUIDE.md](./DOCKER_TESTING_GUIDE.md) - Docker testing guide

## Architecture

```
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
RabbitMQ Queue
    ↓
AI Workers
    ↓
ComfyUI Adapter
    ↓
ComfyUI Service (port 8188)
    ↓
Generated Videos → S3 Storage
```

## Fallback Behavior

If ComfyUI is unavailable, the system automatically falls back to:
1. Other configured models (Runway, Stability AI)
2. Mock adapter (for development/testing)

No manual intervention required!
