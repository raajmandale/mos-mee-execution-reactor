from app.core.decision_engine import DecisionEngine
from typing import Dict, Any
from app.core.pattern_engine import process_pattern


def build_execution(content: bytes, filename: str) -> Dict[str, Any]:
    pattern = process_pattern(content, filename)

    stages = [
        {
            "id": "IN",
            "label": "Input",
            "status": "done",
            "message": f"File accepted: {filename}",
        },
        {
            "id": "SIG",
            "label": "Signature",
            "status": "done",
            "message": f"Signature generated: {pattern['signature'][:12]}",
        },
        {
            "id": "PAT",
            "label": "Pattern",
            "status": "done",
            "message": f"Pattern family detected: {pattern['workflow']}",
        },
        {
            "id": "DEC",
            "label": "Decision",
            "status": "done",
            "message": f"Decision: {pattern['decision']}",
        },
        {
            "id": "OUT",
            "label": "Proof",
            "status": "done",
            "message": f"Proof ID: {pattern['proof_id']}",
        },
    ]

    return {
        **pattern,
        "stages": stages,
        "engine_story": [
            "Input was accepted into Mandale-OS PPE.",
            "A deterministic file signature was generated.",
            "The signature was checked against persistent pattern memory.",
            "The route decision was selected from memory evidence.",
            "A proof-ready execution record was produced.",
        ],
        "console": [s["message"] for s in stages],
    }