from unittest.mock import Mock

from vtb.adapters.tse_open_data import TSEOpenDataAdapter, TSEResource


def _response(payload, status=200):
    response = Mock()
    response.status_code = status
    response.json.return_value = payload
    response.text = ""
    return response


def test_tse_uses_catalog_resource_urls_not_guessed_cdn_paths():
    adapter = TSEOpenDataAdapter()
    payload = {
        "success": True,
        "result": {
            "resources": [
                {"id": "r1", "name": "Bens de candidatos", "format": "CSV", "url": "https://cdn.example/bens.zip"}
            ]
        },
    }
    adapter.http.session.get = Mock(return_value=_response(payload))
    result = adapter.find_candidate_resource(2026, "bens")
    assert result.ok is True
    assert result.data == [TSEResource("Bens de candidatos", "https://cdn.example/bens.zip", "CSV", "r1", "")]
    call = adapter.http.session.get.call_args
    assert call.args[0].endswith("/api/3/action/package_show")
    assert call.kwargs["params"] == {"id": "candidatos-2026"}
