from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EntityCandidate:
    entity_id: str
    name: str
    tax_id: str | None = None
    birth_or_open_date: str | None = None
    municipality: str | None = None
    role_or_cnae: str | None = None


@dataclass(slots=True)
class MatchResult:
    left_id: str
    right_id: str
    score: float
    status: str
    reasons: list[str]


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def compare(left: EntityCandidate, right: EntityCandidate) -> MatchResult:
    score = 0.0
    reasons: list[str] = []
    if left.tax_id and right.tax_id:
        if left.tax_id == right.tax_id:
            return MatchResult(left.entity_id, right.entity_id, 1.0, "MATCH_CONFIRMED", ["EXACT_TAX_ID"])
        return MatchResult(left.entity_id, right.entity_id, 0.0, "MATCH_REJECTED", ["CONFLICTING_TAX_ID"])
    if normalize_text(left.name) == normalize_text(right.name):
        score += 0.45
        reasons.append("EXACT_NORMALIZED_NAME")
    if left.birth_or_open_date and left.birth_or_open_date == right.birth_or_open_date:
        score += 0.25
        reasons.append("MATCH_DATE")
    if left.municipality and normalize_text(left.municipality) == normalize_text(right.municipality):
        score += 0.15
        reasons.append("MATCH_MUNICIPALITY")
    if left.role_or_cnae and normalize_text(left.role_or_cnae) == normalize_text(right.role_or_cnae):
        score += 0.15
        reasons.append("MATCH_ROLE_OR_CNAE")
    if score >= 0.85:
        status = "MATCH_PROBABLE"
    elif score >= 0.60:
        status = "MATCH_POSSIBLE"
    elif score > 0:
        status = "MATCH_UNCERTAIN"
    else:
        status = "MATCH_REJECTED"
    return MatchResult(left.entity_id, right.entity_id, round(score, 3), status, reasons)
