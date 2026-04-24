from __future__ import annotations

from fastapi import APIRouter
from typing import Any, Dict

from app.core.pattern_registry import PatternRegistry


router = APIRouter()


@router.get("/state")
def get_state() -> Dict[str, Any]:
    registry = PatternRegistry()
    state = registry.get_state()
    runs = registry.get_runs()

    return {
        "status": "ok",
        "runs": runs,
        "summary": {
            "pattern_count": len(state.get("patterns", {})),
            "invariant_count": len(state.get("invariant_index", {})),
            "family_count": len(state.get("family_index", {})),
            "reuse_history_count": len(state.get("reuse_history", {})),
            "run_count": len(runs),
        },
        "state": state,
    }