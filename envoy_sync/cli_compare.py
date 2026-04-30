"""CLI entry point for comparing two .env files."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy_sync.parser import parse_env_file
from envoy_sync.comparator import compare_envs


def _load_env(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return parse_env_file(fh.read())
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def run_compare(
    before_path: str,
    after_path: str,
    *,
    show_unchanged: bool = False,
    output: object = sys.stdout,
    err: object = sys.stderr,
) -> int:
    before = _load_env(before_path)
    after = _load_env(after_path)
    report = compare_envs(before, after)

    if not report.has_changes:
        print("No changes detected.", file=output)
        return 0

    print(report.summary(), file=output)

    if show_unchanged and report.unchanged:
        print(f"\n{len(report.unchanged)} unchanged key(s).", file=output)

    return 1


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="envoy-compare",
        description="Compare two .env files and show what changed.",
    )
    parser.add_argument("before", help="Original .env file")
    parser.add_argument("after", help="Updated .env file")
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Also report the count of unchanged keys.",
    )
    args = parser.parse_args(argv)
    sys.exit(run_compare(args.before, args.after, show_unchanged=args.show_unchanged))


if __name__ == "__main__":  # pragma: no cover
    main()
