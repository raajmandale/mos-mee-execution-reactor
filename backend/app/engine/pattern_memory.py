import json, os

MEMORY_FILE = "results/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    return json.load(open(MEMORY_FILE))

def save_memory(memory):
    json.dump(memory, open(MEMORY_FILE, "w"), indent=2)