from fastapi import APIRouter
from backend.orchestrator.state import GLOBAL_STATE

router = APIRouter()

@router.get("/state")
def get_state():
    return GLOBAL_STATE
