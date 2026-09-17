from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .runtime import CaseStore


def _safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    if not name:
        raise ValueError("identificador de caso inválido")
    return name[:120]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_case_bundle(store: CaseStore, case_id: str, destination: str | Path) -> Path:
    """Write a Git-friendly case snapshot with stable JSON and a hash manifest."""
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    bundle = (root / _safe_name(case_id)).resolve()
    if root not in bundle.parents:
        raise ValueError("destino de pacote inválido")
    bundle.mkdir(parents=True, exist_ok=True)
    export = store.export_case(case_id)
    _write_json(bundle / "case.json", export)
    files = []
    for path in sorted(bundle.rglob("*")):
        if path.is_file() and path.name != "bundle-manifest.json":
            files.append({"path": path.relative_to(bundle).as_posix(), "sha256": _sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "format": "vtb-case-bundle-v1",
        "case_id": case_id,
        "files": files,
        "integrity": "sha256",
        "git_versioning_note": "Git é camada editorial; preservação original depende de manifestos e storage controlado.",
    }
    _write_json(bundle / "bundle-manifest.json", manifest)
    return bundle


def verify_case_bundle(bundle_path: str | Path) -> tuple[bool, list[str]]:
    bundle = Path(bundle_path).resolve()
    manifest_path = bundle / "bundle-manifest.json"
    if not manifest_path.exists():
        return False, ["BUNDLE_MANIFEST_MISSING"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reasons: list[str] = []
    for item in manifest.get("files", []):
        path = bundle / str(item["path"])
        if not path.exists():
            reasons.append(f"MISSING:{item['path']}")
            continue
        if _sha256(path) != item["sha256"]:
            reasons.append(f"SHA256_MISMATCH:{item['path']}")
        if path.stat().st_size != item["bytes"]:
            reasons.append(f"BYTE_LENGTH_MISMATCH:{item['path']}")
    return not reasons, reasons
