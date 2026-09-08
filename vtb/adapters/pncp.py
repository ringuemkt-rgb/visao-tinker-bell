from __future__ import annotations

from .base import AdapterResult
from .cnpj_snapshot import normalize_cnpj
from .official_http import OfficialHTTPClient


class PNCPAdapter:
    """Read-only adapter for documented PNCP integration consultation endpoints."""

    adapter_id = "pncp"
    DEFAULT_BASE_URL = "https://pncp.gov.br/api/pncp"

    def __init__(self, base_url: str = DEFAULT_BASE_URL, *, timeout: float = 30.0) -> None:
        self.http = OfficialHTTPClient(base_url, timeout=timeout)

    @staticmethod
    def _path_cnpj(cnpj: str) -> str:
        return normalize_cnpj(cnpj)

    def get_contract(self, cnpj: str, year: int, sequence: int) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/contratos/{int(year)}/{int(sequence)}",
            metadata={"operation": "contract", "source": "PNCP"},
        )

    def contract_documents(self, cnpj: str, year: int, sequence: int) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/contratos/{int(year)}/{int(sequence)}/arquivos",
            metadata={"operation": "contract_documents", "source": "PNCP"},
        )

    def contracts_for_procurement(
        self,
        cnpj: str,
        procurement_year: int,
        procurement_sequence: int,
    ) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/contratos/contratacao/{int(procurement_year)}/{int(procurement_sequence)}",
            metadata={"operation": "contracts_for_procurement", "source": "PNCP"},
        )

    def procurement_items(self, cnpj: str, year: int, sequence: int) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/compras/{int(year)}/{int(sequence)}/itens",
            metadata={"operation": "procurement_items", "source": "PNCP"},
        )

    def procurement_history(self, cnpj: str, year: int, sequence: int) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/compras/{int(year)}/{int(sequence)}/historico",
            metadata={"operation": "procurement_history", "source": "PNCP"},
        )

    def contract_history(self, cnpj: str, year: int, sequence: int) -> AdapterResult:
        cnpj = self._path_cnpj(cnpj)
        return self.http.get_json(
            f"v1/orgaos/{cnpj}/contratos/{int(year)}/{int(sequence)}/historico",
            metadata={"operation": "contract_history", "source": "PNCP"},
        )
