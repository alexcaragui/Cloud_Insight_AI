import asyncio
import os
from typing import AsyncIterator

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


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
