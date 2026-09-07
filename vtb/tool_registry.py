from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml


class ToolStatus(StrEnum):
    S0_NOT_EVALUATED = "S0_NOT_EVALUATED"
    S1_REPOSITORY_FOUND = "S1_REPOSITORY_FOUND"
    S2_INSTALLABLE = "S2_INSTALLABLE"
    S3_INSTALLED = "S3_INSTALLED"
    S4_TESTED = "S4_TESTED"
    S5_OPERATIONAL = "S5_OPERATIONAL"
    S6_OPERATIONAL_LIMITED = "S6_OPERATIONAL_LIMITED"
    S7_DEGRADED = "S7_DEGRADED"
    S8_BROKEN = "S8_BROKEN"
    S9_DISCONTINUED = "S9_DISCONTINUED"
    S10_GOVERNANCE_BLOCKED = "S10_GOVERNANCE_BLOCKED"


@dataclass(slots=True)
class ToolRecord:
    tool_id: str
    name: str
    category: str
    status: ToolStatus = ToolStatus.S0_NOT_EVALUATED
    repository: str | None = None
    version: str | None = None
    commit: str | None = None
    last_checked: str | None = None
    last_tested: str | None = None
    public_only: bool = True
    limitations: list[str] = field(default_factory=list)
    notes: str = ""


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, ToolRecord] = {}

    def add(self, record: ToolRecord) -> None:
        self.tools[record.tool_id] = record

    def mark_executed(self, tool_id: str) -> None:
        if tool_id not in self.tools:
            raise KeyError(tool_id)
        status = self.tools[tool_id].status
        if status not in {ToolStatus.S4_TESTED, ToolStatus.S5_OPERATIONAL, ToolStatus.S6_OPERATIONAL_LIMITED, ToolStatus.S7_DEGRADED}:
            raise RuntimeError(f"tool {tool_id} cannot be represented as executed from status {status}")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ToolRegistry":
        data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        reg = cls()
        for item in data.get("tools", []):
            item = dict(item)
            item["status"] = ToolStatus(item.get("status", ToolStatus.S0_NOT_EVALUATED))
            reg.add(ToolRecord(**item))
        return reg
