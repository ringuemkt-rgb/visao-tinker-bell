import json
from pathlib import Path


def test_forensic_report_schema_is_fail_closed():
    path = Path(__file__).parents[1] / "schemas" / "forensic_report.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert "entity_resolution" in schema["required"]
    assert "evidence_gaps" in schema["required"]
    classifications = schema["properties"]["findings"]["items"]["properties"]["classification"]["enum"]
    assert "EVIDENCE_GAP" in classifications
    assert "FACT" in classifications
