"""Synthetic tests for generic political case intake and CLI."""
import json

import pytest

from vtb.cli import build_parser, cmd_politician_init
from vtb.politician_cases import build_politician_case
from vtb.runtime import CaseStore


def test_person_only_requires_identity_verification():
    case = build_politician_case("SYN-1", " Pessoa   Exemplo ")
    assert case["person"]["name_provided"] == "Pessoa Exemplo"
    assert case["person"]["identity_status"] == "UNRESOLVED"
    assert case["coverage"]["sources_queried"] == 0
    assert case["coverage"]["state"] == "NOT_STARTED"
    assert case["complaint_readiness"]["status"] == "NOT_ASSESSED"
    assert case["complaint_readiness"]["crime_or_corruption_score"] is None
    assert case["report_template"]["findings"] == []
    assert case["report_template"]["publication_status"] == "QUARANTINED"
    assert all(source["status"] == "NOT_QUERIED" for source in case["source_plan"])
    assert len(case["workstreams"]) == 10


def test_municipal_bahia_routes_to_tcm_and_municipal_sources():
    case = build_politician_case(
        "SYN-2", "Pessoa Fictícia", office="vereadora", uf="BA",
        municipality="Município Exemplo", start_year=2024, end_year=2028
    )
    source = {entry["source_id"]: entry for entry in case["source_plan"]}
    assert case["person"]["office_provided"] == "vereador"
    assert source["MUNICIPAL_AUDIT"]["entrypoint_url"] == "https://www.tcm.ba.gov.br/"
    assert "MUNICIPAL_COUNCIL" in source
    assert "STATE_LEGISLATIVE" not in source
    assert "CHAMBER" not in source
    assert case["report_template"]["scope"]["jurisdiction"] == "Município Exemplo/BA"


def test_federal_offices_route_to_their_legislative_sources():
    deputy = build_politician_case("SYN-3", "Pessoa A", office="deputada federal")
    senator = build_politician_case("SYN-4", "Pessoa B", office="senadora")
    federal = {entry["source_id"] for entry in deputy["source_plan"]}
    senate = {entry["source_id"] for entry in senator["source_plan"]}
    assert "CHAMBER" in federal and "SENATE" not in federal
    assert "SENATE" in senate and "CHAMBER" not in senate
    assert "MUNICIPAL_EXECUTIVE" not in senate


def test_non_bahia_does_not_guess_municipal_audit_url():
    case = build_politician_case("SYN-5", "Pessoa Teste", office="prefeito", uf="ES")
    source = {entry["source_id"]: entry for entry in case["source_plan"]}
    assert source["MUNICIPAL_AUDIT"]["entrypoint_url"] is None
    assert source["MUNICIPAL_AUDIT"]["coverage"] == "UNVERIFIED"


@pytest.mark.parametrize(
    ("kwargs", "fragment"),
    [
        ({"uf": "XX"}, "UF"),
        ({"municipality": "Cidade Exemplo"}, "requires UF"),
        ({"office": "rei"}, "unsupported"),
        ({"office": "presidente"}, "ambiguous"),
        ({"start_year": 2030, "end_year": 2020}, "exceed"),
        ({"start_year": 1600}, "years"),
    ],
)
def test_rejects_ambiguous_scope(kwargs, fragment):
    with pytest.raises(ValueError, match=fragment):
        build_politician_case("SYN-INVALID", "Pessoa Exemplo", **kwargs)


def test_cli_writes_local_plan_and_persists_intake(tmp_path):
    output = tmp_path / "private" / "case.json"
    db = tmp_path / "vtb.sqlite3"
    parser = build_parser()
    args = parser.parse_args([
        "--db", str(db), "politician-init", "SYN-CLI", "Pessoa Fictícia",
        "--office", "prefeita", "--uf", "BA", "--municipality",
        "Município Fictício", "--output", str(output),
    ])
    assert cmd_politician_init(args) == 0
    plan = json.loads(output.read_text(encoding="utf-8"))
    assert plan["person"]["identity_status"] == "UNRESOLVED"
    assert plan["coverage"]["sources_queried"] == 0
    store = CaseStore(db)
    try:
        assert store.mission("SYN-CLI")["state"] == "INTAKE"
        assert store.db.execute(
            "SELECT count(*) FROM hypotheses WHERE case_id=?", ("SYN-CLI",)
        ).fetchone()[0] == 3
    finally:
        store.close()
    with pytest.raises(FileExistsError):
        cmd_politician_init(args)
