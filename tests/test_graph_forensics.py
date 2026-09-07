import pytest

from vtb.graph_forensics import EvidenceBackedGraph, GraphNode


def test_graph_blocks_unsupported_edge():
    graph = EvidenceBackedGraph()
    graph.add_node(GraphNode("p", "PERSON", "Pessoa"))
    graph.add_node(GraphNode("c", "COMPANY", "Empresa"))
    with pytest.raises(ValueError):
        graph.add_edge("p", "c", "PARTNER", [])


def test_graph_accepts_evidence_backed_edge():
    graph = EvidenceBackedGraph()
    graph.add_node(GraphNode("p", "PERSON", "Pessoa"))
    graph.add_node(GraphNode("c", "COMPANY", "Empresa"))
    graph.add_edge("p", "c", "PARTNER", ["e1"], start_date="2024-01-01")
    assert graph.shortest_path("p", "c") == ["p", "c"]
