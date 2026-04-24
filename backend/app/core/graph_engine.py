from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class GraphNode:
    id: str
    primitive_type: str
    canonical_step: str
    family_hint: str
    features: Dict[str, Any]
    depends_on: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    source: str
    target: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionGraph:
    """
    Phase-1 execution graph:
    - nodes = reusable primitive units
    - edges = dependency relationships
    """

    def __init__(self, graph_id: str, nodes: List[GraphNode], edges: List[GraphEdge]) -> None:
        self.graph_id = graph_id
        self.nodes = nodes
        self.edges = edges

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


class GraphEngine:
    """
    Build a deterministic execution graph from decomposed primitives.
    """

    def build_graph(
        self,
        pattern_id: str,
        primitive_nodes: List[Dict[str, Any]],
    ) -> ExecutionGraph:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for item in primitive_nodes:
            node = GraphNode(
                id=item["id"],
                primitive_type=item["primitive_type"],
                canonical_step=item["canonical_step"],
                family_hint=item["family_hint"],
                features=item.get("features", {}),
                depends_on=item.get("depends_on", []),
            )
            nodes.append(node)

            for parent in node.depends_on:
                if parent:
                    edges.append(GraphEdge(source=parent, target=node.id))

        graph_id = f"{pattern_id}::graph"
        return ExecutionGraph(graph_id=graph_id, nodes=nodes, edges=edges)


def build_execution_graph(
    pattern_id: str,
    primitive_nodes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    engine = GraphEngine()
    return engine.build_graph(pattern_id=pattern_id, primitive_nodes=primitive_nodes).to_dict()