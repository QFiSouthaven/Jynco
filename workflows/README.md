# ComfyUI Workflow Templates for Video Foundry

This directory contains default ComfyUI workflow templates for the Video Foundry system. These workflows are production-ready JSON files that define the node graph for video generation.

## Available Workflows

### 1. `text-to-video-basic.json`
**Type:** Text-to-Video
**Model:** AnimateDiff + Stable Diffusion XL
**Output:** MP4 video (8 fps, 16 frames)

Generates animated videos from text prompts using the AnimateDiff motion module with SDXL base.

**Key Features:**
- Supports text prompts (node 6) and negative prompts (node 7)
- Configurable resolution (default: 512x512)
- 16-frame animation with context window
- Pyramid fusing for smooth motion

### 2. `image-to-video-basic.json`
**Type:** Image-to-Video
**Model:** Stable Video Diffusion XT (SVD)
**Output:** MP4 video (6 fps, 25 frames)

Animates static images into short video clips using Stable Video Diffusion.

**Key Features:**
- Uses input image as starting frame
- Configurable motion intensity (motion_bucket_id)
- High-quality video output (1024x576 default)
- Linear CFG guidance for better coherence

## Using These Workflows

### Method 1: Via API (Recommended for Production)

Load the workflow JSON and pass it to the ComfyUI adapter:

```python
import json
from workers.ai_worker.adapters.comfyui import ComfyUIAdapter

# Load workflow
with open('workflows/text-to-video-basic.json', 'r') as f:
    workflow = json.load(f)

# Initialize adapter
adapter = ComfyUIAdapter(config={
    "comfyui_url": "http://localhost:8188",
    "default_workflow": workflow
})

# Generate video
job_id = await adapter.initiate_generation(
    prompt="A serene beach at sunset with gentle waves",
    model_params={
        "workflow": workflow,
        "prompt_node_id": "6",  # Default
        "sampler_node_id": "3",
        "width": 512,
        "height": 512
    }
)
```

### Method 2: Via ComfyUI GUI

1. Open ComfyUI web interface
2. Click "Load" button
3. Select the workflow JSON file
4. Modify parameters as needed
5. Click "Queue Prompt" to generate

## How to Export Custom Workflows from ComfyUI

### Step 1: Enable API Format Export

1. Open ComfyUI Settings (gear icon)
2. Enable **"Dev mode Options"**
3. A new menu option will appear: **"Save (API Format)"**

### Step 2: Export Your Workflow

1. Create your workflow in ComfyUI GUI
2. Click the menu button (top-right)
3. Select **"Save (API Format)"**
4. Save the JSON file to this directory

### Step 3: Ensure Node ID Compatibility

The Video Foundry adapter expects:
- **Node 6**: Positive text prompt (CLIPTextEncode)
- **Node 7**: Negative text prompt (CLIPTextEncode - optional)
- **Node with sampler**: Should accept width/height inputs

To ensure compatibility, use node ID "6" for your main text prompt node.

## Modifiable Parameters

### Text-to-Video Workflow

| Node ID | Parameter | Description | Default | Range |
|---------|-----------|-------------|---------|-------|
| 6 | text | Positive prompt | (varies) | Any text |
| 7 | text | Negative prompt | "blurry..." | Any text |
| 2 | width | Video width | 512 | 256-1024 |
| 2 | height | Video height | 512 | 256-1024 |
| 2 | batch_size | Number of frames | 16 | 8-32 |
| 3 | steps | Sampling steps | 20 | 10-50 |
| 3 | cfg | Classifier-free guidance | 7.5 | 1.0-20.0 |
| 3 | seed | Random seed | 42 | Any integer |
| 5 | frame_rate | Output FPS | 8 | 4-30 |

### Image-to-Video Workflow

| Node ID | Parameter | Description | Default | Range |
|---------|-----------|-------------|---------|-------|
| 2 | image | Input image path | "input.png" | File path |
| 3 | width | Video width | 1024 | 512-1024 |
| 3 | height | Video height | 576 | 320-576 |
| 3 | video_frames | Number of frames | 25 | 14-30 |
| 3 | motion_bucket_id | Motion intensity | 127 | 1-255 |
| 3 | fps | Frames per second | 6 | 4-12 |
| 5 | steps | Sampling steps | 20 | 15-30 |
| 5 | cfg | CFG scale | 2.5 | 1.0-5.0 |
| 5 | seed | Random seed | 42 | Any integer |

## Required Models and Custom Nodes

### Text-to-Video Workflow

**Required Models:**
- `sd_xl_base_1.0.safetensors` - Stable Diffusion XL base model
  - Download from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
  - Place in: `ComfyUI/models/checkpoints/`

- `mm_sd_v15_v2.ckpt` - AnimateDiff motion module
  - Download from: https://huggingface.co/guoyww/animatediff/tree/main
  - Place in: `ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models/`

**Required Custom Nodes:**
- [ComfyUI-AnimateDiff-Evolved](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved)
  ```bash
  cd ComfyUI/custom_nodes
  git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
  ```

- [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
  ```bash
  cd ComfyUI/custom_nodes
  git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
  ```

### Image-to-Video Workflow

**Required Models:**
- `svd_xt.safetensors` - Stable Video Diffusion XT model
  - Download from: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt
  - Place in: `ComfyUI/models/checkpoints/`

**Required Custom Nodes:**
- [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
  ```bash
  cd ComfyUI/custom_nodes
  git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
  ```

## Parameter Guidelines

### Resolution Guidelines

**Text-to-Video (AnimateDiff):**
- Recommended: 512x512, 512x768, 768x512
- Maximum: 1024x1024 (requires high VRAM)
- Keep total pixels under 1M for best performance

**Image-to-Video (SVD):**
- Recommended: 1024x576 (native training resolution)
- Alternative: 768x432, 512x288 (downscaled)
- SVD performs best at 1024x576

### Motion Control

**motion_bucket_id** (Image-to-Video):
- Low motion (1-50): Subtle animations, gentle movements
- Medium motion (50-150): Normal animation, good for most scenes
- High motion (150-255): Dramatic movement, action scenes

### Quality Settings

**Sampling Steps:**
- Fast (10-15 steps): Quick preview, lower quality
- Balanced (20-25 steps): Good quality, reasonable time
- High quality (30-50 steps): Best quality, slower

**CFG Scale:**
- Text-to-Video: 7.0-8.5 for balanced prompt following
- Image-to-Video: 2.0-3.5 for stable motion (SVD is sensitive)

### Frame Count

**Text-to-Video:**
- Short (8-12 frames): ~1 second clips
- Medium (16-24 frames): 2-3 second clips
- Long (24-32 frames): Requires more VRAM

**Image-to-Video:**
- Standard: 25 frames (~4 seconds at 6 fps)
- Trained range: 14-30 frames
- Longer videos may reduce quality

## Troubleshooting

### "Missing nodes" Error
Install the required custom nodes listed above. Restart ComfyUI after installation.

### "Model not found" Error
Download the required model files and place them in the correct directories.

### Out of Memory (OOM) Error
- Reduce resolution (e.g., 512x512 instead of 1024x1024)
- Reduce frame count
- Reduce batch size
- Enable `--lowvram` or `--medvram` flags when starting ComfyUI

### Poor Quality Output
- Increase sampling steps
- Adjust CFG scale
- Use better quality prompts
- Ensure using the correct model checkpoint

### Motion Issues (Image-to-Video)
- Adjust `motion_bucket_id` (higher = more motion)
- Use high-contrast images for better motion detection
- Ensure input image is 1024x576 or scaled appropriately

## Advanced Customization

### Creating Custom Workflows

1. **Start with a template**: Load one of the basic workflows
2. **Modify in GUI**: Add/remove nodes as needed
3. **Test thoroughly**: Generate several videos with different prompts
4. **Export API format**: Use "Save (API Format)" option
5. **Verify node IDs**: Ensure node 6 is your main prompt node
6. **Document changes**: Update this README with new parameters

### Workflow Best Practices

- **Keep node 6 as text prompt**: Required for adapter integration
- **Use meaningful node IDs**: Consistent numbering helps debugging
- **Include reasonable defaults**: Users should get good results out of the box
- **Optimize for production**: Balance quality and generation time
- **Document requirements**: List all required models and custom nodes

## Integration with Video Foundry

The ComfyUI adapter (`workers/ai_worker/adapters/comfyui.py`) automatically:
1. Loads the workflow JSON
2. Injects the user's prompt into node 6
3. Optionally updates width/height in the sampler node
4. Submits to ComfyUI API
5. Polls for completion
6. Retrieves the output video

No code changes needed - just provide the workflow JSON!

## Additional Resources

- [ComfyUI Documentation](https://docs.comfy.org/)
- [AnimateDiff Repository](https://github.com/guoyww/AnimateDiff)
- [Stable Video Diffusion Paper](https://stability.ai/research/stable-video-diffusion-scaling-latent-video-diffusion-models-to-large-datasets)
- [ComfyUI Workflow Examples](https://github.com/comfyanonymous/ComfyUI_examples)

## Contributing

To contribute new workflow templates:
1. Create and test your workflow
2. Export in API format
3. Add to this directory
4. Update this README with usage instructions
5. Document all required models and custom nodes
6. Submit a pull request

---

**Last Updated:** 2025-01-13
**ComfyUI Version:** v0.3.0+
**Maintained by:** Video Foundry Team
