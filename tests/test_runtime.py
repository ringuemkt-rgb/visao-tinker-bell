from vtb.runtime import CaseStore


def test_sqlite_mission_roundtrip(tmp_path):
    store = CaseStore(tmp_path / "vtb.sqlite3")
    store.create_mission("CASE-1", "Teste", "Qual é o fato?")
    row = store.mission("CASE-1")
    assert row["case_id"] == "CASE-1"
    assert row["state"] == "INTAKE"
    store.close()
