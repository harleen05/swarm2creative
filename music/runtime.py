from music.engine import MUSIC_STATE
from music.music_mapper import map_frame_to_notes
import random

HARMONIC_MOTION_PROB = {
    "static": 0.0,
    "slow": 0.15,
    "drifting": 0.35
}

CHORD_INTERVALS = [0, 5, 7, -5]

class MusicRuntime:
    def __init__(self):
        self.enabled = True
        self.last_notes = []
        self._tick = 0
        self._chord_root = None
        self._phrase_len = 32
        self._phrase_tick = 0
        self._motif = []
        self._motif_age = 0
        self._drone_pitch = None
        self._bar = 0
        self._beats_per_bar = 4
        self._steps_per_beat = 6
        self._bass_pitch = None

    def step(self, art_frame):
        if not self.enabled or not art_frame or "agents" not in art_frame:
            return None

        self._tick += 1
        if self._tick % (self._steps_per_beat * self._beats_per_bar) == 0:
            self._bar += 1

        self._phrase_tick += 1

        phase = self._phrase_tick % self._phrase_len
        if phase < 6 or phase > self._phrase_len - 6:
            return None

        state = MUSIC_STATE.copy()
        state["density"] *= MUSIC_STATE.get("rhythm_intensity", 1.0)

        notes = map_frame_to_notes(
            art_frame["agents"],
            state,
            chord_root=self._chord_root,
            motif=self._motif
        )

        if notes:
            root_candidate = notes[0]["pitch"] % 12
            if self._chord_root is None:
                self._chord_root = root_candidate
            else:
                motion = MUSIC_STATE.get("harmonic_motion", "static")
                prob = HARMONIC_MOTION_PROB.get(motion, 0)

                if self._bar > 0 and self._bar % random.choice([8, 12, 16]) == 0:
                    if random.random() < prob:
                        interval = random.choice(CHORD_INTERVALS)
                        self._chord_root = (self._chord_root + interval) % 12

            self._motif_age += 1
            if self._motif_age > 64 or not self._motif:
                self._motif = [n["pitch"] for n in notes[:4]]
                self._motif_age = 0

            root_pitch = (self._chord_root or notes[0]["pitch"] % 12)
            target_bass = 36 + root_pitch  # C2 range

            if self._bass_pitch is None:
                self._bass_pitch = target_bass
            else:
                self._bass_pitch = int(self._bass_pitch * 0.97 + target_bass * 0.03)
            
            for n in notes:
                n.setdefault("layer", "melody")

            notes.append({
                "pitch": self._bass_pitch,
                "velocity": 18,
                "duration": 1.8,
                "layer": "bass"
            })

        filtered = []
        for n in notes:
            if n.get("layer") == "bass" and not MUSIC_STATE.get("bass_enabled", True):
                continue
            if n.get("layer") != "bass" and not MUSIC_STATE.get("melody_enabled", True):
                continue
            filtered.append(n)
        notes = filtered

        self.last_notes = notes
        if self._tick % 6 != 0:
            return None

        return {
            "notes": notes,
            "meta": MUSIC_STATE.copy()
        }