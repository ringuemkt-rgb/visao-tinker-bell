from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class ClaimStatus(StrEnum):
    VERIFIED_PRIMARY = "VERIFIED_PRIMARY"
    VERIFIED_CORROBORATED = "VERIFIED_CORROBORATED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    INFERENCE = "INFERENCE"
    ESTIMATE = "ESTIMATE"
    NOT_DEMONSTRATED = "NOT_DEMONSTRATED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    DOCUMENT_CONFLICT = "DOCUMENT_CONFLICT"
    ENTITY_MATCH_UNCERTAIN = "ENTITY_MATCH_UNCERTAIN"
    EVIDENCE_GAP = "EVIDENCE_GAP"
    LEGAL_VALIDATION_REQUIRED = "LEGAL_VALIDATION_REQUIRED"
    REPRODUCIBILITY_WARNING = "REPRODUCIBILITY_WARNING"


class SourceQuality(StrEnum):
    S0_UNKNOWN = "S0_UNKNOWN"
    S1_INFORMAL = "S1_INFORMAL"
    S2_SECONDARY = "S2_SECONDARY"
    S3_INSTITUTIONAL_DERIVATIVE = "S3_INSTITUTIONAL_DERIVATIVE"
    S4_OFFICIAL_STRUCTURED = "S4_OFFICIAL_STRUCTURED"
    S5_OFFICIAL_PRIMARY = "S5_OFFICIAL_PRIMARY"
    S6_ORIGINAL_SIGNED_ACT = "S6_ORIGINAL_SIGNED_ACT"


class SourceHealth(StrEnum):
    HEALTHY = "HEALTHY"
    PARTIAL = "PARTIAL"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    UNKNOWN = "UNKNOWN"


class MissionState(StrEnum):
    INTAKE = "INTAKE"
    SCOPE = "SCOPE"
    PLAN = "PLAN"
    RESEARCH = "RESEARCH"
    INGEST = "INGEST"
    RESOLVE = "RESOLVE"
    ANALYZE = "ANALYZE"
    HYPOTHESIS = "HYPOTHESIS"
    FALSIFY = "FALSIFY"
    GAP_ANALYSIS = "GAP_ANALYSIS"
    RED_TEAM = "RED_TEAM"
    SYNTHESIS = "SYNTHESIS"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    QA = "QA"
    DECISION = "DECISION"
    READY = "READY"
    READY_WITH_LIMITATIONS = "READY_WITH_LIMITATIONS"
    INCONCLUSIVE = "INCONCLUSIVE"
    QUARANTINED = "QUARANTINED"


@dataclass(slots=True)
class SourceRecord:
    source_id: str
    title: str
    issuer: str
    url: str
    quality: SourceQuality = SourceQuality.S0_UNKNOWN
    health: SourceHealth = SourceHealth.UNKNOWN
    publication_date: str | None = None
    retrieved_at: str = field(default_factory=utcnow)
    coverage_period: str | None = None
    query_parameters: dict[str, Any] = field(default_factory=dict)
    original_source_id: str | None = None
    parent_source_id: str | None = None
    sha256: str | None = None
    version: str | None = None
    notes: str = ""

    def lineage_key(self) -> str:
        return self.original_source_id or self.parent_source_id or self.source_id

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    excerpt: str
    locator: str | None = None
    extracted_at: str = field(default_factory=utcnow)
    payload_hash: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Claim:
    claim_id: str
    statement: str
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    materiality: str = "normal"
    critical: bool = False
    legal_sensitive: bool = False
    limitations: list[str] = field(default_factory=list)
    next_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    falsifier: str | None = None
    status: str = "OPEN"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
