from __future__ import annotations

from dataclasses import dataclass

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class ElectoralTransaction:
    candidate_id: str
    counterparty_id: str
    transaction_type: str
    amount: float
    election_year: int
    evidence_ids: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class PublicContractParty:
    supplier_id: str
    public_body_id: str
    contract_id: str
    amount: float
    year: int
    evidence_ids: tuple[str, ...]


def electoral_public_contract_overlaps(
    transactions: list[ElectoralTransaction],
    contracts: list[PublicContractParty],
    year_window: int = 2,
) -> list[RiskSignal]:
    """Sobreposição temporal gera pergunta de conflito/nexo; não demonstra troca de favores."""
    by_supplier: dict[str, list[PublicContractParty]] = {}
    for contract in contracts:
        by_supplier.setdefault(contract.supplier_id, []).append(contract)
    signals: list[RiskSignal] = []
    for tx in transactions:
        matches = [
            contract
            for contract in by_supplier.get(tx.counterparty_id, [])
            if abs(contract.year - tx.election_year) <= year_window
        ]
        if not matches:
            continue
        evidence_ids = sorted(set(tx.evidence_ids).union(*(set(match.evidence_ids) for match in matches)))
        signals.append(
            RiskSignal(
                signal_id=f"ELEC-CONTRACT-OVERLAP-{tx.candidate_id}-{tx.counterparty_id}-{tx.election_year}",
                category=SignalCategory.ELECTORAL,
                title="Sobreposição entre contraparte eleitoral e fornecedor público",
                description="A contraparte eleitoral também aparece em contratos públicos dentro da janela temporal.",
                severity=SignalSeverity.MEDIUM,
                entity_ids=[tx.candidate_id, tx.counterparty_id],
                evidence_ids=evidence_ids,
                method="temporal entity overlap",
                threshold={"year_window": year_window},
                false_positive_risk="high",
                alternative_explanations=["fornecedor habitual", "relação comercial legítima", "coincidência temporal"],
                legal_validation_required=True,
            )
        )
    return signals
