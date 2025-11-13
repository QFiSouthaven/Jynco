FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# Install Python dependencies
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir -r requirements.txt

# Create directories for models, input, and output
RUN mkdir -p models/checkpoints models/vae models/loras input output

# Expose port
EXPOSE 8188

# Run ComfyUI
CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
