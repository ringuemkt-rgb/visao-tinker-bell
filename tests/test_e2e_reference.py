import json
from pathlib import Path
from unittest.mock import Mock

from vtb.adapters.base import AdapterResult
from vtb.e2e_reference import run_public_reference
from vtb.models import SourceHealth
from vtb.reference_pncp import EXPECTED_CONTROL


def test_reference_generates_structured_case_report_and_private_dashboard(tmp_path):
    adapter = Mock()
    adapter.get_contract.return_value = AdapterResult(
        True, SourceHealth.HEALTHY, status_code=200,
        url="https://pncp.gov.br/api/pncp/v1/orgaos/13120613000295/contratos/2026/2",
        data={
            "numeroControlePNCP": EXPECTED_CONTROL, "valorGlobal": 18000,
            "dataAssinatura": "2026-01-05",
            "orgaoEntidade": {"razaoSocial": "MUNICIPIO DE LARANJEIRAS"},
        },
    )
    result = run_public_reference("SYN-E2E", tmp_path / "audit", adapter=adapter)
    assert result["status"] == "INCONCLUSIVE"
    assert result["validation"]["valid"] is True
    paths = result["output_files"]
    report = json.loads(Path(paths["report"]).read_text(encoding="utf8"))
    assert report["publication_status"] == "INCONCLUSIVE"
    assert report["findings"][0]["classification"] == "PARTIALLY_SUPPORTED"
    assert report["evidence_gaps"]
    assert "NÃO VALIDADO" not in Path(paths["dashboard"]).read_text(encoding="utf8")
    assert "<html" in Path(paths["dashboard"]).read_text(encoding="utf8")


def test_reference_source_failure_does_not_fabricate_contract(tmp_path):
    adapter = Mock()
    adapter.get_contract.return_value = AdapterResult(False, SourceHealth.BLOCKED, error="blocked")
    result = run_public_reference("SYN-FAIL", tmp_path / "fail", adapter=adapter)
    assert result["status"] == "INCONCLUSIVE"
    source = json.loads(Path(result["output_files"]["source_summary"]).read_text(encoding="utf8"))
    assert source["contract_verified"] is False
    assert source["coverage"] == "SOURCE_UNAVAILABLE"
