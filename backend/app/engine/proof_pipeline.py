# backend/app/engine/proof_pipeline.py

from typing import Dict, Any, List

from app.core.proof_engine import ProofEngine
from app.core.decision_engine import DecisionEngine
from app.engine.evidence_export import EvidenceExporter


class ProofPipeline:
    """
    M-OS PPE Authority Pipeline:
    run -> decision -> proof -> evidence export
    """

    def __init__(self):
        self.decision_engine = DecisionEngine()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        proof_engine = ProofEngine()
        proof_engine.start(input_data)

        steps: List[Dict[str, Any]] = input_data.get("steps", [])

        if not steps:
            steps = [
                {
                    "name": input_data.get("step", "default_execution"),
                    "context": input_data.get("features", {}),
                    "reuse_available": False,
                }
            ]

        execution_graph = {
            "pipeline": "M-OS PPE Authority Pipeline",
            "total_steps": len(steps),
            "steps": [],
        }

        decisions = []

        for step in steps:
            step_name = step.get("name", "unnamed_step")
            context = step.get("context", {})
            reuse_available = bool(step.get("reuse_available", False))

            decision = self.decision_engine.evaluate(
                step_name=step_name,
                context=context,
                reuse_available=reuse_available,
            )

            decisions.append(decision)

            execution_graph["steps"].append(
                {
                    "step": step_name,
                    "context": context,
                    "decision": decision,
                }
            )

            proof_engine.add_step(
                name=step_name,
                data=context,
                decision=f"{decision['action']} | {decision['reason']}",
            )

        proof = proof_engine.finalize()

        evidence_path = EvidenceExporter.export(
            proof=proof,
            input_data=input_data,
            execution_data={
                "execution_graph": execution_graph,
                "decisions": decisions,
            },
        )

        return {
            "status": "ok",
            "engine": "M-OS PPE",
            "pipeline": "run -> decision -> proof -> export",
            "proof_id": proof["proof_id"],
            "run_id": proof["run_id"],
            "proof": proof,
            "decisions": decisions,
            "execution_graph": execution_graph,
            "evidence_path": evidence_path,
        }