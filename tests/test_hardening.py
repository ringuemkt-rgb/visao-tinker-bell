import json

import pytest

from vtb.models import EvidenceRecord, MissionState, SourceQuality, SourceRecord
from vtb.preservation import preserve_bytes, verify_manifest
from vtb.runtime import CaseStore


def test_state_transition_is_enforced_and_audited(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite3")
    store.create_mission("CASE-1", "Teste", "Pergunta")
    with pytest.raises(ValueError, match="invalid mission transition"):
        store.set_state("CASE-1", MissionState.READY)
    store.set_state("CASE-1", MissionState.SCOPE)
    events = store.audit_events("CASE-1")
    assert events[-1]["event_type"] == "MISSION_STATE_CHANGED"
    store.close()


def test_evidence_requires_existing_source_and_export_is_replayable(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite3")
    store.create_mission("CASE-2", "Teste", "Pergunta")
    source = SourceRecord("SRC-1", "Fonte", "Órgão", "https://example.test", SourceQuality.S5_OFFICIAL_PRIMARY)
    store.add_source("CASE-2", source)
    store.add_evidence("CASE-2", EvidenceRecord("E-1", "SRC-1", "trecho"))
    snapshot_path = store.write_case_export("CASE-2", tmp_path / "export.json")
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["evidence"][0]["evidence_id"] == "E-1"
    assert snapshot["audit_events"]
    store.close()


def test_manifest_verification_detects_tampering(tmp_path):
    target = tmp_path / "artifact.bin"
    manifest = preserve_bytes(b"original", target, "A-1", "https://example.test")
    assert verify_manifest(manifest) == (True, [])
    target.write_bytes(b"tampered")
    valid, reasons = verify_manifest(manifest)
    assert not valid
    assert "SHA256_MISMATCH" in reasons
