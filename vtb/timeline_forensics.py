from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class TimelineEvent:
    event_id: str
    event_date: date
    event_type: str
    entity_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    description: str = ""


def temporal_order_signal(
    earlier: TimelineEvent,
    later: TimelineEvent,
    *,
    expected_relation: str,
) -> RiskSignal | None:
    if earlier.event_date <= later.event_date:
        return None
    return RiskSignal(
        signal_id=f"TIME-ORDER-{earlier.event_id}-{later.event_id}",
        category=SignalCategory.DOCUMENT,
        title="Ordem temporal incompatível com a relação esperada",
        description=(
            f"Evento {earlier.event_id} ({earlier.event_date}) ocorreu depois de "
            f"{later.event_id} ({later.event_date}), embora esperado: {expected_relation}."
        ),
        severity=SignalSeverity.HIGH,
        entity_ids=sorted(set(earlier.entity_ids + later.entity_ids)),
        evidence_ids=sorted(set(earlier.evidence_ids + later.evidence_ids)),
        method="temporal ordering constraint",
        false_positive_risk="medium",
        alternative_explanations=["data de publicação diferente da data do ato", "retificação", "erro de indexação"],
    )


def events_by_entity(events: list[TimelineEvent], entity_id: str) -> list[TimelineEvent]:
    return sorted((event for event in events if entity_id in event.entity_ids), key=lambda event: event.event_date)
