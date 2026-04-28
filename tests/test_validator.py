"""Tests for envoy_sync.validator."""

import pytest

from envoy_sync.validator import ValidationResult, validate_env


# ---------------------------------------------------------------------------
# ValidationResult.is_valid / summary
# ---------------------------------------------------------------------------

def test_result_is_valid_when_empty():
    result = ValidationResult()
    assert result.is_valid is True


def test_result_is_invalid_with_bad_key():
    result = ValidationResult(invalid_keys=["123BAD"])
    assert result.is_valid is False


def test_summary_all_valid():
    result = ValidationResult()
    assert result.summary() == "All variables are valid."


def test_summary_lists_issues():
    result = ValidationResult(
        invalid_keys=["1BAD"],
        empty_value_keys=["EMPTY_KEY"],
    )
    summary = result.summary()
    assert "Invalid key names" in summary
    assert "1BAD" in summary
    assert "Empty values" in summary
    assert "EMPTY_KEY" in summary


# ---------------------------------------------------------------------------
# validate_env — key name rules
# ---------------------------------------------------------------------------

def test_valid_simple_keys():
    env = {"FOO": "bar", "BAZ_QUX": "1", "_PRIVATE": "secret"}
    result = validate_env(env)
    assert result.is_valid
    assert result.invalid_keys == []


def test_key_starting_with_digit_is_invalid():
    result = validate_env({"1INVALID": "value"})
    assert "1INVALID" in result.invalid_keys
    assert not result.is_valid


def test_key_with_hyphen_is_invalid():
    result = validate_env({"MY-KEY": "value"})
    assert "MY-KEY" in result.invalid_keys


def test_key_with_space_is_invalid():
    result = validate_env({"MY KEY": "value"})
    assert "MY KEY" in result.invalid_keys


def test_empty_key_string_is_invalid():
    result = validate_env({"": "value"})
    assert "" in result.invalid_keys


# ---------------------------------------------------------------------------
# validate_env — empty value rules
# ---------------------------------------------------------------------------

def test_empty_value_allowed_by_default():
    result = validate_env({"FOO": ""})
    assert result.is_valid
    assert result.empty_value_keys == []


def test_empty_value_reported_when_disallowed():
    result = validate_env({"FOO": ""}, allow_empty_values=False)
    assert "FOO" in result.empty_value_keys
    assert not result.is_valid


def test_non_empty_value_not_reported():
    result = validate_env({"FOO": "bar"}, allow_empty_values=False)
    assert result.empty_value_keys == []


# ---------------------------------------------------------------------------
# validate_env — mixed issues
# ---------------------------------------------------------------------------

def test_multiple_issues_reported_together():
    env = {"GOOD": "ok", "bad-key": "v", "EMPTY": ""}
    result = validate_env(env, allow_empty_values=False)
    assert "bad-key" in result.invalid_keys
    assert "EMPTY" in result.empty_value_keys
    assert "GOOD" not in result.invalid_keys


def test_validate_empty_mapping():
    result = validate_env({})
    assert result.is_valid
