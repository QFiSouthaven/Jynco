# Video Foundry - Visual Walkthrough

## Complete Step-by-Step Guide with Screenshots

This guide walks you through creating your first AI-generated video using the Video Foundry web interface.

---

## Prerequisites Checklist

- [ ] Docker Desktop installed and running
- [ ] NVIDIA GPU drivers installed (for GPU acceleration)
- [ ] Video Foundry services started (`start.bat` or `./start.sh`)
- [ ] Browser open to http://localhost:5173

---

## Walkthrough: Creating Your First Video

### Part 1: Starting the Application

**Step 1: Launch Services**

Open a terminal and run:
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**Expected Output:**
```
========================================
Video Foundry - Launch Script
========================================

[1/4] Checking for existing services...
[2/4] Building Docker images...
[3/4] Starting services with GPU support...
[4/4] Waiting for services to be ready...

========================================
Video Foundry is now running!
========================================

Backend API:       http://localhost:8000
API Documentation: http://localhost:8000/docs
Frontend UI:       http://localhost:5173
RabbitMQ Console:  http://localhost:15672 (guest/guest)

[SUCCESS] GPU is accessible to AI workers
```

**Step 2: Open the Web Interface**

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the **Video Foundry** interface with a dark theme.

---

### Part 2: Creating a Project

**What you'll see:**
- Page title: "My Projects"
- Blue "New Project" button in the top right
- Empty state message if no projects exist

**Step 1: Click "New Project"**

A modal dialog appears with:
- "Create New Project" title
- Project Name input field
- Description textarea (optional)
- Create and Cancel buttons

**Step 2: Fill in Project Details**

```
Project Name: "My First AI Video"
Description: "A collection of beautiful AI-generated scenes"
```

**Step 3: Click "Create"**

- The modal closes
- You're automatically redirected to the Timeline Editor
- Your new project is now in the projects list

---

### Part 3: Adding Video Segments

**What you'll see:**
- Project title: "My First AI Video"
- Green "Render Video" button (disabled until segments added)
- "Timeline" section with "Add Segment" button
- Empty state: "No segments yet. Add your first segment to get started!"

**Step 1: Click "Add Segment"**

A modal appears with:
- "Add New Segment" title
- "Video Prompt" textarea
- Add Segment and Cancel buttons

**Step 2: Enter Your First Prompt**

Example Prompt 1:
```
A beautiful sunset over the ocean with golden light reflecting on the water,
waves gently crashing on the sandy beach, seagulls flying in the distance
```

**Step 3: Click "Add Segment"**

- Modal closes
- Segment appears in the timeline
- Shows segment number, prompt preview, and status badge

**Step 4: Add More Segments**

Click "Add Segment" again and add more scenes:

Example Prompt 2:
```
A futuristic city at night with flying cars, neon signs in Japanese and English,
rain falling on reflective streets, cyberpunk aesthetic
```

Example Prompt 3:
```
A peaceful forest path with sunlight filtering through tall pine trees,
morning mist, a deer walking gracefully across the path
```

Example Prompt 4:
```
An astronaut floating in space with Earth visible below, stars twinkling,
peaceful and serene, cinematic camera movement
```

**What you'll see:**
- 4 segments displayed vertically in order
- Each shows:
  - Segment number (1, 2, 3, 4)
  - Prompt text (truncated if long)
  - Status badge: "pending" (gray)
  - Delete button (red trash icon)

---

### Part 4: Starting the Render

**Step 1: Review Your Segments**

Make sure:
- All prompts are correct
- Segments are in the desired order
- No typos in your descriptions

**Step 2: Click "Render Video"**

- Button shows "Starting..." briefly
- An alert appears: "Render started! Check the dashboard for progress."
- Segment status badges change to "generating" (blue, spinning)

---

### Part 5: Monitoring Progress

**Step 1: Navigate to Dashboard**

Click "Dashboard" in the navigation menu (top of page)

**What you'll see:**

**Top Section - Stats Cards:**
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Active Renders  │ │   Completed     │ │     Failed      │
│       4         │ │       0         │ │       0         │
│ [spinning icon] │ │ [check icon]    │ │ [warning icon]  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Bottom Section - Recent Activity:**
```
Recent Activity
───────────────────────────────────────────────────────────
[🔵] My First AI Video                    [generating]
     A beautiful sunset over the ocean...

[🔵] My First AI Video                    [generating]
     A futuristic city at night with...

[🔵] My First AI Video                    [generating]
     A peaceful forest path with...

[🔵] My First AI Video                    [generating]
     An astronaut floating in space...
```

**Step 2: Watch Progress**

- Page auto-refreshes every 5 seconds
- As segments complete:
  - Active Renders count decreases
  - Completed count increases
  - Icons change from spinning (🔵) to checkmark (✅)
  - Status badges change from "generating" to "completed"

**After All Segments Complete:**
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Active Renders  │ │   Completed     │ │     Failed      │
│       0         │ │       4         │ │       0         │
│ [spinning icon] │ │ [check icon]    │ │ [warning icon]  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Step 3: View Final Video**

Once all segments are complete, the composition worker stitches them together:
- Final video is created
- Stored in `/videos/final/` directory
- Can be accessed via API or Docker volume

---

### Part 6: Managing Projects

**Back to Projects Page**

Click "My Projects" in the navigation

**What you can do:**

1. **View All Projects**
   - See all your video projects
   - Shows segment count for each
   - Click to open timeline editor

2. **Edit Projects**
   - Click project card to open
   - Add/remove segments
   - Start new renders

3. **Delete Projects**
   - Click red trash icon
   - Confirm deletion
   - Project and segments removed

---

## Interface Overview

### Navigation Bar
```
┌────────────────────────────────────────────────────────┐
│ Video Foundry  [My Projects] [Dashboard]               │
└────────────────────────────────────────────────────────┘
```

### Projects Page Layout
```
┌────────────────────────────────────────────────────────┐
│ My Projects                        [+ New Project]     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ Project 1    │  │ Project 2    │  │ Project 3    ││
│  │ Description  │  │ Description  │  │ Description  ││
│  │ 5 segments   │  │ 3 segments   │  │ 8 segments   ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Timeline Editor Layout
```
┌────────────────────────────────────────────────────────┐
│ My First AI Video              [▶ Render Video]        │
│ A collection of beautiful AI-generated scenes          │
├────────────────────────────────────────────────────────┤
│ Timeline                                  [+ Add Segment]
├────────────────────────────────────────────────────────┤
│ 1. [pending] A beautiful sunset over the ocean...  [🗑]│
│ 2. [pending] A futuristic city at night with...   [🗑]│
│ 3. [pending] A peaceful forest path with...       [🗑]│
│ 4. [pending] An astronaut floating in space...    [🗑]│
└────────────────────────────────────────────────────────┘
```

### Dashboard Layout
```
┌────────────────────────────────────────────────────────┐
│ Render Dashboard                                       │
├────────────────────────────────────────────────────────┤
│  [Active: 4]      [Completed: 0]      [Failed: 0]     │
├────────────────────────────────────────────────────────┤
│ Recent Activity                                        │
│                                                        │
│  [🔵] My First AI Video    [generating]                │
│       A beautiful sunset over the ocean...             │
│                                                        │
│  [✅] Previous Project     [completed]                 │
│       A mountain landscape at sunrise...               │
└────────────────────────────────────────────────────────┘
```

---

## Status Indicators

### Segment Status Badges

| Badge | Color | Meaning | Icon |
|-------|-------|---------|------|
| pending | Gray | Not started | ⏸️ |
| generating | Blue | AI is processing | 🔵 (spinning) |
| completed | Green | Successfully generated | ✅ |
| failed | Red | Error occurred | ❌ |

### Render Job Status

| Status | Meaning |
|--------|---------|
| pending | Waiting to start |
| processing | Generating segments |
| compositing | Stitching segments together |
| completed | Final video ready |
| failed | Error occurred |

---

## Tips for Success

### Writing Good Prompts

**✅ Good Prompt:**
```
A serene lake at sunset with mountains in the background,
golden light reflecting on calm water, a small boat gently
drifting, cinematic wide angle shot
```

**❌ Poor Prompt:**
```
Lake
```

**Why:**
- Good prompts are specific and descriptive
- Include details about lighting, camera angle, mood
- Give the AI clear direction

### Organizing Segments

**Example Video Structure:**
```
1. Opening shot (landscape, wide)
2. Transition scene (medium shot)
3. Detail shot (close-up)
4. Action scene (movement)
5. Closing shot (fade out)
```

### Monitoring Performance

**Check GPU Usage:**
```bash
docker exec jynco-ai_worker-1 nvidia-smi
```

**Check Logs:**
```bash
# All services
docker compose logs -f

# Just workers
docker compose logs -f ai_worker composition_worker
```

---

## Troubleshooting Visual Issues

### Frontend Not Loading

**Symptom:** Blank page or "Cannot connect"

**Solution:**
```bash
# Check if frontend is running
docker compose ps frontend

# Restart frontend
docker compose restart frontend

# Check logs
docker compose logs frontend
```

### Segments Stuck on "Generating"

**Symptom:** Status stays blue/spinning for >5 minutes

**Solution:**
```bash
# Check worker logs
docker compose logs ai_worker

# Restart workers
docker compose restart ai_worker
```

### Dashboard Not Updating

**Symptom:** Numbers don't change, no auto-refresh

**Solution:**
- Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check backend is responding: http://localhost:8000/health

---

## Next Steps

After completing this walkthrough:

1. ✅ Create multiple projects with different themes
2. ✅ Experiment with different prompt styles
3. ✅ Monitor GPU usage and performance
4. ✅ Try longer videos (10+ segments)
5. ✅ Customize model parameters via API
6. ✅ Explore the API documentation at http://localhost:8000/docs

---

Enjoy creating AI-generated videos! 🎬✨
