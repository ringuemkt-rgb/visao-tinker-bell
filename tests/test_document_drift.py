from vtb.document_drift import DocumentVersion, material_drift_signal


def test_material_document_change_is_signal_not_misconduct_label():
    a = DocumentVersion("d", "v1", "e1", {"value": 10, "text": "a"})
    b = DocumentVersion("d", "v2", "e2", {"value": 20, "text": "a"})
    signal = material_drift_signal(a, b, material_fields={"value"})
    assert signal is not None
    assert signal.status == "ANOMALY_FOR_VERIFICATION"
