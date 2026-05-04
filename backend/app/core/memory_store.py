import json
import time
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
MEMORY_FILE = DATA_DIR / "memory.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_memory() -> List[Dict[str, Any]]:
    if not MEMORY_FILE.exists():
        return []

    try:
        return json.loads(MEMORY_FILE.read_text())
    except Exception:
        return []


def save_memory(memory: List[Dict[str, Any]]):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))


def find_exact(signature: str, memory: list):
    return next((m for m in memory if m["signature"] == signature), None)


def find_family(family: str, memory: list):
    return [m for m in memory if m["family"] == family]


def update_or_insert(entry: dict):
    memory = load_memory()

    existing = find_exact(entry["signature"], memory)

    now = int(time.time())

    if existing:
        existing["runs"] += 1
        existing["last_seen"] = now
        existing["reuse"] = min(96, existing.get("reuse", 88) + 2)
        status = "Verified"
    else:
        entry["runs"] = 1
        entry["first_seen"] = now
        entry["last_seen"] = now
        memory.insert(0, entry)
        status = "Learned"

    save_memory(memory[:200])

    return status, memory