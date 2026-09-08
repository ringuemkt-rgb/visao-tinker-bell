from vtb.watchlists import WatchTarget, make_watch_hit, requires_human_resolution


def test_watch_hit_is_candidate_only():
    target = WatchTarget("t1", "PERSON", "Pessoa", {"name": ("Pessoa",)}, "controle social")
    hit = make_watch_hit(target, "source", ["e1"], ["name"], 0.95)
    assert hit.status == "CANDIDATE_MATCH"
    assert requires_human_resolution(hit) is True
