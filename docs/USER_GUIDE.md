# User Guide - Video Foundry

This guide will teach you how to use Video Foundry to create AI-generated videos using the timeline editor and various AI models.

## Table of Contents

- [Getting Started](#getting-started)
- [Understanding the Interface](#understanding-the-interface)
- [Creating Your First Project](#creating-your-first-project)
- [Working with Segments](#working-with-segments)
- [Choosing AI Models](#choosing-ai-models)
- [Rendering Videos](#rendering-videos)
- [Monitoring Progress](#monitoring-progress)
- [Downloading Results](#downloading-results)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Prerequisites

Before you begin, make sure:
1. Video Foundry is installed and running ([Setup Guide](SETUP.md))
2. You can access the frontend at http://localhost:5173
3. At least one AI model is configured (ComfyUI, Runway, or Stability)

### Basic Workflow

The typical workflow for creating a video:

```
Create Project → Add Segments → Configure Models → Render → Download
```

1. **Create Project**: Start a new video project
2. **Add Segments**: Define video clips with prompts
3. **Configure Models**: Choose AI model and parameters
4. **Render**: Generate all segments
5. **Download**: Get your final video

## Understanding the Interface

### Main Dashboard

The dashboard shows:
- **Project List**: All your video projects
- **Create Button**: Start a new project
- **Search/Filter**: Find specific projects
- **Recent Activity**: Latest render jobs

### Project View

When viewing a project:
- **Timeline**: Visual representation of video segments
- **Segment List**: Detailed view of all segments
- **Render Button**: Start video generation
- **Settings**: Project configuration

### Timeline Editor

The timeline shows:
- **Segments**: Video clips in sequence (left to right)
- **Duration**: Length of each segment
- **Status Indicators**: Pending, generating, completed, failed
- **Controls**: Add, edit, delete, reorder segments

**Visual Example (text representation):**
```
Timeline:
┌─────────────────────────────────────────────────────────┐
│ [Segment 1]  [Segment 2]  [Segment 3]  [+ Add Segment] │
│   ✓ 5s         ⚙ 5s        ⏸ 5s                        │
│  "Beach"    "Mountains"   "Sunset"                      │
└─────────────────────────────────────────────────────────┘
```

Status Icons:
- ✓ Completed (green)
- ⚙ Generating (blue/spinning)
- ⏸ Pending (gray)
- ✗ Failed (red)

## Creating Your First Project

### Step 1: Create a New Project

1. Open the frontend at http://localhost:5173
2. Click **"Create Project"** button
3. Fill in the form:
   - **Name**: Give your project a descriptive name
   - **Description**: (Optional) Describe the video's purpose
4. Click **"Create"**

**API Alternative:**
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Video",
    "description": "A beautiful nature montage"
  }'
```

### Step 2: View Your Project

After creation, you'll be taken to the project view where you can:
- Add segments
- Configure settings
- Start rendering

## Working with Segments

### Adding a Segment

1. Click **"Add Segment"** button
2. Fill in the segment details:
   - **Prompt**: Describe what you want to see
   - **Model**: Choose AI model (ComfyUI, Runway, Stability)
   - **Duration**: Video length in seconds
   - **Resolution**: Video dimensions
   - **Advanced**: Model-specific parameters
3. Click **"Add"**

**Example Prompts:**
- Text-to-Video: "A serene beach at sunset with gentle waves"
- Image-to-Video: Upload an image and describe motion
- Abstract: "Colorful paint swirling in water, macro shot"
- Scene: "A bustling city street at night, cinematic"

**API Alternative:**
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
  -H "Content-Type: application/json" \
  -d '{
    "order_index": 0,
    "prompt": "A serene beach at sunset with gentle waves",
    "model_params": {
      "model": "comfyui",
      "workflow": {...},
      "duration": 5,
      "resolution": "512x512"
    }
  }'
```

### Editing a Segment

1. Click on a segment in the timeline
2. Modify any field:
   - Change the prompt
   - Adjust parameters
   - Switch models
3. Click **"Save"**

**Note:** Editing a segment resets its status to "pending". It will be re-generated on the next render.

### Deleting a Segment

1. Click on a segment
2. Click **"Delete"** button
3. Confirm deletion

**Warning:** This cannot be undone!

### Reordering Segments

Drag and drop segments in the timeline to change their order. The final video will match the timeline order.

**API Alternative:**
```bash
# Update segment order
curl -X PUT http://localhost:8000/api/segments/{segment_id} \
  -H "Content-Type: application/json" \
  -d '{"order_index": 2}'
```

## Choosing AI Models

Video Foundry supports multiple AI models, each with different strengths.

### ComfyUI (Local, Free)

**Best for:**
- Local generation without API costs
- Custom workflows
- Full control over generation process
- Longer videos (limited by hardware)

**Requirements:**
- ComfyUI running and configured
- Required models installed
- (Optional) GPU for faster generation

**Configuration:**
```json
{
  "model": "comfyui",
  "workflow": "text-to-video-basic",
  "width": 512,
  "height": 512,
  "steps": 20,
  "cfg": 7.5,
  "seed": 42
}
```

**Workflows Available:**
- `text-to-video-basic`: AnimateDiff + SDXL for text-to-video
- `image-to-video-basic`: SVD for animating images
- Custom workflows (see [ComfyUI Integration](COMFYUI_INTEGRATION.md))

### Runway Gen-3 (Cloud, Paid)

**Best for:**
- High-quality cinematic videos
- Fast generation (cloud GPU)
- Professional results
- No local hardware requirements

**Requirements:**
- Runway API key
- Runway account with credits

**Configuration:**
```json
{
  "model": "runway",
  "duration": 5,
  "aspect_ratio": "16:9",
  "resolution": "1080p"
}
```

### Stability AI (Cloud, Paid)

**Best for:**
- Stable Video Diffusion
- Image-to-video conversion
- Consistent quality
- API-based generation

**Requirements:**
- Stability AI API key
- Stability AI account with credits

**Configuration:**
```json
{
  "model": "stability",
  "duration": 4,
  "motion_bucket_id": 127,
  "fps": 6
}
```

### Mock (Testing)

**Best for:**
- Testing the system
- Development
- No generation, instant results

**Configuration:**
```json
{
  "model": "mock"
}
```

## Rendering Videos

### Starting a Render Job

1. Review all segments in the timeline
2. Click **"Render"** button
3. The system will:
   - Queue segments for generation
   - Generate videos in parallel
   - Compose final video
   - Store result

**What happens during rendering:**
```
Render Job Created
    ↓
Segments queued to RabbitMQ
    ↓
AI Workers pick up segments (parallel)
    ↓
Generate video for each segment
    ↓
Store generated segments
    ↓
All segments complete
    ↓
Composition worker combines segments
    ↓
Final video ready
```

**API Alternative:**
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/render
```

### Intelligent Re-rendering

Video Foundry only regenerates segments that have changed:

- **New segment**: Will be generated
- **Edited segment**: Will be re-generated
- **Unchanged segment**: Will use cached video

This saves time and money when using cloud APIs!

**Example:**
```
Original render:
  Segment 1 (beach) + Segment 2 (mountain) + Segment 3 (sunset) → Full render

Edit Segment 2 prompt:
  Segment 1 (cached) + Segment 2 (re-generate) + Segment 3 (cached) → Partial render
```

### Canceling a Render

To cancel an in-progress render job:
1. Click **"Cancel"** button on the render job
2. Segments in progress will be stopped
3. Completed segments are preserved

**Note:** You cannot resume a canceled job. You must start a new render.

## Monitoring Progress

### Real-time Progress Updates

Video Foundry provides real-time updates via WebSocket:

- **Segment Status**: Pending → Generating → Completed/Failed
- **Progress Percentage**: Overall completion (e.g., 2/5 segments = 40%)
- **Estimated Time**: Time remaining (if available)
- **Error Messages**: Detailed error information

### Progress Indicators

**In the UI:**
- Timeline shows segment status with color-coded icons
- Progress bar shows overall completion
- Status panel shows current activity

**API Monitoring:**
```bash
# Get render job status
curl http://localhost:8000/api/render-jobs/{render_job_id}

# WebSocket endpoint (use a WebSocket client)
ws://localhost:8000/api/render-jobs/{render_job_id}/progress
```

### Checking Logs

```bash
# View backend logs
docker-compose logs -f backend

# View worker logs
docker-compose logs -f ai_worker

# View composition logs
docker-compose logs -f composition_worker

# View ComfyUI logs
docker-compose logs -f comfyui
```

## Downloading Results

### From the UI

1. Wait for render job to complete (status: "Completed")
2. Click **"Download"** button
3. Video downloads to your browser's download folder

### From the API

```bash
# Get render job details
curl http://localhost:8000/api/render-jobs/{render_job_id}

# Response includes video URL
{
  "id": "...",
  "status": "completed",
  "final_video_url": "http://s3.amazonaws.com/bucket/video.mp4"
}

# Download video
wget {final_video_url} -O my_video.mp4
```

### From Docker Volume (Local Storage)

```bash
# List videos
docker-compose exec backend ls -la /videos

# Copy video from container
docker cp vf_backend:/videos/render-job-{id}.mp4 ./my_video.mp4
```

## Advanced Features

### Custom ComfyUI Workflows

You can create custom workflows in ComfyUI and use them:

1. Create workflow in ComfyUI GUI (http://localhost:8188)
2. Export as API format (Save > API Format)
3. Save to `/workflows/my-custom-workflow.json`
4. Reference in segment:
```json
{
  "model": "comfyui",
  "workflow": "my-custom-workflow",
  "prompt_node_id": "6",
  "custom_param": "value"
}
```

See [ComfyUI Integration](COMFYUI_INTEGRATION.md) for details.

### Retry Failed Segments

If a segment fails during generation:

1. Click on the failed segment
2. Review error message
3. Fix the issue (adjust prompt, parameters, etc.)
4. Click **"Retry"** button

**API Alternative:**
```bash
curl -X POST http://localhost:8000/api/segments/{segment_id}/retry
```

### Render Job History

View all render jobs for a project:

1. Go to project view
2. Click **"Render History"** tab
3. See all past renders with status and results

**API Alternative:**
```bash
curl http://localhost:8000/api/projects/{project_id}/render-jobs
```

### Batch Operations

**Delete multiple segments:**
```bash
# Delete all segments (via API)
for id in $(curl http://localhost:8000/api/projects/{project_id}/segments | jq -r '.[].id'); do
  curl -X DELETE http://localhost:8000/api/segments/$id
done
```

**Duplicate a project** (not built-in, but can be done via API):
```bash
# Get project details
curl http://localhost:8000/api/projects/{project_id} > project.json

# Create new project with same data
# ... implement duplication logic
```

## Best Practices

### Writing Effective Prompts

**Do:**
- Be specific and descriptive
- Include style keywords (cinematic, photorealistic, artistic)
- Specify mood and atmosphere
- Mention camera angles if needed
- Use positive language (what you want, not what you don't want)

**Don't:**
- Use vague descriptions
- Include too many conflicting concepts
- Forget about aspect ratio/composition
- Use copyrighted/trademarked terms

**Good Examples:**
```
✓ "A misty forest at dawn, golden sunlight filtering through trees, cinematic wide shot"
✓ "Waves crashing on rocky shore, slow motion, dramatic sunset lighting, 4k quality"
✓ "Abstract colorful smoke swirling, vibrant purples and blues, macro photography"
```

**Bad Examples:**
```
✗ "Forest" (too vague)
✗ "A Marvel superhero flying through NYC" (copyright issues)
✗ "Something cool with water" (not specific enough)
```

### Model Selection

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| High quality, cinematic | Runway Gen-3 | Best quality, fastest |
| Budget-friendly | ComfyUI | Free, local |
| Image animation | Stability AI or ComfyUI (SVD) | Specialized |
| Long videos | ComfyUI | No cloud API limits |
| Quick prototyping | Mock | Instant results |
| Custom styles | ComfyUI | Full workflow control |

### Performance Optimization

**For faster rendering:**
1. Use multiple AI workers: `docker-compose up -d --scale ai_worker=4`
2. Lower resolution for drafts (512x512), final render in higher res
3. Use GPU for ComfyUI (see [Setup Guide](SETUP.md))
4. Reduce sampling steps for faster generation
5. Use shorter segments (3-5 seconds)

**For better quality:**
1. Increase sampling steps (25-30)
2. Use higher resolution (1024x576 or higher)
3. Adjust CFG scale (7-8.5 for text-to-video)
4. Use detailed prompts
5. Experiment with different seeds

**For cost efficiency (cloud APIs):**
1. Test with ComfyUI first
2. Only use cloud APIs for final renders
3. Leverage intelligent re-rendering
4. Use shorter durations
5. Batch similar segments

### Project Organization

**Naming Conventions:**
- Projects: "Client_ProjectName_Version" (e.g., "Acme_ProductDemo_v2")
- Segments: Number segments by scene (e.g., "01_intro", "02_product", "03_outro")

**Descriptions:**
- Use descriptions to document:
  - Project purpose
  - Target audience
  - Delivery date
  - Special requirements

### Video Composition Tips

**Segment Duration:**
- Short (2-3s): Quick cuts, dynamic pacing
- Medium (5-7s): Standard scenes
- Long (10s+): Establishing shots, slow reveals

**Ordering:**
- Start strong: Hook viewers immediately
- Build momentum: Increase energy toward middle
- End memorable: Strong closing shot

**Transitions:**
- Current version concatenates segments directly
- Plan for smooth visual flow between segments
- Consider matching colors/lighting across cuts

## Tips and Tricks

### Getting Consistent Results

**Use seeds:**
```json
{
  "seed": 42  // Same seed = reproducible results
}
```

**Save working prompts:**
- Keep a document of successful prompts
- Note which models work best for each style

### Troubleshooting Generation Issues

**Low quality output:**
- Increase sampling steps
- Adjust CFG scale
- Try different workflows
- Use better quality models

**Unwanted content:**
- Add negative prompt (ComfyUI)
- Be more specific in positive prompt
- Try different seeds

**Slow generation:**
- Use GPU
- Reduce resolution
- Lower sampling steps
- Use cloud APIs

### Keyboard Shortcuts (Future Feature)

Currently, Video Foundry doesn't have keyboard shortcuts, but these would be useful:
- Ctrl+N: New project
- Ctrl+S: Save/render
- Delete: Delete selected segment
- Ctrl+D: Duplicate segment

### Browser Recommendations

**Best Performance:**
- Chrome/Chromium
- Firefox
- Edge

**Features:**
- WebSocket support required for real-time updates
- Modern JavaScript support

### Mobile Access

The web UI works on mobile browsers, but the experience is optimized for desktop:
- Timeline editing is easier on desktop
- Video preview works on mobile
- API is fully accessible from any device

## Common Workflows

### Workflow 1: Marketing Video

```
1. Create project: "Product Launch Video"
2. Add segments:
   - Segment 1: Product reveal (5s)
   - Segment 2: Features showcase (7s)
   - Segment 3: Call-to-action (3s)
3. Use Runway for high quality
4. Render and download
5. Add music/voiceover in external editor
```

### Workflow 2: Social Media Content

```
1. Create project: "Instagram Reel"
2. Add 3-5 short segments (3s each)
3. Use ComfyUI for budget
4. Portrait orientation (9:16)
5. Render quickly
6. Post directly
```

### Workflow 3: Experimentation

```
1. Create project: "Style Tests"
2. Add same prompt with different models
3. Compare results
4. Save best workflow for production
```

### Workflow 4: Long-form Content

```
1. Create project: "Documentary B-Roll"
2. Add many segments (20+)
3. Use ComfyUI to avoid costs
4. Render in batches
5. Edit in traditional video editor
```

## Getting Help

### Built-in Help

- **Tooltips**: Hover over UI elements for descriptions
- **API Docs**: http://localhost:8000/docs (interactive API documentation)
- **Error Messages**: Detailed error messages in UI and logs

### Documentation

- [Setup Guide](SETUP.md) - Installation and configuration
- [ComfyUI Integration](COMFYUI_INTEGRATION.md) - Custom workflows
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Workflow README](../workflows/README.md) - Workflow details

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share tips
- Discord: (Add server link if available)

## Next Steps

Now that you know the basics:

1. **Experiment**: Try different prompts and models
2. **Explore**: Read [ComfyUI Integration](COMFYUI_INTEGRATION.md) for advanced workflows
3. **Optimize**: Use the tips above to improve quality and speed
4. **Share**: Post your creations and help others!

---

**Happy video creating!**
