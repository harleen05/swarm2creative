import os
import base64
import time
import uuid
from typing import Optional

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from backend.orchestrator.state import GLOBAL_STATE


router = APIRouter()


class ImageRequest(BaseModel):
    prompt: Optional[str] = None


def build_prompt_from_state(user_prompt: Optional[str] = None) -> str:
    """
    Turn the current art / music / architecture state into
    a descriptive text prompt for a generative image model.
    """
    art_meta = GLOBAL_STATE.get("art_frame", {}).get("meta", {}) or {}
    arch = GLOBAL_STATE.get("architecture", {}) or {}
    music_meta = GLOBAL_STATE.get("music_frame", {}).get("meta", {}) or {}

    pieces = []
    if user_prompt:
        pieces.append(user_prompt)

    # high-level mood from art + music
    art_emotion = art_meta.get("emotion") or "neutral"
    music_emotion = music_meta.get("emotion") or "neutral"

    pieces.append(
        f"mood: {art_emotion} art with {music_emotion} music energy"
    )

    # art style
    art_mode = art_meta.get("art_mode") or "abstract swarm"
    symmetry = art_meta.get("symmetry") or 4
    pieces.append(
        f"style: {art_mode}, high symmetry ({symmetry}-fold), flowing neon trails"
    )

    # architecture as spatial context
    openness = arch.get("spatial_openness") or "medium"
    privacy = arch.get("room_privacy") or "medium"
    circulation = arch.get("circulation_style") or "linear"

    pieces.append(
        f"space: {openness} openness, {privacy} privacy, {circulation} circulation"
    )

    # hint that we want figurative objects
    pieces.append(
        "subject: highly detailed figurative illustration, clean anatomy and clear silhouettes, professional photography, sharp focus, 8k uhd"
    )

    return ", ".join(pieces)


def build_comfyui_workflow(prompt: str, negative_prompt: str = "", width: int = 768, height: int = 768, steps: int = 30, cfg_scale: float = 7.0, model_name: str = "sd_xl_base_1.0.safetensors") -> dict:
    """
    Build a ComfyUI workflow JSON for text-to-image generation.
    This creates a simple workflow with CLIP encoding, KSampler, and VAEDecode.
    
    Node structure:
    - Node 1: CheckpointLoaderSimple (loads the model)
    - Node 2: CLIPTextEncode (positive prompt)
    - Node 3: CLIPTextEncode (negative prompt)
    - Node 4: EmptyLatentImage (creates empty latent)
    - Node 5: KSampler (generates latent)
    - Node 6: VAEDecode (decodes to image)
    - Node 7: SaveImage (saves the image)
    """
    
    workflow = {
        "1": {  # CheckpointLoaderSimple (model loader) - must be first
            "inputs": {
                "ckpt_name": model_name
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {  # CLIPTextEncode (positive prompt)
            "inputs": {
                "text": prompt,
                "clip": ["1", 0]  # Reference to checkpoint's CLIP output
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {  # CLIPTextEncode (negative prompt)
            "inputs": {
                "text": negative_prompt or "blurry, low quality, distorted, bad anatomy, watermark, text, signature",
                "clip": ["1", 0]  # Reference to checkpoint's CLIP output
            },
            "class_type": "CLIPTextEncode"
        },
        "4": {  # EmptyLatentImage
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "5": {  # KSampler
            "inputs": {
                "seed": int(time.time()) % 2147483647,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],  # Reference to checkpoint's model output
                "positive": ["2", 0],  # Reference to positive prompt
                "negative": ["3", 0],  # Reference to negative prompt
                "latent_image": ["4", 0]  # Reference to empty latent
            },
            "class_type": "KSampler"
        },
        "6": {  # VAEDecode
            "inputs": {
                "samples": ["5", 0],  # Reference to KSampler output
                "vae": ["1", 2]  # Reference to checkpoint's VAE output
            },
            "class_type": "VAEDecode"
        },
        "7": {  # SaveImage
            "inputs": {
                "filename_prefix": "swarm2creative",
                "images": ["6", 0]  # Reference to VAEDecode output
            },
            "class_type": "SaveImage"
        }
    }
    
    return workflow


def get_available_models(comfyui_url: str) -> Optional[str]:
    """Get first available checkpoint model from ComfyUI."""
    try:
        resp = requests.get(f"{comfyui_url}/object_info", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # ComfyUI returns model list in different formats
            checkpoint_info = data.get("CheckpointLoaderSimple", {})
            if checkpoint_info:
                # Try different possible structures
                ckpt_name_info = checkpoint_info.get("input", {}).get("required", {}).get("ckpt_name", [])
                if isinstance(ckpt_name_info, list) and len(ckpt_name_info) > 0:
                    # Usually it's a list of strings
                    if isinstance(ckpt_name_info[0], str):
                        return ckpt_name_info[0]
                    elif isinstance(ckpt_name_info[0], list) and len(ckpt_name_info[0]) > 0:
                        return ckpt_name_info[0][0]
    except Exception as e:
        print(f"⚠️ Could not fetch available models: {e}")
    return None


def call_comfyui_api(prompt: str, negative_prompt: str = "") -> Optional[str]:
    """
    Call ComfyUI's API to generate an image.
    
    ComfyUI workflow:
    1. POST /prompt with workflow JSON → get prompt_id
    2. Poll /history/{prompt_id} until complete
    3. Download image from ComfyUI's output folder or get base64
    
    Returns base64 PNG data string on success, or None on failure.
    """
    comfyui_url = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
    client_id = str(uuid.uuid4())
    
    # Try to get available models first
    detected_model = get_available_models(comfyui_url)
    model_name = detected_model or "sd_xl_base_1.0.safetensors"  # fallback to default
    print(f"📦 Using model: {model_name}")
    
    # Build workflow with detected model
    workflow = build_comfyui_workflow(prompt, negative_prompt, model_name=model_name)
    
    try:
        # Step 1: Submit the prompt
        submit_url = f"{comfyui_url}/prompt"
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }
        
        # Debug: print workflow structure (first 500 chars)
        import json
        workflow_str = json.dumps(workflow, indent=2)
        print(f"🔍 Sending workflow (first 500 chars):\n{workflow_str[:500]}...")
        
        submit_resp = requests.post(
            submit_url,
            json=payload,
            timeout=10
        )
        
        # Better error reporting
        if submit_resp.status_code != 200:
            error_text = submit_resp.text
            print(f"⚠️ ComfyUI API error {submit_resp.status_code}: {error_text}")
            try:
                error_json = submit_resp.json()
                print(f"⚠️ Error details: {json.dumps(error_json, indent=2)}")
            except:
                pass
            # Also print the full workflow for debugging
            print(f"🔍 Full workflow sent:\n{workflow_str}")
            return None
        
        submit_resp.raise_for_status()
        submit_data = submit_resp.json()
        prompt_id = submit_data.get("prompt_id")
        
        if not prompt_id:
            print("⚠️ ComfyUI: No prompt_id returned")
            print(f"⚠️ Response: {submit_data}")
            return None
        
        print(f"✅ ComfyUI: Prompt submitted, prompt_id={prompt_id}")
        
        # Step 2: Poll for completion (check history)
        max_wait = 120  # 2 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(2)  # Poll every 2 seconds
            
            history_url = f"{comfyui_url}/history/{prompt_id}"
            history_resp = requests.get(history_url, timeout=5)
            
            if history_resp.status_code == 200:
                history_data = history_resp.json()
                
                # Check if prompt is complete
                if prompt_id in history_data:
                    output_data = history_data[prompt_id]
                    outputs = output_data.get("outputs", {})
                    
                    # Find the SaveImage node output
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            images = node_output["images"]
                            if images and len(images) > 0:
                                # Get the image filename
                                image_info = images[0]
                                filename = image_info.get("filename", "")
                                subfolder = image_info.get("subfolder", "")
                                
                                # Step 3: Download the image
                                image_url = f"{comfyui_url}/view"
                                params = {
                                    "filename": filename,
                                    "subfolder": subfolder,
                                    "type": "output"
                                }
                                
                                img_resp = requests.get(image_url, params=params, timeout=10)
                                if img_resp.status_code == 200:
                                    # Convert to base64
                                    img_b64 = base64.b64encode(img_resp.content).decode('utf-8')
                                    print(f"✅ ComfyUI: Image generated successfully")
                                    return img_b64
                    
                    # Still processing
                    continue
            
            # Check queue status
            queue_url = f"{comfyui_url}/queue"
            queue_resp = requests.get(queue_url, timeout=5)
            if queue_resp.status_code == 200:
                queue_data = queue_resp.json()
                # Check if our prompt is still in queue
                queue_running = queue_data.get("queue_running", [])
                queue_pending = queue_data.get("queue_pending", [])
                
                found = False
                for item in queue_running + queue_pending:
                    if item[1] == prompt_id:
                        found = True
                        break
                
                if not found:
                    # Not in queue anymore, check history one more time
                    continue
        
        print("⚠️ ComfyUI: Timeout waiting for image generation")
        return None
        
    except Exception as e:
        print(f"⚠️ ComfyUI API error: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.post("/generate-image")
def generate_image(payload: ImageRequest):
    """
    Generate a figurative image using the current multimodal state
    (art / music / architecture) as conditioning for ComfyUI.
    """
    prompt = build_prompt_from_state(payload.prompt)
    image_b64 = call_comfyui_api(prompt)

    return {
        "prompt": prompt,
        "image_base64": image_b64,
    }


