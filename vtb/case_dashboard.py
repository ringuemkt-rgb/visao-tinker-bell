"""Offline, read-only, HTML/SVG evidence dashboard; no hosted publication."""
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


def _h(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    if parts.scheme not in {"https", "http"} or not parts.netloc or parts.username or parts.password:
        return None
    return value


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{_h(name)}</th>" for name in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def _graph(links: list[dict[str, Any]], valid_evidence: set[str]) -> str:
    """Render an unaccusatory source-labelled network, no remote JS or data loading."""
    clean = []
    for item in links:
        if not isinstance(item, dict):
            continue
        src, dst = str(item.get("from", "")), str(item.get("to", ""))
        if not src or not dst or src == dst:
            continue
        evidence = [str(e) for e in item.get("evidence_ids", [])]
        documented = (
            item.get("status") == "DOCUMENTED"
            and bool(evidence) and set(evidence).issubset(valid_evidence)
        )
        clean.append((src, dst, str(item.get("relation", "")),
                      documented, evidence))
    nodes = sorted({a for a, _, _, _, _ in clean} | {b for _, b, _, _, _ in clean})
    if not nodes:
        return "<p>Sem relações documentais fornecidas para o grafo.</p>"
    if len(nodes) > 40:
        return "<p>Grafo acima do limite local de 40 nós: use recorte por caso.</p>"
    radius = 180
    positions = {
        name: (250 + radius * math.cos(2 * math.pi * i / len(nodes)),
               230 + radius * math.sin(2 * math.pi * i / len(nodes)))
        for i, name in enumerate(nodes)
    }
    edges = []
    for src, dst, relation, verified, evidence in clean:
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        color = "#417a69" if verified else "#a47d46"
        dash = "" if verified else ' stroke-dasharray="5 5"'
        tooltip = _h(f"{relation}; {'documented' if verified else 'candidate/unverified'}; "
                     f"evidence: {', '.join(evidence)}")
        edges.append(
            f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{color}" stroke-width="2"{dash}><title>{tooltip}</title></line>'
        )
    circles = []
    for name, (x, y) in positions.items():
        circles.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#315b7d">'
            f'<title>{_h(name)}</title></circle>'
            f'<text x="{x:.0f}" y="{y + 21:.0f}" text-anchor="middle" '
            f'font-size="11" fill="#263950">{_h(name[:34])}</text>'
        )
    return (
        '<svg viewBox="0 0 500 470" role="img" '
        'aria-label="Grafo de relações: linhas sólidas com evidência informada; pontilhadas candidatas">'
        + "".join(edges + circles) + "</svg>"
        '<p class="muted">Linha sólida: evidência registrada; tracejada: hipótese ou fonte ausente. '
        'O grafo não confirma identidade, dolo ou pagamento.</p>'
    )


def render_dashboard(
    snapshot: dict[str, Any],
    *,
    links: list[dict[str, Any]] | None = None,
    validation: dict[str, Any] | None = None,
) -> str:
    """Render safely escaped local case snapshot. Input need not contain true facts."""
    mission = snapshot.get("mission") or {}
    sources = snapshot.get("sources") or []
    evidence = snapshot.get("evidence") or []
    claims = snapshot.get("claims") or []
    hypotheses = snapshot.get("hypotheses") or []
    all_evidence = {row["evidence_id"] for row in evidence if row.get("evidence_id")}
    src_rows = []
    for row in sources:
        source = row.get("payload") or {}
        url = _url(source.get("url"))
        uri = f'<a href="{_h(url)}" rel="noopener noreferrer" target="_blank">Origem</a>' if url else "Sem URL segura"
        src_rows.append([_h(row.get("source_id")), _h(source.get("issuer")),
                         _h(source.get("health")), _h(source.get("quality")), uri])
    evidence_rows = [
        [_h(row.get("evidence_id")), _h((row.get("payload") or {}).get("source_id")),
         _h((row.get("payload") or {}).get("locator")),
         _h((row.get("payload") or {}).get("excerpt"))]
        for row in evidence
    ]
    claim_rows = []
    for row in claims:
        payload = row.get("payload") or {}
        ids = [str(v) for v in payload.get("evidence_ids", [])]
        good = all(x in all_evidence for x in ids)
        claim_rows.append([
            _h(payload.get("claim_id")), _h(payload.get("status")),
            _h(payload.get("statement")),
            _h(", ".join(ids)),
            "IDs registrados" if ids and good else "Dados insuficientes",
        ])
    hypotheses_rows = [
        [_h((r.get("payload") or {}).get("hypothesis_id")),
         _h((r.get("payload") or {}).get("status")),
         _h((r.get("payload") or {}).get("statement"))]
        for r in hypotheses
    ]
    graph = _graph(links or [], all_evidence)
    if validation is None:
        readiness = "NÃO VALIDADO — não publicar como perícia conclusiva"
    else:
        readiness = "VALIDADO PARA REVISÃO" if validation.get("valid") else "QUARENTENA / FALHAS"
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'">
<title>Tinker Bell — painel de evidências</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#172b40;font:15px/1.5 system-ui,sans-serif}}
header{{background:#112337;color:#fff;padding:24px}}.wrap{{max-width:1200px;margin:auto;padding:15px}}
nav a{{color:#bfe5ff;margin-right:16px}}main section{{background:white;margin:15px 0;padding:20px;border:1px solid #dce4ec;border-radius:12px}}
h1,h2,h3{{line-height:1.2}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
.stat{{background:#e8eef6;padding:12px;border-radius:8px}}.stat strong{{font-size:24px;display:block}}
.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #e4eaf0}}
th{{background:#e9f0f6}}svg{{max-width:100%;height:auto;display:block;margin:auto}}
.muted{{color:#526273}}.warning{{font-weight:700;color:#70471b}}
@media(max-width:660px){{.stats{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body>
<header><div class="wrap"><h1>Visão Tinker Bell | Dossiê de evidências</h1>
<p>Investigação: {_h(mission.get("title", "Não informado"))} • {_h(mission.get("case_id"))}</p>
<nav><a href="#fontes">Fontes</a><a href="#provas">Evidências</a><a href="#alegacoes">Alegações</a>
<a href="#relacoes">Relações</a><a href="#hipoteses">Hipóteses</a></nav></div></header>
<main class="wrap"><section><h2>Estado de revisão</h2>
<p class="warning">{_h(readiness)}</p><p>{_h(mission.get("question"))}</p>
<div class="stats"><div class="stat"><strong>{len(sources)}</strong>fontes</div>
<div class="stat"><strong>{len(evidence)}</strong>registros de evidência</div>
<div class="stat"><strong>{len(claims)}</strong>alegações</div>
<div class="stat"><strong>{len(hypotheses)}</strong>hipóteses</div></div>
<p class="muted">Contagens não medem veracidade, independência das provas ou corrupção.</p></section>
<section id="fontes"><h2>Fontes</h2>{_table(["ID","Órgão","Saúde","Qualidade","Link"],src_rows)}</section>
<section id="provas"><h2>Provas e documentos</h2>
{_table(["Evidência","Fonte","Localização","Trecho declarado"],evidence_rows)}</section>
<section id="alegacoes"><h2>Alegações e status documental</h2>
{_table(["ID","Status","Afirmação","Evidências","Verificação de referência"],claim_rows)}</section>
<section id="relacoes"><h2>Grafo de relações fornecidas</h2>{graph}</section>
<section id="hipoteses"><h2>Hipóteses concorrentes</h2>
{_table(["ID","Estado","Hipótese"],hypotheses_rows)}</section>
<section><h2>Limites e origem</h2><p>Visualização HTML local de dados fornecidos à VTB.
Identificadores de evidência não autenticam um documento. Cada valor e relação material
precisa ser conferido no original, com contraditório e revisão jurídica quando pertinente.</p></section>
</main></body></html>"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate safe, offline investigative HTML dashboard")
    p.add_argument("case_export", help="JSON from CaseStore export")
    p.add_argument("--links", help="Optional JSON list of typed public-document relations")
    p.add_argument("--validation", help="Optional report-validator result JSON")
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    dest = Path(args.output)
    if dest.resolve() == Path(args.case_export).resolve():
        p.error("Output must differ from input")
    snapshot = json.loads(Path(args.case_export).read_text(encoding="utf-8"))
    links = json.loads(Path(args.links).read_text(encoding="utf-8")) if args.links else None
    validation = json.loads(Path(args.validation).read_text(encoding="utf-8")) if args.validation else None
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as handle:
        handle.write(render_dashboard(snapshot, links=links, validation=validation))
    print(json.dumps({"output": str(dest), "published": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
