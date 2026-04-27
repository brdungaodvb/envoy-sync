"""Tests for envoy_sync.parser."""

import pytest
from pathlib import Path

from envoy_sync.parser import parse_env_file, write_env_file


# ---------------------------------------------------------------------------
# parse_env_file
# ---------------------------------------------------------------------------

def test_parse_simple_pairs(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = parse_env_file(env_file)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_quoted_double(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text('GREETING="hello world"\n')
    result = parse_env_file(env_file)
    assert result["GREETING"] == "hello world"


def test_parse_quoted_single(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("MSG='it works'\n")
    result = parse_env_file(env_file)
    assert result["MSG"] == "it works"


def test_parse_skips_comments_and_blanks(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nKEY=val\n")
    result = parse_env_file(env_file)
    assert result == {"KEY": "val"}


def test_parse_inline_comment(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080 # http port\n")
    result = parse_env_file(env_file)
    assert result["PORT"] == "8080"


def test_parse_value_with_equals(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text('TOKEN=abc=def==\n')
    result = parse_env_file(env_file)
    assert result["TOKEN"] == "abc=def=="


def test_parse_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_parse_invalid_syntax(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("INVALID_LINE\n")
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_file(env_file)


def test_parse_empty_key(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("=value\n")
    with pytest.raises(ValueError, match="Empty key"):
        parse_env_file(env_file)


# ---------------------------------------------------------------------------
# write_env_file
# ---------------------------------------------------------------------------

def test_write_and_read_roundtrip(tmp_path: Path):
    env_file = tmp_path / ".env"
    original = {"HOST": "localhost", "PORT": "5432", "NAME": "my db"}
    write_env_file(env_file, original)
    result = parse_env_file(env_file)
    assert result == original


def test_write_quotes_values_with_spaces(tmp_path: Path):
    env_file = tmp_path / ".env"
    write_env_file(env_file, {"KEY": "hello world"})
    content = env_file.read_text()
    assert 'KEY="hello world"' in content
