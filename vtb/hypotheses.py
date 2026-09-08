from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceAssessment:
    evidence_id: str
    hypothesis_id: str
    value: str  # C consistent, I inconsistent, N neutral, NA unavailable
    weight: float = 1.0


@dataclass
class CompetingHypotheses:
    hypotheses: dict[str, str] = field(default_factory=dict)
    assessments: list[EvidenceAssessment] = field(default_factory=list)

    def add_hypothesis(self, hypothesis_id: str, statement: str) -> None:
        self.hypotheses[hypothesis_id] = statement

    def assess(self, evidence_id: str, hypothesis_id: str, value: str, weight: float = 1.0) -> None:
        if hypothesis_id not in self.hypotheses:
            raise KeyError(hypothesis_id)
        value = value.upper()
        if value not in {"C", "I", "N", "NA"}:
            raise ValueError("assessment value must be C, I, N or NA")
        self.assessments.append(EvidenceAssessment(evidence_id, hypothesis_id, value, weight))

    def inconsistency_score(self, hypothesis_id: str) -> float:
        return sum(a.weight for a in self.assessments if a.hypothesis_id == hypothesis_id and a.value == "I")

    def least_refuted(self) -> list[tuple[str, float]]:
        scores = [(hid, self.inconsistency_score(hid)) for hid in self.hypotheses]
        return sorted(scores, key=lambda item: (item[1], item[0]))

    def falsification_prompts(self) -> list[str]:
        return [f"Que evidência, se localizada, refutaria {hid}: {text}?" for hid, text in self.hypotheses.items()]
