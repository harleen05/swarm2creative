import time
from backend.orchestrator.state import GLOBAL_STATE
from backend.orchestrator.ws_manager import manager
from art.runtime import ART_RUNTIME
from architecture import ARCHITECTURE_RUNTIME
from anyio import from_thread

def frame_loop():
    while True:
        art_frame = ART_RUNTIME.get_frame()
        arch_frame = ARCHITECTURE_RUNTIME.step()

        if art_frame:
            GLOBAL_STATE["art_frame"] = art_frame

        if arch_frame:
            # Keep the key name aligned with what the frontend expects
            GLOBAL_STATE["architecture"] = arch_frame

        try:
            from_thread.run(manager.broadcast, GLOBAL_STATE)
        except RuntimeError:
            pass

        time.sleep(1 / 30)
