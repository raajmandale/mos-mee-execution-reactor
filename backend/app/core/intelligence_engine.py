from .signature_engine import extract_signature
from .reuse_engine import find_reuse
from .pattern_registry import register_pattern

def run_intelligence(workload):
    # Step 1: Extract signature
    signature = extract_signature(workload)

    # Step 2: Check reuse
    reuse_result = find_reuse(signature)

    # Step 3: Register new pattern
    register_pattern(signature)

    return {
        "signature": signature,
        "reuse": reuse_result.get("reuse", 0),
        "matched": reuse_result.get("matched", []),
        "status": reuse_result.get("status", "fresh")
    }