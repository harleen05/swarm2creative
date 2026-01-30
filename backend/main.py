import sys
import os
import threading
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.chat import router as chat_router
from backend.api.ws import router as ws_router
from backend.api.image import router as image_router
from backend.orchestrator.frame_loop import frame_loop
from art.runtime import ART_RUNTIME
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(title="Swarm2Creative Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.include_router(ws_router)
app.include_router(chat_router)
app.include_router(image_router)

@app.on_event("startup")
def start_background_loops():
    ART_RUNTIME.start()

    threading.Thread(
        target=frame_loop,
        daemon=True
    ).start()

@app.get("/")
def health():
    return {"status": "swarm backend running"}