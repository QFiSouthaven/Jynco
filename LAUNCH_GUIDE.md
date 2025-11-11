# 🚀 Jynco Video Foundry - Launch Guide

This guide will help you launch the Jynco Video Foundry platform on your local machine or server.

## Prerequisites

Before launching, ensure you have:

1. **Docker** (version 20.10+)
   - Download: https://docs.docker.com/get-docker/

2. **Docker Compose** (version 2.0+)
   - Usually included with Docker Desktop
   - Linux: https://docs.docker.com/compose/install/

3. **System Requirements**
   - 8GB+ RAM allocated to Docker
   - 10GB+ free disk space
   - Ports available: 3000, 5432, 5672, 6379, 8000, 15672

4. **API Keys** (Optional for testing, required for AI features)
   - AWS credentials (S3 storage)
   - Runway API key (AI video generation)
   - Stability AI API key (AI image/video generation)

## Quick Launch (Automated)

The easiest way to launch the platform:

```bash
# Make sure you're in the project directory
cd /home/user/Jynco

# Run the launch script
./launch.sh
```

The script will:
- ✅ Check Docker availability
- ✅ Create .env file if needed
- ✅ Stop any existing containers
- ✅ Build and start all services
- ✅ Verify service health
- ✅ Display access URLs

## Manual Launch

If you prefer to launch manually:

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
```

**Required Configuration:**

```env
# For AI features to work (optional for basic testing)
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
S3_BUCKET=your-bucket-name
RUNWAY_API_KEY=your_runway_key
STABILITY_API_KEY=your_stability_key

# Change in production
SECRET_KEY=generate-a-secure-random-key-here
```

### Step 2: Start Services

```bash
# Build and start all services in detached mode
docker-compose up -d --build

# Wait for services to initialize (~30 seconds)
sleep 30

# Check service status
docker-compose ps
```

### Step 3: Verify Services

All services should show as "Up":

```
     Name                   Command              State           Ports
-------------------------------------------------------------------------
jynco_backend_1         uvicorn main:app ...         Up      0.0.0.0:8000->8000/tcp
jynco_frontend_1        npm run dev                  Up      0.0.0.0:3000->3000/tcp
jynco_postgres_1        docker-entrypoint ...        Up      5432/tcp
jynco_redis_1           docker-entrypoint ...        Up      6379/tcp
jynco_rabbitmq_1        docker-entrypoint ...        Up      5672/tcp, 15672/tcp
jynco_ai_worker_1       python worker.py             Up
jynco_composition_...   python worker.py             Up
```

## Access Points

Once launched, access the platform at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:3000 | Create account on first visit |
| **Backend API** | http://localhost:8000 | N/A |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |

## Architecture Overview

The platform consists of 7 Docker containers:

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                        │
│                     http://localhost:3000                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Frontend    │  React + TypeScript
                    │  (Port 3000)  │  Vite Dev Server
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Backend     │  FastAPI + Python
                    │  (Port 8000)  │  REST API + WebSockets
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │PostgreSQL│    │  Redis   │    │ RabbitMQ │
    │  (5432)  │    │  (6379)  │    │  (5672)  │
    └──────────┘    └──────────┘    └────┬─────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
                ┌──────────────┐                  ┌──────────────┐
                │  AI Worker   │                  │ Composition  │
                │   (x2 pods)  │                  │   Worker     │
                │ Video Gen    │                  │ Video Merge  │
                └──────────────┘                  └──────────────┘
```

## Service Descriptions

### Frontend (Port 3000)
- React-based web interface
- Timeline editor for video projects
- Real-time progress tracking
- User authentication

### Backend (Port 8000)
- FastAPI REST API
- WebSocket server for real-time updates
- Authentication & authorization
- Database management
- Task orchestration

### PostgreSQL (Port 5432)
- Primary database
- Stores projects, segments, users
- Persistent volume: `./postgres_data`

### Redis (Port 6379)
- Session management
- Caching layer
- Real-time state tracking

### RabbitMQ (Ports 5672, 15672)
- Message broker
- Task queue management
- Worker coordination

### AI Workers (x2)
- Video generation from prompts
- Runway Gen-3 integration
- Stability AI integration
- Horizontally scalable

### Composition Worker
- Video stitching/merging
- FFMPEG processing
- Timeline assembly

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai_worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
docker-compose restart ai_worker
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop, remove, and delete volumes (CAUTION: deletes database)
docker-compose down -v
```

### Scale Workers

```bash
# Scale AI workers to 4 instances
docker-compose up -d --scale ai_worker=4

# Scale back to 2
docker-compose up -d --scale ai_worker=2
```

### Database Management

```bash
# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d videofoundry

# Backup database
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres videofoundry < backup.sql
```

### Reset Everything

```bash
# Nuclear option: delete all containers, volumes, and images
docker-compose down -v
docker-compose up -d --build --force-recreate
```

## Testing the Installation

After launching, verify functionality:

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 2. Create Test User

Visit http://localhost:3000 and register a new account.

### 3. API Documentation

Visit http://localhost:8000/docs to explore the interactive API documentation.

### 4. RabbitMQ Queues

1. Visit http://localhost:15672
2. Login: guest / guest
3. Check "Queues" tab - should see:
   - `segment_generation`
   - `video_composition`

### 5. Run Test Suite

```bash
cd tests
pip install -r requirements.txt
pytest -v
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
# or
netstat -tulpn | grep 3000

# Kill the process
kill -9 <PID>
```

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs backend
docker-compose logs postgres

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# Check connection string in .env
cat .env | grep DATABASE_URL
```

### Frontend Can't Connect to Backend

1. Check CORS settings in `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

2. Verify backend is accessible:
   ```bash
   curl http://localhost:8000/health
   ```

### Worker Not Processing Tasks

```bash
# Check RabbitMQ connection
docker-compose logs ai_worker | grep -i "error\|failed"

# Verify queues exist
# Visit http://localhost:15672 and check Queues tab

# Restart workers
docker-compose restart ai_worker composition_worker
```

### Out of Memory

```bash
# Check Docker memory allocation
docker stats

# Increase Docker memory in Docker Desktop:
# Settings > Resources > Memory (allocate 8GB+)

# Reduce worker count
docker-compose up -d --scale ai_worker=1
```

## Production Deployment

For production deployment, additional steps are required:

### 1. Security

- [ ] Generate strong `SECRET_KEY`
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up VPC/network isolation
- [ ] Use secrets management (AWS Secrets Manager, etc.)

### 2. Scaling

- [ ] Use managed database (AWS RDS, etc.)
- [ ] Use managed Redis (ElastiCache, etc.)
- [ ] Use managed message queue (Amazon MQ, CloudAMQP)
- [ ] Use container orchestration (Kubernetes, ECS)
- [ ] Set up auto-scaling for workers
- [ ] Configure load balancer

### 3. Monitoring

- [ ] Set up logging aggregation (ELK, CloudWatch)
- [ ] Configure metrics (Prometheus, Grafana)
- [ ] Set up alerts (PagerDuty, etc.)
- [ ] Enable health checks
- [ ] Configure uptime monitoring

### 4. Backups

- [ ] Automated database backups
- [ ] S3 bucket versioning
- [ ] Disaster recovery plan

## Getting Help

- **Documentation**: See `README.md` and `VIDEO_FOUNDRY_README.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Docker Testing Guide**: See `DOCKER_TESTING_GUIDE.md`
- **Test Results**: See `TEST_RESULTS.md`

## Quick Reference

```bash
# Start everything
./launch.sh

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Scale workers
docker-compose up -d --scale ai_worker=4

# Access database
docker-compose exec postgres psql -U postgres videofoundry

# Run tests
cd tests && pytest -v

# Check status
docker-compose ps
```

---

**Ready to launch?** Run `./launch.sh` and start building amazing AI-powered videos! 🎬✨
