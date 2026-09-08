from vtb.benford import assess_benford


def test_benford_blocks_small_sample():
    assessment = assess_benford([10, 20, 30, 40], minimum_n=100)
    assert assessment.applicable is False
    assert "n<100" in assessment.reasons
