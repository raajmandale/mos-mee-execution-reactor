from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .intelligence_engine import predict_next_route
from .pattern_engine import (
    build_signature,
    decide_route,
    match_signature,
    summarize_zip_entries,
    update_memory,
)
from .runtime_manager import (
    build_history_entry,
    build_queue_entry,
    build_runtime_payload,
    recompute_summary,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Mandale-OS MEE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def empty_state() -> dict:
    return {
        "totalRuns": 0,
        "averageReuse": 0,
        "bestWorkflow": "Unknown",
        "savedMs": 0,
        "efficiencyScore": 0,
        "memory": {},
        "history": [],
        "queue": [],
        "lastResult": None,
        "prediction": {
            "prediction": "Learning",
            "confidence": "Low",
            "reason": "No execution history yet.",
            "memoryClusters": [],
        },
    }


def load_state() -> dict:
    if not STATE_FILE.exists():
        state = empty_state()
        save_state(state)
        return state

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        state = empty_state()
        save_state(state)
        return state


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p")


def safe_zip_summary(file_bytes: bytes) -> dict:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            return summarize_zip_entries(names)
    except Exception:
        return {"inner_count": 0, "inner_families": [], "hybrid": False}


@app.get("/state")
def get_state():
    return load_state()


@app.post("/upload-react")
async def upload_react(file: UploadFile = File(...)):
    state = load_state()

    filename = file.filename or "unknown.bin"
    file_bytes = await file.read()
    size_bytes = len(file_bytes)

    suffix = Path(filename).suffix.lower()
    zip_info = {"inner_count": 0, "inner_families": [], "hybrid": False}
    if suffix == ".zip":
        zip_info = safe_zip_summary(file_bytes)

    signature = build_signature(
        filename=filename,
        size_bytes=size_bytes,
        zip_info=zip_info,
    )

    memory = state.get("memory", {})
    match = match_signature(signature, memory)
    route = decide_route(signature, match)

    result = build_runtime_payload(
        route=route,
        filename=filename,
        size_bytes=size_bytes,
        signature=signature,
    )

    estimated_before = max(
        int(route["time"] / 0.2) if route["reuse"] > 0 else route["time"],
        route["time"],
    )

    timestamp = now_str()

    history_entry = build_history_entry(
        result=result,
        timestamp=timestamp,
        estimated_before=estimated_before,
    )

    queue_entry = build_queue_entry(
        file_id=datetime.now().strftime("%H%M%S%f"),
        filename=filename,
        timestamp=timestamp,
    )

    state["memory"] = update_memory(memory, signature, route)

    history = state.get("history", [])
    history.insert(0, history_entry)
    state["history"] = history[:40]

    queue = state.get("queue", [])
    queue.insert(0, queue_entry)
    state["queue"] = queue[:25]

    state["lastResult"] = result
    state = recompute_summary(state)
    state["prediction"] = predict_next_route(state["history"], state["memory"])
    save_state(state)

    return result