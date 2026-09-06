#!/usr/bin/env python3
"""Exemplo: analytics (Benford/HHI) + red flags de regras."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.analytics import analyze_values
from lib.red_flags_engine import load_engine


def main():
    values = [
        92188.80, 96000.00, 547490.00, 160000.00, 15600.00,
        118999.92, 50000.00, 60000.00, 3568989.80, 317560.86,
        99500.00, 89900.00, 97000.00, 149500.00, 93000.00,
        88000.00, 91000.00, 45000.00, 120000.00, 75000.00,
        82000.00, 99000.00, 110000.00, 67000.00, 54000.00,
        101000.00, 95000.00, 87000.00, 76000.00, 64000.00,
    ]
    print("=== Analytics (sinais estatísticos) ===")
    stats = analyze_values(values)
    print("Benford chi2:", stats["benford"].get("chi2"), stats["benford"].get("risk"))
    print("Anomalias:", stats["anomalies"].get("count"))
    print("Structuring:", stats["structuring"].get("risk"))
    print("Risk level:", stats["risk_level"])
    print(stats["nota"])

    print("\n=== Red Flags Engine (regras) ===")
    engine = load_engine()
    findings = engine.evaluate(
        {
            "valorGlobal": 15_000_000,
            "capital_social": 5_000,
            "data_inicio_atividade": "2025-02-01",
            "dataAssinatura": "2025-08-15",
        }
    )
    for f in findings:
        print(f"  [{f.severidade}] {f.nome}")


if __name__ == "__main__":
    main()
