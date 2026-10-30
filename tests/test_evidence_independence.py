from vtb.signals import RiskSignal, SignalCategory, SignalSeverity, triage_band


def signal(key: str, evidence: list[str], *, legal: bool = False) -> RiskSignal:
    return RiskSignal(
        signal_id=key, category=SignalCategory.PROCUREMENT,
        title="Synthetic review", description="No allegation",
        severity=SignalSeverity.CRITICAL_REVIEW,
        evidence_ids=evidence, legal_validation_required=legal,
    )


def test_publication_defaults_fail_closed():
    item = signal("x", ["A"])
    assert item.publication_safe() is False
    assert item.publication_safe(verified_evidence_ids={"A"}, human_reviewed=True) is True
    assert item.publication_safe(verified_evidence_ids={"B"}, human_reviewed=True) is False
    assert item.publication_safe(verified_evidence_ids={"A"}) is False


def test_legal_signal_requires_specialist_review():
    item = signal("x", ["A"], legal=True)
    assert not item.publication_safe(verified_evidence_ids={"A"}, human_reviewed=True)
    assert item.publication_safe(
        verified_evidence_ids={"A"}, human_reviewed=True, legal_reviewed=True
    )


def test_many_evidence_ids_from_one_source_not_independent():
    items = [signal("1", ["a1", "a2"]), signal("2", ["a3", "a4"])]
    assert triage_band(items) == "P3_ROUTINE_REVIEW"
    assert triage_band(items, evidence_lineage={
        "a1": "publication-1", "a2": "publication-1",
        "a3": "publication-1", "a4": "publication-1",
    }) == "P3_ROUTINE_REVIEW"
    assert triage_band(items, evidence_lineage={
        "a1": "document-A", "a2": "document-B",
        "a3": "document-C", "a4": "document-D",
    }) == "P1_DEEP_REVIEW"


def test_absent_lineage_not_counted():
    assert triage_band([signal("x", ["unverified"]), signal("y", ["also-unverified"])],
                       evidence_lineage={"other": "doc"}) == "P3_ROUTINE_REVIEW"
