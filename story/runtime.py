# story/runtime.py
from story.story_mapper import StoryMapper
from story.engine import STORY_STATE

def _count_words(text):
    """Count words in a text string"""
    return len(text.split())

def _enforce_constraints(paragraphs, word_limit, paragraph_count):
    """
    Post-process paragraphs to enforce word limit and paragraph count.
    This is a copy of the function from backend.api.story to avoid circular imports.
    """
    if not paragraphs:
        return paragraphs
    
    # Validate inputs
    if word_limit is None or word_limit <= 0:
        word_limit = 500
    if paragraph_count is None or paragraph_count <= 0:
        paragraph_count = 5
    
    # Separate headers and paragraphs
    headers = [p for p in paragraphs if p.get("type") == "header"]
    para_items = [p for p in paragraphs if p.get("type") == "paragraph"]
    
    if not para_items:
        return paragraphs
    
    # Count current words
    all_text = " ".join([p.get("content", "") for p in para_items])
    current_words = _count_words(all_text)
    
    # If we have too many paragraphs, merge some
    if len(para_items) > paragraph_count:
        # Calculate target words per paragraph
        target_words_per_para = word_limit // paragraph_count if paragraph_count > 0 else 100
        
        merged = []
        current_para = []
        current_word_count = 0
        
        for para in para_items:
            content = para.get("content", "")
            word_count = _count_words(content)
            
            # If adding this paragraph would exceed target, start a new paragraph
            if current_word_count + word_count > target_words_per_para * 1.2 and current_para:
                merged.append({
                    "type": "paragraph",
                    "content": " ".join(current_para),
                    "enhanced": para.get("enhanced", False)
                })
                current_para = [content]
                current_word_count = word_count
            else:
                current_para.append(content)
                current_word_count += word_count
        
        # Add remaining paragraph
        if current_para:
            merged.append({
                "type": "paragraph",
                "content": " ".join(current_para),
                "enhanced": para_items[-1].get("enhanced", False) if para_items else False
            })
        
        para_items = merged[:paragraph_count]  # Limit to paragraph_count
    
    # If we have too few paragraphs, split some
    elif len(para_items) < paragraph_count and paragraph_count > 1:
        # Try to split longer paragraphs
        target_words_per_para = word_limit // paragraph_count if paragraph_count > 0 else 100
        split_paras = []
        
        for para in para_items:
            content = para.get("content", "")
            word_count = _count_words(content)
            
            if word_count > target_words_per_para * 1.5 and len(split_paras) < paragraph_count:
                # Split into sentences and regroup
                sentences = content.split(". ")
                current_group = []
                current_group_words = 0
                
                for sentence in sentences:
                    sent_words = _count_words(sentence)
                    if current_group_words + sent_words > target_words_per_para and current_group:
                        split_paras.append({
                            "type": "paragraph",
                            "content": ". ".join(current_group) + ("." if current_group else ""),
                            "enhanced": para.get("enhanced", False)
                        })
                        current_group = [sentence]
                        current_group_words = sent_words
                    else:
                        current_group.append(sentence)
                        current_group_words += sent_words
                    
                    if len(split_paras) >= paragraph_count - 1:
                        # Put remaining in last paragraph
                        break
                
                if current_group:
                    split_paras.append({
                        "type": "paragraph",
                        "content": ". ".join(current_group) + ("." if current_group else ""),
                        "enhanced": para.get("enhanced", False)
                    })
            else:
                split_paras.append(para)
            
            if len(split_paras) >= paragraph_count:
                break
        
        # Fill remaining slots if needed
        while len(split_paras) < paragraph_count and para_items:
            # Duplicate or split last paragraph
            last = split_paras[-1] if split_paras else para_items[-1]
            split_paras.append(last)
        
        para_items = split_paras[:paragraph_count]
    
    # Enforce word limit by truncating if necessary
    all_text = " ".join([p.get("content", "") for p in para_items])
    total_words = _count_words(all_text)
    
    if total_words > word_limit * 1.1:  # Allow 10% over, then truncate
        # Truncate from the end
        words = all_text.split()
        truncated_words = words[:word_limit]
        truncated_text = " ".join(truncated_words)
        
        # Redistribute truncated text across paragraphs
        words_per_para = len(truncated_words) // len(para_items) if para_items else 0
        result_paras = []
        word_index = 0
        
        for i, para in enumerate(para_items):
            if i == len(para_items) - 1:
                # Last paragraph gets remaining words
                para_words = truncated_words[word_index:]
            else:
                para_words = truncated_words[word_index:word_index + words_per_para]
                word_index += words_per_para
            
            if para_words:
                result_paras.append({
                    "type": "paragraph",
                    "content": " ".join(para_words),
                    "enhanced": para.get("enhanced", False)
                })
        
        para_items = result_paras
    
    # Reconstruct with headers
    result = []
    header_index = 0
    
    for para in para_items:
        # Add header before first paragraph of each section if available
        if header_index < len(headers) and not result:
            result.append(headers[header_index])
            header_index += 1
        elif header_index < len(headers) and result and result[-1].get("type") == "paragraph":
            # Add header between paragraphs occasionally
            if len(result) % 3 == 0:  # Every 3 paragraphs
                result.append(headers[header_index % len(headers)])
                header_index += 1
        
        result.append(para)
    
    # Add remaining headers at the end if any
    while header_index < len(headers):
        result.append(headers[header_index])
        header_index += 1
    
    return result

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
            
            # Apply word limit and paragraph count constraints
            word_limit = STORY_STATE.get("word_limit", 500)
            paragraph_count = STORY_STATE.get("paragraph_count", 5)
            paragraphs = _enforce_constraints(paragraphs, word_limit, paragraph_count)
            
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
        
        # Apply word limit and paragraph count constraints
        word_limit = STORY_STATE.get("word_limit", 500)
        paragraph_count = STORY_STATE.get("paragraph_count", 5)
        paragraphs = _enforce_constraints(paragraphs, word_limit, paragraph_count)
        
        return {
            "paragraphs": paragraphs,
            "story_events": self.mapper.story_events,
            "story_json": self.mapper.generate_story_json()
        }