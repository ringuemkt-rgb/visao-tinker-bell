from vtb.procurement_forensics import ProcurementRecord, concentration_signal, supplier_hhi


def test_hhi_is_concentration_not_fraud_label():
    rows = [
        ProcurementRecord("p1", "a", 90.0, ["e1"]),
        ProcurementRecord("p2", "b", 10.0, ["e2"]),
    ]
    hhi = supplier_hhi(rows)
    assert hhi is not None and hhi > 2500
    signal = concentration_signal(rows)
    assert signal is not None
    assert signal.status == "ANOMALY_FOR_VERIFICATION"
    assert "cartel" not in signal.title.lower()
