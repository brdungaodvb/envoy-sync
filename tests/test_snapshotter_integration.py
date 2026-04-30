"""Integration tests: snapshotter round-trips with parser."""

from pathlib import Path

from envoy_sync.parser import parse_env_file, write_env_file
from envoy_sync.snapshotter import (
    load_snapshots,
    save_snapshot,
    take_snapshot,
)


def test_snapshot_env_matches_parsed_file(tmp_path):
    env_file = tmp_path / ".env"
    write_env_file({"HOST": "db.local", "PORT": "5432"}, env_file)
    parsed = parse_env_file(env_file)
    snap = take_snapshot(parsed, source=str(env_file))
    assert snap.env == parsed


def test_multiple_snapshots_preserve_order(tmp_path):
    store_path = tmp_path / "snaps.jsonl"
    for i in range(3):
        env_file = tmp_path / f"v{i}.env"
        write_env_file({"VERSION": str(i)}, env_file)
        parsed = parse_env_file(env_file)
        snap = take_snapshot(parsed, source=str(env_file), note=f"v{i}")
        save_snapshot(snap, store_path)

    store = load_snapshots(store_path)
    assert len(store.snapshots) == 3
    notes = [s.note for s in store.snapshots]
    assert notes == ["v0", "v1", "v2"]


def test_snapshot_env_is_restored_correctly(tmp_path):
    original = {"SECRET": "abc123", "DEBUG": "false"}
    env_file = tmp_path / ".env"
    write_env_file(original, env_file)
    parsed = parse_env_file(env_file)
    snap = take_snapshot(parsed, source=str(env_file))

    store_path = tmp_path / "snaps.jsonl"
    save_snapshot(snap, store_path)

    store = load_snapshots(store_path)
    restored_env = store.latest().env
    assert restored_env["SECRET"] == "abc123"
    assert restored_env["DEBUG"] == "false"
