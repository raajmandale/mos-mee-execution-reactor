from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from app.core.normalizer import normalize_input
from app.core.signature_engine import build_signatures
from app.core.decomposition_engine import decompose_task
from app.core.graph_engine import build_execution_graph
from app.core.pattern_registry import PatternRegistry
from app.core.reuse_engine import ReuseEngine
from app.core.intelligence_engine import run_intelligence


router = APIRouter()


DEMO_META = {
    "creative": {"title": "Creative Pipeline", "family": "Image Flow"},
    "data": {"title": "Data Pipeline", "family": "Data Clean"},
    "dev": {"title": "Dev Pipeline", "family": "Build Chain"},
    "bundle": {"title": "Bundle Pipeline", "family": "Bundle Workload"},
}


class RunRequest(BaseModel):
    step: str = Field(..., description="Human-readable task step")
    features: Dict[str, Any] = Field(default_factory=dict)
    family_hint: Optional[str] = None
    mode: str = "standard"


def _match_type_to_status(match_type: str) -> str:
    if match_type == "exact":
        return "reused"
    if match_type == "partial":
        return "partial"
    if match_type == "family":
        return "partial"
    return "new"


def _match_type_to_reuse_percent(match_type: str, confidence: float) -> int:
    if match_type == "exact":
        return 85
    if match_type == "partial":
        return max(35, min(75, int(confidence * 100)))
    if match_type == "family":
        return 30
    return 0


def _match_type_to_time_after_ms(match_type: str, confidence: float) -> int:
    if match_type == "exact":
        return 120
    if match_type == "partial":
        return max(220, int(900 - (confidence * 400)))
    if match_type == "family":
        return 700
    return 1100


def _build_steps(
    primitive_nodes: List[Dict[str, Any]],
    match_type: str,
    reason: str,
    confidence: float,
) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []

    for node in primitive_nodes:
        steps.append(
            {
                "name": f"{node['primitive_type']}::{node['canonical_step']}",
                "reason": reason,
                "match_type": match_type if match_type != "none" else "fresh",
                "status": _match_type_to_status(match_type),
                "confidence": int(confidence * 100),
            }
        )

    return steps


def _build_match_summary(steps: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "reused": sum(1 for s in steps if s.get("status") == "reused"),
        "partial": sum(1 for s in steps if s.get("status") == "partial"),
        "fresh": sum(1 for s in steps if s.get("status") == "new"),
    }


def _build_invariant_signature(
    normalized: Dict[str, Any],
    signatures: Dict[str, str],
    match_type: str,
    reason: str,
    confidence: float,
) -> Dict[str, Any]:
    feature_keys = list(normalized.get("normalized_features", {}).keys())
    return {
        "id": signatures["invariant_signature"],
        "structural_class": normalized.get("family_hint", "generic"),
        "input_shape": ", ".join(feature_keys) if feature_keys else "none",
        "reuse_safety": (
            "high" if match_type == "exact"
            else "medium" if match_type in {"partial", "family"}
            else "low"
        ),
        "stable_invariants": [
            f"canonical_step={normalized.get('canonical_step', 'unknown')}",
            f"family_hint={normalized.get('family_hint', 'generic')}",
            f"feature_keys={feature_keys}",
            f"confidence={round(confidence, 2)}",
        ],
        "decision_reason": reason,
    }


def _infer_demo_key(family_hint: str) -> str:
    family = (family_hint or "").lower()
    if family in {"sorting", "image flow", "image", "creative"}:
        return "creative"
    if family in {"data clean", "data", "aggregation", "mapping"}:
        return "data"
    if family in {"build chain", "dev", "comparison", "transformation"}:
        return "dev"
    if family in {"bundle", "bundle workload"}:
        return "bundle"
    return "creative"


@router.post("/run")
def run_task(payload: RunRequest) -> Dict[str, Any]:
    normalized = normalize_input(
        step=payload.step,
        features=payload.features,
        family_hint=payload.family_hint,
        mode=payload.mode,
    )

    signatures = build_signatures(normalized)

    registry = PatternRegistry()
    reuse_engine = ReuseEngine(registry=registry)

    reuse_result = reuse_engine.check_reuse(
        step_signature=signatures["step_signature"],
        invariant_signature=signatures["invariant_signature"],
        family_hint=normalized["family_hint"],
        normalized_task=normalized,
    )

    primitive_nodes = decompose_task(normalized)
    graph = build_execution_graph(
        pattern_id=signatures["step_signature"],
        primitive_nodes=primitive_nodes,
    )

    if reuse_result["match_type"] == "none":
        registry.store_pattern(
            step_signature=signatures["step_signature"],
            invariant_signature=signatures["invariant_signature"],
            family_hint=normalized["family_hint"],
            normalized_task=normalized,
            graph=graph,
        )

    match_type = reuse_result["match_type"]
    reason = reuse_result["reason"]
    confidence = float(reuse_result.get("confidence", 0.35))

    steps = _build_steps(
        primitive_nodes=primitive_nodes,
        match_type=match_type,
        reason=reason,
        confidence=confidence,
    )

    match_summary = _build_match_summary(steps)
    reuse_percent = _match_type_to_reuse_percent(match_type, confidence)
    time_after_ms = _match_type_to_time_after_ms(match_type, confidence)
    demo_key = _infer_demo_key(normalized["family_hint"])

    workload_summary = {
        "mode": payload.mode,
        "files_scanned": 1,
        "total_size_bytes": 0,
        "exact_or_invariant_matches": match_summary["reused"],
        "partial_matches": match_summary["partial"],
        "fresh_steps": match_summary["fresh"],
    }

    invariant_signature = _build_invariant_signature(
        normalized=normalized,
        signatures=signatures,
        match_type=match_type,
        reason=reason,
        confidence=confidence,
    )

    response = {
        "status": "ok",
        "demo_key": demo_key,
        "mode": payload.mode,
        "normalized": normalized,
        "signatures": signatures,
        "reuse": reuse_result,
        "graph": graph,
        "executed_fresh": match_type == "none",
        "insights": {
            "summary": "Execution captured and analyzed",
            "user_message": reason,
        },
        "execution": {
            "mode": match_type,
            "confidence": round(confidence, 2),
            "reuse_percent": reuse_percent,
            "time_after_ms": time_after_ms,
        },
        "match_summary": match_summary,
        "steps": steps,
        "workload_summary": workload_summary,
        "invariant_signature": invariant_signature,
        "source_name": None,
    }

    run_record = {
        "id": f"run_{int(datetime.utcnow().timestamp() * 1000)}",
        "demo_key": demo_key,
        "family": DEMO_META[demo_key]["family"],
        "workflow": DEMO_META[demo_key]["title"],
        "reusePercent": reuse_percent,
        "timeAfter": time_after_ms,
        "timeSaved": max(0, 1400 - time_after_ms),
        "status": (
            "Pattern Reused" if match_type == "exact"
            else "Partial Reuse" if match_type == "partial"
            else "Family Reuse" if match_type == "family"
            else "First Run"
        ),
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "steps": steps,
        "workloadSummary": workload_summary,
        "invariantSignature": invariant_signature,
        "sourceName": None,
    }
    registry.append_run(run_record)
    response["run"] = run_record

    return response


@router.post("/reset")
def reset_state() -> Dict[str, Any]:
    registry = PatternRegistry()
    registry.reset_all()
    return {"status": "ok", "message": "MEE state reset complete."}