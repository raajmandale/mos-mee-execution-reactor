from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def _stable_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_signatures(normalized_task: Dict[str, Any]) -> Dict[str, str]:
    canonical_step = normalized_task.get("canonical_step", "unknown")
    normalized_features = normalized_task.get("normalized_features", {})
    family_hint = normalized_task.get("family_hint", "generic")

    feature_hash = _sha256(_stable_json(normalized_features))

    invariant_payload = {
        "canonical_step": canonical_step,
        "family_hint": family_hint,
        "feature_keys": sorted(normalized_features.keys()),
    }

    step_payload = {
        "canonical_step": canonical_step,
        "family_hint": family_hint,
        "features": normalized_features,
    }

    invariant_signature = _sha256(_stable_json(invariant_payload))
    step_signature = _sha256(_stable_json(step_payload))

    return {
        "step_signature": step_signature,
        "invariant_signature": invariant_signature,
        "feature_hash": feature_hash,
    }