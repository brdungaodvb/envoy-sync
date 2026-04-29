"""Tests for envoy_sync.validator."""

from __future__ import annotations

import pytest

from envoy_sync.validator import (
    ValidationResult,
    validate_env,
    validate_lines,
)


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

def test_is_valid_when_no_issues():
    result = ValidationResult()
    assert result.is_valid is True


def test_is_invalid_when_invalid_keys():
    result = ValidationResult(invalid_keys=["123BAD"])
    assert result.is_valid is False


def test_summary_all_clear():
    assert validate_env({"FOO": "bar"}).summary() == "All checks passed."


def test_summary_contains_all_sections():
    result = ValidationResult(
        invalid_keys=["1BAD"],
        empty_value_keys=["EMPTY"],
        duplicate_keys=["DUP"],
    )
    summary = result.summary()
    assert "1BAD" in summary
    assert "EMPTY" in summary
    assert "DUP" in summary


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def test_valid_env_passes():
    result = validate_env({"DATABASE_URL": "postgres://localhost", "PORT": "5432"})
    assert result.is_valid


def test_invalid_key_detected():
    result = validate_env({"123NOPE": "value"})
    assert "123NOPE" in result.invalid_keys


def test_key_starting_with_hyphen_is_invalid():
    result = validate_env({"-KEY": "val"})
    assert "-KEY" in result.invalid_keys


def test_empty_value_flagged_by_default():
    result = validate_env({"SECRET": ""})
    assert "SECRET" in result.empty_value_keys


def test_empty_value_allowed_when_flag_set():
    result = validate_env({"SECRET": ""}, allow_empty_values=True)
    assert result.is_valid


def test_multiple_issues_reported():
    result = validate_env({"bad-key": "", "GOOD": "ok"})
    assert "bad-key" in result.invalid_keys
    assert "bad-key" in result.empty_value_keys
    assert "GOOD" not in result.invalid_keys


def test_underscore_and_mixed_case_key_valid():
    result = validate_env({"My_Var_123": "hello"})
    assert result.is_valid


# ---------------------------------------------------------------------------
# validate_lines
# ---------------------------------------------------------------------------

def test_no_duplicates():
    lines = ["FOO=1\n", "BAR=2\n"]
    result = validate_lines(lines)
    assert result.duplicate_keys == []


def test_duplicate_key_detected():
    lines = ["FOO=1\n", "BAR=2\n", "FOO=3\n"]
    result = validate_lines(lines)
    assert "FOO" in result.duplicate_keys


def test_comments_and_blanks_ignored():
    lines = ["# comment\n", "\n", "FOO=1\n"]
    result = validate_lines(lines)
    assert result.duplicate_keys == []


def test_duplicate_reported_once():
    lines = ["KEY=a\n", "KEY=b\n", "KEY=c\n"]
    result = validate_lines(lines)
    assert result.duplicate_keys.count("KEY") == 1
