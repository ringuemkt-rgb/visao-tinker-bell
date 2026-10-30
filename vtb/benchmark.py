"""Deterministic screening benchmark with synthetic positive and negative controls.

This is a regression benchmark, NOT a measurement of real-world corruption
detection accuracy. Labels refer to mechanically expected audit alerts only.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from decimal import Decimal
from typing import Any

from .serenata_screening import PublicExpense, QuotaPolicy, screen_expenses

VALID_CNPJ = "11222333000181"


def _row(code: str, **overrides: Any) -> PublicExpense:
    payload = {
        "expense_id": code, "actor_id": "SYNTHETIC_ACTOR",
        "issue_date": "2026-06-10", "amount_brl": "25.00",
        "evidence_ids": [f"SYN-{code}"], "supplier_cnpj": VALID_CNPJ,
    }
    payload.update(overrides)
    return PublicExpense.from_dict(payload)


def _corpus() -> list[dict[str, Any]]:
    """Balanced labels deliberately include hard negative examples."""
    rule = QuotaPolicy("FOOD", Decimal(100), date(2026, 1, 1),
                       date(2026, 12, 31), ("SYN-POLICY",))
    return [
        {"id": "invalid-cnpj", "rows": [_row("A", supplier_cnpj="11222333000182")],
         "policies": [], "expected": True},
        {"id": "valid-cnpj", "rows": [_row("B")], "policies": [],
         "expected": False},
        {"id": "status-prior", "rows": [_row("C", supplier_status="BAIXADA",
                                          supplier_status_from="2025-01-01",
                                          supplier_status_evidence_ids=["SYN-REG"])],
         "policies": [], "expected": True},
        {"id": "status-after", "rows": [_row("D", supplier_status="BAIXADA",
                                          supplier_status_from="2027-01-01",
                                          supplier_status_evidence_ids=["SYN-REG"])],
         "policies": [], "expected": False},
        {"id": "same-invoice", "rows": [_row("E", invoice_id="001"),
                                        _row("F", invoice_id="001")],
         "policies": [], "expected": True},
        {"id": "different-invoices", "rows": [_row("G", invoice_id="001"),
                                              _row("H", invoice_id="002")],
         "policies": [], "expected": False},
        {"id": "quota-exceeded", "rows": [_row("I", amount_brl="110", subquota="FOOD")],
         "policies": [rule], "expected": True},
        {"id": "quota-no-policy", "rows": [_row("J", amount_brl="110", subquota="FOOD")],
         "policies": [], "expected": False},
        {"id": "far-same-date", "rows": [
            _row("K", latitude=-12.97, longitude=-38.5, personal_presence_evidenced=True),
            _row("L", latitude=-23.55, longitude=-46.63, personal_presence_evidenced=True)],
         "policies": [], "expected": True},
        {"id": "far-without-presence", "rows": [
            _row("M", latitude=-12.97, longitude=-38.5),
            _row("N", latitude=-23.55, longitude=-46.63)],
         "policies": [], "expected": False},
        {"id": "price-high-comparable", "rows": [
            *[_row(f"P{i}", peer_group="same-specs") for i in range(10)],
            _row("PX", amount_brl="250", peer_group="same-specs")],
         "policies": [], "expected": True},
        {"id": "price-insufficient-sample", "rows": [
            _row("Q1", peer_group="same-specs"),
            _row("QX", amount_brl="250", peer_group="same-specs")],
         "policies": [], "expected": False},
    ]


def run_benchmark() -> dict[str, Any]:
    metrics: Counter[str] = Counter()
    cases: list[dict[str, Any]] = []
    for sample in _corpus():
        result = screen_expenses(sample["rows"], quota_policies=sample["policies"])
        actual = bool(result["signals"])
        expected = sample["expected"]
        label = "TP" if actual and expected else (
            "TN" if not actual and not expected else "FP" if actual else "FN"
        )
        metrics[label] += 1
        cases.append({
            "id": sample["id"],
            "expected_alert": expected,
            "observed_alert": actual,
            "result": label,
            "signal_ids": [s["signal_id"] for s in result["signals"]],
        })
    tp, tn, fp, fn = (metrics[key] for key in ("TP", "TN", "FP", "FN"))
    return {
        "schema": "vtb.synthetic_benchmark.v1",
        "dataset": "SYNTHETIC_TEST_CONTROLS_ONLY",
        "cases": cases,
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "precision_on_fixture": tp / (tp + fp) if tp + fp else None,
        "recall_on_fixture": tp / (tp + fn) if tp + fn else None,
        "specificity_on_fixture": tn / (tn + fp) if tn + fp else None,
        "limitations": [
            "Synthetic controls check code regressions and applicability gates only.",
            "These metrics do NOT measure performance on real contracts or allegations.",
            "Real-world benchmarking requires independently adjudicated cases, negative controls, "
            "complete source coverage and blinded reviewers.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run synthetic VTB audit-screening benchmark")
    p.add_argument("--output", help="Optional local JSON result")
    args = p.parse_args(argv)
    result = run_benchmark()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        from pathlib import Path

        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
    return 0 if result["confusion"]["fp"] == 0 and result["confusion"]["fn"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
