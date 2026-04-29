"""Export environment variables to various output formats."""

from __future__ import annotations

import json
from typing import Dict, Literal

OutputFormat = Literal["dotenv", "json", "shell", "csv"]


def export_env(
    env: Dict[str, str],
    fmt: OutputFormat = "dotenv",
    *,
    sort_keys: bool = False,
) -> str:
    """Serialize *env* to the requested output format string.

    Supported formats:
      - ``dotenv``  – standard KEY=VALUE lines
      - ``json``    – pretty-printed JSON object
      - ``shell``   – ``export KEY=VALUE`` lines (bash-compatible)
      - ``csv``     – two-column CSV with header
    """
    if fmt not in ("dotenv", "json", "shell", "csv"):
        raise ValueError(f"Unsupported export format: {fmt!r}")

    items = sorted(env.items()) if sort_keys else list(env.items())

    if fmt == "json":
        return json.dumps(dict(items), indent=2)

    if fmt == "csv":
        lines = ["key,value"]
        for key, value in items:
            # Wrap fields that contain commas or quotes in double-quotes.
            safe_value = value.replace('"', '""')
            if "," in safe_value or '"' in safe_value or "\n" in safe_value:
                safe_value = f'"{safe_value}"'
            lines.append(f"{key},{safe_value}")
        return "\n".join(lines)

    if fmt == "shell":
        lines = []
        for key, value in items:
            escaped = value.replace("'", "'\"'\"'")
            lines.append(f"export {key}='{escaped}'")
        return "\n".join(lines)

    # Default: dotenv
    lines = []
    for key, value in items:
        # Quote values that contain whitespace or special characters.
        if any(ch in value for ch in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)
