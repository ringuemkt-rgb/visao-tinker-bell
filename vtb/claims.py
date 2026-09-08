from __future__ import annotations

from dataclasses import dataclass, field

from .models import Claim, ClaimStatus, EvidenceRecord, SourceQuality, SourceRecord

_PRIMARY = {SourceQuality.S5_OFFICIAL_PRIMARY, SourceQuality.S6_ORIGINAL_SIGNED_ACT}


@dataclass
class ClaimLedger:
    claims: dict[str, Claim] = field(default_factory=dict)
    evidence: dict[str, EvidenceRecord] = field(default_factory=dict)
    sources: dict[str, SourceRecord] = field(default_factory=dict)

    def add_source(self, source: SourceRecord) -> None:
        self.sources[source.source_id] = source

    def add_evidence(self, evidence: EvidenceRecord) -> None:
        if evidence.source_id not in self.sources:
            raise KeyError(f"unknown source: {evidence.source_id}")
        self.evidence[evidence.evidence_id] = evidence

    def add_claim(self, claim: Claim) -> None:
        if claim.claim_id in self.claims:
            raise ValueError(f"duplicate claim: {claim.claim_id}")
        self.claims[claim.claim_id] = claim

    def supporting_sources(self, claim_id: str) -> list[SourceRecord]:
        claim = self.claims[claim_id]
        return [self.sources[self.evidence[eid].source_id] for eid in claim.evidence_ids if eid in self.evidence]

    def independent_lineages(self, claim_id: str) -> set[str]:
        return {source.lineage_key() for source in self.supporting_sources(claim_id)}

    def has_primary_support(self, claim_id: str) -> bool:
        return any(source.quality in _PRIMARY for source in self.supporting_sources(claim_id))

    def suggested_status(self, claim_id: str) -> ClaimStatus:
        claim = self.claims[claim_id]
        if claim.contradicting_evidence_ids:
            return ClaimStatus.DOCUMENT_CONFLICT
        sources = self.supporting_sources(claim_id)
        if not sources:
            return ClaimStatus.EVIDENCE_GAP if claim.critical else ClaimStatus.UNVERIFIED
        if self.has_primary_support(claim_id):
            if len(self.independent_lineages(claim_id)) >= 2:
                return ClaimStatus.VERIFIED_CORROBORATED
            return ClaimStatus.VERIFIED_PRIMARY
        return ClaimStatus.PARTIALLY_SUPPORTED

    def reconcile(self, claim_id: str) -> ClaimStatus:
        status = self.suggested_status(claim_id)
        self.claims[claim_id].status = status
        return status

    def critical_unsupported(self) -> list[Claim]:
        bad = {
            ClaimStatus.UNVERIFIED,
            ClaimStatus.EVIDENCE_GAP,
            ClaimStatus.DOCUMENT_CONFLICT,
            ClaimStatus.ENTITY_MATCH_UNCERTAIN,
            ClaimStatus.REPRODUCIBILITY_WARNING,
        }
        return [claim for claim in self.claims.values() if claim.critical and claim.status in bad]
