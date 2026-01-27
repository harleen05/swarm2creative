import time
from backend.orchestrator.state import GLOBAL_STATE
from backend.orchestrator.ws_manager import manager
from art.runtime import ART_RUNTIME
from anyio import from_thread

def frame_loop():
    while True:
        frame = ART_RUNTIME.get_frame()
        if frame:
            GLOBAL_STATE["art_frame"] = frame
            try:
                from_thread.run(manager.broadcast, GLOBAL_STATE)
            except RuntimeError:
                pass
        time.sleep(1 / 30)