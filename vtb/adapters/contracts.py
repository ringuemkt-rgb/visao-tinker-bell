from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..models import SourceHealth


@dataclass(slots=True)
class EntityMatchCandidate:
    candidate_id: str
    score: float | None
    schema: str
    properties: dict[str, list[str]] = field(default_factory=dict)
    dataset: str | None = None
    source_url: str | None = None


@dataclass(slots=True)
class MatchResult:
    query_id: str
    health: SourceHealth
    candidates: list[EntityMatchCandidate] = field(default_factory=list)
    identifiers_used: dict[str, list[str]] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def requires_independent_validation(self) -> bool:
        return True


class EntityMatcher(Protocol):
    def match_person(
        self,
        query_id: str,
        name: str,
        *,
        country: str | None = None,
        birth_date: str | None = None,
        id_number: str | None = None,
    ) -> MatchResult: ...


class CNPJRegistry(Protocol):
    def get_company(self, cnpj: str) -> dict[str, Any] | None: ...


class PublicSpendingSource(Protocol):
    def fetch_records(self, *, year: int | None = None, entity_id: str | None = None) -> list[dict[str, Any]]: ...
