import hashlib
import json
import os
import time

# ===== PATH =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

MEMORY_FILE = os.path.join(DATA_PATH, "pattern_memory.json")


# ===== INIT MEMORY =====
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


# ===== SIGNATURE =====
def compute_signature(file_bytes):
    """
    Deterministic file signature
    """
    return hashlib.sha256(file_bytes).hexdigest()


# ===== CLASSIFICATION =====
def classify_file(filename):
    name = filename.lower()

    if name.endswith(".zip"):
        return "Bundle Pattern", "Bundle Workload"

    if name.endswith((".jpg", ".png", ".jpeg")):
        return "Visual Pattern", "Image Flow"

    return "Generic Pattern", "Generic Flow"


# ===== MAIN ENGINE =====
def process_file(file_bytes, filename):
    memory = load_memory()

    signature = compute_signature(file_bytes)

    family, workflow = classify_file(filename)

    now = int(time.time())

    # ===== EXISTING PATTERN =====
    if signature in memory:
        entry = memory[signature]

        entry["count"] += 1
        entry["last_seen"] = now

        save_memory(memory)

        return {
            "workflow": entry["workflow"],
            "source": filename,
            "reuse": min(95, 80 + entry["count"] * 2),
            "confidence": "HIGH",
            "decision": "Pattern Reused",
            "mode": "reused",
            "family": entry["family"],
            "saved": 4800 + entry["count"] * 100,
            "proof": f"MOS-PPE-{now}",
            "step_timings": {
                "IN": 200,
                "SIG": 250,
                "PAT": 300,
                "DEC": 200,
                "OUT": 150,
            }
        }

    # ===== NEW PATTERN =====
    memory[signature] = {
        "family": family,
        "workflow": workflow,
        "count": 1,
        "created": now,
        "last_seen": now
    }

    save_memory(memory)

    return {
        "workflow": workflow,
        "source": filename,
        "reuse": 0,
        "confidence": "LEARNING",
        "decision": "New Pattern Learned",
        "mode": "hybrid",
        "family": family,
        "saved": 1200,
        "proof": f"MOS-PPE-{now}",
        "step_timings": {
            "IN": 250,
            "SIG": 400,
            "PAT": 600,
            "DEC": 300,
            "OUT": 200,
        }
    }