from vtb.ensemble import combine_signals
from vtb.signals import RiskSignal, SignalCategory, SignalSeverity


def test_ensemble_requires_independent_sources():
    records = [
        RiskSignal("P", SignalCategory.PROCUREMENT, "Procurement", "Synthetic",
                   severity=SignalSeverity.HIGH, evidence_ids=["a", "b"]),
        RiskSignal("C", SignalCategory.CORPORATE, "Corporate", "Synthetic",
                   severity=SignalSeverity.HIGH, evidence_ids=["c"]),
        RiskSignal("N", SignalCategory.NETWORK, "Network", "Synthetic",
                   severity=SignalSeverity.HIGH, evidence_ids=["d"]),
    ]
    assert combine_signals(records).review_priority == "P3_ROUTINE_REVIEW"
    same = {eid: "source-1" for eid in "abcd"}
    assert combine_signals(records, evidence_lineage=same).review_priority == "P3_ROUTINE_REVIEW"
    distinct = {eid: f"source-{eid}" for eid in "abcd"}
    assert combine_signals(records, evidence_lineage=distinct).review_priority == "P1_DEEP_REVIEW"
