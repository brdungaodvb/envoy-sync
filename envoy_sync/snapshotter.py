"""Snapshot and restore .env state for auditing and rollback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Snapshot:
    timestamp: str
    source: str
    env: Dict[str, str]
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "env": self.env,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            timestamp=data["timestamp"],
            source=data["source"],
            env=data["env"],
            note=data.get("note", ""),
        )


@dataclass
class SnapshotStore:
    snapshots: List[Snapshot] = field(default_factory=list)

    def add(self, snapshot: Snapshot) -> None:
        self.snapshots.append(snapshot)

    def latest(self) -> Optional[Snapshot]:
        return self.snapshots[-1] if self.snapshots else None

    def by_source(self, source: str) -> List[Snapshot]:
        return [s for s in self.snapshots if s.source == source]


def take_snapshot(
    env: Dict[str, str],
    source: str,
    note: str = "",
) -> Snapshot:
    """Create a new snapshot from the given env dict."""
    timestamp = datetime.now(timezone.utc).isoformat()
    return Snapshot(timestamp=timestamp, source=source, env=dict(env), note=note)


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    """Append a snapshot to a JSON-lines file."""
    path = Path(path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(snapshot.to_dict()) + "\n")


def load_snapshots(path: Path) -> SnapshotStore:
    """Load all snapshots from a JSON-lines file."""
    store = SnapshotStore()
    path = Path(path)
    if not path.exists():
        return store
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                store.add(Snapshot.from_dict(json.loads(line)))
    return store
