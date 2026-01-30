from collections import defaultdict
import random

# ---------------------------
# Agent Names
# ---------------------------
AGENT_NAMES_LIST = [
    "Astra","Blip","Cleo","Dax","Echo","Fizz","Glim","Haze",
    "Iris","Juno","Kip","Luna","Milo","Nova","Orin","Pip",
    "Quinn","Rex","Sage","Tess","Uma","Vex","Wren","Xan",
    "Yara","Zed","Faye","Nico","Rina","Taro","Zara","Leo",
    "Mara","Koda","Vira","Eli","Ryo","Lina","Sora","Kai",
    "Jace","Naya","Rex","Fia","Zeno","Aya","Tia","Rem","Lio","Zia",
]

NUM_AGENTS = 60  
AGENT_NAMES = {i: AGENT_NAMES_LIST[i % len(AGENT_NAMES_LIST)] for i in range(NUM_AGENTS)}

# ---------------------------
# Story Mapper
# ---------------------------
class StoryMapper:
    def __init__(self):
        self.story_events = []
        self.relationships = defaultdict(int)
        self.proximity_tracker = defaultdict(int)
        self.last_seen_frame = {}
        self.formed_alliances = set()
        self.ALLIANCE_THRESHOLD = 20  # frames for alliance formation

    # Determine story phase
    def _get_phase(self, frame, total_frames):
        if frame < total_frames * 0.3:
            return "introduction"
        elif frame < total_frames * 0.7:
            return "rising_conflict"
        else:
            return "climax"

    # Process events
    def process_event(self, event, total_frames):
        frame = event.get("frame")
        etype = event.get("type")
        agents = event.get("info", {}).get("agents", [])

        phase = self._get_phase(frame, total_frames)

        # ---- Collisions: Tension → Conflict → Rivalry ----
        if etype == "collision" and len(agents) == 2:
            pair = tuple(sorted(agents))
            self.relationships[pair] += 1
            count = self.relationships[pair]

            if count == 1:
                story_type = "tension"
            elif count < 4:
                story_type = "conflict"
            else:
                story_type = "rivalry"

            self.story_events.append({
                "frame": frame,
                "event_type": "collision",
                "agents": pair,
                "story_type": story_type,
                "phase": phase,
                "intensity": count
            })

        # ---- Proximity: Alliance ----
        if etype == "proximity" and len(agents) >= 3:
            group = tuple(sorted(agents))
            last_frame = self.last_seen_frame.get(group, -1)

            if frame != last_frame + 1:
                self.proximity_tracker[group] = 1
            else:
                self.proximity_tracker[group] += 1

            self.last_seen_frame[group] = frame

            if self.proximity_tracker[group] >= self.ALLIANCE_THRESHOLD and group not in self.formed_alliances:
                self.formed_alliances.add(group)
                self.story_events.append({
                    "frame": frame,
                    "event_type": "group_merge",
                    "agents": group,
                    "story_type": "alliance",
                    "phase": phase,
                    "intensity": self.proximity_tracker[group]
                })

    # JSON output
    def generate_story_json(self):
        return {"story_events": self.story_events}

    # Textual narrative - improved with better paragraph structure
    def generate_story_text(self):
        if not self.story_events:
            return [{"type": "paragraph", "content": "The swarm moved in silence, with no notable interactions."}]

        story = []
        current_phase = None
        seen_pairs = set()  # track (pair/group, story_type) globally
        phase_events = defaultdict(list)  # Group events by phase

        # Group events by phase
        for e in self.story_events:
            phase = e["phase"]
            phase_events[phase].append(e)

        # Optional narrative phrases for variation
        conflict_phrases = [
            "erupted into repeated confrontations",
            "clashed multiple times",
            "had escalating tensions",
            "engaged in a fierce standoff",
            "found themselves locked in conflict",
        ]
        rivalry_phrases = [
            "escalated into a lasting rivalry",
            "became a defining force within the swarm",
            "remained in conflict throughout the simulation",
            "forged an enduring animosity",
        ]
        alliance_phrases = [
            "formed a strategic alliance",
            "stayed close long enough to coordinate",
            "banded together for mutual benefit",
            "discovered strength in unity",
        ]

        # Introduction phase
        intro_events = phase_events.get("introduction", [])
        if intro_events:
            story.append({"type": "header", "content": "🌱 INTRODUCTION"})
            
            intro_paragraph = "At the beginning of the simulation, the swarm drifted calmly across the digital space. Each agent moved with purpose, yet unaware of the complex relationships that would soon emerge from their simple interactions."
            story.append({"type": "paragraph", "content": intro_paragraph})
            
            # Group events into paragraphs
            tensions = [e for e in intro_events if e["story_type"] == "tension"]
            conflicts = [e for e in intro_events if e["story_type"] == "conflict"]
            rivalries = [e for e in intro_events if e["story_type"] == "rivalry"]
            alliances = [e for e in intro_events if e["story_type"] == "alliance"]
            
            if tensions:
                names_list = []
                for e in tensions[:3]:  # Limit to 3 examples
                    key = (tuple(e["agents"]), e["story_type"])
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        names = [AGENT_NAMES[a] for a in e["agents"]]
                        names_list.append(f"{names[0]} and {names[1]}")
                
                if names_list:
                    story.append({"type": "paragraph", "content": f"First encounters began to surface. Agents {', '.join(names_list[:2])} crossed paths, sensing an unease that would mark the beginning of their story."})
            
            if conflicts:
                conflict_names = []
                for e in conflicts[:2]:
                    key = (tuple(e["agents"]), e["story_type"])
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        names = [AGENT_NAMES[a] for a in e["agents"]]
                        phrase = random.choice(conflict_phrases)
                        conflict_names.append(f"{names[0]} and {names[1]} {phrase}")
                
                if conflict_names:
                    story.append({"type": "paragraph", "content": f"As the simulation progressed, tensions escalated. {conflict_names[0]}."})

        # Rising conflict phase
        rising_events = phase_events.get("rising_conflict", [])
        if rising_events:
            story.append({"type": "header", "content": "⚡ RISING CONFLICT"})
            
            rising_paragraph = "As time passed, repeated encounters shaped relationships. Subtle tensions grew into open confrontations, and the swarm's dynamics began to shift."
            story.append({"type": "paragraph", "content": rising_paragraph})
            
            conflicts = [e for e in rising_events if e["story_type"] in ["conflict", "rivalry"]]
            if conflicts:
                conflict_stories = []
                for e in conflicts[:3]:
                    key = (tuple(e["agents"]), e["story_type"])
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        names = [AGENT_NAMES[a] for a in e["agents"]]
                        if e["story_type"] == "rivalry":
                            phrase = random.choice(rivalry_phrases)
                            conflict_stories.append(f"{names[0]} and {names[1]} {phrase}")
                        else:
                            phrase = random.choice(conflict_phrases)
                            conflict_stories.append(f"{names[0]} and {names[1]} {phrase}")
                
                if conflict_stories:
                    story.append({"type": "paragraph", "content": f"{conflict_stories[0]}."})
            
            alliances = [e for e in rising_events if e["story_type"] == "alliance"]
            if alliances:
                for e in alliances[:2]:
                    key = (tuple(e["agents"]), e["story_type"])
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        names = [AGENT_NAMES[a] for a in e["agents"]]
                        phrase = random.choice(alliance_phrases)
                        story.append({"type": "paragraph", "content": f"Amidst the chaos, agents {', '.join(names)} {phrase}, finding strength in their unity."})

        # Climax phase
        climax_events = phase_events.get("climax", [])
        if climax_events:
            story.append({"type": "header", "content": "🔥 CLIMAX"})
            
            climax_paragraph = "In the final moments, unresolved conflicts surfaced. The swarm's fate hung in the balance as relationships reached their breaking point."
            story.append({"type": "paragraph", "content": climax_paragraph})
            
            rivalries = [e for e in climax_events if e["story_type"] == "rivalry"]
            if rivalries:
                for e in rivalries[:2]:
                    key = (tuple(e["agents"]), e["story_type"])
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        names = [AGENT_NAMES[a] for a in e["agents"]]
                        phrase = random.choice(rivalry_phrases)
                        story.append({"type": "paragraph", "content": f"The most intense conflicts came to a head. Agents {names[0]} and {names[1]} {phrase}, their struggle defining the final moments of the simulation."})

        # Epilogue
        story.append({"type": "header", "content": "🧠 Epilogue"})
        story.append({"type": "paragraph", "content": "Though governed by simple rules, the swarm revealed complex relationships—a reminder that stories can emerge even from mathematics. Each collision, each alliance, each moment of tension contributed to a narrative that transcended the sum of its parts."})

        return story







