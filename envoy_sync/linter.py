"""Lint .env files for style and consistency issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LintResult:
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.warnings and not self.errors

    def summary(self) -> str:
        lines = []
        if self.is_clean:
            return "No lint issues found."
        for e in self.errors:
            lines.append(f"  [error]   {e}")
        for w in self.warnings:
            lines.append(f"  [warning] {w}")
        return "\n".join(lines)


def lint_env(env: Dict[str, str], raw_lines: List[str] | None = None) -> LintResult:
    """Lint an env dict (and optionally its raw source lines) for issues."""
    result = LintResult()

    seen_keys: Dict[str, int] = {}
    for lineno, line in enumerate(raw_lines or [], start=1):
        stripped = line.rstrip("\n")
        # Warn about trailing whitespace
        if stripped != stripped.rstrip():
            result.warnings.append(f"Line {lineno}: trailing whitespace detected.")
        # Warn about Windows-style CRLF
        if "\r" in stripped:
            result.warnings.append(f"Line {lineno}: Windows-style line ending (CRLF) detected.")
        # Skip blank lines and comments for key checks
        if not stripped or stripped.lstrip().startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in seen_keys:
                result.errors.append(
                    f"Duplicate key '{key}' on line {lineno} (first seen on line {seen_keys[key]})."
                )
            else:
                seen_keys[key] = lineno

    for key, value in env.items():
        # Warn about empty values
        if value == "":
            result.warnings.append(f"Key '{key}' has an empty value.")
        # Warn about keys that are not uppercase
        if key != key.upper():
            result.warnings.append(f"Key '{key}' is not uppercase.")
        # Error on keys with spaces
        if " " in key:
            result.errors.append(f"Key '{key}' contains a space character.")
        # Warn about very long values
        if len(value) > 512:
            result.warnings.append(f"Key '{key}' has a very long value (>{512} chars).")

    return result
