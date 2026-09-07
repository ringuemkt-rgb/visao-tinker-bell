from vtb.tool_registry import ToolStatus
from vtb.toolcheck import check_command


def test_missing_command_is_not_claimed_operational():
    result = check_command("vtb-command-that-should-not-exist-91c2")
    assert not result.present
    assert result.status == ToolStatus.S1_REPOSITORY_FOUND
