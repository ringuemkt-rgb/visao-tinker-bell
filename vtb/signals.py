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

    def publication_safe(self) -> bool:
        return bool(self.evidence_ids) and self.status == "ANOMALY_FOR_VERIFICATION"


def triage_band(signals: list[RiskSignal]) -> str:
    """Prioridade de revisão, nunca probabilidade de corrupção ou culpa."""
    weights = {
        SignalSeverity.INFO: 0,
        SignalSeverity.LOW: 1,
        SignalSeverity.MEDIUM: 2,
        SignalSeverity.HIGH: 4,
        SignalSeverity.CRITICAL_REVIEW: 6,
    }
    points = sum(weights[s.severity] for s in signals)
    independent_evidence = len({e for signal in signals for e in signal.evidence_ids})
    if points >= 12 and independent_evidence >= 4:
        return "P1_DEEP_REVIEW"
    if points >= 6 and independent_evidence >= 2:
        return "P2_PRIORITY_REVIEW"
    if signals:
        return "P3_ROUTINE_REVIEW"
    return "P4_NO_SIGNAL"
