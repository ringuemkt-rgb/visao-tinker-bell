from __future__ import annotations

from .models import MissionState

_TERMINAL = {
    MissionState.READY,
    MissionState.READY_WITH_LIMITATIONS,
    MissionState.INCONCLUSIVE,
    MissionState.QUARANTINED,
}

_ALLOWED: dict[MissionState, set[MissionState]] = {
    MissionState.INTAKE: {MissionState.SCOPE},
    MissionState.SCOPE: {MissionState.PLAN},
    MissionState.PLAN: {MissionState.RESEARCH},
    MissionState.RESEARCH: {MissionState.INGEST, MissionState.GAP_ANALYSIS},
    MissionState.INGEST: {MissionState.RESOLVE},
    MissionState.RESOLVE: {MissionState.ANALYZE, MissionState.RESEARCH},
    MissionState.ANALYZE: {MissionState.HYPOTHESIS, MissionState.GAP_ANALYSIS},
    MissionState.HYPOTHESIS: {MissionState.FALSIFY},
    MissionState.FALSIFY: {MissionState.GAP_ANALYSIS, MissionState.RED_TEAM},
    MissionState.GAP_ANALYSIS: {MissionState.RESEARCH, MissionState.RED_TEAM},
    MissionState.RED_TEAM: {MissionState.SYNTHESIS, MissionState.RESEARCH},
    MissionState.SYNTHESIS: {MissionState.LEGAL_REVIEW, MissionState.QA},
    MissionState.LEGAL_REVIEW: {MissionState.QA, MissionState.RESEARCH},
    MissionState.QA: {MissionState.DECISION, MissionState.RESEARCH},
    MissionState.DECISION: _TERMINAL,
    **{state: set() for state in _TERMINAL},
}


def can_transition(current: MissionState, target: MissionState) -> bool:
    return target in _ALLOWED[current]


def transition(current: MissionState, target: MissionState) -> MissionState:
    if not can_transition(current, target):
        raise ValueError(f"invalid mission transition: {current} -> {target}")
    return target


def allowed_next(current: MissionState) -> set[MissionState]:
    return set(_ALLOWED[current])
