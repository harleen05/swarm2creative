import json
import re
import os
from groq import Groq
from dotenv import load_dotenv
from backend.llm.prompt import PROMPT_TEMPLATE

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    )

client = Groq(api_key=GROQ_API_KEY)


def _extract_json(text: str):
    """Extract JSON object from text response"""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return match.group(0)


def interpret_prompt(user_text: str):
    """
    Interpret user text prompt using Groq LLM.
    
    Args:
        user_text: The user's natural language input
        
    Returns:
        dict: Parsed intent containing art, music, architecture, story parameters
    """
    prompt = PROMPT_TEMPLATE.replace("{input}", user_text)

    try:
        # Call Groq API
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise JSON generator for a multimodal creative system. Always respond with valid JSON only, no explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2048,
            top_p=0.9
        )

        # Extract the response text
        raw_output = response.choices[0].message.content
        
        # Extract and parse JSON
        json_str = _extract_json(raw_output)
        parsed = json.loads(json_str)

        return parsed if isinstance(parsed, dict) else {}

    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        import traceback
        traceback.print_exc()
        return {}