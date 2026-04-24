from __future__ import annotations

from fastapi import APIRouter
from typing import Any, Dict

from app.core.pattern_registry import PatternRegistry


router = APIRouter()


@router.get("/registry")
def debug_registry() -> Dict[str, Any]:
    registry = PatternRegistry()
    state = registry.get_state()

    return {
        "status": "ok",
        "patterns": state.get("patterns", {}),
        "family_index": state.get("family_index", {}),
        "invariant_index": state.get("invariant_index", {}),
        "reuse_history": state.get("reuse_history", {}),
        "runs": state.get("runs", []),
    }