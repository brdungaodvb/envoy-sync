"""Compare two env snapshots and produce a structured change report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ChangeReport:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    modified: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def summary(self) -> str:
        lines = []
        if not self.has_changes:
            return "No changes detected."
        lines.append(f"{len(self.added)} added, {len(self.removed)} removed, {len(self.modified)} modified.")
        for key, val in sorted(self.added.items()):
            lines.append(f"  + {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"  - {key}={val}")
        for key, old, new in sorted(self.modified):
            lines.append(f"  ~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def compare_envs(
    before: Dict[str, str],
    after: Dict[str, str],
) -> ChangeReport:
    """Return a ChangeReport describing what changed from *before* to *after*."""
    report = ChangeReport()
    all_keys = set(before) | set(after)
    for key in all_keys:
        in_before = key in before
        in_after = key in after
        if in_before and in_after:
            if before[key] != after[key]:
                report.modified.append((key, before[key], after[key]))
            else:
                report.unchanged[key] = before[key]
        elif in_after:
            report.added[key] = after[key]
        else:
            report.removed[key] = before[key]
    return report
