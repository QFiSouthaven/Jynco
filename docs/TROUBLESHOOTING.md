# Troubleshooting Guide - Video Foundry

This guide helps you diagnose and fix common issues with Video Foundry.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Service Issues](#service-issues)
- [ComfyUI Issues](#comfyui-issues)
- [Database Issues](#database-issues)
- [Storage Issues](#storage-issues)
- [Worker Issues](#worker-issues)
- [Video Generation Issues](#video-generation-issues)
- [Performance Issues](#performance-issues)
- [Error Code Reference](#error-code-reference)
- [FAQ](#faq)

## Quick Diagnostics

### Health Check Commands

Run these commands to check system health:

```bash
# Check all services status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check ComfyUI health
curl http://localhost:8188/system_stats

# Check database connection
docker-compose exec postgres pg_isready

# Check Redis connection
docker-compose exec redis redis-cli ping

# Check RabbitMQ connection
docker-compose exec rabbitmq rabbitmq-diagnostics ping
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai_worker
docker-compose logs -f comfyui
docker-compose logs -f composition_worker

# Last 100 lines
docker-compose logs --tail=100 backend

# Logs since 10 minutes ago
docker-compose logs --since=10m backend
```

### Quick Fix

Many issues can be resolved by restarting services:

```bash
# Restart specific service
docker-compose restart backend
docker-compose restart comfyui

# Restart all services
docker-compose restart

# Nuclear option: rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Service Issues

### Backend Not Starting

**Symptoms:**
- Cannot access http://localhost:8000
- Backend container exits immediately
- Health check fails

**Diagnosis:**
```bash
# Check if container is running
docker-compose ps backend

# View logs
docker-compose logs backend

# Check ports
netstat -tulpn | grep 8000
```

**Common Causes:**

**1. Port Already in Use**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or change port
# Edit docker-compose.yml:
backend:
  ports:
    - "8001:8000"  # Change host port
```

**2. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test database connection
docker-compose exec backend python -c "
from sqlalchemy import create_engine
from config.settings import get_settings
settings = get_settings()
engine = create_engine(settings.database_url)
conn = engine.connect()
print('Database connection successful!')
"
```

**3. Missing Environment Variables**
```bash
# Check .env file exists
ls -la .env

# Verify required variables are set
docker-compose exec backend env | grep DATABASE_URL
docker-compose exec backend env | grep REDIS_URL
```

**Fix:**
```bash
# Ensure .env file is configured
cp .env.example .env
# Edit .env with correct values

# Restart backend
docker-compose restart backend
```

### Frontend Not Starting

**Symptoms:**
- Cannot access http://localhost:5173
- White screen or loading forever
- Build errors in logs

**Diagnosis:**
```bash
# Check container status
docker-compose ps frontend

# View logs
docker-compose logs frontend

# Check for JavaScript errors
# Open browser console (F12) when accessing frontend
```

**Common Causes:**

**1. Node Modules Not Installed**
```bash
# Check logs for npm errors
docker-compose logs frontend | grep -i error

# Fix: Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

**2. API Connection Failed**
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Check CORS settings in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**3. Port Conflict**
```bash
# Change frontend port
# Edit docker-compose.yml:
frontend:
  ports:
    - "5174:3000"  # Use different host port
```

### RabbitMQ Not Starting

**Symptoms:**
- Workers can't connect
- "Connection refused" errors in worker logs
- Management UI not accessible

**Diagnosis:**
```bash
# Check RabbitMQ status
docker-compose ps rabbitmq

# View logs
docker-compose logs rabbitmq

# Test connection
docker-compose exec rabbitmq rabbitmqctl status
```

**Fix:**
```bash
# Restart RabbitMQ
docker-compose restart rabbitmq

# If persistent issues, reset data
docker-compose down -v
docker-compose up -d
```

## ComfyUI Issues

### ComfyUI Not Starting

**Symptoms:**
- Cannot access http://localhost:8188
- ComfyUI container exits
- Workers report "Cannot connect to ComfyUI"

**Diagnosis:**
```bash
# Check container status
docker-compose ps comfyui

# View logs
docker-compose logs comfyui

# Check GPU access (if using GPU)
docker-compose exec comfyui nvidia-smi
```

**Common Causes:**

**1. GPU Not Accessible**
```bash
# Check if NVIDIA drivers are installed
nvidia-smi

# Check if docker has GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Fix: Install NVIDIA Container Toolkit
# See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

**2. Out of Memory**
```bash
# Check system memory
free -h

# Check docker memory limits
docker stats comfyui

# Fix: Reduce memory usage
# Edit docker-compose.yml:
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --lowvram
```

**3. Port Conflict**
```bash
# Check if port 8188 is in use
lsof -i :8188

# Change port in docker-compose.yml:
comfyui:
  ports:
    - "8189:8188"
```

### Missing ComfyUI Models

**Symptoms:**
- "Model not found" error
- Workflow fails to load
- Generation fails immediately

**Diagnosis:**
```bash
# List installed models
docker-compose exec comfyui ls -la /home/runner/models/checkpoints/

# Check specific model
docker-compose exec comfyui ls -la /home/runner/models/checkpoints/sd_xl_base_1.0.safetensors
```

**Fix:**
```bash
# Download required model
docker-compose exec comfyui bash
cd /home/runner/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
exit

# Or mount local models directory
# Edit docker-compose.yml:
comfyui:
  volumes:
    - /path/to/your/models:/home/runner/models
```

### Missing Custom Nodes

**Symptoms:**
- "Node 'AnimateDiffLoader' not found"
- Workflow loads but fails to execute
- Missing node errors in logs

**Diagnosis:**
```bash
# List installed custom nodes
docker-compose exec comfyui ls -la /home/runner/ComfyUI/custom_nodes/

# Check specific node
docker-compose exec comfyui ls -la /home/runner/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved
```

**Fix:**
```bash
# Install missing custom node
docker-compose exec comfyui bash
cd /home/runner/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt
exit

# Restart ComfyUI
docker-compose restart comfyui
```

### ComfyUI Generation Slow

**Symptoms:**
- Generation takes hours
- CPU at 100% but GPU idle
- System becomes unresponsive

**Diagnosis:**
```bash
# Check GPU usage
docker-compose exec comfyui nvidia-smi

# Check if GPU is being used
docker-compose logs comfyui | grep -i "device"
```

**Solutions:**

**1. Enable GPU**
```yaml
# Uncomment in docker-compose.yml:
comfyui:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**2. Optimize Settings**
```yaml
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --highvram --fp16-vae
```

**3. Reduce Generation Load**
- Lower resolution (512x512)
- Fewer steps (15-20)
- Fewer frames (8-12)

## Database Issues

### Cannot Connect to Database

**Symptoms:**
- Backend fails to start
- "Connection refused" errors
- Database migration fails

**Diagnosis:**
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -d videofoundry -c "SELECT 1;"

# Check logs
docker-compose logs postgres
```

**Fix:**
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Wait for it to be healthy
docker-compose ps postgres

# If still failing, check DATABASE_URL
echo $DATABASE_URL
# Should be: postgresql://postgres:password@postgres:5432/videofoundry
```

### Database Schema Outdated

**Symptoms:**
- "relation does not exist" errors
- "column does not exist" errors
- API returns 500 errors

**Diagnosis:**
```bash
# Check current migration state
docker-compose exec backend alembic current

# Check pending migrations
docker-compose exec backend alembic heads
```

**Fix:**
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# If errors persist, check migration files
docker-compose exec backend ls -la /app/alembic/versions/
```

### Database Corruption

**Symptoms:**
- Random crashes
- Inconsistent data
- "invalid page header" errors

**Diagnosis:**
```bash
# Check database integrity
docker-compose exec postgres psql -U postgres -d videofoundry -c "VACUUM FULL ANALYZE;"
```

**Fix (Nuclear Option):**
```bash
# Backup data first!
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# Reset database
docker-compose down -v
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
sleep 10

# Restore backup
docker-compose exec -T postgres psql -U postgres -d videofoundry < backup.sql

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Storage Issues

### S3 Upload Failed

**Symptoms:**
- Segments generate but don't show in UI
- "Failed to upload to S3" errors
- Video URLs not accessible

**Diagnosis:**
```bash
# Check S3 credentials
docker-compose exec backend env | grep AWS

# Test S3 access
docker-compose exec backend python -c "
import boto3
from config.settings import get_settings
settings = get_settings()
s3 = boto3.client('s3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)
print(s3.list_buckets())
"
```

**Solutions:**

**1. Use Local Storage**
```bash
# Remove S3 credentials from .env
# Comment out or remove:
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# Restart backend
docker-compose restart backend
```

**2. Fix S3 Credentials**
```bash
# Verify credentials are correct
aws s3 ls s3://your-bucket-name

# Update .env with correct values
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name

# Restart services
docker-compose restart backend ai_worker composition_worker
```

**3. Check S3 Bucket Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Local Storage Full

**Symptoms:**
- "No space left on device" errors
- Docker volumes full
- Generation fails with disk errors

**Diagnosis:**
```bash
# Check disk space
df -h

# Check Docker disk usage
docker system df

# Check specific volume
docker volume inspect jynco_local_videos
```

**Fix:**
```bash
# Clean up old videos
docker-compose exec backend rm -rf /videos/old-*

# Prune Docker system
docker system prune -a

# Increase disk space or add external volume
# Edit docker-compose.yml:
backend:
  volumes:
    - /mnt/external-drive/videos:/videos
```

## Worker Issues

### Workers Not Processing Tasks

**Symptoms:**
- Segments stay in "pending" state
- No activity in worker logs
- RabbitMQ queue has messages but they're not consumed

**Diagnosis:**
```bash
# Check worker status
docker-compose ps ai_worker composition_worker

# Check RabbitMQ queues
# Open http://localhost:15672
# Login: guest/guest
# Check "Queues" tab - should show messages being consumed

# Check worker logs
docker-compose logs ai_worker
docker-compose logs composition_worker
```

**Common Causes:**

**1. Workers Not Running**
```bash
# Restart workers
docker-compose restart ai_worker composition_worker

# Check if they stay running
docker-compose ps
```

**2. Queue Name Mismatch**
```bash
# Check queue names in .env
SEGMENT_QUEUE_NAME=segment_generation
COMPOSITION_QUEUE_NAME=video_composition

# Verify workers are using same names
docker-compose logs ai_worker | grep -i "queue"
```

**3. Workers Crashing**
```bash
# Check for errors in logs
docker-compose logs ai_worker | grep -i error

# Common issues:
# - Import errors: Rebuild worker image
# - Memory errors: Increase Docker memory limit
# - Connection errors: Check RabbitMQ connection
```

**Fix:**
```bash
# Rebuild and restart workers
docker-compose build ai_worker composition_worker
docker-compose up -d ai_worker composition_worker

# Scale workers for more capacity
docker-compose up -d --scale ai_worker=4
```

### Worker Memory Issues

**Symptoms:**
- Workers crash during generation
- "Killed" messages in logs
- OOM (Out of Memory) errors

**Diagnosis:**
```bash
# Monitor memory usage
docker stats

# Check logs for OOM
docker-compose logs ai_worker | grep -i "killed\|memory"
```

**Fix:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory: 8GB+

# Reduce generation parameters
# Use lower resolution, fewer frames

# Enable swap memory
# Edit docker-compose.yml:
ai_worker:
  mem_swappiness: 60
```

## Video Generation Issues

### Segment Generation Fails

**Symptoms:**
- Segment status shows "failed"
- Error message in UI
- Worker logs show exceptions

**Diagnosis:**
```bash
# Check segment error in database
docker-compose exec postgres psql -U postgres -d videofoundry -c "
  SELECT id, status, error_message, error_code
  FROM segments
  WHERE status = 'failed'
  ORDER BY updated_at DESC
  LIMIT 5;
"

# Check worker logs at time of failure
docker-compose logs --tail=100 ai_worker
```

**Common Error Codes:**

| Code | Meaning | Solution |
|------|---------|----------|
| COMFYUI_CONNECTION_ERROR | Can't connect to ComfyUI | Check ComfyUI is running |
| COMFYUI_TIMEOUT_ERROR | Generation timeout | Increase timeout or reduce complexity |
| COMFYUI_WORKFLOW_ERROR | Invalid workflow | Verify workflow JSON |
| COMFYUI_MISSING_NODE_ERROR | Custom node missing | Install required custom nodes |
| COMFYUI_OUTPUT_ERROR | No output produced | Check workflow produces video |
| RUNWAY_API_ERROR | Runway API failed | Check API key and credits |
| STABILITY_API_ERROR | Stability API failed | Check API key and credits |

**Generic Fixes:**

**1. Retry Segment**
```bash
# Via API
curl -X POST http://localhost:8000/api/segments/{segment_id}/retry

# Via UI: Click segment → "Retry" button
```

**2. Check Model/API Keys**
```bash
# Verify API keys are set
docker-compose exec backend env | grep API_KEY

# Test API connection
curl -H "Authorization: Bearer ${RUNWAY_API_KEY}" \
  https://api.runwayml.com/v1/models
```

**3. Simplify Prompt**
```bash
# Try with simple prompt first
curl -X PUT http://localhost:8000/api/segments/{segment_id} \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A simple test prompt"}'
```

### Video Composition Fails

**Symptoms:**
- All segments complete but no final video
- Composition worker shows errors
- Render job stuck in "composing" state

**Diagnosis:**
```bash
# Check composition worker logs
docker-compose logs composition_worker | grep -i error

# Check render job status
curl http://localhost:8000/api/render-jobs/{render_job_id}

# Verify all segments are completed
curl http://localhost:8000/api/projects/{project_id}/segments
```

**Common Causes:**

**1. Missing Segment Videos**
```bash
# Check if all segment videos exist
docker-compose exec backend ls -la /videos/segment-*

# Re-render missing segments
curl -X POST http://localhost:8000/api/segments/{segment_id}/retry
```

**2. FFMPEG Error**
```bash
# Check FFMPEG is installed
docker-compose exec composition_worker ffmpeg -version

# Test FFMPEG manually
docker-compose exec composition_worker ffmpeg -i /videos/segment-1.mp4 -i /videos/segment-2.mp4 -filter_complex concat=n=2:v=1:a=0 -an /tmp/test.mp4
```

**3. Incompatible Video Formats**
```bash
# Check video properties
docker-compose exec composition_worker ffprobe /videos/segment-1.mp4

# Segments must have same:
# - Resolution
# - Frame rate
# - Codec
```

**Fix:**
```bash
# Restart composition worker
docker-compose restart composition_worker

# If persistent, regenerate segments with consistent parameters
```

### Poor Quality Results

**Symptoms:**
- Video is blurry or low quality
- Artifacts and glitches
- Doesn't match prompt

**Solutions:**

**1. Increase Quality Parameters**
```json
{
  "steps": 30,         // More steps = better quality
  "cfg": 8.0,          // Higher CFG = stronger prompt following
  "width": 1024,       // Higher resolution
  "height": 576
}
```

**2. Improve Prompt**
```
Bad:  "beach"
Good: "A pristine tropical beach at golden hour, crystal clear turquoise water, gentle waves, cinematic lighting, 4k quality, photorealistic"
```

**3. Use Better Model**
- Switch from ComfyUI to Runway Gen-3 for higher quality
- Use appropriate workflow (text-to-video vs image-to-video)

**4. Try Different Seeds**
```bash
# Generate multiple variations
for seed in 42 123 456 789; do
  # Create segment with different seed
  curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"...\", \"model_params\": {\"seed\": $seed}}"
done
```

## Performance Issues

### Slow UI Loading

**Symptoms:**
- Frontend takes long to load
- Laggy interface
- Slow API responses

**Diagnosis:**
```bash
# Check API response time
time curl http://localhost:8000/api/projects

# Check database query performance
docker-compose exec postgres psql -U postgres -d videofoundry -c "
  EXPLAIN ANALYZE SELECT * FROM projects ORDER BY created_at DESC LIMIT 10;
"

# Check Redis performance
docker-compose exec redis redis-cli --latency
```

**Solutions:**

**1. Add Database Indexes**
```sql
-- Connect to database
docker-compose exec postgres psql -U postgres -d videofoundry

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_segments_project_id ON segments(project_id);
CREATE INDEX IF NOT EXISTS idx_segments_status ON segments(status);
CREATE INDEX IF NOT EXISTS idx_render_jobs_project_id ON render_jobs(project_id);

-- Analyze tables
ANALYZE projects;
ANALYZE segments;
ANALYZE render_jobs;
```

**2. Enable Redis Caching**
```python
# Add to backend/api/projects.py
from services import redis_client

@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    # Check cache
    cached = redis_client.get("projects_list")
    if cached:
        return json.loads(cached)

    # Query database
    projects = db.query(Project).all()

    # Cache result
    redis_client.set("projects_list", json.dumps(projects), ex=60)

    return projects
```

**3. Optimize Frontend**
```bash
# Build production frontend
cd frontend
npm run build

# Serve built files with NGINX
```

### High Resource Usage

**Symptoms:**
- System becomes slow
- High CPU/RAM usage
- Docker using too much disk space

**Diagnosis:**
```bash
# Check Docker resource usage
docker stats

# Check disk usage
docker system df

# Check system resources
htop  # or: top
```

**Solutions:**

**1. Limit Docker Resources**
```yaml
# Edit docker-compose.yml
services:
  backend:
    mem_limit: 2g
    cpus: 2

  comfyui:
    mem_limit: 8g
    cpus: 4
```

**2. Clean Up Docker**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

**3. Reduce Worker Count**
```bash
# Scale down workers
docker-compose up -d --scale ai_worker=1
```

## Error Code Reference

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid JSON, missing required fields |
| 404 | Not Found | Project/segment/render job doesn't exist |
| 500 | Internal Server Error | Unhandled exception, check logs |
| 503 | Service Unavailable | Service starting up or overloaded |

### Application Error Codes

| Code | Component | Meaning | Solution |
|------|-----------|---------|----------|
| COMFYUI_CONNECTION_ERROR | AI Worker | Cannot connect to ComfyUI | Check ComfyUI is running |
| COMFYUI_TIMEOUT_ERROR | AI Worker | Request timed out | Increase timeout or simplify generation |
| COMFYUI_WORKFLOW_ERROR | AI Worker | Invalid workflow JSON | Verify workflow structure |
| COMFYUI_MISSING_NODE_ERROR | AI Worker | Required node not installed | Install custom nodes |
| COMFYUI_INVALID_PARAMETERS_ERROR | AI Worker | Invalid parameters | Check parameter values |
| COMFYUI_GENERATION_ERROR | AI Worker | Generation failed | Check ComfyUI logs |
| COMFYUI_OUTPUT_ERROR | AI Worker | No output produced | Verify workflow produces video |
| RABBITMQ_CONNECTION_ERROR | Worker | Cannot connect to RabbitMQ | Check RabbitMQ is running |
| REDIS_CONNECTION_ERROR | Backend | Cannot connect to Redis | Check Redis is running |
| DATABASE_CONNECTION_ERROR | Backend | Cannot connect to database | Check PostgreSQL is running |
| S3_UPLOAD_ERROR | Worker | Failed to upload to S3 | Check S3 credentials |
| FFMPEG_ERROR | Composition | FFMPEG command failed | Check FFMPEG logs |

## FAQ

### General Questions

**Q: How do I reset everything?**
```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d --build
```

**Q: How do I backup my data?**
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres videofoundry > backup.sql

# Backup videos
docker cp vf_backend:/videos ./videos_backup/

# Backup .env
cp .env .env.backup
```

**Q: How do I update Video Foundry?**
```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

**Q: Can I run without Docker?**

Yes, but it's more complex. See [Setup Guide](SETUP.md) for local development instructions.

**Q: How much does it cost to run?**

- ComfyUI: Free (local hardware)
- Runway Gen-3: ~$0.05-0.10 per second
- Stability AI: ~$0.04-0.08 per generation
- Infrastructure: Docker hosting costs (varies)

**Q: Can I use my own AI models?**

Yes! Create custom ComfyUI workflows with any compatible model. See [ComfyUI Integration](COMFYUI_INTEGRATION.md).

**Q: Is GPU required?**

No, but highly recommended for ComfyUI. Cloud APIs (Runway, Stability) don't require local GPU.

**Q: How long does generation take?**

- ComfyUI (GPU): 30 seconds to 5 minutes
- ComfyUI (CPU): 10-30 minutes or more
- Runway Gen-3: 1-3 minutes
- Stability AI: 1-2 minutes

**Q: What video formats are supported?**

- Input: Most common formats (MP4, MOV, AVI, etc.)
- Output: MP4 (H.264)

**Q: Can I add audio to videos?**

Not currently. Export videos and add audio in external video editor.

**Q: How do I get support?**

- Check this troubleshooting guide
- Search GitHub issues
- Open a new issue with logs and error messages
- Join community discussions

## Still Having Issues?

If you're still experiencing problems:

1. **Collect Information:**
   ```bash
   # Get all logs
   docker-compose logs > logs.txt

   # Get system info
   docker version > system-info.txt
   docker-compose version >> system-info.txt
   uname -a >> system-info.txt
   ```

2. **Check GitHub Issues:**
   - Search existing issues: https://github.com/QFiSouthaven/Jynco/issues
   - Check closed issues for solutions

3. **Open a New Issue:**
   - Describe the problem clearly
   - Include error messages
   - Attach logs (logs.txt)
   - Mention your environment (OS, Docker version, etc.)

4. **Community Support:**
   - GitHub Discussions
   - Discord server (if available)

---

**Remember: Most issues can be solved by checking logs and restarting services!**
