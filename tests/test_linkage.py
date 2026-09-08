from vtb.linkage import LinkageCandidate, can_auto_merge, classify_candidate


def test_probabilistic_linkage_never_auto_merges_sensitive_identity():
    candidate = LinkageCandidate("a", "b", 0.999, ("name", "birthDate"), ("e1",), "model")
    assert classify_candidate(candidate) == "HIGH_PRIORITY_HUMAN_REVIEW"
    assert can_auto_merge(candidate) is False
