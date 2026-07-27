"""
Cloud Insight AI — backend
FastAPI service 
"""

import asyncio
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from app.database import get_logger, init_db, get_ch, init_logger
from app.routes import logs, models, app as app_router


async def _module_health_checker() -> None:
    # Wait one interval before the first check — modules may still be starting when the backend boots.
    await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_logger()

    ch = get_ch()  # raw adapter needed for DDL operations (migrations, ensure_* calls)
    ch.run_migrations()  # rename legacy tables/columns before DDL provisioning
    ch.ensure_api_logs()  # CREATE TABLE IF NOT EXISTS api_logs
    ch.ensure_app_logs()  # CREATE TABLE IF NOT EXISTS app_logs
    get_logger().app("app.start", "anomascan", message="anomascan backend started")  # first lifecycle event; signals successful startup

    health_task = asyncio.create_task(_module_health_checker())
    yield
    health_task.cancel()
    for task in [health_task]:
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="AnomaScan Api", lifespan=lifespan, version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creăm folderul public și îl montăm pentru acces frontend
os.makedirs("/app/public", exist_ok=True)
app.mount("/public", StaticFiles(directory="/app/public"), name="public")

app.include_router(app_router.router)
app.include_router(models.router)
app.include_router(logs.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}