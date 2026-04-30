"""Tests for envoy_sync.cli_compare."""
import io
import os
import tempfile
import pytest

from envoy_sync.cli_compare import run_compare


def _write_env(tmp_path, filename: str, content: str) -> str:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_identical_files_returns_0(tmp_path):
    content = "FOO=bar\nBAZ=qux\n"
    a = _write_env(tmp_path, "a.env", content)
    b = _write_env(tmp_path, "b.env", content)
    out = io.StringIO()
    rc = run_compare(a, b, output=out, err=io.StringIO())
    assert rc == 0
    assert "No changes" in out.getvalue()


def test_added_key_returns_1(tmp_path):
    a = _write_env(tmp_path, "a.env", "FOO=1\n")
    b = _write_env(tmp_path, "b.env", "FOO=1\nBAR=2\n")
    out = io.StringIO()
    rc = run_compare(a, b, output=out, err=io.StringIO())
    assert rc == 1
    assert "+ BAR=2" in out.getvalue()


def test_removed_key_returns_1(tmp_path):
    a = _write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write_env(tmp_path, "b.env", "FOO=1\n")
    out = io.StringIO()
    rc = run_compare(a, b, output=out, err=io.StringIO())
    assert rc == 1
    assert "- BAR=2" in out.getvalue()


def test_modified_key_returns_1(tmp_path):
    a = _write_env(tmp_path, "a.env", "FOO=old\n")
    b = _write_env(tmp_path, "b.env", "FOO=new\n")
    out = io.StringIO()
    rc = run_compare(a, b, output=out, err=io.StringIO())
    assert rc == 1
    assert "~ FOO" in out.getvalue()


def test_show_unchanged_flag(tmp_path):
    a = _write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write_env(tmp_path, "b.env", "FOO=1\nBAR=99\n")
    out = io.StringIO()
    rc = run_compare(a, b, show_unchanged=True, output=out, err=io.StringIO())
    assert rc == 1
    assert "unchanged" in out.getvalue()


def test_missing_file_exits_2(tmp_path, capsys):
    a = _write_env(tmp_path, "a.env", "FOO=1\n")
    with pytest.raises(SystemExit) as exc_info:
        run_compare(a, str(tmp_path / "missing.env"), output=io.StringIO(), err=io.StringIO())
    assert exc_info.value.code == 2
