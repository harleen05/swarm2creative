from music.engine import MUSIC_STATE
from music.music_mapper import map_frame_to_notes
import random

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

    def step(self, art_frame):
        if not self.enabled or not art_frame or "agents" not in art_frame:
            return None

        self._tick += 1
        self._phrase_tick += 1

        phase = self._phrase_tick % self._phrase_len
        if phase < 6 or phase > self._phrase_len - 6:
            return None

        notes = map_frame_to_notes(
            art_frame["agents"],
            MUSIC_STATE,
            chord_root=self._chord_root,
            motif=self._motif
        )

        if notes:
            root_candidate = notes[0]["pitch"] % 12
            if self._chord_root is None:
                self._chord_root = root_candidate
            elif self._tick % 120 == 0:
                self._chord_root = random.choice([
                    self._chord_root,
                    root_candidate
                ])
            self._motif_age += 1
            if self._motif_age > 64 or not self._motif:
                self._motif = [n["pitch"] for n in notes[:4]]
                self._motif_age = 0

            if self._drone_pitch is None:
                self._drone_pitch = notes[0]["pitch"]
            else:
                self._drone_pitch = int(
                    self._drone_pitch * 0.98 + notes[0]["pitch"] * 0.02
                )
            notes.append({
                "pitch": self._drone_pitch,
                "velocity": 25,
                "duration": 1.2
            })

        self.last_notes = notes
        if self._tick % 6 != 0:
            return None

        return {
            "notes": notes,
            "meta": MUSIC_STATE.copy()
        }