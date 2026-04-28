"""CLI command for diffing two .env files or sources."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_sync.differ import diff_envs, has_differences, summary
from envoy_sync.parser import parse_env_file


def _load_env(path: str) -> dict[str, str]:
    """Load an env file from disk, exit with error if not found."""
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return parse_env_file(p.read_text())


def run_diff(argv: list[str] | None = None) -> int:
    """Entry point for the `envoy-sync diff` sub-command.

    Returns an exit code:
      0 — files are identical
      1 — differences found
      2 — usage / IO error
    """
    parser = argparse.ArgumentParser(
        prog="envoy-sync diff",
        description="Diff two .env files and report added, removed, or changed keys.",
    )
    parser.add_argument("left", help="Base .env file (left side of diff)")
    parser.add_argument("right", help="Target .env file (right side of diff)")
    parser.add_argument(
        "--only-changed",
        action="store_true",
        default=False,
        help="Only print keys whose values differ; suppress added/removed.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress output; exit code only.",
    )

    args = parser.parse_args(argv)

    left_env = _load_env(args.left)
    right_env = _load_env(args.right)

    result = diff_envs(left_env, right_env)

    if not args.quiet:
        if not args.only_changed:
            for key in sorted(result.only_in_left):
                print(f"- {key}={left_env[key]}")
            for key in sorted(result.only_in_right):
                print(f"+ {key}={right_env[key]}")
        for key in sorted(result.changed):
            old_val, new_val = result.changed[key]
            print(f"~ {key}: {old_val!r} -> {new_val!r}")

        print(summary(result))

    return 1 if has_differences(result) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run_diff())
