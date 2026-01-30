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
        await manager.broadcast(GLOBAL_STATE)
    except Exception:
        pass

    return {"status": "ok"}