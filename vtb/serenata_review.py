"""Read-only Jarbas-inspired local HTML review of user-supplied audit records.

This does not fetch documents, establish facts, publish accusations or expose
a server. Outputs stay local, and all user strings are HTML escaped.
"""
from __future__ import annotations

import argparse
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .serenata_screening import PublicExpense, screen_expenses


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_review(expenses: list[PublicExpense], screening: dict[str, Any]) -> str:
    """Build a navigable local report (not evidence verification or public site)."""
    if screening.get("schema") != "vtb.serenata_screening.v1":
        raise ValueError("unsupported screening format")
    if screening.get("records_examined") != len(expenses):
        raise ValueError("record count does not match the related screening")
    rows_by_day: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(expenses):
        rows_by_day[(row.actor_id, row.issue_date.isoformat())].append(index)

    sections: list[str] = []
    for signal in screening.get("signals", []):
        evidence = ", ".join(esc(v) for v in signal.get("evidence_ids", []))
        explanations = "".join(
            f"<li>{esc(alt)}</li>" for alt in signal.get("alternative_explanations", [])
        )
        threshold = esc(json.dumps(signal.get("threshold", {}), ensure_ascii=False, sort_keys=True))
        sections.append(
            '<article class="signal">'
            f'<h3>{esc(signal.get("title", ""))}</h3>'
            f'<p>{esc(signal.get("description", ""))}</p>'
            f'<p><strong>Regra:</strong> {esc(signal.get("method", ""))}</p>'
            f'<p><strong>Parâmetros:</strong> {threshold}</p>'
            f'<p><strong>Evidências informadas:</strong> {evidence}</p>'
            f'<details><summary>Explicações alternativas a verificar</summary><ul>{explanations}</ul></details>'
            "</article>"
        )

    expense_articles = []
    for index, row in enumerate(expenses):
        same = rows_by_day[(row.actor_id, row.issue_date.isoformat())]
        same_day = " ".join(
            f'<a href="#exp-{i}">Registro {i + 1}</a>'
            for i in same if i != index
        ) or "Nenhum outro registro da mesma pessoa e data no conjunto."
        evidence = ", ".join(esc(e) for e in row.evidence_ids)
        expense_articles.append(
            f'<article class="expense" id="exp-{index}">'
            f'<h3>Registro {index + 1} — {esc(row.expense_id)}</h3>'
            '<dl>'
            f'<dt>Data</dt><dd>{esc(row.issue_date.isoformat())}</dd>'
            f'<dt>Identificador de análise</dt><dd>{esc(row.actor_id)}</dd>'
            f'<dt>Valor informado</dt><dd>R$ {esc(row.amount_brl)}</dd>'
            f'<dt>Categoria</dt><dd>{esc(row.category or "Não informada")}</dd>'
            f'<dt>Fornecedor (CNPJ público)</dt><dd>{esc(row.supplier_cnpj or "Não informado")}</dd>'
            f'<dt>Documento</dt><dd>{esc(row.invoice_id or "Não informado")}</dd>'
            f'<dt>Evidências informadas</dt><dd>{evidence}</dd>'
            f'<dt>Outros registros do dia</dt><dd>{same_day}</dd>'
            '</dl></article>'
        )

    limitations = "".join(
        f"<li>{esc(item)}</li>" for item in screening.get("limitations", [])
    )
    return (
        "<!doctype html><html lang=\"pt-BR\"><head>"
        "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>VTB | Revisão documental</title>"
        "<style>"
        "body{font:16px/1.5 system-ui,sans-serif;background:#f7f8fa;color:#16202c;max-width:1040px;"
        "margin:auto;padding:20px}main,header,footer{background:white;border:1px solid #dce2e8;"
        "border-radius:10px;padding:20px;margin:14px 0}h1,h2,h3{line-height:1.2}a{color:#135b9a}"
        ".signal,.expense{border-top:1px solid #dce2e8;padding:12px 0}dl{display:grid;"
        "grid-template-columns:minmax(150px,220px) 1fr;gap:6px}dt{font-weight:700}"
        "summary{cursor:pointer}@media(max-width:600px){dl{grid-template-columns:1fr}}"
        "@media print{body{background:white}header,main{border:none}}"
        "</style></head><body>"
        "<header><h1>Tinker Bell — revisão documental</h1>"
        "<p>Protótipo inspirado no Jarbas da Serenata de Amor. "
        "Somente triagem de documentos fornecidos; não comprova desvio nem corrupção.</p>"
        f'<p><strong>Registros:</strong> {len(expenses)} | '
        f'<strong>Alertas:</strong> {len(screening.get("signals", []))} | '
        f'<strong>Prioridade de revisão:</strong> {esc(screening.get("triage_band", "UNKNOWN"))}</p>'
        '<nav><a href="#alerts">Alertas</a> | <a href="#records">Despesas</a> | '
        '<a href="#limits">Limites</a></nav></header>'
        '<main id="alerts"><h2>Alertas que exigem verificação</h2>'
        + ("".join(sections) or "<p>Nenhum alerta nas regras aplicáveis aos dados fornecidos.</p>")
        + '</main><main id="records"><h2>Documentos e registros correlatos</h2>'
        + "".join(expense_articles)
        + '</main><footer id="limits"><h2>Limites da análise</h2><ul>'
        + limitations
        + '</ul><p>Identificadores de evidência foram fornecidos pelo analista; '
        "a conferência dos originais ainda é necessária.</p></footer></body></html>"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Produce private Jarbas-style HTML case review")
    p.add_argument("input", help="Original JSON input with expenses")
    p.add_argument("--screening", help="Existing screening JSON report; otherwise re-screen locally")
    p.add_argument("--output", required=True, help="Local HTML file (not public)")
    args = p.parse_args(argv)
    path = Path(args.input)
    dest = Path(args.output)
    if dest.resolve() == path.resolve():
        p.error("Output must differ from input")
    raw = json.loads(path.read_text(encoding="utf-8"))
    expenses = [PublicExpense.from_dict(v) for v in raw["expenses"]]
    if args.screening:
        screening = json.loads(Path(args.screening).read_text(encoding="utf-8"))
    else:
        screening = screen_expenses(expenses)
    generated = render_review(expenses, screening)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as handle:
        handle.write(generated)
    print(json.dumps({"html": str(dest), "records": len(expenses),
                      "signals": len(screening.get("signals", []))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
