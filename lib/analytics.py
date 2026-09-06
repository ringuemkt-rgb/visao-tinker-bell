#!/usr/bin/env python3
"""
Visão Tinker Bell — Analytics (sinais estatísticos)
Benford, Z-score, HHI, structuring flags.
Produz sinais objetivos. Nunca gera acusação.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def _first_digit(v: float) -> Optional[int]:
    s = str(abs(float(v))).replace(".", "").lstrip("0")
    if not s:
        return None
    d = int(s[0])
    return d if 1 <= d <= 9 else None


def analyze_benford(values: List[float]) -> Dict[str, Any]:
    """Lei de Benford (1º dígito). Retorna chi² e classificação de risco como sinal."""
    digits = [d for d in (_first_digit(v) for v in values) if d is not None]
    n = len(digits)
    if n < 30:
        return {"status": "AMOSTRA_INSUFICIENTE", "n": n, "flag": False}

    observed = Counter(digits)
    expected = {d: math.log10(1 + 1 / d) * n for d in range(1, 10)}
    chi2 = 0.0
    for d in range(1, 10):
        obs = observed.get(d, 0)
        exp = expected[d]
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp

    # Limiares aproximados (df=8). Sinal, não prova.
    risk = "ALTO" if chi2 > 20 else "MEDIO" if chi2 > 15 else "BAIXO"
    return {
        "status": "OK",
        "chi2": round(chi2, 2),
        "n": n,
        "risk": risk,
        "flag": chi2 > 15,
        "observed": {str(k): observed.get(k, 0) for k in range(1, 10)},
    }


def detect_anomalies_zscore(values: List[float], threshold: float = 2.5) -> Dict[str, Any]:
    if len(values) < 5:
        return {"status": "AMOSTRA_INSUFICIENTE", "flag": False}
    if HAS_NUMPY:
        arr = np.array(values, dtype=float)
        mean, std = float(np.mean(arr)), float(np.std(arr))
    else:
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
    if std == 0:
        return {"status": "DESVIO_ZERO", "flag": False}

    anomalies = []
    for i, v in enumerate(values):
        z = (float(v) - mean) / std
        if abs(z) > threshold:
            anomalies.append(
                {
                    "index": i,
                    "value": float(v),
                    "z_score": round(z, 3),
                    "type": "ALTO" if z > 0 else "BAIXO",
                }
            )
    return {
        "status": "OK",
        "mean": round(mean, 2),
        "std": round(std, 2),
        "anomalies": anomalies,
        "count": len(anomalies),
        "flag": len(anomalies) > 0,
    }


def detect_structuring(values: List[float], limits: Optional[List[float]] = None) -> Dict[str, Any]:
    """Sinal de valores concentrados logo abaixo de limites comuns (não prova de structuring)."""
    limits = limits or [50_000, 100_000, 150_000]
    arr = [float(v) for v in values if v is not None]
    hits = []
    for L in limits:
        band = [v for v in arr if L * 0.85 <= v < L]
        if band:
            hits.append({"limit": L, "count": len(band), "values_sample": band[:5]})
    total_hits = sum(h["count"] for h in hits)
    risk = "ALTO" if total_hits >= 5 else "MEDIO" if total_hits >= 2 else "BAIXO"
    return {
        "hits": hits,
        "total_near_limits": total_hits,
        "risk": risk,
        "flag": total_hits >= 3,
    }


def calculate_hhi(contracts: List[Dict[str, Any]], key: str = "fornecedor", value_key: str = "valor") -> Dict[str, Any]:
    """Índice Herfindahl-Hirschman (concentração). Sinal de mercado concentrado."""
    by_supplier: Dict[str, float] = {}
    for c in contracts:
        supplier = str(c.get(key) or "desconhecido")
        by_supplier[supplier] = by_supplier.get(supplier, 0.0) + float(c.get(value_key) or 0)
    total = sum(by_supplier.values())
    if total <= 0:
        return {"hhi": 0, "classification": "N/A", "flag": False}

    shares = [(v / total) * 100 for v in by_supplier.values()]
    hhi = sum(p ** 2 for p in shares)
    classification = (
        "ALTAMENTE_CONCENTRADO" if hhi > 2500 else "MODERADO" if hhi > 1500 else "COMPETITIVO"
    )
    top_pct = max(shares) if shares else 0
    return {
        "hhi": round(hhi, 2),
        "classification": classification,
        "top_supplier_pct": round(top_pct, 2),
        "n_suppliers": len(by_supplier),
        "flag": hhi > 2500,
    }


def analyze_values(
    values: List[float], contracts: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Pipeline de sinais sobre uma lista de valores (e opcionalmente contratos)."""
    results: Dict[str, Any] = {
        "benford": analyze_benford(values),
        "anomalies": detect_anomalies_zscore(values),
        "structuring": detect_structuring(values),
    }
    if contracts:
        results["hhi"] = calculate_hhi(contracts)

    flags = sum(1 for r in results.values() if r.get("flag"))
    results["total_flags"] = flags
    results["risk_level"] = (
        "ALTO" if flags >= 3 else "MEDIO" if flags >= 1 else "BAIXO"
    )
    results["nota"] = (
        "Sinais estatísticos objetivos. Não constituem prova de irregularidade. "
        "Usar com ACH e fontes primárias."
    )
    return results


if __name__ == "__main__":
    sample = [
        92188.80, 96000.00, 547490.00, 160000.00, 15600.00,
        118999.92, 50000.00, 60000.00, 3568989.80, 317560.86,
        99500.00, 89900.00, 97000.00, 149500.00, 93000.00,
        88000.00, 91000.00, 45000.00, 120000.00, 75000.00,
        82000.00, 99000.00, 110000.00, 67000.00, 54000.00,
        101000.00, 95000.00, 87000.00, 76000.00, 64000.00,
    ]
    out = analyze_values(sample)
    print("Benford:", out["benford"])
    print("Anomalias:", out["anomalies"]["count"])
    print("Structuring risk:", out["structuring"]["risk"])
    print("Risk level:", out["risk_level"])
