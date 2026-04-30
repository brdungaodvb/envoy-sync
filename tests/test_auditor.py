"""Tests for envoy_sync.auditor."""
import pytest
from envoy_sync.auditor import AuditEntry, AuditLog


# ---------------------------------------------------------------------------
# AuditEntry round-trip
# ---------------------------------------------------------------------------

def test_entry_to_dict_round_trip():
    entry = AuditEntry(
        timestamp="2024-01-01T00:00:00Z",
        action="set",
        key="FOO",
        old_value=None,
        new_value="bar",
        note="initial",
    )
    assert AuditEntry.from_dict(entry.to_dict()) == entry


def test_entry_missing_note_defaults_to_empty():
    data = {"timestamp": "T", "action": "delete", "key": "X", "old_value": "v", "new_value": None}
    entry = AuditEntry.from_dict(data)
    assert entry.note == ""


# ---------------------------------------------------------------------------
# AuditLog.record_* helpers
# ---------------------------------------------------------------------------

def test_record_set_creates_set_action():
    log = AuditLog()
    log.record_set("API_KEY", None, "secret")
    assert log.entries[0].action == "set"
    assert log.entries[0].new_value == "secret"


def test_record_set_existing_key_uses_update_action():
    log = AuditLog()
    log.record_set("API_KEY", "old", "new")
    assert log.entries[0].action == "update"
    assert log.entries[0].old_value == "old"


def test_record_delete_stores_old_value():
    log = AuditLog()
    log.record_delete("DB_PASS", "hunter2", note="removing legacy key")
    e = log.entries[0]
    assert e.action == "delete"
    assert e.old_value == "hunter2"
    assert e.new_value is None
    assert "legacy" in e.note


def test_record_rename_encodes_keys():
    log = AuditLog()
    log.record_rename("OLD_NAME", "NEW_NAME", "value")
    assert log.entries[0].key == "OLD_NAME->NEW_NAME"


# ---------------------------------------------------------------------------
# AuditLog.replay
# ---------------------------------------------------------------------------

def test_replay_applies_set():
    log = AuditLog()
    log.record_set("FOO", None, "bar")
    result = log.replay({})
    assert result == {"FOO": "bar"}


def test_replay_applies_delete():
    log = AuditLog()
    log.record_delete("FOO", "bar")
    result = log.replay({"FOO": "bar", "KEEP": "yes"})
    assert "FOO" not in result
    assert result["KEEP"] == "yes"


def test_replay_applies_rename():
    log = AuditLog()
    log.record_rename("OLD", "NEW", "val")
    result = log.replay({"OLD": "val"})
    assert "OLD" not in result
    assert result["NEW"] == "val"


def test_replay_does_not_mutate_base():
    base = {"A": "1"}
    log = AuditLog()
    log.record_set("B", None, "2")
    log.replay(base)
    assert "B" not in base


def test_replay_sequential_operations():
    log = AuditLog()
    log.record_set("X", None, "initial")
    log.record_set("X", "initial", "updated")
    log.record_delete("X", "updated")
    result = log.replay({})
    assert "X" not in result


# ---------------------------------------------------------------------------
# AuditLog serialisation & summary
# ---------------------------------------------------------------------------

def test_audit_log_round_trip():
    log = AuditLog()
    log.record_set("K", None, "v", note="hello")
    restored = AuditLog.from_dict(log.to_dict())
    assert len(restored.entries) == 1
    assert restored.entries[0].note == "hello"


def test_summary_contains_action_and_key():
    log = AuditLog()
    log.record_set("MY_KEY", None, "val", note="reason")
    lines = log.summary()
    assert len(lines) == 1
    assert "MY_KEY" in lines[0]
    assert "reason" in lines[0]
