from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import requests
import json
import os
from backend.orchestrator.frame_loop import STORY_RUNTIME
from backend.orchestrator.state import GLOBAL_STATE
from backend.orchestrator.ws_manager import manager
from story.engine import STORY_STATE

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _count_words(text):
    """Count words in a text string"""
    return len(text.split())


def _enforce_constraints(paragraphs, word_limit, paragraph_count):
    """
    Post-process paragraphs to enforce word limit and paragraph count.
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
    
    print(f"🔧 Enforcing constraints: {len(para_items)} paragraphs, target: {paragraph_count} paragraphs, {word_limit} words")
    
    # Count current words
    all_text = " ".join([p.get("content", "") for p in para_items])
    current_words = _count_words(all_text)
    print(f"📝 Current word count: {current_words}, target: {word_limit}")
    
    # If we have too many paragraphs, merge some
    if len(para_items) > paragraph_count:
        print(f"🔀 Merging {len(para_items)} paragraphs down to {paragraph_count}")
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
                    "enhanced": True
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
                "enhanced": True
            })
        
        para_items = merged[:paragraph_count]  # Limit to paragraph_count
    
    # If we have too few paragraphs, split some
    elif len(para_items) < paragraph_count and paragraph_count > 1:
        print(f"✂️ Splitting {len(para_items)} paragraphs up to {paragraph_count}")
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
                            "enhanced": True
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
                        "enhanced": True
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
    print(f"📏 Final word count before truncation: {total_words}, limit: {word_limit}")
    
    if total_words > word_limit * 1.1:  # Allow 10% over, then truncate
        print(f"✂️ Truncating from {total_words} to {word_limit} words")
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
                    "enhanced": True
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

class StoryEnhancementRequest(BaseModel):
    prompt: Optional[str] = None
    enhance: bool = False
    tone: Optional[str] = None
    mood: Optional[str] = None
    pace: Optional[str] = None
    word_limit: Optional[int] = None
    paragraph_count: Optional[int] = None


def enhance_story_with_llm(story_events, tone="neutral", pace="moderate", mood="neutral", word_limit=500, paragraph_count=5, user_prompt=None, base_story=None):
    """
    Use LLM to enhance the story narrative based on events and user intent.
    Returns paragraphs marked as enhanced.
    If no events, generates an initial story based on tone/mood/pace.
    """
    # Build context from story events with agent names (limit to prevent long prompts)
    from story.story_mapper import AGENT_NAMES
    event_summary = []
    # Limit to last 15 events to keep prompt shorter
    for event in story_events[-15:]:
        event_type = event.get("story_type", "interaction")
        agents = event.get("agents", [])
        phase = event.get("phase", "introduction")
        intensity = event.get("intensity", 1)
        
        # Use agent names for better context
        agent_names = [AGENT_NAMES.get(a, f"Agent {a}") for a in agents]
        event_summary.append(f"{phase}: {event_type} between {', '.join(agent_names)}")
    
    context = "\n".join(event_summary)
    
    # Include base story if available (limit to prevent long prompts)
    base_context = ""
    if base_story and base_story.get("paragraphs"):
        base_paras = [p.get("content", "") for p in base_story["paragraphs"] if p.get("type") == "paragraph"]
        # Limit to first 2 paragraphs to keep prompt short
        base_context = "\n\nCurrent story:\n" + "\n".join(base_paras[:2])
    
    # Calculate target words per paragraph
    words_per_paragraph = max(50, word_limit // paragraph_count) if paragraph_count > 0 else 100
    
    # Use limited context (already limited to 15 events above)
    limited_context = context
    
    # Adjust prompt based on whether we have events
    if not story_events:
        events_context = "This is the beginning of a swarm simulation. Generate an opening narrative about a digital swarm of agents moving through space."
    else:
        events_context = f"Events:\n{limited_context}"
    
    # Define very distinct style templates
    style_templates = {
        "dramatic": "Use INTENSE, gripping language. Short punchy sentences. Exclamation marks! Vivid action verbs. High stakes. Tension in every line.",
        "poetic": "Use flowing, lyrical prose. Rich metaphors. Sensory imagery. Rhythm in sentences. Beauty in description. Elegant word choices.",
        "mysterious": "Use cryptic, enigmatic language. Questions without answers. Shadows and secrets. Whispered hints. Unknown forces at work.",
        "epic": "Use grand, sweeping language. Legendary scale. Heroic deeds. Ancient wisdom. The fate of worlds hangs in the balance.",
        "intimate": "Use close, personal language. Quiet moments. Inner thoughts. Gentle observations. The small details that matter.",
        "neutral": "Use clear, balanced prose. Straightforward narration. Neither too dramatic nor too subtle."
    }
    
    mood_templates = {
        "hopeful": "The overall feeling is OPTIMISTIC. Light breaking through. Promise of better things. Warmth and encouragement.",
        "melancholic": "The overall feeling is SAD and wistful. Loss pervades. Bittersweet memories. A sense of what could have been.",
        "tense": "The overall feeling is ANXIOUS and on-edge. Something is wrong. Danger lurks. Hearts racing. Breath held.",
        "triumphant": "The overall feeling is VICTORIOUS. Celebration. Achievement. Glory earned. Pride and joy.",
        "somber": "The overall feeling is SERIOUS and heavy. Grave matters. Solemn reflection. Weight of decisions.",
        "neutral": "The overall feeling is BALANCED. Neither too happy nor too sad."
    }
    
    pace_templates = {
        "slow": "SLOW pace: Long, flowing sentences. Detailed descriptions. Take time with each moment. Contemplative pauses.",
        "moderate": "MODERATE pace: Mix of sentence lengths. Balance action and reflection. Steady rhythm.",
        "fast": "FAST pace: SHORT sentences. Quick cuts. Rapid action. No time to breathe. Go go go!"
    }
    
    style_instruction = style_templates.get(tone, style_templates["neutral"])
    mood_instruction = mood_templates.get(mood, mood_templates["neutral"])
    pace_instruction = pace_templates.get(pace, pace_templates["moderate"])
    
    prompt = f"""Write a richly detailed, immersive story about a digital swarm simulation.

**CRITICAL STYLE REQUIREMENTS - FOLLOW EXACTLY:**
{style_instruction}
{mood_instruction}
{pace_instruction}

**LENGTH REQUIREMENTS (CRITICAL):**
- Total word count: You must aim for **{word_limit} words** or more. Do not write less.
- Total paragraphs: EXACTLY {paragraph_count} paragraphs.
- **Words per paragraph:** Each paragraph MUST be roughly **{words_per_paragraph} to {words_per_paragraph + 50} words**.
- **DETAIL:** Do not summarize. Expand every scene. Use long, descriptive sentences to meet the word count.
- If the story feels too short, ADD MORE DESCRIPTION to the middle sections.

**REQUIRED STRUCTURE:**
You MUST include these sections with headers:
1. 🌱 INTRODUCTION - Set the scene, introduce the swarm and its digital world.
2. 📖 RISING ACTION - Build tension as agents begin to interact. Determine the conflict.
3. ⚡ CLIMAX - The peak moment of conflict or transformation. Make this the longest section.
4. 🔄 RESOLUTION - How the swarm adapts and changes.
5. 🧠 EPILOGUE - Philosophical reflection on emergence and digital life.

**CONTEXT:**
{events_context}

**OUTPUT FORMAT:**
Return ONLY valid JSON:
{{
  "paragraphs": [
    {{"type": "header", "content": "🌱 INTRODUCTION"}},
    {{"type": "paragraph", "content": "A detailed, evocative opening paragraph ({words_per_paragraph} words)..."}},
    {{"type": "header", "content": "📖 RISING ACTION"}},
    {{"type": "paragraph", "content": "Tension builds ({words_per_paragraph} words)..."}},
    {{"type": "header", "content": "⚡ CLIMAX"}},
    {{"type": "paragraph", "content": "The peak moment, fully described ({words_per_paragraph} words)..."}},
    {{"type": "header", "content": "🔄 RESOLUTION"}},
    {{"type": "paragraph", "content": "Change occurs ({words_per_paragraph} words)..."}},
    {{"type": "header", "content": "🧠 EPILOGUE"}},
    {{"type": "paragraph", "content": "Reflection on meaning ({words_per_paragraph} words)..."}}
  ]
}}

CRITICAL: Write {word_limit} words total. Make the {tone} tone and {mood} mood unmistakable in every sentence!
"""
    
    
    # Check if we have API key
    if not GROQ_API_KEY:
        print("⚠️ No GROQ_API_KEY found. Falling back to base story.")
        full_story = STORY_RUNTIME.generate_full_story()
        constrained = _enforce_constraints(
            full_story.get("paragraphs", []),
            word_limit,
            paragraph_count
        )
        return {"paragraphs": constrained}

    try:
        # Groq API endpoint
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a creative storyteller who writes detailed, engaging narratives about digital swarm simulations. You MUST return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": word_limit * 3  # Allow enough tokens
        }

        print(f"🚀 Sending request to Groq (Model: {MODEL}, Target: {word_limit} words)...")
        import time
        start_time = time.time()
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(10, 300) # Increased to 300s for long stories
        )
        
        duration = time.time() - start_time
        print(f"⏱️ LLM request took {duration:.2f}s")
        
        response.raise_for_status()
        data = response.json()
        raw_output = data["choices"][0]["message"]["content"]
        print(f"📝 Raw LLM output length: {len(raw_output)} chars")
        
        # Extract JSON from response
        import re
        # Robust JSON Extraction
        enhanced_paragraphs = []
        
        # Strategy 1: Try to parse complete JSON first (best case)
        json_match = re.search(r"\{[\s\S]*\}", raw_output)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                if "paragraphs" in parsed and isinstance(parsed["paragraphs"], list):
                    for p in parsed["paragraphs"]:
                        if isinstance(p, dict) and "content" in p:
                            enhanced_paragraphs.append({
                                "type": p.get("type", "paragraph"),
                                "content": p.get("content", "").strip(),
                                "enhanced": True
                            })
                    if enhanced_paragraphs:
                        print(f"✅ Successfully parsed perfect JSON ({len(enhanced_paragraphs)} paragraphs)")
            except:
                pass
        
        # Strategy 2: If complete parse failed (or was empty), try regex extraction
        # This handles truncated JSON where the closing brace is missing
        if not enhanced_paragraphs:
            print("⚠️ Perfect JSON parse failed/empty. Attempting dirty regex extraction...")
            # Pattern matches {"type": "...", "content": "..."} across newlines
            pattern = r'\{\s*"type"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"(.*?)"\s*\}'
            matches = re.finditer(pattern, raw_output, re.DOTALL)
            
            for m in matches:
                p_type = m.group(1)
                # Unescape quotes and newlines manually since we're regexing raw JSON string
                p_content = m.group(2).replace('\\"', '"').replace('\\n', '\n').strip()
                if p_content:
                    enhanced_paragraphs.append({
                        "type": p_type,
                        "content": p_content,
                        "enhanced": True
                    })
            
            if enhanced_paragraphs:
                print(f"✅ Recovered {len(enhanced_paragraphs)} paragraphs via regex")
        
        # Fallback: parse raw text into paragraphs if JSON parsing failed
        if not enhanced_paragraphs:
            print("⚠️ Parsing raw text as fallback")
            lines = [l.strip() for l in raw_output.split("\n") if l.strip()]
            # Filter out markdown code blocks markers
            lines = [l for l in lines if not l.startswith("```")]
            
            for line in lines:
                if line.startswith(("{", "}", "[", "]")):
                    continue # Skip json artifacts
                
                if any(start in line for start in ["🌱", "⚡", "🔥", "🧠", "INTRODUCTION", "EPILOGUE"]):
                    enhanced_paragraphs.append({"type": "header", "content": line, "enhanced": True})
                elif len(line) > 20: # Filter out short noise
                    enhanced_paragraphs.append({"type": "paragraph", "content": line, "enhanced": True})

        
        if not enhanced_paragraphs:
            print("⚠️ No paragraphs extracted from LLM response")
            enhanced_paragraphs = [{"type": "paragraph", "content": "Story generation returned no content. Please try again.", "enhanced": True}]
        
        # Post-process to enforce constraints but be generous to preserve the epilogue/content
        # We only truncate if it's grossly over limit (e.g. 1.5x) to avoid cutting off the epilogue
        print(f"📊 Before constraints: {len(enhanced_paragraphs)} items")
        
        # Calculate current word count
        current_words = _count_words(" ".join([p["content"] for p in enhanced_paragraphs if p.get("type") == "paragraph"]))
        
        if current_words > word_limit * 1.5:
             enhanced_paragraphs = _enforce_constraints(
                enhanced_paragraphs, 
                word_limit, 
                paragraph_count
            )
        else:
             print(f"✨ Keeping story as is ({current_words} words), within acceptable margin of {word_limit}")
                
        return {"paragraphs": enhanced_paragraphs}
        
    except requests.exceptions.Timeout:
        print(f"⚠️ LLM timeout - generating story without LLM enhancement")
        # Generate story using the base story mapper with constraints
        full_story = STORY_RUNTIME.generate_full_story()
        # Apply constraints to the base story
        constrained = _enforce_constraints(
            full_story.get("paragraphs", []),
            word_limit,
            paragraph_count
        )
        # Mark as enhanced (even though LLM failed, we applied constraints)
        for para in constrained:
            para["enhanced"] = True
        return {"paragraphs": constrained}
    except requests.exceptions.ConnectionError:
        print(f"⚠️ LLM connection error - Ollama may not be running")
        # Generate story using the base story mapper with constraints
        full_story = STORY_RUNTIME.generate_full_story()
        constrained = _enforce_constraints(
            full_story.get("paragraphs", []),
            word_limit,
            paragraph_count
        )
        for para in constrained:
            para["enhanced"] = True
        return {"paragraphs": constrained}
    except Exception as e:
        print(f"⚠️ LLM story enhancement error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to basic story generation with constraints
        full_story = STORY_RUNTIME.generate_full_story()
        constrained = _enforce_constraints(
            full_story.get("paragraphs", []),
            word_limit,
            paragraph_count
        )
        for para in constrained:
            para["enhanced"] = True
        return {"paragraphs": constrained}


@router.get("/story")
def get_story():
    """Get current story state"""
    story_frame = GLOBAL_STATE.get("story_frame", {})
    return story_frame


@router.post("/story/generate")
async def generate_story(payload: StoryEnhancementRequest):
    """
    Generate or enhance story using LLM.
    """
    story_frame = GLOBAL_STATE.get("story_frame", {})
    story_events = story_frame.get("story_events", [])
    
    # Use provided values or fall back to state/defaults
    tone = payload.tone if payload.tone is not None else STORY_STATE.get("tone", "neutral")
    pace = payload.pace if payload.pace is not None else STORY_STATE.get("pace", "moderate")
    mood = payload.mood if payload.mood is not None else STORY_STATE.get("mood", "neutral")
    word_limit = payload.word_limit if payload.word_limit is not None else 800
    paragraph_count = payload.paragraph_count if payload.paragraph_count is not None else 6
    
    print(f"🎯 Story generation params: tone={tone}, mood={mood}, pace={pace}, word_limit={word_limit}, paragraph_count={paragraph_count}")
    
    # Update state with new values
    if payload.tone:
        STORY_STATE["tone"] = payload.tone
    if payload.pace:
        STORY_STATE["pace"] = payload.pace
    if payload.mood:
        STORY_STATE["mood"] = payload.mood
    if payload.word_limit is not None:
        STORY_STATE["word_limit"] = payload.word_limit
    if payload.paragraph_count is not None:
        STORY_STATE["paragraph_count"] = payload.paragraph_count
    
    if payload.enhance or payload.prompt:
        print(f"🎨 REGENERATING STORY with tone={tone}, mood={mood}, pace={pace}")
        # Get base story for context
        base_story = STORY_RUNTIME.generate_full_story()
        
        # Use LLM to enhance the story
        enhanced = enhance_story_with_llm(
            story_events,
            tone=tone,
            pace=pace,
            mood=mood,
            word_limit=word_limit,
            paragraph_count=paragraph_count,
            user_prompt=payload.prompt,
            base_story=base_story
        )
        
        # Merge enhanced paragraphs with base story, keeping structure
        # Replace base paragraphs with enhanced ones, but keep headers if they exist
        enhanced_paragraphs = enhanced.get("paragraphs", [])
        
        # Update story frame with enhanced content
        story_frame["paragraphs"] = enhanced_paragraphs
        story_frame["enhanced"] = True
        story_frame["enhanced_at"] = story_frame.get("meta", {}).get("current_frame", 0)
        # Update meta with current parameters
        story_frame["meta"] = {
            **story_frame.get("meta", {}),
            "tone": tone,
            "mood": mood,
            "pace": pace,
            "word_limit": word_limit,
            "paragraph_count": paragraph_count
        }
        
        print(f"✅ Story regenerated: {len(enhanced_paragraphs)} paragraphs, tone={tone}, mood={mood}, pace={pace}")
        
        GLOBAL_STATE["story_frame"] = story_frame
        
        # Broadcast updated state via WebSocket so frontend receives the update
        try:
            await manager.broadcast(GLOBAL_STATE)
        except Exception as e:
            print(f"⚠️ Could not broadcast story update: {e}")
        
        return {
            "status": "ok",
            "story": story_frame
        }
    else:
        # User updated parameters (tone, mood, etc) but didn't request a re-write.
        # Check if we already have an enhanced story.
        current_frame = GLOBAL_STATE.get("story_frame", {})
        if current_frame.get("enhanced") and current_frame.get("paragraphs"):
            print(f"✨ Preserving existing enhanced story while updating metadata")
            # Just update metadata in the existing frame
            current_frame["meta"] = {
                "tone": tone,
                "pace": pace,
                "mood": mood,
                "total_events": len(story_events),
                "current_frame": current_frame.get("meta", {}).get("current_frame", 0)
            }
            # Ensure GLOBAL_STATE is updated (it should be ref update, but good to be explicit)
            GLOBAL_STATE["story_frame"] = current_frame
        else:
            # No enhanced story, or we want to update the algorithmic story
            full_story = STORY_RUNTIME.generate_full_story()
            
            # If there are no events or the story is just the default message, generate with LLM
            # (Only do this if we don't have ANY story yet)
            # If there are no events or the story is just the default message, generate with LLM
            # (Only do this if we don't have ANY story yet)
            if not story_events and (not full_story.get("paragraphs") or len(full_story["paragraphs"]) <= 1):
                print(f"📝 No events found, generating initial story with tone={tone}, mood={mood}, pace={pace}")
                # Use LLM to generate an initial story based on tone/mood/pace
                enhanced = enhance_story_with_llm(
                    [],  # No events
                    tone=tone,
                    pace=pace,
                    mood=mood,
                    word_limit=word_limit,
                    paragraph_count=paragraph_count,
                    user_prompt=None,
                    base_story=None
                )
                
                enhanced_paragraphs = enhanced.get("paragraphs", [])
                story_frame = GLOBAL_STATE.get("story_frame", {})
                story_frame["paragraphs"] = enhanced_paragraphs
                story_frame["enhanced"] = True
                story_frame["story_events"] = story_events
                story_frame["phase"] = "introduction"
                story_frame["meta"] = {
                    "tone": tone,
                    "pace": pace,
                    "mood": mood,
                    "total_events": len(story_events),
                    "current_frame": 0
                }
                GLOBAL_STATE["story_frame"] = story_frame
                
                # Return immediately as we've updated the state
                try:
                    await manager.broadcast(GLOBAL_STATE)
                except Exception as e:
                    print(f"⚠️ Could not broadcast story update: {e}")
                
                return {
                    "status": "ok",
                    "story": story_frame
                } 
            
            # Update GLOBAL_STATE with the constrained story
            paragraphs = full_story.get("paragraphs", [])
            if not paragraphs:
                # Fallback if algorithmic generation fails
                paragraphs = [{"type": "paragraph", "content": "Waiting for events...", "enhanced": False}]
                
            story_frame = GLOBAL_STATE.get("story_frame", {})
            story_frame["paragraphs"] = paragraphs
            story_frame["story_events"] = full_story.get("story_events", [])
            story_frame["meta"] = {
                "tone": tone,
                "pace": pace,
                "mood": mood,
                "total_events": len(story_events),
                "current_frame": STORY_RUNTIME.current_frame
            }
            GLOBAL_STATE["story_frame"] = story_frame
        
        # Broadcast updated state via WebSocket
        try:
            await manager.broadcast(GLOBAL_STATE)
        except Exception as e:
            print(f"⚠️ Could not broadcast story update: {e}")
        
        return {
            "status": "ok",
            "story": GLOBAL_STATE.get("story_frame", {})
        }


@router.get("/story/full")
def get_full_story():
    """Get the complete story narrative"""
    full_story = STORY_RUNTIME.generate_full_story()
    return full_story

