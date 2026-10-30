"""Bounded read-only PNCP supplier-index searches; not evidence of payment or crime."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

SEARCH_URL = "https://pncp.gov.br/api/search/"
DEFAULT_CNPJS = (
    "01.061.616/0001-35",  # Associação Zambiapunga
    "54.304.243/0001-42",  # MEI referenced in previous documentary dossier
    "32.626.977/0001-05",  # JM Produções
)


def normalize_cnpj(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 14:
        raise ValueError("CNPJ must contain 14 digits")
    return digits


def _official_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    if value.startswith("https://pncp.gov.br/"):
        return value
    if value.startswith("/app/"):
        return "https://pncp.gov.br" + value
    return None


def _record(item: dict[str, Any], expected: str) -> dict[str, Any] | None:
    supplier = str(item.get("cnpj_fornecedor") or "")
    if not supplier or normalize_cnpj(supplier) != expected:
        return None
    key = str(item.get("numero_controle_pncp") or item.get("id") or "")
    if not key:
        return None
    return {
        "pncp_id": key,
        "supplier_cnpj": expected,
        "supplier_name_as_published": item.get("nome_fornecedor"),
        "contracting_agency": item.get("orgao_nome"),
        "contracting_agency_cnpj": item.get("orgao_cnpj"),
        "municipality": item.get("municipio_nome"),
        "uf": item.get("uf"),
        "object": item.get("description") or item.get("title"),
        "publication_date": item.get("data_publicacao_pncp"),
        "signature_date": item.get("data_assinatura"),
        "contract_global_value": item.get("valor_global"),
        "pncp_url": _official_url(item.get("item_url")),
        "data_stage": "PUBLISHED_CONTRACT_NOT_PAYMENT",
    }


def scan_supplier(
    cnpj: str,
    *,
    session: requests.Session | None = None,
    max_pages: int = 8,
    page_size: int = 50,
    delay_seconds: float = 0.2,
    timeout_seconds: float = 25,
) -> dict[str, Any]:
    """Query public PNCP search index; never issue a certificate of non-existence.

    The text search endpoint is an index, not a complete financial ledger.
    Network, pagination, or schema errors make coverage explicitly incomplete.
    """
    expected = normalize_cnpj(cnpj)
    if not 1 <= max_pages <= 50 or not 1 <= page_size <= 50:
        raise ValueError("max_pages and page_size must be within 1..50")
    client = session or requests.Session()
    output: dict[str, Any] = {
        "target_cnpj": expected,
        "query_endpoint": SEARCH_URL,
        "query_kind": "PNCP_SEARCH_TEXT_INDEX_NOT_EXHAUSTIVE",
        "health": "UNKNOWN",
        "coverage": "UNVERIFIED",
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "pages_fetched": 0,
        "index_total_reported": None,
        "items_examined": 0,
        "items_without_exact_supplier_cnpj": 0,
        "records": [],
        "errors": [],
        "note": "Contract is not payment; an empty search is not a certificate of no contracts.",
    }
    seen: set[str] = set()
    try:
        for page in range(1, max_pages + 1):
            if page > 1 and delay_seconds:
                time.sleep(delay_seconds)
            response = client.get(
                SEARCH_URL,
                params={
                    "q": expected,
                    "tipos_documento": "contrato",
                    "ordenacao": "-data",
                    "pagina": page,
                    "tam_pagina": page_size,
                    "status": "todos",
                },
                timeout=timeout_seconds,
                headers={"Accept": "application/json", "User-Agent": "VisaoTinkerBell/8.0 public-document-audit"},
            )
            if not 200 <= response.status_code < 300:
                output["health"] = "RATE_LIMITED" if response.status_code == 429 else "UNAVAILABLE"
                output["errors"].append({"page": page, "status_code": response.status_code})
                break
            try:
                data = response.json()
            except ValueError:
                output["health"] = "INVALID_JSON"
                output["errors"].append({"page": page, "kind": "invalid_json"})
                break
            if (
                not isinstance(data, dict)
                or not isinstance(data.get("items"), list)
                or not isinstance(data.get("total"), int)
                or data["total"] < 0
            ):
                output["health"] = "INVALID_SCHEMA"
                output["errors"].append({"page": page, "kind": "unexpected_search_schema"})
                break
            if output["index_total_reported"] is None:
                output["index_total_reported"] = data["total"]
            output["pages_fetched"] += 1
            output["items_examined"] += len(data["items"])
            for item in data["items"]:
                try:
                    record = _record(item, expected) if isinstance(item, dict) else None
                except ValueError:
                    record = None
                if record is None:
                    output["items_without_exact_supplier_cnpj"] += 1
                    continue
                if record["pncp_id"] not in seen:
                    seen.add(record["pncp_id"])
                    output["records"].append(record)
            if not data["items"] and output["items_examined"] < data["total"]:
                output["health"] = "INVALID_PAGINATION"
                output["errors"].append({"page": page, "kind": "empty_page_before_reported_total"})
                break
            if output["items_examined"] >= data["total"]:
                output["coverage"] = "INDEX_QUERY_COMPLETE_NOT_FULL_PNCP"
                output["health"] = "OK"
                break
        else:
            output["coverage"] = "PAGE_CAP_REACHED_INCOMPLETE"
            output["health"] = "PARTIAL"
    except requests.RequestException as exc:
        output["health"] = "NETWORK_ERROR"
        output["errors"].append({"kind": type(exc).__name__})
    if output["health"] != "OK" and output["coverage"] == "UNVERIFIED":
        output["coverage"] = "INCOMPLETE"
    output["records"].sort(key=lambda x: x["pncp_id"])
    for record in output["records"]:
        raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        record["snapshot_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return output


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Auditable PNCP supplier search index snapshot")
    p.add_argument("--cnpj", action="append", dest="cnpjs")
    p.add_argument("--max-pages", type=int, default=8)
    p.add_argument("--output", default="pncp-supplier-watch.json")
    args = p.parse_args(argv)
    try:
        results = [scan_supplier(c, max_pages=args.max_pages) for c in (args.cnpjs or DEFAULT_CNPJS)]
    except ValueError as exc:
        p.error(str(exc))
    output = {
        "schema": "vtb.pncp_supplier_watch.v1",
        "source": SEARCH_URL,
        "method": "Exact supplier CNPJ, bounded index pagination, fail-closed coverage",
        "results": results,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "health": {r["target_cnpj"]: r["health"] for r in results}}))
    return 0 if all(r["health"] == "OK" for r in results) else 2


if __name__ == "__main__":
    sys.exit(main())
