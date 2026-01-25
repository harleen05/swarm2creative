import json
import re
import requests
from backend.llm.prompt import PROMPT_TEMPLATE

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"

def _extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return match.group(0)


def interpret_prompt(user_text: str):
    prompt = PROMPT_TEMPLATE.replace("{input}", user_text)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            },
            timeout=180
        )

        raw_output = response.json().get("response", "")
        json_str = _extract_json(raw_output)
        parsed = json.loads(json_str)

        return parsed if isinstance(parsed, dict) else {}

    except Exception as e:
        print("⚠️ Ollama error:", e)
        return {}
