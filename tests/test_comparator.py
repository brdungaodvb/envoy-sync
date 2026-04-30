"""Tests for envoy_sync.comparator."""
import pytest
from envoy_sync.comparator import compare_envs, ChangeReport


def test_identical_envs_no_changes():
    env = {"FOO": "bar", "BAZ": "qux"}
    report = compare_envs(env, env.copy())
    assert not report.has_changes
    assert report.total_changes == 0
    assert report.unchanged == env


def test_added_key_detected():
    before = {"FOO": "1"}
    after = {"FOO": "1", "NEW": "2"}
    report = compare_envs(before, after)
    assert report.added == {"NEW": "2"}
    assert not report.removed
    assert not report.modified


def test_removed_key_detected():
    before = {"FOO": "1", "OLD": "x"}
    after = {"FOO": "1"}
    report = compare_envs(before, after)
    assert report.removed == {"OLD": "x"}
    assert not report.added
    assert not report.modified


def test_modified_key_detected():
    before = {"FOO": "old"}
    after = {"FOO": "new"}
    report = compare_envs(before, after)
    assert len(report.modified) == 1
    key, old, new = report.modified[0]
    assert key == "FOO"
    assert old == "old"
    assert new == "new"


def test_total_changes_counts_all_types():
    before = {"A": "1", "B": "2", "C": "3"}
    after = {"A": "9", "C": "3", "D": "4"}
    report = compare_envs(before, after)
    assert report.total_changes == 3  # A modified, B removed, D added


def test_summary_no_changes():
    env = {"X": "y"}
    report = compare_envs(env, env.copy())
    assert report.summary() == "No changes detected."


def test_summary_contains_change_counts():
    before = {"A": "1"}
    after = {"B": "2"}
    report = compare_envs(before, after)
    summary = report.summary()
    assert "1 added" in summary
    assert "1 removed" in summary
    assert "+ B=2" in summary
    assert "- A=1" in summary


def test_empty_before_all_added():
    after = {"X": "1", "Y": "2"}
    report = compare_envs({}, after)
    assert report.added == after
    assert not report.removed
    assert not report.modified


def test_empty_after_all_removed():
    before = {"X": "1", "Y": "2"}
    report = compare_envs(before, {})
    assert report.removed == before
    assert not report.added
    assert not report.modified
