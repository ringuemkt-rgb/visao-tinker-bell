from __future__ import annotations

from typing import Any

import requests

from ..models import SourceHealth
from ..source_health import classify_exception, classify_http_status
from .contracts import EntityMatchCandidate, MatchResult


class YenteMatcher:
    """OpenSanctions/Yente enrichment adapter.

    A match is a lead. It never establishes that a local person is a PEP, sanctioned,
    wanted, or otherwise the same entity without independent identity resolution.
    """

    def __init__(
        self,
        base_url: str,
        *,
        dataset: str = "default",
        api_key: str | None = None,
        timeout: float = 30.0,
        threshold: float | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.dataset = dataset
        self.api_key = api_key
        self.timeout = timeout
        self.threshold = threshold

    def match_person(
        self,
        query_id: str,
        name: str,
        *,
        country: str | None = None,
        birth_date: str | None = None,
        id_number: str | None = None,
    ) -> MatchResult:
        properties: dict[str, list[str]] = {"name": [name]}
        if country:
            properties["country"] = [country]
        if birth_date:
            properties["birthDate"] = [birth_date]
        if id_number:
            properties["idNumber"] = [id_number]

        payload = {"queries": {query_id: {"schema": "Person", "properties": properties}}}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        params: dict[str, Any] = {}
        if self.threshold is not None:
            params["threshold"] = self.threshold

        url = f"{self.base_url}/match/{self.dataset}"
        try:
            response = requests.post(url, json=payload, headers=headers, params=params, timeout=self.timeout)
            health = classify_http_status(response.status_code)
            if not 200 <= response.status_code < 300:
                return MatchResult(query_id, health, identifiers_used=properties, error=response.text[:500])
            body = response.json()
        except requests.RequestException as exc:
            return MatchResult(query_id, classify_exception(exc), identifiers_used=properties, error=str(exc))
        except ValueError as exc:
            return MatchResult(query_id, SourceHealth.DEGRADED, identifiers_used=properties, error=f"invalid JSON: {exc}")

        results = body.get("responses", {}).get(query_id, {}).get("results", [])
        candidates: list[EntityMatchCandidate] = []
        for item in results:
            candidate = item.get("entity") if isinstance(item.get("entity"), dict) else item
            properties_out = candidate.get("properties", {}) if isinstance(candidate, dict) else {}
            candidates.append(
                EntityMatchCandidate(
                    candidate_id=str(candidate.get("id") or item.get("id") or ""),
                    score=_extract_score(item),
                    schema=str(candidate.get("schema") or item.get("schema") or "Person"),
                    properties={str(k): [str(v) for v in values] for k, values in properties_out.items()},
                    dataset=self.dataset,
                    source_url=url,
                )
            )
        return MatchResult(query_id, health, candidates, properties, body)


def _extract_score(item: dict[str, Any]) -> float | None:
    for key in ("score", "match", "confidence"):
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None
