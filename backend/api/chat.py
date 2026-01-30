from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.orchestrator.controller import apply_parameters
from backend.orchestrator.ws_manager import manager
from backend.orchestrator.state import GLOBAL_STATE

from anyio import from_thread

router = APIRouter()


class Intent(BaseModel):
    art: Optional[dict] = None
    music: Optional[dict] = None
    architecture: Optional[dict] = None
    story: Optional[dict] = None


@router.post("/interpret")
async def interpret(payload: Intent):
    apply_parameters(payload.dict(exclude_none=True))

    try:
        # We're already in an async context here, so we can await directly
        await manager.broadcast(GLOBAL_STATE)
    except Exception:
        # If broadcasting fails we don't want to break the API contract
        pass

    return {"status": "ok"}