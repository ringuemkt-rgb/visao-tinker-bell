"""Contract-first synthetic tests for a non-accusatory audit dossier engine."""
import pytest

from vtb.investigative_reasoning import audit_dossier
from vtb.models import (
    Claim, EvidenceRecord, Hypothesis, SourceHealth, SourceQuality, SourceRecord,
)
from vtb.runtime import CaseStore


def setup_case(tmp_path, *, with_evidence=True, conflict=False, mirror=False):
    store = CaseStore(tmp_path / "research.sqlite")
    store.create_mission("CASE-T", "Auditoria", "Contrato de consultoria", "Bahia", "2025-2026")
    store.add_source("CASE-T", SourceRecord(
        "SRC-1", "Contrato público", "Câmara", "https://example.gov.br/contrato",
        SourceQuality.S5_OFFICIAL_PRIMARY, health=SourceHealth.HEALTHY,
        sha256="a" * 64, original_source_id="ORIGINAL-1",
    ))
    if mirror:
        store.add_source("CASE-T", SourceRecord(
            "SRC-2", "Espelho do mesmo contrato", "Espelho",
            "https://example.gov.br/espelho", SourceQuality.S5_OFFICIAL_PRIMARY,
            health=SourceHealth.HEALTHY, sha256="b" * 64,
            original_source_id="ORIGINAL-1",
        ))
    if with_evidence:
        store.add_evidence("CASE-T", EvidenceRecord(
            "EV-1", "SRC-1", "Registro sintético: objeto e valor", locator="p. 2"
        ))
    if mirror:
        store.add_evidence("CASE-T", EvidenceRecord(
            "EV-2", "SRC-2", "Registro sintético: objeto e valor", locator="p. 2"
        ))
    ev = ["EV-1"] if with_evidence else []
    if mirror:
        ev.append("EV-2")
    store.add_claim("CASE-T", Claim(
        "CLAIM-1", "Contrato registra objeto de assessoria.",
        critical=True, legal_sensitive=True, evidence_ids=ev,
        contradicting_evidence_ids=["EV-2"] if conflict else [],
    ))
    store.add_hypothesis("CASE-T", Hypothesis("H-REG", "Necessidade excepcional do serviço", falsifier="Serviço inteiramente coberto por estrutura própria"))
    store.add_hypothesis("CASE-T", Hypothesis("H-ALT", "Possível sobreposição funcional", falsifier="Escopo técnico especializado comprovado"))
    return store


def review(*, valid=True):
    return {
        "criteria": {
            "CLAIM-1": {
                "criterion": "Verificar necessidade e preço pela lei aplicável",
                "source_url": "https://example.gov.br/lei"
            }
        },
        "hypotheses": [
            {"hypothesis_id": "H-REG", "kind": "regular", "checks": [{"evidence_id": "EV-1", "assessment": "NEUTRAL"}]},
            {"hypothesis_id": "H-ALT", "kind": "irregularity", "checks": [{"evidence_id": "EV-1", "assessment": "NEUTRAL"}]},
        ] if valid else [],
    }


def test_full_dossier_requires_human_review_and_never_alleges_crime(tmp_path):
    store = setup_case(tmp_path)
    result = audit_dossier(store, "CASE-T", review())
    assert result["status"] == "READY_WITH_LIMITATIONS"
    assert result["publication_authorized"] is False
    finding = result["matrix"][0]
    assert finding["claim_id"] == "CLAIM-1"
    assert finding["criterion"]["source_url"] == "https://example.gov.br/lei"
    assert finding["source_lineages"] == 1
    assert finding["evidence"][0]["locator"] == "p. 2"
    assert "EV-1" in result["markdown"]
    assert "revisão humana" in result["markdown"].lower()
    store.close()


def test_mirrored_sources_never_count_as_independent_corrob(tmp_path):
    store = setup_case(tmp_path, mirror=True)
    result = audit_dossier(store, "CASE-T", review())
    assert result["matrix"][0]["source_lineages"] == 1
    assert "VERIFIED_CORROBORATED" not in result["matrix"][0]["classification"]
    store.close()


def test_critical_claim_with_no_evidence_is_quarantined(tmp_path):
    store = setup_case(tmp_path, with_evidence=False)
    result = audit_dossier(store, "CASE-T", review(valid=False))
    assert result["status"] == "QUARANTINED"
    assert "CRITICAL_NO_EVIDENCE" in result["matrix"][0]["gaps"]
    store.close()


def test_contradiction_never_becomes_corrob(tmp_path):
    store = setup_case(tmp_path, conflict=True, mirror=True)
    result = audit_dossier(store, "CASE-T", review())
    assert result["status"] == "QUARANTINED"
    assert "UNRESOLVED_CONTRADICTION" in result["matrix"][0]["gaps"]
    store.close()


def test_missing_regular_rival_hypothesis_blocks_synthesis(tmp_path):
    store = setup_case(tmp_path)
    report = review(valid=False)
    result = audit_dossier(store, "CASE-T", report)
    assert result["status"] == "INCONCLUSIVE"
    assert "REGULAR_EXPLANATION_MISSING" in result["global_gaps"]
    store.close()


def test_unreferenced_hypothesis_assessment_is_rejected(tmp_path):
    store = setup_case(tmp_path)
    data = review()
    data["hypotheses"][0]["checks"][0]["evidence_id"] = "FAKE"
    with pytest.raises(ValueError, match="unknown evidence"):
        audit_dossier(store, "CASE-T", data)
    store.close()


def test_legal_sensitive_claim_requires_criterion_source(tmp_path):
    store = setup_case(tmp_path)
    data = review()
    data["criteria"] = {}
    result = audit_dossier(store, "CASE-T", data)
    assert result["status"] == "QUARANTINED"
    assert "LEGAL_CRITERION_MISSING" in result["matrix"][0]["gaps"]
    store.close()


def test_no_roleplay_or_autonomous_disclosure():
    from vtb.investigative_reasoning import reasoning_contract
    contract = reasoning_contract()
    assert contract["auto_file"] is False
    assert contract["publish"] is False
    assert contract["human_validation_required"] is True
