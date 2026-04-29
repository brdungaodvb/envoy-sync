"""CLI entry-point for the *validate* sub-command."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from envoy_sync.parser import parse_env_file
from envoy_sync.validator import validate_env, validate_lines


def run_validate(paths: List[str], *, allow_empty: bool = False) -> int:
    """Validate one or more .env files.

    Prints a per-file report and returns an exit code:

    * ``0`` — all files are valid.
    * ``1`` — at least one file has validation errors.

    Args:
        paths: File system paths to ``.env`` files.
        allow_empty: When *True*, empty values are not treated as errors.

    Returns:
        Integer exit code suitable for :func:`sys.exit`.
    """
    overall_ok = True

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            print(f"[ERROR] File not found: {path}", file=sys.stderr)
            overall_ok = False
            continue

        raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        dup_result = validate_lines(raw_lines)

        try:
            env = parse_env_file(str(path))
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Could not parse {path}: {exc}", file=sys.stderr)
            overall_ok = False
            continue

        val_result = validate_env(env, allow_empty_values=allow_empty)

        # Merge duplicate findings into the validation result
        val_result.duplicate_keys.extend(dup_result.duplicate_keys)

        if val_result.is_valid:
            print(f"[OK]    {path}")
        else:
            overall_ok = False
            print(f"[FAIL]  {path}")
            for line in val_result.summary().splitlines():
                print(f"        {line}")

    return 0 if overall_ok else 1


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(
        prog="envoy-validate",
        description="Validate .env file keys and values.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to validate")
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        default=False,
        help="Do not flag keys with empty values as errors.",
    )
    args = parser.parse_args(argv)
    sys.exit(run_validate(args.files, allow_empty=args.allow_empty))
