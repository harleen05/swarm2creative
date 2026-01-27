from fastapi import APIRouter
from pydantic import BaseModel
from backend.orchestrator.controller import apply_parameters

router = APIRouter()

class Intent(BaseModel):
    art: dict | None = None
    music: dict | None = None
    architecture: dict | None = None
    story: dict | None = None

@router.post("/interpret")
def interpret(intent: Intent):
    apply_parameters(intent.dict(exclude_none=True))
    return {"ok": True}