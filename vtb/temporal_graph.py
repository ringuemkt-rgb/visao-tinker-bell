from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import networkx as nx


@dataclass(slots=True, frozen=True)
class TemporalEdge:
    source: str
    target: str
    relation: str
    evidence_ids: tuple[str, ...]
    valid_from: date | None = None
    valid_to: date | None = None

    def active_on(self, when: date) -> bool:
        if self.valid_from and when < self.valid_from:
            return False
        return not (self.valid_to and when > self.valid_to)


class TemporalEvidenceGraph:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_node(self, node_id: str, node_type: str, **attrs: object) -> None:
        self.graph.add_node(node_id, node_type=node_type, **attrs)

    def add_edge(self, edge: TemporalEdge) -> None:
        if not edge.evidence_ids:
            raise ValueError("temporal edges require evidence")
        if edge.source not in self.graph or edge.target not in self.graph:
            raise KeyError("nodes must exist before edge insertion")
        self.graph.add_edge(
            edge.source,
            edge.target,
            relation=edge.relation,
            evidence_ids=edge.evidence_ids,
            valid_from=edge.valid_from.isoformat() if edge.valid_from else None,
            valid_to=edge.valid_to.isoformat() if edge.valid_to else None,
        )

    def edges_active_on(self, when: date) -> list[TemporalEdge]:
        rows: list[TemporalEdge] = []
        for source, target, data in self.graph.edges(data=True):
            edge = TemporalEdge(
                source,
                target,
                str(data["relation"]),
                tuple(data["evidence_ids"]),
                date.fromisoformat(data["valid_from"]) if data.get("valid_from") else None,
                date.fromisoformat(data["valid_to"]) if data.get("valid_to") else None,
            )
            if edge.active_on(when):
                rows.append(edge)
        return rows

    def relationship_existed_on(self, source: str, target: str, relation: str, when: date) -> bool:
        for edge in self.edges_active_on(when):
            if edge.source == source and edge.target == target and edge.relation == relation:
                return True
        return False
