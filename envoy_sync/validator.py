"""Validation utilities for environment variable keys and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


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
            lines.append(f"Invalid key names: {', '.join(self.invalid_keys)}")
        if self.empty_value_keys:
            lines.append(f"Empty values for keys: {', '.join(self.empty_value_keys)}")
        if self.duplicate_keys:
            lines.append(f"Duplicate keys detected: {', '.join(self.duplicate_keys)}")
        return "\n".join(lines) if lines else "All checks passed."


def validate_env(
    env: Dict[str, str],
    *,
    allow_empty_values: bool = False,
) -> ValidationResult:
    """Validate keys and values in an env mapping.

    Args:
        env: Mapping of environment variable names to values.
        allow_empty_values: When *False* (default), keys with empty string
            values are reported in :attr:`ValidationResult.empty_value_keys`.

    Returns:
        A :class:`ValidationResult` describing any issues found.
    """
    invalid_keys: List[str] = []
    empty_value_keys: List[str] = []

    for key, value in env.items():
        if not _VALID_KEY_RE.match(key):
            invalid_keys.append(key)
        if not allow_empty_values and value == "":
            empty_value_keys.append(key)

    return ValidationResult(
        invalid_keys=invalid_keys,
        empty_value_keys=empty_value_keys,
        duplicate_keys=[],  # dicts cannot have duplicates; see validate_lines
    )


def validate_lines(lines: List[str]) -> ValidationResult:
    """Detect duplicate keys in raw .env file lines before parsing.

    Only assignment lines (``KEY=value``) are inspected; comments and blank
    lines are ignored.

    Returns:
        A :class:`ValidationResult` with ``duplicate_keys`` populated.
    """
    seen: List[str] = []
    duplicates: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in seen and key not in duplicates:
                duplicates.append(key)
            seen.append(key)

    return ValidationResult(duplicate_keys=duplicates)
