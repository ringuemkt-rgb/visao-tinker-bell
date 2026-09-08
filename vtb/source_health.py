from __future__ import annotations

from .models import SourceHealth


def classify_http_status(status: int | None) -> SourceHealth:
    if status is None:
        return SourceHealth.UNKNOWN
    if 200 <= status < 300:
        return SourceHealth.HEALTHY
    if status in {401}:
        return SourceHealth.AUTH_REQUIRED
    if status in {403, 451}:
        return SourceHealth.BLOCKED
    if status == 429:
        return SourceHealth.RATE_LIMITED
    if 500 <= status < 600:
        return SourceHealth.DEGRADED
    if 300 <= status < 500:
        return SourceHealth.PARTIAL
    return SourceHealth.UNKNOWN


def classify_exception(exc: BaseException) -> SourceHealth:
    name = exc.__class__.__name__.lower()
    text = str(exc).lower()
    if "timeout" in name or "timeout" in text:
        return SourceHealth.TIMEOUT
    if any(token in name or token in text for token in ("connection", "dns", "resolve", "network")):
        return SourceHealth.CONNECTION_ERROR
    return SourceHealth.UNKNOWN


def absence_is_established(health: SourceHealth, exhaustive_scope: bool, explicit_negative: bool) -> bool:
    """Only a healthy, sufficiently scoped source with an explicit negative may establish absence."""
    return health == SourceHealth.HEALTHY and exhaustive_scope and explicit_negative


def negative_result_label(health: SourceHealth, exhaustive_scope: bool = False, explicit_negative: bool = False) -> str:
    if absence_is_established(health, exhaustive_scope, explicit_negative):
        return "NOT_FOUND_WITHIN_VERIFIED_SCOPE"
    if health in {SourceHealth.BLOCKED, SourceHealth.TIMEOUT, SourceHealth.CONNECTION_ERROR, SourceHealth.DEGRADED}:
        return "SOURCE_DEGRADED_NO_ABSENCE_INFERENCE"
    return "NO_RESULT_NO_ABSENCE_INFERENCE"
