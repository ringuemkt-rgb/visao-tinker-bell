"""No real-person cases: synthetic documents and claims only."""
import hashlib
from datetime import UTC, datetime

from vtb.report_validator import validate_report


def report(eid="E-1", classification="FACT"):
    return {
        "report_id": "SYN-1",
        "cutoff_at": datetime.now(UTC).isoformat(),
        "scope": {"question": "Was the contract published?", "jurisdiction": "Synthetic"},
        "methodology": ["Read original"],
        "entity_resolution": [],
        "findings": [{
            "finding_id": "F-1", "classification": classification,
            "statement": "The synthetic contract exists.", "evidence_ids": [eid],
            "confidence": "HIGH",
        }],
        "hypotheses": [],
        "evidence_gaps": [],
        "limitations": [],
        "publication_status": "DRAFT",
    }


def snapshot(data):
    digest = hashlib.sha256(data).hexdigest()
    return {
        "sources": [{"source_id": "S-1", "payload": {
            "source_id": "S-1", "quality": "S5_OFFICIAL_PRIMARY",
            "health": "HEALTHY", "sha256": digest,
        }}],
        "evidence": [{"evidence_id": "E-1", "payload": {
            "evidence_id": "E-1", "source_id": "S-1",
            "locator": "line 1", "excerpt": "Synthetic contract",
        }}],
    }


def test_real_bytes_and_source_are_required(tmp_path):
    original = tmp_path / "original.txt"
    original.write_bytes(b"Synthetic contract")
    case = snapshot(original.read_bytes())
    assert validate_report(report(), case_snapshot=case)["valid"] is False
    valid = validate_report(report(), case_snapshot=case,
                            artifact_paths={"S-1": original}, human_reviewed=True)
    assert valid["valid"] is True
    assert valid["documents_checked"] == 1
    assert valid["facts_checked"] == 1
    original.write_bytes(b"Tampered original")
    assert "ORIGINAL_HASH_MISMATCH:F-1:S-1" in validate_report(
        report(), case_snapshot=case, artifact_paths={"S-1": original}
    )["issues"]


def test_fake_source_ids_and_unhealthy_sources_are_rejected(tmp_path):
    file = tmp_path / "src.txt"
    file.write_text("Synthetic contract", encoding="utf8")
    case = snapshot(file.read_bytes())
    assert "UNRESOLVED_EVIDENCE:F-1:NONEXISTENT" in validate_report(
        report("NONEXISTENT"), case_snapshot=case
    )["issues"]
    case["sources"][0]["payload"]["health"] = "BLOCKED"
    assert "SOURCE_NOT_HEALTHY:F-1:S-1" in validate_report(
        report(), case_snapshot=case, artifact_paths={"S-1": file}
    )["issues"]


def test_ready_report_requires_review_and_verified_fact(tmp_path):
    original = tmp_path / "src.txt"
    original.write_bytes(b"Synthetic contract")
    case = snapshot(original.read_bytes())
    sample = report()
    sample["publication_status"] = "READY_WITH_LIMITATIONS"
    result = validate_report(sample, case_snapshot=case, artifact_paths={"S-1": original})
    assert not result["valid"]
    assert "LEGAL_REVIEW_NOT_RECORDED" in result["issues"]
    assert validate_report(sample, case_snapshot=case, artifact_paths={"S-1": original},
                           human_reviewed=True, counterevidence_reviewed=True,
                           legal_reviewed=True)["valid"]


def test_schema_catches_missing_and_unexpected_fields():
    sample = report()
    sample["unknown"] = "not allowed"
    assert any("additionalProperties" in item for item in validate_report(sample)["issues"])
    del sample["unknown"]
    del sample["report_id"]
    assert not validate_report(sample)["valid"]


def test_hypothesis_without_evidence_is_permitted_but_fake_reference_is_not():
    sample = report(classification="HYPOTHESIS")
    sample["findings"][0]["evidence_ids"] = []
    sample["hypotheses"] = [{
        "id": "H-1", "statement": "Could be regular", "status": "UNRESOLVED",
        "pro_evidence_ids": [], "contra_evidence_ids": [],
    }]
    assert validate_report(sample)["valid"]
    sample["hypotheses"][0]["pro_evidence_ids"] = ["E-FAKE"]
    assert "UNRESOLVED_HYPOTHESIS_EVIDENCE:H-1:E-FAKE" in validate_report(sample)["issues"]


def test_excerpt_must_exist_in_actual_text_original(tmp_path):
    original = tmp_path / "source.txt"
    original.write_bytes(b"Synthetic contract")
    case = snapshot(original.read_bytes())
    case["evidence"][0]["payload"]["excerpt"] = "Invented snippet not in file"
    result = validate_report(
        report(), case_snapshot=case, artifact_paths={"S-1": original},
        human_reviewed=True,
    )
    assert "EXCERPT_NOT_IN_ORIGINAL:F-1:E-1" in result["issues"]


def test_material_fact_needs_manual_review_even_in_draft(tmp_path):
    original = tmp_path / "source.txt"
    original.write_bytes(b"Synthetic contract")
    case = snapshot(original.read_bytes())
    result = validate_report(report(), case_snapshot=case,
                             artifact_paths={"S-1": original})
    assert "MATERIAL_FACT_REVIEW_REQUIRED" in result["issues"]


def test_negative_fact_needs_scope_review(tmp_path):
    original = tmp_path / "source.txt"
    original.write_bytes(b"Synthetic contract")
    case = snapshot(original.read_bytes())
    sample = report(classification="NEGATIVE_FACT_WITHIN_VERIFIED_SCOPE")
    result = validate_report(sample, case_snapshot=case,
                             artifact_paths={"S-1": original}, human_reviewed=True)
    assert "NEGATIVE_SCOPE_NOT_VERIFIED:F-1" in result["issues"]
    assert validate_report(sample, case_snapshot=case,
                           artifact_paths={"S-1": original},
                           human_reviewed=True, negative_scope_reviewed=True)["valid"]
