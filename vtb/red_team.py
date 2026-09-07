from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_CHECKS = [
    "HOMONYM_OR_ENTITY_COLLISION",
    "WRONG_DATE_OR_TIME_WINDOW",
    "WRONG_VALUE_OR_UNIT",
    "LATER_DOCUMENT_SUPERSEDES_EARLIER",
    "DEPENDENT_SOURCES_MISTAKEN_FOR_CORROBORATION",
    "SELECTION_BIAS",
    "INVALID_ECONOMIC_COMPARISON",
    "LEGAL_RULE_OUTDATED",
    "PLAUSIBLE_LEGITIMATE_EXPLANATION_NOT_TESTED",
    "INFERENCE_LEAKED_AS_FACT",
]


@dataclass
class RedTeamResult:
    checked: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    notes: dict[str, str] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.failures and set(DEFAULT_CHECKS).issubset(self.checked)

    def check(self, item: str, passed: bool, note: str = "") -> None:
        if item not in self.checked:
            self.checked.append(item)
        if not passed and item not in self.failures:
            self.failures.append(item)
        if note:
            self.notes[item] = note

    def missing(self) -> list[str]:
        return [item for item in DEFAULT_CHECKS if item not in self.checked]
