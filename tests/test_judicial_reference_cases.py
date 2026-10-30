import json
from pathlib import Path


def test_judicial_corpus_is_non_scoring_and_source_grounded():
    path = Path(__file__).parents[1] / "config" / "judicial_reference_cases.json"
    corpus = json.loads(path.read_text(encoding="utf-8"))
    assert len(corpus["cases"]) == 4
    assert not corpus["evaluated_by_engine"]
    assert not corpus["blinded_review"]
    assert not corpus["original_full_court_records_archived"]
    assert len({c["id"] for c in corpus["cases"]}) == len(corpus["cases"])
    assert all(c["source_url"].startswith(("https://scon.stj.jus.br/", "https://www.stj.jus.br/"))
               for c in corpus["cases"])
    assert any(c["control_class"] == "DOCUMENTED_SPECIFIC_INTENT" for c in corpus["cases"])
    assert any(c["control_class"] == "IRREGULARITY_NOT_ENOUGH" for c in corpus["cases"])
