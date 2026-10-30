import pytest

from vtb.models import Claim, EvidenceRecord, SourceHealth, SourceQuality, SourceRecord
from vtb.notice import draft_case_notice
from vtb.runtime import CaseStore


def case_with_evidence(tmp_path, health=SourceHealth.HEALTHY):
    store = CaseStore(tmp_path / "case.sqlite")
    store.create_mission("TEST", "Auditoria", "Verificar objeto", "Município", "2025")
    store.add_source("TEST", SourceRecord("S1", "Documento oficial", "Órgão", "https://example.gov.br/doc.pdf", SourceQuality.S5_OFFICIAL_PRIMARY, health=health))
    store.add_evidence("TEST", EvidenceRecord("E1", "S1", "Valor publicado", locator="p.2"))
    store.add_claim("TEST", Claim("C1", "O documento registra determinado valor.", evidence_ids=["E1"]))
    return store


def test_draft_facts_require_primary_healthy_evidence(tmp_path):
    store = case_with_evidence(tmp_path)
    draft = draft_case_notice(store, "TEST", "Ouvidoria pública", ["C1"])
    assert draft["status"] == "DRAFT_REVIEW_REQUIRED"
    assert draft["publication_allowed"] is False
    assert "E1" in draft["markdown"]
    assert "nenhum envio efetuado" in draft["markdown"]
    store.close()


def test_unhealthy_source_blocks_draft(tmp_path):
    store = case_with_evidence(tmp_path, SourceHealth.TIMEOUT)
    with pytest.raises(ValueError, match="not verified healthy"):
        draft_case_notice(store, "TEST", "Ouvidoria pública", ["C1"])
    store.close()


def test_unknown_claim_is_rejected(tmp_path):
    store = case_with_evidence(tmp_path)
    with pytest.raises(ValueError, match="claim unknown"):
        draft_case_notice(store, "TEST", "Ouvidoria pública", ["UNKNOWN"])
    store.close()
