from vtb.claims import ClaimLedger
from vtb.models import Claim, ClaimStatus, EvidenceRecord, SourceQuality, SourceRecord


def source(sid: str, lineage: str):
    return SourceRecord(sid, sid, "órgão", f"https://example.test/{sid}", quality=SourceQuality.S5_OFFICIAL_PRIMARY, original_source_id=lineage)


def test_repeated_mirror_is_not_independent_corroboration():
    ledger = ClaimLedger()
    ledger.add_source(source("S1", "ORIGINAL-A"))
    ledger.add_source(source("S2", "ORIGINAL-A"))
    ledger.add_evidence(EvidenceRecord("E1", "S1", "x"))
    ledger.add_evidence(EvidenceRecord("E2", "S2", "x"))
    ledger.add_claim(Claim("C1", "claim", evidence_ids=["E1", "E2"]))
    assert ledger.reconcile("C1") == ClaimStatus.VERIFIED_PRIMARY


def test_independent_primary_sources_corroborate():
    ledger = ClaimLedger()
    ledger.add_source(source("S1", "A"))
    ledger.add_source(source("S2", "B"))
    ledger.add_evidence(EvidenceRecord("E1", "S1", "x"))
    ledger.add_evidence(EvidenceRecord("E2", "S2", "y"))
    ledger.add_claim(Claim("C1", "claim", evidence_ids=["E1", "E2"]))
    assert ledger.reconcile("C1") == ClaimStatus.VERIFIED_CORROBORATED


def test_critical_claim_without_evidence_is_gap():
    ledger = ClaimLedger()
    ledger.add_claim(Claim("C1", "critical", critical=True))
    assert ledger.reconcile("C1") == ClaimStatus.EVIDENCE_GAP
