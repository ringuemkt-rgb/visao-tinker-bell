"""Canais oficiais para protocolo humano. O sistema nao envia a peca."""

from __future__ import annotations

from typing import Any

CANAIS = [
    {
        "id": "falabr",
        "nome": "Fala.BR / CGU",
        "url": "https://falabr.cgu.gov.br/web/manifestacao/criar?tipo=1&anonimo=true",
        "esfera": "federal",
        "quando": "Irregularidade em orgao federal, emenda, servidor federal, contrato federal.",
        "anonimo": True,
        "relato_max": 7000,
        "anexo_mb": 30,
        "retorno": False,
    },
    {
        "id": "tcu",
        "nome": "Ouvidoria do TCU",
        "url": "https://portal.tcu.gov.br/ouvidoria/",
        "esfera": "federal",
        "quando": "Contas, contrato, licitacao ou ato de gestor federal.",
        "anonimo": True,
        "relato_max": 7000,
        "anexo_mb": 30,
        "retorno": False,
    },
    {
        "id": "mpf",
        "nome": "Ministerio Publico Federal",
        "url": "https://www.mpf.mp.br/servicos/denuncias",
        "esfera": "federal",
        "quando": "Fato com possivel lesao a bem federal. Anonimo total nao acompanha.",
        "anonimo": True,
        "relato_max": 7000,
        "anexo_mb": 30,
        "retorno": False,
    },
    {
        "id": "camara",
        "nome": "Ouvidoria da Camara",
        "url": "https://www.camara.leg.br/ouvidoria",
        "esfera": "federal",
        "quando": "Cota parlamentar, ato de deputado, uso da CEAP.",
        "anonimo": True,
        "relato_max": 7000,
        "anexo_mb": 30,
        "retorno": False,
    },
]


def escolher(meta: dict[str, Any]) -> list[dict[str, Any]]:
    esfera = (meta.get("esfera") or "federal").lower()
    tema = (meta.get("tema") or "").lower()
    chosen = [c for c in CANAIS if c["esfera"] == esfera or esfera == "federal"]
    if "ceap" in tema or "deput" in tema:
        preferred = [c for c in CANAIS if c["id"] in {"falabr", "camara"}]
        rest = [c for c in chosen if c["id"] not in {"falabr", "camara"}]
        chosen = preferred + rest
    return chosen or CANAIS[:1]


def folha(meta: dict[str, Any]) -> str:
    lines = [
        "CANAIS. Protocolo humano. Este sistema nao envia a peca.",
        "Anonimo no Fala.BR nao gera protocolo de retorno.",
        "Cole relato.txt no campo descricao. Anexe representacao.pdf se o canal aceitar.",
        "",
    ]
    for canal in escolher(meta):
        lines.append(f"{canal['nome']}: {canal['url']}")
        lines.append(f"Quando: {canal['quando']}")
        lines.append("")
    lines.append("Nao protocolar se o relato nao tiver URL e SHA-256 em cada fato.")
    return "\n".join(lines).strip()
