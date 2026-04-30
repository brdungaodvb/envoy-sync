"""Tests for envoy_sync.snapshotter."""

import json
from pathlib import Path

import pytest

from envoy_sync.snapshotter import (
    Snapshot,
    SnapshotStore,
    load_snapshots,
    save_snapshot,
    take_snapshot,
)


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_take_snapshot_captures_env():
    snap = take_snapshot(ENV, source=".env")
    assert snap.env == ENV
    assert snap.source == ".env"
    assert snap.note == ""
    assert "T" in snap.timestamp  # ISO format


def test_take_snapshot_with_note():
    snap = take_snapshot(ENV, source=".env", note="before deploy")
    assert snap.note == "before deploy"


def test_snapshot_is_independent_copy():
    original = {"KEY": "value"}
    snap = take_snapshot(original, source=".env")
    original["KEY"] = "changed"
    assert snap.env["KEY"] == "value"


def test_snapshot_to_dict_round_trip():
    snap = take_snapshot(ENV, source="prod.env", note="test")
    data = snap.to_dict()
    restored = Snapshot.from_dict(data)
    assert restored.env == snap.env
    assert restored.source == snap.source
    assert restored.note == snap.note
    assert restored.timestamp == snap.timestamp


def test_snapshot_store_add_and_latest():
    store = SnapshotStore()
    assert store.latest() is None
    snap1 = take_snapshot({"A": "1"}, source="a.env")
    snap2 = take_snapshot({"B": "2"}, source="b.env")
    store.add(snap1)
    store.add(snap2)
    assert store.latest() is snap2


def test_snapshot_store_by_source():
    store = SnapshotStore()
    store.add(take_snapshot({"A": "1"}, source="a.env"))
    store.add(take_snapshot({"B": "2"}, source="b.env"))
    store.add(take_snapshot({"C": "3"}, source="a.env"))
    results = store.by_source("a.env")
    assert len(results) == 2
    assert all(s.source == "a.env" for s in results)


def test_save_and_load_snapshots(tmp_path):
    path = tmp_path / "snapshots.jsonl"
    snap1 = take_snapshot({"X": "1"}, source="x.env")
    snap2 = take_snapshot({"Y": "2"}, source="y.env", note="hi")
    save_snapshot(snap1, path)
    save_snapshot(snap2, path)

    store = load_snapshots(path)
    assert len(store.snapshots) == 2
    assert store.snapshots[0].source == "x.env"
    assert store.snapshots[1].note == "hi"


def test_load_snapshots_missing_file(tmp_path):
    store = load_snapshots(tmp_path / "nonexistent.jsonl")
    assert store.snapshots == []


def test_save_appends_to_existing_file(tmp_path):
    path = tmp_path / "snaps.jsonl"
    save_snapshot(take_snapshot({"A": "1"}, "a.env"), path)
    save_snapshot(take_snapshot({"B": "2"}, "b.env"), path)
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
