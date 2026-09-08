from __future__ import annotations

from dataclasses import dataclass

from .source_catalog import (
    SourceCatalog,
    SourceSpec,
)

MODE_DOMAINS = {
    "PROCUREMENT": ("procurement", "contracts", "price"),
    "MONEY": ("budget", "payments", "transfers"),
    "CORPORATE": ("corporate", "sanctions", "pep"),
    "ELECTORAL": ("electoral", "assets"),
    "CONTROL": ("control", "judicial"),
    "LEGISLATIVE": ("legislative", "budget"),
    "FULL": (
        "procurement",
        "contracts",
        "price",
        "budget",
        "payments",
        "transfers",
        "corporate",
        "sanctions",
        "pep",
        "electoral",
        "assets",
        "control",
        "judicial",
        "legislative",
    ),
}


@dataclass(slots=True, frozen=True)
class ResearchPlan:
    mode: str
    domains: tuple[str, ...]
    sources: tuple[SourceSpec, ...]


def build_research_plan(catalog: SourceCatalog, mode: str = "FULL") -> ResearchPlan:
    normalized = mode.upper()
    if normalized not in MODE_DOMAINS:
        raise ValueError(f"unknown investigation mode: {mode}")
    domains = MODE_DOMAINS[normalized]
    return ResearchPlan(normalized, domains, tuple(catalog.for_domains(*domains)))
