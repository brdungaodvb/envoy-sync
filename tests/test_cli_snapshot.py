"""Tests for envoy_sync.cli_snapshot."""

from pathlib import Path

import pytest

from envoy_sync.cli_snapshot import run_snapshot


def _write_env(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_take_single_file_returns_0(tmp_path):
    env_file = tmp_path / ".env"
    store = tmp_path / "snaps.jsonl"
    _write_env(env_file, "KEY=value\n")
    rc = run_snapshot(["take", str(env_file), "--store", str(store)])
    assert rc == 0
    assert store.exists()


def test_take_creates_snapshot_entry(tmp_path):
    env_file = tmp_path / ".env"
    store = tmp_path / "snaps.jsonl"
    _write_env(env_file, "A=1\nB=2\n")
    run_snapshot(["take", str(env_file), "--store", str(store)])
    lines = store.read_text().strip().splitlines()
    assert len(lines) == 1


def test_take_with_note_stores_note(tmp_path):
    import json

    env_file = tmp_path / ".env"
    store = tmp_path / "snaps.jsonl"
    _write_env(env_file, "X=1\n")
    run_snapshot(["take", str(env_file), "--note", "pre-release", "--store", str(store)])
    data = json.loads(store.read_text().strip())
    assert data["note"] == "pre-release"


def test_take_multiple_files(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    store = tmp_path / "snaps.jsonl"
    _write_env(f1, "A=1\n")
    _write_env(f2, "B=2\n")
    rc = run_snapshot(["take", str(f1), str(f2), "--store", str(store)])
    assert rc == 0
    lines = store.read_text().strip().splitlines()
    assert len(lines) == 2


def test_take_missing_file_returns_1(tmp_path):
    store = tmp_path / "snaps.jsonl"
    rc = run_snapshot(["take", str(tmp_path / "ghost.env"), "--store", str(store)])
    assert rc == 1


def test_list_empty_store_returns_0(tmp_path, capsys):
    store = tmp_path / "snaps.jsonl"
    rc = run_snapshot(["list", "--store", str(store)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "no snapshots" in out


def test_list_shows_entries(tmp_path, capsys):
    env_file = tmp_path / ".env"
    store = tmp_path / "snaps.jsonl"
    _write_env(env_file, "K=v\n")
    run_snapshot(["take", str(env_file), "--store", str(store)])
    run_snapshot(["list", "--store", str(store)])
    out = capsys.readouterr().out
    assert str(env_file) in out


def test_list_filter_by_source(tmp_path, capsys):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    store = tmp_path / "snaps.jsonl"
    _write_env(f1, "A=1\n")
    _write_env(f2, "B=2\n")
    run_snapshot(["take", str(f1), str(f2), "--store", str(store)])
    capsys.readouterr()
    run_snapshot(["list", "--source", str(f1), "--store", str(store)])
    out = capsys.readouterr().out
    assert str(f1) in out
    assert str(f2) not in out
