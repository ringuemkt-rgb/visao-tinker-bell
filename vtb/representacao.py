"""Peca de apuracao. Relato curto para o Fala.BR e PDF de anexo.

O texto sai do registro, nao de um modelo. Claim sem URL e sem SHA-256
fica de fora. A peca pede apuracao. Nao afirma ilicito.
"""

from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path
from typing import Any

RELATO_MAX = 7000
BANNED = (
    "vale ressaltar",
    "em suma",
    "cabe salientar",
    "ecossistema",
    "robustez",
    "corrupto",
    "corrupcao",
    "corrupção",
    "corruptos",
)


def select_facts(claims: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    kept: list[dict[str, Any]] = []
    omitted: list[str] = []
    for claim in claims:
        fato = (claim.get("fato") or "").strip()
        url = (claim.get("url") or "").strip()
        digest = (claim.get("sha256") or "").strip()
        if not fato or not url or len(digest) < 16:
            omitted.append(claim.get("id") or fato[:40] or "sem-id")
            continue
        if _banned(fato):
            omitted.append(claim.get("id") or fato[:40])
            continue
        kept.append(claim)
    return kept, omitted


def build_relato(meta: dict[str, Any], claims: list[dict[str, Any]]) -> str:
    kept, omitted = select_facts(claims)
    lines = [
        f"Destino: {meta.get('destino', 'ouvidoria competente')}.",
        f"Orgao: {meta.get('orgao', 'nao indicado')}. Agente publico citado: {meta.get('agente', 'nao indicado')}.",
        f"Periodo: {meta.get('periodo', 'nao indicado')}. Acesso aos documentos: {meta.get('acesso', 'nao indicado')}.",
        "",
        "Requeiro a apuracao dos fatos publicos abaixo. Este relato nao afirma ilicito, nao pede condenacao e nao substitui o documento oficial.",
        "",
    ]
    for index, claim in enumerate(kept, start=1):
        limite = claim.get("limite") or "O registro nao informa pagamento nem decisao."
        lines.append(
            f"{index}. {claim['fato']} Documento: {claim.get('documento', 'nao indicado')}. "
            f"URL: {claim['url']}. SHA-256: {claim['sha256']}. Limite: {limite}"
        )
    if omitted:
        lines.append("")
        lines.append(f"Ficaram de fora do relato {len(omitted)} itens sem URL, sem hash ou com termo vedado.")
    text = "\n".join(lines).strip()
    if len(text) > RELATO_MAX:
        text = text[: RELATO_MAX - 40].rsplit(" ", 1)[0] + " [relato cortado no limite do canal]"
    return text


def build_anexo(meta: dict[str, Any], claims: list[dict[str, Any]]) -> str:
    kept, omitted = select_facts(claims)
    lines = [
        "REPRESENTACAO PARA APURACAO DE FATOS PUBLICOS",
        f"Destino: {meta.get('destino', 'ouvidoria competente')}",
        f"Data: {meta.get('data', '')}",
        "",
        "1. Pedido",
        "Apuracao dos fatos listados. Nada neste anexo e sentenca.",
        "",
        "2. Fatos com fonte",
    ]
    for index, claim in enumerate(kept, start=1):
        lines.append(
            f"{index}. {claim['fato']} | {claim.get('documento', '')} | {claim['url']} | {claim['sha256']} | {claim.get('limite', '')}"
        )
    lines.extend(["", "3. Fora do relato", ", ".join(omitted) or "nenhum", "", "4. Metodo", "Tabela montada a partir dos documentos citados. Sem inferencia de autoria."])
    return "\n".join(lines)


def write_packet(meta: dict[str, Any], claims: list[dict[str, Any]], output: Path) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    relato = build_relato(meta, claims)
    anexo = build_anexo(meta, claims)
    relato_path = output / "relato.txt"
    anexo_path = output / "anexo.txt"
    pdf_path = output / "representacao.pdf"
    relato_path.write_text(relato, encoding="utf-8")
    anexo_path.write_text(anexo, encoding="utf-8")
    digest = hashlib.sha256(relato.encode("utf-8")).hexdigest()
    write_pdf(pdf_path, anexo, digest)
    manifest = {
        "relato": str(relato_path),
        "anexo": str(anexo_path),
        "pdf": str(pdf_path),
        "relato_sha256": digest,
        "label": "ANOMALY_FOR_VERIFICATION",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_pdf(path: Path, text: str, relato_sha256: str) -> None:
    pages = _paginate(text, relato_sha256)
    objects: list[bytes] = []
    page_ids: list[int] = []
    font_id = 3
    next_id = 4
    content_ids = []
    for page in pages:
        content_ids.append(next_id)
        objects.append(_stream(page))
        next_id += 1
    for cid in content_ids:
        page_ids.append(next_id)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {cid} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode()
        )
        next_id += 1
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
    pages_obj = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode()
    font = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    ordered = [catalog, pages_obj, font, *objects]
    _write_pdf(path, ordered)


def _paginate(text: str, digest: str) -> list[str]:
    wrapped: list[str] = []
    for raw in text.splitlines():
        wrapped.extend(textwrap.wrap(raw, width=88) or [""])
    pages = []
    chunk: list[str] = []
    for line in wrapped:
        chunk.append(line)
        if len(chunk) == 46:
            pages.append("\n".join(chunk))
            chunk = []
    if chunk:
        pages.append("\n".join(chunk))
    if not pages:
        pages = ["Sem fato com fonte e hash."]
    rendered = []
    total = len(pages)
    for index, body in enumerate(pages, start=1):
        footer = f"Pedido de apuracao. Nao e condenacao. SHA-256 do relato {digest[:16]}  {index}/{total}"
        rendered.append(_page_stream(body, footer))
    return rendered


def _page_stream(body: str, footer: str) -> str:
    lines = ["BT", "/F1 10 Tf", "48 790 Td", "14 TL"]
    for line in body.splitlines():
        lines.append(f"({_pdf_escape(line)}) Tj T*")
    lines.append("ET")
    lines.append("BT /F1 8 Tf 48 36 Td")
    lines.append(f"({_pdf_escape(footer)}) Tj ET")
    return "\n".join(lines)


def _pdf_escape(text: str) -> str:
    encoded = text.encode("latin-1", errors="replace")
    out = []
    for byte in encoded:
        if byte in (0x28, 0x29, 0x5C):
            out.append(f"\\{chr(byte)}")
        elif byte < 32 or byte > 126:
            out.append(f"\\{byte:03o}")
        else:
            out.append(chr(byte))
    return "".join(out)


def _stream(content: str) -> bytes:
    raw = content.encode("latin-1", errors="replace")
    return b"<< /Length " + str(len(raw)).encode() + b" >>\nstream\n" + raw + b"\nendstream"


def _write_pdf(path: Path, objects: list[bytes]) -> None:
    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part) for part in chunks))
        chunks.append(f"{index} 0 obj\n".encode())
        chunks.append(obj)
        chunks.append(b"\nendobj\n")
    xref = sum(len(part) for part in chunks)
    chunks.append(f"xref\n0 {len(objects) + 1}\n".encode())
    chunks.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        chunks.append(f"{offset:010d} 00000 n \n".encode())
    chunks.append(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(b"".join(chunks))


def _banned(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in BANNED)
