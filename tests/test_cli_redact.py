"""Tests for envoy_sync.cli_redact."""

import json
import os
from pathlib import Path

import pytest

from envoy_sync.cli_redact import run_redact


def _write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_safe_file_returns_0(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "HOST=localhost\nPORT=5432\n")
    assert run_redact([f]) == 0


def test_sensitive_value_is_redacted(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "DB_PASSWORD=secret\nHOST=localhost\n")
    run_redact([f])
    out = capsys.readouterr().out
    assert "secret" not in out
    assert "***REDACTED***" in out
    assert "HOST=localhost" in out


def test_custom_placeholder(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "API_KEY=abc123\n")
    run_redact([f, "--placeholder", "<hidden>"])
    out = capsys.readouterr().out
    assert "<hidden>" in out
    assert "abc123" not in out


def test_show_summary_to_stderr(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "TOKEN=tok\nHOST=h\n")
    run_redact([f, "--show-summary"])
    err = capsys.readouterr().err
    assert "TOKEN" in err
    assert "1" in err


def test_show_summary_no_sensitive(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "HOST=h\nPORT=80\n")
    run_redact([f, "--show-summary"])
    err = capsys.readouterr().err
    assert "No sensitive" in err


def test_json_format(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "SECRET=s\nHOST=h\n")
    run_redact([f, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["SECRET"] == "***REDACTED***"
    assert data["HOST"] == "h"


def test_missing_file_returns_2(tmp_path):
    assert run_redact(["/nonexistent/.env"]) == 2


def test_extra_pattern_redacts_custom_key(tmp_path, capsys):
    f = _write_env(tmp_path, ".env", "MY_PIN=1234\nHOST=h\n")
    run_redact([f, "--pattern", r"(?i)pin"])
    out = capsys.readouterr().out
    assert "1234" not in out
    assert "***REDACTED***" in out
