from unittest.mock import Mock

from vtb.adapters.transparency import PortalTransparenciaAdapter


def _response(payload, status=200):
    response = Mock()
    response.status_code = status
    response.json.return_value = payload
    response.text = ""
    return response


def test_ceis_uses_official_path_and_keeps_secret_out_of_metadata():
    adapter = PortalTransparenciaAdapter("super-secret")
    adapter.http.session.get = Mock(return_value=_response([]))
    result = adapter.sanctions("ceis", pagina=1, codigoSancionado="123")
    call = adapter.http.session.get.call_args
    assert call.args[0].endswith("/api-de-dados/ceis")
    assert call.kwargs["headers"]["chave-api-dados"] == "super-secret"
    assert "super-secret" not in repr(result.metadata)
    assert result.metadata["operation"] == "ceis"


def test_registry_is_allowlisted():
    adapter = PortalTransparenciaAdapter()
    try:
        adapter.sanctions("unknown")
    except ValueError as exc:
        assert "ceis" in str(exc)
    else:
        raise AssertionError("expected ValueError")
