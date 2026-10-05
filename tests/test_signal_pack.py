from vtb.signal_pack import circular_flows, disproportionate_expense, score_contratacao, supplier_partner, surname_homonym


def test_despesa_e_socio():
    hit = disproportionate_expense(250_000, 20_000)
    assert hit and hit["label"] == "ANOMALY_FOR_VERIFICATION"
    assert disproportionate_expense(30_000, 20_000) is None
    socios = [{"documento": "123.456.789-00", "cnpj": "11222333000181"}]
    assert supplier_partner(["12345678900"], socios)
    assert surname_homonym("Silva", ["Ana Silva"])["rule_id"] == "sobrenome-homonimo"


def test_ciclo_e_score():
    edges = [
        {"src": "doador", "dst": "candidato", "valor": 20000},
        {"src": "candidato", "dst": "fornecedor", "valor": 20000},
        {"src": "fornecedor", "dst": "doador", "valor": 20000},
    ]
    ciclos = circular_flows(edges)
    assert ciclos and ciclos[0]["valor"] >= 10000
    score = score_contratacao(
        {"preco_sobre_mediana": 3.2, "documento_socio_igual": True, "count_ceis": 1, "participantes": 1}
    )
    assert score["fila"] is True
    assert score["score"] <= 100
    homonimo = score_contratacao({"sobrenome_igual": True})
    assert homonimo["eixos"]["relacao"] == 10
