from __future__ import annotations

from typing import Any, Dict, Optional


STEP_ALIASES = {
    "sort array": "sort",
    "arrange list": "sort",
    "order numbers": "sort",
    "filter rows": "filter",
    "map values": "map",
    "aggregate data": "aggregate",
    "sum values": "aggregate",
    "normalize input": "normalize",
}


def _canonicalize_step(step: str) -> str:
    raw = (step or "").strip().lower()
    return STEP_ALIASES.get(raw, raw.replace(" ", "_"))


def _normalize_features(features: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not features:
        return {}

    normalized: Dict[str, Any] = {}
    for key in sorted(features.keys()):
        value = features[key]
        normalized[str(key)] = value
    return normalized


def normalize_input(
    *,
    step: str,
    features: Optional[Dict[str, Any]] = None,
    family_hint: Optional[str] = None,
    mode: str = "standard",
) -> Dict[str, Any]:
    canonical_step = _canonicalize_step(step)
    normalized_features = _normalize_features(features)

    inferred_family = family_hint or canonical_step

    return {
        "raw_step": step,
        "canonical_step": canonical_step,
        "normalized_features": normalized_features,
        "family_hint": inferred_family,
        "mode": mode,
    }