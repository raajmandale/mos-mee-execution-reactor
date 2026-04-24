from __future__ import annotations

from typing import Any


def build_memory_clusters(memory: dict[str, Any]) -> list[dict[str, Any]]:
    clusters: dict[str, dict[str, Any]] = {}

    for _, entry in (memory or {}).items():
        cluster = entry.get("cluster_key", f"{entry.get('family', 'generic')}:unknown")
        if cluster not in clusters:
            clusters[cluster] = {
                "cluster": cluster,
                "family": entry.get("family", "generic"),
                "label": entry.get("label", "Unknown"),
                "items": 0,
                "seen": 0,
                "best_reuse": 0,
                "confidence": entry.get("last_confidence", "Low"),
            }

        clusters[cluster]["items"] += 1
        clusters[cluster]["seen"] += int(entry.get("seen", 0))
        clusters[cluster]["best_reuse"] = max(
            clusters[cluster]["best_reuse"],
            int(entry.get("best_reuse", 0)),
        )

    return sorted(
        clusters.values(),
        key=lambda item: (item["best_reuse"], item["seen"]),
        reverse=True,
    )


def predict_next_route(history: list[dict[str, Any]], memory: dict[str, Any]) -> dict[str, Any]:
    if not history:
        return {
            "prediction": "Learning",
            "confidence": "Low",
            "reason": "No execution history yet.",
        }

    latest = history[0]
    workflow = latest.get("workflow", "Unknown")
    reuse = int(latest.get("reuse", 0))

    if reuse >= 88:
        confidence = "High"
        prediction = "Pattern Reused"
        reason = f"Recent strong reuse detected in {workflow}."
    elif reuse >= 60:
        confidence = "Medium"
        prediction = "Partial Match"
        reason = f"Moderate reuse trend detected in {workflow}."
    else:
        confidence = "Low"
        prediction = "Learning"
        reason = f"No reliable reuse dominance yet for {workflow}."

    return {
        "prediction": prediction,
        "confidence": confidence,
        "reason": reason,
        "memoryClusters": build_memory_clusters(memory),
    }