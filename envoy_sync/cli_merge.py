"""CLI sub-command: merge multiple .env files and print or write the result."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from envoy_sync.merger import MergeConflictError, MergeStrategy
from envoy_sync.parser import write_env_file
from envoy_sync.resolver import resolve_files


def run_merge(
    input_paths: List[str],
    output_path: Optional[str] = None,
    strategy: str = "last",
    quiet: bool = False,
) -> int:
    """Entry-point for the ``merge`` sub-command.

    Parameters
    ----------
    input_paths:
        One or more source .env file paths (ordered).
    output_path:
        Destination file.  If *None*, the merged result is printed to stdout.
    strategy:
        One of ``first``, ``last``, or ``error``.
    quiet:
        Suppress informational messages.

    Returns
    -------
    int
        Exit code (0 = success, 1 = error).
    """
    try:
        merge_strategy = MergeStrategy(strategy)
    except ValueError:
        print(
            f"error: unknown strategy {strategy!r}. "
            "Choose from: first, last, error",
            file=sys.stderr,
        )
        return 1

    try:
        merged = resolve_files(input_paths, strategy=merge_strategy)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except MergeConflictError as exc:
        print(f"error: merge conflict — {exc}", file=sys.stderr)
        return 1

    if output_path is None:
        for key, value in sorted(merged.items()):
            print(f"{key}={value}")
    else:
        dest = Path(output_path)
        write_env_file(dest, merged)
        if not quiet:
            print(f"Merged {len(input_paths)} file(s) → {dest} ({len(merged)} keys)")

    return 0
