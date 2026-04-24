from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


PRIMITIVE_TYPES = {
    "transform",
    "filter",
    "map",
    "reduce",
    "compare",
    "combine",
}


@dataclass
class PrimitiveNode:
    """
    Smallest reusable execution unit for Phase-1 MEE.
    """

    id: str
    primitive_type: str
    canonical_step: str
    family_hint: str
    features: Dict[str, Any]
    depends_on: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DecompositionEngine:
    """
    Phase-1 decomposition engine.

    Converts a normalized task into a deterministic list of reusable primitives.
    """

    def decompose(self, normalized_task: Dict[str, Any]) -> List[PrimitiveNode]:
        canonical_step = normalized_task.get("canonical_step", "unknown")
        family_hint = normalized_task.get("family_hint", "generic")
        features = normalized_task.get("normalized_features", {}) or {}

        primitives = self._infer_primitives(
            canonical_step=canonical_step,
            family_hint=family_hint,
            features=features,
        )

        nodes: List[PrimitiveNode] = []
        prev_id: Optional[str] = None

        for idx, primitive_type in enumerate(primitives, start=1):
            node_id = f"node_{idx}"
            node = PrimitiveNode(
                id=node_id,
                primitive_type=primitive_type,
                canonical_step=canonical_step,
                family_hint=family_hint,
                features=self._slice_features_for_primitive(primitive_type, features),
                depends_on=[prev_id] if prev_id else [],
            )
            nodes.append(node)
            prev_id = node_id

        return nodes

    def _infer_primitives(
        self,
        canonical_step: str,
        family_hint: str,
        features: Dict[str, Any],
    ) -> List[str]:
        step = canonical_step.lower()
        family = family_hint.lower()

        if family == "sorting" or "sort" in step or "order" in step or "arrange" in step:
            return ["transform", "compare", "combine"]

        if family == "filtering" or "filter" in step:
            return ["filter", "combine"]

        if family == "mapping" or "map" in step:
            return ["map", "combine"]

        if family == "aggregation" or "aggregate" in step or "sum" in step:
            return ["map", "reduce", "combine"]

        if family == "transformation" or "transform" in step or "normalize" in step:
            return ["transform", "combine"]

        if family == "comparison" or "compare" in step or "diff" in step:
            return ["compare", "combine"]

        return ["transform", "combine"]

    def _slice_features_for_primitive(
        self,
        primitive_type: str,
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        if primitive_type not in PRIMITIVE_TYPES:
            primitive_type = "transform"

        return {
            "primitive_scope": primitive_type,
            "payload": features,
        }


def decompose_task(normalized_task: Dict[str, Any]) -> List[Dict[str, Any]]:
    engine = DecompositionEngine()
    return [node.to_dict() for node in engine.decompose(normalized_task)]