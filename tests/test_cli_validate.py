"""Tests for envoy_sync.cli_validate.run_validate."""

from __future__ import annotations

from pathlib import Path

import pytest

from envoy_sync.cli_validate import run_validate


def _write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Happy-path
# ---------------------------------------------------------------------------

def test_valid_file_returns_0(tmp_path):
    f = _write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    assert run_validate([f]) == 0


def test_multiple_valid_files_return_0(tmp_path):
    f1 = _write_env(tmp_path, ".env.a", "A=1\n")
    f2 = _write_env(tmp_path, ".env.b", "B=2\n")
    assert run_validate([f1, f2]) == 0


def test_empty_file_returns_0(tmp_path):
    f = _write_env(tmp_path, ".env", "")
    assert run_validate([f]) == 0


# ---------------------------------------------------------------------------
# Invalid key names
# ---------------------------------------------------------------------------

def test_invalid_key_returns_1(tmp_path):
    f = _write_env(tmp_path, ".env", "123BAD=value\n")
    assert run_validate([f]) == 1


def test_hyphen_key_returns_1(tmp_path):
    f = _write_env(tmp_path, ".env", "MY-KEY=value\n")
    assert run_validate([f]) == 1


# ---------------------------------------------------------------------------
# Empty values
# ---------------------------------------------------------------------------

def test_empty_value_returns_1_by_default(tmp_path):
    f = _write_env(tmp_path, ".env", "SECRET=\n")
    assert run_validate([f]) == 1


def test_empty_value_returns_0_when_allowed(tmp_path):
    f = _write_env(tmp_path, ".env", "SECRET=\n")
    assert run_validate([f], allow_empty=True) == 0


# ---------------------------------------------------------------------------
# Duplicate keys
# ---------------------------------------------------------------------------

def test_duplicate_key_returns_1(tmp_path):
    f = _write_env(tmp_path, ".env", "FOO=1\nFOO=2\n")
    assert run_validate([f]) == 1


# ---------------------------------------------------------------------------
# Mixed files
# ---------------------------------------------------------------------------

def test_one_invalid_among_valid_returns_1(tmp_path):
    good = _write_env(tmp_path, ".env.good", "OK=yes\n")
    bad = _write_env(tmp_path, ".env.bad", "1NOPE=val\n")
    assert run_validate([good, bad]) == 1


# ---------------------------------------------------------------------------
# Missing file
# ---------------------------------------------------------------------------

def test_missing_file_returns_1(tmp_path):
    assert run_validate([str(tmp_path / "nonexistent.env")]) == 1
