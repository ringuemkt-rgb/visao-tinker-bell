from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProceedingStatus(StrEnum):
    DISCOVERY_ONLY = "DISCOVERY_ONLY"
    FILED = "FILED"
    PENDING = "PENDING"
    PRELIMINARY_DECISION = "PRELIMINARY_DECISION"
    DECIDED = "DECIDED"
    APPEALED = "APPEALED"
    FINAL = "FINAL"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True, frozen=True)
class ControlProceeding:
    proceeding_id: str
    authority: str
    status: ProceedingStatus
    evidence_ids: tuple[str, ...]
    decision_summary: str = ""
    finality_confirmed: bool = False

    def supports_final_liability_claim(self) -> bool:
        return self.status == ProceedingStatus.FINAL and self.finality_confirmed and bool(self.evidence_ids)

    def semantic_label(self) -> str:
        if self.supports_final_liability_claim():
            return "FINAL_DECISION_DOCUMENTED"
        if self.status in {ProceedingStatus.FILED, ProceedingStatus.PENDING, ProceedingStatus.DISCOVERY_ONLY}:
            return "PROCEEDING_IS_NOT_FINDING"
        return "STATUS_REQUIRES_PROCEDURAL_CONTEXT"
