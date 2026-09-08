from __future__ import annotations

from dataclasses import dataclass, field

from .signals import RiskSignal, triage_band


@dataclass(slots=True)
class IntegrityAssessment:
    case_id: str
    signals: list[RiskSignal] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    counterevidence: list[str] = field(default_factory=list)

    def add_signal(self, signal: RiskSignal | None) -> None:
        if signal is not None:
            self.signals.append(signal)

    def add_signals(self, signals: list[RiskSignal]) -> None:
        self.signals.extend(signals)

    def priority(self) -> str:
        return triage_band(self.signals)

    def can_describe_as_corruption(self) -> bool:
        """VTB não automatiza imputação de corrupção a partir de sinais."""
        return False

    def summary(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "triage_priority": self.priority(),
            "signals": [signal.to_dict() for signal in self.signals],
            "contradictions": self.contradictions,
            "evidence_gaps": self.evidence_gaps,
            "counterevidence": self.counterevidence,
            "automatic_corruption_label": False,
        }
