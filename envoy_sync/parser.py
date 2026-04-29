"""Parser for .env files — reads and writes key-value pairs."""

from pathlib import Path
from typing import Dict, Optional


def parse_env_file(filepath: str | Path) -> Dict[str, str]:
    """
    Parse a .env file and return a dict of key-value pairs.

    Supports:
    - KEY=VALUE
    - KEY="VALUE WITH SPACES"
    - KEY='VALUE WITH SPACES'
    - Inline comments (# ...)
    - Blank lines and full-line comments are skipped
    """
    env: Dict[str, str] = {}
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f".env file not found: {filepath}")

    with path.open("r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Skip blanks and full-line comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid syntax at line {line_number}: '{line}'"
                )

            key, _, value = line.partition("=")
            key = key.strip()

            if not key:
                raise ValueError(
                    f"Empty key at line {line_number}: '{line}'"
                )

            if not key.replace("_", "").isalnum() or key[0].isdigit():
                raise ValueError(
                    f"Invalid key name at line {line_number}: '{key}'"
                )

            # Strip inline comments (outside quotes)
            value = _strip_inline_comment(value.strip())
            # Strip surrounding quotes
            value = _unquote(value)

            env[key] = value

    return env


def write_env_file(filepath: str | Path, env: Dict[str, str]) -> None:
    """Write a dict of key-value pairs to a .env file."""
    path = Path(filepath)
    with path.open("w", encoding="utf-8") as f:
        for key, value in env.items():
            # Quote values that contain spaces or special chars
            if any(c in value for c in (" ", "\t", "#", "'", '"')):
                escaped = value.replace('"', '\\"')
                f.write(f'{key}="{escaped}"\n')
            else:
                f.write(f"{key}={value}\n")


def _strip_inline_comment(value: str) -> str:
    """Remove inline comment from an unquoted value."""
    if value and value[0] in ('"', "'"):
        return value  # quoted — leave as-is for _unquote
    if " #" in value:
        value = value[: value.index(" #")].rstrip()
    return value


def _unquote(value: str) -> str:
    """Strip matching surrounding quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
