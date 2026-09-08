from vtb.incremental import Checkpoint, CheckpointStore


def test_checkpoint_round_trip(tmp_path):
    store = CheckpointStore(tmp_path / "checkpoints.json")
    store.save(Checkpoint("pncp", cursor="abc", records_seen=10))
    loaded = store.load("pncp")
    assert loaded.cursor == "abc"
    assert loaded.records_seen == 10
