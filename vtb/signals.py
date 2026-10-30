from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class SignalCategory(StrEnum):
    PROCUREMENT = "PROCUREMENT"
    PAYMENT = "PAYMENT"
    CORPORATE = "CORPORATE"
    ELECTORAL = "ELECTORAL"
    ASSET = "ASSET"
    NETWORK = "NETWORK"
    DOCUMENT = "DOCUMENT"
    CONTROL = "CONTROL"
    PRICE = "PRICE"
    STATISTICAL = "STATISTICAL"


class SignalSeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL_REVIEW = "CRITICAL_REVIEW"


@dataclass(slots=True)
class RiskSignal:
    signal_id: str
    category: SignalCategory
    title: str
    description: str
    severity: SignalSeverity = SignalSeverity.INFO
    entity_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    method: str = ""
    threshold: dict[str, Any] = field(default_factory=dict)
    false_positive_risk: str = "unknown"
    alternative_explanations: list[str] = field(default_factory=list)
    legal_validation_required: bool = False
    status: str = "ANOMALY_FOR_VERIFICATION"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def publication_safe(
        self,
        *,
        verified_evidence_ids: set[str] | None = None,
        human_reviewed: bool = False,
        legal_reviewed: bool = False,
    ) -> bool:
        """A textual evidence ID never authorizes publication by itself."""
        return (
            self.status == "ANOMALY_FOR_VERIFICATION"
            and bool(self.evidence_ids)
            and verified_evidence_ids is not None
            and set(self.evidence_ids).issubset(verified_evidence_ids)
            and human_reviewed
            and (not self.legal_validation_required or legal_reviewed)
        )


def triage_band(
    signals: list[RiskSignal], *, evidence_lineage: dict[str, str] | None = None
) -> str:
    """Prioridade de revisão. Sem proveniência, não presumir fontes independentes."""
    weights = {
        SignalSeverity.INFO: 0,
        SignalSeverity.LOW: 1,
        SignalSeverity.MEDIUM: 2,
        SignalSeverity.HIGH: 4,
        SignalSeverity.CRITICAL_REVIEW: 6,
    }
    points = sum(weights[s.severity] for s in signals)
    evidence_ids = {e for signal in signals for e in signal.evidence_ids}
    # Lineage must be supplied from audited source records, not derived from ID names.
    independent_evidence = (
        len({evidence_lineage[e] for e in evidence_ids if evidence_lineage.get(e)})
        if evidence_lineage is not None else 0
    )
    if points >= 12 and independent_evidence >= 4:
        return "P1_DEEP_REVIEW"
    if points >= 6 and independent_evidence >= 2:
        return "P2_PRIORITY_REVIEW"
    if signals:
        return "P3_ROUTINE_REVIEW"
    return "P4_NO_SIGNAL"
