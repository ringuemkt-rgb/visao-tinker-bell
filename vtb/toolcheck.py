from __future__ import annotations

import shutil
from dataclasses import dataclass

from .tool_registry import ToolStatus


@dataclass(slots=True)
class LocalToolCheck:
    command: str
    present: bool
    executable: str | None
    status: ToolStatus
    note: str


def check_command(command: str) -> LocalToolCheck:
    path = shutil.which(command)
    if not path:
        return LocalToolCheck(command, False, None, ToolStatus.S1_REPOSITORY_FOUND, "Not found in PATH; repository existence is not operational status")
    return LocalToolCheck(command, True, path, ToolStatus.S3_INSTALLED, "Installed/present only; synthetic functional test still required before S4+")
