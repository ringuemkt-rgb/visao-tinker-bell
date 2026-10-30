"""Strict report validation against schema and local, original evidence.

No LLM generated assertion is promoted to evidence by this module.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

MATERIAL_CLASSES = {"FACT", "NEGATIVE_FACT_WITHIN_VERIFIED_SCOPE"}
VALIDATED_SOURCE_QUALITIES = {"S4_OFFICIAL_STRUCTURED", "S5_OFFICIAL_PRIMARY", "S6_ORIGINAL_SIGNED_ACT"}


def _report_schema() -> dict[str, Any]:
    file = Path(__file__).parents[1] / "schemas" / "forensic_report.schema.json"
    return json.loads(file.read_text(encoding="utf-8"))


def validate_report(
    report: dict[str, Any],
    *,
    case_snapshot: dict[str, Any] | None = None,
    artifact_paths: dict[str, str | Path] | None = None,
    human_reviewed: bool = False,
    counterevidence_reviewed: bool = False,
    legal_reviewed: bool = False,
) -> dict[str, Any]:
    """Fail closed for material facts, without pretending to certify document truth."""
    schema = _report_schema()
    violations: set[str] = set()
    for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(report):
        where = ".".join(map(str, error.absolute_path)) or "report"
        violations.add(f"SCHEMA:{where}:{error.validator}")
    if violations:
        return {"valid": False, "status": "QUARANTINED", "issues": sorted(violations),
                "documents_checked": 0, "facts_checked": 0}

    findings = report.get("findings", [])
    all_evidence = {x: row["payload"] for row in (case_snapshot or {}).get("evidence", [])
                    if (x := row.get("evidence_id"))}
    all_sources = {x: row["payload"] for row in (case_snapshot or {}).get("sources", [])
                   if (x := row.get("source_id"))}
    artifacts = artifact_paths or {}
    documents_checked: set[str] = set()
    material_facts = 0

    for finding in findings:
        fid = finding["finding_id"]
        ids = finding["evidence_ids"]
        if len(ids) != len(set(ids)):
            violations.add(f"DUPLICATE_EVIDENCE:{fid}")
        if finding["classification"] in MATERIAL_CLASSES:
            material_facts += 1
            if not ids:
                violations.add(f"FACT_WITHOUT_EVIDENCE:{fid}")
            if not case_snapshot:
                violations.add(f"CASE_EXPORT_MISSING:{fid}")
        for eid in ids:
            ev = all_evidence.get(eid)
            if ev is None:
                violations.add(f"UNRESOLVED_EVIDENCE:{fid}:{eid}")
                continue
            sid = ev.get("source_id")
            source = all_sources.get(sid)
            if source is None:
                violations.add(f"UNRESOLVED_SOURCE:{fid}:{eid}")
                continue
            if finding["classification"] not in MATERIAL_CLASSES:
                continue
            if source.get("health") != "HEALTHY":
                violations.add(f"SOURCE_NOT_HEALTHY:{fid}:{sid}")
            if source.get("quality") not in VALIDATED_SOURCE_QUALITIES:
                violations.add(f"SOURCE_NOT_PRIMARY:{fid}:{sid}")
            if not ev.get("locator") or not ev.get("excerpt"):
                violations.add(f"EVIDENCE_NOT_LOCATED:{fid}:{eid}")
            sha = source.get("sha256")
            original = artifacts.get(sid)
            if not (isinstance(sha, str) and len(sha) == 64 and original):
                violations.add(f"ORIGINAL_NOT_PRESERVED:{fid}:{sid}")
                continue
            try:
                data = Path(original).read_bytes()
            except OSError:
                violations.add(f"ORIGINAL_UNREADABLE:{fid}:{sid}")
                continue
            if hashlib.sha256(data).hexdigest() != sha:
                violations.add(f"ORIGINAL_HASH_MISMATCH:{fid}:{sid}")
                continue
            documents_checked.add(sid)

    for hypothesis in report.get("hypotheses", []):
        for eid in hypothesis.get("pro_evidence_ids", []) + hypothesis.get("contra_evidence_ids", []):
            if eid not in all_evidence:
                violations.add(f"UNRESOLVED_HYPOTHESIS_EVIDENCE:{hypothesis['id']}:{eid}")
    ids = [x["finding_id"] for x in findings]
    if len(ids) != len(set(ids)):
        violations.add("DUPLICATE_FINDING_ID")
    if report.get("publication_status") == "READY_WITH_LIMITATIONS":
        if not human_reviewed:
            violations.add("HUMAN_REVIEW_NOT_RECORDED")
        if not counterevidence_reviewed:
            violations.add("COUNTEREVIDENCE_REVIEW_NOT_RECORDED")
        if not legal_reviewed:
            violations.add("LEGAL_REVIEW_NOT_RECORDED")
        if material_facts == 0:
            violations.add("NO_VERIFIED_MATERIAL_FACT")
    return {
        "valid": not violations,
        "status": "VALIDATED_FOR_REVIEW" if not violations else "QUARANTINED",
        "issues": sorted(violations),
        "documents_checked": len(documents_checked),
        "facts_checked": material_facts,
        "limitation": "SHA-256 establishes byte integrity, not document authorship or truth. "
                      "A verified excerpt and legal interpretation still need independent human review.",
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate report and local evidence without publication")
    parser.add_argument("report", help="JSON forensic report")
    parser.add_argument("--case-export", help="CaseStore export JSON")
    parser.add_argument("--artifact-map", help="JSON mapping source_id to local original filepath")
    parser.add_argument("--human-reviewed", action="store_true")
    parser.add_argument("--counterevidence-reviewed", action="store_true")
    parser.add_argument("--legal-reviewed", action="store_true")
    args = parser.parse_args(argv)
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    case = json.loads(Path(args.case_export).read_text(encoding="utf-8")) if args.case_export else None
    paths = json.loads(Path(args.artifact_map).read_text(encoding="utf-8")) if args.artifact_map else None
    result = validate_report(
        report, case_snapshot=case, artifact_paths=paths,
        human_reviewed=args.human_reviewed, counterevidence_reviewed=args.counterevidence_reviewed,
        legal_reviewed=args.legal_reviewed,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
