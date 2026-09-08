from __future__ import annotations

from typing import Any

from .base import AdapterResult
from .official_http import OfficialHTTPClient


class PortalTransparenciaAdapter:
    """Read-only adapter for the official Portal da Transparência API.

    The API key is sent only in `chave-api-dados` and is never emitted in metadata.
    """

    adapter_id = "portal_transparencia"
    DEFAULT_BASE_URL = "https://api.portaldatransparencia.gov.br"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self.http = OfficialHTTPClient(base_url, timeout=timeout)

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["chave-api-dados"] = self._api_key
        return headers

    def sanctions(self, registry: str, **params: Any) -> AdapterResult:
        normalized = registry.strip().lower()
        if normalized not in {"ceis", "cnep", "cepim"}:
            raise ValueError("registry must be one of: ceis, cnep, cepim")
        return self.http.get_json(
            f"api-de-dados/{normalized}",
            params={key: value for key, value in params.items() if value is not None},
            headers=self._headers(),
            metadata={"operation": normalized, "source": "Portal da Transparência"},
        )

    def sanction_by_id(self, registry: str, record_id: int | str) -> AdapterResult:
        normalized = registry.strip().lower()
        if normalized not in {"ceis", "cnep", "cepim"}:
            raise ValueError("registry must be one of: ceis, cnep, cepim")
        return self.http.get_json(
            f"api-de-dados/{normalized}/{record_id}",
            headers=self._headers(),
            metadata={"operation": f"{normalized}_by_id", "source": "Portal da Transparência"},
        )
