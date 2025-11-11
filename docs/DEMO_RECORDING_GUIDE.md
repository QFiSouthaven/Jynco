# Demo GIF Recording Guide

This guide will help you create professional demo GIFs showcasing Video Foundry's timeline editor.

## Tools Needed

### Option 1: macOS (Easiest)
- **Kap** (Free, Open Source): https://getkap.co/
  - Best quality, easy to use
  - Can export directly to GIF
  - Has cropping and trimming tools

### Option 2: Windows
- **ScreenToGif** (Free): https://www.screentogif.com/
  - Record, edit, and export GIFs
  - Built-in editor

### Option 3: Linux
- **Peek** (Free): https://github.com/phw/peek
  - Simple GIF recorder for Linux
  - Works with most window managers

### Option 4: Cross-Platform
- **OBS Studio** + **FFMPEG**: Record video, convert to GIF
  ```bash
  # Record with OBS, then convert:
  ffmpeg -i input.mp4 -vf "fps=15,scale=1200:-1:flags=lanczos" output.gif
  ```

## Demo Scenarios

### Demo 1: Complete Workflow (30 seconds)
**File**: `demo-complete-workflow.gif`

**Script:**
1. **Start**: Show empty project list (2s)
2. **Create**: Click "New Project", enter name "My AI Video" (3s)
3. **Timeline**: Show empty timeline editor (2s)
4. **Add Segment 1**: Click "Add Segment", type "Sunrise over mountains" (4s)
5. **Add Segment 2**: Click "Add Segment", type "Birds flying in sky" (4s)
6. **Add Segment 3**: Click "Add Segment", type "Ocean waves crashing" (4s)
7. **Render**: Click "Render Video" button (2s)
8. **Dashboard**: Navigate to dashboard, show progress (5s)
9. **Complete**: Show completed render with 3 segments (4s)

### Demo 2: Timeline Editor Focus (15 seconds)
**File**: `demo-timeline-editor.gif`

**Script:**
1. **Show**: Timeline with 3 existing segments (3s)
2. **Edit**: Click edit on segment 2, change prompt (5s)
3. **Reorder**: Drag segment to new position (3s)
4. **Add**: Click "Add Segment" button (2s)
5. **Save**: Show save indicator (2s)

### Demo 3: Real-Time Progress (20 seconds)
**File**: `demo-realtime-progress.gif`

**Script:**
1. **Dashboard**: Show dashboard with active render (3s)
2. **Progress**: Show segments moving from "pending" → "generating" (10s)
3. **Complete**: Show segments turning green as they complete (5s)
4. **Final**: Show final video download link (2s)

## Recording Tips

### Before Recording

1. **Clean environment**
   ```bash
   # Reset database for clean demo
   docker-compose down -v
   docker-compose up -d

   # Wait for services to start
   sleep 20
   ```

2. **Browser setup**
   - Use Chrome or Firefox
   - Set browser zoom to 100%
   - Close unnecessary tabs
   - Hide bookmarks bar (Ctrl/Cmd + Shift + B)
   - Use incognito mode for clean UI

3. **Screen resolution**
   - Recommended: 1920x1080 or 1280x720
   - Record in 16:9 aspect ratio
   - Don't record full screen - crop to just the app

### During Recording

1. **Recording settings**
   - Frame rate: 15-20 FPS (lower file size)
   - Resolution: 1200px wide (GitHub maximum)
   - Format: GIF or MP4 (convert to GIF later)

2. **Mouse movements**
   - Move mouse slowly and deliberately
   - Pause briefly before clicking (1 second)
   - Use smooth, direct movements

3. **Timing**
   - Keep GIFs under 30 seconds
   - Let UI transitions complete before next action
   - Don't rush - clarity > speed

4. **Text input**
   - Type at moderate speed
   - Use realistic prompts that showcase features

### After Recording

1. **Trim and edit**
   - Remove dead time at start/end
   - Cut out any mistakes
   - Add 1-second pause at the end (loops better)

2. **Optimize GIF size**
   ```bash
   # Using gifsicle (install via brew/apt)
   gifsicle -O3 --colors 256 input.gif -o output.gif

   # Or use online tools:
   # - https://ezgif.com/optimize
   # - https://gifcompressor.com/
   ```

3. **Target specifications**
   - File size: Under 10MB (GitHub limit)
   - Dimensions: 1200px max width
   - Frame rate: 15 FPS
   - Colors: 256 (GIF limit)

## Recording Script

Here's the exact script to follow:

### Setup Phase (Do Before Recording)
```bash
# 1. Start fresh
docker-compose down -v
docker-compose up -d

# 2. Wait for services
sleep 30

# 3. Open browser
open http://localhost:3000  # macOS
# or: xdg-open http://localhost:3000  # Linux
# or: start http://localhost:3000  # Windows

# 4. Resize browser window to 1280x800
# 5. Start recording tool
# 6. Position window for optimal framing
```

### Recording Phase
```
SCENE 1: Home (3 seconds)
- Show project list page
- Hover over "New Project" button
- PAUSE

SCENE 2: Create Project (5 seconds)
- Click "New Project"
- Type: "My AI Video Demo"
- Type in description: "Three-segment video showcasing timeline"
- Click "Create"
- PAUSE

SCENE 3: Timeline Editor (15 seconds)
- Timeline loads (empty)
- Click "Add Segment"
- Type prompt: "A beautiful sunrise over mountain peaks"
- Click "Add Segment" (confirmed)
- PAUSE
- Click "Add Segment" again
- Type prompt: "Birds soaring through clouds"
- Click "Add Segment"
- PAUSE
- Click "Add Segment" third time
- Type prompt: "Ocean waves crashing on beach"
- Click "Add Segment"
- Show all 3 segments in timeline
- PAUSE

SCENE 4: Render (3 seconds)
- Hover over "Render Video" button
- Click "Render Video"
- See confirmation/loading state
- PAUSE

SCENE 5: Dashboard (7 seconds)
- Click "Dashboard" in navigation
- Show render job appearing
- Segments show as "generating"
- Segments turn to "completed" (accelerated if needed)
- Show final video link
- END
```

### Post-Production
1. **Trim**: Remove first/last 0.5 seconds
2. **Speed up**: If over 30 seconds, speed up to 1.2x
3. **Add loop pause**: Add 1 second pause at end
4. **Optimize**: Run through optimizer
5. **Test**: Verify loops smoothly

## Placement in README

Add GIFs to README.md:

```markdown
## 🎬 See It In Action

### Complete Workflow
![Video Foundry Demo](docs/demo-complete-workflow.gif)

### Timeline Editor
![Timeline Editor](docs/demo-timeline-editor.gif)

### Real-Time Progress
![Real-Time Progress](docs/demo-realtime-progress.gif)
```

## Alternative: Video Demo

If GIF file size is too large, consider video instead:

```markdown
## 🎬 Demo Video

[![Video Foundry Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
```

Upload to:
- YouTube (unlisted)
- Vimeo
- Loom
- Direct MP4 in GitHub release assets

## Checklist

Before finalizing demos:

- [ ] GIFs load quickly (under 10MB each)
- [ ] GIFs loop smoothly
- [ ] UI is crisp and readable
- [ ] No personal information visible
- [ ] Mock data looks realistic
- [ ] All buttons/actions are clear
- [ ] Timing feels natural (not rushed)
- [ ] Demonstrates key features clearly
- [ ] Works in both light/dark themes (if applicable)
- [ ] Mobile-friendly viewing (consider responsive screenshots too)

## Examples of Good Demo GIFs

Reference these for inspiration:
- https://github.com/vercel/next.js (homepage demo)
- https://github.com/laurent22/joplin (feature demos)
- https://github.com/excalidraw/excalidraw (interaction demos)

## Quick Record Now

Want to record right away? Run this:

```bash
# Start everything fresh
docker-compose down -v && docker-compose up -d

# Wait for startup
echo "Waiting for services to start..." && sleep 30

# Open browser
open http://localhost:3000

# Start your screen recorder and follow the script above!
```

Good luck with your demo recording! 🎥✨
