from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class Checkpoint:
    collector_id: str
    cursor: str | None = None
    last_seen_timestamp: str | None = None
    last_content_hash: str | None = None
    records_seen: int = 0


class CheckpointStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, collector_id: str) -> Checkpoint:
        if not self.path.exists():
            return Checkpoint(collector_id)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        raw = data.get(collector_id)
        return Checkpoint(collector_id, **raw) if raw else Checkpoint(collector_id)

    def save(self, checkpoint: Checkpoint) -> None:
        data: dict[str, object] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
        payload = asdict(checkpoint)
        payload.pop("collector_id")
        data[checkpoint.collector_id] = payload
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
