from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LinkageCandidate:
    left_id: str
    right_id: str
    probability: float
    compared_fields: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    model_id: str = ""
    status: str = "CANDIDATE_MATCH"


def classify_candidate(candidate: LinkageCandidate, review_threshold: float = 0.8) -> str:
    if not 0 <= candidate.probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    if candidate.probability >= review_threshold:
        return "HIGH_PRIORITY_HUMAN_REVIEW"
    return "LOW_PRIORITY_HUMAN_REVIEW"


def can_auto_merge(candidate: LinkageCandidate) -> bool:
    """Probabilistic linkage never auto-merges identity in sensitive investigations."""
    return False


@dataclass(slots=True)
class LinkageModelManifest:
    model_id: str
    engine: str
    version: str
    fields: tuple[str, ...]
    training_scope: str = ""
    calibration_notes: str = ""
    false_match_reviewed: bool = False
    missed_match_reviewed: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
