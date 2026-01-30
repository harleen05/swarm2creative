from backend.orchestrator.state import GLOBAL_STATE, HISTORY
from backend.utils.safety import apply_delta
from backend.orchestrator.ws_manager import manager
from art.engine import ART_STATE
from music.engine import MUSIC_STATE
from architecture.engine import ARCH_STATE
from story.engine import STORY_STATE
from anyio import from_thread
import art.engine as engine
from art.runtime import ART_RUNTIME
import random
import math
import pygame
from music.runtime import MusicRuntime
from architecture.engine import ARCH_STATE
from backend.orchestrator.state import GLOBAL_STATE
from backend.orchestrator.frame_loop import STORY_RUNTIME
MUSIC_RUNTIME = MusicRuntime()

def apply_parameters(params):
    HISTORY.append(params)

    if "art" in params:
        _apply_art(params["art"])

    if "music" in params:
        _apply_music(params["music"])

    if "architecture" in params:
        _apply_architecture(params["architecture"])

    if "story" in params:
        _apply_story(params["story"])

    frame = ART_RUNTIME.get_frame()
    if frame:
        GLOBAL_STATE["art_frame"] = frame

        music_frame = MUSIC_RUNTIME.step(frame)
        if music_frame:
            GLOBAL_STATE["music_frame"] = music_frame

    # Story frame is now updated in frame_loop.py

def _apply_art(p):
    if "emotion" in p:
        if p["emotion"]["confidence"] > 0.4:
            ART_STATE["emotion"] = p["emotion"]["value"]

    if "flow_noise_delta" in p:
        ART_STATE["flow_noise"] = apply_delta(
            ART_STATE.get("flow_noise", 0.02),
            p["flow_noise_delta"]["value"],
            p["flow_noise_delta"]["confidence"],
            0.001, 0.1
        )
        ART_STATE["paused"] = False

    if "symmetry_delta" in p:
        ART_STATE["symmetry"] = int(apply_delta(
            ART_STATE.get("symmetry", 4),
            p["symmetry_delta"]["value"],
            p["symmetry_delta"]["confidence"],
            1, 12
        ))
    if "shape" in p:
        ART_STATE["shape"] = p["shape"]["value"]

        for agent in ART_RUNTIME.agents:
            agent.history.clear()
            if hasattr(agent, "_shape_mem"):
                agent._shape_mem["star_target"] = None
                agent._shape_mem["star_timer"] = 0

    if "paused" in p:
        ART_STATE["paused"] = p["paused"]["value"]

    if "art_mode" in p:
        ui_mode = p["art_mode"]["value"]
        MODE_MAP = {
            "freeform": "chaos",
            "geometric": "flow",
            "mandala": "composition"
        }
        ART_STATE["art_mode"] = MODE_MAP.get(ui_mode, "chaos")
        ART_STATE["paused"] = False
        for agent in ART_RUNTIME.agents:
            angle = random.uniform(0, 2 * math.pi)
            agent.vel = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
            ) * random.uniform(0.6, 1.2)

            agent.history.clear()
            if hasattr(agent, "_shape_mem"):
                agent._shape_mem["star_target"] = None
                agent._shape_mem["star_timer"] = 0

def _apply_music(p):
    if "tempo_shift" in p and p["tempo_shift"]["confidence"] > 0.4:
        tempo_value = p["tempo_shift"]["value"]
        # Handle string values like "fast", "slow", "moderate"
        if isinstance(tempo_value, str):
            tempo_map = {"fast": 150, "moderate": 120, "slow": 80, "very fast": 180, "very slow": 60}
            MUSIC_STATE["tempo"] = tempo_map.get(tempo_value.lower(), 120)
        # Handle numeric values (absolute BPM or relative delta)
        elif isinstance(tempo_value, (int, float)):
            # If it's a reasonable BPM value (60-200), use it directly
            if 60 <= tempo_value <= 200:
                MUSIC_STATE["tempo"] = int(tempo_value)
            # Otherwise, treat as delta and add to current tempo
            else:
                MUSIC_STATE["tempo"] = max(60, min(200, MUSIC_STATE.get("tempo", 120) + int(tempo_value)))

    if "density_shift" in p and p["density_shift"]["confidence"] > 0.4:
        MUSIC_STATE["density"] = p["density_shift"]["value"]

    if "dynamics" in p and p["dynamics"]["confidence"] > 0.4:
        MUSIC_STATE["dynamics"] = p["dynamics"]["value"]

    if "music_intent" in p:
        intent = p["music_intent"]

        if "mood" in intent and intent["mood"]["confidence"] > 0.4:
            MUSIC_STATE["emotion"] = intent["mood"]["value"]

        if "rhythm_style" in intent and intent["rhythm_style"]["confidence"] > 0.4:
            MUSIC_STATE["rhythm_style"] = intent["rhythm_style"]["value"]

        if "energy_curve" in intent and intent["energy_curve"]["confidence"] > 0.4:
            MUSIC_STATE["energy_curve"] = intent["energy_curve"]["value"]

        if "harmonic_motion" in intent and intent["harmonic_motion"]["confidence"] > 0.4:
            MUSIC_STATE["harmonic_motion"] = intent["harmonic_motion"]["value"]
    
    if "melody_enabled" in p:
        MUSIC_STATE["melody_enabled"] = p["melody_enabled"]["value"]

    if "bass_enabled" in p:
        MUSIC_STATE["bass_enabled"] = p["bass_enabled"]["value"]

    if "rhythm_intensity" in p and p["rhythm_intensity"]["confidence"] > 0.4:
        MUSIC_STATE["rhythm_intensity"] = p["rhythm_intensity"]["value"]

def _apply_architecture(p):
    if "architecture_intent" in p:
        intent = p["architecture_intent"]

        if "spatial_openness" in intent:
            ARCH_STATE["spatial_openness"] = intent["spatial_openness"]["value"]

        if "room_privacy" in intent:
            ARCH_STATE["room_privacy"] = intent["room_privacy"]["value"]

        if "circulation_style" in intent:
            ARCH_STATE["circulation_style"] = intent["circulation_style"]["value"]

def _apply_story(p):
    if "tone" in p and p["tone"]["confidence"] > 0.4:
        STORY_STATE["tone"] = p["tone"]["value"]

    if "pace_shift" in p and p["pace_shift"]["confidence"] > 0.4:
        STORY_STATE["pace"] = p["pace_shift"]["value"]
    
    if "mood" in p and p["mood"]["confidence"] > 0.4:
        STORY_STATE["mood"] = p["mood"]["value"]