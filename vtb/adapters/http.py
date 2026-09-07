from __future__ import annotations

from typing import Any

import requests

from ..source_health import classify_exception, classify_http_status
from .base import AdapterResult, PublicSourceAdapter


class SafeHttpAdapter(PublicSourceAdapter):
    adapter_id = "safe-http"

    def __init__(self, user_agent: str = "VisaoTinkerBell/8.0 public-records evidence-first", timeout: float = 25.0):
        self.headers = {"User-Agent": user_agent}
        self.timeout = timeout

    def fetch(self, url: str, params: dict[str, Any] | None = None, expect_json: bool = True) -> AdapterResult:
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            health = classify_http_status(response.status_code)
            if not response.ok:
                return AdapterResult(False, health, status_code=response.status_code, url=response.url, error=response.text[:500])
            data = response.json() if expect_json else response.text
            return AdapterResult(True, health, data=data, status_code=response.status_code, url=response.url)
        except Exception as exc:
            return AdapterResult(False, classify_exception(exc), url=url, error=str(exc))
