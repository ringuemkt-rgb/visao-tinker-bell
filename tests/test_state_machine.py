import pytest

from vtb.models import MissionState
from vtb.state_machine import transition


def test_valid_transition():
    assert transition(MissionState.INTAKE, MissionState.SCOPE) == MissionState.SCOPE


def test_skipping_research_is_rejected():
    with pytest.raises(ValueError):
        transition(MissionState.INTAKE, MissionState.DECISION)
