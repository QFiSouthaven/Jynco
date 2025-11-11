# Video Foundry - User Guide

## How to Generate Videos

Video Foundry allows you to create AI-generated videos by combining multiple video segments, each generated from text prompts. The system uses your local GPU for acceleration.

## Getting Started

### 1. Start the Application

Run the launch script:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

Wait for all services to start (about 30 seconds). You'll see:
- ✓ Backend API at http://localhost:8000
- ✓ Frontend UI at http://localhost:5173
- ✓ GPU verification

### 2. Open the Web Interface

Open your web browser and navigate to:
```
http://localhost:5173
```

You'll see the Video Foundry interface with three main sections:
- **My Projects** - Main page for managing projects
- **Timeline Editor** - Edit project segments
- **Dashboard** - View render progress

---

## Creating Your First Video

### Step 1: Create a New Project

1. Click the **"New Project"** button (blue button with + icon)
2. Enter a project name (e.g., "My First AI Video")
3. Optionally add a description
4. Click **"Create"**

You'll be automatically taken to the Timeline Editor for your new project.

### Step 2: Add Video Segments

A video is composed of multiple segments, each generated from a text prompt.

1. Click **"Add Segment"** button
2. Enter a detailed prompt describing the video clip you want:
   ```
   Example prompts:
   - "A beautiful sunset over the ocean with waves crashing on the beach"
   - "A futuristic city with flying cars and neon lights at night"
   - "A cat playing with a ball of yarn in slow motion"
   - "An astronaut floating in space with Earth in the background"
   ```
3. Click **"Add Segment"**
4. Repeat to add more segments (they'll play in order)

**Tips for Good Prompts:**
- Be specific and descriptive
- Include details about lighting, camera movement, and mood
- Keep prompts focused on a single scene
- Each segment is about 5 seconds by default

### Step 3: Start Rendering

1. Once you've added all your segments, click the **"Render Video"** button (green button with play icon)
2. The system will:
   - Create a render job
   - Generate each segment using AI workers with GPU acceleration
   - Compose all segments into a final video

### Step 4: Monitor Progress

1. Click **"Dashboard"** in the navigation
2. You'll see:
   - **Active Renders** - Currently processing
   - **Completed** - Successfully generated segments
   - **Failed** - Any errors (rare with mock data)
3. The dashboard auto-refreshes every 5 seconds
4. Watch as segments move from "generating" → "completed"

### Step 5: View Results

Once rendering is complete:
- Completed segments show a green checkmark
- The final composed video will be available
- Video files are stored in the local `/videos` directory

---

## Understanding the Workflow

```
1. Create Project
   ↓
2. Add Segments (with prompts)
   ↓
3. Start Render
   ↓
4. AI Workers Generate Each Segment (GPU accelerated)
   ↓
5. Composition Worker Stitches Segments Together
   ↓
6. Final Video Ready
```

---

## Using the Interface

### Projects Page (Home)

**Features:**
- View all your projects
- See segment count for each project
- Create new projects
- Delete projects (with confirmation)
- Click any project to edit

### Timeline Editor

**Features:**
- Add/remove segments
- View segment prompts and status
- Reorder segments (drag and drop - if implemented)
- Start render job
- See project details

**Segment Status Indicators:**
- **Pending** - Not yet generated
- **Generating** - AI worker processing (blue, spinning)
- **Completed** - Successfully generated (green checkmark)
- **Failed** - Error occurred (red exclamation)

### Dashboard

**Features:**
- Real-time render progress monitoring
- Stats: Active, Completed, Failed renders
- Recent activity feed
- Auto-refreshes every 5 seconds

---

## Advanced: Using the API Directly

For advanced users or API integration, you can use the REST API directly.

### API Documentation

Visit the interactive API docs:
```
http://localhost:8000/docs
```

### Example API Workflow

**1. Create a Project:**
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Project",
    "description": "Created via API"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "API Test Project",
  "description": "Created via API",
  "segments": [],
  "created_at": "2025-11-11T22:00:00Z"
}
```

**2. Add a Segment:**
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
  -H "Content-Type: application/json" \
  -d '{
    "order_index": 0,
    "prompt": "A serene mountain landscape at sunrise",
    "model_params": {
      "model": "comfyui",
      "duration": 5,
      "aspect_ratio": "16:9"
    }
  }'
```

**3. Start Rendering:**
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/render
```

**4. Check Render Status:**
```bash
curl http://localhost:8000/api/render-jobs/{render_job_id}
```

Response:
```json
{
  "id": "render-job-id",
  "status": "processing",
  "segments_total": 3,
  "segments_completed": 1,
  "created_at": "2025-11-11T22:05:00Z"
}
```

**5. Get Project with Segments:**
```bash
curl http://localhost:8000/api/projects/{project_id}
```

---

## Video Output

### Storage Location

Videos are stored locally in the Docker volume:
- Segment videos: `/videos/segments/`
- Final composed videos: `/videos/final/`

To access them from your host machine:
```bash
# List generated videos
docker exec vf_backend ls -la /videos

# Copy a video out
docker cp vf_backend:/videos/final/video.mp4 ./output.mp4
```

### Video Specifications

Default settings:
- **Format**: MP4 (H.264)
- **Resolution**: 1920x1080 (16:9)
- **Duration**: 5 seconds per segment
- **Frame Rate**: 24 fps

These can be customized in `model_params` when creating segments.

---

## Tips and Best Practices

### For Better Results

1. **Prompt Engineering**
   - Use descriptive, detailed prompts
   - Specify camera angles, lighting, mood
   - Avoid overly complex scenes in a single segment
   - Test different phrasings

2. **Segment Organization**
   - Keep related scenes together
   - Use logical transitions between segments
   - Typical videos: 3-10 segments
   - Each segment: 5-10 seconds

3. **Project Management**
   - Use descriptive project names
   - Add descriptions to track purpose
   - Delete old test projects to keep things organized

### Performance Tips

1. **GPU Utilization**
   - The system runs 2 AI workers in parallel
   - Each worker can process one segment at a time
   - Segments are processed concurrently for speed

2. **Monitoring**
   - Check GPU usage: `docker exec jynco-ai_worker-1 nvidia-smi`
   - View worker logs: `docker compose logs -f ai_worker`
   - Check backend logs: `docker compose logs -f backend`

---

## Troubleshooting

### Frontend Not Loading
```bash
# Check if frontend is running
docker compose ps frontend

# View frontend logs
docker compose logs frontend

# Restart frontend
docker compose restart frontend
```

### Render Stuck
```bash
# Check worker status
docker compose ps

# Check worker logs
docker compose logs ai_worker composition_worker

# Restart workers
docker compose restart ai_worker composition_worker
```

### API Errors
```bash
# Check backend logs
docker compose logs backend

# Check database connection
docker compose logs postgres

# Check RabbitMQ
docker compose logs rabbitmq
```

### Video Not Generating
1. Check GPU is accessible: `docker exec jynco-ai_worker-1 nvidia-smi`
2. Check worker logs for errors: `docker compose logs ai_worker`
3. Verify ComfyUI configuration in `.env.local`

---

## Keyboard Shortcuts

When using the web interface:
- **Projects page**: Click project to open
- **Timeline Editor**: Press ESC to close modals
- **Dashboard**: Auto-refreshes, no manual refresh needed

---

## Getting Help

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f ai_worker
```

### Check Service Health
```bash
# Run status script
status.bat    # Windows
./status.sh   # Linux/Mac

# Or manually
curl http://localhost:8000/health
```

### Common Issues

1. **"Backend API is not responding"**
   - Check: `docker compose ps backend`
   - Fix: `docker compose restart backend`

2. **"Segments stuck in generating"**
   - Check: `docker compose logs ai_worker`
   - Fix: `docker compose restart ai_worker`

3. **"Cannot create project"**
   - Check: `docker compose logs postgres`
   - Fix: `docker compose restart postgres backend`

---

## Next Steps

1. **Customize AI Models**: Configure ComfyUI or other AI backends in `workers/ai_worker/`
2. **Add More Workers**: Increase `replicas` in `docker-compose.yml` for more parallel processing
3. **Integrate Cloud Storage**: Enable S3 in `.env.local` for cloud storage
4. **API Integration**: Build custom tools using the REST API

---

## Resources

- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Console**: http://localhost:15672 (guest/guest)
- **Project Repository**: https://github.com/QFiSouthaven/Jynco
- **Docker Compose File**: `docker-compose.yml`
- **Environment Config**: `.env.local`

---

Enjoy creating AI-generated videos with Video Foundry! 🎬
