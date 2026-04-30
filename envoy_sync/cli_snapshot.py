"""CLI command: take or list snapshots of .env files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_sync.parser import parse_env_file
from envoy_sync.snapshotter import load_snapshots, save_snapshot, take_snapshot

_DEFAULT_STORE = Path(".envoy_snapshots.jsonl")


def run_snapshot(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy-snapshot",
        description="Snapshot .env files for auditing and rollback.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    take_p = sub.add_parser("take", help="Take a snapshot of one or more .env files")
    take_p.add_argument("files", nargs="+", metavar="FILE")
    take_p.add_argument("--note", default="", help="Optional note for this snapshot")
    take_p.add_argument(
        "--store", default=str(_DEFAULT_STORE), help="Snapshot store file"
    )

    list_p = sub.add_parser("list", help="List stored snapshots")
    list_p.add_argument(
        "--store", default=str(_DEFAULT_STORE), help="Snapshot store file"
    )
    list_p.add_argument("--source", default=None, help="Filter by source file name")

    args = parser.parse_args(argv)

    if args.cmd == "take":
        store_path = Path(args.store)
        for file_path in args.files:
            try:
                env = parse_env_file(Path(file_path))
            except FileNotFoundError:
                print(f"error: file not found: {file_path}", file=sys.stderr)
                return 1
            snap = take_snapshot(env, source=file_path, note=args.note)
            save_snapshot(snap, store_path)
            print(f"snapshot taken: {file_path} at {snap.timestamp}")
        return 0

    if args.cmd == "list":
        store = load_snapshots(Path(args.store))
        snaps = (
            store.by_source(args.source) if args.source else store.snapshots
        )
        if not snaps:
            print("no snapshots found.")
            return 0
        for snap in snaps:
            note_str = f"  [{snap.note}]" if snap.note else ""
            print(f"{snap.timestamp}  {snap.source}{note_str}")
        return 0

    return 1  # unreachable


def main() -> None:
    sys.exit(run_snapshot())


if __name__ == "__main__":
    main()
