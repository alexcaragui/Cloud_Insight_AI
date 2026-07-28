import asyncio
import json
import time
from typing import AsyncIterator

import httpx

from app.settings import OLLAMA_URL

async def list_models() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{OLLAMA_URL}/api/tags")
        r.raise_for_status()
        return r.json()


async def pull_model_stream(name: str) -> AsyncIterator[str]:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{OLLAMA_URL}/api/pull", json={"name": name}) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if line:
                    yield f"data: {line}\n\n"


async def delete_model(name: str) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.request("DELETE", f"{OLLAMA_URL}/api/delete", json={"name": name})
        r.raise_for_status()


async def chat_stream(model: str, messages: list) -> AsyncIterator[str]:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST", f"{OLLAMA_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": True}
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if line:
                    yield f"data: {line}\n\n"


async def _is_model_present(name: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models = r.json().get("models", [])
            base = name.split(":")[0]
            return any(m.get("name", "").startswith(base) for m in models)
    except Exception:
        return False


async def _background_pull(name: str) -> None:
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/pull", json={"name": name}):
                pass
    except Exception:
        pass


async def ensure_model(name: str) -> None:
    """Pull the model in the background if it is not already present."""
    if not await _is_model_present(name):
        asyncio.create_task(_background_pull(name))


async def handle_chat_ws(websocket, session_id: str, model: str, messages: list) -> None:
    """Stream an Ollama chat response over an open WebSocket and log the exchange to ClickHouse."""
    from app.database import get_ch
    from app.schemas.logs import ChatLogEntry

    start = time.monotonic()
    reply_parts: list[str] = []
    user_message = messages[-1]["content"] if messages else ""

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", f"{OLLAMA_URL}/api/chat",
                json={"model": model, "messages": messages, "stream": True},
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        reply_parts.append(token)
                        await websocket.send_json({"type": "token", "content": token})
                    if chunk.get("done"):
                        break

        await websocket.send_json({"type": "done"})

        entry = ChatLogEntry(
            session_id=session_id,
            model=model,
            user_message=user_message,
            assistant_reply="".join(reply_parts),
            duration_ms=round((time.monotonic() - start) * 1000, 2),
        )
        await asyncio.to_thread(get_ch().write_chat_log, entry)

    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
