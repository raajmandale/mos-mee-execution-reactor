from __future__ import annotations

from typing import Any


def build_runtime_payload(route: dict[str, Any], filename: str, size_bytes: int, signature: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow": route["workflow"],
        "family": signature["family"].title() if signature["family"] != "bundle" else "Bundle Workload",
        "reuse": route["reuse"],
        "confidence": route["confidence"],
        "time": route["time"],
        "decision": route["decision"],
        "mode": route["mode"],
        "systemState": route["systemState"],
        "routeType": route["routeType"],
        "nodes": route["nodes"],
        "topNodes": route["topNodes"],
        "bottomNodes": route["bottomNodes"],
        "notes": route["notes"],
        "console": route["console"],
        "sourceFile": filename,
        "sizeBytes": size_bytes,
        "signature": signature,
    }


def build_history_entry(result: dict[str, Any], timestamp: str, estimated_before: int) -> dict[str, Any]:
    return {
        "timestamp": timestamp,
        "workflow": result["workflow"],
        "reuse": result["reuse"],
        "mode": result["mode"],
        "decision": result["decision"],
        "source": result["sourceFile"],
        "time": result["time"],
        "confidence": result["confidence"],
        "estimatedBefore": estimated_before,
    }


def build_queue_entry(file_id: str, filename: str, timestamp: str) -> dict[str, Any]:
    return {
        "id": file_id,
        "file": filename,
        "status": "processed",
        "timestamp": timestamp,
    }


def recompute_summary(state: dict[str, Any]) -> dict[str, Any]:
    history = state.get("history", [])
    total_runs = len(history)

    avg_reuse = 0
    if total_runs:
        avg_reuse = round(sum(int(item.get("reuse", 0)) for item in history) / total_runs)

    best_workflow = "Unknown"
    best_reuse = -1
    saved_ms = 0

    for item in history:
        reuse = int(item.get("reuse", 0))
        if reuse > best_reuse:
            best_reuse = reuse
            best_workflow = item.get("workflow", "Unknown")

        time_after = int(item.get("time", 0))
        estimated_before = int(item.get("estimatedBefore", time_after))
        saved_ms += max(estimated_before - time_after, 0)

    efficiency = 0
    if total_runs:
        efficiency = round((avg_reuse * 0.7) + (min(saved_ms / max(total_runs, 1), 1000) / 1000 * 30))

    state["totalRuns"] = total_runs
    state["averageReuse"] = avg_reuse
    state["bestWorkflow"] = best_workflow
    state["savedMs"] = saved_ms
    state["efficiencyScore"] = efficiency
    return state