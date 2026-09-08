from pathlib import Path

from vtb.case_router import build_research_plan
from vtb.source_catalog import SourceCatalog


def test_full_plan_prioritizes_primary_sources():
    catalog = SourceCatalog.from_yaml(Path("config/sources_br_v8.yaml"))
    plan = build_research_plan(catalog, "CORPORATE")
    assert plan.sources
    assert plan.sources[0].primary is True
    assert any(source.source_id == "opensanctions" and not source.primary for source in plan.sources)
