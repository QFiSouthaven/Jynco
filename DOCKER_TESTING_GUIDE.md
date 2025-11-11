# Video Foundry - Docker Setup Testing Guide

## Prerequisites Checklist

Before testing, ensure you have:
- [ ] Docker Desktop installed (or Docker Engine + Docker Compose)
- [ ] At least 8GB RAM allocated to Docker
- [ ] Ports available: 3000, 5432, 5672, 6379, 8000, 15672
- [ ] Git repository cloned locally

## Quick Start Testing

### 1. Initial Setup

```bash
# Navigate to the project directory
cd Jynco

# Verify .env file exists and configure it
cp .env.example .env

# Edit .env with your actual credentials (optional for testing)
# For testing with mock AI, you don't need real API keys
nano .env
```

### 2. Minimal .env for Testing (Mock Mode)

```bash
# Database (defaults work fine)
DATABASE_URL=postgresql://postgres:password@postgres:5432/videofoundry

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# S3 - Use LocalStack or mock (not needed for basic testing)
S3_BUCKET=video-foundry-dev
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1

# AI APIs - Not needed for mock mode
RUNWAY_API_KEY=not_needed_for_mock
STABILITY_API_KEY=not_needed_for_mock

# Application
SECRET_KEY=test-secret-key-for-development
ENVIRONMENT=development
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 4. Monitor Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ai_worker
docker-compose logs -f frontend
```

## Service Health Checks

### Check Running Containers

```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
vf_backend              Up (healthy)        0.0.0.0:8000->8000/tcp
vf_frontend             Up                  0.0.0.0:3000->3000/tcp
vf_postgres             Up (healthy)        0.0.0.0:5432->5432/tcp
vf_redis                Up (healthy)        0.0.0.0:6379->6379/tcp
vf_rabbitmq             Up (healthy)        0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
vf_ai_worker            Up
vf_composition_worker   Up
```

### Test Each Service

#### 1. PostgreSQL Database

```bash
# Connect to database
docker exec -it vf_postgres psql -U postgres -d videofoundry

# Inside psql, check tables
\dt

# Exit
\q
```

#### 2. Redis Cache

```bash
# Test Redis
docker exec -it vf_redis redis-cli ping
# Should return: PONG
```

#### 3. RabbitMQ

```bash
# Check RabbitMQ status
docker exec -it vf_rabbitmq rabbitmq-diagnostics status

# Access Management UI
# Open: http://localhost:15672
# Login: guest / guest
```

#### 4. Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Access API documentation
# Open: http://localhost:8000/docs
```

#### 5. Frontend

```bash
# Access frontend
# Open: http://localhost:3000
```

## Testing the Complete Workflow

### Test 1: Create a Project

```bash
# Create a test project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing Video Foundry"
  }'

# Note the returned project ID
```

### Test 2: Add Segments

```bash
# Replace {project_id} with actual ID from previous step
curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
  -H "Content-Type: application/json" \
  -d '{
    "order_index": 0,
    "prompt": "A beautiful sunrise over mountains",
    "model_params": {
      "model": "mock-ai",
      "duration": 5,
      "aspect_ratio": "16:9"
    }
  }'
```

### Test 3: Start Render

```bash
# Start rendering
curl -X POST http://localhost:8000/api/projects/{project_id}/render

# Note the returned render_job_id
```

### Test 4: Monitor Progress

```bash
# Check render job status
curl http://localhost:8000/api/render-jobs/{render_job_id}

# Watch worker logs
docker-compose logs -f ai_worker
```

## Testing with Frontend UI

1. Open browser: http://localhost:3000
2. Click "New Project"
3. Name your project and click "Create"
4. Click "Add Segment"
5. Enter a prompt like "Birds flying over ocean"
6. Click "Add Segment"
7. Click "Render Video"
8. Navigate to "Dashboard" to see progress

## Running E2E Tests

```bash
# Install test dependencies
cd tests
pip install -r requirements.txt

# Run tests (ensure services are running)
pytest -v

# Run specific test
pytest tests/e2e/test_timeline_workflow.py -v -s
```

## Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # or :3000, :5432, etc.

# Kill the process or change ports in docker-compose.yml
```

### Issue: Services Won't Start

```bash
# Clean everything and restart
docker-compose down -v
docker-compose up --build
```

### Issue: Database Connection Errors

```bash
# Check if postgres is healthy
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Issue: Worker Not Processing Tasks

```bash
# Check RabbitMQ queues
# Open: http://localhost:15672
# Navigate to "Queues" tab
# Check "segment_generation" queue

# Check worker logs
docker-compose logs ai_worker
```

### Issue: Frontend Can't Connect to Backend

```bash
# Check VITE_API_URL in docker-compose.yml
# Should be: http://localhost:8000

# Restart frontend
docker-compose restart frontend
```

## Performance Testing

### Load Test with Multiple Segments

```bash
# Python script to create multiple segments
python - << 'EOF'
import requests
import json

API_URL = "http://localhost:8000"

# Create project
resp = requests.post(f"{API_URL}/api/projects/", json={
    "name": "Load Test Project",
    "description": "Testing with 10 segments"
})
project = resp.json()
project_id = project["id"]
print(f"Created project: {project_id}")

# Add 10 segments
for i in range(10):
    requests.post(
        f"{API_URL}/api/projects/{project_id}/segments",
        json={
            "order_index": i,
            "prompt": f"Test segment {i}",
            "model_params": {"model": "mock-ai", "duration": 5}
        }
    )
    print(f"Added segment {i}")

# Start render
resp = requests.post(f"{API_URL}/api/projects/{project_id}/render")
render_job = resp.json()
print(f"Started render job: {render_job['id']}")
EOF
```

## Scaling Workers

```bash
# Scale AI workers to 5 instances
docker-compose up -d --scale ai_worker=5

# Check running workers
docker-compose ps ai_worker
```

## Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Monitoring

### View Resource Usage

```bash
# Docker stats
docker stats

# Specific services
docker stats vf_backend vf_ai_worker vf_postgres
```

### Database Queries

```bash
# Check projects
docker exec -it vf_postgres psql -U postgres -d videofoundry -c "SELECT * FROM projects;"

# Check segments
docker exec -it vf_postgres psql -U postgres -d videofoundry -c "SELECT id, status, prompt FROM segments;"

# Check render jobs
docker exec -it vf_postgres psql -U postgres -d videofoundry -c "SELECT id, status, segments_total, segments_completed FROM render_jobs;"
```

## Success Criteria

✅ All containers start successfully
✅ Health checks pass for postgres, redis, rabbitmq
✅ Backend API accessible at http://localhost:8000
✅ Frontend accessible at http://localhost:3000
✅ Can create projects via API
✅ Can add segments via API
✅ Can start render jobs
✅ Workers process segment tasks
✅ Mock AI adapter generates videos
✅ Real-time progress updates work

## Next Steps After Testing

1. Configure real AI API keys (Runway, Stability)
2. Set up AWS S3 for production storage
3. Configure SSL/TLS for production
4. Set up monitoring (Prometheus/Grafana)
5. Configure backups
6. Deploy to production environment

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify .env configuration
3. Ensure all ports are available
4. Check Docker has enough resources
5. Review error messages in backend/worker logs
