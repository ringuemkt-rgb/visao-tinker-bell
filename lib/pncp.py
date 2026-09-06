#!/usr/bin/env python3
"""
Visão Tinker Bell — Cliente PNCP (Portal Nacional de Contratações Públicas)
API pública de consulta: https://pncp.gov.br/api/consulta
Swagger: https://pncp.gov.br/api/consulta/swagger-ui/index.html
Sem autenticação. Respeite rate limits.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

import requests

BASE = "https://pncp.gov.br/api/consulta"
HEADERS = {
    "User-Agent": "VisaoTinkerBell/0.4 (pesquisa-transparencia; evidence-only)",
    "Accept": "application/json",
}

# Modalidades comuns (Lei 14.133) — códigos usados na API de publicação
MODALIDADES = {
    1: "Leilão - Eletrônico",
    2: "Diálogo Competitivo",
    3: "Concurso",
    4: "Concorrência - Eletrônica",
    5: "Concorrência - Presencial",
    6: "Pregão - Eletrônico",
    7: "Pregão - Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    11: "Pré-qualificação",
    12: "Credenciamento",
    13: "Leilão - Presencial",
}


def _get(path: str, params: Optional[Dict] = None, timeout: int = 30) -> Any:
    url = f"{BASE}{path}"
    r = requests.get(url, headers=HEADERS, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def consultar_contratacao(orgao_cnpj: str, ano: int, sequencial: int) -> Optional[Dict[str, Any]]:
    """GET /v1/orgaos/{cnpj}/compras/{ano}/{sequencial}"""
    cnpj = "".join(filter(str.isdigit, orgao_cnpj))
    try:
        return _get(f"/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}")
    except Exception:
        return None


def listar_contratacoes_publicacao(
    data_inicial: str,
    data_final: str,
    codigo_modalidade: int,
    pagina: int = 1,
    tamanho_pagina: int = 50,
) -> Dict[str, Any]:
    """
    GET /v1/contratacoes/publicacao
    datas no formato YYYYMMDD
    codigo_modalidade: ver MODALIDADES (ex.: 6=pregão eletrônico, 8=dispensa)
    """
    params = {
        "dataInicial": data_inicial.replace("-", ""),
        "dataFinal": data_final.replace("-", ""),
        "codigoModalidadeContratacao": codigo_modalidade,
        "pagina": pagina,
        "tamanhoPagina": min(max(tamanho_pagina, 10), 50),
    }
    return _get("/v1/contratacoes/publicacao", params)


def iter_contratacoes_publicacao(
    data_inicial: str,
    data_final: str,
    codigo_modalidade: int,
    max_paginas: int = 20,
    pausa: float = 0.4,
) -> Iterator[Dict[str, Any]]:
    """Itera páginas de contratações publicadas."""
    pagina = 1
    while pagina <= max_paginas:
        data = listar_contratacoes_publicacao(
            data_inicial, data_final, codigo_modalidade, pagina=pagina
        )
        items = data if isinstance(data, list) else data.get("data") or data.get("content") or []
        if not items:
            break
        for item in items:
            yield item
        if len(items) < 10:
            break
        pagina += 1
        time.sleep(pausa)


def listar_contratos(
    data_inicial: str,
    data_final: str,
    pagina: int = 1,
    cnpj: Optional[str] = None,
) -> Any:
    """GET /v1/contratos — contratos/empenhos por data de publicação."""
    params: Dict[str, Any] = {
        "dataInicial": data_inicial.replace("-", ""),
        "dataFinal": data_final.replace("-", ""),
        "pagina": pagina,
    }
    if cnpj:
        params["cnpj"] = "".join(filter(str.isdigit, cnpj))
    return _get("/v1/contratos", params)


def extrair_contexto_red_flags(contratacao: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza campos típicos da API PNCP para o motor de red flags.
    Campos variam entre endpoints; tenta várias chaves comuns.
    """
    def g(*keys, default=None):
        for k in keys:
            if k in contratacao and contratacao[k] is not None:
                return contratacao[k]
        return default

    valor = g(
        "valorTotalHomologado",
        "valorGlobal",
        "valorTotalEstimado",
        "valor",
        default=0,
    )
    try:
        valor = float(valor or 0)
    except (TypeError, ValueError):
        valor = 0.0

    modalidade = g("modalidadeId", "codigoModalidadeContratacao", "modalidade")
    fornecedor_cnpj = g(
        "niFornecedor",
        "cnpjFornecedor",
        "fornecedorCnpj",
        "numeroDocumentoFornecedor",
    )
    if fornecedor_cnpj:
        fornecedor_cnpj = "".join(filter(str.isdigit, str(fornecedor_cnpj)))

    return {
        "valorGlobal": valor,
        "valorTotalEstimado": valor,
        "modalidadeId": modalidade,
        "frutoAdesao": bool(g("frutoAdesao", default=False)),
        "numeroRetificacao": int(g("numeroRetificacao", "retificacao", default=0) or 0),
        "dataPublicacaoPncp": g("dataPublicacaoPncp", "dataPublicacao", "dataInclusao"),
        "dataEncerramentoProposta": g(
            "dataEncerramentoProposta", "dataEncerramento", "dataFimPropostas"
        ),
        "dataVigenciaInicio": g("dataVigenciaInicio", "dataInicioVigencia"),
        "dataVigenciaFim": g("dataVigenciaFim", "dataFimVigencia"),
        "dataAssinatura": g("dataAssinatura", "dataAssinaturaContrato"),
        "orgao_cnpj": g("orgaoCnpj", "cnpjOrgao", "cnpjEntidade"),
        "uf_orgao": g("uf", "ufOrgao", "unidadeFederativa"),
        "objeto": g("objetoCompra", "objeto", "objetoContrato"),
        "fornecedor_cnpj": fornecedor_cnpj,
        "fornecedor_nome": g(
            "nomeRazaoSocialFornecedor", "razaoSocialFornecedor", "nomeFornecedor"
        ),
        "amparoLegal": str(g("amparoLegal", "amparoLegalDescricao", default="") or ""),
        "raw_keys": list(contratacao.keys()),
    }


def pipeline_contratacao_para_flags(
    orgao_cnpj: str,
    ano: int,
    sequencial: int,
    enriquecer_fornecedor: bool = True,
) -> Dict[str, Any]:
    """
    Busca contratação no PNCP, monta contexto de red flags e opcionalmente
    enriquece com BrasilAPI + CEIS/CNEP do fornecedor.
    """
    from lib.api_clients import build_context_from_cnpj  # evita ciclo no import inicial

    raw = consultar_contratacao(orgao_cnpj, ano, sequencial)
    if not raw:
        return {"erro": "contratacao_nao_encontrada", "orgao": orgao_cnpj, "ano": ano, "seq": sequencial}

    ctx = extrair_contexto_red_flags(raw)
    ctx["pncp_raw"] = {k: raw[k] for k in list(raw.keys())[:40]}  # amostra

    forn = ctx.get("fornecedor_cnpj")
    if enriquecer_fornecedor and forn and len(forn) == 14:
        extra = build_context_from_cnpj(forn, valor_contrato=ctx["valorGlobal"])
        for k, v in extra.items():
            if k not in ctx or ctx[k] in (None, "", 0):
                ctx[k] = v
        if "dataAssinatura" in ctx and "data_inicio_atividade" in extra:
            ctx["data_inicio_atividade"] = extra.get("data_inicio_atividade")

    return ctx


if __name__ == "__main__":
    print("PNCP client OK. MODALIDADES:", list(MODALIDADES.items())[:5], "...")
    print("Funções: consultar_contratacao, listar_contratacoes_publicacao,")
    print("         listar_contratos, pipeline_contratacao_para_flags")
