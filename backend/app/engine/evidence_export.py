import os
import json
import hashlib
import hmac
from typing import Dict, Any


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _sign(data: Dict[str, Any]) -> str:
    key = os.getenv("M_OS_PPE_SIGNING_KEY", "M-OS-PPE-DEV-SIGNING-KEY")
    return hmac.new(
        key.encode(),
        _canonical_json(data).encode(),
        hashlib.sha256
    ).hexdigest()


class EvidenceExporter:
    BASE_DIR = "proof_reports"

    @staticmethod
    def export(proof: Dict, input_data: Dict, execution_data: Dict) -> str:
        proof_id = proof["proof_id"]
        folder = os.path.join(EvidenceExporter.BASE_DIR, proof_id)
        os.makedirs(folder, exist_ok=True)

        summary = {
            "proof_id": proof["proof_id"],
            "run_id": proof["run_id"],
            "input_hash": proof["input_hash"],
            "final_hash": proof["final_hash"],
            "total_steps": len(proof["steps"]),
        }

        integrity_payload = {
            "input": _hash(_canonical_json(input_data)),
            "execution": _hash(_canonical_json(execution_data)),
            "proof": _hash(_canonical_json(proof)),
        }

        integrity_hash = _hash(_canonical_json(integrity_payload))

        signed_payload = {
            "system": "Mandale-OS PPE",
            "artifact": "Signed Proof Authority Export",
            "version": "3.0.0",
            "proof": proof,
            "summary": summary,
            "input_data": input_data,
            "execution_data": execution_data,
            "integrity_payload": integrity_payload,
            "integrity_hash": integrity_hash,
        }

        signature = _sign(signed_payload)

        signed_export = {
            **signed_payload,
            "signature_type": "HMAC-SHA256",
            "signature": signature,
            "verification": "canonical-json + integrity-hash + signature",
        }

        files = {
            "input.json": input_data,
            "execution.json": execution_data,
            "decision.json": proof["steps"],
            "summary.json": summary,
            "signed_proof.json": signed_export,
        }

        for name, payload in files.items():
            with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

        with open(os.path.join(folder, "integrity.txt"), "w", encoding="utf-8") as f:
            f.write(integrity_hash)

        return folder