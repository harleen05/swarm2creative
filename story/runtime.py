# story/runtime.py
from story.story_mapper import StoryMapper
from story.engine import STORY_STATE

class StoryRuntime:
    def __init__(self):
        self.mapper = StoryMapper()
        self.total_frames = 2000
        self.current_frame = 0
        self.story_text_cache = []
        self.last_text_update = 0

    def step(self, events):
        """
        events = list of low-level events
        e.g. collisions detected in art runtime
        """
        if events:
            for e in events:
                self.mapper.process_event(e, self.total_frames)

        self.current_frame += 1

        # Generate story text periodically (every 100 frames or when significant events occur)
        should_update_text = (
            self.current_frame - self.last_text_update > 100 or
            len(events) > 0
        )

        paragraphs = []
        if should_update_text and self.mapper.story_events:
            story_items = self.mapper.generate_story_text()
            # Convert story items to structured paragraphs
            for item in story_items:
                if item.get("type") == "header":
                    paragraphs.append({
                        "type": "header",
                        "content": item["content"],
                        "enhanced": False
                    })
                elif item.get("type") == "paragraph":
                    paragraphs.append({
                        "type": "paragraph",
                        "content": item["content"],
                        "enhanced": False
                    })
            
            self.story_text_cache = paragraphs
            self.last_text_update = self.current_frame

        return {
            "story_events": self.mapper.story_events[-10:],  # Last 10 events
            "phase": self.mapper._get_phase(self.current_frame, self.total_frames),
            "paragraphs": self.story_text_cache,
            "meta": {
                "tone": STORY_STATE.get("tone", "neutral"),
                "pace": STORY_STATE.get("pace", "moderate"),
                "mood": STORY_STATE.get("mood", "neutral"),
                "total_events": len(self.mapper.story_events),
                "current_frame": self.current_frame
            }
        }

    def generate_full_story(self):
        """Generate complete story narrative"""
        if not self.mapper.story_events:
            return {
                "paragraphs": [{"type": "paragraph", "content": "The swarm moved in silence, with no notable interactions.", "enhanced": False}],
                "story_events": []
            }
        
        story_items = self.mapper.generate_story_text()
        paragraphs = []
        
        for item in story_items:
            paragraphs.append({
                "type": item.get("type", "paragraph"),
                "content": item["content"],
                "enhanced": False
            })
        
        return {
            "paragraphs": paragraphs,
            "story_events": self.mapper.story_events,
            "story_json": self.mapper.generate_story_json()
        }