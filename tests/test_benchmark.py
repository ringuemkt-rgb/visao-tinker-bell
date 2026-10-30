from vtb.benchmark import run_benchmark


def test_synthetic_controls_both_positive_and_negative():
    report = run_benchmark()
    assert report["dataset"] == "SYNTHETIC_TEST_CONTROLS_ONLY"
    assert len(report["cases"]) == 12
    assert report["confusion"] == {"tp": 6, "tn": 6, "fp": 0, "fn": 0}
    assert report["precision_on_fixture"] == 1
    assert report["recall_on_fixture"] == 1
    assert "not measure performance" in report["limitations"][1]
