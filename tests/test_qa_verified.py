from vtb.claims import ClaimLedger
from vtb.models import Claim
from vtb.qa import run_case_qa
from vtb.signals import RiskSignal, SignalCategory


def test_qa_rejects_unverified_claim_and_signal_ids():
    ledger = ClaimLedger()
    ledger.add_claim(Claim("CLAIM", "Synthetic critical proposition", critical=True,
                           evidence_ids=["EVIDENCE-TEXT"]))
    signal = RiskSignal("SIG", SignalCategory.DOCUMENT, "Alert", "Synthetic",
                        evidence_ids=["EVIDENCE-TEXT"])
    report = run_case_qa(ledger, [signal], red_team_done=True, legal_review_done=True)
    assert not report.passed
    assert {x.code for x in report.findings if not x.passed} == {
        "CRITICAL_CLAIMS_HAVE_VERIFIED_EVIDENCE",
        "SIGNALS_HAVE_VERIFIED_EVIDENCE",
    }
    reviewed = run_case_qa(ledger, [signal], red_team_done=True, legal_review_done=True,
                           verified_evidence_ids={"EVIDENCE-TEXT"})
    assert reviewed.passed
