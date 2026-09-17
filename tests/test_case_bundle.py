import json

from vtb.case_bundle import verify_case_bundle, write_case_bundle
from vtb.runtime import CaseStore


def test_case_bundle_roundtrip_and_tamper_detection(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite3")
    store.create_mission("CASE-BUNDLE", "Bundle", "Pergunta")
    bundle = write_case_bundle(store, "CASE-BUNDLE", tmp_path / "bundles")
    assert (bundle / "case.json").exists()
    assert verify_case_bundle(bundle) == (True, [])
    case_file = bundle / "case.json"
    case_file.write_text(case_file.read_text(encoding="utf-8") + "tampered", encoding="utf-8")
    valid, reasons = verify_case_bundle(bundle)
    assert not valid
    assert any("SHA256_MISMATCH:case.json" == reason for reason in reasons)
    store.close()


def test_case_bundle_manifest_is_structured(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite3")
    store.create_mission("CASE-MANIFEST", "Manifest", "Pergunta")
    bundle = write_case_bundle(store, "CASE-MANIFEST", tmp_path / "bundles")
    manifest = json.loads((bundle / "bundle-manifest.json").read_text(encoding="utf-8"))
    assert manifest["format"] == "vtb-case-bundle-v1"
    assert manifest["files"][0]["path"] == "case.json"
    store.close()
