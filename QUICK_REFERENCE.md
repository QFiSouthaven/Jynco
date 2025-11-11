# Video Foundry - Quick Reference Card

## 🚀 Starting the System

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**Wait for:** ✓ All services healthy, ✓ GPU verified

---

## 🎬 Creating Your First Video (Web UI)

### 1. Open Browser
```
http://localhost:5173
```

### 2. Create Project
1. Click **"+ New Project"**
2. Enter name: `"My First Video"`
3. Click **"Create"**

### 3. Add Segments
1. Click **"+ Add Segment"**
2. Enter prompt:
   ```
   A beautiful sunset over the ocean with golden light
   reflecting on the water, waves crashing on the beach
   ```
3. Click **"Add Segment"**
4. Repeat for more scenes (3-5 segments recommended)

### 4. Start Render
1. Click **"▶ Render Video"** (green button)
2. Click **"Dashboard"** to monitor progress
3. Wait for all segments to show ✅ (completed)

### 5. View Results
- Segments show green checkmarks when done
- Final video composited automatically
- Videos stored in `/videos` directory

---

## 📡 API Quick Commands

### Create Project
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "API Test", "description": "Test video"}'
```

### Add Segment
```bash
curl -X POST http://localhost:8000/api/projects/{PROJECT_ID}/segments \
  -H "Content-Type: application/json" \
  -d '{
    "order_index": 0,
    "prompt": "A serene mountain landscape at sunrise",
    "model_params": {"model": "comfyui", "duration": 5}
  }'
```

### Start Render
```bash
curl -X POST http://localhost:8000/api/projects/{PROJECT_ID}/render
```

### Check Status
```bash
curl http://localhost:8000/api/render-jobs/{RENDER_JOB_ID}
```

---

## 🔍 Monitoring & Debugging

### Check Service Status
```bash
status.bat    # Windows
./status.sh   # Linux/Mac
```

### View Logs
```bash
logs.bat      # Windows
./logs.sh     # Linux/Mac
```

### Check GPU
```bash
docker exec jynco-ai_worker-1 nvidia-smi
```

### Restart Services
```bash
docker compose restart backend
docker compose restart ai_worker
docker compose restart composition_worker
```

---

## 🎯 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main web interface |
| **API Docs** | http://localhost:8000/docs | Interactive API docs |
| **Health** | http://localhost:8000/health | Backend health check |
| **RabbitMQ** | http://localhost:15672 | Message queue console |

---

## 📊 Status Indicators

| Badge | Meaning |
|-------|---------|
| 🔵 **pending** | Waiting to start |
| 🔄 **generating** | AI is processing |
| ✅ **completed** | Successfully done |
| ❌ **failed** | Error occurred |

---

## 💡 Tips for Best Results

### Good Prompts
- ✅ Detailed and specific
- ✅ Include lighting, camera angles
- ✅ Describe mood and atmosphere
- ✅ 2-3 sentences max

### Example Prompts
```
✅ "A futuristic city at night with neon lights, rain
   falling on reflective streets, flying cars above,
   cyberpunk aesthetic, cinematic wide shot"

❌ "City at night"
```

### Video Structure
```
1. Establishing shot (wide angle)
2. Detail shots (medium/close-up)
3. Transition scenes
4. Action/movement
5. Closing shot
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend not loading | `docker compose restart frontend` |
| Segments stuck | Check logs: `docker compose logs ai_worker` |
| API errors | `docker compose restart backend` |
| GPU not detected | Check: `nvidia-smi` on host |

---

## 📁 File Structure

```
Jynco/
├── start.bat / start.sh       # Launch scripts
├── stop.bat / stop.sh         # Stop scripts
├── status.bat / status.sh     # Status check
├── logs.bat / logs.sh         # View logs
├── test_workflow.py           # Test script
├── QUICKSTART.md              # Quick start guide
├── USER_GUIDE.md              # Complete user guide
├── VISUAL_WALKTHROUGH.md      # Step-by-step walkthrough
└── docker-compose.yml         # Service configuration
```

---

## ⚡ Shortcuts

### Start Everything
```bash
start.bat && curl http://localhost:5173
```

### Stop Everything
```bash
docker compose down
```

### Full Restart
```bash
docker compose down && docker compose up -d --build
```

### View All Logs
```bash
docker compose logs -f
```

### Clean Everything
```bash
docker compose down -v  # ⚠️ Deletes all data!
```

---

## 📞 Getting Help

1. **Check logs**: `logs.bat` or `./logs.sh`
2. **Check status**: `status.bat` or `./status.sh`
3. **View API docs**: http://localhost:8000/docs
4. **Read guides**: See USER_GUIDE.md
5. **Check GPU**: `docker exec jynco-ai_worker-1 nvidia-smi`

---

## 🎓 Learning Path

1. ✅ Run `start.bat` / `./start.sh`
2. ✅ Open http://localhost:5173
3. ✅ Follow VISUAL_WALKTHROUGH.md
4. ✅ Create your first 3-segment video
5. ✅ Run `python test_workflow.py`
6. ✅ Explore API at http://localhost:8000/docs
7. ✅ Read USER_GUIDE.md for advanced features

---

**Ready to create amazing AI videos! 🎬✨**
