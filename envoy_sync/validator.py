"""Validation utilities for environment variable keys and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# POSIX-compliant env var name: letters, digits, underscores; must not start with digit
_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


@dataclass
class ValidationResult:
    """Holds the outcome of validating an env mapping."""

    invalid_keys: List[str] = field(default_factory=list)
    empty_value_keys: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (
            self.invalid_keys or self.empty_value_keys or self.duplicate_keys
        )

    def summary(self) -> str:
        lines: List[str] = []
        if self.invalid_keys:
            lines.append(
                f"Invalid key names ({len(self.invalid_keys)}): "
                + ", ".join(self.invalid_keys)
            )
        if self.empty_value_keys:
            lines.append(
                f"Empty values ({len(self.empty_value_keys)}): "
                + ", ".join(self.empty_value_keys)
            )
        if self.duplicate_keys:
            lines.append(
                f"Duplicate keys ({len(self.duplicate_keys)}): "
                + ", ".join(self.duplicate_keys)
            )
        return "\n".join(lines) if lines else "All variables are valid."


def validate_env(
    env: Dict[str, str],
    *,
    allow_empty_values: bool = True,
) -> ValidationResult:
    """Validate keys (and optionally values) of an env mapping.

    Args:
        env: Mapping of environment variable names to values.
        allow_empty_values: When *False*, keys whose value is an empty
            string are reported in ``empty_value_keys``.

    Returns:
        A :class:`ValidationResult` describing any issues found.
    """
    invalid_keys: List[str] = []
    empty_value_keys: List[str] = []
    seen: set[str] = set()
    duplicate_keys: List[str] = []

    for key, value in env.items():
        if key in seen:
            duplicate_keys.append(key)
        else:
            seen.add(key)

        if not _KEY_RE.match(key):
            invalid_keys.append(key)

        if not allow_empty_values and value == "":
            empty_value_keys.append(key)

    return ValidationResult(
        invalid_keys=invalid_keys,
        empty_value_keys=empty_value_keys,
        duplicate_keys=duplicate_keys,
    )
