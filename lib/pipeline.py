"""Orquestrador de perícia pública — Visão Tinker Bell v7."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

from .ach import ACHMatrix
from .evidence import EvidenceStore

UA = {"User-Agent": "VisaoTinkerBell/7.0 (evidence-only; public-records)"}
BRASILAPI = "https://brasilapi.com.br/api"


@dataclass
class Entity:
    name: str
    role: str | None = None
    municipality: str | None = None
    uf: str | None = None
    party: str | None = None
    cnpjs: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class PericiaResult:
    entity: Entity
    companies: list[dict[str, Any]]
    flags: list[dict[str, Any]]
    ach_markdown: str
    evidence_markdown: str
    dossier_markdown: str


def digits(cnpj: str) -> str:
    return "".join(ch for ch in cnpj if ch.isdigit())


def consultar_cnpj(cnpj: str) -> dict[str, Any]:
    code = digits(cnpj)
    url = f"{BRASILAPI}/cnpj/v1/{code}"
    r = requests.get(url, headers=UA, timeout=25)
    r.raise_for_status()
    return r.json()


def evaluate_simple_flags(company: dict[str, Any], contract_value: float | None, orgao_uf: str | None) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    capital = float(company.get("capital_social") or 0)
    sit = (company.get("descricao_situacao_cadastral") or company.get("situacao") or "").upper()
    uf = company.get("uf")
    if sit and sit != "ATIVA":
        flags.append({"id": "situacao-irregular", "sev": "alta", "detalhe": sit})
    if contract_value and contract_value >= 10_000_000:
        flags.append({"id": "contrato-valor-global-elevado", "sev": "media", "detalhe": contract_value})
    if contract_value and capital and (capital / contract_value) < 0.01:
        flags.append({"id": "capital-incompativel", "sev": "media", "detalhe": f"{capital}/{contract_value}"})
    if orgao_uf and uf and uf != orgao_uf:
        flags.append({"id": "fornecedor-outra-uf", "sev": "baixa", "detalhe": f"{uf} vs {orgao_uf}"})
    return flags


def run_pericia(entity: Entity, contracts: list[dict[str, Any]] | None = None) -> PericiaResult:
    store = EvidenceStore()
    contracts = contracts or []
    companies: list[dict[str, Any]] = []
    flags: list[dict[str, Any]] = []

    for raw in entity.cnpjs:
        code = digits(raw)
        url = f"{BRASILAPI}/cnpj/v1/{code}"
        try:
            data = consultar_cnpj(code)
            store.add_api(f"cnpj-{code}", f"BrasilAPI CNPJ {code}", url, data, tier=1)
            companies.append(data)
            related = [c for c in contracts if digits(str(c.get("cnpj", ""))) == code]
            valor = related[0]["valor"] if related else None
            flags.extend(evaluate_simple_flags(data, valor, entity.uf))
        except Exception as exc:
            store.add_api(f"cnpj-{code}-erro", f"Falha CNPJ {code}", url, {"error": str(exc)}, tier=3)

    ach = ACHMatrix()
    if companies:
        ach.add("E-CNPJ", "Consulta cadastral pública retornou empresa ATIVA", {"H0": "C", "H1": "C", "H2": "NA", "H3": "I"})
    else:
        ach.add("E-CNPJ", "Não houve consulta CNPJ bem-sucedida", {"H0": "NA", "H1": "NA", "H2": "NA", "H3": "C"})
    if any(f["id"] == "contrato-valor-global-elevado" for f in flags):
        ach.add("E-VAL", "Contrato com valor global elevado (≥ R$ 10 mi)", {"H0": "C", "H1": "C", "H2": "C", "H3": "I"})
    if any(f["id"] == "fornecedor-outra-uf" for f in flags):
        ach.add("E-UF", "Sede da empresa em UF distinta do órgão", {"H0": "C", "H1": "C", "H2": "NA", "H3": "I"})
    if not flags:
        ach.add("E-SINAL", "Nenhum sinal determinístico disparado nesta rodada", {"H0": "C", "H1": "I", "H2": "I", "H3": "I"})

    dossier = _render_dossier(entity, companies, flags, contracts, ach, store)
    return PericiaResult(entity, companies, flags, ach.markdown(), store.markdown(), dossier)


def _render_dossier(entity, companies, flags, contracts, ach, store) -> str:
    hid, hlabel, score = ach.least_refuted()
    lines = [
        f"# Dossiê — {entity.name}",
        "",
        f"- Papel: {entity.role or '—'}",
        f"- Município/UF: {entity.municipality or '—'} / {entity.uf or '—'}",
        f"- Partido (declarado no caso): {entity.party or '—'}",
        "",
        "## Empresas consultadas",
        "",
    ]
    for c in companies:
        lines.append(
            f"- **{c.get('razao_social')}** ({c.get('cnpj')}) — {c.get('descricao_situacao_cadastral')} "
            f"— {c.get('municipio')}/{c.get('uf')} — capital R$ {c.get('capital_social')}"
        )
    lines += ["", "## Contratos informados no caso", ""]
    for ct in contracts:
        lines.append(f"- {ct.get('id')}: {ct.get('objeto')} — R$ {ct.get('valor')} — {ct.get('cnpj')} — {ct.get('fonte')}")
    lines += ["", "## Sinais (não são prova)", ""]
    if not flags:
        lines.append("- Nenhum sinal determinístico nesta rodada.")
    for f in flags:
        lines.append(f"- `{f['id']}` ({f['sev']}): {f['detalhe']}")
    lines += ["", "## ACH", "", ach.markdown(), "", f"**Saída:** {hid} — {hlabel}", "", "## Cadeia de evidências", "", store.markdown()]
    lines += [
        "",
        "## Limites",
        "",
        "Consulta CEIS/CNEP exige `PORTAL_TRANSPARENCIA_KEY`. ",
        "Este dossiê não é acusação. Valores e CNPJs devem ser conferidos no documento primário.",
    ]
    return "\n".join(lines) + "\n"


def load_caso(path: Path) -> tuple[Entity, list[dict[str, Any]]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError:
            raise SystemExit("Instale PyYAML para ler caso.yaml, ou use JSON.")
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)
    ent = data["entity"]
    entity = Entity(
        name=ent["name"],
        role=ent.get("role"),
        municipality=ent.get("municipality"),
        uf=ent.get("uf"),
        party=ent.get("party"),
        cnpjs=ent.get("cnpjs") or [],
        notes=ent.get("notes") or "",
    )
    return entity, data.get("contracts") or []
