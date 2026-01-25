from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.orchestrator.ws_manager import manager
from backend.orchestrator.state import GLOBAL_STATE

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state on connect
        await websocket.send_json(GLOBAL_STATE)

        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)