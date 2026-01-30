import architecture.engine as ARCH
from architecture.engine import ARCH_STATE
from backend.orchestrator.state import GLOBAL_STATE

class ArchitectureRuntime:
    def __init__(self):
        self.enabled = True
    
    def step(self):
        if not self.enabled:
            return None

        frame = {
            "rooms": [],
            "edges": [],
            # expose current intent parameters so the frontend
            # can render and display them directly
            "spatial_openness": ARCH_STATE.get("spatial_openness"),
            "room_privacy": ARCH_STATE.get("room_privacy"),
            "circulation_style": ARCH_STATE.get("circulation_style"),
        }

        # rooms (adapt keys if names differ)
        for r in getattr(ARCH, "ROOMS", []):
            frame["rooms"].append({
                "id": r.get("id"),
                "x": r["x"],
                "y": r["y"],
                "w": r["w"],
                "h": r["h"],
                "type": r.get("type", "public")
            })

        # circulation / connections
        for e in getattr(ARCH, "EDGES", []):
            frame["edges"].append({
                "from": e["from"],
                "to": e["to"]
            })
        GLOBAL_STATE["architecture"] = frame
        return frame