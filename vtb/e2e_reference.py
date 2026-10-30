"""One-command safe reference: PNCP fetch → CaseStore → JSON report → validation → HTML.

All outputs are local. No public accusations and no false statement of payment.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .adapters.pncp import PNCPAdapter
from .case_dashboard import render_dashboard
from .reference_pncp import ingest_pncp_reference
from .report_validator import validate_report
from .runtime import CaseStore


def _write(path: Path, item: Any) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(item, handle, ensure_ascii=False, indent=2, default=str)
        handle.write("\n")


def run_public_reference(
    case_id: str,
    output_dir: str | Path,
    *,
    adapter: PNCPAdapter | None = None,
) -> dict[str, Any]:
    """Create a real-source workflow; do not overstate the final verification."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / "case.sqlite3"
    store = CaseStore(database)
    try:
        finding = ingest_pncp_reference(store, case_id, adapter=adapter)
        snapshot = store.export_case(case_id)
    finally:
        store.close()
    source_ids = [entry["source_id"] for entry in snapshot["sources"]]
    evidence_ids = [entry["evidence_id"] for entry in snapshot["evidence"]]
    report = {
        "report_id": case_id,
        "cutoff_at": datetime.now(UTC).isoformat(),
        "scope": {
            "question": "What official contract metadata can be reproduced? What is not known?",
            "jurisdiction": "Public PNCP example only",
            "time_range": "2026",
        },
        "methodology": [
            "Query PNCP public contract detail endpoint",
            "Preserve source ID and exact control number in the local SQLite CaseStore",
            "Do not infer financial stages from contract metadata",
        ],
        "entity_resolution": [],
        "findings": [{
            "finding_id": "F-PUBLISHED-METADATA",
            "classification": "PARTIALLY_SUPPORTED" if source_ids else "EVIDENCE_GAP",
            "statement": "The PNCP API reported contract metadata; payment and delivery are not demonstrated."
                         if source_ids else "PNCP source could not be verified in this execution.",
            "evidence_ids": evidence_ids,
            "confidence": "MEDIUM" if source_ids else "LOW",
            "limitations": ["Original HTTP response bytes not preserved; no primary payment records"],
        }],
        "hypotheses": [
            {"id": "H-REGULAR", "statement": "Public contract may have been lawfully executed.",
             "status": "UNRESOLVED", "pro_evidence_ids": [], "contra_evidence_ids": []},
            {"id": "H-MISSING", "statement": "Some missing financial stages may only reflect source coverage.",
             "status": "UNRESOLVED", "pro_evidence_ids": [], "contra_evidence_ids": []},
        ],
        "evidence_gaps": [{
            "description": description,
            "source_needed": "contracting body's original financial and performance documents",
            "impact": "Insufficient to verify actual spending or delivery",
        } for description in finding.get("missing_documents", ["official contract detail"])],
        "limitations": [
            "No signed original, complete payment trail or execution audit was obtained",
            "Published value is NOT amount paid or misappropriated",
            "No wrongdoing is attributed to a person or institution",
        ],
        "publication_status": "INCONCLUSIVE",
    }
    validation = validate_report(report, case_snapshot=snapshot)
    paths = {
        "case": directory / "case-export.json",
        "report": directory / "forensic-report.json",
        "validation": directory / "validation.json",
        "dashboard": directory / "index.html",
        "source_summary": directory / "source-summary.json",
    }
    _write(paths["case"], snapshot)
    _write(paths["report"], report)
    _write(paths["validation"], validation)
    _write(paths["source_summary"], finding)
    with paths["dashboard"].open("x", encoding="utf-8") as handle:
        handle.write(render_dashboard(snapshot, validation=validation))
    return {
        "status": "INCONCLUSIVE" if validation["valid"] else "QUARANTINED",
        "source_coverage": finding["coverage"],
        "validation": validation,
        "output_files": {key: str(path) for key, path in paths.items()},
        "not_a_fraud_finding": True,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Audit-safe PNCP reference end-to-end smoke")
    p.add_argument("case_id")
    p.add_argument("--output-dir", required=True)
    args = p.parse_args(argv)
    result = run_public_reference(args.case_id, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "INCONCLUSIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
