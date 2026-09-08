from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..models import SourceHealth


@dataclass(slots=True)
class AdapterResult:
    ok: bool
    health: SourceHealth
    data: Any = None
    status_code: int | None = None
    url: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PublicSourceAdapter(ABC):
    adapter_id: str

    @abstractmethod
    def fetch(self, *args: Any, **kwargs: Any) -> AdapterResult:
        raise NotImplementedError
