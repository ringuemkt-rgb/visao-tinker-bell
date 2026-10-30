"""Read-only capability discovery; installed does not imply tested or operational."""
from __future__ import annotations

import importlib.util
from importlib import metadata
from typing import Any

OPTIONAL_MODULES: dict[str, tuple[str, str]] = {
    "docling": ("docling", "docling"),
    "pymupdf": ("fitz", "PyMuPDF"),
    "ocrmypdf": ("ocrmypdf", "ocrmypdf"),
    "splink": ("splink", "splink"),
    "openrefine_client": ("openrefine", "openrefine-client"),
    "gliner": ("gliner", "gliner"),
    "sentence_transformers": ("sentence_transformers", "sentence-transformers"),
    "prefect": ("prefect", "prefect"),
    "openlineage": ("openlineage", "openlineage-python"),
    "followthemoney": ("followthemoney", "followthemoney"),
    "duckdb": ("duckdb", "duckdb"),
    "networkx": ("networkx", "networkx"),
}


def optional_toolcheck(names: list[str] | None = None) -> dict[str, Any]:
    """Check Python distributions without importing or running tool code."""
    requested = list(OPTIONAL_MODULES) if names is None else names
    if not isinstance(requested, list) or len(requested) > len(OPTIONAL_MODULES):
        raise ValueError("invalid tool list")
    if any(name not in OPTIONAL_MODULES for name in requested):
        raise ValueError("unknown optional tool")
    records = []
    for name in requested:
        module, distribution = OPTIONAL_MODULES[name]
        try:
            installed = importlib.util.find_spec(module) is not None
        except (ValueError, ModuleNotFoundError, ImportError):
            installed = False
        version = None
        if installed:
            try:
                version = metadata.version(distribution)
            except metadata.PackageNotFoundError:
                pass
        records.append({
            "tool": name,
            "installed": installed,
            "version": version,
            "status": "S3_INSTALLED" if installed else "S0_NOT_EVALUATED",
            "operational": False,
            "reason": "Execution, model weights and external service connectivity not tested",
        })
    return {"tools": records, "requires_runtime_validation": True}
