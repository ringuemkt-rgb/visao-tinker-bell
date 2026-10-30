"""Regression tests for read-only, local Jarbas-style review. All data synthetic."""
import pytest

from vtb.serenata_review import render_review
from vtb.serenata_screening import PublicExpense, screen_expenses


def event(code, **kwargs):
    row = {
        "expense_id": code,
        "actor_id": "AGENTE FICTÍCIO",
        "issue_date": "2026-06-10",
        "amount_brl": "20.00",
        "evidence_ids": ["DOC-" + code],
    }
    row.update(kwargs)
    return PublicExpense.from_dict(row)


def test_html_renders_same_day_navigation_and_source_ids():
    events = [event("A"), event("B"), event("C", issue_date="2026-06-11")]
    page = render_review(events, screen_expenses(events))
    assert "Registro 1" in page
    assert "Registro 2" in page
    assert 'href="#exp-1"' in page
    assert "DOC-B" in page
    assert "não comprova desvio" in page


def test_html_escapes_user_supplied_content_and_scripts():
    events = [event("<script>alert('x')</script>",
                    actor_id='<img src=x onerror="attack()">',
                    invoice_id="<svg onload=alert(1)>",
                    evidence_ids=['<b>EVIDENCE</b>'])]
    page = render_review(events, screen_expenses(events))
    assert "<script>" not in page
    assert "<img " not in page
    assert "<svg " not in page
    assert "&lt;script&gt;" in page
    assert "&lt;b&gt;EVIDENCE&lt;/b&gt;" in page


def test_html_does_not_claim_zero_alerts_proves_legal_compliance():
    events = [event("SAFE")]
    page = render_review(events, screen_expenses(events))
    assert "Nenhum alerta nas regras aplicáveis" in page
    assert "conferência dos originais" in page


def test_html_refuses_different_screening_volume():
    events = [event("A")]
    other = screen_expenses([event("A"), event("B")])
    with pytest.raises(ValueError, match="record count"):
        render_review(events, other)


def test_html_refuses_another_dataset_even_if_row_count_matches():
    original = [event("A")]
    altered = [event("B")]
    other = screen_expenses(original)
    with pytest.raises(ValueError, match="input hash"):
        render_review(altered, other)
