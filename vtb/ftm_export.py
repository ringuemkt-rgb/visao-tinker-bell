"""Export FollowTheMoney-compativel. Nao exige o pacote followthemoney.

Schema minimo para Aleph/Yente: Person, Company, Payment, Contract.
Propriedades saem do registro ja resolvido. Isto nao resolve entidade.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA = {
    "pessoa": "Person",
    "empresa": "Company",
    "pagamento": "Payment",
    "contrato": "Contract",
    "sancao": "Sanction",
}


def entity(schema: str, entity_id: str, properties: dict[str, Any]) -> dict[str, Any]:
    clean = {k: _as_list(v) for k, v in properties.items() if v not in (None, "", [], {})}
    return {"id": entity_id, "schema": schema, "properties": clean}


def from_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for person in case.get("pessoas", []):
        out.append(
            entity(
                "Person",
                person["id"],
                {
                    "name": person.get("nome"),
                    "idNumber": person.get("documento"),
                    "notes": person.get("limite"),
                },
            )
        )
    for company in case.get("empresas", []):
        out.append(
            entity(
                "Company",
                company["id"],
                {
                    "name": company.get("nome"),
                    "registrationNumber": company.get("cnpj"),
                    "incorporationDate": company.get("abertura"),
                },
            )
        )
    for payment in case.get("pagamentos", []):
        out.append(
            entity(
                "Payment",
                payment["id"],
                {
                    "payer": payment.get("pagador_id"),
                    "beneficiary": payment.get("beneficiario_id"),
                    "amount": payment.get("valor"),
                    "date": payment.get("data"),
                    "sourceUrl": payment.get("url"),
                },
            )
        )
    for contract in case.get("contratos", []):
        out.append(
            entity(
                "Contract",
                contract["id"],
                {
                    "title": contract.get("objeto"),
                    "contractNumber": contract.get("numero"),
                    "amount": contract.get("valor"),
                    "sourceUrl": contract.get("url"),
                },
            )
        )
    return out


def dump(case: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "followthemoney", "entities": from_case(case)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]
