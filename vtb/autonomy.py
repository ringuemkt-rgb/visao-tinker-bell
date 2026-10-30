"""Bounded, read-only public-source mission executor.

This module deliberately cannot upload, publish, accuse, or access arbitrary URLs.
Every network operation must be an explicitly registered public-source adapter.
"""
from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from .adapters.base import AdapterResult
from .adapters.pncp import PNCPAdapter
from .adapters.transparency import PortalTransparenciaAdapter
from .adapters.tse_open_data import TSEOpenDataAdapter
from .models import SourceHealth
from .runtime import CaseStore

MAX_QUERIES = 5
OPERATIONS = frozenset({
    "pncp.contract",
    "pncp.contract_documents",
    "tse.candidate_resources",
    "transparency.sanctions",
})


def _digits(value: Any) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())


def validate_query(query: dict[str, Any]) -> dict[str, Any]:
    """Normalize and restrict query arguments; reject arbitrary endpoints."""
    if not isinstance(query, dict):
        raise TypeError("query must be an object")
    operation = query.get("operation")
    if operation not in OPERATIONS:
        raise ValueError("operation is not allowlisted")
    if operation.startswith("pncp."):
        cnpj = _digits(query.get("cnpj", ""))
        year = query.get("year")
        sequence = query.get("sequence")
        if len(cnpj) != 14 or type(year) is not int or not 2000 <= year <= 2100:
            raise ValueError("valid PNCP CNPJ and year required")
        if type(sequence) is not int or not 1 <= sequence <= 1_000_000:
            raise ValueError("valid PNCP sequence required")
        return {"operation": operation, "cnpj": cnpj, "year": year, "sequence": sequence}
    if operation == "tse.candidate_resources":
        year = query.get("year")
        if type(year) is not int or not 1994 <= year <= 2100:
            raise ValueError("valid election year required")
        return {"operation": operation, "year": year}
    registry = query.get("registry")
    if registry not in {"ceis", "cnep", "cepim"}:
        raise ValueError("sanctions registry must be ceis, cnep, or cepim")
    cnpj = _digits(query.get("cnpj", ""))
    if len(cnpj) != 14:
        raise ValueError("valid CNPJ required")
    page = query.get("page", 1)
    if type(page) is not int or not 1 <= page <= 30:
        raise ValueError("page must be 1..30")
    return {"operation": operation, "registry": registry, "cnpj": cnpj, "page": page}


def build_readonly_plan(case_id: str, queries: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a bounded research plan without running or asserting discoveries."""
    if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 120:
        raise ValueError("case_id must be nonempty and <=120 chars")
    if not isinstance(queries, list) or not 1 <= len(queries) <= MAX_QUERIES:
        raise ValueError("plan must have 1..5 queries")
    normalized = [validate_query(q) for q in queries]
    if len({repr(sorted(q.items())) for q in normalized}) != len(normalized):
        raise ValueError("duplicate queries")
    return {
        "case_id": case_id,
        "queries": normalized,
        "mode": "PUBLIC_READ_ONLY",
        "human_review_required": True,
        "publication_allowed": False,
    }


def _default_handler(query: dict[str, Any]) -> AdapterResult:
    operation = query["operation"]
    if operation == "pncp.contract":
        return PNCPAdapter().get_contract(query["cnpj"], query["year"], query["sequence"])
    if operation == "pncp.contract_documents":
        return PNCPAdapter().contract_documents(query["cnpj"], query["year"], query["sequence"])
    if operation == "tse.candidate_resources":
        return TSEOpenDataAdapter().candidate_resources(query["year"])
    key = os.environ.get("PORTAL_TRANSPARENCIA_KEY") or os.environ.get("PORTAL_API_KEY")
    if not key:
        return AdapterResult(False, SourceHealth.AUTH_REQUIRED, error="Portal API key not configured")
    return PortalTransparenciaAdapter(api_key=key).sanctions(
        query["registry"], codigoSancionado=query["cnpj"], pagina=query["page"]
    )


def _preview(data: Any) -> Any:
    """Limit output size and avoid passing full datasets to an LLM."""
    if isinstance(data, list):
        return [str(item)[:500] for item in data[:5]]
    if isinstance(data, dict):
        return {str(k): str(v)[:300] for k, v in list(data.items())[:15]}
    return str(data)[:1500]


def execute_readonly_plan(
    plan: dict[str, Any],
    *,
    store: CaseStore,
    handler: Callable[[dict[str, Any]], AdapterResult] | None = None,
) -> dict[str, Any]:
    """Execute only allowlisted operations and audit their *actual* outcomes."""
    validated = build_readonly_plan(plan["case_id"], plan["queries"])
    store.mission(validated["case_id"])  # must exist before any external action
    runner = handler or _default_handler
    outputs: list[dict[str, Any]] = []
    for query in validated["queries"]:
        try:
            result = runner(query)
            if not isinstance(result, AdapterResult):
                raise TypeError("adapter must return AdapterResult")
            outcome = {
                "operation": query["operation"],
                "ok": bool(result.ok),
                "source_health": str(result.health),
                "status_code": result.status_code,
                "source_url": result.url,
                "error": str(result.error or "")[:500],
                "preview": _preview(result.data) if result.ok else None,
                "negative_result_not_proof_of_absence": True,
            }
        except Exception as exc:  # noqa: BLE001 - isolate untrusted adapter failure
            outcome = {
                "operation": query["operation"], "ok": False, "source_health": "UNKNOWN",
                "error": f"{type(exc).__name__}: {str(exc)[:250]}",
                "negative_result_not_proof_of_absence": True,
            }
        store.log_tool_run(
            validated["case_id"], query["operation"],
            "SUCCESS" if outcome["ok"] else "FAILED",
            input_data=query,
            output_data={k: v for k, v in outcome.items() if k != "preview"},
        )
        outputs.append(outcome)
    return {
        "case_id": validated["case_id"],
        "results": outputs,
        "completed_queries": len(outputs),
        "human_review_required": True,
        "publication_allowed": False,
    }
