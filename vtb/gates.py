from __future__ import annotations

from dataclasses import dataclass, field

from .claims import ClaimLedger
from .models import ClaimStatus, MissionState


@dataclass(slots=True)
class GateResult:
    passed: bool
    code: str
    reasons: list[str] = field(default_factory=list)


def evidence_gate(ledger: ClaimLedger) -> GateResult:
    unsupported = ledger.critical_unsupported()
    return GateResult(
        passed=not unsupported,
        code="EVIDENCE_GATE",
        reasons=[f"{claim.claim_id}:{claim.status}" for claim in unsupported],
    )


def publication_gate(ledger: ClaimLedger, red_team_done: bool, legal_review_done: bool = True) -> GateResult:
    reasons: list[str] = []
    eg = evidence_gate(ledger)
    reasons.extend(eg.reasons)
    if not red_team_done:
        reasons.append("RED_TEAM_NOT_COMPLETED")
    if not legal_review_done and any(c.legal_sensitive for c in ledger.claims.values()):
        reasons.append("LEGAL_REVIEW_REQUIRED")
    for claim in ledger.claims.values():
        if claim.critical and claim.status in {ClaimStatus.INFERENCE, ClaimStatus.ESTIMATE}:
            reasons.append(f"CRITICAL_NONFACTUAL_CLAIM:{claim.claim_id}")
    return GateResult(not reasons, "PUBLICATION_GATE", reasons)


def final_state(gate: GateResult, has_material_findings: bool, has_gaps: bool) -> MissionState:
    if not gate.passed:
        return MissionState.QUARANTINED
    if not has_material_findings and has_gaps:
        return MissionState.INCONCLUSIVE
    if has_gaps:
        return MissionState.READY_WITH_LIMITATIONS
    return MissionState.READY
