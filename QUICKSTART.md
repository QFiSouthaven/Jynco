# Video Foundry - Quick Start Guide

## Prerequisites

- Docker Desktop installed and running
- NVIDIA GPU with drivers installed (for GPU acceleration)
- NVIDIA Container Toolkit installed

## Launch Scripts

This project includes convenient launch scripts for easy management:

### Windows

```bash
# Start all services
start.bat

# Stop all services
stop.bat

# View logs
logs.bat

# Check status
status.bat
```

### Linux/WSL/Mac

```bash
# Start all services
./start.sh

# Stop all services
./stop.sh

# View logs
./logs.sh

# Check status
./status.sh
```

## What the Launch Script Does

1. **Checks Docker**: Verifies Docker is running
2. **Stops existing services**: Cleans up any running containers
3. **Builds images**: Builds all Docker images with latest code
4. **Starts services**: Launches all services with GPU support
5. **Verifies startup**: Checks service health and GPU access

## Service URLs

Once started, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:5173
- **RabbitMQ Management**: http://localhost:15672 (username: `guest`, password: `guest`)

## Services Overview

### Infrastructure Services
- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Caching
- **RabbitMQ** (ports 5672, 15672) - Message queue

### Application Services
- **Backend API** (port 8000) - FastAPI REST API
- **Frontend** (port 5173) - React web interface
- **AI Workers** (2 replicas) - GPU-accelerated video generation
- **Composition Worker** - Video composition and stitching

## Manual Docker Commands

If you prefer using Docker Compose directly:

```bash
# Start services
docker compose --env-file .env.local up -d

# Stop services
docker compose --env-file .env.local down

# View logs
docker compose --env-file .env.local logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f ai_worker

# Rebuild a specific service
docker compose build backend
docker compose up -d backend

# Check service status
docker compose ps

# Check GPU access
docker exec jynco-ai_worker-1 nvidia-smi
```

## Troubleshooting

### Services won't start
1. Check Docker Desktop is running
2. Run `stop.bat` (or `./stop.sh`) to clean up
3. Run `start.bat` (or `./start.sh`) again

### GPU not detected
1. Verify NVIDIA drivers: `nvidia-smi`
2. Check Docker GPU support: `docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi`
3. Ensure NVIDIA Container Toolkit is installed

### Port conflicts
If ports 8000, 5173, 5432, 6379, 5672, or 15672 are in use:
1. Stop conflicting applications
2. Or modify port mappings in `docker-compose.yml`

### Import errors in logs
If you see "ModuleNotFoundError":
1. Rebuild images: `docker compose build --no-cache`
2. Restart services

## Development Workflow

1. **Start services**: Run `start.bat` or `./start.sh`
2. **Make code changes**: Edit files in `backend/`, `frontend/`, or `workers/`
3. **Backend auto-reload**: Backend has hot reload enabled - changes apply automatically
4. **Frontend auto-reload**: Frontend has hot reload enabled - changes apply automatically
5. **Workers**: Restart workers after changes: `docker compose restart ai_worker composition_worker`
6. **View logs**: Run `logs.bat` or `./logs.sh` to monitor output

## First Time Setup

After starting for the first time:

1. The database tables will be created automatically
2. Check logs to ensure all services connected: `docker compose logs`
3. Visit http://localhost:8000/docs to explore the API
4. Visit http://localhost:5173 to access the web interface

## Stopping Services

Always use the stop script or `docker compose down` to cleanly shut down:

```bash
# Windows
stop.bat

# Linux/WSL/Mac
./stop.sh
```

## Getting Help

- Check service logs: `docker compose logs [service-name]`
- Check service status: `status.bat` or `./status.sh`
- View API documentation: http://localhost:8000/docs
