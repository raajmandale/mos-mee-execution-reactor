# backend/app/core/proof_engine.py

import json
import hashlib
import time
import uuid
from typing import List, Dict, Any


def _canonical_json(data: Any) -> str:
    """Deterministic JSON (no randomness, sorted keys)"""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class ProofEngine:
    def __init__(self):
        self.trace = []
        self.prev_hash = "GENESIS"

    def start(self, input_data: Dict):
        """Initialize proof run"""
        self.run_id = str(uuid.uuid4())
        self.timestamp = int(time.time())

        self.input_hash = _hash(_canonical_json(input_data))

        self.trace = []
        self.prev_hash = self.input_hash

    def add_step(self, name: str, data: Dict, decision: str):
        """Add execution step with chaining"""

        payload = {
            "step": name,
            "data": data,
            "decision": decision,
            "prev_hash": self.prev_hash
        }

        canonical = _canonical_json(payload)
        step_hash = _hash(canonical)

        record = {
            "step": name,
            "decision": decision,
            "hash": step_hash,
            "prev_hash": self.prev_hash
        }

        self.trace.append(record)
        self.prev_hash = step_hash

    def finalize(self) -> Dict:
        """Generate final proof"""

        final_payload = {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "input_hash": self.input_hash,
            "final_hash": self.prev_hash,
            "steps": self.trace
        }

        proof_id = _hash(_canonical_json(final_payload))

        return {
            "proof_id": proof_id,
            "run_id": self.run_id,
            "final_hash": self.prev_hash,
            "input_hash": self.input_hash,
            "steps": self.trace,
            "timestamp": self.timestamp
        }

    @staticmethod
    def verify(proof: Dict) -> bool:
        """Verify full proof integrity"""

        prev_hash = proof["input_hash"]

        for step in proof["steps"]:
            payload = {
                "step": step["step"],
                "decision": step["decision"],
                "data": {},  # data not stored → structure verification only
                "prev_hash": prev_hash
            }

            canonical = _canonical_json(payload)
            expected_hash = _hash(canonical)

            if step["hash"] != expected_hash:
                return False

            prev_hash = step["hash"]

        return prev_hash == proof["final_hash"]