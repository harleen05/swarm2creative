# art/runtime.py
import time
import threading
from art.engine import Agent, get_frame_state, ART_STATE

class ArtRuntime:
    def __init__(self, agent_count=50):
        self.agents = [Agent() for _ in range(agent_count)]
        self.running = False
        self.thread = None
        self.frame = None
        self.t = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        while self.running:
            paused = ART_STATE.get("paused", False)
            for agent in self.agents:
                if paused:
                    agent.vel *= 0.90
                else:
                    agent.apply_behaviors(self.agents, self.t, ART_STATE)
                    agent.update()

            self.frame = get_frame_state(self.agents)
            self.t += 0.01
            time.sleep(1 / 60)

    def get_frame(self):
        return self.frame

ART_RUNTIME = ArtRuntime()