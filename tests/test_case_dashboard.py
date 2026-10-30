"""Synthetic private cases. Dashboard must never execute untrusted HTML."""
from vtb.case_dashboard import render_dashboard


def snapshot():
    return {
        "mission": {"case_id": "SYN", "title": "<script>alert(1)</script>",
                    "question": "Was the contract published?"},
        "sources": [{
            "source_id": "S1", "payload": {
                "issuer": "<img src=x onerror=alert(1)>",
                "url": "javascript:alert(1)",
                "health": "HEALTHY", "quality": "S4_OFFICIAL_STRUCTURED",
            },
        }],
        "evidence": [{
            "evidence_id": "E1", "payload": {
                "source_id": "S1", "locator": "field",
                "excerpt": "<svg onload=alert(1)>",
            },
        }],
        "claims": [{
            "claim_id": "C1", "payload": {
                "claim_id": "C1", "status": "PARTIALLY_SUPPORTED",
                "statement": "Synthetic claim", "evidence_ids": ["E1"],
            },
        }],
        "hypotheses": [],
    }


def test_dashboard_html_escapes_and_blocks_javascript_links():
    page = render_dashboard(snapshot())
    assert "<script>" not in page
    assert "<img src=x" not in page
    assert "<svg onload" not in page
    assert 'href="javascript:' not in page
    assert "&lt;script&gt;" in page
    assert "NÃO VALIDADO" in page


def test_documented_edge_requires_known_evidence():
    data = snapshot()
    page = render_dashboard(data, links=[
        {"from": "AGENT A", "to": "SUPPLIER B", "relation": "Documented contract",
         "evidence_ids": ["E1"], "status": "DOCUMENTED"},
        {"from": "SUPPLIER B", "to": "AGENT C", "relation": "Unknown relation",
         "evidence_ids": ["FAKE"], "status": "DOCUMENTED"},
    ])
    assert "Grafo de relações" in page
    assert "candidate/unverified" in page
    assert "documented" in page
    assert "AGENT A" in page
    assert 'stroke-dasharray="5 5"' in page


def test_no_source_links_without_safe_urls():
    data = snapshot()
    data["sources"][0]["payload"]["url"] = "https://pncp.gov.br/"
    page = render_dashboard(data)
    assert 'href="https://pncp.gov.br/"' in page
    assert 'rel="noopener noreferrer"' in page
