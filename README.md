# Video Foundry - AI-Powered Video Generation Platform

<div align="center">

**A scalable, production-ready platform for generating AI videos with timeline-based editing and ComfyUI integration**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## Overview

Video Foundry is a sophisticated AI video generation platform that combines the power of multiple AI models with an intelligent timeline-based editing system. Built for both developers and content creators, it provides a seamless workflow for creating AI-generated video content at scale.

### Key Highlights

- **Timeline-Based Editing**: Visual timeline editor for managing multi-segment video projects
- **ComfyUI Integration**: Leverage ComfyUI's powerful node-based workflows for local video generation
- **Multiple AI Models**: Support for Runway Gen-3, Stability AI, ComfyUI, and custom adapters
- **Intelligent Re-rendering**: Only regenerates modified segments, saving time and resources
- **Real-time Progress**: WebSocket-based progress tracking for all render jobs
- **Scalable Architecture**: Horizontally scalable worker services for high-volume production
- **Local or Cloud**: Generate videos locally with ComfyUI or use cloud APIs

## Features

### Video Generation
- **Text-to-Video**: Generate videos from text prompts using AnimateDiff + SDXL
- **Image-to-Video**: Animate static images using Stable Video Diffusion
- **Custom Workflows**: Create and export custom ComfyUI workflows
- **Batch Processing**: Generate multiple segments in parallel

### Timeline Management
- **Visual Editor**: Drag-and-drop timeline interface
- **Segment Control**: Add, edit, delete, and reorder video segments
- **Smart Updates**: Change prompts or parameters without regenerating entire projects
- **Version Control**: Track changes and render history

### Integration & Extensibility
- **Pluggable Adapters**: Easy integration with new AI models
- **API-First Design**: RESTful API for all operations
- **Webhook Support**: Real-time notifications via WebSockets
- **S3 Storage**: Automatic storage and CDN delivery

### Production Ready
- **Docker Deployment**: One-command deployment with Docker Compose
- **Health Monitoring**: Built-in health checks for all services
- **Error Recovery**: Automatic retry logic and graceful degradation
- **Logging & Metrics**: Comprehensive logging for debugging and monitoring

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Git](https://git-scm.com/)
- (Optional) NVIDIA GPU with CUDA for local ComfyUI generation

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration (optional for local setup)
```

3. **Start all services**
```bash
# Using Docker Compose
docker-compose up -d

# Or use the provided startup scripts
# Windows:
start.bat

# Linux/Mac:
./start.sh
```

4. **Access the application**
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ComfyUI Interface**: http://localhost:8188
- **RabbitMQ Console**: http://localhost:15672 (guest/guest)
- **Portainer**: http://localhost:9000

### First Video

1. Open the frontend at http://localhost:5173
2. Click "Create Project" and enter a name
3. Add a segment with a prompt (e.g., "A serene beach at sunset")
4. Select the AI model (ComfyUI for local generation)
5. Click "Render" and watch the progress in real-time
6. Download your generated video when complete

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Video Foundry Platform                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐       ┌──────────────┐                        │
│  │   Frontend   │◄─────►│   Backend    │                        │
│  │  (React/TS)  │       │  (FastAPI)   │                        │
│  └──────────────┘       └──────┬───────┘                        │
│                                 │                                 │
│                    ┌────────────┼────────────┐                  │
│                    ▼            ▼            ▼                   │
│            ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│            │PostgreSQL│  │  Redis   │  │ RabbitMQ │            │
│            │          │  │          │  │          │            │
│            └──────────┘  └──────────┘  └────┬─────┘            │
│                                              │                   │
│                           ┌──────────────────┴─────────┐        │
│                           ▼                            ▼         │
│                    ┌─────────────┐            ┌─────────────┐  │
│                    │ AI Workers  │            │ Composition │  │
│                    │  (Parallel) │            │   Worker    │  │
│                    └──────┬──────┘            └──────┬──────┘  │
│                           │                          │          │
│                           ▼                          ▼          │
│              ┌───────────────────┐        ┌────────────────┐  │
│              │     ComfyUI       │        │   S3/Local     │  │
│              │  (Local Models)   │        │    Storage     │  │
│              └───────────────────┘        └────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend (`/frontend`)
- **Technology**: React 18 + TypeScript + TailwindCSS
- **State Management**: Zustand
- **Features**: Timeline editor, real-time progress, drag-and-drop

#### Backend (`/backend`)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **API**: RESTful endpoints + WebSocket support
- **Orchestration**: Manages render jobs and segment lifecycle

#### Workers (`/workers`)
1. **AI Worker** (`/workers/ai_worker`)
   - Processes video generation requests
   - Supports multiple AI model adapters
   - Horizontal scaling (run multiple instances)

2. **Composition Worker** (`/workers/composition_worker`)
   - Combines segments into final video
   - FFMPEG-based video processing
   - Handles transitions and effects

#### Supporting Services
- **PostgreSQL**: Persistent data storage
- **Redis**: Real-time state and caching
- **RabbitMQ**: Task queue and message broker
- **ComfyUI**: Local AI video/image generation
- **S3/MinIO**: Video asset storage

### Data Flow

```
User Request → Backend API → RabbitMQ Queue
                    ↓
              AI Workers (parallel)
                    ↓
         Generate Video Segments
                    ↓
              Store in S3/Local
                    ↓
        Update DB + Redis Progress
                    ↓
        Composition Queue → Worker
                    ↓
         Combine All Segments
                    ↓
         Final Video → Storage
                    ↓
      WebSocket → Frontend Update
```

## Documentation

### User Documentation
- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [User Guide](docs/USER_GUIDE.md) - How to create and manage video projects
- [ComfyUI Integration](docs/COMFYUI_INTEGRATION.md) - Working with ComfyUI workflows
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

### Developer Documentation
- [API Reference](http://localhost:8000/docs) - Interactive API documentation (Swagger)
- [Workflow Templates](workflows/README.md) - ComfyUI workflow guide
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

### Quick References
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - API and CLI quick reference
- [DOCKER_TESTING_GUIDE.md](DOCKER_TESTING_GUIDE.md) - Testing with Docker

## Technology Stack

### Backend & Workers
- **Python 3.11+**: Core programming language
- **FastAPI**: Modern web framework with automatic OpenAPI docs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Celery Alternative**: RabbitMQ + custom workers
- **HTTPX**: Async HTTP client for external APIs

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Vite**: Fast build tool and dev server

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **PostgreSQL 15**: Relational database
- **Redis 7**: In-memory data store
- **RabbitMQ 3**: Message broker
- **NGINX**: Reverse proxy (production)
- **ComfyUI**: Node-based AI workflow interface

### AI Models & APIs
- **ComfyUI**: Local video generation (AnimateDiff, SVD)
- **Runway Gen-3**: Cloud-based video generation API
- **Stability AI**: Image and video generation API
- **Custom Adapters**: Extensible model interface

## Configuration

### Environment Variables

Key configuration options (see [.env.example](.env.example)):

```bash
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/videofoundry

# Redis & RabbitMQ
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# AI Services
COMFYUI_URL=http://comfyui:8188
RUNWAY_API_KEY=your_runway_api_key      # Optional
STABILITY_API_KEY=your_stability_api_key # Optional

# Storage (S3 or Local)
S3_BUCKET=video-foundry-dev
AWS_ACCESS_KEY_ID=your_access_key        # Optional for S3
AWS_SECRET_ACCESS_KEY=your_secret_key    # Optional for S3

# Application
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### GPU Support

For NVIDIA GPU acceleration with ComfyUI:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Uncomment GPU sections in `docker-compose.yml`:

```yaml
# Uncomment for GPU support (NVIDIA)
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Development

### Local Development Setup

1. **Backend Development**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend Development**
```bash
cd frontend
npm install
npm run dev
```

3. **Worker Development**
```bash
cd workers/ai_worker
pip install -r requirements.txt
python worker.py
```

### Running Tests

```bash
# Backend tests
cd tests
pip install -r requirements.txt
pytest -v

# E2E tests
pytest tests/e2e/ -v

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Production Deployment

1. **Update environment variables**
```bash
cp .env.example .env.production
# Edit .env.production with production values
```

2. **Use production Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Configure reverse proxy** (NGINX example)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Setup SSL/TLS** with Let's Encrypt
```bash
certbot --nginx -d your-domain.com
```

### Scaling

**Scale AI workers horizontally:**
```bash
docker-compose up -d --scale ai_worker=4
```

**Monitor with Portainer:**
- Access http://localhost:9000
- View logs, resource usage, and scale services

## Performance Tuning

### ComfyUI Optimization
- Use `--lowvram` flag for systems with limited VRAM
- Use `--medvram` for better performance on mid-range GPUs
- Use `--highvram` for maximum speed on high-end GPUs

### Database Optimization
- Add indexes for frequently queried fields
- Use connection pooling (already configured)
- Regular VACUUM and ANALYZE operations

### Worker Optimization
- Adjust worker count based on GPU memory
- Use Redis for caching frequently accessed data
- Implement request batching for external APIs

## Monitoring & Logging

### Application Logs
```bash
# View all logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai_worker
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# ComfyUI health
curl http://localhost:8188/system_stats
```

### Metrics
- RabbitMQ Management: http://localhost:15672
- Portainer Dashboard: http://localhost:9000
- Custom metrics via `/api/health` endpoint

## Security Best Practices

1. **Change default credentials** in production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Restrict CORS origins** to your domain
5. **Implement authentication** (JWT ready)
6. **Regular security updates** for dependencies
7. **Use secrets management** (e.g., AWS Secrets Manager)

## Troubleshooting

### Common Issues

**ComfyUI not starting**
- Check GPU drivers are installed
- Verify docker has GPU access
- Try without GPU first

**Workers not processing**
- Check RabbitMQ connection
- Verify queue names match in .env
- Check worker logs for errors

**Out of memory errors**
- Reduce video resolution
- Reduce batch size/frame count
- Add more RAM or use swap

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## Roadmap

- [ ] User authentication and multi-tenancy
- [ ] Advanced video editing features
- [ ] More AI model integrations
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Video preview and trimming
- [ ] Audio track support
- [ ] Transition effects library
- [ ] Template library for common workflows

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute
- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests
- Create ComfyUI workflow templates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/QFiSouthaven/Jynco/issues)
- **Discussions**: [GitHub Discussions](https://github.com/QFiSouthaven/Jynco/discussions)

## Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Node-based AI workflow interface
- [AnimateDiff](https://github.com/guoyww/AnimateDiff) - Text-to-video generation
- [Stability AI](https://stability.ai/) - Stable Video Diffusion
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI framework

## Project Status

**Current Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: January 2025

---

<div align="center">

Made with ❤️ by the Video Foundry Team

[Documentation](docs/) • [API Docs](http://localhost:8000/docs) • [GitHub](https://github.com/QFiSouthaven/Jynco)

</div>
