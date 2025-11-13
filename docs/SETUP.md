# Setup Guide - Video Foundry

This comprehensive guide will walk you through setting up Video Foundry from scratch, including all prerequisites, configuration, and optional components.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Environment Configuration](#environment-configuration)
- [Docker Setup](#docker-setup)
- [ComfyUI Installation](#comfyui-installation)
- [Database Setup](#database-setup)
- [Storage Configuration](#storage-configuration)
- [GPU Configuration](#gpu-configuration)
- [Verification](#verification)
- [Next Steps](#next-steps)

## Prerequisites

### Required Software

#### 1. Docker & Docker Compose

**Linux:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

**macOS:**
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

**Windows:**
```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# Enable WSL 2 backend for better performance
wsl --install

# Verify installation
docker --version
docker-compose --version
```

#### 2. Git

**Linux:**
```bash
sudo apt-get update
sudo apt-get install git
```

**macOS:**
```bash
brew install git
```

**Windows:**
- Download from: https://git-scm.com/download/win

### Optional Software

#### For Local Development (Without Docker)

**Python 3.11+:**
```bash
# Linux/macOS
curl https://pypa.io/get-pip.py -o get-pip.py
python3.11 --version

# Windows
# Download from: https://www.python.org/downloads/
```

**Node.js 18+:**
```bash
# Linux/macOS (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Windows
# Download from: https://nodejs.org/
```

#### For GPU Acceleration (NVIDIA)

**NVIDIA Container Toolkit:**
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB free space
- OS: Linux, macOS 10.15+, Windows 10/11 with WSL2

**Recommended for ComfyUI:**
- CPU: 8+ cores
- RAM: 16+ GB
- GPU: NVIDIA GPU with 8+ GB VRAM
- Storage: 50+ GB free space (for models)
- OS: Ubuntu 22.04 LTS or Windows 11 with WSL2

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest and most reliable method. All services run in containers.

#### 1. Clone the Repository

```bash
git clone https://github.com/QFiSouthaven/Jynco.git
cd Jynco
```

#### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings (see [Environment Configuration](#environment-configuration))

#### 3. Start All Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- ComfyUI: http://localhost:8188
- RabbitMQ: http://localhost:15672 (guest/guest)
- Portainer: http://localhost:9000

### Method 2: Local Development

For active development, you may want to run services locally.

#### 1. Start Infrastructure Services

```bash
# Start only database, redis, rabbitmq, comfyui
docker-compose up -d postgres redis rabbitmq comfyui
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

#### 4. AI Worker

```bash
cd workers/ai_worker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start worker
python worker.py
```

#### 5. Composition Worker

```bash
cd workers/composition_worker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start worker
python worker.py
```

## Environment Configuration

### Basic Configuration

Edit the `.env` file with your settings:

```bash
# ================================
# DATABASE CONFIGURATION
# ================================
# For Docker: use service name 'postgres'
# For local: use 'localhost'
DATABASE_URL=postgresql://postgres:password@postgres:5432/videofoundry

# ================================
# REDIS CONFIGURATION
# ================================
REDIS_URL=redis://redis:6379/0

# ================================
# RABBITMQ CONFIGURATION
# ================================
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
SEGMENT_QUEUE_NAME=segment_generation
COMPOSITION_QUEUE_NAME=video_composition

# ================================
# STORAGE CONFIGURATION
# ================================
# Option 1: S3 Storage (Production)
S3_BUCKET=video-foundry-production
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_REGION=us-east-1

# Option 2: Local Storage (Development)
# Leave AWS credentials empty to use local storage
# Videos will be stored in Docker volume 'local_videos'

# ================================
# AI MODEL CONFIGURATION
# ================================
# ComfyUI (Local generation - always available)
COMFYUI_URL=http://comfyui:8188

# Runway Gen-3 (Optional - Cloud API)
RUNWAY_API_KEY=your_runway_api_key

# Stability AI (Optional - Cloud API)
STABILITY_API_KEY=your_stability_api_key

# ================================
# APPLICATION CONFIGURATION
# ================================
SECRET_KEY=your-super-secret-key-change-this-in-production
ENVIRONMENT=development
DEBUG=true

# CORS - Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174

# ================================
# JWT CONFIGURATION
# ================================
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production Configuration

For production, create a separate `.env.production`:

```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-random-key>

# Use production database
DATABASE_URL=postgresql://user:password@prod-db-host:5432/videofoundry

# Use production Redis
REDIS_URL=redis://prod-redis-host:6379/0

# Use production S3
S3_BUCKET=video-foundry-production
AWS_ACCESS_KEY_ID=<production-key>
AWS_SECRET_ACCESS_KEY=<production-secret>

# Restrict CORS to your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Docker Setup

### Understanding Docker Compose

The `docker-compose.yml` file defines all services:

```yaml
services:
  postgres       # PostgreSQL database
  redis          # Redis cache
  rabbitmq       # Message queue
  backend        # FastAPI backend
  frontend       # React frontend
  ai_worker      # AI generation worker
  composition_worker  # Video composition worker
  comfyui        # ComfyUI service
  portainer      # Docker management UI
```

### Common Docker Commands

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis rabbitmq

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f ai_worker

# Scale workers
docker-compose up -d --scale ai_worker=4

# Rebuild services
docker-compose build
docker-compose up -d --build

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d videofoundry
```

### Managing Docker Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect jynco_postgres_data

# Backup database
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres videofoundry < backup.sql

# Remove unused volumes
docker volume prune
```

## ComfyUI Installation

### Basic ComfyUI Setup (Docker)

ComfyUI runs automatically in Docker. No additional setup needed for basic functionality.

```bash
# Check ComfyUI status
docker-compose logs comfyui

# Access ComfyUI interface
# Open: http://localhost:8188
```

### Installing ComfyUI Models

ComfyUI needs AI models to generate videos. Install them in the Docker volume.

#### Option 1: Install via ComfyUI Manager (Easiest)

1. Access ComfyUI: http://localhost:8188
2. Click "Manager" button
3. Click "Install Models"
4. Search and install:
   - "Stable Diffusion XL Base 1.0"
   - "AnimateDiff Motion Module"
   - "Stable Video Diffusion XT"

#### Option 2: Manual Installation

```bash
# Access ComfyUI container
docker-compose exec comfyui bash

# Create directories
cd /home/runner/models
mkdir -p checkpoints

# Download Stable Diffusion XL
cd checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Download AnimateDiff motion module
cd ..
mkdir -p custom_nodes/ComfyUI-AnimateDiff-Evolved/models
cd custom_nodes/ComfyUI-AnimateDiff-Evolved/models
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt

# Download SVD for image-to-video
cd /home/runner/models/checkpoints
wget https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main/svd_xt.safetensors
```

#### Option 3: Mount Local Model Directory

Edit `docker-compose.yml`:

```yaml
comfyui:
  volumes:
    - /path/to/your/local/models:/home/runner/models
    - comfyui_output:/home/runner/ComfyUI/output
```

Then copy your existing models to that directory.

### Installing Custom Nodes

Required custom nodes for the default workflows:

```bash
# Access ComfyUI container
docker-compose exec comfyui bash

cd /home/runner/ComfyUI/custom_nodes

# Install AnimateDiff
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt

# Install VideoHelperSuite
cd /home/runner/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt

# Restart ComfyUI
exit
docker-compose restart comfyui
```

### Verify ComfyUI Setup

```bash
# Test ComfyUI API
curl http://localhost:8188/system_stats

# Expected response: JSON with system information
```

Load a workflow:
1. Open http://localhost:8188
2. Click "Load"
3. Select `/workflows/text-to-video-basic.json`
4. Click "Queue Prompt"
5. Check if generation starts

## Database Setup

### Automatic Setup (Docker)

Database is created automatically when using Docker Compose.

### Manual Database Setup

If running PostgreSQL separately:

```bash
# Create database
createdb -U postgres videofoundry

# Or via psql
psql -U postgres
CREATE DATABASE videofoundry;
\q
```

### Running Migrations

```bash
# Docker
docker-compose exec backend alembic upgrade head

# Local
cd backend
alembic upgrade head
```

### Database Management

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d videofoundry

# Useful queries
\dt                          # List tables
\d+ projects                 # Describe table
SELECT * FROM projects;      # View data
\q                           # Quit

# Create backup
docker-compose exec postgres pg_dump -U postgres videofoundry > backup-$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U postgres videofoundry < backup-20250113.sql

# Reset database (WARNING: deletes all data)
docker-compose exec postgres psql -U postgres -c "DROP DATABASE videofoundry;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE videofoundry;"
docker-compose exec backend alembic upgrade head
```

## Storage Configuration

### Option 1: S3 Storage (Production)

**AWS S3 Setup:**

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Create bucket
aws s3 mb s3://video-foundry-production --region us-east-1

# Set bucket policy (public read for videos)
aws s3api put-bucket-policy --bucket video-foundry-production --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::video-foundry-production/*"
  }]
}'

# Enable CORS
aws s3api put-bucket-cors --bucket video-foundry-production --cors-configuration '{
  "CORSRules": [{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }]
}'
```

Update `.env`:
```bash
S3_BUCKET=video-foundry-production
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

**MinIO Setup (Self-hosted S3-compatible):**

```yaml
# Add to docker-compose.yml
minio:
  image: minio/minio
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  ports:
    - "9000:9000"
    - "9001:9001"
  volumes:
    - minio_data:/data
```

Update `.env`:
```bash
S3_BUCKET=videofoundry
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_ENDPOINT_URL=http://minio:9000
```

### Option 2: Local Storage (Development)

Leave AWS credentials empty in `.env`:

```bash
# Don't set these or leave them empty
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
```

Videos will be stored in Docker volume `local_videos`:

```bash
# View local videos
docker-compose exec backend ls -la /videos

# Copy video from container
docker cp vf_backend:/videos/segment-123.mp4 ./downloads/
```

## GPU Configuration

### NVIDIA GPU Support

#### 1. Install NVIDIA Drivers

```bash
# Ubuntu
sudo ubuntu-drivers autoinstall
sudo reboot

# Verify
nvidia-smi
```

#### 2. Install NVIDIA Container Toolkit

```bash
# Add repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

#### 3. Enable GPU in docker-compose.yml

Uncomment GPU sections:

```yaml
comfyui:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]

ai_worker:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

#### 4. Restart Services

```bash
docker-compose down
docker-compose up -d

# Verify GPU access
docker-compose exec comfyui nvidia-smi
```

### AMD GPU Support

AMD GPU support requires ROCm. This is more complex and less tested:

```bash
# Install ROCm
# See: https://docs.amd.com/en/latest/deploy/linux/index.html

# Use ROCm-compatible ComfyUI image
# Modify docker-compose.yml to use ROCm image
```

### CPU-Only Mode

ComfyUI works on CPU but is very slow:

```bash
# Modify docker-compose.yml
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --cpu
```

## Verification

### 1. Check All Services

```bash
docker-compose ps

# All services should show "Up" status
```

### 2. Check Health Endpoints

```bash
# Backend health
curl http://localhost:8000/health

# ComfyUI health
curl http://localhost:8188/system_stats

# PostgreSQL
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping

# RabbitMQ
docker-compose exec rabbitmq rabbitmq-diagnostics ping
```

### 3. Test API

```bash
# List projects
curl http://localhost:8000/api/projects

# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "Testing setup"}'
```

### 4. Access Web Interfaces

Visit each URL and verify it loads:

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- ComfyUI: http://localhost:8188
- RabbitMQ: http://localhost:15672 (guest/guest)
- Portainer: http://localhost:9000

### 5. Test Video Generation

Run the test script:

```bash
python test_workflow.py
```

Or manually through the UI:
1. Open http://localhost:5173
2. Create a new project
3. Add a segment with prompt
4. Click "Render"
5. Monitor progress
6. Download result

## Next Steps

- [User Guide](USER_GUIDE.md) - Learn how to create videos
- [ComfyUI Integration](COMFYUI_INTEGRATION.md) - Customize workflows
- [Troubleshooting](TROUBLESHOOTING.md) - Fix common issues
- [API Documentation](http://localhost:8000/docs) - Explore the API

## Additional Resources

### Model Downloads

- Stable Diffusion XL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- AnimateDiff: https://huggingface.co/guoyww/animatediff
- Stable Video Diffusion: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt

### Documentation

- Docker: https://docs.docker.com/
- ComfyUI: https://docs.comfy.org/
- FastAPI: https://fastapi.tiangolo.com/
- PostgreSQL: https://www.postgresql.org/docs/

### Support

- GitHub Issues: https://github.com/QFiSouthaven/Jynco/issues
- Community Forum: https://github.com/QFiSouthaven/Jynco/discussions

---

**Setup complete! Ready to create AI videos!**
