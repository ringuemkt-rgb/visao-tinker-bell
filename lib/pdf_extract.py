"""Extração de PDF com cadeia de evidência.

Ordem: Docling → PyMuPDF → AIPDF (opcional, nunca fato sem revisão).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Backend = Literal["docling", "pymupdf", "aipdf", "none"]


@dataclass
class PdfExtractResult:
    path: str
    sha256: str
    backend: Backend
    markdown: str
    pages: int | None = None
    notes: str = ""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _try_docling(path: Path) -> PdfExtractResult | None:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        return None
    converter = DocumentConverter()
    result = converter.convert(str(path))
    md = result.document.export_to_markdown()
    pages = None
    try:
        pages = result.document.num_pages()
    except Exception:
        pass
    return PdfExtractResult(str(path), _sha256(path), "docling", md, pages, "Docling local")


def _try_pymupdf(path: Path) -> PdfExtractResult | None:
    try:
        import fitz
    except ImportError:
        return None
    doc = fitz.open(path)
    parts = []
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        parts.append(f"\n\n## Página {i + 1}\n\n{text}")
    md = "".join(parts).strip()
    n = doc.page_count
    doc.close()
    return PdfExtractResult(str(path), _sha256(path), "pymupdf", md, n, "PyMuPDF texto nativo")


def extract_pdf(path: str | Path, prefer: Backend | None = None) -> PdfExtractResult:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    if prefer == "pymupdf":
        order = ["pymupdf", "docling", "aipdf"]
    elif prefer == "aipdf":
        order = ["aipdf", "docling", "pymupdf"]
    else:
        order = ["docling", "pymupdf", "aipdf"]
    for backend in order:
        if backend == "docling":
            out = _try_docling(p)
            if out and out.markdown.strip():
                return out
        elif backend == "pymupdf":
            out = _try_pymupdf(p)
            if out and out.markdown.strip():
                return out
    return PdfExtractResult(str(p), _sha256(p), "none", "", None, "Nenhum extrator disponível")
