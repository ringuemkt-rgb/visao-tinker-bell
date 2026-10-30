"""Regression tests for PNCP supplier watcher; all records synthetic."""
import json
from unittest.mock import Mock

from vtb.pncp_watch import _official_url, main, scan_supplier

CNPJ = "01061616000135"


def _item(cnpj, ident="2026-A"):
    return {
        "numero_controle_pncp": ident,
        "cnpj_fornecedor": cnpj,
        "nome_fornecedor": "Fornecedor Teste",
        "orgao_nome": "Órgão Teste",
        "valor_global": 18000.0,
        "item_url": "https://pncp.gov.br/app/contratos/123",
    }


def _response(items, total, status=200):
    r = Mock()
    r.status_code = status
    r.json.return_value = {"items": items, "total": total}
    return r


def test_exact_cnpj_without_false_matches():
    session = Mock()
    session.get.return_value = _response(
        [_item(CNPJ), _item("54304243000142", "2026-B"), {"title": CNPJ}], 3
    )
    result = scan_supplier("01.061.616/0001-35", session=session, delay_seconds=0)
    assert result["health"] == "OK"
    assert result["coverage"] == "INDEX_QUERY_COMPLETE_NOT_FULL_PNCP"
    assert len(result["records"]) == 1
    assert result["records"][0]["supplier_cnpj"] == CNPJ
    assert result["items_without_exact_supplier_cnpj"] == 2
    assert len(result["records"][0]["snapshot_sha256"]) == 64
    assert session.get.call_args.kwargs["params"]["q"] == CNPJ


def test_pagination_deduplicates_contract_ids():
    session = Mock()
    session.get.side_effect = [
        _response([_item(CNPJ, "A")], 2),
        _response([_item(CNPJ, "A"), _item(CNPJ, "B")], 2),
    ]
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "OK"
    assert len(result["records"]) == 2
    assert result["pages_fetched"] == 2


def test_non_200_is_not_absence():
    session = Mock()
    session.get.return_value = _response([], 0, status=503)
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "UNAVAILABLE"
    assert result["coverage"] == "INCOMPLETE"
    assert result["errors"] == [{"page": 1, "status_code": 503}]


def test_page_cap_is_incomplete():
    session = Mock()
    session.get.return_value = _response([{"title": CNPJ}], 100)
    result = scan_supplier(CNPJ, session=session, max_pages=1, delay_seconds=0)
    assert result["health"] == "PARTIAL"
    assert result["coverage"] == "PAGE_CAP_REACHED_INCOMPLETE"


def test_zero_index_hits_not_no_contract_certification():
    session = Mock()
    session.get.return_value = _response([], 0)
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "OK"
    assert "NOT_FULL_PNCP" in result["coverage"]
    assert "not payment" in result["note"]


def test_broken_schema_is_incomplete():
    session = Mock()
    response = Mock(status_code=200)
    response.json.return_value = []
    session.get.return_value = response
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "INVALID_SCHEMA"
    assert result["coverage"] == "INCOMPLETE"


def test_empty_page_before_reported_total_is_incomplete():
    session = Mock()
    session.get.side_effect = [
        _response([_item(CNPJ)], 200),
        _response([], 200),
    ]
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "INVALID_PAGINATION"
    assert result["coverage"] == "INCOMPLETE"


def test_only_pncp_urls_are_recorded():
    assert _official_url("https://other.example/hello") is None
    assert _official_url("/app/contratos/123") == "https://pncp.gov.br/app/contratos/123"


def test_cli_preserves_failure_output_and_exits_nonzero(tmp_path, monkeypatch):
    def fake_scan(cnpj, *, max_pages):
        return {"target_cnpj": cnpj, "health": "UNAVAILABLE", "records": [], "errors": []}
    monkeypatch.setattr("vtb.pncp_watch.scan_supplier", fake_scan)
    output = tmp_path / "report.json"
    assert main(["--cnpj", CNPJ, "--output", str(output)]) == 2
    assert json.loads(output.read_text(encoding="utf8"))["results"][0]["health"] == "UNAVAILABLE"


def test_live_index_schema_supplier_ni():
    session = Mock()
    session.get.return_value = _response(
        [{
            "fornecedor_ni": CNPJ,
            "fornecedor_nome": "GRUPO FOLCLORICO CULTURAL ZAMBIAPUNGA",
            "numero_controle_pncp": "13120613000295-2-000002/2026",
            "orgao_nome": "MUNICIPIO DE LARANJEIRAS",
            "item_url": "/contratos/13120613000295/2026/2",
            "valor_global": 18000,
        }], 1
    )
    result = scan_supplier(CNPJ, session=session, delay_seconds=0)
    assert result["health"] == "OK"
    assert len(result["records"]) == 1
    assert result["records"][0]["contract_global_value"] == 18000
    assert result["records"][0]["pncp_url"] == (
        "https://pncp.gov.br/contratos/13120613000295/2026/2"
    )
