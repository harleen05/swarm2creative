from backend.orchestrator.state import GLOBAL_STATE, HISTORY
from backend.utils.safety import apply_delta
from backend.orchestrator.ws_manager import manager
from art.engine import ART_STATE
from music.engine import MUSIC_STATE
from architecture.engine import ARCH_STATE
from story.engine import STORY_STATE
from anyio import from_thread

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

    try:
        from_thread.run(manager.broadcast, GLOBAL_STATE)
    except RuntimeError:
        pass

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

    if "symmetry_delta" in p:
        ART_STATE["symmetry"] = int(apply_delta(
            ART_STATE.get("symmetry", 4),
            p["symmetry_delta"]["value"],
            p["symmetry_delta"]["confidence"],
            1, 12
        ))

def _apply_music(p):
    if "tempo_shift" in p and p["tempo_shift"]["confidence"] > 0.4:
        MUSIC_STATE["tempo"] = p["tempo_shift"]["value"]

    if "density_shift" in p and p["density_shift"]["confidence"] > 0.4:
        MUSIC_STATE["density"] = p["density_shift"]["value"]

    if "dynamics" in p and p["dynamics"]["confidence"] > 0.4:
        MUSIC_STATE["dynamics"] = p["dynamics"]["value"]

def _apply_architecture(p):
    if "door_attraction_delta" in p:
        ARCH_STATE["door_attraction"] = apply_delta(
            ARCH_STATE.get("door_attraction", 1.0),
            p["door_attraction_delta"]["value"],
            p["door_attraction_delta"]["confidence"],
            0.2, 2.0
        )

    if "room_privacy_shift" in p and p["room_privacy_shift"]["confidence"] > 0.4:
        ARCH_STATE["room_privacy"] = p["room_privacy_shift"]["value"]

    if "spatial_openness_shift" in p and p["spatial_openness_shift"]["confidence"] > 0.4:
        ARCH_STATE["spatial_openness"] = p["spatial_openness_shift"]["value"]

def _apply_story(p):
    if "tone" in p and p["tone"]["confidence"] > 0.4:
        STORY_STATE["tone"] = p["tone"]["value"]

    if "pace_shift" in p and p["pace_shift"]["confidence"] > 0.4:
        STORY_STATE["pace"] = p["pace_shift"]["value"]
