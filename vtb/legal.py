from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LegalAssessment:
    claim_id: str
    rule: str | None = None
    rule_version: str | None = None
    consulted_at: str | None = None
    competence_verified: bool = False
    concrete_act_verified: bool = False
    nexus_verified: bool = False
    subjective_element_required: bool = False
    subjective_element_supported: bool = False
    damage_or_advantage_required: bool = False
    damage_or_advantage_supported: bool = False
    counterevidence_checked: bool = False
    jurisprudence_checked: bool = False
    notes: list[str] = field(default_factory=list)

    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.rule or not self.rule_version or not self.consulted_at:
            blockers.append("CURRENT_RULE_NOT_VALIDATED")
        if not self.competence_verified:
            blockers.append("COMPETENCE_NOT_VERIFIED")
        if not self.concrete_act_verified:
            blockers.append("CONCRETE_ACT_NOT_VERIFIED")
        if not self.nexus_verified:
            blockers.append("NEXUS_NOT_VERIFIED")
        if self.subjective_element_required and not self.subjective_element_supported:
            blockers.append("DOLO_OR_SUBJECTIVE_ELEMENT_NOT_SUPPORTED")
        if self.damage_or_advantage_required and not self.damage_or_advantage_supported:
            blockers.append("DAMAGE_OR_ADVANTAGE_NOT_SUPPORTED")
        if not self.counterevidence_checked:
            blockers.append("COUNTEREVIDENCE_NOT_CHECKED")
        if not self.jurisprudence_checked:
            blockers.append("JURISPRUDENCE_NOT_CHECKED")
        return blockers

    @property
    def ready(self) -> bool:
        return not self.blockers()
