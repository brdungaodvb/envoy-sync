"""CLI command: render a .env template against a context file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_sync.parser import parse_env_file, write_env_file
from envoy_sync.templater import render_template


def run_template(argv: list[str] | None = None) -> int:
    """Entry point for the *template* sub-command.

    Returns 0 on success, 1 when unresolved variables remain.
    """
    parser = argparse.ArgumentParser(
        prog="envoy-sync template",
        description="Render a .env template by substituting variable references.",
    )
    parser.add_argument("template", help="Path to the .env template file")
    parser.add_argument(
        "--context",
        metavar="FILE",
        help="Optional .env file supplying substitution values",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write rendered output to FILE instead of stdout",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any variables remain unresolved",
    )
    args = parser.parse_args(argv)

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"error: template file not found: {template_path}", file=sys.stderr)
        return 1

    template_env = parse_env_file(template_path)

    context: dict[str, str] = {}
    if args.context:
        ctx_path = Path(args.context)
        if not ctx_path.exists():
            print(f"error: context file not found: {ctx_path}", file=sys.stderr)
            return 1
        context = parse_env_file(ctx_path)

    result = render_template(template_env, context=context)

    if args.output:
        write_env_file(Path(args.output), result.rendered)
    else:
        for key, value in result.rendered.items():
            print(f"{key}={value}")

    if result.unresolved:
        print(
            f"warning: {len(result.unresolved)} unresolved variable(s): "
            + ", ".join(result.unresolved),
            file=sys.stderr,
        )
        if args.strict:
            return 1

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run_template())


if __name__ == "__main__":  # pragma: no cover
    main()
