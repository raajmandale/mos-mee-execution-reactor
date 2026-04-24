from __future__ import annotations

from typing import Any, Dict, Optional

from app.core.pattern_registry import PatternRegistry


def get_registry_state() -> Dict[str, Any]:
    registry = PatternRegistry()
    return registry.get_state()


def get_exact_pattern(step_signature: str) -> Optional[Dict[str, Any]]:
    registry = PatternRegistry()
    return registry.get_exact(step_signature)


def store_pattern(
    *,
    step_signature: str,
    invariant_signature: str,
    family_hint: str,
    normalized_task: Dict[str, Any],
    graph: Dict[str, Any],
) -> Dict[str, Any]:
    registry = PatternRegistry()
    return registry.store_pattern(
        step_signature=step_signature,
        invariant_signature=invariant_signature,
        family_hint=family_hint,
        normalized_task=normalized_task,
        graph=graph,
    )