from __future__ import annotations

from dataclasses import dataclass, field

from .claims import ClaimLedger
from .signals import RiskSignal


@dataclass(slots=True)
class QAFinding:
    code: str
    passed: bool
    detail: str


@dataclass(slots=True)
class QAReport:
    findings: list[QAFinding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.findings)


def run_case_qa(
    ledger: ClaimLedger,
    signals: list[RiskSignal],
    *,
    red_team_done: bool,
    legal_review_done: bool,
) -> QAReport:
    report = QAReport()
    unsupported_critical = [
        claim.claim_id for claim in ledger.claims.values() if claim.critical and not claim.evidence_ids
    ]
    report.findings.append(
        QAFinding("CRITICAL_CLAIMS_HAVE_EVIDENCE", not unsupported_critical, ",".join(unsupported_critical) or "ok")
    )
    unsupported_signals = [signal.signal_id for signal in signals if not signal.evidence_ids]
    report.findings.append(
        QAFinding("SIGNALS_HAVE_EVIDENCE", not unsupported_signals, ",".join(unsupported_signals) or "ok")
    )
    report.findings.append(QAFinding("RED_TEAM_DONE", red_team_done, "required before sensitive publication"))
    legal_sensitive = any(claim.legal_sensitive for claim in ledger.claims.values()) or any(
        signal.legal_validation_required for signal in signals
    )
    report.findings.append(
        QAFinding("LEGAL_REVIEW_WHEN_NEEDED", (not legal_sensitive) or legal_review_done, "legal-sensitive content gate")
    )
    return report
