"""Tests for envoy_sync.resolver."""

import pytest

from envoy_sync.merger import MergeConflictError, MergeStrategy
from envoy_sync.resolver import resolve_files, resolve_with_overrides


@pytest.fixture()
def base_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP=myapp\nDEBUG=false\nSECRET=abc\n")
    return p


@pytest.fixture()
def override_env(tmp_path):
    p = tmp_path / ".env.local"
    p.write_text("DEBUG=true\nEXTRA=1\n")
    return p


def test_resolve_single_file(base_env):
    result = resolve_files([base_env])
    assert result == {"APP": "myapp", "DEBUG": "false", "SECRET": "abc"}


def test_resolve_two_files_last_wins(base_env, override_env):
    result = resolve_files([base_env, override_env], strategy=MergeStrategy.LAST)
    assert result["DEBUG"] == "true"
    assert result["APP"] == "myapp"
    assert result["EXTRA"] == "1"


def test_resolve_two_files_first_wins(base_env, override_env):
    result = resolve_files([base_env, override_env], strategy=MergeStrategy.FIRST)
    assert result["DEBUG"] == "false"  # base wins
    assert result["EXTRA"] == "1"     # only in override


def test_resolve_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing.env"):
        resolve_files([tmp_path / "missing.env"])


def test_resolve_empty_list():
    assert resolve_files([]) == {}


def test_resolve_with_overrides_no_override(base_env):
    result = resolve_with_overrides(base_env)
    assert result["SECRET"] == "abc"


def test_resolve_with_overrides_applies_override(base_env, override_env):
    result = resolve_with_overrides(base_env, override_env)
    assert result["DEBUG"] == "true"


def test_resolve_error_strategy_conflict(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=val1\n")
    b.write_text("KEY=val2\n")
    with pytest.raises(MergeConflictError):
        resolve_files([a, b], strategy=MergeStrategy.ERROR)
