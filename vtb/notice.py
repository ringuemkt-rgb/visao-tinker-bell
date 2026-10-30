"""Conservative Markdown draft from an existing case's corroborated records.

No publishing, filing, network access, or automatic legal classification.
"""
from __future__ import annotations

from typing import Any

from .claims import ClaimLedger
from .models import Claim, EvidenceRecord, SourceHealth, SourceQuality, SourceRecord
from .runtime import CaseStore


def _one_line(text: Any, limit: int = 1200) -> str:
    return " ".join(str(text).split())[:limit]


def draft_case_notice(
    store: CaseStore, case_id: str, recipient: str, claim_ids: list[str]
) -> dict[str, Any]:
    """Require actual healthy primary records and explicit evidence IDs."""
    if not isinstance(recipient, str) or not 3 <= len(recipient.strip()) <= 200:
        raise ValueError("recipient authority is required")
    if not isinstance(claim_ids, list) or not 1 <= len(claim_ids) <= 10:
        raise ValueError("select 1..10 supported claim IDs")
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("duplicate claim IDs")
    snapshot = store.export_case(case_id)
    ledger = ClaimLedger()
    source_payloads = {x["source_id"]: x["payload"] for x in snapshot["sources"]}
    evidence_payloads = {x["evidence_id"]: x["payload"] for x in snapshot["evidence"]}
    claim_payloads = {x["claim_id"]: x["payload"] for x in snapshot["claims"]}
    selected = []
    for claim_id in claim_ids:
        if claim_id not in claim_payloads:
            raise ValueError(f"claim unknown: {claim_id}")
        claim = Claim(**claim_payloads[claim_id])
        if not claim.evidence_ids or claim.contradicting_evidence_ids:
            raise ValueError(f"unresolved evidence for: {claim_id}")
        for evidence_id in claim.evidence_ids:
            evidence_data = evidence_payloads.get(evidence_id)
            if not evidence_data:
                raise ValueError(f"evidence not found: {evidence_id}")
            source_data = source_payloads.get(evidence_data["source_id"])
            if not source_data:
                raise ValueError(f"source not found: {evidence_id}")
            if evidence_data["source_id"] not in ledger.sources:
                ledger.add_source(SourceRecord(**source_data))
            if evidence_id not in ledger.evidence:
                ledger.add_evidence(EvidenceRecord(**evidence_data))
        ledger.add_claim(claim)
        status = ledger.reconcile(claim_id)
        if status not in {"VERIFIED_PRIMARY", "VERIFIED_CORROBORATED"}:
            raise ValueError(f"primary support missing: {claim_id}")
        references = []
        for evidence_id in claim.evidence_ids:
            evidence = ledger.evidence[evidence_id]
            source = ledger.sources[evidence.source_id]
            if source.quality not in {SourceQuality.S5_OFFICIAL_PRIMARY, SourceQuality.S6_ORIGINAL_SIGNED_ACT}:
                continue
            if source.health != SourceHealth.HEALTHY:
                raise ValueError(f"source not verified healthy: {evidence_id}")
            if not source.url.startswith("https://"):
                raise ValueError(f"invalid official source URL: {evidence_id}")
            references.append({
                "evidence_id": evidence_id, "source_id": source.source_id,
                "url": source.url, "locator": evidence.locator or "localização não informada",
            })
        if not references:
            raise ValueError(f"healthy primary evidence missing: {claim_id}")
        selected.append({"claim_id": claim_id, "statement": _one_line(claim.statement), "references": references})

    mission = snapshot["mission"]
    lines = [
        "# MINUTA PARA REVISÃO HUMANA — NÃO PROTOCOLADA",
        "",
        f"**Destinatário sugerido:** {_one_line(recipient, 200)}",
        f"**Objeto:** {_one_line(mission['question'])}",
        f"**Escopo:** {_one_line(mission.get('geography') or 'não delimitado')} — {_one_line(mission.get('time_range') or 'não delimitado')}",
        "",
        "## Fatos documentados no escopo",
    ]
    for index, item in enumerate(selected, 1):
        lines.append(f"{index}. {_one_line(item['statement'])} (claim {item['claim_id']}).")
        for ref in item["references"]:
            lines.append(f"   - Evidência {ref['evidence_id']}; fonte {ref['source_id']}; {_one_line(ref['locator'], 200)}; {ref['url']}")
    lines.extend([
        "",
        "## Limitações",
        "Esta é uma minuta gerada a partir de registros previamente classificados no CaseStore. A correspondência material entre documentos e alegações, eventuais contraprovas, regras jurídicas e dados pessoais ainda exigem revisão humana independente.",
        "",
        "## Pedido de verificação",
        "Solicita-se à autoridade destinatária, se competente, que examine os documentos indicados e avalie a pertinência de diligências e providências legais cabíveis, sem presunção de culpa.",
        "",
        "**Estado:** DRAFT_REVIEW_REQUIRED — nenhum envio efetuado.",
    ])
    return {
        "case_id": case_id, "status": "DRAFT_REVIEW_REQUIRED",
        "publication_allowed": False, "human_review_required": True,
        "claims_used": [x["claim_id"] for x in selected],
        "markdown": "\n".join(lines) + "\n",
    }
