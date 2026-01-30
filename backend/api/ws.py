from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.orchestrator.ws_manager import manager
from backend.orchestrator.state import GLOBAL_STATE

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        await websocket.send_json(GLOBAL_STATE)
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception:
        manager.disconnect(websocket)