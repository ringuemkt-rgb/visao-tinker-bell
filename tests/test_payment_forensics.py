from decimal import Decimal

from vtb.payment_forensics import PaymentRecord, duplicate_payment_candidates


def test_duplicate_is_candidate_not_conclusion():
    rows = [
        PaymentRecord("p1", "s1", Decimal(100), "2026-01-02", ("e1",), invoice_number="NF1"),
        PaymentRecord("p2", "s1", Decimal(100), "2026-01-02", ("e2",), invoice_number="NF1"),
    ]
    signals = duplicate_payment_candidates(rows)
    assert len(signals) == 1
    assert "Possível" in signals[0].title
    assert signals[0].status == "ANOMALY_FOR_VERIFICATION"
