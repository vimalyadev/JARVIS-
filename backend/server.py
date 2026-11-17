import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from .config import HOST, PORT, JARVIS_NAME, USER_NAME, WAKE_WORDS
from .brain import think
from .skills.system_info import get_system_status
from .tts import speak, synthesize_edge_tts_bytes

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title=f"{JARVIS_NAME} Personal AI Assistant")

# Allow mobile devices on the network to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    text: str
    vocalize: bool = False

class TTSRequest(BaseModel):
    text: str

@app.get("/api/status")
def api_status():
    status = get_system_status()
    status["assistant"] = JARVIS_NAME
    status["user"] = USER_NAME
    status["wake_words"] = WAKE_WORDS
    return status

@app.post("/api/command")
def api_command(req: CommandRequest):
    response_text = think(req.text)
    if req.vocalize:
        speak(response_text)
    return {
        "query": req.text,
        "response": response_text,
        "status": get_system_status()
    }

@app.post("/api/tts")
async def api_tts(req: TTSRequest):
    try:
        audio_bytes = await synthesize_edge_tts_bytes(req.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response_text = think(data)
            await websocket.send_json({
                "type": "response",
                "text": response_text
            })
    except WebSocketDisconnect:
        pass

# Mount frontend files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/manifest.json")
    def serve_manifest():
        return FileResponse(str(FRONTEND_DIR / "manifest.json"))

    @app.get("/sw.js")
    def serve_sw():
        return FileResponse(str(FRONTEND_DIR / "sw.js"), media_type="application/javascript")

def start_server():
    import uvicorn
    uvicorn.run("backend.server:app", host=HOST, port=PORT, reload=False)

if __name__ == "__main__":
    start_server()
