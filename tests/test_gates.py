from vtb.claims import ClaimLedger
from vtb.gates import publication_gate
from vtb.models import Claim


def test_publication_blocks_critical_gap_and_missing_red_team():
    ledger = ClaimLedger()
    ledger.add_claim(Claim("C1", "acusação material", critical=True))
    ledger.reconcile("C1")
    gate = publication_gate(ledger, red_team_done=False)
    assert not gate.passed
    assert any("C1" in reason for reason in gate.reasons)
    assert "RED_TEAM_NOT_COMPLETED" in gate.reasons
