from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)


class EvidenceBackedGraph:
    """Grafo onde toda aresta material precisa carregar evidência e janela temporal quando aplicável."""

    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: GraphNode) -> None:
        self.graph.add_node(node.node_id, node_type=node.node_type, label=node.label, **node.attributes)

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        evidence_ids: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
        status: str = "VERIFIED_LINK",
    ) -> None:
        if not evidence_ids:
            raise ValueError("material graph edges require evidence_ids")
        if source not in self.graph or target not in self.graph:
            raise KeyError("both graph nodes must exist before adding an edge")
        self.graph.add_edge(
            source,
            target,
            relation=relation,
            evidence_ids=tuple(sorted(set(evidence_ids))),
            start_date=start_date,
            end_date=end_date,
            status=status,
        )

    def centrality(self) -> dict[str, float]:
        if not self.graph:
            return {}
        simple = nx.Graph(self.graph)
        return nx.degree_centrality(simple)

    def connected_components(self) -> list[set[str]]:
        if not self.graph:
            return []
        return [set(component) for component in nx.connected_components(nx.Graph(self.graph))]

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        simple = nx.Graph(self.graph)
        try:
            return nx.shortest_path(simple, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def high_degree_signals(self, review_degree: int = 6) -> list[RiskSignal]:
        signals: list[RiskSignal] = []
        for node_id, degree in self.graph.degree():
            if degree < review_degree:
                continue
            evidence_ids: set[str] = set()
            for _, _, data in self.graph.edges(node_id, data=True):
                evidence_ids.update(data.get("evidence_ids", ()))
            for _, _, data in self.graph.in_edges(node_id, data=True):
                evidence_ids.update(data.get("evidence_ids", ()))
            signals.append(
                RiskSignal(
                    signal_id=f"NET-HIGH-DEGREE-{node_id}",
                    category=SignalCategory.NETWORK,
                    title="Nó com conectividade elevada",
                    description=f"Nó {node_id} possui grau {degree} no grafo do caso.",
                    severity=SignalSeverity.LOW,
                    entity_ids=[node_id],
                    evidence_ids=sorted(evidence_ids),
                    method="network degree",
                    threshold={"review_degree": review_degree},
                    false_positive_risk="high",
                    alternative_explanations=["contador/advogado", "grupo empresarial legítimo", "fornecedor recorrente"],
                )
            )
        return signals

    def export_graphml(self, path: str) -> None:
        exportable = nx.MultiDiGraph()
        for node_id, data in self.graph.nodes(data=True):
            exportable.add_node(node_id, **{k: str(v) for k, v in data.items()})
        for source, target, key, data in self.graph.edges(keys=True, data=True):
            exportable.add_edge(source, target, key=key, **{k: str(v) for k, v in data.items()})
        nx.write_graphml(exportable, path)
