from typing import List

from fastapi import APIRouter, HTTPException
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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]


@router.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        ollama_service.chat_stream(req.model, [m.model_dump() for m in req.messages]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
