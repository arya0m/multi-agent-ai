from __future__ import annotations
import asyncio
import json
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core.config import settings
from backend.orchestrator.engine import Orchestrator
from backend.schemas.models import RunRequest, RunResponse, RunState, LogEvent

DB_PATH = settings.db_path
RUN_CACHE: dict[str, RunState] = {}
WEBSOCKETS: dict[str, set[WebSocket]] = {}


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            status TEXT NOT NULL,
            final_output TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT NOT NULL,
            meta TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[s.strip() for s in settings.cors_allow_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def persist_log(event: LogEvent) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs(run_id,timestamp,level,source,message,meta) VALUES(?,?,?,?,?,?)",
        (event.run_id, event.timestamp.isoformat(), event.level, event.source, event.message, json.dumps(event.meta)),
    )
    conn.commit()
    conn.close()

    for ws in list(WEBSOCKETS.get(event.run_id, set())):
        try:
            await ws.send_json(event.model_dump(mode="json"))
        except Exception:
            WEBSOCKETS[event.run_id].discard(ws)


async def persist_run(state: RunState) -> None:
    RUN_CACHE[state.run_id] = state
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO runs(run_id,query,status,final_output,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        (
            state.run_id,
            state.query,
            state.status,
            state.final_output,
            state.created_at.isoformat(),
            state.updated_at.isoformat(),
        ),
    )
    conn.commit()
    conn.close()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": settings.app_name, "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run_workflow(payload: RunRequest) -> RunResponse:
    run_id = str(uuid.uuid4())
    orchestrator = Orchestrator()
    state = await orchestrator.run(run_id=run_id, query=payload.query, log_cb=persist_log)
    await persist_run(state)
    return RunResponse(run_id=run_id, status=state.status, final_output=state.final_output, tasks=state.tasks)


@app.get("/runs/{run_id}", response_model=RunState)
def get_run(run_id: str) -> RunState:
    if run_id in RUN_CACHE:
        return RUN_CACHE[run_id]
    raise HTTPException(status_code=404, detail="Run not found")


@app.get("/logs/{run_id}")
def get_logs(run_id: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, level, source, message, meta FROM logs WHERE run_id=? ORDER BY id ASC", (run_id,))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "timestamp": r[0],
            "level": r[1],
            "source": r[2],
            "message": r[3],
            "meta": json.loads(r[4]) if r[4] else {},
        }
        for r in rows
    ]


@app.websocket("/ws/logs/{run_id}")
async def websocket_logs(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    WEBSOCKETS.setdefault(run_id, set()).add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        WEBSOCKETS.get(run_id, set()).discard(websocket)
