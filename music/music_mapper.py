# music_mapper.py
import math
from mido import Message, MidiFile, MidiTrack, MetaMessage
import random

WIDTH = 900
SCALE = [60, 62, 64, 65, 67, 69, 71]
SCALES = {
    "calm":    [60, 62, 64, 67, 69],
    "neutral": [60, 62, 64, 65, 67, 69, 71],
    "tense":   [60, 61, 63, 66, 68],
    "dark":    [60, 63, 65, 66, 68]
}

class SwarmMusicMapper:
    def __init__(self):
        self.mid = MidiFile()
        self.melody = MidiTrack()
        self.mid.tracks.append(self.melody)
        self.melody.append(Message('program_change', program=48, time=0))
        self.bass = MidiTrack()
        self.mid.tracks.append(self.bass)
        self.bass.append(Message('program_change', program=32, time=0))

        self.last_pitch = None
        self.frame_count = 0
        self.base_tempo = 500000
        self.current_tempo = self.base_tempo
        self.melody.append(
            MetaMessage('set_tempo', tempo=self.base_tempo, time=0)
        )

    def speed(self, vel):
        return math.sqrt(vel[0] ** 2 + vel[1] ** 2)

    def compute_swarm_energy(self, frame):
        return sum(self.speed(a['vel']) for a in frame) / len(frame)

    def energy_to_tempo(self, energy):
        bpm = 60 + energy * 20
        bpm = max(60, min(140, bpm))
        return int(60_000_000 / bpm)

    def melody_notes(self, frame):
        notes = []
        for agent in frame:
            x, _ = agent['pos']
            vel = agent['vel']

            idx = int((x / WIDTH) * len(SCALE))
            idx = min(idx, len(SCALE) - 1)
            target = 60 + int((x / WIDTH) * 24)

            if last_pitch is None:
                pitch = target
            else:
                delta = target - last_pitch
                pitch = last_pitch + max(-2, min(2, delta))

            if state is not None:
                state["_last_pitch"] = pitch

            volume = int(min(127, self.speed(vel) * 40))
            notes.append((pitch, volume))

        return sorted(notes, key=lambda n: n[1], reverse=True)

    # ---------------- BASS ----------------

    def bass_note(self, frame):
        avg_x = sum(a['pos'][0] for a in frame) / len(frame)
        idx = int((avg_x / WIDTH) * len(SCALE))
        idx = min(idx, len(SCALE) - 1)
        return SCALE[idx] - 24


    def add_frame(self, frame):
        self.frame_count += 1
        energy = self.compute_swarm_energy(frame)
        tempo = self.energy_to_tempo(energy)

        if tempo != self.current_tempo:
            self.melody.append(
                MetaMessage('set_tempo', tempo=tempo, time=0)
            )
            self.current_tempo = tempo

        duration = int(100 + energy * 30)
        melody = self.melody_notes(frame)[:3]
        for pitch, volume in melody:
            self.melody.append(
                Message('note_on', note=pitch, velocity=volume, time=0)
            )
            self.melody.append(
                Message('note_off', note=pitch, velocity=64, time=duration)
            )

        if self.frame_count % 8 == 0:
            bass_pitch = self.bass_note(frame)

            self.bass.append(
                Message('note_on', note=bass_pitch, velocity=70, time=0)
            )
            self.bass.append(
                Message('note_off', note=bass_pitch, velocity=64, time=duration * 4)
            )

    def save(self, filename="swarm_music.mid"):
        self.mid.save(filename)

EMOTION_WEIGHTS = {
    "calm": 0.1,
    "neutral": 0.2,
    "tense": 0.4,
    "dark": 0.45,
    "hopeful": 0.15
}

HARMONIC_GRAVITY = {
    "static": 0.0,
    "slow": 0.15,
    "drifting": 0.35
}

def map_frame_to_notes(agents, state=None, chord_root=None, motif=None, max_notes=6):
    import math, random

    if state is None:
        state = {}

    emotion = state.get("emotion", "neutral")
    rhythm = state.get("rhythm_style", "ambient")
    energy_curve = state.get("energy_curve", "flat")
    density = state.get("density", 0.5)
    dynamics = state.get("dynamics", 0.5)
    motif = state.get("motif", None)

    use_motif = motif and random.random() < 0.65
    call_phase = state.setdefault("_call_phase", 0)
    state["_call_phase"] = (call_phase + 1) % 8
    is_call = call_phase < 4

    scale = SCALES.get(emotion, SCALES["neutral"])
    harmonic_motion = state.get("harmonic_motion", "static")
    gravity = EMOTION_WEIGHTS.get(emotion, 0.25) + HARMONIC_GRAVITY.get(harmonic_motion, 0)
    notes = []

    if chord_root is None:
        chord_root = scale[0] % 12

    chord = [
        chord_root,
        (chord_root + 4) % 12,
        (chord_root + 7) % 12
    ]

    beat_offsets = [0, 0.25, 0.5, 0.75]

    for i, agent in enumerate(agents):
        if random.random() > density:
            continue

        x = agent["x"]
        trail = agent.get("trail", [])

        if len(trail) >= 2:
            (x1, y1), (x2, y2) = trail[-2], trail[-1]
            energy = math.hypot(x2 - x1, y2 - y1)
        else:
            energy = 0

        base = 60 
        if use_motif:
            pitch = motif[i % len(motif)]
        else:
            degree = chord[i % len(chord)]
            pitch = base + degree

        if random.random() < gravity:
            pitch += random.choice([-1, 1])

        if is_call:
            velocity = int(55 + energy * 45 * dynamics)
        else:
            velocity = int(35 + energy * 30 * dynamics)

        if rhythm == "ambient":
            duration = random.uniform(0.6, 1.2)
        elif rhythm == "pulse":
            duration = 0.25
        elif rhythm == "groove":
            duration = random.choice([0.25, 0.25, 0.5])

        if len(notes) >= max_notes:
            break

        if energy_curve == "rising":
            velocity = int(velocity * (0.7 + i / max_notes))
        elif energy_curve == "falling":
            velocity = int(velocity * (1.2 - i / max_notes))
        elif energy_curve == "waves":
            velocity = int(velocity * (0.6 + 0.4 * math.sin(i)))

        velocity = max(20, min(100, velocity))

        notes.append({
            "pitch": pitch,
            "velocity": velocity,
            "duration": duration
        })

        if len(notes) >= max_notes:
            break

    notes = sorted(notes, key=lambda n: n["velocity"], reverse=True)
    return notes[:max_notes]