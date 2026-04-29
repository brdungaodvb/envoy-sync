"""Merge multiple .env sources into a single resolved mapping."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple


class MergeStrategy(str, Enum):
    """How to resolve conflicts when the same key appears in multiple sources."""

    FIRST = "first"   # keep the value from the first source that defines the key
    LAST = "last"    # keep the value from the last source that defines the key
    ERROR = "error"  # raise an error on any conflict


class MergeConflictError(ValueError):
    """Raised when a key conflict is found and strategy is ERROR."""

    def __init__(self, key: str, sources: List[Tuple[str, str]]) -> None:
        self.key = key
        self.sources = sources
        detail = ", ".join(f"{name!r}={val!r}" for name, val in sources)
        super().__init__(f"Conflict for key {key!r}: {detail}")


def merge_envs(
    sources: List[Tuple[str, Dict[str, str]]],
    strategy: MergeStrategy = MergeStrategy.LAST,
) -> Dict[str, str]:
    """Merge a list of (name, env_dict) pairs into one dict.

    Parameters
    ----------
    sources:
        Ordered list of ``(source_name, mapping)`` tuples.
    strategy:
        Conflict resolution strategy (default: LAST wins).

    Returns
    -------
    dict
        Merged environment mapping.
    """
    if not sources:
        return {}

    # Track which source last set each key for conflict detection
    seen: Dict[str, Tuple[str, str]] = {}  # key -> (source_name, value)
    result: Dict[str, str] = {}

    for source_name, env in sources:
        for key, value in env.items():
            if key in seen:
                prev_name, prev_value = seen[key]
                if prev_value == value:
                    # Same value — not a real conflict
                    seen[key] = (source_name, value)
                    continue
                if strategy is MergeStrategy.ERROR:
                    raise MergeConflictError(
                        key,
                        [(prev_name, prev_value), (source_name, value)],
                    )
                if strategy is MergeStrategy.FIRST:
                    continue  # keep existing
                # LAST: fall through to overwrite
            seen[key] = (source_name, value)
            result[key] = value

    return result


def find_conflicts(
    sources: List[Tuple[str, Dict[str, str]]],
) -> Dict[str, List[Tuple[str, str]]]:
    """Return all keys that have differing values across sources.

    Parameters
    ----------
    sources:
        Ordered list of ``(source_name, mapping)`` tuples.

    Returns
    -------
    dict
        Mapping of conflicting key to a list of ``(source_name, value)`` pairs
        for every source that defines that key with a distinct value.
        Keys with identical values across all sources are omitted.
    """
    seen: Dict[str, List[Tuple[str, str]]] = {}  # key -> [(source_name, value), ...]

    for source_name, env in sources:
        for key, value in env.items():
            seen.setdefault(key, [])
            seen[key].append((source_name, value))

    return {
        key: entries
        for key, entries in seen.items()
        if len({v for _, v in entries}) > 1
    }
