from typing import Dict, Any, List
from app.core.memory_store import load_memory


def build_execution_graph(execution: Dict[str, Any]) -> Dict[str, Any]:
    nodes = [
        {
            "id": "IN",
            "label": "Input",
            "type": "input",
            "weight": 1,
            "message": f"Source: {execution.get('source')}",
        },
        {
            "id": "SIG",
            "label": "Signature",
            "type": "signature",
            "weight": 2,
            "message": execution.get("signature", "")[:12],
        },
        {
            "id": "PAT",
            "label": execution.get("workflow", "Pattern"),
            "type": "pattern",
            "weight": 3,
            "message": execution.get("pattern_family", "Generic Flow"),
        },
        {
            "id": "DEC",
            "label": "Decision",
            "type": "decision",
            "weight": 3,
            "message": execution.get("decision"),
        },
        {
            "id": "OUT",
            "label": "Proof",
            "type": "proof",
            "weight": 2,
            "message": execution.get("proof_id"),
        },
    ]

    edges = [
        {"source": "IN", "target": "SIG"},
        {"source": "SIG", "target": "PAT"},
        {"source": "PAT", "target": "DEC"},
        {"source": "DEC", "target": "OUT"},
    ]

    return {
        "nodes": nodes,
        "edges": edges,
    }


def build_memory_graph() -> Dict[str, Any]:
    memory = load_memory()

    nodes: List[Dict[str, Any]] = [
        {
            "id": "MOS",
            "label": "Mandale-OS",
            "type": "core",
            "weight": 5,
        }
    ]

    edges: List[Dict[str, str]] = []
    families = set()

    for item in memory[:40]:
        family = item.get("family", "Generic Flow")
        family_id = family.upper().replace(" ", "_")

        if family_id not in families:
          families.add(family_id)
          nodes.append({
              "id": family_id,
              "label": family,
              "type": "family",
              "weight": 3,
          })
          edges.append({"source": "MOS", "target": family_id})

        sig = item.get("signature", "unknown")[:10]
        source = item.get("source", "unknown")
        nodes.append({
            "id": sig,
            "label": source,
            "type": "signature",
            "weight": max(1, int(item.get("runs", 1))),
            "reuse": item.get("reuse", 0),
            "status": item.get("status", "Verified"),
        })
        edges.append({"source": family_id, "target": sig})

    return {
        "nodes": nodes,
        "edges": edges,
        "history": memory[:50],
    }