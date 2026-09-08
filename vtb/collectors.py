from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .models import SourceHealth


@dataclass(slots=True)
class CollectionBatch:
    collector_id: str
    source_id: str
    health: SourceHealth
    records: list[dict[str, Any]] = field(default_factory=list)
    next_cursor: str | None = None
    retrieved_at: str | None = None
    query_parameters: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class IncrementalCollector(Protocol):
    collector_id: str
    source_id: str

    def collect(self, *, cursor: str | None = None) -> CollectionBatch: ...
