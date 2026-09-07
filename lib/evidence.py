"""Cadeia de custódia — Visão Tinker Bell v7."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class EvidenceItem:
    source_id: str
    title: str
    url: str | None
    accessed_at: str
    tier: int
    kind: str
    sha256: str | None = None
    local_path: str | None = None
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvidenceStore:
    def __init__(self) -> None:
        self.items: list[EvidenceItem] = []

    def add(self, item: EvidenceItem) -> EvidenceItem:
        self.items.append(item)
        return item

    def add_api(self, source_id: str, title: str, url: str, payload: Any, tier: int = 1) -> EvidenceItem:
        raw = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        return self.add(
            EvidenceItem(
                source_id=source_id,
                title=title,
                url=url,
                accessed_at=utc_now(),
                tier=tier,
                kind="api",
                sha256=sha256_bytes(raw),
            )
        )

    def add_file(self, source_id: str, title: str, path: Path, url: str | None = None, tier: int = 1) -> EvidenceItem:
        digest = sha256_file(path)
        return self.add(
            EvidenceItem(
                source_id=source_id,
                title=title,
                url=url,
                accessed_at=utc_now(),
                tier=tier,
                kind=path.suffix.lstrip(".") or "file",
                sha256=digest,
                local_path=str(path),
            )
        )

    def dump(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps([i.to_dict() for i in self.items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def markdown(self) -> str:
        lines = ["| ID | Título | Tier | SHA-256 | URL |", "|----|--------|------|---------|-----|"]
        for i in self.items:
            digest = (i.sha256 or "")[:16]
            url = i.url or ""
            lines.append(f"| {i.source_id} | {i.title} | {i.tier} | `{digest}` | {url} |")
        return "\n".join(lines)
