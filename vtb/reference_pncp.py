"""Reproducible, non-accusatory PNCP case-reference runner.

A contract publication does not establish payment or successful execution.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from .adapters.pncp import PNCPAdapter
from .models import Claim, ClaimStatus, EvidenceRecord, SourceHealth, SourceQuality, SourceRecord
from .runtime import CaseStore

EXAMPLE_ORGANIZATION_CNPJ = "13120613000295"
EXAMPLE_CONTRACT_YEAR = 2026
EXAMPLE_CONTRACT_SEQUENCE = 2
EXPECTED_CONTROL = "13120613000295-2-000002/2026"


def ingest_pncp_reference(
    store: CaseStore,
    case_id: str,
    *,
    adapter: PNCPAdapter | None = None,
    organization_cnpj: str = EXAMPLE_ORGANIZATION_CNPJ,
    year: int = EXAMPLE_CONTRACT_YEAR,
    sequence: int = EXAMPLE_CONTRACT_SEQUENCE,
    expected_control: str = EXPECTED_CONTROL,
) -> dict[str, Any]:
    """Fetch one official contract into a local case. No legal conclusions."""
    store.create_mission(
        case_id, "PNCP reference (contractual stage only)",
        "Is one contract present in PNCP? What financial evidence is missing?",
        "Brazil; example municipality", f"{year}",
    )
    client = adapter or PNCPAdapter()
    result = client.get_contract(organization_cnpj, year, sequence)
    store.log_search(case_id, result.url or "PNCP", source="PNCP",
                     result_class="API_RESPONSE" if result.ok else "UNAVAILABLE",
                     source_health=result.health.value)
    store.log_tool_run(case_id, "pncp.get_contract", "OK" if result.ok else "ERROR",
                       {"cnpj": organization_cnpj, "year": year, "seq": sequence},
                       {"status_code": result.status_code}, result.error or "")
    if not result.ok or not isinstance(result.data, dict):
        return {"case_id": case_id, "coverage": "SOURCE_UNAVAILABLE", "contract_verified": False,
                "issues": [result.error or "invalid/empty API response"]}
    payload = result.data
    if payload.get("numeroControlePNCP") != expected_control:
        return {"case_id": case_id, "coverage": "IDENTIFIER_CONFLICT", "contract_verified": False,
                "issues": ["PNCP control ID mismatch; do not link unrelated records"]}
    sid = f"PNCP-{expected_control}"
    source = SourceRecord(
        source_id=sid, title="PNCP structured contract record",
        issuer="Portal Nacional de Contratações Públicas",
        url=result.url or "https://pncp.gov.br/",
        health=SourceHealth.HEALTHY, quality=SourceQuality.S4_OFFICIAL_STRUCTURED,
        notes="API structured response; original response bytes not preserved in this run; "
              "payment, invoices, acceptance and delivery not verified.",
    )
    store.add_source(case_id, source)
    fields = {
        "numeroControlePNCP": expected_control,
        "numeroContratoEmpenho": payload.get("numeroContratoEmpenho"),
        "dataAssinatura": payload.get("dataAssinatura"),
        "valorInicial": payload.get("valorInicial"),
        "valorGlobal": payload.get("valorGlobal"),
        "orgaoEntidade": (payload.get("orgaoEntidade") or {}).get("razaoSocial")
        if isinstance(payload.get("orgaoEntidade"), dict) else None,
    }
    for name, value in fields.items():
        if value is None:
            continue
        eid = f"E-{name}"
        store.add_evidence(case_id, EvidenceRecord(
            evidence_id=eid, source_id=sid, locator=f"JSON field '{name}'",
            excerpt=f"{name}: {value}",
            notes="PNCP published field; document preservation and reviewer confirmation pending",
        ))
        store.add_claim(case_id, Claim(
            claim_id=f"C-{name}", statement=f"PNCP API reports {name} = {value}.",
            status=ClaimStatus.PARTIALLY_SUPPORTED, evidence_ids=[eid],
            limitations=["Contract metadata only; not payment or work delivered"],
        ))
    return {
        "case_id": case_id, "coverage": "OFFICIAL_STRUCTURED_CONTRACT_ONLY",
        "contract_verified": True, "control_id": expected_control,
        "financial_reconciliation": {
            "contracted_brl": payload.get("valorGlobal"),
            "committed_brl": None,
            "liquidated_brl": None,
            "paid_brl": None,
            "deliveries_verified": None,
        },
        "status": "INCONCLUSIVE_ON_SPENDING_AND_EXECUTION",
        "missing_documents": [
            "signed contract and annexes", "budget commitment",
            "liquidation records", "payment orders", "invoices",
            "service/works delivery and acceptance documents",
        ],
        "caution": "No finding of fraud or corruption; source metadata is not proof of payment.",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Public PNCP read-only reference case")
    p.add_argument("case_id", help="Local case ID")
    p.add_argument("--db", default="data/vtb.sqlite3")
    p.add_argument("--cnpj", default=EXAMPLE_ORGANIZATION_CNPJ)
    p.add_argument("--year", type=int, default=EXAMPLE_CONTRACT_YEAR)
    p.add_argument("--sequence", type=int, default=EXAMPLE_CONTRACT_SEQUENCE)
    p.add_argument("--control", default=EXPECTED_CONTROL)
    args = p.parse_args(argv)
    store = CaseStore(args.db)
    try:
        output = ingest_pncp_reference(
            store, args.case_id, organization_cnpj=args.cnpj,
            year=args.year, sequence=args.sequence, expected_control=args.control,
        )
    finally:
        store.close()
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    return 0 if output["contract_verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
