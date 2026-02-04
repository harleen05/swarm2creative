from fastapi import APIRouter

from art.runtime import ART_RUNTIME
from art.engine import ART_STATE

from architecture.runtime import ArchitectureRuntime
from music.runtime import MusicRuntime
from story.runtime import StoryRuntime

# instantiate runtimes (singletons)
ARCH_RUNTIME = ArchitectureRuntime()
MUSIC_RUNTIME = MusicRuntime()
STORY_RUNTIME = StoryRuntime()

router = APIRouter()


@router.get("/state")
def get_state():
    from backend.orchestrator.state import GLOBAL_STATE
    
    # Return GLOBAL_STATE directly to match WebSocket broadcast structure
    # This ensures consistency between REST API and WebSocket updates
    art_frame = ART_RUNTIME.get_frame()
    if art_frame:
        GLOBAL_STATE["art_frame"] = art_frame

    # music + story depend on art output
    music_frame = MUSIC_RUNTIME.step(art_frame)
    if music_frame:
        GLOBAL_STATE["music_frame"] = music_frame
    
    # Use existing story_frame from GLOBAL_STATE if available (set by frame_loop initialization)
    # Otherwise generate a new one
    if "story_frame" not in GLOBAL_STATE or not GLOBAL_STATE.get("story_frame"):
        story_frame = STORY_RUNTIME.step(events=[])
        if story_frame:
            GLOBAL_STATE["story_frame"] = story_frame

    architecture_frame = ARCH_RUNTIME.step()
    if architecture_frame:
        GLOBAL_STATE["architecture"] = architecture_frame

    # Return GLOBAL_STATE structure to match what WebSocket broadcasts
    return {
        **GLOBAL_STATE,
        "meta": {
            "art_state": ART_STATE
        }
    }