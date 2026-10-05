"""Sinais deterministicos. Saida sempre ANOMALY_FOR_VERIFICATION.

Nao copia codigo de terceiros. Regras proprias, inspiradas em padroes
publicos (ciclo de doacao, despesa fora da mediana, socio-fornecedor,
eixos de preco/relacao/objeto/estrutura/sancao). Sobrenome igual e
homonimo, nunca aresta.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

LABEL = "ANOMALY_FOR_VERIFICATION"


def disproportionate_expense(
    valor: float,
    mediana: float,
    fator: float = 5.0,
) -> dict[str, Any] | None:
    if mediana <= 0 or valor <= 0:
        return None
    razao = valor / mediana
    if razao < fator:
        return None
    return {
        "rule_id": "despesa-desproporcional",
        "label": LABEL,
        "razao": round(razao, 2),
        "valor": valor,
        "mediana": mediana,
        "limite": "Mediana da categoria nao prova sobrepreco. Conferir item e unidade.",
    }


def supplier_partner(
    documentos_candidato: list[str],
    socios: list[dict[str, str]],
) -> list[dict[str, Any]]:
    alvo = {_digits(d) for d in documentos_candidato if _digits(d)}
    hits = []
    for socio in socios:
        doc = _digits(socio.get("documento", ""))
        if doc and doc in alvo:
            hits.append(
                {
                    "rule_id": "candidato-socio-fornecedor",
                    "label": LABEL,
                    "documento": doc,
                    "cnpj_fornecedor": socio.get("cnpj", ""),
                    "limite": "Documento igual em base publica. Nao afirma controle nem ilicito.",
                }
            )
    return hits


def surname_homonym(sobrenome: str, nomes: list[str]) -> dict[str, Any] | None:
    key = _norm(sobrenome)
    if len(key) < 4:
        return None
    matches = [n for n in nomes if key and key in _norm(n).split()]
    if not matches:
        return None
    return {
        "rule_id": "sobrenome-homonimo",
        "label": LABEL,
        "sobrenome": sobrenome,
        "ocorrencias": matches,
        "limite": "Homonimo. Nao cria aresta nem identifica pessoa.",
    }


def circular_flows(edges: list[dict[str, Any]], min_valor: float = 10_000) -> list[dict[str, Any]]:
    """Ciclo curto doador -> candidato -> fornecedor -> doador. Aresta precisa de id e valor."""
    graph: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for edge in edges:
        src, dst = edge.get("src"), edge.get("dst")
        if not src or not dst or src == dst:
            continue
        graph[str(src)].append((str(dst), float(edge.get("valor") or 0)))
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for start in list(graph):
        _walk(graph, start, [start], 0.0, found, seen, min_valor, depth=0)
    return found


def score_contratacao(ctx: dict[str, Any]) -> dict[str, Any]:
    preco = _eixo_preco(float(ctx.get("preco_sobre_mediana") or 0))
    relacao = _eixo_relacao(ctx)
    objeto = 25 if ctx.get("cnae_incompativel") else 0
    estrutural = 0
    if int(ctx.get("participantes") or 99) == 1:
        estrutural += 15
    if ctx.get("prazo_edital_dias") is not None and int(ctx["prazo_edital_dias"]) < 3:
        estrutural += 10
    if ctx.get("empresa_dias") is not None and int(ctx["empresa_dias"]) < 180:
        estrutural += 10
    estrutural = min(35, estrutural)
    sancao = 35 if int(ctx.get("count_ceis") or 0) + int(ctx.get("count_cnep") or 0) > 0 else 0
    total = min(100, preco + relacao + objeto + estrutural + sancao)
    return {
        "rule_id": "score-contratacao",
        "label": LABEL,
        "score": total,
        "fila": total >= 50,
        "eixos": {
            "preco": preco,
            "relacao": relacao,
            "objeto": objeto,
            "estrutural": estrutural,
            "sancao": sancao,
        },
        "limite": "Score e fila de leitura. Nao e risco provado nem irregularidade.",
    }


def _eixo_preco(razao: float) -> int:
    if razao >= 3:
        return 40
    if razao >= 1.5:
        return 20
    return 0


def _eixo_relacao(ctx: dict[str, Any]) -> int:
    if ctx.get("documento_socio_igual"):
        return 50
    if ctx.get("doacao_campanha"):
        return 30
    if ctx.get("sobrenome_igual"):
        return 10
    return 0


def _walk(graph, start, path, total, found, seen, min_valor, depth) -> None:
    if depth >= 4:
        return
    for dst, valor in graph.get(path[-1], []):
        if dst == start and len(path) >= 3:
            ciclo = tuple(path)
            key = tuple(sorted(ciclo))
            if key in seen:
                continue
            seen.add(key)
            if total + valor >= min_valor:
                found.append(
                    {
                        "rule_id": "fluxo-circular",
                        "label": LABEL,
                        "ciclo": list(ciclo),
                        "valor": round(total + valor, 2),
                        "limite": "Ciclo pode ser coligacao, reembolso ou homonimo. Nao e lavagem.",
                    }
                )
            continue
        if dst in path:
            continue
        _walk(graph, start, path + [dst], total + valor, found, seen, min_valor, depth + 1)


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _norm(value: str) -> str:
    return " ".join(value.lower().split())
