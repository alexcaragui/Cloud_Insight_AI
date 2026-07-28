import uuid
from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services import ollama_service

router = APIRouter(prefix="/api/ollama", tags=["ollama"])


@router.get("/models")
async def list_models():
    try:
        return await ollama_service.list_models()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama unreachable: {e}")


class PullRequest(BaseModel):
    name: str


@router.post("/models/pull")
async def pull_model(req: PullRequest):
    return StreamingResponse(
        ollama_service.pull_model_stream(req.name),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/models/{name:path}")
async def delete_model(name: str):
    try:
        await ollama_service.delete_model(name)
        return {"status": "deleted", "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat/ws")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    try:
        while True:
            data = await websocket.receive_json()
            model = data.get("model", "qwen2.5:7b")
            messages = data.get("messages", [])
            await ollama_service.handle_chat_ws(websocket, session_id, model, messages)
    except WebSocketDisconnect:
        pass
