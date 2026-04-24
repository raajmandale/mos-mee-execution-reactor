from __future__ import annotations

from typing import Any, Dict

from app.core.pattern_registry import PatternRegistry
from app.core.reuse_engine import ReuseEngine


def match_pattern(
    *,
    step_signature: str,
    invariant_signature: str,
    family_hint: str,
) -> Dict[str, Any]:
    """
    Compatibility bridge for older matcher usage.

    New canonical flow:
    matcher -> reuse_engine -> pattern_registry
    """
    registry = PatternRegistry()
    engine = ReuseEngine(registry=registry)
    return engine.check_reuse(
        step_signature=step_signature,
        invariant_signature=invariant_signature,
        family_hint=family_hint,
    )