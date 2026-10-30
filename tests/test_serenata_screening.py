"""Synthetic and deterministic regressions for Serenata-inspired triage."""
from datetime import date
from decimal import Decimal

import pytest

from vtb.serenata_screening import (
    PublicExpense,
    QuotaPolicy,
    _cnpj_valid,
    screen_expenses,
)

VALID_CNPJ = "11.222.333/0001-81"


def make(expense_id, **kwargs):
    record = {
        "expense_id": expense_id,
        "actor_id": "FUNCIONARIO-FICTICIO",
        "issue_date": "2026-06-10",
        "amount_brl": "45.20",
        "evidence_ids": ["DOC-" + expense_id],
        "supplier_cnpj": VALID_CNPJ,
    }
    record.update(kwargs)
    return PublicExpense.from_dict(record)


def codes(result):
    return {s["signal_id"] for s in result["signals"]}


def test_cnpj_check_digits_and_missing_identifier():
    assert _cnpj_valid(VALID_CNPJ)
    assert not _cnpj_valid("11.222.333/0001-82")
    assert not _cnpj_valid("11.111.111/1111-11")
    result = screen_expenses([make("A"), make("B", supplier_cnpj="11.222.333/0001-82"),
                              make("C", supplier_cnpj=None)])
    assert codes(result) == {"ROSIE-ID-B"}
    assert result["rule_coverage"]["skipped_or_inapplicable"]["supplier_identifier"] == 1


def test_vendor_status_requires_prior_date_and_separate_evidence():
    a = make("A", supplier_status="BAIXADA", supplier_status_from="2025-01-01",
             supplier_status_evidence_ids=["REG-1"])
    b = make("B", supplier_status="BAIXADA", supplier_status_from="2027-01-01",
             supplier_status_evidence_ids=["REG-2"])
    c = make("C", supplier_status="BAIXADA", supplier_status_from="2025-01-01")
    result = screen_expenses([a, b, c])
    assert codes(result) == {"ROSIE-STATUS-A"}
    assert {"DOC-A", "REG-1"} <= set(result["signals"][0]["evidence_ids"])


def test_quota_uses_authoritative_temporal_rule_and_exact_decimal():
    policies = [
        QuotaPolicy("MEAL", Decimal("100.00"), date(2026, 1, 1), date(2026, 12, 31), ("ACT-2026",)),
        QuotaPolicy("MEAL", Decimal("1.00"), date(2025, 1, 1), date(2025, 12, 31), ("ACT-2025",)),
    ]
    rows = [
        make("A", amount_brl="60.00", subquota="MEAL"),
        make("B", amount_brl="40.01", subquota="MEAL"),
        make("C", issue_date="2025-06-10", amount_brl="0", subquota="MEAL"),
    ]
    result = screen_expenses(rows, quota_policies=policies)
    assert "ROSIE-QUOTA-FUNCIONARIO-FICTICIO-2026-6-MEAL" in codes(result)
    assert len(result["signals"]) == 1
    assert "ACT-2026" in result["signals"][0]["evidence_ids"]
    assert result["signals"][0]["threshold"]["total_brl"] == "100.01"


def test_quota_fails_closed_when_no_rule_or_ambiguous_rules():
    e = make("A", subquota="FOOD")
    p = QuotaPolicy("FOOD", Decimal(100), date(2026, 1, 1), date(2026, 12, 31), ("POL",))
    assert screen_expenses([e])["signals"] == []
    assert screen_expenses([e], quota_policies=[p, p])["signals"] == []


def test_invoice_repeat_is_only_review_flag():
    result = screen_expenses([
        make("A", invoice_id="NF-155"),
        make("B", invoice_id="NF-155"),
        make("C", invoice_id="NF-156"),
    ])
    assert len(result["signals"]) == 1
    signal = result["signals"][0]
    assert signal["category"] == "PAYMENT"
    assert signal["status"] == "ANOMALY_FOR_VERIFICATION"
    assert signal["false_positive_risk"] == "high"
    assert signal["legal_validation_required"] is True


def test_peer_outlier_requires_minimum_comparable_population():
    few = [make(f"A{i}", amount_brl="25.00", peer_group="same-specs") for i in range(4)]
    few.append(make("X", amount_brl="250.00", peer_group="same-specs"))
    assert screen_expenses(few)["signals"] == []
    rows = [make(f"A{i}", amount_brl="25.00", peer_group="same-specs") for i in range(10)]
    rows.append(make("X", amount_brl="250.00", peer_group="same-specs"))
    result = screen_expenses(rows)
    assert codes(result) == {"ROSIE-PEER-X"}
    assert result["signals"][0]["threshold"]["group_size"] == 11


def test_geo_does_not_establish_presence_and_requires_eligibility():
    rows = [
        make("A", latitude=-12.9714, longitude=-38.5014, personal_presence_evidenced=True),
        make("B", latitude=-23.5505, longitude=-46.6333, personal_presence_evidenced=True),
        make("C", latitude=-3.1, longitude=-60.0, personal_presence_evidenced=False),
    ]
    result = screen_expenses(rows)
    assert codes(result) == {"ROSIE-GEO-FUNCIONARIO-FICTICIO-2026-06-10"}
    assert "não demonstram presença física" in result["signals"][0]["description"]


def test_election_legal_nature_requires_explicit_metadata():
    result = screen_expenses([
        make("A", supplier_legal_nature="409-0 - CANDIDATO A CARGO ELETIVO"),
        make("B"),
    ])
    assert codes(result) == {"ROSIE-ELECTION-A"}


def test_duplicate_expense_identifiers_rejected_before_signals():
    with pytest.raises(ValueError, match="duplicate expense IDs"):
        screen_expenses([make("A"), make("A")])


@pytest.mark.parametrize("bad", [float("nan"), "-2", "Infinity"])
def test_invalid_amount_rejected(bad):
    with pytest.raises(ValueError, match="amount"):
        make("B", amount_brl=bad)


def test_source_provenance_and_no_conclusions():
    result = screen_expenses([make("A")])
    assert result["signals"] == []
    assert result["source_scope"] == "USER_SUPPLIED_RECORDS_ONLY"
    assert not result["data_verified_against_primary_sources"]
    assert result["triage_band"] == "P4_NO_SIGNAL"


def test_malformed_coordinate_rejected():
    with pytest.raises(ValueError, match="coordinates"):
        make("A", latitude=100, longitude=0)
