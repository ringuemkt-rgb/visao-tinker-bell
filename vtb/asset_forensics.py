from __future__ import annotations

from dataclasses import dataclass

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class AssetSnapshot:
    entity_id: str
    year: int
    declared_value: float
    evidence_ids: tuple[str, ...]
    source_scope: str
    methodology: str = "declared assets"


def reconcile_asset_variation(
    earlier: AssetSnapshot,
    later: AssetSnapshot,
    review_change_ratio: float = 1.0,
) -> RiskSignal | None:
    if earlier.entity_id != later.entity_id:
        raise ValueError("asset snapshots must belong to the same resolved entity")
    if earlier.source_scope != later.source_scope:
        return RiskSignal(
            signal_id=f"ASSET-NONCOMPARABLE-{earlier.entity_id}-{earlier.year}-{later.year}",
            category=SignalCategory.ASSET,
            title="Série patrimonial não comparável",
            description="Os snapshots usam universos/fontes incompatíveis; não calcular variação conclusiva.",
            severity=SignalSeverity.INFO,
            entity_ids=[earlier.entity_id],
            evidence_ids=sorted(set(earlier.evidence_ids + later.evidence_ids)),
            method="comparability gate",
            false_positive_risk="low",
        )
    baseline = abs(earlier.declared_value)
    if baseline == 0:
        return None
    ratio = (later.declared_value - earlier.declared_value) / baseline
    if abs(ratio) < review_change_ratio:
        return None
    return RiskSignal(
        signal_id=f"ASSET-VARIATION-{earlier.entity_id}-{earlier.year}-{later.year}",
        category=SignalCategory.ASSET,
        title="Variação patrimonial declarada para reconciliação",
        description=f"Variação relativa={ratio:.2%}; exige composição item a item e fontes de renda/alienação públicas.",
        severity=SignalSeverity.MEDIUM,
        entity_ids=[earlier.entity_id],
        evidence_ids=sorted(set(earlier.evidence_ids + later.evidence_ids)),
        method="same-scope declared-asset comparison",
        threshold={"review_change_ratio": review_change_ratio},
        false_positive_risk="high",
        alternative_explanations=["compra/venda declarada", "financiamento", "reavaliação", "mudança de composição"],
        legal_validation_required=True,
    )
