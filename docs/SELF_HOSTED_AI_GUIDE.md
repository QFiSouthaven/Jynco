# Self-Hosted AI Models Guide

Want to run Video Foundry completely independently without relying on external APIs? This guide shows you how to use self-hosted, open-source AI models.

## Why Self-Host?

✅ **No API costs** - Run unlimited generations
✅ **Full control** - Your data stays on your servers
✅ **No rate limits** - Generate as fast as your hardware allows
✅ **Offline capable** - Works without internet
✅ **Customizable** - Fine-tune models for your needs

## Option 1: Mock Adapter (Built-in, No Setup)

Perfect for testing, demos, and development:

```python
# In your segments, use:
{
  "model": "mock-ai",
  "duration": 5
}
```

✅ Already included
✅ Zero setup
✅ Instant results (2-3 seconds)
✅ No GPU needed

## Option 2: Local Stable Diffusion (Best Quality)

### Requirements
- NVIDIA GPU with 8GB+ VRAM (or Apple Silicon Mac)
- 20GB disk space
- Docker (or Python environment)

### Setup ComfyUI (Easiest)

```bash
# 1. Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download video model
cd models/checkpoints
wget https://huggingface.co/damo-vilab/text-to-video-ms-1.7b/resolve/main/model.safetensors

# 4. Start ComfyUI
cd ../..
python main.py

# ComfyUI now running at http://localhost:8188
```

### Configure Video Foundry

```bash
# In your .env:
LOCAL_SD_URL=http://localhost:8188
LOCAL_SD_OUTPUT_DIR=/path/to/output
```

### Use in Segments

```python
{
  "model": "local-sd",
  "steps": 30,
  "fps": 8,
  "frames": 24
}
```

## Option 3: Hugging Face Diffusers (Python Library)

Run models directly without ComfyUI:

### Install

```bash
pip install diffusers torch transformers accelerate
```

### Models Available

**Text-to-Video:**
- `damo-vilab/text-to-video-ms-1.7b` (1.7B params, good quality)
- `cerspense/zeroscope_v2_576w` (Zeroscope, fast)
- `stabilityai/stable-video-diffusion` (SVD, high quality)

### Integration

The `LocalStableDiffusionAdapter` in Video Foundry supports this:

```python
from diffusers import DiffusionPipeline

# Load model (do this once at startup)
pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16
)
pipe.to("cuda")

# Generate
video = pipe(
    prompt="A cat playing piano",
    num_frames=24,
    num_inference_steps=30
).frames
```

## Option 4: AnimateDiff (High Quality Animations)

### Setup

```bash
# 1. Clone AnimateDiff
git clone https://github.com/guoyww/AnimateDiff.git
cd AnimateDiff

# 2. Install
pip install -r requirements.txt

# 3. Download models
bash download_bashscripts/0-MotionModule.sh
bash download_bashscripts/1-ToonYou.sh

# 4. Run inference
python -m scripts.animate --config configs/prompts/1-ToonYou.yaml
```

### Create Custom Adapter

Similar to the Local SD adapter, create `AnimateDiffAdapter`:

```python
class AnimateDiffAdapter(VideoModelInterface):
    # Call AnimateDiff CLI or Python API
    pass
```

Register in factory:

```python
VideoModelFactory.register_adapter("animatediff", AnimateDiffAdapter)
```

## Option 5: ModelScope (Free Hugging Face Model)

### Quickest Setup

```python
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b"
)

video_frames = pipe(prompt="A dog running on beach").frames
```

✅ Free
✅ No API key
✅ Runs on consumer GPUs
⚠️ Needs 8GB+ VRAM

## Hardware Requirements

### Minimum
- GPU: NVIDIA GTX 1080 (8GB VRAM)
- RAM: 16GB
- Storage: 20GB for models
- Generation time: ~30-60 seconds per 3-second clip

### Recommended
- GPU: NVIDIA RTX 3090 / 4090 (24GB VRAM)
- RAM: 32GB
- Storage: 100GB SSD
- Generation time: ~10-20 seconds per 3-second clip

### Budget Option
- Google Colab (Free tier with GPU)
- Kaggle Notebooks (Free GPU)
- Paperspace Gradient (Free tier)

## Comparing Options

| Model | Quality | Speed | VRAM | Setup Difficulty |
|-------|---------|-------|------|------------------|
| Mock | N/A | Instant | 0GB | ✅ None |
| Local SD | Good | 30-60s | 8GB | ⚠️ Medium |
| AnimateDiff | Great | 60-120s | 12GB | ⚠️ Medium |
| SVD | Excellent | 90-180s | 16GB | ❌ Hard |

## Production Setup

### Docker Compose with GPU

Add GPU support to your AI worker:

```yaml
# docker-compose.yml
ai_worker:
  build:
    context: ./workers/ai_worker
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
```

### Multiple GPUs

Scale workers across GPUs:

```yaml
ai_worker_gpu0:
  environment:
    - CUDA_VISIBLE_DEVICES=0

ai_worker_gpu1:
  environment:
    - CUDA_VISIBLE_DEVICES=1
```

## Cost Comparison

### External APIs (per 1000 videos)

- Runway Gen-3: ~$500-1000
- Stability AI: ~$300-700

### Self-Hosted (one-time + ongoing)

- GPU: $500-2000 (one-time)
- Electricity: ~$20-50/month
- **Total first year**: ~$740-2600
- **Break-even**: After 1-5 months of heavy use

## Recommendations

**For Testing/Demos:**
→ Use **Mock Adapter** (built-in, zero setup)

**For Development:**
→ Use **Local SD + ComfyUI** (good balance)

**For Production:**
→ Use **AnimateDiff** or **SVD** (best quality)

**For Budget:**
→ Use **Hugging Face Spaces** (free GPU hosting)

## No GPU? Cloud Options

### Free Tiers
- Google Colab (15GB GPU, free)
- Kaggle Notebooks (16GB GPU, free)
- Hugging Face Spaces (free inference)

### Paid Options
- RunPod ($0.34/hour for RTX 3090)
- Vast.ai ($0.20/hour for RTX 3080)
- Lambda Labs ($0.50/hour for A100)

## Getting Started Checklist

- [ ] Decide on your model (Mock, Local SD, AnimateDiff)
- [ ] Check hardware requirements
- [ ] Install dependencies
- [ ] Download model weights
- [ ] Test generation locally
- [ ] Integrate with Video Foundry
- [ ] Update docker-compose.yml for GPU
- [ ] Configure .env
- [ ] Test end-to-end workflow

## Next Steps

1. Start with **Mock Adapter** (already works!)
2. Try **Local SD** when ready for real generation
3. Upgrade to **AnimateDiff** for production quality

**Need help?** Open an issue with your setup and we'll help you get running!

---

**Bottom line:** You can run Video Foundry 100% independently with no external API dependencies! 🚀
