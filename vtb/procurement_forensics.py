from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import isfinite

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True)
class ProcurementRecord:
    procurement_id: str
    supplier_id: str
    amount: float
    evidence_ids: list[str]
    procedure_type: str = ""
    bidders: int | None = None
    publication_date: str | None = None
    award_date: str | None = None
    object_description: str = ""
    emergency: bool = False
    amendments: int = 0
    metadata: dict[str, object] = field(default_factory=dict)


def supplier_hhi(records: list[ProcurementRecord]) -> float | None:
    """HHI no universo fornecido. Mede concentração; não prova cartel ou direcionamento."""
    totals: dict[str, float] = defaultdict(float)
    for row in records:
        if isfinite(row.amount) and row.amount > 0:
            totals[row.supplier_id] += row.amount
    total = sum(totals.values())
    if total <= 0:
        return None
    return sum((value / total * 100) ** 2 for value in totals.values())


def concentration_signal(records: list[ProcurementRecord], hhi_review_threshold: float = 2500.0) -> RiskSignal | None:
    hhi = supplier_hhi(records)
    if hhi is None or hhi < hhi_review_threshold:
        return None
    evidence_ids = sorted({e for row in records for e in row.evidence_ids})
    return RiskSignal(
        signal_id="PROC-SUPPLIER-CONCENTRATION",
        category=SignalCategory.PROCUREMENT,
        title="Concentração de fornecedores no universo analisado",
        description=f"HHI={hhi:.1f}; requer avaliação do mercado, objeto e universo antes de qualquer inferência.",
        severity=SignalSeverity.MEDIUM,
        evidence_ids=evidence_ids,
        method="HHI por valor adjudicado/contratado no dataset informado",
        threshold={"hhi_review_threshold": hhi_review_threshold},
        false_positive_risk="high",
        alternative_explanations=["mercado naturalmente concentrado", "objeto especializado", "dataset incompleto"],
    )


def low_competition_signals(records: list[ProcurementRecord], review_bidders_below: int = 2) -> list[RiskSignal]:
    out: list[RiskSignal] = []
    for row in records:
        if row.bidders is None or row.bidders >= review_bidders_below:
            continue
        out.append(
            RiskSignal(
                signal_id=f"PROC-LOW-COMPETITION-{row.procurement_id}",
                category=SignalCategory.PROCUREMENT,
                title="Competição reduzida",
                description=f"Procedimento {row.procurement_id} registrou {row.bidders} participante(s).",
                severity=SignalSeverity.MEDIUM,
                entity_ids=[row.supplier_id],
                evidence_ids=row.evidence_ids,
                method="contagem de participantes no procedimento",
                threshold={"review_bidders_below": review_bidders_below},
                false_positive_risk="high",
                alternative_explanations=["mercado restrito", "objeto especializado", "desistência legítima"],
            )
        )
    return out


def repeated_emergency_signal(records: list[ProcurementRecord], review_count: int = 3) -> RiskSignal | None:
    emergency = [row for row in records if row.emergency]
    if len(emergency) < review_count:
        return None
    return RiskSignal(
        signal_id="PROC-REPEATED-EMERGENCY",
        category=SignalCategory.PROCUREMENT,
        title="Contratações emergenciais recorrentes",
        description=f"Foram localizados {len(emergency)} registros emergenciais no universo informado.",
        severity=SignalSeverity.HIGH,
        evidence_ids=sorted({e for row in emergency for e in row.evidence_ids}),
        method="contagem temporal de procedimentos classificados como emergenciais",
        threshold={"review_count": review_count},
        false_positive_risk="medium",
        alternative_explanations=["desastre", "continuidade de serviço essencial", "mudança regulatória"],
        legal_validation_required=True,
    )


def winner_recurrence_signal(records: list[ProcurementRecord], minimum_wins: int = 4) -> RiskSignal | None:
    wins = Counter(row.supplier_id for row in records)
    recurrent = {supplier: count for supplier, count in wins.items() if count >= minimum_wins}
    if not recurrent:
        return None
    evidence_ids = sorted({e for row in records if row.supplier_id in recurrent for e in row.evidence_ids})
    detail = ", ".join(f"{supplier}:{count}" for supplier, count in sorted(recurrent.items()))
    return RiskSignal(
        signal_id="PROC-WINNER-RECURRENCE",
        category=SignalCategory.PROCUREMENT,
        title="Recorrência de vencedor",
        description=f"Fornecedores com recorrência acima do limiar: {detail}.",
        severity=SignalSeverity.LOW,
        entity_ids=sorted(recurrent),
        evidence_ids=evidence_ids,
        method="frequência de vitórias no universo informado",
        threshold={"minimum_wins": minimum_wins},
        false_positive_risk="high",
        alternative_explanations=["melhor preço recorrente", "mercado pequeno", "especialização"],
    )


def threshold_proximity_signal(
    record: ProcurementRecord,
    legal_threshold: float,
    tolerance_ratio: float = 0.02,
) -> RiskSignal | None:
    """Só opera com limiar fornecido e previamente validado para o período/norma do caso."""
    if legal_threshold <= 0 or tolerance_ratio <= 0:
        raise ValueError("threshold and tolerance must be positive")
    lower = legal_threshold * (1 - tolerance_ratio)
    if not lower <= record.amount < legal_threshold:
        return None
    return RiskSignal(
        signal_id=f"PROC-THRESHOLD-PROXIMITY-{record.procurement_id}",
        category=SignalCategory.PROCUREMENT,
        title="Valor próximo a limiar jurídico informado",
        description="Proximidade de limiar é triagem; não demonstra fracionamento ou intenção.",
        severity=SignalSeverity.MEDIUM,
        entity_ids=[record.supplier_id],
        evidence_ids=record.evidence_ids,
        method="distância percentual a limiar externo validado",
        threshold={"legal_threshold": legal_threshold, "tolerance_ratio": tolerance_ratio},
        false_positive_risk="high",
        alternative_explanations=["preço de mercado", "escopo legítimo", "coincidência"],
        legal_validation_required=True,
    )
