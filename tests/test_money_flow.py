from vtb.money_flow import MoneyFlow, MoneyRecord, MoneyStage


def test_paid_is_not_naive_sum_of_stages():
    flow = MoneyFlow([
        MoneyRecord("c", MoneyStage.CONTRACTED, 100.0, "S1"),
        MoneyRecord("e", MoneyStage.COMMITTED, 80.0, "S2"),
        MoneyRecord("l", MoneyStage.LIQUIDATED, 70.0, "S3"),
        MoneyRecord("p", MoneyStage.PAID, 60.0, "S4"),
    ])
    assert flow.paid_total() == 60.0
    assert flow.naive_sum_is_invalid() == 310.0
    assert flow.consistency_warnings() == []
