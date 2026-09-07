from vtb.asset_forensics import AssetSnapshot, reconcile_asset_variation


def test_noncomparable_assets_are_blocked_from_naive_growth_claim():
    a = AssetSnapshot("x", 2020, 100.0, ("e1",), "TSE-declared")
    b = AssetSnapshot("x", 2024, 500.0, ("e2",), "commercial-estimate")
    signal = reconcile_asset_variation(a, b)
    assert signal is not None
    assert signal.title == "Série patrimonial não comparável"
