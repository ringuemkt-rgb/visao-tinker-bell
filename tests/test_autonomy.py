import pytest

from vtb.adapters.base import AdapterResult
from vtb.autonomy import build_readonly_plan, execute_readonly_plan, validate_query
from vtb.models import SourceHealth
from vtb.runtime import CaseStore


def test_no_arbitrary_network_operations():
    with pytest.raises(ValueError, match="allowlisted"):
        validate_query({"operation": "http.get", "url": "https://example.com"})


def test_plan_rejects_invalid_inputs_and_unbounded_queries():
    with pytest.raises(ValueError):
        build_readonly_plan("x", [{"operation": "tse.candidate_resources", "year": 2026}] * 6)
    with pytest.raises(ValueError):
        validate_query({"operation": "pncp.contract", "cnpj": "abc", "year": 2025, "sequence": 1})
    with pytest.raises(ValueError):
        validate_query({"operation": "tse.candidate_resources", "year": "2026"})


def test_readonly_execution_is_audited_and_fails_closed(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite")
    store.create_mission("C1", "Test", "Document the question")
    plan = build_readonly_plan("C1", [{"operation": "tse.candidate_resources", "year": 2026}])
    calls = []
    def handler(query):
        calls.append(query)
        return AdapterResult(False, SourceHealth.TIMEOUT, error="network timeout")
    result = execute_readonly_plan(plan, store=store, handler=handler)
    assert len(calls) == 1
    assert result["publication_allowed"] is False
    assert result["results"][0]["source_health"] == "TIMEOUT"
    assert store.export_case("C1")["tool_runs"][0]["status"] == "FAILED"
    store.close()


def test_only_existing_cases_can_run(tmp_path):
    store = CaseStore(tmp_path / "case.sqlite")
    plan = build_readonly_plan("missing", [{"operation": "tse.candidate_resources", "year": 2026}])
    with pytest.raises(KeyError):
        execute_readonly_plan(plan, store=store, handler=lambda q: None)
    store.close()


def test_sanctions_registry_and_page_are_validated():
    assert validate_query({"operation": "transparency.sanctions", "registry": "ceis", "cnpj": "12.345.678/0001-99"})["cnpj"] == "12345678000199"
    with pytest.raises(ValueError):
        validate_query({"operation": "transparency.sanctions", "registry": "private", "cnpj": "12345678000199"})
