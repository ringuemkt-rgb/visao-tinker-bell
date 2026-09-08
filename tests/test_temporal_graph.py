from datetime import date

from vtb.temporal_graph import TemporalEdge, TemporalEvidenceGraph


def test_relationship_is_checked_at_contract_date():
    graph = TemporalEvidenceGraph()
    graph.add_node("p", "PERSON")
    graph.add_node("c", "COMPANY")
    graph.add_edge(TemporalEdge("p", "c", "PARTNER", ("e1",), date(2024, 1, 1), date(2024, 12, 31)))
    assert graph.relationship_existed_on("p", "c", "PARTNER", date(2024, 6, 1)) is True
    assert graph.relationship_existed_on("p", "c", "PARTNER", date(2025, 1, 1)) is False
