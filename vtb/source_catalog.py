from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True, frozen=True)
class SourceSpec:
    source_id: str
    name: str
    authority: str
    level: str
    domains: tuple[str, ...]
    primary: bool
    geography: str = "BR"
    notes: str = ""


class SourceCatalog:
    def __init__(self, sources: list[SourceSpec]) -> None:
        self.sources = {source.source_id: source for source in sources}

    @classmethod
    def from_yaml(cls, path: str | Path) -> SourceCatalog:
        raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        sources = [
            SourceSpec(
                source_id=item["id"],
                name=item["name"],
                authority=item["authority"],
                level=item["level"],
                domains=tuple(item.get("domains", [])),
                primary=bool(item.get("primary", False)),
                geography=item.get("geography", "BR"),
                notes=item.get("notes", ""),
            )
            for item in raw.get("sources", [])
        ]
        return cls(sources)

    def for_domains(self, *domains: str, primary_first: bool = True) -> list[SourceSpec]:
        wanted = set(domains)
        rows = [source for source in self.sources.values() if wanted.intersection(source.domains)]
        if primary_first:
            rows.sort(key=lambda source: (not source.primary, source.authority, source.level, source.name))
        return rows

    def get(self, source_id: str) -> SourceSpec:
        return self.sources[source_id]
