#!/usr/bin/env python3
"""
Visão Tinker Bell — Clientes mínimos para APIs públicas
(PNCP, BrasilAPI CNPJ, placeholders para Câmara/TSE/Portal).
Sem chave por padrão. Respeite rate limits e termos de uso.
"""

from __future__ import annotations

import requests
from typing import Any, Dict, Optional

HEADERS = {
    "User-Agent": "VisaoTinkerBell/0.1 (pesquisa-transparencia; evidence-only)",
    "Accept": "application/json",
}


def consultar_cnpj(cnpj: str) -> Optional[Dict[str, Any]]:
    """Consulta CNPJ via BrasilAPI (público, sem chave)."""
    cnpj = "".join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14:
        return None
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def consultar_pncp_contrato(orgao_cnpj: str, ano: int, sequencial: int) -> Optional[Dict[str, Any]]:
    """Consulta detalhe de contrato no PNCP (exemplo de endpoint)."""
    url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def build_context_from_cnpj(cnpj: str, valor_contrato: float = 0) -> Dict[str, Any]:
    """Exemplo: monta contexto parcial a partir de um CNPJ para o motor de red flags."""
    data = consultar_cnpj(cnpj)
    if not data:
        return {}
    return {
        "cnpj": cnpj,
        "descricao_situacao_cadastral": data.get("descricao_situacao_cadastral"),
        "situacao": data.get("descricao_situacao_cadastral"),
        "capital_social": float(data.get("capital_social") or 0),
        "data_inicio_atividade": data.get("data_inicio_atividade"),
        "valorGlobal": valor_contrato,
        "razao_social": data.get("razao_social"),
    }


if __name__ == "__main__":
    print("Funções prontas: consultar_cnpj(), build_context_from_cnpj()")
