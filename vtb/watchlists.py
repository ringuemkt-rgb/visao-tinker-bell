from __future__ import annotations

from dataclasses import dataclass, field

from .ids import stable_id


@dataclass(slots=True, frozen=True)
class WatchTarget:
    target_id: str
    entity_type: str
    label: str
    identifiers: dict[str, tuple[str, ...]] = field(default_factory=dict)
    public_interest_basis: str = ""


@dataclass(slots=True, frozen=True)
class WatchHit:
    hit_id: str
    target_id: str
    source_id: str
    evidence_ids: tuple[str, ...]
    matched_fields: tuple[str, ...]
    confidence: float | None = None
    status: str = "CANDIDATE_MATCH"


def make_watch_hit(
    target: WatchTarget,
    source_id: str,
    evidence_ids: list[str],
    matched_fields: list[str],
    confidence: float | None = None,
) -> WatchHit:
    return WatchHit(
        hit_id=stable_id("WATCH", target.target_id, source_id, *sorted(evidence_ids), *sorted(matched_fields)),
        target_id=target.target_id,
        source_id=source_id,
        evidence_ids=tuple(sorted(set(evidence_ids))),
        matched_fields=tuple(sorted(set(matched_fields))),
        confidence=confidence,
    )


def requires_human_resolution(hit: WatchHit) -> bool:
    return True
