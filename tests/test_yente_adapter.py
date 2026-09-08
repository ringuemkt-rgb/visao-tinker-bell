from unittest.mock import Mock, patch

from vtb.adapters.yente import YenteMatcher


def test_yente_match_is_candidate_not_identity_proof():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "responses": {
            "q1": {
                "results": [
                    {
                        "id": "X",
                        "schema": "Person",
                        "score": 0.91,
                        "properties": {"name": ["Pessoa Teste"]},
                    }
                ]
            }
        }
    }
    with patch("vtb.adapters.yente.requests.post", return_value=response):
        result = YenteMatcher("https://example.test").match_person("q1", "Pessoa Teste", country="br")
    assert result.candidates[0].score == 0.91
    assert result.requires_independent_validation is True
