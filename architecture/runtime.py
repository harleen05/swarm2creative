import architecture.engine as ARCH
from backend.orchestrator.state import GLOBAL_STATE

class ArchitectureRuntime:
    def __init__(self):
        self.enabled = True

    def step(self):
        if not self.enabled:
            return None

        frame = {
            "rooms": [],
            "edges": []
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