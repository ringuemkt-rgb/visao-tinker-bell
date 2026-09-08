from vtb.preservation import preserve_bytes, sha256_bytes, sha256_file, write_manifest


def test_preservation_manifest_roundtrip(tmp_path):
    payload = b"public record snapshot"
    target = tmp_path / "snapshot.bin"
    manifest = preserve_bytes(payload, target, "A1", "https://example.test")
    assert manifest.sha256 == sha256_bytes(payload)
    assert manifest.sha256 == sha256_file(target)
    out = tmp_path / "manifest.json"
    write_manifest(manifest, out)
    assert '"artifact_id": "A1"' in out.read_text(encoding="utf-8")
