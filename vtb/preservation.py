from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(slots=True)
class PreservationManifest:
    artifact_id: str
    source_url: str
    retrieved_at: str
    file_path: str
    sha256: str
    byte_length: int
    method: str
    original_filename: str | None = None
    notes: str = ""


def preserve_bytes(data: bytes, destination: str | Path, artifact_id: str, source_url: str, method: str = "direct-download") -> PreservationManifest:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return PreservationManifest(
        artifact_id=artifact_id,
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        file_path=str(path),
        sha256=sha256_bytes(data),
        byte_length=len(data),
        method=method,
        original_filename=path.name,
    )


def copy_preserving_original(source: str | Path, destination: str | Path, artifact_id: str, source_url: str = "local-file") -> PreservationManifest:
    src = Path(source)
    dst = Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return PreservationManifest(
        artifact_id=artifact_id,
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        file_path=str(dst),
        sha256=sha256_file(dst),
        byte_length=dst.stat().st_size,
        method="forensic-copy",
        original_filename=src.name,
    )


def write_manifest(manifest: PreservationManifest, path: str | Path) -> None:
    Path(path).write_text(json.dumps(asdict(manifest), ensure_ascii=False, indent=2), encoding="utf-8")
