import pytest

from vtb.optional_tools import OPTIONAL_MODULES, optional_toolcheck


def test_optional_tools_are_not_claimed_operational():
    result = optional_toolcheck(["networkx", "docling"])
    assert result["requires_runtime_validation"] is True
    assert len(result["tools"]) == 2
    assert all(row["operational"] is False for row in result["tools"])
    assert all(row["status"] in {"S0_NOT_EVALUATED", "S3_INSTALLED"} for row in result["tools"])


def test_unknown_tools_rejected():
    assert "splink" in OPTIONAL_MODULES
    with pytest.raises(ValueError):
        optional_toolcheck(["arbitrary_shell_executor"])
