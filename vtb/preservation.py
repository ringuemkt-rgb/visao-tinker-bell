from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
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
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_bytes(data)
    os.replace(temporary, path)
    return PreservationManifest(artifact_id, source_url, datetime.now(UTC).isoformat(), str(path), sha256_bytes(data), len(data), method, path.name)


def copy_preserving_original(source: str | Path, destination: str | Path, artifact_id: str, source_url: str = "local-file") -> PreservationManifest:
    src, dst = Path(source), Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    temporary = dst.with_name(f".{dst.name}.partial")
    shutil.copy2(src, temporary)
    os.replace(temporary, dst)
    return PreservationManifest(artifact_id, source_url, datetime.now(UTC).isoformat(), str(dst), sha256_file(dst), dst.stat().st_size, "forensic-copy", src.name)


def verify_manifest(manifest: PreservationManifest | dict[str, object]) -> tuple[bool, list[str]]:
    data = asdict(manifest) if isinstance(manifest, PreservationManifest) else manifest
    path = Path(str(data["file_path"]))
    reasons: list[str] = []
    if not path.exists():
        return False, ["ARTIFACT_MISSING"]
    actual_hash = sha256_file(path)
    actual_size = path.stat().st_size
    if actual_hash != data["sha256"]:
        reasons.append("SHA256_MISMATCH")
    if actual_size != int(data["byte_length"]):
        reasons.append("BYTE_LENGTH_MISMATCH")
    return not reasons, reasons


def write_manifest(manifest: PreservationManifest, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(manifest), ensure_ascii=False, indent=2), encoding="utf-8")
