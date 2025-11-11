# ⚡ Jynco Video Foundry - Quick Start Guide

Get up and running with Jynco Video Foundry in 5 minutes!

## Prerequisites

Before you begin, ensure you have:

- ✅ **Docker** installed (version 20.10+)
- ✅ **Docker Compose** installed (version 2.0+)
- ✅ At least **8GB RAM** allocated to Docker
- ✅ **10GB free disk space**

Check your Docker installation:
```bash
docker --version
docker-compose --version
```

## 🚀 Launch in 3 Steps

### Step 1: Get API Keys (15 minutes)

You'll need accounts and API keys from:

1. **AWS** (Required for video storage)
   - Sign up: https://aws.amazon.com/
   - Get Access Key: https://console.aws.amazon.com/iam/
   - Create S3 bucket: https://s3.console.aws.amazon.com/

2. **Runway ML** (Required for AI video generation)
   - Sign up: https://runwayml.com/
   - Get API key: https://app.runwayml.com/settings/api
   - Add credits ($10+ recommended)

3. **Stability AI** (Optional but recommended)
   - Sign up: https://platform.stability.ai/
   - Get API key: https://platform.stability.ai/account/keys
   - Add credits ($10+ recommended)

**Need help?** See [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md) for detailed instructions.

### Step 2: Configure (5 minutes)

Run the interactive configuration wizard:

```bash
cd /home/user/Jynco
./configure_keys.sh
```

The wizard will guide you through:
- ✅ AWS credentials
- ✅ Runway API key
- ✅ Stability AI key
- ✅ Secret key generation
- ✅ Database password (optional)

**Or configure manually:**
```bash
cp .env.example .env
nano .env  # Edit with your keys
```

### Step 3: Launch (2 minutes)

Start all services:

```bash
./launch.sh
```

That's it! 🎉

## 🌐 Access Your Application

Once launched, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application UI |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **RabbitMQ** | http://localhost:15672 | Message queue admin (guest/guest) |

## ✅ Verify Installation

### 1. Check All Services Running

```bash
docker-compose ps
```

All services should show "Up" status.

### 2. Validate API Keys

```bash
./validate_keys.py
```

This verifies:
- ✅ AWS credentials work
- ✅ S3 bucket is accessible
- ✅ Runway API key is valid
- ✅ Stability AI key is valid
- ✅ Secret key is secure

### 3. Create Test Account

1. Open http://localhost:3000
2. Click "Sign Up"
3. Create your account
4. Explore the interface!

## 📖 Basic Usage

### Creating Your First Video Project

1. **Log in** to the frontend (http://localhost:3000)

2. **Create a new project**
   - Click "New Project"
   - Enter project name
   - Click "Create"

3. **Add video segments**
   - Click "Add Segment"
   - Enter text prompt: "A serene ocean wave at sunset"
   - Set duration: 5 seconds
   - Select model: "Runway Gen-3 Turbo"
   - Click "Generate"

4. **Monitor progress**
   - Watch real-time progress in the UI
   - WebSocket updates show generation status

5. **Preview and export**
   - Once complete, click "Preview"
   - Click "Export" to download

### Video Timeline Editor

The timeline editor allows you to:
- ✨ Create multi-segment video projects
- 🎬 Arrange segments in sequence
- ⚡ Regenerate individual segments
- 🎨 Preview before final render
- 💾 Export to MP4

## 🛠️ Common Operations

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
# Stop (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and delete everything (CAUTION)
docker-compose down -v
```

### Scale Workers

```bash
# Scale to 4 AI workers
docker-compose up -d --scale ai_worker=4

# Scale back to 2
docker-compose up -d --scale ai_worker=2
```

## 💰 Cost Management

### Estimate Your Costs

**Per Video Segment (5 seconds):**
- Runway Gen-3 Turbo: $0.25 (5 seconds × $0.05/sec)
- S3 Storage: ~$0.001 per video
- S3 Transfer: ~$0.01 per video

**Example Monthly Costs:**

| Usage Level | Videos/Month | Runway Cost | S3 Cost | Total |
|-------------|--------------|-------------|---------|-------|
| **Light** | 50 segments | $12.50 | $1.00 | **$13.50** |
| **Medium** | 200 segments | $50.00 | $3.00 | **$53.00** |
| **Heavy** | 1000 segments | $250.00 | $12.00 | **$262.00** |

### Monitor Costs

1. **Runway**: https://app.runwayml.com/billing
2. **Stability AI**: https://platform.stability.ai/account/billing
3. **AWS**: https://console.aws.amazon.com/billing/

### Set Budget Alerts

In AWS Console:
1. Go to AWS Budgets
2. Create budget
3. Set threshold (e.g., $50/month)
4. Add email alerts

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

### Services Not Starting

```bash
# Check logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### API Key Not Working

```bash
# Validate your keys
./validate_keys.py

# Check for typos in .env
cat .env | grep -E "(RUNWAY|STABILITY|AWS)"

# Restart services after updating .env
docker-compose restart
```

### Worker Not Processing

```bash
# Check worker logs
docker-compose logs ai_worker

# Verify RabbitMQ is running
curl http://localhost:15672

# Restart workers
docker-compose restart ai_worker composition_worker
```

## 📚 Next Steps

### Learn More

- **Full Documentation**: [README.md](./README.md)
- **Video Foundry Details**: [VIDEO_FOUNDRY_README.md](./VIDEO_FOUNDRY_README.md)
- **Launch Guide**: [LAUNCH_GUIDE.md](./LAUNCH_GUIDE.md)
- **API Keys Guide**: [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)
- **Security**: [SECURITY_BEST_PRACTICES.md](./SECURITY_BEST_PRACTICES.md)
- **Docker Testing**: [DOCKER_TESTING_GUIDE.md](./DOCKER_TESTING_GUIDE.md)

### Explore Features

1. **Multi-segment projects**: Create videos with multiple AI-generated segments
2. **Timeline editing**: Arrange and edit segments visually
3. **Smart re-rendering**: Only regenerate modified segments
4. **Worker scaling**: Add more workers for faster processing
5. **WebSocket updates**: Real-time progress tracking

### Advanced Configuration

- Set up HTTPS with Let's Encrypt
- Configure auto-scaling
- Set up monitoring with Prometheus
- Implement automated backups
- Deploy to production (AWS, Azure, GCP)

## 🆘 Getting Help

### Documentation

All documentation is in the root directory:
```bash
ls *.md
```

### Check Status

```bash
# Service status
docker-compose ps

# System health
docker stats

# Available disk space
df -h
```

### Common Commands

```bash
# Start everything
./launch.sh

# Configure keys
./configure_keys.sh

# Validate setup
./validate_keys.py

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## ✨ Tips & Best Practices

1. **Start small**: Test with 1-2 segments before creating large projects
2. **Monitor costs**: Check your API billing regularly
3. **Use shorter videos**: Start with 3-5 second segments
4. **Scale workers**: Add more workers during heavy use
5. **Backup data**: Regular database backups are important
6. **Keep it updated**: Pull latest images regularly
7. **Read the logs**: Logs contain helpful error messages

## 🎓 Example Workflows

### Workflow 1: Single Video Clip

```bash
1. Launch platform: ./launch.sh
2. Open: http://localhost:3000
3. Create project: "My First Video"
4. Add segment: "A cat playing with a ball"
5. Generate and download
```

### Workflow 2: Multi-Segment Story

```bash
1. Create project: "Nature Documentary"
2. Add segments:
   - "A sunrise over mountains"
   - "Birds flying through the sky"
   - "A river flowing through forest"
   - "Sunset over the ocean"
3. Generate all segments
4. Preview timeline
5. Export final video
```

### Workflow 3: Iterative Refinement

```bash
1. Create project
2. Generate segment: "A dog running"
3. Preview result
4. If not satisfied, edit prompt: "A golden retriever running in slow motion"
5. Regenerate (only that segment)
6. Export when satisfied
```

## 🚀 You're Ready!

You now have everything you need to create amazing AI-generated videos with Jynco Video Foundry!

**Start creating:** http://localhost:3000

**Questions?** Check the documentation or review the logs.

**Happy video creating!** 🎬✨
