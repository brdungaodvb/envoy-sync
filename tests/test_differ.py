"""Tests for envoy_sync.differ module."""

import pytest
from envoy_sync.differ import diff_envs, DiffResult


LEFT = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "DATABASE_URL": "postgres://localhost/dev",
    "SECRET_KEY": "abc123",
}

RIGHT = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DATABASE_URL": "postgres://prod-host/prod",
    "NEW_FEATURE_FLAG": "enabled",
}


def test_only_in_left():
    result = diff_envs(LEFT, RIGHT)
    assert "SECRET_KEY" in result.only_in_left
    assert result.only_in_left["SECRET_KEY"] == "abc123"


def test_only_in_right():
    result = diff_envs(LEFT, RIGHT)
    assert "NEW_FEATURE_FLAG" in result.only_in_right
    assert result.only_in_right["NEW_FEATURE_FLAG"] == "enabled"


def test_changed_values():
    result = diff_envs(LEFT, RIGHT)
    assert "DEBUG" in result.changed
    assert result.changed["DEBUG"] == ("true", "false")
    assert "DATABASE_URL" in result.changed


def test_unchanged_values():
    result = diff_envs(LEFT, RIGHT)
    assert "APP_NAME" in result.unchanged
    assert result.unchanged["APP_NAME"] == "myapp"


def test_has_differences_true():
    result = diff_envs(LEFT, RIGHT)
    assert result.has_differences is True


def test_has_differences_false():
    result = diff_envs({"A": "1"}, {"A": "1"})
    assert result.has_differences is False


def test_no_differences_summary():
    result = diff_envs({"X": "foo"}, {"X": "foo"})
    assert result.summary() == "No differences found."


def test_summary_contains_markers():
    result = diff_envs(LEFT, RIGHT)
    summary = result.summary()
    assert "- SECRET_KEY" in summary
    assert "+ NEW_FEATURE_FLAG" in summary
    assert "~ DEBUG" in summary


def test_ignore_keys():
    result = diff_envs(LEFT, RIGHT, ignore_keys=["DEBUG", "SECRET_KEY"])
    assert "DEBUG" not in result.changed
    assert "SECRET_KEY" not in result.only_in_left


def test_empty_dicts():
    result = diff_envs({}, {})
    assert not result.has_differences


def test_left_empty():
    result = diff_envs({}, {"A": "1"})
    assert "A" in result.only_in_right


def test_right_empty():
    result = diff_envs({"A": "1"}, {})
    assert "A" in result.only_in_left
