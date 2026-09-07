from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MoneyStage(StrEnum):
    ESTIMATED = "ESTIMATED"
    AWARDED = "AWARDED"
    CONTRACTED = "CONTRACTED"
    AMENDED = "AMENDED"
    COMMITTED = "COMMITTED"  # empenhado
    LIQUIDATED = "LIQUIDATED"
    PAID = "PAID"
    EXECUTED = "EXECUTED"


@dataclass(slots=True)
class MoneyRecord:
    record_id: str
    stage: MoneyStage
    amount: float
    source_id: str
    date: str | None = None
    contract_id: str | None = None
    notes: str = ""


class MoneyFlow:
    def __init__(self, records: list[MoneyRecord] | None = None):
        self.records = records or []

    def add(self, record: MoneyRecord) -> None:
        if record.amount < 0:
            raise ValueError("amount must be non-negative")
        self.records.append(record)

    def totals_by_stage(self) -> dict[MoneyStage, float]:
        totals: dict[MoneyStage, float] = {}
        for record in self.records:
            totals[record.stage] = totals.get(record.stage, 0.0) + record.amount
        return totals

    def paid_total(self) -> float:
        return self.totals_by_stage().get(MoneyStage.PAID, 0.0)

    def naive_sum_is_invalid(self) -> float:
        """Exposes the number only so callers can demonstrate why stage totals must not be added as spend."""
        return sum(record.amount for record in self.records)

    def consistency_warnings(self) -> list[str]:
        totals = self.totals_by_stage()
        warnings: list[str] = []
        paid = totals.get(MoneyStage.PAID, 0.0)
        liquidated = totals.get(MoneyStage.LIQUIDATED, 0.0)
        committed = totals.get(MoneyStage.COMMITTED, 0.0)
        contracted = totals.get(MoneyStage.CONTRACTED, 0.0) + totals.get(MoneyStage.AMENDED, 0.0)
        if liquidated and paid > liquidated:
            warnings.append("PAID_GT_LIQUIDATED_RECONCILE_SCOPE")
        if committed and liquidated > committed:
            warnings.append("LIQUIDATED_GT_COMMITTED_RECONCILE_SCOPE")
        if contracted and paid > contracted:
            warnings.append("PAID_GT_CONTRACTED_RECONCILE_ADDITIVES_AND_SCOPE")
        return warnings
