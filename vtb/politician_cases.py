"""Neutral, source-scoped investigation bootstrap for any Brazilian political office.

This module does not search networks or identify people automatically. A case is
never a criminal finding, and all planned sources start as NOT_QUERIED.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

UF_CODES = frozenset(
    "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
)
OFFICE_ALIASES = {
    "vereador": "vereador",
    "vereadora": "vereador",
    "prefeito": "prefeito",
    "prefeita": "prefeito",
    "vice-prefeito": "vice-prefeito",
    "vice-prefeita": "vice-prefeito",
    "deputado estadual": "deputado estadual",
    "deputada estadual": "deputado estadual",
    "deputado distrital": "deputado estadual",
    "deputada distrital": "deputado estadual",
    "deputado federal": "deputado federal",
    "deputada federal": "deputado federal",
    "senador": "senador",
    "senadora": "senador",
    "governador": "governador",
    "governadora": "governador",
    "vice-governador": "vice-governador",
    "vice-governadora": "vice-governador",
    "presidente da república": "presidente",
    "vice-presidente da república": "vice-presidente",
    "presidente da câmara municipal": "vereador",
    "presidenta da câmara municipal": "vereador",
    "presidente da assembleia": "deputado estadual",
    "presidente do senado": "senador",
    "presidente da câmara dos deputados": "deputado federal",
    "ministro": "ministro",
    "ministra": "ministro",
    "secretario": "secretario",
    "secretaria": "secretario",
    "candidato": "candidato",
    "candidata": "candidato",
}
MUNICIPAL = {"vereador", "prefeito", "vice-prefeito"}
STATE = {"deputado estadual", "governador", "vice-governador"}
FEDERAL = {"deputado federal", "senador", "presidente", "vice-presidente", "ministro"}
STREAMS: tuple[tuple[str, str], ...] = (
    ("identity", "Mandatos, homônimos, cargo, nomes e ato de investidura"),
    ("electoral", "Candidaturas, patrimônio DECLARADO e prestações eleitorais"),
    ("official_acts", "Leis, emendas, votações, nomeações e atos administrativos"),
    ("contracts", "Licitações, contratos, aditivos, fornecedores e justificativas"),
    ("financial_flow", "Empenhos, liquidações, pagamentos, NFs e entregas"),
    ("organizational_links", "Empresas, OSCs, representação e datas dos vínculos"),
    ("oversight", "Auditorias e decisões, com estágio e situação processual exatos"),
    ("price_benchmark", "Preço de mercado com unidade, escopo e vigência comparáveis"),
    ("counterevidence", "Documentos regulares e hipóteses que refutam alertas"),
    ("legal_review", "Competência, norma aplicável, nexo e diligências necessárias"),
)


def _source(source_id: str, title: str, url: str | None, purpose: str, **kw: Any) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "issuer": title,
        "entrypoint_url": url,
        "purpose": purpose,
        "status": "NOT_QUERIED",
        "coverage": "UNVERIFIED",
        "retrieved_at_utc": None,
        "records_found": None,
        "source_health": "UNKNOWN",
        **kw,
    }


def _sources(office: str | None, uf: str | None, municipality: str | None) -> list[dict[str, Any]]:
    rows = [
        _source("TSE_CANDIDATES", "TSE", "https://dadosabertos.tse.jus.br/group/candidatos",
                "Confirmar candidato e identificadores eleitorais; comparar eleições e cargos."),
        _source("TSE_ACCOUNTS", "TSE", "https://dadosabertos.tse.jus.br/",
                "Consultar prestação de contas eleitoral, receitas, despesas e bens declarados."),
        _source("PNCP", "PNCP", "https://pncp.gov.br/",
                "Contratos, editais, aditivos e anexos; buscar por CNPJ, órgão e período."),
        _source("CGU", "Portal da Transparência", "https://portaldatransparencia.gov.br/",
                "Contratos e despesas federais, emendas e sanções; cobertura depende do órgão."),
        _source("CNJ", "CNJ", "https://www.cnj.jus.br/sistemas/datajud/",
                "Localizar processos públicos e confirmar decisões e estágio no tribunal."),
        _source("DOU", "Imprensa Nacional", "https://www.in.gov.br/",
                "Publicações oficiais federais pertinentes ao cargo e à competência."),
        _source("REVENUE", "Receita Federal", "https://www.gov.br/receitafederal/pt-br",
                "CNPJ e quadro societário quando publicamente disponível; atos históricos via registro."),
        _source("TRANSFEREGOV", "Transferegov", "https://www.gov.br/transferegov/pt-br",
                "Convênios, parcerias e transferências federais pertinentes."),
    ]
    if office in MUNICIPAL or office is None:
        rows.extend([
            _source("MUNICIPAL_EXECUTIVE", "Prefeitura / diário do município", None,
                    "Transparência municipal, pessoal, despesas e contratos oficiais.",
                    locator_required="municipality", scope_municipality=municipality, scope_uf=uf),
            _source("MUNICIPAL_COUNCIL", "Câmara Municipal", None,
                    "Atos, atas, votações, despesas legislativas e controle de conflitos.",
                    locator_required="municipality", scope_municipality=municipality, scope_uf=uf),
            _source("MUNICIPAL_AUDIT", "Tribunal de Contas com jurisdição municipal", 
                    "https://www.tcm.ba.gov.br/" if uf == "BA" else None,
                    "Processos de fiscalização e contas municipais; competência a confirmar.",
                    locator_required=None if uf == "BA" else "uf", scope_uf=uf),
        ])
    if office in STATE or office is None:
        rows.extend([
            _source("STATE_LEGISLATIVE", "Assembleia Legislativa / CLDF", None,
                    "Atos e despesas do parlamento estadual ou distrital.", locator_required="uf", scope_uf=uf),
            _source("STATE_EXECUTIVE", "Governo e Diário Oficial estadual", None,
                    "Transferências, nomeações, contratos e atos do Poder Executivo.", locator_required="uf", scope_uf=uf),
            _source("STATE_AUDIT", "Tribunal de Contas estadual/distrital", None,
                    "Fiscalização conforme origem do recurso e competência.", locator_required="uf", scope_uf=uf),
        ])
    if office == "deputado federal" or office is None:
        rows.append(_source("CHAMBER", "Câmara dos Deputados",
                            "https://dadosabertos.camara.leg.br/swagger/api.html",
                            "Mandato, autoria, votações e cota parlamentar (CEAP)."))
    if office == "senador" or office is None:
        rows.append(_source("SENATE", "Senado Federal", "https://www12.senado.leg.br/dados-abertos",
                            "Mandato, votações, relatórios e cota parlamentar (CEAPS)."))
    if office in FEDERAL or office is None:
        rows.append(_source("FEDERAL_ISSUER", "Órgão de exercício federal", None,
                            "Atos e despesas do órgão competente; identificar o órgão.",
                            locator_required="office"))
    if office in {"secretario", "candidato"}:
        rows.append(_source("APPOINTING_BODY", "Órgão/ente de exercício a determinar", None,
                            "Confirmar esfera e ato de nomeação, se houver.", locator_required="jurisdiction"))
    return rows


def build_politician_case(
    case_id: str,
    name: str,
    *,
    office: str | None = None,
    uf: str | None = None,
    municipality: str | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> dict[str, Any]:
    """Build an evidence-empty intake package; does NOT confirm identity or run an audit."""
    name = " ".join(name.split())
    if not name or len(name) > 180:
        raise ValueError("Political subject name must contain 1..180 characters")
    if not case_id.strip() or len(case_id) > 96:
        raise ValueError("case_id must contain 1..96 characters")
    office = office.strip().lower() if office else None
    if office and office not in OFFICE_ALIASES:
        raise ValueError("unsupported or ambiguous office; see --office in CLI documentation")
    office = OFFICE_ALIASES.get(office) if office else None
    uf = uf.upper().strip() if uf else None
    if uf is not None and uf not in UF_CODES:
        raise ValueError("UF must be a valid two-letter Brazilian state code")
    municipality = " ".join(municipality.split()) if municipality else None
    if municipality and not uf:
        raise ValueError("municipality requires UF to avoid geographic ambiguity")
    for year in (start_year, end_year):
        if year is not None and not (1889 <= year <= 2200):
            raise ValueError("years must be between 1889 and 2200")
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError("start_year cannot exceed end_year")
    cutoff = datetime.now(UTC).isoformat()
    jurisdiction = "/".join(x for x in (municipality, uf) if x) or "Brasil (a definir)"
    time_range = (
        f"{start_year or 'início não definido'}..{end_year or 'fim não definido'}"
    )
    question = f"Quais fatos documentados sobre a atuação pública de {name} podem ser confirmados ou refutados?"
    sources = _sources(office, uf, municipality)
    gaps = [
        {
            "description": "Identidade, cargo, mandatos e datas ainda não verificados",
            "source_needed": "TSE e ato oficial do órgão de exercício",
            "impact": "Bloqueia atribuição de atos, contratos e vínculos à pessoa",
        },
        {
            "description": "Não há peças originais preservadas e localizadas",
            "source_needed": "Documentos oficiais originais com data, URL, localizador e hash conferido",
            "impact": "Não permite fatos verificados nem conclusão sobre ilícitos",
        },
        {
            "description": "Execução financeira e eventual dano não conciliados",
            "source_needed": "Contrato, empenho, liquidação, pagamento, nota e entrega",
            "impact": "Não permite inferir pagamentos indevidos ou desvio",
        },
    ]
    report = {
        "report_id": case_id,
        "cutoff_at": cutoff,
        "scope": {"question": question, "jurisdiction": jurisdiction, "time_range": time_range},
        "methodology": [
            "Identidade verificada antes de cruzamentos; nome sozinho não confirma pessoa",
            "Documento oficial original antes de hipótese e acusação",
            "Contrato, empenho, liquidação e pagamento são etapas distintas",
            "Contraprovas, delimitação temporal e revisão humana obrigatórias",
        ],
        "entity_resolution": [
            {"candidate": name, "decision": "UNRESOLVED",
             "reason": "Nome informado; nenhum identificador ou mandato consultado", "evidence_ids": []}
        ],
        "findings": [],
        "hypotheses": [
            {"id": "H-REGULAR", "statement": "Os atos e despesas podem ter sido regulares",
             "status": "UNRESOLVED", "pro_evidence_ids": [], "contra_evidence_ids": []},
            {"id": "H-REGISTRATION", "statement": "Eventuais diferenças podem decorrer de erro ou cobertura incompleta",
             "status": "UNRESOLVED", "pro_evidence_ids": [], "contra_evidence_ids": []},
            {"id": "H-IRREGULAR", "statement": "Uma irregularidade específica só poderá ser formulada com fato e documento",
             "status": "UNRESOLVED", "pro_evidence_ids": [], "contra_evidence_ids": []},
        ],
        "evidence_gaps": gaps,
        "limitations": [
            "Pacote de abertura: nenhuma consulta externa realizada",
            "Documentos e vínculos ainda não comprovados; não imputar crimes",
            "Fontes locais e competências exigem localização e validação",
        ],
        "publication_status": "QUARANTINED",
    }
    return {
        "schema": "vtb.politician_case_intake.v1",
        "created_at_utc": cutoff,
        "case_id": case_id,
        "person": {
            "name_provided": name,
            "office_provided": office,
            "uf": uf,
            "municipality": municipality,
            "identity_status": "UNRESOLVED",
            "public_identifiers_verified": [],
            "mandates_verified": [],
        },
        "source_plan": sources,
        "workstreams": [
            {"id": key, "question": description, "state": "PENDING",
             "evidence_ids": [], "contradicting_evidence_ids": []}
            for key, description in STREAMS
        ],
        "coverage": {
            "sources_planned": len(sources),
            "sources_queried": 0,
            "documents_preserved": 0,
            "payments_reconciled": 0,
            "state": "NOT_STARTED",
        },
        "complaint_readiness": {
            "status": "NOT_ASSESSED",
            "reason": "Não existe documentação probatória suficiente para avaliar encaminhamento",
            "crime_or_corruption_score": None,
        },
        "report_template": report,
        "next_action": "Confirmar identidade, mandato e órgão competente em fontes oficiais antes de atribuir fatos.",
    }
