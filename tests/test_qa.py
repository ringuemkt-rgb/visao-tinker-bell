from vtb.claims import ClaimLedger
from vtb.models import Claim
from vtb.qa import run_case_qa


def test_qa_blocks_unsupported_critical_claim():
    ledger = ClaimLedger()
    ledger.add_claim(Claim("c1", "claim", critical=True))
    report = run_case_qa(ledger, [], red_team_done=True, legal_review_done=True)
    assert report.passed is False
