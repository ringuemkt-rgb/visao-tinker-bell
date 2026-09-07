from vtb.anti_corruption import IntegrityAssessment
from vtb.signals import RiskSignal, SignalCategory, SignalSeverity


def test_no_automatic_corruption_label():
    assessment = IntegrityAssessment("case")
    assessment.add_signal(
        RiskSignal(
            "s1",
            SignalCategory.PROCUREMENT,
            "Anomalia",
            "Teste",
            SignalSeverity.HIGH,
            evidence_ids=["e1"],
        )
    )
    assert assessment.can_describe_as_corruption() is False
    assert assessment.summary()["automatic_corruption_label"] is False
