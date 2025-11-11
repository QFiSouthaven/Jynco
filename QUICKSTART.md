# 🚀 Quick Start Guide

Get Video Foundry running in under 5 minutes with **zero external dependencies**!

## Prerequisites

- Docker & Docker Compose
- Git
- 4GB RAM minimum

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

**That's it!** The default `.env` configuration works out of the box:
- ✅ AI Model: `mock-ai` (no API keys needed)
- ✅ Storage: Local file system (no S3 required)
- ✅ All services: Pre-configured for Docker

### 3. Start the System

```bash
docker-compose up --build
```

Wait for all services to start (about 2-3 minutes on first run).

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 🎬 Create Your First Video

1. **Open the Frontend**: http://localhost:3000
2. **Create a Project**: Click "New Project" and give it a name
3. **Add Segments**:
   - Click "Add Segment"
   - Enter a prompt (e.g., "A rocket launching into space")
   - Click Save
4. **Render**: Click "Render Project"
5. **Watch Progress**: See real-time updates as segments are generated

## Configuration Options

### Using Different AI Models

Edit `.env` and change `AI_MODEL`:

```bash
# No API needed (default)
AI_MODEL=mock-ai

# Self-hosted Stable Diffusion
AI_MODEL=local-sd
COMFY_URL=http://localhost:8188

# External APIs (requires API keys)
AI_MODEL=runway-gen3
RUNWAY_API_KEY=your_key_here

AI_MODEL=stability-ai
STABILITY_API_KEY=your_key_here
```

### Using S3 Storage

To use AWS S3 instead of local storage:

```bash
USE_LOCAL_STORAGE=false
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

## Troubleshooting

### Services Won't Start

**Problem**: Docker shows errors during startup

**Solution**:
```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### Port Already in Use

**Problem**: Error: "port is already allocated"

**Solution**: Change ports in `docker-compose.yml` or stop conflicting services:
```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

### Worker Not Processing Jobs

**Problem**: Segments stuck in "Pending" status

**Solution**: Check worker logs:
```bash
docker-compose logs ai_worker
docker-compose logs composition_worker
```

### Database Connection Errors

**Problem**: Backend can't connect to PostgreSQL

**Solution**: Wait for PostgreSQL health check to pass:
```bash
docker-compose ps  # Check service status
docker-compose logs postgres  # Check PostgreSQL logs
```

## Development Mode

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Worker Development

```bash
cd workers/ai_worker
python worker.py
```

## Scaling Workers

To handle more concurrent video generation:

Edit `docker-compose.yml`:

```yaml
ai_worker:
  deploy:
    replicas: 4  # Increase from 1 to 4
```

Then restart:

```bash
docker-compose up -d --scale ai_worker=4
```

## Architecture Overview

```
┌─────────────┐
│  Frontend   │ (React @ :3000)
│   (Vite)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│   Backend   │────→│  PostgreSQL  │
│  (FastAPI)  │     │   Database   │
└──────┬──────┘     └──────────────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│  RabbitMQ   │────→│  AI Worker   │
│    Queue    │     │   (x1-N)     │
└─────────────┘     └──────────────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│ Composition │────→│    Redis     │
│   Worker    │     │    Cache     │
└─────────────┘     └──────────────┘
```

## Next Steps

- 📚 Read the [Self-Hosted AI Guide](docs/SELF_HOSTED_AI_GUIDE.md) to run your own AI models
- 🔧 Explore the [API Documentation](http://localhost:8000/docs)
- 📖 Check the [Architecture Overview](docs/ARCHITECTURE.md)
- 🎯 Review the [API Integration Guide](docs/API_INTEGRATION.md)

## Support

- **Issues**: https://github.com/QFiSouthaven/Jynco/issues
- **Discussions**: https://github.com/QFiSouthaven/Jynco/discussions
- **Documentation**: See the `docs/` directory

## License

MIT License - see [LICENSE](LICENSE) for details
