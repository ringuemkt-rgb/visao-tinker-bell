from unittest.mock import Mock

from vtb.adapters.pncp import PNCPAdapter
from vtb.models import SourceHealth


def _response(payload, status=200):
    response = Mock()
    response.status_code = status
    response.json.return_value = payload
    response.text = ""
    return response


def test_pncp_contract_uses_documented_path():
    adapter = PNCPAdapter()
    adapter.http.session.get = Mock(return_value=_response({"numeroControlePNCP": "x"}))
    result = adapter.get_contract("00.394.460/0001-41", 2021, 1)
    assert result.ok is True
    url = adapter.http.session.get.call_args.args[0]
    assert url.endswith("/v1/orgaos/00394460000141/contratos/2021/1")


def test_pncp_degraded_does_not_become_not_found():
    adapter = PNCPAdapter()
    adapter.http.session.get = Mock(return_value=_response({}, status=500))
    result = adapter.get_contract("00394460000141", 2021, 1)
    assert result.ok is False
    assert result.health == SourceHealth.DEGRADED
