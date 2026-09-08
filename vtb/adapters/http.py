from __future__ import annotations

from typing import Any

import requests

from ..models import SourceHealth
from ..source_health import classify_exception, classify_http_status
from .base import AdapterResult, PublicSourceAdapter


class SafeHttpAdapter(PublicSourceAdapter):
    adapter_id = "safe-http"

    def __init__(
        self,
        user_agent: str = "VisaoTinkerBell/8.0 public-records evidence-first",
        timeout: float = 25.0,
    ):
        self.headers = {"User-Agent": user_agent}
        self.timeout = timeout

    def fetch(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> AdapterResult:
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        except requests.RequestException as exc:
            return AdapterResult(False, classify_exception(exc), url=url, error=str(exc))

        health = classify_http_status(response.status_code)
        if not response.ok:
            return AdapterResult(
                False,
                health,
                status_code=response.status_code,
                url=response.url,
                error=response.text[:500],
            )

        if not expect_json:
            return AdapterResult(True, health, data=response.text, status_code=response.status_code, url=response.url)

        try:
            data = response.json()
        except ValueError as exc:
            return AdapterResult(
                False,
                SourceHealth.PARTIAL,
                status_code=response.status_code,
                url=response.url,
                error=f"invalid JSON payload: {exc}",
            )
        return AdapterResult(True, health, data=data, status_code=response.status_code, url=response.url)
