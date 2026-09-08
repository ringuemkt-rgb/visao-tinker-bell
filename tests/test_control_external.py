from vtb.control_external import ControlProceeding, ProceedingStatus


def test_pending_case_is_not_final_finding():
    item = ControlProceeding("x", "TCM", ProceedingStatus.PENDING, ("e1",))
    assert item.supports_final_liability_claim() is False
    assert item.semantic_label() == "PROCEEDING_IS_NOT_FINDING"
