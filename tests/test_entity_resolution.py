from vtb.entity_resolution import EntityCandidate, compare


def test_conflicting_tax_ids_reject_merge():
    a = EntityCandidate("A", "Empresa Igual", tax_id="111")
    b = EntityCandidate("B", "Empresa Igual", tax_id="222")
    assert compare(a, b).status == "MATCH_REJECTED"


def test_exact_tax_id_confirms():
    a = EntityCandidate("A", "Nome A", tax_id="111")
    b = EntityCandidate("B", "Nome B", tax_id="111")
    assert compare(a, b).status == "MATCH_CONFIRMED"
