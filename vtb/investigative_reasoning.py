"""Evidence-first forensic reasoning for public administrative records.

Technical adaptation of public TCU/CGU audit matrices, ACH/falsification and
source-lineage practices. This is *not* a legal opinion or an automated verdict.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from .models import (
    Claim,
    ClaimStatus,
    SourceHealth,
    SourceQuality,
)
from .runtime import CaseStore

MAX_CLAIMS = 75
MAX_HYPOTHESES = 20
SUPPORTED_CHECKS = frozenset({"SUPPORTS", "REFUTES", "NEUTRAL", "NOT_AVAILABLE"})
SUPPORTED_KINDS = frozenset({"regular", "irregularity", "uncertain"})
PRIMARY = {SourceQuality.S5_OFFICIAL_PRIMARY, SourceQuality.S6_ORIGINAL_SIGNED_ACT}
CRITICAL_GAPS = {
    "CRITICAL_NO_EVIDENCE", "EVIDENCE_ID_MISSING", "SOURCE_UNAVAILABLE",
    "PRIMARY_EVIDENCE_MISSING", "PROVENANCE_HASH_MISSING",
    "EVIDENCE_LOCATOR_MISSING", "UNRESOLVED_CONTRADICTION",
    "LEGAL_CRITERION_MISSING",
}
ACTION_BY_GAP = {
    "CRITICAL_NO_EVIDENCE": "Localizar documento oficial que sustente ou refute a alegação.",
    "EVIDENCE_ID_MISSING": "Corrigir referência a documento ainda não catalogado.",
    "SOURCE_UNAVAILABLE": "Repetir busca oficial em fonte saudável, sem inferir ausência.",
    "PRIMARY_EVIDENCE_MISSING": "Obter contrato, ato assinado ou documento primário do órgão competente.",
    "PROVENANCE_HASH_MISSING": "Preservar original e manifesto de integridade em storage controlado.",
    "EVIDENCE_LOCATOR_MISSING": "Identificar página, item, cláusula ou campo do documento.",
    "UNRESOLVED_CONTRADICTION": "Obter documentos de esclarecimento e examinar versões conflitantes.",
    "LEGAL_CRITERION_MISSING": "Conferir norma ou decisão na íntegra e sua vigência temporal.",
    "REGULAR_EXPLANATION_MISSING": "Formular e testar hipótese de legalidade ou explicação administrativa.",
    "HYPOTHESIS_UNTESTED": "Vincular hipóteses concorrentes a evidências rastreáveis.",
}


def _normal_line(value: Any, length: int = 900) -> str:
    return " ".join(str(value or "").split())[:length]


def _safe_md(value: Any) -> str:
    return _normal_line(value).replace("|", "∣").replace("<", "&lt;").replace(">", "&gt;")


def _verified_url(value: Any) -> bool:
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parts = urlsplit(value)
    return parts.scheme == "https" and bool(parts.netloc) and not parts.username


def reasoning_contract() -> dict[str, Any]:
    return {
        "engine": "VTB-REASONING-V1",
        "basis": ["CGU-AUDIT-FINDINGS", "TCU-MATRIX", "ACH", "SOURCE-LINEAGE"],
        "requires": ["existing_case", "source_evidence_claim_ledger", "rival_hypotheses"],
        "required_criteria_format": {"claim_id": {"criterion": "string", "source_url": "https URL"}},
        "assessment_values": sorted(SUPPORTED_CHECKS),
        "status_values": ["QUARANTINED", "INCONCLUSIVE", "READY_WITH_LIMITATIONS"],
        "auto_file": False,
        "publish": False,
        "human_validation_required": True,
        "no_crime_or_intent_inference": True,
        "max_claims": MAX_CLAIMS,
    }


def _hypothesis_matrix(
    listed: dict[str, dict[str, Any]],
    reviews: Any,
    evidence_ids: set[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(reviews, list) or len(reviews) > MAX_HYPOTHESES:
        raise ValueError("hypotheses must be a list of at most 20 entries")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in reviews:
        if not isinstance(item, dict):
            raise TypeError("invalid hypothesis assessment")
        hid = str(item.get("hypothesis_id", ""))
        kind = str(item.get("kind", ""))
        if hid not in listed or hid in seen or kind not in SUPPORTED_KINDS:
            raise ValueError(f"invalid or repeated hypothesis: {hid}")
        seen.add(hid)
        checks = item.get("checks", [])
        if not isinstance(checks, list) or len(checks) > 150:
            raise ValueError("invalid hypothesis checks")
        assessments = []
        for row in checks:
            if not isinstance(row, dict):
                raise TypeError("invalid evidence assessment")
            eid = str(row.get("evidence_id", ""))
            if eid not in evidence_ids:
                raise ValueError(f"unknown evidence: {eid}")
            value = str(row.get("assessment", "")).upper()
            if value not in SUPPORTED_CHECKS:
                raise ValueError("assessment must be SUPPORTS/REFUTES/NEUTRAL/NOT_AVAILABLE")
            assessments.append({"evidence_id": eid, "assessment": value})
        records.append({
            "hypothesis_id": hid,
            "kind": kind,
            "statement": _normal_line(listed[hid].get("statement")),
            "falsifier": _normal_line(listed[hid].get("falsifier")),
            "checks": assessments,
            "supports": sum(x["assessment"] == "SUPPORTS" for x in assessments),
            "refutes": sum(x["assessment"] == "REFUTES" for x in assessments),
            "interpretation": "HYPOTHESIS_NOT_A_VERDICT",
        })
    gaps: list[str] = []
    if not any(x["kind"] == "regular" for x in records):
        gaps.append("REGULAR_EXPLANATION_MISSING")
    if not records or any(not x["checks"] or not x["falsifier"] for x in records):
        gaps.append("HYPOTHESIS_UNTESTED")
    return records, gaps


def _one_finding(
    claim: Claim,
    evidence: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    criterion: Any,
) -> dict[str, Any]:
    gaps: list[str] = []
    valid_records: list[dict[str, Any]] = []
    lineages: set[str] = set()
    if not claim.evidence_ids:
        gaps.append("CRITICAL_NO_EVIDENCE" if claim.critical else "NO_EVIDENCE")
    for eid in claim.evidence_ids:
        data = evidence.get(eid)
        if data is None:
            gaps.append("EVIDENCE_ID_MISSING")
            continue
        source = sources.get(data.get("source_id"))
        if source is None:
            gaps.append("EVIDENCE_ID_MISSING")
            continue
        quality = str(source.get("quality", ""))
        health = str(source.get("health", ""))
        is_primary = quality in PRIMARY
        healthy = health == SourceHealth.HEALTHY
        sha = str(source.get("sha256") or "")
        locator = str(data.get("locator") or "")
        if not healthy:
            gaps.append("SOURCE_UNAVAILABLE")
        if not is_primary:
            gaps.append("PRIMARY_EVIDENCE_MISSING")
        if not re.fullmatch("[0-9a-fA-F]{64}", sha):
            gaps.append("PROVENANCE_HASH_MISSING")
        if not locator.strip():
            gaps.append("EVIDENCE_LOCATOR_MISSING")
        if is_primary and healthy:
            lineages.add(str(source.get("original_source_id") or source.get("parent_source_id") or source["source_id"]))
        valid_records.append({
            "evidence_id": eid,
            "source_id": str(source["source_id"]),
            "url": source.get("url"),
            "locator": locator,
            "sha256": sha or None,
            "source_health": health,
            "source_quality": quality,
            "lineage": str(source.get("original_source_id") or source.get("parent_source_id") or source["source_id"]),
            "excerpt": _normal_line(data.get("excerpt"), 400),
        })
    if claim.contradicting_evidence_ids:
        gaps.append("UNRESOLVED_CONTRADICTION")
    if not any(row["source_quality"] in PRIMARY and row["source_health"] == SourceHealth.HEALTHY for row in valid_records):
        gaps.append("PRIMARY_EVIDENCE_MISSING")
    legal: dict[str, Any] | None = None
    if isinstance(criterion, dict):
        statement = str(criterion.get("criterion", "")).strip()
        source_url = criterion.get("source_url")
        if statement and _verified_url(source_url):
            legal = {"criterion": _normal_line(statement), "source_url": str(source_url)}
    if claim.legal_sensitive and legal is None:
        gaps.append("LEGAL_CRITERION_MISSING")
    classification = ClaimStatus.UNVERIFIED
    if valid_records and not gaps:
        classification = (
            ClaimStatus.VERIFIED_CORROBORATED if len(lineages) >= 2
            else ClaimStatus.VERIFIED_PRIMARY
        )
    if "UNRESOLVED_CONTRADICTION" in gaps:
        classification = ClaimStatus.DOCUMENT_CONFLICT

    return {
        "claim_id": claim.claim_id,
        "condition": _normal_line(claim.statement),
        "critical": claim.critical,
        "legal_sensitive": claim.legal_sensitive,
        "classification": str(classification),
        "criterion": legal,
        "evidence": valid_records,
        "source_lineages": len(lineages),
        "contradicting_evidence_ids": list(claim.contradicting_evidence_ids),
        "gaps": sorted(set(gaps)),
        "cause": "NÃO DETERMINADA — exigir prova independente",
        "effect": "NÃO QUANTIFICADO — diferenciar contratação, empenho, liquidação e pagamento",
        "response_of_audited_entity": "NÃO DOCUMENTADA NESTA MATRIZ",
        "disposition": "DILIGÊNCIA OU REVISÃO HUMANA — não imputar autoria nem dolo",
    }


def _markdown(result: dict[str, Any]) -> str:
    m = result["mission"]
    lines = [
        "# Dossiê de auditoria documental — para revisão humana",
        "",
        "**Não protocolado. Não constitui acusação nem parecer jurídico.**",
        f"**Caso:** {_safe_md(m['case_id'])}",
        f"**Questão:** {_safe_md(m['question'])}",
        f"**Escopo:** {_safe_md(m.get('geography'))}; {_safe_md(m.get('time_range'))}",
        f"**Estado:** {result['status']}",
        "",
        "## Matriz de achados (TCU/CGU — adaptação)",
        "| Alegação | Critério | Evidência e localização | Lacunas |",
        "| --- | --- | --- | --- |",
    ]
    for item in result["matrix"]:
        evidence = "; ".join(
            f"{_safe_md(e['evidence_id'])} — {_safe_md(e['locator'])} — {_safe_md(e['url'])}"
            for e in item["evidence"]
        ) or "PENDENTE"
        criterion = item["criterion"]
        criterion_text = (
            f"{_safe_md(criterion['criterion'])} ({_safe_md(criterion['source_url'])})"
            if criterion else "PENDENTE DE VALIDAÇÃO"
        )
        lines.append(
            f"| {_safe_md(item['claim_id'])}: {_safe_md(item['condition'])} | "
            f"{criterion_text} | {evidence} | {', '.join(item['gaps']) or 'sem lacunas estruturais'} |"
        )
    lines.extend(["", "## Hipóteses rivais e testes de falsificação"])
    for hypothesis in result["hypotheses"]:
        lines.append(
            f"- **{_safe_md(hypothesis['hypothesis_id'])} ({hypothesis['kind']})**: "
            f"{_safe_md(hypothesis['statement'])}. Como refutar: {_safe_md(hypothesis['falsifier'])}. "
            f"Avaliações declaradas: {len(hypothesis['checks'])}. "
            "Nenhuma hipótese foi juridicamente confirmada."
        )
    lines.extend(["", "## Lacunas gerais", *[f"- {x}" for x in result["global_gaps"]]])
    lines.extend(["", "## Próximas diligências sugeridas"])
    lines.extend([f"- {x}" for x in result["next_actions"]])
    lines.extend([
        "",
        "## Limitações e responsabilidades",
        ("As classificações descrevem COMPLETUDE DOCUMENTAL, não veracidade material ou culpa. "
         "Os conteúdos e vínculos devem ser conferidos nos originais. Revisão humana, jurídica "
         "e contraditório são necessários antes de qualquer protocolo."),
        "",
        "**Publicação automática: proibida. Dolo e responsabilidade: não inferidos.**",
    ])
    return "\n".join(lines) + "\n"


def audit_dossier(store: CaseStore, case_id: str, review: dict[str, Any]) -> dict[str, Any]:
    """Read-only dossier QA against an existing case, using only stored evidence."""
    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    snapshot = store.export_case(case_id)
    source_rows = {r["source_id"]: r["payload"] for r in snapshot["sources"]}
    evidence_rows = {r["evidence_id"]: r["payload"] for r in snapshot["evidence"]}
    claim_rows = snapshot["claims"]
    hypothesis_rows = {r["hypothesis_id"]: r["payload"] for r in snapshot["hypotheses"]}
    if len(claim_rows) > MAX_CLAIMS:
        raise ValueError("dossier claim limit exceeded")
    criteria = review.get("criteria", {})
    if not isinstance(criteria, dict):
        raise TypeError("criteria must be a mapping")
    matrix = [
        _one_finding(Claim(**row["payload"]), evidence_rows, source_rows, criteria.get(row["claim_id"]))
        for row in claim_rows
    ]
    hypotheses, global_gaps = _hypothesis_matrix(
        hypothesis_rows, review.get("hypotheses", []), set(evidence_rows),
    )
    if not snapshot["mission"].get("geography") or not snapshot["mission"].get("time_range"):
        global_gaps.append("SCOPE_INCOMPLETE")
    if not matrix:
        global_gaps.append("NO_CLAIMS")
    critical_breaks = any(
        finding["critical"] and any(gap in CRITICAL_GAPS for gap in finding["gaps"])
        for finding in matrix
    )
    if critical_breaks:
        status = "QUARANTINED"
    elif global_gaps or any(item["gaps"] for item in matrix):
        status = "INCONCLUSIVE"
    else:
        status = "READY_WITH_LIMITATIONS"
    all_gaps = sorted(set(global_gaps) | {
        gap for finding in matrix for gap in finding["gaps"]
    })
    next_actions = [
        ACTION_BY_GAP.get(gap, f"Revisar lacuna documental: {gap}")
        for gap in all_gaps
    ] or [
        "Conferir manualmente o inteiro teor de cada documento e o nexo com a alegação.",
        "Obter esclarecimentos administrativos, testar a hipótese regular e validar a legislação.",
    ]
    result: dict[str, Any] = {
        "engine": "VTB-REASONING-V1",
        "mission": snapshot["mission"],
        "status": status,
        "matrix": matrix,
        "hypotheses": hypotheses,
        "global_gaps": sorted(set(global_gaps)),
        "next_actions": next_actions,
        "publication_authorized": False,
        "human_validation_required": True,
        "inference_of_criminal_intent": False,
    }
    result["markdown"] = _markdown(result)
    return result
