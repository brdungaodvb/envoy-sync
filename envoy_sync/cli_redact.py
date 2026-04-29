"""CLI command: redact sensitive values from an env file."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy_sync.exporter import export_env
from envoy_sync.parser import parse_env_file
from envoy_sync.redactor import REDACTED_PLACEHOLDER, redact_env


def run_redact(argv: Optional[List[str]] = None) -> int:
    """Parse arguments and run the redact command.

    Args:
        argv: Argument list to parse. Defaults to sys.argv if None.

    Returns:
        Exit code: 0 on success, 2 on input/file error.
    """
    parser = argparse.ArgumentParser(
        prog="envoy-sync redact",
        description="Print an env file with sensitive values redacted.",
    )
    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--format",
        choices=["dotenv", "json", "shell"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    parser.add_argument(
        "--placeholder",
        default=REDACTED_PLACEHOLDER,
        help="Replacement string for redacted values",
    )
    parser.add_argument(
        "--pattern",
        dest="patterns",
        action="append",
        metavar="REGEX",
        help="Extra regex pattern to mark keys as sensitive (repeatable)",
    )
    parser.add_argument(
        "--show-summary",
        action="store_true",
        help="Print a summary of redacted keys to stderr",
    )

    args = parser.parse_args(argv)

    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = redact_env(env, patterns=args.patterns or None, placeholder=args.placeholder)

    print(export_env(result.redacted, fmt=args.format), end="")

    if args.show_summary:
        _print_summary(result)

    return 0


def _print_summary(result) -> None:
    """Print a human-readable redaction summary to stderr.

    Args:
        result: The redaction result object containing redaction_count
                and redacted_keys.
    """
    if result.redaction_count == 0:
        print("No sensitive keys detected.", file=sys.stderr)
    else:
        print(
            f"Redacted {result.redaction_count} key(s): "
            + ", ".join(result.redacted_keys),
            file=sys.stderr,
        )


def main() -> None:  # pragma: no cover
    sys.exit(run_redact())


if __name__ == "__main__":  # pragma: no cover
    main()
