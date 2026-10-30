from unittest.mock import Mock

from vtb.adapters.base import AdapterResult
from vtb.models import SourceHealth
from vtb.reference_pncp import EXPECTED_CONTROL, ingest_pncp_reference
from vtb.runtime import CaseStore


def test_real_contract_schema_replay_without_financial_claim(tmp_path):
    store = CaseStore(tmp_path / "case.db")
    mock = Mock()
    mock.get_contract.return_value = AdapterResult(
        True, SourceHealth.HEALTHY, status_code=200,
        url="https://pncp.gov.br/api/pncp/v1/orgaos/13120613000295/contratos/2026/2",
        data={
            "numeroControlePNCP": EXPECTED_CONTROL,
            "numeroContratoEmpenho": "001",
            "dataAssinatura": "2026-01-05",
            "valorInicial": 18000,
            "valorGlobal": 18000,
            "orgaoEntidade": {"razaoSocial": "MUNICIPIO DE LARANJEIRAS"},
        },
    )
    result = ingest_pncp_reference(store, "SYN-CASE", adapter=mock)
    case = store.export_case("SYN-CASE")
    store.close()
    assert result["contract_verified"] is True
    assert result["financial_reconciliation"]["paid_brl"] is None
    assert result["status"] == "INCONCLUSIVE_ON_SPENDING_AND_EXECUTION"
    assert len(case["sources"]) == 1
    assert len(case["claims"]) >= 4
    assert all(row["payload"]["status"] == "PARTIALLY_SUPPORTED" for row in case["claims"])
    assert len(case["tool_runs"]) == 1


def test_contract_id_mismatch_does_not_attach_another_entity(tmp_path):
    store = CaseStore(tmp_path / "case.db")
    mock = Mock()
    mock.get_contract.return_value = AdapterResult(
        True, SourceHealth.HEALTHY, data={"numeroControlePNCP": "different"},
    )
    result = ingest_pncp_reference(store, "DIFFERENT", adapter=mock)
    assert result["coverage"] == "IDENTIFIER_CONFLICT"
    assert store.export_case("DIFFERENT")["sources"] == []
    store.close()


def test_http_failure_not_classified_as_no_contract(tmp_path):
    store = CaseStore(tmp_path / "case.db")
    mock = Mock()
    mock.get_contract.return_value = AdapterResult(
        False, SourceHealth.BLOCKED, status_code=403, error="Forbidden",
    )
    result = ingest_pncp_reference(store, "BLOCKED", adapter=mock)
    assert result["coverage"] == "SOURCE_UNAVAILABLE"
    assert result["contract_verified"] is False
    assert store.export_case("BLOCKED")["searches"][0]["source_health"] == "BLOCKED"
    store.close()
