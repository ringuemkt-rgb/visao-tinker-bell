from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests

from ..models import SourceHealth
from ..source_health import classify_exception, classify_http_status
from .base import AdapterResult


class OfficialHTTPClient:
    """Small read-only HTTP client with VTB source-health semantics.

    Sensitive headers are deliberately excluded from AdapterResult metadata.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = session or requests.Session()

    def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AdapterResult:
        url = urljoin(self.base_url, path.lstrip("/"))
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            health = classify_http_status(response.status_code)
            safe_metadata = dict(metadata or {})
            safe_metadata["query_parameters"] = dict(params or {})
            if not 200 <= response.status_code < 300:
                return AdapterResult(
                    False,
                    health,
                    status_code=response.status_code,
                    url=url,
                    error=response.text[:500],
                    metadata=safe_metadata,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                return AdapterResult(
                    False,
                    SourceHealth.DEGRADED,
                    status_code=response.status_code,
                    url=url,
                    error=f"invalid JSON: {exc}",
                    metadata=safe_metadata,
                )
            return AdapterResult(
                True,
                health,
                data=payload,
                status_code=response.status_code,
                url=url,
                metadata=safe_metadata,
            )
        except requests.RequestException as exc:
            return AdapterResult(
                False,
                classify_exception(exc),
                url=url,
                error=str(exc),
                metadata={"query_parameters": dict(params or {}), **dict(metadata or {})},
            )
