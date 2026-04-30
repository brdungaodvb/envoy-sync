"""Profile an env dict: count keys, detect empty values, measure value lengths."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    total_keys: int
    empty_keys: List[str]
    long_value_keys: List[str]  # values exceeding max_value_len
    duplicate_values: Dict[str, List[str]]  # value -> list of keys sharing it
    stats: Dict[str, object] = field(default_factory=dict)

    def has_empty(self) -> bool:
        return len(self.empty_keys) > 0

    def has_long_values(self) -> bool:
        return len(self.long_value_keys) > 0

    def has_duplicate_values(self) -> bool:
        return len(self.duplicate_values) > 0

    def summary(self) -> str:
        lines = [
            f"Total keys     : {self.total_keys}",
            f"Empty values   : {len(self.empty_keys)}",
            f"Long values    : {len(self.long_value_keys)}",
            f"Duplicate vals : {len(self.duplicate_values)}",
        ]
        if self.empty_keys:
            lines.append("  Empty  -> " + ", ".join(self.empty_keys))
        if self.long_value_keys:
            lines.append("  Long   -> " + ", ".join(self.long_value_keys))
        for val, keys in self.duplicate_values.items():
            preview = val[:20] + "..." if len(val) > 20 else val
            lines.append(f"  Dup '{preview}' -> " + ", ".join(keys))
        return "\n".join(lines)


def profile_env(
    env: Dict[str, str],
    max_value_len: int = 200,
) -> ProfileResult:
    """Analyse *env* and return a :class:`ProfileResult`."""
    empty_keys: List[str] = []
    long_value_keys: List[str] = []
    value_index: Dict[str, List[str]] = {}

    for key, value in env.items():
        if value == "":
            empty_keys.append(key)
        if len(value) > max_value_len:
            long_value_keys.append(key)
        value_index.setdefault(value, []).append(key)

    duplicate_values = {
        val: keys for val, keys in value_index.items() if len(keys) > 1 and val != ""
    }

    avg_len = (
        sum(len(v) for v in env.values()) / len(env) if env else 0.0
    )

    return ProfileResult(
        total_keys=len(env),
        empty_keys=empty_keys,
        long_value_keys=long_value_keys,
        duplicate_values=duplicate_values,
        stats={"avg_value_length": round(avg_len, 2)},
    )
