from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class PriceObservation:
    item_key: str
    unit_price: float
    evidence_id: str
    date: str
    location: str
    quantity: float | None = None
    specification: str = ""


def comparable_prices(rows: list[PriceObservation], item_key: str, specification: str) -> list[PriceObservation]:
    return [row for row in rows if row.item_key == item_key and row.specification == specification and row.unit_price > 0]


def price_anomaly_signal(
    target: PriceObservation,
    benchmarks: list[PriceObservation],
    review_ratio: float = 1.5,
    minimum_comparables: int = 3,
) -> RiskSignal | None:
    peers = [
        row
        for row in comparable_prices(benchmarks, target.item_key, target.specification)
        if row.evidence_id != target.evidence_id
    ]
    if len(peers) < minimum_comparables:
        return None
    benchmark = median(row.unit_price for row in peers)
    if benchmark <= 0 or target.unit_price / benchmark < review_ratio:
        return None
    evidence_ids = sorted({target.evidence_id, *(row.evidence_id for row in peers)})
    return RiskSignal(
        signal_id=f"PRICE-ANOMALY-{target.item_key}-{target.evidence_id}",
        category=SignalCategory.PRICE,
        title="Preço unitário acima da mediana de comparáveis",
        description=(
            f"Preço alvo/mediana={target.unit_price / benchmark:.2f}x. "
            "É necessário validar quantidade, frete, data, marca, condições e escopo."
        ),
        severity=SignalSeverity.MEDIUM,
        evidence_ids=evidence_ids,
        method="median of normalized comparable observations",
        threshold={"review_ratio": review_ratio, "minimum_comparables": minimum_comparables},
        false_positive_risk="high",
        alternative_explanations=["frete", "prazo", "marca/modelo", "escala", "localidade", "condição comercial"],
    )
