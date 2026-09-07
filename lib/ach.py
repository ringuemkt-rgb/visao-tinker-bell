"""Analysis of Competing Hypotheses — Visão Tinker Bell v7.

A hipótese de saída é a MENOS REFUTADA, não a mais 'provável'.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Mark = Literal["C", "I", "NA"]

DEFAULT_HYPOTHESES = {
    "H0": "Conduta compatível com registro público regular",
    "H1": "Anomalia estatística/documental sem irregularidade demonstrada",
    "H2": "Irregularidade possível — exige documento primário adicional",
    "H3": "Evidência pública insuficiente para concluir",
}


@dataclass
class EvidenceRow:
    eid: str
    text: str
    marks: dict[str, Mark]
    weight: float = 1.0


@dataclass
class ACHMatrix:
    hypotheses: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_HYPOTHESES))
    rows: list[EvidenceRow] = field(default_factory=list)

    def add(self, eid: str, text: str, marks: dict[str, Mark], weight: float = 1.0) -> None:
        missing = set(self.hypotheses) - set(marks)
        for h in missing:
            marks[h] = "NA"
        self.rows.append(EvidenceRow(eid=eid, text=text, marks=marks, weight=weight))

    def inconsistency_scores(self) -> dict[str, float]:
        scores = {h: 0.0 for h in self.hypotheses}
        for row in self.rows:
            for h, mark in row.marks.items():
                if mark == "I":
                    scores[h] += row.weight
        return scores

    def least_refuted(self) -> tuple[str, str, float]:
        scores = self.inconsistency_scores()
        hid = min(scores, key=lambda k: scores[k])
        return hid, self.hypotheses[hid], scores[hid]

    def markdown(self) -> str:
        hyps = list(self.hypotheses)
        header = "| Evidência | " + " | ".join(hyps) + " |"
        sep = "|-----------|" + "|".join(["---"] * len(hyps)) + "|"
        lines = [header, sep]
        for row in self.rows:
            cells = " | ".join(row.marks.get(h, "NA") for h in hyps)
            lines.append(f"| {row.eid}: {row.text} | {cells} |")
        scores = self.inconsistency_scores()
        hid, label, val = self.least_refuted()
        lines.append("")
        lines.append("Inconsistências ponderadas: " + ", ".join(f"{h}={scores[h]:.1f}" for h in hyps))
        lines.append(f"**Hipótese menos refutada:** {hid} — {label} (score I={val:.1f})")
        lines.append("")
        lines.append("C = consistente · I = inconsistente · NA = não aplicável")
        return "\n".join(lines)
