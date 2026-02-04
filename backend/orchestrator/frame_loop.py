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
    # Initialize story on startup - always provide SOMETHING
    print("🚀 Initializing story on startup...")
    
    # Start with a guaranteed fallback
    GLOBAL_STATE["story_frame"] = {
        "paragraphs": [
            {"type": "header", "content": "🌱 THE AWAKENING"},
            {"type": "paragraph", "content": "In the depths of digital space, a swarm begins to stir. Autonomous agents, each with their own simple rules, start to move and interact. What emerges from their collective behavior is far greater than the sum of their parts."},
            {"type": "paragraph", "content": "Watch as they create art through motion, compose music through harmony, design architecture through spatial relationships, and weave stories through their encounters. This is emergence in action."},
            {"type": "paragraph", "content": "The journey begins now. Each agent follows its path, unaware of the greater patterns forming. Yet together, they paint, they sing, they build, they tell tales of digital life."}
        ],
        "meta": {
            "tone": "neutral",
            "mood": "hopeful",
            "pace": "moderate",
            "total_events": 0,
            "current_frame": 0
        },
        "phase": "introduction",
        "story_events": [],
        "enhanced": False
    }
    print("✅ Fallback story initialized")
    
    # Try to enhance with LLM in background (non-blocking)
    try:
        from backend.api.story import enhance_story_with_llm
        print("🤖 Attempting LLM enhancement...")
        
        enhanced = enhance_story_with_llm(
            story_events=[],
            tone="neutral",
            pace="moderate", 
            mood="hopeful",
            word_limit=500,
            paragraph_count=5,
            user_prompt="Create an engaging introduction to a digital swarm simulation where autonomous agents create art, music, architecture, and stories through emergent behavior.",
            base_story=None
        )
        
        if enhanced and enhanced.get("paragraphs") and len(enhanced["paragraphs"]) > 2:
            GLOBAL_STATE["story_frame"]["paragraphs"] = enhanced["paragraphs"]
            GLOBAL_STATE["story_frame"]["enhanced"] = True
            print(f"✅ LLM enhancement successful: {len(enhanced['paragraphs'])} paragraphs")
        else:
            print("⚠️ LLM returned insufficient content, keeping fallback")
    except Exception as e:
        print(f"⚠️ LLM enhancement failed: {e}")
        print("✅ Using fallback story (this is fine!)")
    
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

