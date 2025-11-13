# ComfyUI Integration Guide - Video Foundry

This guide explains how Video Foundry integrates with ComfyUI, how to use the provided workflows, and how to create your own custom workflows.

## Table of Contents

- [Overview](#overview)
- [How ComfyUI Integration Works](#how-comfyui-integration-works)
- [Default Workflows](#default-workflows)
- [Using ComfyUI Workflows](#using-comfyui-workflows)
- [Creating Custom Workflows](#creating-custom-workflows)
- [Exporting Workflows from ComfyUI](#exporting-workflows-from-comfyui)
- [Workflow Parameters Reference](#workflow-parameters-reference)
- [Advanced Customization](#advanced-customization)
- [Troubleshooting ComfyUI Issues](#troubleshooting-comfyui-issues)
- [Required Models and Nodes](#required-models-and-nodes)

## Overview

ComfyUI is a powerful node-based UI for Stable Diffusion and other AI models. Video Foundry integrates with ComfyUI to provide:

- **Local generation**: No cloud API costs
- **Custom workflows**: Full control over generation pipeline
- **Multiple models**: AnimateDiff, SVD, SDXL, and more
- **Flexible parameters**: Adjust every aspect of generation

### Why Use ComfyUI?

**Advantages:**
- Free (no API costs)
- Runs locally on your hardware
- Complete customization
- Access to latest models
- Privacy (data never leaves your machine)

**Considerations:**
- Requires local hardware (GPU recommended)
- Slower than cloud APIs (depending on hardware)
- Requires model installation
- More complex setup

## How ComfyUI Integration Works

### Architecture

```
Video Foundry Backend
        ↓
   AI Worker
        ↓
  ComfyUI Adapter
        ↓
  HTTP API Request
        ↓
  ComfyUI Server
        ↓
  Generate Video
        ↓
  Return Result
        ↓
  Store in S3/Local
```

### Data Flow

1. **User creates segment** with prompt and model params
2. **Backend queues** segment generation task
3. **AI Worker picks up** task from RabbitMQ
4. **ComfyUI Adapter:**
   - Loads workflow JSON
   - Injects user prompt into workflow
   - Injects parameters (resolution, steps, etc.)
   - Submits to ComfyUI API
5. **ComfyUI executes** workflow:
   - Loads models
   - Processes nodes in order
   - Generates video frames
   - Encodes video
6. **Adapter polls** for completion
7. **Downloads result** from ComfyUI
8. **Stores video** in S3 or local storage
9. **Updates database** with video URL

### ComfyUI API

Video Foundry uses ComfyUI's REST API:

- `POST /prompt` - Submit workflow for execution
- `GET /history/{prompt_id}` - Check status
- `GET /view` - Download generated video
- `GET /system_stats` - Health check

## Default Workflows

Video Foundry includes two production-ready workflows:

### 1. Text-to-Video (AnimateDiff)

**File:** `/workflows/text-to-video-basic.json`

**Description:**
Generates short animated videos from text prompts using AnimateDiff motion module with Stable Diffusion XL.

**Models Required:**
- `sd_xl_base_1.0.safetensors` (Stable Diffusion XL)
- `mm_sd_v15_v2.ckpt` (AnimateDiff motion module)

**Custom Nodes Required:**
- ComfyUI-AnimateDiff-Evolved
- ComfyUI-VideoHelperSuite

**Default Parameters:**
```json
{
  "model": "comfyui",
  "workflow": "text-to-video-basic",
  "width": 512,
  "height": 512,
  "batch_size": 16,  // Number of frames
  "steps": 20,
  "cfg": 7.5,
  "seed": 42,
  "frame_rate": 8
}
```

**Best For:**
- Text-to-video generation
- Artistic animations
- Short clips (2-3 seconds)
- Creative effects

**Example Usage:**
```json
{
  "prompt": "A serene Japanese garden in autumn, leaves falling gently, cinematic",
  "model_params": {
    "model": "comfyui",
    "workflow": "text-to-video-basic",
    "width": 512,
    "height": 512,
    "steps": 25,
    "cfg": 7.5
  }
}
```

### 2. Image-to-Video (Stable Video Diffusion)

**File:** `/workflows/image-to-video-basic.json`

**Description:**
Animates static images into short video clips using Stable Video Diffusion XT.

**Models Required:**
- `svd_xt.safetensors` (Stable Video Diffusion XT)

**Custom Nodes Required:**
- ComfyUI-VideoHelperSuite

**Default Parameters:**
```json
{
  "model": "comfyui",
  "workflow": "image-to-video-basic",
  "image_path": "input.png",
  "width": 1024,
  "height": 576,
  "video_frames": 25,
  "motion_bucket_id": 127,
  "fps": 6,
  "steps": 20,
  "cfg": 2.5
}
```

**Best For:**
- Animating still images
- Product demonstrations
- Character animation
- Smooth motion

**Example Usage:**
```json
{
  "prompt": "Gentle camera pan and zoom",
  "model_params": {
    "model": "comfyui",
    "workflow": "image-to-video-basic",
    "image_path": "/path/to/image.png",
    "motion_bucket_id": 100,
    "steps": 25
  }
}
```

## Using ComfyUI Workflows

### Method 1: Via API (Production)

Load workflow and submit via API:

```python
import json
import requests

# Load workflow
with open('workflows/text-to-video-basic.json', 'r') as f:
    workflow = json.load(f)

# Create segment with workflow
response = requests.post(
    'http://localhost:8000/api/projects/{project_id}/segments',
    json={
        'order_index': 0,
        'prompt': 'A beautiful sunset over mountains',
        'model_params': {
            'model': 'comfyui',
            'workflow': workflow,
            'width': 512,
            'height': 512,
            'steps': 20
        }
    }
)
```

### Method 2: Via Frontend (User-Friendly)

1. Open project in frontend
2. Click "Add Segment"
3. Select model: "ComfyUI"
4. Choose workflow: "Text-to-Video" or "Image-to-Video"
5. Adjust parameters as needed
6. Enter prompt
7. Click "Add"

### Method 3: Direct ComfyUI Testing

Test workflows directly in ComfyUI UI before using in Video Foundry:

1. Open ComfyUI: http://localhost:8188
2. Click "Load"
3. Select workflow JSON file
4. Edit nodes as needed
5. Click "Queue Prompt"
6. View results in ComfyUI
7. Once satisfied, use in Video Foundry

## Creating Custom Workflows

### Step-by-Step Guide

#### Step 1: Design in ComfyUI GUI

1. Open ComfyUI UI: http://localhost:8188
2. Create your workflow:
   - Add nodes (right-click → Add Node)
   - Connect nodes (drag from output to input)
   - Configure parameters
3. Test the workflow with sample prompts
4. Iterate until you get desired results

**Example Workflow Structure:**
```
[Checkpoint Loader] → [CLIP Text Encode] → [KSampler] → [VAE Decode] → [Video Combine]
                           ↑                      ↑            ↑
                    [Prompt Input]        [Latent Image]  [Frames]
```

#### Step 2: Identify Prompt Node

**Important:** Node ID "6" should be your main text prompt input.

Find or create a CLIPTextEncode node:
1. Add "CLIP Text Encode" node
2. Set its ID to "6" (important!)
3. Connect to your sampler

**Why Node 6?**
The ComfyUI adapter automatically injects your prompt into node 6. This is a convention for compatibility.

#### Step 3: Test Thoroughly

Test with various prompts:
- Simple prompts
- Complex prompts
- Edge cases
- Different resolutions
- Different parameters

#### Step 4: Export API Format

**Enable Dev Mode:**
1. Click Settings (gear icon)
2. Enable "Dev mode Options"
3. Close settings

**Export Workflow:**
1. Click Menu (☰)
2. Select "Save (API Format)"
3. Save as `my-custom-workflow.json`
4. Move to `/workflows/` directory

#### Step 5: Document Your Workflow

Create a README section for your workflow:
```markdown
### My Custom Workflow

**Description:** Brief description

**Models Required:**
- model_name.safetensors

**Custom Nodes:**
- NodePackageName

**Parameters:**
- param1: description (default: value)
- param2: description (range: min-max)
```

### Custom Workflow Template

Here's a minimal workflow template:

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    }
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "placeholder - will be replaced",
      "clip": ["1", 1]
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 7.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["2", 0]
    }
  }
  // ... more nodes
}
```

## Exporting Workflows from ComfyUI

### Prerequisites

- ComfyUI running and accessible
- Workflow created and tested
- Dev mode enabled

### Export Process

**Step 1: Enable API Format Export**

```
ComfyUI UI → Settings (⚙) → Enable "Dev mode Options" → Close
```

**Step 2: Save API Format**

```
Menu (☰) → Save (API Format) → Choose filename → Save
```

**Step 3: Verify Export**

Check the JSON file:
```bash
cat my-workflow.json | jq .

# Should show node structure:
{
  "1": { "class_type": "...", "inputs": {...} },
  "2": { ... },
  ...
}
```

**Step 4: Test in Video Foundry**

```bash
# Copy to workflows directory
cp my-workflow.json /home/user/Jynco/workflows/

# Test via API
curl -X POST http://localhost:8000/api/projects/{project_id}/segments \
  -H "Content-Type: application/json" \
  -d @test-segment.json
```

### Common Export Issues

**Issue: Can't find "Save (API Format)"**
- Solution: Enable Dev mode in Settings

**Issue: Export is empty or invalid**
- Solution: Make sure workflow has nodes before exporting

**Issue: Workflow doesn't work in Video Foundry**
- Solution: Verify node 6 exists and is a text input node

## Workflow Parameters Reference

### ComfyUI Adapter Parameters

The adapter injects these parameters automatically:

| Parameter | Description | Injected Into | Default |
|-----------|-------------|---------------|---------|
| `prompt` | User's text prompt | Node 6 | (required) |
| `width` | Video width | Sampler node | 512 |
| `height` | Video height | Sampler node | 512 |
| `seed` | Random seed | Sampler node | 42 |
| `steps` | Sampling steps | Sampler node | 20 |
| `cfg` | CFG scale | Sampler node | 7.5 |

**How Injection Works:**

```python
# Example from ComfyUIAdapter
def _inject_prompt(workflow, prompt, model_params):
    # Inject prompt into node 6
    if "6" in workflow:
        workflow["6"]["inputs"]["text"] = prompt

    # Inject resolution into sampler
    sampler_id = model_params.get("sampler_node_id", "3")
    if sampler_id in workflow:
        workflow[sampler_id]["inputs"]["width"] = model_params.get("width", 512)
        workflow[sampler_id]["inputs"]["height"] = model_params.get("height", 512)

    return workflow
```

### Custom Parameters

You can pass custom parameters via `model_params`:

```json
{
  "model_params": {
    "model": "comfyui",
    "workflow": "my-custom-workflow",
    "custom_param_1": "value",
    "custom_param_2": 123,
    "node_overrides": {
      "5": {
        "inputs": {
          "strength": 0.8
        }
      }
    }
  }
}
```

To use custom parameters, modify the adapter's `_inject_prompt` method.

### AnimateDiff Parameters

For text-to-video workflows:

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `batch_size` | Number of frames | 8-32 | 16 |
| `context_length` | Context window | 8-24 | 16 |
| `context_stride` | Frame stride | 1-4 | 1 |
| `context_overlap` | Frame overlap | 2-8 | 4 |
| `frame_rate` | Output FPS | 4-30 | 8 |

### SVD Parameters

For image-to-video workflows:

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `video_frames` | Number of frames | 14-30 | 25 |
| `motion_bucket_id` | Motion intensity | 1-255 | 127 |
| `fps` | Frames per second | 4-12 | 6 |
| `augmentation_level` | Noise augmentation | 0.0-1.0 | 0.0 |

## Advanced Customization

### Custom Adapter Logic

Modify `/workers/ai_worker/adapters/comfyui.py` to add custom logic:

```python
def _inject_prompt(self, workflow, prompt, model_params):
    # Standard injection
    workflow = super()._inject_prompt(workflow, prompt, model_params)

    # Custom logic
    if "custom_mode" in model_params:
        mode = model_params["custom_mode"]
        if mode == "high_quality":
            # Adjust settings for quality
            workflow["3"]["inputs"]["steps"] = 30
            workflow["3"]["inputs"]["cfg"] = 8.5

    return workflow
```

### Multi-Prompt Workflows

Support multiple prompts (e.g., positive + negative):

```python
def _inject_prompt(self, workflow, prompt, model_params):
    # Positive prompt (node 6)
    workflow["6"]["inputs"]["text"] = prompt

    # Negative prompt (node 7)
    negative = model_params.get("negative_prompt", "")
    if "7" in workflow:
        workflow["7"]["inputs"]["text"] = negative

    return workflow
```

Usage:
```json
{
  "prompt": "Beautiful landscape, high quality",
  "model_params": {
    "negative_prompt": "blurry, low quality, distorted"
  }
}
```

### Conditional Nodes

Use different nodes based on parameters:

```python
def _inject_prompt(self, workflow, prompt, model_params):
    use_controlnet = model_params.get("use_controlnet", False)

    if use_controlnet:
        # Enable ControlNet nodes
        workflow["10"]["inputs"]["strength"] = 0.8
    else:
        # Disable ControlNet nodes
        del workflow["10"]

    return workflow
```

### Dynamic Workflow Selection

Choose workflow based on prompt analysis:

```python
def initiate_generation(self, prompt, model_params):
    # Analyze prompt
    if "image" in model_params:
        workflow_name = "image-to-video-basic"
    elif len(prompt.split()) < 10:
        workflow_name = "text-to-video-simple"
    else:
        workflow_name = "text-to-video-complex"

    # Load workflow
    workflow = self._load_workflow(workflow_name)

    # Continue with generation...
```

## Troubleshooting ComfyUI Issues

### Connection Issues

**Error: "Cannot connect to ComfyUI"**

Check if ComfyUI is running:
```bash
docker-compose ps comfyui
curl http://localhost:8188/system_stats
```

Fix:
```bash
# Restart ComfyUI
docker-compose restart comfyui

# Check logs
docker-compose logs comfyui
```

### Missing Nodes Error

**Error: "Node 'AnimateDiffLoader' not found"**

Install required custom nodes:
```bash
docker-compose exec comfyui bash
cd /home/runner/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt
exit

docker-compose restart comfyui
```

### Model Not Found

**Error: "Model 'sd_xl_base_1.0.safetensors' not found"**

Download required model:
```bash
docker-compose exec comfyui bash
cd /home/runner/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### Out of Memory (OOM)

**Error: "CUDA out of memory"**

Solutions:
1. Reduce resolution: `512x512` instead of `1024x1024`
2. Reduce frame count: `8` instead of `16`
3. Enable low VRAM mode:
```yaml
# docker-compose.yml
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --lowvram
```

4. Use CPU (very slow):
```yaml
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --cpu
```

### Slow Generation

**Issue: Generation takes too long**

Optimizations:
1. **Use GPU**: Ensure GPU is enabled and working
2. **Reduce steps**: Use 15-20 instead of 30-50
3. **Lower resolution**: Start with 512x512
4. **Fewer frames**: Use 8-12 frames for testing
5. **Enable optimizations**:
```yaml
comfyui:
  environment:
    - CLI_ARGS=--listen 0.0.0.0 --port 8188 --highvram --fp16-vae
```

### Workflow Not Working

**Issue: Exported workflow fails in Video Foundry**

Debug steps:
1. **Test in ComfyUI UI first**
2. **Verify node 6 exists**:
```bash
cat workflow.json | jq '.["6"]'
```
3. **Check workflow structure**:
```bash
cat workflow.json | jq 'keys'
```
4. **Enable debug logging**:
```python
# In comfyui.py
logger.setLevel(logging.DEBUG)
```
5. **Check adapter logs**:
```bash
docker-compose logs ai_worker | grep comfyui
```

## Required Models and Nodes

### Models

**For Text-to-Video:**
- Stable Diffusion XL Base 1.0
  - Size: ~6.9 GB
  - Download: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
  - Path: `ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`

- AnimateDiff Motion Module v2
  - Size: ~1.7 GB
  - Download: https://huggingface.co/guoyww/animatediff/tree/main
  - Path: `ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models/mm_sd_v15_v2.ckpt`

**For Image-to-Video:**
- Stable Video Diffusion XT
  - Size: ~9.6 GB
  - Download: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt
  - Path: `ComfyUI/models/checkpoints/svd_xt.safetensors`

### Custom Nodes

**Required for Text-to-Video:**
```bash
# ComfyUI-AnimateDiff-Evolved
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git

# ComfyUI-VideoHelperSuite
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
```

**Installation:**
```bash
docker-compose exec comfyui bash
cd /home/runner/ComfyUI/custom_nodes

git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt

cd /home/runner/ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt

exit
docker-compose restart comfyui
```

### Verification

Check if models and nodes are installed:

```bash
# Access ComfyUI
# Open http://localhost:8188

# Try loading a default workflow
# Load → text-to-video-basic.json
# If it loads without errors, everything is installed!
```

## Next Steps

- Explore [Workflow Templates](../workflows/README.md)
- Create your first custom workflow
- Join the community and share your workflows
- Contribute new workflow templates to the repository

## Resources

- [ComfyUI Documentation](https://docs.comfy.org/)
- [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples)
- [AnimateDiff GitHub](https://github.com/guoyww/AnimateDiff)
- [Stable Video Diffusion Paper](https://stability.ai/research/stable-video-diffusion-scaling-latent-video-diffusion-models-to-large-datasets)
- [Video Foundry Workflow Repository](../workflows/)

---

**Happy workflow creating!**
