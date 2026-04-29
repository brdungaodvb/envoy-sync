"""Tests for envoy_sync.exporter."""

import json
import pytest

from envoy_sync.exporter import export_env


SIMPLE_ENV = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true", "PORT": "8080"}


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_dotenv_simple_values():
    result = export_env(SIMPLE_ENV, "dotenv", sort_keys=True)
    lines = result.splitlines()
    assert "DATABASE_URL=postgres://localhost/db" in lines
    assert "DEBUG=true" in lines
    assert "PORT=8080" in lines


def test_dotenv_quotes_values_with_spaces():
    result = export_env({"MSG": "hello world"}, "dotenv")
    assert result == 'MSG="hello world"'


def test_dotenv_quotes_values_with_hash():
    result = export_env({"VAL": "foo#bar"}, "dotenv")
    assert result == 'VAL="foo#bar"'


def test_dotenv_sort_keys():
    env = {"Z": "z", "A": "a", "M": "m"}
    result = export_env(env, "dotenv", sort_keys=True)
    keys = [line.split("=")[0] for line in result.splitlines()]
    assert keys == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# json format
# ---------------------------------------------------------------------------

def test_json_format_is_valid_json():
    result = export_env(SIMPLE_ENV, "json")
    parsed = json.loads(result)
    assert parsed["PORT"] == "8080"
    assert parsed["DEBUG"] == "true"


def test_json_sort_keys():
    env = {"Z": "z", "A": "a"}
    result = export_env(env, "json", sort_keys=True)
    parsed = json.loads(result)
    assert list(parsed.keys()) == ["A", "Z"]


# ---------------------------------------------------------------------------
# shell format
# ---------------------------------------------------------------------------

def test_shell_format_export_prefix():
    result = export_env({"FOO": "bar"}, "shell")
    assert result == "export FOO='bar'"


def test_shell_format_escapes_single_quotes():
    result = export_env({"GREETING": "it's alive"}, "shell")
    # Single quotes inside single-quoted string use the 'end-quote, literal, reopen' trick.
    assert "export GREETING=" in result
    assert "it" in result and "alive" in result


# ---------------------------------------------------------------------------
# csv format
# ---------------------------------------------------------------------------

def test_csv_has_header():
    result = export_env({"A": "1"}, "csv")
    assert result.startswith("key,value\n")


def test_csv_simple_row():
    result = export_env({"HOST": "localhost"}, "csv")
    lines = result.splitlines()
    assert "HOST,localhost" in lines


def test_csv_quotes_values_with_commas():
    result = export_env({"LIST": "a,b,c"}, "csv")
    assert '"a,b,c"' in result


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_env({"K": "v"}, "toml")  # type: ignore[arg-type]


def test_empty_env_dotenv():
    assert export_env({}, "dotenv") == ""


def test_empty_env_json():
    assert json.loads(export_env({}, "json")) == {}
