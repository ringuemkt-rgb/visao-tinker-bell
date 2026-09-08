from vtb.models import SourceHealth
from vtb.source_health import classify_http_status, negative_result_label


def test_403_never_becomes_not_found():
    health = classify_http_status(403)
    assert health == SourceHealth.BLOCKED
    assert negative_result_label(health) == "SOURCE_DEGRADED_NO_ABSENCE_INFERENCE"


def test_verified_explicit_negative_can_establish_scoped_absence():
    assert negative_result_label(SourceHealth.HEALTHY, True, True) == "NOT_FOUND_WITHIN_VERIFIED_SCOPE"
