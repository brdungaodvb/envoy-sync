"""Tests for envoy_sync.sorter."""

import pytest

from envoy_sync.sorter import SortBy, SortOrder, SortResult, sort_env


SAMPLE = {"ZEBRA": "last", "ALPHA": "first", "MIDDLE": "mid"}


def test_sort_by_key_asc_default():
    result = sort_env(SAMPLE)
    assert list(result.sorted_env.keys()) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_sort_by_key_desc():
    result = sort_env(SAMPLE, order=SortOrder.DESC)
    assert list(result.sorted_env.keys()) == ["ZEBRA", "MIDDLE", "ALPHA"]


def test_sort_by_value_asc():
    result = sort_env(SAMPLE, sort_by=SortBy.VALUE)
    assert list(result.sorted_env.keys()) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_sort_by_value_desc():
    result = sort_env(SAMPLE, order=SortOrder.DESC, sort_by=SortBy.VALUE)
    assert list(result.sorted_env.keys()) == ["ZEBRA", "MIDDLE", "ALPHA"]


def test_changed_is_true_when_order_differs():
    result = sort_env(SAMPLE)
    assert result.changed is True


def test_changed_is_false_when_already_sorted():
    already = {"ALPHA": "a", "BETA": "b", "GAMMA": "g"}
    result = sort_env(already)
    assert result.changed is False


def test_moved_keys_identifies_repositioned_keys():
    result = sort_env(SAMPLE)
    # ZEBRA moves from position 0 to 2; ALPHA moves from 1 to 0
    assert len(result.moved_keys) > 0


def test_empty_env_returns_empty():
    result = sort_env({})
    assert result.sorted_env == {}
    assert result.changed is False


def test_single_key_unchanged():
    env = {"ONLY": "one"}
    result = sort_env(env)
    assert result.sorted_env == {"ONLY": "one"}
    assert result.changed is False


def test_group_prefix_places_prefixed_keys_first():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy", "DB_PORT": "5432"}
    result = sort_env(env, group_prefix="DB_")
    keys = list(result.sorted_env.keys())
    assert keys[0] == "DB_HOST"
    assert keys[1] == "DB_PORT"
    assert keys[2] == "APP_NAME"


def test_group_prefix_desc_within_group():
    env = {"DB_HOST": "h", "DB_PORT": "p", "APP_NAME": "a"}
    result = sort_env(env, order=SortOrder.DESC, group_prefix="DB_")
    keys = list(result.sorted_env.keys())
    assert keys[0] == "DB_PORT"
    assert keys[1] == "DB_HOST"


def test_sort_result_preserves_original():
    env = {"Z": "z", "A": "a"}
    result = sort_env(env)
    assert list(result.original.keys()) == ["Z", "A"]
    assert list(result.sorted_env.keys()) == ["A", "Z"]
