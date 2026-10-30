"""Rosie-inspired, evidence-first screening of PUBLIC expense records.

Original adaptation for Tinker Bell; architectural inspiration:
https://github.com/okfn-brasil/serenata-de-amor (MIT, 2017 Data Science Brigade).

Not a copy of historical classifiers. Output is an audit *lead*, not proof of
corruption, misuse, travel, individual liability, or payment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import median
from typing import Any

from .signals import RiskSignal, SignalCategory, SignalSeverity, triage_band

NONCOMPLIANT_STATUSES = frozenset({"BAIXADA", "NULA", "SUSPENSA", "INAPTA"})


def _date(value: str | date) -> date:
    return value if isinstance(value, date) else date.fromisoformat(value)


def _money(value: str | float | Decimal) -> Decimal:
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid monetary value") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("amount must be finite and nonnegative")
    return result


def _cnpj_valid(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def check(weights: list[int]) -> int:
        remainder = sum(int(digits[i]) * w for i, w in enumerate(weights)) % 11
        return 0 if remainder < 2 else 11 - remainder

    return (
        int(digits[12]) == check([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        and int(digits[13]) == check([6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    )


@dataclass(frozen=True, slots=True)
class PublicExpense:
    expense_id: str
    actor_id: str
    issue_date: date
    amount_brl: Decimal
    evidence_ids: tuple[str, ...]
    category: str = ""
    supplier_cnpj: str | None = None
    supplier_status: str | None = None
    supplier_status_from: date | None = None
    supplier_status_evidence_ids: tuple[str, ...] = ()
    supplier_legal_nature: str | None = None
    subquota: str | None = None
    peer_group: str | None = None
    invoice_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    personal_presence_evidenced: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PublicExpense:
        mandatory = ("expense_id", "actor_id", "issue_date", "amount_brl", "evidence_ids")
        if any(key not in raw for key in mandatory):
            raise ValueError("missing required expense field")
        if not isinstance(raw["evidence_ids"], list) or not raw["evidence_ids"]:
            raise ValueError("each expense needs at least one existing evidence ID")
        if any(not isinstance(x, str) or not x.strip() for x in raw["evidence_ids"]):
            raise ValueError("evidence IDs must be nonempty strings")
        if not str(raw["expense_id"]).strip() or not str(raw["actor_id"]).strip():
            raise ValueError("expense_id and actor_id must be nonempty")
        lat = raw.get("latitude")
        lon = raw.get("longitude")
        if lat is not None or lon is not None:
            if lat is None or lon is None:
                raise ValueError("coordinates must contain latitude and longitude together")
            lat, lon = float(lat), float(lon)
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("invalid geographic coordinates")
        return cls(
            expense_id=str(raw["expense_id"]),
            actor_id=str(raw["actor_id"]),
            issue_date=_date(raw["issue_date"]),
            amount_brl=_money(raw["amount_brl"]),
            evidence_ids=tuple(raw["evidence_ids"]),
            category=str(raw.get("category") or ""),
            supplier_cnpj=str(raw["supplier_cnpj"]) if raw.get("supplier_cnpj") else None,
            supplier_status=str(raw["supplier_status"]).strip().upper() if raw.get("supplier_status") else None,
            supplier_status_from=_date(raw["supplier_status_from"]) if raw.get("supplier_status_from") else None,
            supplier_status_evidence_ids=tuple(raw.get("supplier_status_evidence_ids") or []),
            supplier_legal_nature=str(raw["supplier_legal_nature"]) if raw.get("supplier_legal_nature") else None,
            subquota=str(raw["subquota"]) if raw.get("subquota") is not None else None,
            peer_group=str(raw["peer_group"]) if raw.get("peer_group") else None,
            invoice_id=str(raw["invoice_id"]) if raw.get("invoice_id") else None,
            latitude=lat,
            longitude=lon,
            personal_presence_evidenced=bool(raw.get("personal_presence_evidenced", False)),
        )


@dataclass(frozen=True, slots=True)
class QuotaPolicy:
    category: str
    limit_brl: Decimal
    valid_from: date
    valid_to: date
    evidence_ids: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> QuotaPolicy:
        ids = tuple(raw.get("evidence_ids") or [])
        if not ids:
            raise ValueError("quota policy needs evidence for authoritative limit")
        first, last = _date(raw["valid_from"]), _date(raw["valid_to"])
        if first > last:
            raise ValueError("invalid policy validity range")
        return cls(str(raw["category"]), _money(raw["limit_brl"]), first, last, ids)


def _signal(code: str, title: str, explanation: str, ids: set[str], *,
            category: SignalCategory, severity: SignalSeverity,
            method: str, threshold: dict[str, Any],
            alternatives: list[str], entities: list[str] | None = None) -> RiskSignal:
    return RiskSignal(
        signal_id=code, category=category, title=title, description=explanation,
        severity=severity, entity_ids=entities or [],
        evidence_ids=sorted(ids), method=method, threshold=threshold,
        false_positive_risk="high", alternative_explanations=alternatives,
        legal_validation_required=True, status="ANOMALY_FOR_VERIFICATION",
    )


def _distance_km(a: PublicExpense, b: PublicExpense) -> float:
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    dlat = lat2 - lat1
    dlon = math.radians(b.longitude - a.longitude)
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(hav)))


def input_fingerprint(expenses: list[PublicExpense]) -> str:
    """Hash of the local parsed records, not provenance of official originals."""
    payload = [asdict(expense) for expense in expenses]
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def screen_expenses(
    expenses: list[PublicExpense],
    *,
    quota_policies: list[QuotaPolicy] | None = None,
    min_peer_size: int = 10,
    peer_multiplier: Decimal = Decimal(3),
    distance_review_km: float = 600.0,
) -> dict[str, Any]:
    """Apply six explainable screens with failure-closed applicability gates."""
    if min_peer_size < 6 or peer_multiplier <= 1 or distance_review_km <= 0:
        raise ValueError("invalid screening parameters")
    expense_ids = [e.expense_id for e in expenses]
    if len(set(expense_ids)) != len(expense_ids):
        raise ValueError("duplicate expense IDs: deduplicate provenance before analysis")

    findings: list[RiskSignal] = []
    evaluated = defaultdict(int)
    skipped = defaultdict(int)
    rows_by_month: dict[tuple[str, int, int, str], list[PublicExpense]] = defaultdict(list)
    rows_by_peer: dict[str, list[PublicExpense]] = defaultdict(list)
    rows_by_invoice: dict[tuple[str, str], list[PublicExpense]] = defaultdict(list)
    rows_by_actor_day: dict[tuple[str, date], list[PublicExpense]] = defaultdict(list)

    for row in expenses:
        if row.supplier_cnpj is None:
            skipped["supplier_identifier"] += 1
        else:
            evaluated["supplier_identifier"] += 1
            if not _cnpj_valid(row.supplier_cnpj):
                findings.append(_signal(
                    f"ROSIE-ID-{row.expense_id}", "Identificador de fornecedor inconsistente",
                    "O identificador fornecido não passou no dígito verificador de CNPJ; pode ser erro de digitação.",
                    set(row.evidence_ids), category=SignalCategory.DOCUMENT, severity=SignalSeverity.LOW,
                    method="cálculo verificável dos dois dígitos do CNPJ",
                    threshold={"cnpj_checksum": "invalid"},
                    alternatives=["erro de entrada", "fonte com digitação incorreta"],
                ))
        if row.supplier_status and row.supplier_status_from and row.supplier_status_evidence_ids:
            evaluated["vendor_status"] += 1
            if row.supplier_status in NONCOMPLIANT_STATUSES and row.supplier_status_from < row.issue_date:
                findings.append(_signal(
                    f"ROSIE-STATUS-{row.expense_id}", "Situação cadastral requer contextualização temporal",
                    f"Situação {row.supplier_status} registrada antes da despesa; requer documentação histórica e análise jurídica.",
                    set(row.evidence_ids + row.supplier_status_evidence_ids),
                    category=SignalCategory.CORPORATE, severity=SignalSeverity.MEDIUM,
                    method="comparação de status cadastral documentado e data de emissão",
                    threshold={"status": row.supplier_status, "effective_from": row.supplier_status_from.isoformat()},
                    alternatives=["regularização posterior", "cadastro desatualizado", "regime de contratação aplicável"],
                ))
        else:
            skipped["vendor_status"] += 1

        if row.supplier_legal_nature:
            evaluated["electoral_nature"] += 1
            if row.supplier_legal_nature.strip().startswith("409-0"):
                findings.append(_signal(
                    f"ROSIE-ELECTION-{row.expense_id}", "Despesa com categoria cadastral eleitoral",
                    "Fornecedor possui natureza cadastral de candidatura; verificar competência e finalidade do gasto.",
                    set(row.evidence_ids), category=SignalCategory.ELECTORAL, severity=SignalSeverity.MEDIUM,
                    method="comparação com natureza jurídica 409-0 declarada no cadastro",
                    threshold={"legal_nature_prefix": "409-0"},
                    alternatives=["categoria correta para o instrumento", "despesa eleitoral legítima"],
                ))
        else:
            skipped["electoral_nature"] += 1
        if row.subquota:
            rows_by_month[(row.actor_id, row.issue_date.year, row.issue_date.month, row.subquota)].append(row)
        else:
            skipped["monthly_quota"] += 1
        if row.peer_group:
            rows_by_peer[row.peer_group].append(row)
        else:
            skipped["peer_outlier"] += 1
        if row.invoice_id and row.supplier_cnpj and _cnpj_valid(row.supplier_cnpj):
            rows_by_invoice[(re.sub(r"\D", "", row.supplier_cnpj), row.invoice_id.strip())].append(row)
        else:
            skipped["invoice_overlap"] += 1
        if row.personal_presence_evidenced and row.latitude is not None and row.longitude is not None:
            rows_by_actor_day[(row.actor_id, row.issue_date)].append(row)
        else:
            skipped["geo_dispersion"] += 1

    for key, group in rows_by_month.items():
        month = date(key[1], key[2], 1)
        policies = [p for p in (quota_policies or []) if p.category == key[3] and p.valid_from <= month <= p.valid_to]
        if len(policies) != 1:
            skipped["monthly_quota"] += len(group)
            continue
        evaluated["monthly_quota"] += len(group)
        policy = policies[0]
        total = sum((row.amount_brl for row in group), Decimal(0))
        if total > policy.limit_brl:
            findings.append(_signal(
                f"ROSIE-QUOTA-{key[0]}-{key[1]}-{key[2]}-{key[3]}",
                "Soma mensal supera limite fornecido e documentado",
                f"Total R$ {total} supera o limite R$ {policy.limit_brl}; confirmar escopo, compensações e retificações.",
                set(policy.evidence_ids).union(*(set(r.evidence_ids) for r in group)),
                category=SignalCategory.PAYMENT, severity=SignalSeverity.MEDIUM,
                method="soma Decimal por responsável, mês e categoria sob norma temporal",
                threshold={"monthly_limit_brl": str(policy.limit_brl), "total_brl": str(total)},
                alternatives=["reembolsos retificados", "exceção legal", "valor atribuído à categoria incorreta"],
            ))

    for name, group in rows_by_peer.items():
        if len(group) < min_peer_size:
            skipped["peer_outlier"] += len(group)
            continue
        evaluated["peer_outlier"] += len(group)
        amounts = [row.amount_brl for row in group]
        med = median(amounts)
        mad = median([abs(x - med) for x in amounts])
        ceiling = max(med * peer_multiplier, med + 6 * mad)
        for row in group:
            if ceiling > 0 and row.amount_brl > ceiling:
                findings.append(_signal(
                    f"ROSIE-PEER-{row.expense_id}", "Despesa atípica entre valores comparáveis",
                    f"R$ {row.amount_brl} supera corte R$ {ceiling} do grupo {name}; comparação não valida escopo.",
                    set(row.evidence_ids), category=SignalCategory.PRICE, severity=SignalSeverity.LOW,
                    method="mediana, desvio absoluto mediano e multiplicador no grupo previamente comparável",
                    threshold={"peer_group": name, "group_size": len(group),
                               "median_brl": str(med), "review_cut_brl": str(ceiling)},
                    alternatives=["maior quantidade", "serviço distinto", "diferença de local ou duração"],
                ))

    for (supplier, invoice), group in rows_by_invoice.items():
        if len(group) < 2:
            evaluated["invoice_overlap"] += len(group)
            continue
        evaluated["invoice_overlap"] += len(group)
        findings.append(_signal(
            f"ROSIE-INVOICE-{supplier}-{invoice}", "Identificador de documento fiscal reutilizado",
            "Documento fiscal aparece em mais de um registro; conferir estorno, parcela ou pagamento repetido.",
            set().union(*(set(row.evidence_ids) for row in group)),
            category=SignalCategory.PAYMENT, severity=SignalSeverity.MEDIUM,
            method="CNPJ e identificador de documento fiscal coincidentes em registros distintos",
            threshold={"record_count": len(group)},
            alternatives=["parcelamento legítimo", "retificação", "mesmo documento de prestação de contas"],
        ))

    for (actor, day), group in rows_by_actor_day.items():
        if len(group) < 2:
            skipped["geo_dispersion"] += len(group)
            continue
        evaluated["geo_dispersion"] += len(group)
        farthest = max(
            ((a, b, _distance_km(a, b)) for i, a in enumerate(group) for b in group[i + 1:]),
            key=lambda x: x[2],
        )
        if farthest[2] > distance_review_km:
            findings.append(_signal(
                f"ROSIE-GEO-{actor}-{day.isoformat()}", "Dispersão geográfica de despesas no mesmo dia",
                f"Documentos sugerem locais separados por cerca de {farthest[2]:.0f} km; não demonstram presença física.",
                set(farthest[0].evidence_ids + farthest[1].evidence_ids),
                category=SignalCategory.DOCUMENT, severity=SignalSeverity.LOW,
                method="distância geodésica Haversine entre pontos associados à mesma data",
                threshold={"distance_review_km": distance_review_km,
                           "observed_distance_km": round(farthest[2], 1)},
                alternatives=["despesas emitidas por terceiros", "viagem legítima", "data fiscal diferente do consumo"],
            ))

    return {
        "schema": "vtb.serenata_screening.v1",
        "analysis_type": "AUDIT_TRIAGE_NOT_CRIMINAL_FINDING",
        "records_examined": len(expenses),
        "input_sha256": input_fingerprint(expenses),
        "source_scope": "USER_SUPPLIED_RECORDS_ONLY",
        "data_verified_against_primary_sources": False,
        "signals": [s.to_dict() for s in findings],
        "triage_band": triage_band(findings),
        "rule_coverage": {"evaluated": dict(evaluated), "skipped_or_inapplicable": dict(skipped)},
        "limitations": [
            "Nenhum dado foi consultado autonomamente em fonte primária.",
            "Documento fiscal repetido, situação cadastral, distância e preço atípico exigem validação.",
            "Sem documentação de empenho, liquidação, pagamento e entrega não há prova de desvio.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ROSIE-inspired VTB public expense screening")
    parser.add_argument("input", help="Private JSON with expenses and optional quota_policies")
    parser.add_argument("--output", required=True, help="Path for private JSON report")
    args = parser.parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)
    if input_path.resolve() == output_path.resolve():
        parser.error("Output must differ from input")
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("expenses"), list):
        parser.error("Expected JSON object with expenses list")
    expenses = [PublicExpense.from_dict(item) for item in payload["expenses"]]
    policies = [QuotaPolicy.from_dict(item) for item in payload.get("quota_policies", [])]
    results = screen_expenses(expenses, quota_policies=policies)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"output": str(output_path), "records": len(expenses),
                      "signals": len(results["signals"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
