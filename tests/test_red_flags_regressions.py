from lib.red_flags_engine import RedFlagsEngine
from vtb.claims import ClaimLedger
from vtb.gates import publication_gate
from vtb.models import Claim, ClaimStatus


def test_absent_assets_field_does_not_mean_zero_assets():
    engine = RedFlagsEngine()
    findings = engine.evaluate({})
    assert "candidato-sem-bens-declarados" not in {x.rule_id for x in findings}
    explicit_zero = engine.evaluate({"totalDeBens": 0})
    assert "candidato-sem-bens-declarados" in {x.rule_id for x in explicit_zero}


def test_unparseable_assets_field_records_error_instead_of_silent_success():
    engine = RedFlagsEngine()
    findings = engine.evaluate({"totalDeBens": "unknown"})
    assert "candidato-sem-bens-declarados" not in {x.rule_id for x in findings}
    assert any(x["rule_id"] == "candidato-sem-bens-declarados" for x in engine.errors)


def test_company_founded_after_contract_is_not_recent_company_alert():
    engine = RedFlagsEngine()
    result = engine.evaluate({"data_inicio_atividade": "2026-06-01", "dataAssinatura": "2025-06-01"})
    ids = {x.rule_id for x in result}
    assert "fornecedor-cnpj-recem-aberto" not in ids
    assert "fornecedor-cnpj-muito-recente" not in ids


def test_sensitive_legal_review_is_not_assumed_completed():
    ledger = ClaimLedger()
    ledger.add_claim(Claim("LEGAL", "conclusão sensível", critical=True, legal_sensitive=True, status=ClaimStatus.VERIFIED_PRIMARY))
    gate = publication_gate(ledger, red_team_done=True)
    assert not gate.passed
    assert "LEGAL_REVIEW_REQUIRED" in gate.reasons
    assert publication_gate(ledger, red_team_done=True, legal_review_done=True).passed
