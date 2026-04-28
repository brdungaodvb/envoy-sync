"""Tests for envoy_sync.merger."""

import pytest

from envoy_sync.merger import MergeConflictError, MergeStrategy, merge_envs


A = ("a.env", {"FOO": "1", "BAR": "hello"})
B = ("b.env", {"FOO": "2", "BAZ": "world"})
C = ("c.env", {"BAR": "hello", "QUX": "42"})


def test_merge_empty_sources():
    assert merge_envs([]) == {}


def test_merge_single_source():
    result = merge_envs([A])
    assert result == {"FOO": "1", "BAR": "hello"}


def test_merge_last_strategy_wins():
    result = merge_envs([A, B], strategy=MergeStrategy.LAST)
    assert result["FOO"] == "2"   # B overrides A
    assert result["BAR"] == "hello"
    assert result["BAZ"] == "world"


def test_merge_first_strategy_wins():
    result = merge_envs([A, B], strategy=MergeStrategy.FIRST)
    assert result["FOO"] == "1"   # A keeps its value
    assert result["BAZ"] == "world"


def test_merge_error_strategy_raises_on_conflict():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_envs([A, B], strategy=MergeStrategy.ERROR)
    err = exc_info.value
    assert err.key == "FOO"
    assert any(v == "1" for _, v in err.sources)
    assert any(v == "2" for _, v in err.sources)


def test_merge_error_strategy_no_raise_when_same_value():
    # BAR appears in both A and C with identical values — should NOT raise
    result = merge_envs([A, C], strategy=MergeStrategy.ERROR)
    assert result["BAR"] == "hello"
    assert result["QUX"] == "42"


def test_merge_three_sources_last():
    extra = ("d.env", {"FOO": "99"})
    result = merge_envs([A, B, extra], strategy=MergeStrategy.LAST)
    assert result["FOO"] == "99"


def test_merge_three_sources_first():
    extra = ("d.env", {"FOO": "99"})
    result = merge_envs([A, B, extra], strategy=MergeStrategy.FIRST)
    assert result["FOO"] == "1"


def test_merge_conflict_error_message():
    with pytest.raises(MergeConflictError, match="FOO"):
        merge_envs([A, B], strategy=MergeStrategy.ERROR)


def test_merge_preserves_all_unique_keys():
    result = merge_envs([A, B, C])
    assert set(result.keys()) == {"FOO", "BAR", "BAZ", "QUX"}
