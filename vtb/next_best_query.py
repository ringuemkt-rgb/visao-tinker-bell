from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class QueryCandidate:
    query: str
    purpose: str
    expected_information_gain: float
    materiality: float = 1.0
    primary_source_bonus: float = 0.0
    contradiction_bonus: float = 0.0
    cost: float = 1.0

    @property
    def score(self) -> float:
        denominator = self.cost if self.cost > 0 else 0.1
        return (
            self.expected_information_gain * self.materiality
            + self.primary_source_bonus
            + self.contradiction_bonus
        ) / denominator


def rank_queries(candidates: list[QueryCandidate]) -> list[QueryCandidate]:
    return sorted(candidates, key=lambda q: (-q.score, q.query))


def next_best_query(candidates: list[QueryCandidate]) -> QueryCandidate | None:
    ranked = rank_queries(candidates)
    return ranked[0] if ranked else None
