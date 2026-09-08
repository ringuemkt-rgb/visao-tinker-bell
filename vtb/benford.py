from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class BenfordAssessment:
    applicable: bool
    n: int
    chi_square: float | None
    reasons: tuple[str, ...]
    observed: dict[int, float]
    expected: dict[int, float]


def first_digit(value: float) -> int | None:
    value = abs(value)
    if value == 0 or not math.isfinite(value):
        return None
    while value >= 10:
        value /= 10
    while value < 1:
        value *= 10
    digit = int(value)
    return digit if 1 <= digit <= 9 else None


def assess_benford(
    values: list[float],
    *,
    minimum_n: int = 100,
    require_order_span: bool = True,
) -> BenfordAssessment:
    cleaned = [abs(float(value)) for value in values if value and math.isfinite(float(value))]
    reasons: list[str] = []
    if len(cleaned) < minimum_n:
        reasons.append(f"n<{minimum_n}")
    if cleaned and require_order_span:
        positive = [value for value in cleaned if value > 0]
        if positive and max(positive) / min(positive) < 100:
            reasons.append("insufficient_order_of_magnitude_span")
    counts = Counter(first_digit(value) for value in cleaned)
    counts.pop(None, None)
    n = sum(counts.values())
    expected = {digit: math.log10(1 + 1 / digit) for digit in range(1, 10)}
    observed = {digit: (counts[digit] / n if n else 0.0) for digit in range(1, 10)}
    chi_square = None
    if n:
        chi_square = sum(
            ((counts[digit] - n * expected[digit]) ** 2) / (n * expected[digit])
            for digit in range(1, 10)
        )
    return BenfordAssessment(not reasons and n >= minimum_n, n, chi_square, tuple(reasons), observed, expected)


def benford_signal(
    values: list[float],
    evidence_ids: list[str],
    *,
    review_chi_square: float = 15.507,
    minimum_n: int = 100,
) -> RiskSignal | None:
    assessment = assess_benford(values, minimum_n=minimum_n)
    if not assessment.applicable or assessment.chi_square is None or assessment.chi_square < review_chi_square:
        return None
    return RiskSignal(
        signal_id="STAT-BENFORD-FIRST-DIGIT",
        category=SignalCategory.STATISTICAL,
        title="Sinal Benford para revisão estatística",
        description=(
            f"χ²={assessment.chi_square:.3f}, n={assessment.n}. "
            "Benford é triagem e não demonstra manipulação, fraude ou autoria."
        ),
        severity=SignalSeverity.LOW,
        evidence_ids=sorted(set(evidence_ids)),
        method="Benford first-digit chi-square with applicability gate",
        threshold={"review_chi_square": review_chi_square, "minimum_n": minimum_n},
        false_positive_risk="high",
        alternative_explanations=["preços tabelados", "limites administrativos", "dataset truncado", "mistura de populações"],
    )
