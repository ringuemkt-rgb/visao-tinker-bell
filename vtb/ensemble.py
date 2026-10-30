from __future__ import annotations

from dataclasses import dataclass

from .signals import RiskSignal


@dataclass(slots=True, frozen=True)
class EnsembleResult:
    review_priority: str
    independent_families: int
    evidence_count: int
    contributing_signal_ids: tuple[str, ...]
    explanation: tuple[str, ...]


def combine_signals(
    signals: list[RiskSignal], *, evidence_lineage: dict[str, str] | None = None
) -> EnsembleResult:
    """Combina sinais para priorização de revisão, nunca para estimar probabilidade de corrupção."""
    families = {signal.category for signal in signals}
    evidence = {item for signal in signals for item in signal.evidence_ids}
    independent = (
        {evidence_lineage[e] for e in evidence if evidence_lineage.get(e)}
        if evidence_lineage is not None else set()
    )
    severe = sum(signal.severity in {"HIGH", "CRITICAL_REVIEW"} for signal in signals)
    if len(families) >= 3 and len(independent) >= 4 and severe >= 1:
        priority = "P1_DEEP_REVIEW"
    elif len(families) >= 2 and len(independent) >= 2:
        priority = "P2_PRIORITY_REVIEW"
    elif signals:
        priority = "P3_ROUTINE_REVIEW"
    else:
        priority = "P4_NO_SIGNAL"
    explanation = tuple(
        f"{signal.signal_id}: {signal.title} | false_positive_risk={signal.false_positive_risk}"
        for signal in signals
    )
    return EnsembleResult(priority, len(families), len(independent), tuple(s.signal_id for s in signals), explanation)
