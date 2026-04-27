"""Diff utilities for comparing environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Result of comparing two env variable sets."""

    only_in_left: Dict[str, str] = field(default_factory=dict)
    only_in_right: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (left_val, right_val)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_left or self.only_in_right or self.changed)

    def summary(self) -> str:
        lines = []
        if not self.has_differences:
            return "No differences found."
        for key, val in sorted(self.only_in_left.items()):
            lines.append(f"- {key}={val}")
        for key, val in sorted(self.only_in_right.items()):
            lines.append(f"+ {key}={val}")
        for key, (left, right) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {left!r} -> {right!r}")
        return "\n".join(lines)


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        left: The base environment mapping.
        right: The target environment mapping to compare against.
        ignore_keys: Optional list of keys to exclude from comparison.

    Returns:
        A DiffResult describing the differences.
    """
    ignore = set(ignore_keys or [])
    all_keys = (set(left) | set(right)) - ignore

    result = DiffResult()
    for key in all_keys:
        in_left = key in left
        in_right = key in right
        if in_left and not in_right:
            result.only_in_left[key] = left[key]
        elif in_right and not in_left:
            result.only_in_right[key] = right[key]
        elif left[key] != right[key]:
            result.changed[key] = (left[key], right[key])
        else:
            result.unchanged[key] = left[key]

    return result
