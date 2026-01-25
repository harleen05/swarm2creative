from fastapi import APIRouter
from pydantic import BaseModel
from backend.llm.interpreter import interpret_prompt
from backend.orchestrator.controller import apply_parameters

router = APIRouter()

class ChatInput(BaseModel):
    text: str

@router.post("/interpret")
def interpret(chat: ChatInput):
    params = interpret_prompt(chat.text)

    if not params:
        return {
            "applied": False,
            "reason": "LLM unavailable or quota exceeded"
        }

    apply_parameters(params)
    return {"applied": True, "parameters": params}