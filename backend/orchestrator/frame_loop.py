import time
from backend.orchestrator.state import GLOBAL_STATE
from backend.orchestrator.ws_manager import manager
from art.runtime import ART_RUNTIME
from architecture import ARCHITECTURE_RUNTIME
from story.runtime import StoryRuntime
from music.runtime import MusicRuntime
from anyio import from_thread

STORY_RUNTIME = StoryRuntime()
MUSIC_RUNTIME = MusicRuntime()

def detect_collisions(agents_data):
    """Detect collisions between agents for story events"""
    events = []
    if not agents_data:
        return events
    
    COLLISION_THRESHOLD = 10  # pixels
    
    for i, a1 in enumerate(agents_data):
        for j, a2 in enumerate(agents_data[i+1:], start=i+1):
            dx = a1["x"] - a2["x"]
            dy = a1["y"] - a2["y"]
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < COLLISION_THRESHOLD:
                events.append({
                    "frame": STORY_RUNTIME.current_frame,
                    "type": "collision",
                    "info": {"agents": [i, j]}
                })
    
    return events

def frame_loop():
    while True:
        art_frame = ART_RUNTIME.get_frame()
        arch_frame = ARCHITECTURE_RUNTIME.step()

        if art_frame:
            GLOBAL_STATE["art_frame"] = art_frame
            
            # Update music frame based on art frame
            music_frame = MUSIC_RUNTIME.step(art_frame)
            if music_frame:
                GLOBAL_STATE["music_frame"] = music_frame
            
            # Extract events from art frame for story generation
            agents = art_frame.get("agents", [])
            events = detect_collisions(agents)
            
            # Update story frame
            story_frame = STORY_RUNTIME.step(events)
            GLOBAL_STATE["story_frame"] = story_frame

        if arch_frame:
            # Keep the key name aligned with what the frontend expects
            GLOBAL_STATE["architecture"] = arch_frame

        try:
            from_thread.run(manager.broadcast, GLOBAL_STATE)
        except RuntimeError:
            pass

        time.sleep(1 / 30)
