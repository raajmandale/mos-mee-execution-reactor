import time
from .workload_parser import parse_zip
from .similarity import file_signature, similarity
from .pattern_memory import load_memory, save_memory

def run_workload(path):
    start = time.time()

    files = parse_zip(path)
    memory = load_memory()

    reused = 0
    partial = 0
    total = len(files)

    for f in files:
        sig = file_signature(f)

        if sig in memory:
            reused += 1
        else:
            # check partial
            for existing in memory:
                if similarity(sig, existing) > 0.5:
                    partial += 1
                    break

        memory[sig] = True

    save_memory(memory)

    end = time.time()

    return {
        "total_files": total,
        "reused": reused,
        "partial": partial,
        "fresh": total - reused - partial,
        "time_ms": int((end - start) * 1000),
        "reuse_percent": int((reused / total) * 100) if total else 0
    }