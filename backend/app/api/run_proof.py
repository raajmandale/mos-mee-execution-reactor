from fastapi import APIRouter
from typing import Dict, Any
import hashlib
import uuid

from app.engine.evidence_export import EvidenceExporter

router = APIRouter()

# 🔒 Fixed constant (no import dependency)
PUBLIC_KEY_PATH = "keys/mos_ppe_public.pem"


# =========================
# MOCK ENGINE (SIMULATION)
# =========================

def simulate_engine(file_name: str) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())

    input_hash = hashlib.sha256(file_name.encode()).hexdigest()

    if "image" in file_name.lower():
        workflow = "Image Flow"
        confidence = 91
        decision = "Pattern Reused"
        cost_saved = 91
        integrity = "Verified"

    elif "bundle" in file_name.lower():
        workflow = "Bundle Workload"
        confidence = 88
        decision = "Pattern Reused"
        cost_saved = 88
        integrity = "Verified"

    else:
        workflow = "Generic Flow"
        confidence = 59
        decision = "Partial Reuse"
        cost_saved = 44
        integrity = "Verified"

    final_hash = hashlib.sha256((input_hash + decision).encode()).hexdigest()

    return {
        "proofId": run_id[:12],
        "runId": run_id,
        "inputHash": input_hash,
        "finalHash": final_hash,
        "workflow": workflow,
        "confidenceValue": confidence,
        "decision": decision,
        "costSaved": cost_saved,
        "integrity": integrity,
        "decisionReason": "Similarity above threshold"
    }


# =========================
# RUN PROOF
# =========================

@router.post("/run-proof")
def run_proof(data: Dict[str, Any]):

    file_name = data.get("file_name", "sample.bin")

    result = simulate_engine(file_name)

    # 🧠 Payload to sign
    payload = {
        "proof_id": result["proofId"],
        "run_id": result["runId"],
        "input_hash": result["inputHash"],
        "final_hash": result["finalHash"],
        "workflow": result["workflow"],
        "decision": result["decision"],
        "confidence": result["confidenceValue"],
        "cost_saved": result["costSaved"],
        "integrity": result["integrity"]
    }

    exporter = EvidenceExporter()
    signed_proof = exporter.sign(payload)

    return {
        "result": result,
        "signed_proof": signed_proof,
        "public_key_path": PUBLIC_KEY_PATH
    }