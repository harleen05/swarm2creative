from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.orchestrator.controller import apply_parameters
from backend.orchestrator.ws_manager import manager
from backend.orchestrator.state import GLOBAL_STATE
from backend.llm.interpreter import interpret_prompt

from art.runtime import ART_RUNTIME
from art.engine import ART_STATE

from architecture.runtime import ArchitectureRuntime
from music.runtime import MusicRuntime
from story.runtime import StoryRuntime

ARCH_RUNTIME = ArchitectureRuntime()
MUSIC_RUNTIME = MusicRuntime()
STORY_RUNTIME = StoryRuntime()

router = APIRouter()


class Intent(BaseModel):
    art: Optional[dict] = None
    music: Optional[dict] = None
    architecture: Optional[dict] = None
    story: Optional[dict] = None


class TextPrompt(BaseModel):
    text: str


@router.post("/chat")
async def chat(payload: TextPrompt):
    """
    Accept text input from user, interpret it using LLM, and apply the resulting intent.
    """
    print(f"💬 Received user prompt: {payload.text}")
    
    # Use LLM to interpret the text into structured intent
    try:
        intent = interpret_prompt(payload.text)
        print(f"🤖 LLM interpreted intent: {intent}")
        
        if not intent:
            print("⚠️ LLM returned empty intent, using fallback")
            return {"status": "error", "message": "Could not interpret prompt"}
        
        # Apply the interpreted intent
        apply_parameters(intent)
        
        # Generate updated frames
        art_frame = ART_RUNTIME.get_frame()
        if art_frame:
            GLOBAL_STATE["art_frame"] = art_frame
        
        music_frame = MUSIC_RUNTIME.step(art_frame)
        if music_frame:
            GLOBAL_STATE["music_frame"] = music_frame
        
        story_frame = STORY_RUNTIME.step(events=[])
        if story_frame:
            GLOBAL_STATE["story_frame"] = story_frame
        
        architecture_frame = ARCH_RUNTIME.step()
        if architecture_frame:
            GLOBAL_STATE["architecture"] = architecture_frame

        # Broadcast GLOBAL_STATE to match what frame_loop broadcasts
        snapshot = {
            **GLOBAL_STATE,
            "meta": {
                "art_state": ART_STATE
            }
        }

        try:
            await manager.broadcast(snapshot)
        except Exception as e:
            print("WS broadcast failed:", e)

        return {"status": "ok", "intent": intent}
        
    except Exception as e:
        print(f"⚠️ Error interpreting prompt: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@router.post("/interpret")
async def interpret(payload: Intent):
    """
    Accept structured intent directly (for programmatic use).
    """
    data = payload.dict(exclude_none=True)

    # Update intent parameters (ART_STATE, MUSIC_STATE, etc.)
    apply_parameters(data)

    art_frame = ART_RUNTIME.get_frame()
    if art_frame:
        GLOBAL_STATE["art_frame"] = art_frame
    
    music_frame = MUSIC_RUNTIME.step(art_frame)
    if music_frame:
        GLOBAL_STATE["music_frame"] = music_frame
    
    story_frame = STORY_RUNTIME.step(events=[])
    if story_frame:
        GLOBAL_STATE["story_frame"] = story_frame
    
    architecture_frame = ARCH_RUNTIME.step()
    if architecture_frame:
        GLOBAL_STATE["architecture"] = architecture_frame

    # Broadcast GLOBAL_STATE to match what frame_loop broadcasts
    # This ensures consistency across all WebSocket updates
    snapshot = {
        **GLOBAL_STATE,
        "meta": {
            "art_state": ART_STATE
        }
    }

    try:
        await manager.broadcast(snapshot)
    except Exception as e:
        print("WS broadcast failed:", e)

    return {"status": "ok"}