from pathlib import Path

from vtb.ftm_export import from_case
from vtb.representacao import build_relato, select_facts, write_packet


def test_recusa_claim_sem_hash():
    claims = [
        {"id": "a", "fato": "Contrato 1.", "url": "https://pncp.gov.br/1", "sha256": "abc123def4567890"},
        {"id": "b", "fato": "Sem fonte."},
        {"id": "c", "fato": "O alvo e corrupto.", "url": "https://x", "sha256": "abc123def4567890"},
    ]
    kept, omitted = select_facts(claims)
    assert [c["id"] for c in kept] == ["a"]
    assert "b" in omitted and "c" in omitted
    relato = build_relato({"destino": "CGU", "orgao": "Municipio", "agente": "cargo X"}, claims)
    assert "Requeiro a apuracao" in relato
    assert "corrupto" not in relato.lower()
    assert len(relato) <= 7000


def test_pdf_e_ftm(tmp_path: Path):
    manifest = write_packet(
        {"destino": "CGU", "orgao": "Municipio", "agente": "cargo X", "data": "05/10/2026"},
        [{"fato": "Empenho 10, nao pagamento.", "url": "https://pncp.gov.br/1", "sha256": "abc123def4567890", "documento": "PNCP"}],
        tmp_path,
    )
    pdf = Path(manifest["pdf"]).read_bytes()
    assert pdf.startswith(b"%PDF-1.4")
    entities = from_case({"empresas": [{"id": "br-cnpj-1", "nome": "Empresa", "cnpj": "11222333000181"}]})
    assert entities[0]["schema"] == "Company"
