"""Tests for the envoy_sync.cli_diff module."""

from __future__ import annotations

import pytest

from envoy_sync.cli_diff import run_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_env(tmp_path, filename: str, content: str):
    p = tmp_path / filename
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_identical_files_returns_0(tmp_path):
    content = "FOO=bar\nBAZ=qux\n"
    left = _write_env(tmp_path, "a.env", content)
    right = _write_env(tmp_path, "b.env", content)
    assert run_diff([left, right]) == 0


def test_different_files_returns_1(tmp_path):
    left = _write_env(tmp_path, "a.env", "FOO=bar\n")
    right = _write_env(tmp_path, "b.env", "FOO=changed\n")
    assert run_diff([left, right]) == 1


def test_added_key_returns_1(tmp_path):
    left = _write_env(tmp_path, "a.env", "FOO=bar\n")
    right = _write_env(tmp_path, "b.env", "FOO=bar\nNEW=val\n")
    assert run_diff([left, right]) == 1


def test_removed_key_returns_1(tmp_path):
    left = _write_env(tmp_path, "a.env", "FOO=bar\nOLD=val\n")
    right = _write_env(tmp_path, "b.env", "FOO=bar\n")
    assert run_diff([left, right]) == 1


def test_quiet_flag_suppresses_output(tmp_path, capsys):
    left = _write_env(tmp_path, "a.env", "FOO=bar\n")
    right = _write_env(tmp_path, "b.env", "FOO=changed\n")
    code = run_diff(["--quiet", left, right])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert code == 1


def test_only_changed_hides_added_removed(tmp_path, capsys):
    left = _write_env(tmp_path, "a.env", "FOO=bar\nOLD=gone\n")
    right = _write_env(tmp_path, "b.env", "FOO=changed\nNEW=here\n")
    run_diff(["--only-changed", left, right])
    captured = capsys.readouterr()
    assert "OLD" not in captured.out
    assert "NEW" not in captured.out
    assert "FOO" in captured.out


def test_missing_left_file_exits(tmp_path):
    right = _write_env(tmp_path, "b.env", "FOO=bar\n")
    with pytest.raises(SystemExit) as exc_info:
        run_diff(["/nonexistent/a.env", right])
    assert exc_info.value.code == 1


def test_missing_right_file_exits(tmp_path):
    left = _write_env(tmp_path, "a.env", "FOO=bar\n")
    with pytest.raises(SystemExit) as exc_info:
        run_diff([left, "/nonexistent/b.env"])
    assert exc_info.value.code == 1


def test_output_shows_added_removed_changed(tmp_path, capsys):
    left = _write_env(tmp_path, "a.env", "FOO=old\nREMOVED=gone\n")
    right = _write_env(tmp_path, "b.env", "FOO=new\nADDED=here\n")
    run_diff([left, right])
    out = capsys.readouterr().out
    assert "- REMOVED" in out
    assert "+ ADDED" in out
    assert "~ FOO" in out
