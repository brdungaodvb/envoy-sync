"""Audit trail: record and replay changes made to env variable sets."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AuditEntry:
    timestamp: str
    action: str          # 'set', 'delete', 'rename'
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            timestamp=data["timestamp"],
            action=data["action"],
            key=data["key"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            note=data.get("note", ""),
        )


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def _now(self) -> str:
        return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def record_set(self, key: str, old_value: Optional[str], new_value: str, note: str = "") -> None:
        action = "set" if old_value is None else "update"
        self.entries.append(AuditEntry(self._now(), action, key, old_value, new_value, note))

    def record_delete(self, key: str, old_value: Optional[str], note: str = "") -> None:
        self.entries.append(AuditEntry(self._now(), "delete", key, old_value, None, note))

    def record_rename(self, old_key: str, new_key: str, value: str, note: str = "") -> None:
        self.entries.append(AuditEntry(self._now(), "rename", f"{old_key}->{new_key}", value, value, note))

    def replay(self, base: Dict[str, str]) -> Dict[str, str]:
        """Apply all recorded changes to *base* and return the result."""
        env = dict(base)
        for entry in self.entries:
            if entry.action in ("set", "update"):
                env[entry.key] = entry.new_value or ""
            elif entry.action == "delete":
                env.pop(entry.key, None)
            elif entry.action == "rename":
                old_key, _, new_key = entry.key.partition("->")
                if old_key in env:
                    env[new_key] = env.pop(old_key)
        return env

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        return cls(entries=[AuditEntry.from_dict(e) for e in data.get("entries", [])])

    def summary(self) -> List[str]:
        return [
            f"[{e.timestamp}] {e.action.upper():8s} {e.key}" + (f" — {e.note}" if e.note else "")
            for e in self.entries
        ]
