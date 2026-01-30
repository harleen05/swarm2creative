# ComfyUI Integration Setup Guide

This guide will help you set up ComfyUI to work with Swarm2Creative's figurative image generation feature.

## Prerequisites

1. **Python 3.10+** (ComfyUI requirement)
2. **Git** (to clone ComfyUI)
3. **CUDA-capable GPU** (recommended, but CPU works too)

## Step 1: Install ComfyUI

```bash
# Clone ComfyUI repository
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

## Step 2: Download SDXL Models

ComfyUI needs model files to generate images. For SDXL (recommended):

```bash
cd ComfyUI/models/checkpoints
# Download SDXL base model (you'll need to get this from HuggingFace or Stability AI)
# Place it as: sd_xl_base_1.0.safetensors
```

**Quick download options:**
- Visit https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- Download `sd_xl_base_1.0.safetensors` to `ComfyUI/models/checkpoints/`

You may also need the VAE:
```bash
cd ComfyUI/models/vae
# Download sdxl_vae.safetensors from the same HuggingFace repo
```

## Step 3: Start ComfyUI Server

```bash
cd ~/ComfyUI
python main.py --port 8188
```

ComfyUI should now be running at `http://127.0.0.1:8188`

You can verify by opening `http://127.0.0.1:8188` in your browser - you should see the ComfyUI interface.

## Step 4: Configure Swarm2Creative Backend

Set the environment variable (or add to your `.env` file if you use one):

```bash
export COMFYUI_URL="http://127.0.0.1:8188"
```

**Note:** The backend defaults to `http://127.0.0.1:8188` if `COMFYUI_URL` is not set, so this step is optional if ComfyUI runs on the default port.

## Step 5: Test the Integration

1. Start your Swarm2Creative backend:
   ```bash
   cd /path/to/swarm2creative
   uvicorn backend.main:app --reload --port 8000
   ```

2. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. In the UI:
   - Open the **Art Studio** panel
   - Scroll to **Figurative Snapshot** section
   - Click **Generate Figurative Image**
   - Wait for the image to generate (may take 30-60 seconds)
   - The image should auto-download as `figurative_snapshot.png`

## Troubleshooting

### ComfyUI won't start
- Check if port 8188 is already in use: `lsof -i :8188`
- Try a different port: `python main.py --port 8189` (then set `COMFYUI_URL=http://127.0.0.1:8189`)

### "Model not found" errors
- Make sure `sd_xl_base_1.0.safetensors` is in `ComfyUI/models/checkpoints/`
- Check the filename matches exactly (case-sensitive)

### Image generation times out
- GPU generation is much faster than CPU
- Increase timeout in `backend/api/image.py` if needed (currently 120 seconds)
- Check ComfyUI logs for errors

### Wrong model name in workflow
If your ComfyUI uses a different model name, edit `backend/api/image.py`:
- Find the `CheckpointLoaderSimple` node in `build_comfyui_workflow()`
- Change `"ckpt_name": "sd_xl_base_1.0.safetensors"` to your model's filename

## Advanced: Custom Workflows

The current implementation uses a simple workflow. You can customize it in `backend/api/image.py`:
- Modify `build_comfyui_workflow()` to add ControlNet, LoRA, or other nodes
- Adjust sampler settings (steps, CFG scale, etc.)
- Change image dimensions

## Alternative: Use ComfyUI's Web UI

You can also manually create workflows in ComfyUI's web interface and save them as JSON, then load them programmatically. This gives you full control over the generation pipeline.

