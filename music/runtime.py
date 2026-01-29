from music.engine import MUSIC_STATE
from music.music_mapper import map_frame_to_notes
import random
import math

HARMONIC_MOTION_PROB = {
    "static": 0.0,
    "slow": 0.15,
    "drifting": 0.35
}

PROGRESSIONS = {
    "calm":      [0, 5, 7, 0],
    "hopeful":   [0, 5, 9, 7],
    "tense":     [0, 1, 6, 7],
    "dark":      [0, 3, 5, 6],
    "neutral":   [0, 5, 7, 9]
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
        self._harmony_step = 0
        self._harmony_root = random.choice([0, 2, 4, 5, 7, 9])
        self._chord_root = self._harmony_root

    def step(self, art_frame):
        if not self.enabled or not art_frame or "agents" not in art_frame:
            return None

        self._tick += 1
        if self._tick % (self._steps_per_beat * self._beats_per_bar) == 0:
            self._bar += 1

        self._phrase_tick += 1

        if self._tick % (self._steps_per_beat * 8) == 0:
            emotion = MUSIC_STATE.get("emotion", "neutral")
            progression = PROGRESSIONS.get(emotion, PROGRESSIONS["neutral"])

            interval = progression[self._harmony_step % len(progression)]
            self._chord_root = (self._harmony_root + interval) % 12
            self._harmony_root = self._chord_root
            if self._harmony_step % 4 == 0:
                self._harmony_root = (self._harmony_root + random.choice([2, 5, 7])) % 12
            self._harmony_step += 1
        
        if self._tick % (self._steps_per_beat * 8) == 0:
            curve = MUSIC_STATE.get("energy_curve", "flat")

            if curve == "rising":
                MUSIC_STATE["density"] = min(1.0, MUSIC_STATE["density"] + 0.05)
            elif curve == "falling":
                MUSIC_STATE["density"] = max(0.2, MUSIC_STATE["density"] - 0.05)
            elif curve == "waves":
                MUSIC_STATE["density"] = 0.4 + 0.3 * math.sin(self._tick * 0.01)

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
            self._motif_age += 1
            if self._motif_age > 64 or not self._motif:
                self._motif = [n["pitch"] for n in notes[:4]]
                self._motif_age = 0

            root_pitch = self._chord_root
            if root_pitch is None:
                root_pitch = notes[0]["pitch"] % 12

            target_bass = 36 + root_pitch

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
            "chord": self._chord_root,
            "meta": MUSIC_STATE.copy()
        }