"""Tests for envoy_sync.cli_template.run_template."""
import pytest
from pathlib import Path
from envoy_sync.cli_template import run_template


def _write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_simple_render_exits_0(tmp_path, capsys):
    tpl = _write_env(tmp_path, "tpl.env", "URL=https://${HOST}/api\n")
    ctx = _write_env(tmp_path, "ctx.env", "HOST=example.com\n")
    code = run_template([str(tpl), "--context", str(ctx)])
    assert code == 0
    out = capsys.readouterr().out
    assert "URL=https://example.com/api" in out


def test_no_substitution_exits_0(tmp_path, capsys):
    tpl = _write_env(tmp_path, "tpl.env", "KEY=plain_value\n")
    code = run_template([str(tpl)])
    assert code == 0
    assert "KEY=plain_value" in capsys.readouterr().out


def test_unresolved_without_strict_exits_0(tmp_path, capsys):
    tpl = _write_env(tmp_path, "tpl.env", "DSN=postgres://${DB_HOST}/db\n")
    code = run_template([str(tpl)])
    assert code == 0
    err = capsys.readouterr().err
    assert "DB_HOST" in err


def test_unresolved_with_strict_exits_1(tmp_path):
    tpl = _write_env(tmp_path, "tpl.env", "DSN=postgres://${DB_HOST}/db\n")
    code = run_template([str(tpl), "--strict"])
    assert code == 1


def test_missing_template_file_exits_1(tmp_path, capsys):
    code = run_template([str(tmp_path / "nonexistent.env")])
    assert code == 1
    assert "not found" in capsys.readouterr().err


def test_missing_context_file_exits_1(tmp_path, capsys):
    tpl = _write_env(tmp_path, "tpl.env", "KEY=value\n")
    code = run_template([str(tpl), "--context", str(tmp_path / "missing.env")])
    assert code == 1


def test_output_written_to_file(tmp_path):
    tpl = _write_env(tmp_path, "tpl.env", "HOST=localhost\nURL=${HOST}/path\n")
    out_file = tmp_path / "rendered.env"
    code = run_template([str(tpl), "--output", str(out_file)])
    assert code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "URL" in content
    assert "localhost/path" in content
