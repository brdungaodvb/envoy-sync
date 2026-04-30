"""CLI entry point for the lint command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envoy_sync.parser import parse_env_file
from envoy_sync.linter import lint_env


def run_lint(paths: List[str], strict: bool = False) -> int:
    """Lint one or more .env files.

    Returns 0 if all files are clean (or only have warnings in non-strict mode),
    returns 1 if any errors are found (or any warnings in strict mode).
    """
    exit_code = 0

    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            print(f"[error] File not found: {path}", file=sys.stderr)
            exit_code = 1
            continue

        raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        env = parse_env_file(str(path))
        result = lint_env(env, raw_lines=raw_lines)

        if result.is_clean:
            print(f"{path}: OK")
        else:
            print(f"{path}:")
            print(result.summary())

        if result.errors:
            exit_code = 1
        elif strict and result.warnings:
            exit_code = 1

    return exit_code


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="envoy-lint",
        description="Lint .env files for style and consistency issues.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to lint")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as errors (exit 1 on any warning).",
    )
    args = parser.parse_args(argv)
    sys.exit(run_lint(args.files, strict=args.strict))


if __name__ == "__main__":  # pragma: no cover
    main()
