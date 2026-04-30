"""Tests for envoy_sync.profiler."""
import pytest
from envoy_sync.profiler import profile_env, ProfileResult


def test_empty_env_returns_zero_totals():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.empty_keys == []
    assert result.long_value_keys == []
    assert result.duplicate_values == {}


def test_total_keys_counted_correctly():
    env = {"A": "1", "B": "2", "C": "3"}
    result = profile_env(env)
    assert result.total_keys == 3


def test_empty_values_detected():
    env = {"KEY": "", "OTHER": "value"}
    result = profile_env(env)
    assert "KEY" in result.empty_keys
    assert "OTHER" not in result.empty_keys
    assert result.has_empty() is True


def test_no_empty_values():
    env = {"A": "hello", "B": "world"}
    result = profile_env(env)
    assert result.has_empty() is False


def test_long_values_detected_with_default_threshold():
    long_val = "x" * 201
    env = {"LONG": long_val, "SHORT": "ok"}
    result = profile_env(env)
    assert "LONG" in result.long_value_keys
    assert "SHORT" not in result.long_value_keys
    assert result.has_long_values() is True


def test_long_values_custom_threshold():
    env = {"KEY": "hello"}
    result = profile_env(env, max_value_len=3)
    assert "KEY" in result.long_value_keys


def test_duplicate_values_detected():
    env = {"A": "same", "B": "same", "C": "unique"}
    result = profile_env(env)
    assert "same" in result.duplicate_values
    assert set(result.duplicate_values["same"]) == {"A", "B"}
    assert result.has_duplicate_values() is True


def test_empty_values_not_flagged_as_duplicates():
    env = {"A": "", "B": ""}
    result = profile_env(env)
    # both empty but empty strings should not appear in duplicate_values
    assert "" not in result.duplicate_values


def test_no_duplicate_values():
    env = {"A": "one", "B": "two"}
    result = profile_env(env)
    assert result.has_duplicate_values() is False


def test_stats_avg_value_length():
    env = {"A": "ab", "B": "abcd"}  # lengths 2 and 4, avg = 3.0
    result = profile_env(env)
    assert result.stats["avg_value_length"] == 3.0


def test_stats_avg_empty_env():
    result = profile_env({})
    assert result.stats["avg_value_length"] == 0.0


def test_summary_contains_total_keys():
    env = {"X": "val"}
    result = profile_env(env)
    assert "Total keys" in result.summary()
    assert "1" in result.summary()


def test_summary_lists_empty_keys():
    env = {"EMPTY_KEY": ""}
    result = profile_env(env)
    assert "EMPTY_KEY" in result.summary()
