# Swarm2Creative

A multimodal creative system that generates art, architecture, and music through swarm intelligence, with optional AI-powered figurative image generation.

## Features

- **Swarm Art**: Dynamic agent-based visual art with multiple modes (Freeform, Geometric, Mandala)
- **Architecture**: Spatial design visualization with openness, privacy, and circulation controls
- **Music**: Real-time music generation synchronized with art movements
- **Figurative Image Generation**: Generate high-quality images using ComfyUI/Stable Diffusion XL

## Quick Start

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### ComfyUI Integration (Optional - for figurative image generation)

See [COMFYUI_SETUP.md](./COMFYUI_SETUP.md) for detailed setup instructions.

Quick setup:
1. Install ComfyUI: `git clone https://github.com/comfyanonymous/ComfyUI.git`
2. Download SDXL models to `ComfyUI/models/checkpoints/`
3. Start ComfyUI: `python ComfyUI/main.py --port 8188`
4. The backend will automatically connect to ComfyUI at `http://127.0.0.1:8188`

## Usage

1. Open the web interface (typically `http://localhost:5173`)
2. Use the left panel to control:
   - **Art Studio**: Mode, shapes, emotions, and fine adjustments
   - **Architecture Studio**: Spatial parameters and presets
   - **Music Studio**: Music generation controls
3. Click the **Art** icon to see swarm movements
4. Click the **Music** icon to see music visualization
5. Click the **Architecture** icon to see spatial designs
6. Use **Figurative Snapshot** in Art Studio to generate AI images from current state

## Architecture

- `backend/`: FastAPI server with WebSocket support
- `frontend/`: React + Vite frontend
- `art/`: Swarm art engine (boids/flocking algorithms)
- `architecture/`: Spatial design engine
- `music/`: Music generation engine
- `backend/api/image.py`: ComfyUI integration for figurative image generation