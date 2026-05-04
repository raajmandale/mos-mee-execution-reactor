import json
import hashlib
import time
import uuid
from typing import Dict, Any


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class ProofEngine:
    def __init__(self):
        self.trace = []
        self.prev_hash = "GENESIS"

    def start(self, input_data: Dict):
        self.run_id = str(uuid.uuid4())
        self.timestamp = int(time.time())

        self.input_hash = _hash(_canonical_json(input_data))

        self.trace = []
        self.prev_hash = self.input_hash

    def add_step(self, name: str, data: Dict, decision: str):
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