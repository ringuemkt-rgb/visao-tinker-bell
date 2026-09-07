from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class PaymentRecord:
    payment_id: str
    supplier_id: str
    amount: Decimal
    payment_date: str
    evidence_ids: tuple[str, ...]
    contract_id: str | None = None
    invoice_number: str | None = None
    commitment_id: str | None = None
    liquidation_id: str | None = None


def duplicate_payment_candidates(payments: list[PaymentRecord]) -> list[RiskSignal]:
    """Detecta duplicidades candidatas por chave forte; exige conferência de estorno/parcelamento."""
    buckets: dict[tuple[str, str, Decimal, str], list[PaymentRecord]] = defaultdict(list)
    for row in payments:
        if not row.invoice_number:
            continue
        key = (row.supplier_id, row.invoice_number, row.amount, row.payment_date)
        buckets[key].append(row)
    signals: list[RiskSignal] = []
    for rows in buckets.values():
        if len(rows) < 2:
            continue
        evidence_ids = sorted({e for row in rows for e in row.evidence_ids})
        signals.append(
            RiskSignal(
                signal_id=f"PAY-DUP-CANDIDATE-{rows[0].supplier_id}-{rows[0].invoice_number}",
                category=SignalCategory.PAYMENT,
                title="Possível pagamento duplicado para conferência",
                description="Mesma chave fornecedor+nota+valor+data apareceu mais de uma vez.",
                severity=SignalSeverity.HIGH,
                entity_ids=[rows[0].supplier_id],
                evidence_ids=evidence_ids,
                method="duplicate key matching",
                false_positive_risk="medium",
                alternative_explanations=["parcelamento", "estorno/reemissão", "duplicidade de publicação"],
            )
        )
    return signals


def orphan_payment_signals(payments: list[PaymentRecord]) -> list[RiskSignal]:
    out: list[RiskSignal] = []
    for row in payments:
        if row.contract_id or row.commitment_id:
            continue
        out.append(
            RiskSignal(
                signal_id=f"PAY-LINKAGE-GAP-{row.payment_id}",
                category=SignalCategory.PAYMENT,
                title="Lacuna de vinculação documental do pagamento",
                description="Pagamento não possui contrato nem empenho vinculados no dataset analisado.",
                severity=SignalSeverity.MEDIUM,
                entity_ids=[row.supplier_id],
                evidence_ids=list(row.evidence_ids),
                method="referential-integrity check",
                false_positive_risk="high",
                alternative_explanations=["dataset incompleto", "identificador incompatível entre sistemas"],
            )
        )
    return out


def summarize_supplier_payments(payments: list[PaymentRecord]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for row in payments:
        totals[row.supplier_id] += row.amount
    return dict(totals)
