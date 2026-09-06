#!/usr/bin/env python3
"""
Visão Tinker Bell — Clientes para APIs públicas
BrasilAPI CNPJ, PNCP, CEIS/CNEP (Portal da Transparência).
Chave do Portal é opcional (env PORTAL_TRANSPARENCIA_KEY).
Respeite rate limits e termos de uso.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

HEADERS = {
    "User-Agent": "VisaoTinkerBell/0.3 (pesquisa-transparencia; evidence-only)",
    "Accept": "application/json",
}

PORTAL_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"


def _portal_headers() -> Dict[str, str]:
    h = dict(HEADERS)
    key = os.environ.get("PORTAL_TRANSPARENCIA_KEY") or os.environ.get("PORTAL_API_KEY")
    if key:
        h["chave-api-dados"] = key
    return h


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


def consultar_pncp_contrato(
    orgao_cnpj: str, ano: int, sequencial: int
) -> Optional[Dict[str, Any]]:
    orgao_cnpj = "".join(filter(str.isdigit, orgao_cnpj))
    url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def consultar_ceis(
    cnpj: str, pagina: int = 1
) -> List[Dict[str, Any]]:
    """
    Consulta CEIS (Cadastro de Empresas Inidôneas e Suspensas).
    Requer PORTAL_TRANSPARENCIA_KEY no ambiente.
    Cadastro gratuito: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
    """
    cnpj = "".join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14:
        return []
    if not (os.environ.get("PORTAL_TRANSPARENCIA_KEY") or os.environ.get("PORTAL_API_KEY")):
        return []
    url = f"{PORTAL_BASE}/ceis"
    params = {"codigoSancionado": cnpj, "pagina": pagina}
    try:
        r = requests.get(url, headers=_portal_headers(), params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def consultar_cnep(
    cnpj: str, pagina: int = 1
) -> List[Dict[str, Any]]:
    """
    Consulta CNEP (Cadastro Nacional de Empresas Punidas — Lei Anticorrupção).
    Requer PORTAL_TRANSPARENCIA_KEY.
    """
    cnpj = "".join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14:
        return []
    if not (os.environ.get("PORTAL_TRANSPARENCIA_KEY") or os.environ.get("PORTAL_API_KEY")):
        return []
    url = f"{PORTAL_BASE}/cnep"
    params = {"codigoSancionado": cnpj, "pagina": pagina}
    try:
        r = requests.get(url, headers=_portal_headers(), params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def sancao_resumo(cnpj: str) -> Dict[str, Any]:
    """Resumo CEIS+CNEP para alimentar o motor de red flags."""
    ceis = consultar_ceis(cnpj)
    cnep = consultar_cnep(cnpj)
    return {
        "cnpj": "".join(filter(str.isdigit, cnpj)),
        "count_ceis": len(ceis),
        "count_cnep": len(cnep),
        "ceis": ceis,
        "cnep": cnep,
        "sancionado": len(ceis) + len(cnep) > 0,
        "chave_configurada": bool(
            os.environ.get("PORTAL_TRANSPARENCIA_KEY") or os.environ.get("PORTAL_API_KEY")
        ),
    }


def build_context_from_cnpj(
    cnpj: str, valor_contrato: float = 0, incluir_sancoes: bool = True
) -> Dict[str, Any]:
    """Monta contexto para o motor de red flags a partir de CNPJ (+ sanções se chave)."""
    data = consultar_cnpj(cnpj)
    if not data:
        ctx: Dict[str, Any] = {"cnpj": cnpj, "valorGlobal": valor_contrato}
    else:
        ctx = {
            "cnpj": cnpj,
            "descricao_situacao_cadastral": data.get("descricao_situacao_cadastral"),
            "situacao": data.get("descricao_situacao_cadastral"),
            "capital_social": float(data.get("capital_social") or 0),
            "data_inicio_atividade": data.get("data_inicio_atividade"),
            "valorGlobal": valor_contrato,
            "razao_social": data.get("razao_social"),
            "uf_empresa": data.get("uf"),
            "opcao_pelo_mei": data.get("opcao_pelo_mei") or data.get("mei"),
        }
    if incluir_sancoes:
        s = sancao_resumo(cnpj)
        ctx["count_ceis"] = s["count_ceis"]
        ctx["count_cnep"] = s["count_cnep"]
    return ctx


if __name__ == "__main__":
    print("Clientes: consultar_cnpj, consultar_ceis, consultar_cnep, sancao_resumo")
    print("Defina PORTAL_TRANSPARENCIA_KEY para CEIS/CNEP.")
    print("Cadastro: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email")
