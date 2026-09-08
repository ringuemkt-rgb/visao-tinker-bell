from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import AdapterResult
from .official_http import OfficialHTTPClient


@dataclass(slots=True, frozen=True)
class TSEResource:
    name: str
    url: str
    format: str
    resource_id: str = ""
    description: str = ""


class TSEOpenDataAdapter:
    """Catalog adapter for the TSE open-data portal.

    Uses the CKAN package action exposed by the portal. Resource URLs returned by
    the catalog are preserved rather than guessed. Availability is source-health dependent.
    """

    adapter_id = "tse_open_data"
    DEFAULT_BASE_URL = "https://dadosabertos.tse.jus.br"

    def __init__(self, base_url: str = DEFAULT_BASE_URL, *, timeout: float = 30.0) -> None:
        self.http = OfficialHTTPClient(base_url, timeout=timeout)

    @staticmethod
    def candidates_dataset_id(year: int) -> str:
        if year < 1994 or year > 2100:
            raise ValueError("unexpected election year")
        return f"candidatos-{int(year)}"

    def package_show(self, dataset_id: str) -> AdapterResult:
        return self.http.get_json(
            "api/3/action/package_show",
            params={"id": dataset_id},
            metadata={"operation": "package_show", "source": "TSE Dados Abertos"},
        )

    def candidate_resources(self, year: int) -> AdapterResult:
        raw = self.package_show(self.candidates_dataset_id(year))
        if not raw.ok:
            return raw
        payload: dict[str, Any] = raw.data or {}
        result = payload.get("result", {}) if payload.get("success", True) else {}
        resources = [
            TSEResource(
                name=str(item.get("name", "")),
                url=str(item.get("url", "")),
                format=str(item.get("format", "")),
                resource_id=str(item.get("id", "")),
                description=str(item.get("description", "")),
            )
            for item in result.get("resources", [])
            if item.get("url")
        ]
        raw.data = resources
        raw.metadata["dataset_id"] = self.candidates_dataset_id(year)
        raw.metadata["resource_count"] = len(resources)
        return raw

    def find_candidate_resource(self, year: int, name_contains: str) -> AdapterResult:
        result = self.candidate_resources(year)
        if not result.ok:
            return result
        needle = name_contains.casefold()
        matches = [resource for resource in result.data if needle in resource.name.casefold()]
        result.data = matches
        result.metadata["filter"] = name_contains
        result.metadata["matched_count"] = len(matches)
        return result
