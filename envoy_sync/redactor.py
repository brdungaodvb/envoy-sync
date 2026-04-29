"""Redact sensitive values from env dicts based on key patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api[_]?key",
    r"(?i)private[_]?key",
    r"(?i)auth",
    r"(?i)credential",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactionResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redacted_keys)


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def is_sensitive_key(
    key: str,
    patterns: Optional[List[str]] = None,
) -> bool:
    """Return True if the key matches any sensitive pattern."""
    compiled = _compile_patterns(patterns or DEFAULT_SENSITIVE_PATTERNS)
    return any(p.search(key) for p in compiled)


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> RedactionResult:
    """Return a RedactionResult with sensitive values replaced by placeholder."""
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if is_sensitive_key(key, patterns):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactionResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )
