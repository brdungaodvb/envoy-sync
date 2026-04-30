"""CLI entry-point: envoy-audit — record and replay env changes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from envoy_sync.auditor import AuditLog
from envoy_sync.parser import parse_env_file, write_env_file


def _load_log(log_path: Path) -> AuditLog:
    if log_path.exists():
        return AuditLog.from_dict(json.loads(log_path.read_text()))
    return AuditLog()


def _save_log(log: AuditLog, log_path: Path) -> None:
    log_path.write_text(json.dumps(log.to_dict(), indent=2))


def run_audit(args: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="envoy-audit",
        description="Record and replay changes to .env files.",
    )
    parser.add_argument("--log", default=".envoy_audit.json", help="Path to audit log file.")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- record set ---
    p_set = sub.add_parser("set", help="Record a key=value change.")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.add_argument("--old", default=None, help="Previous value (if any).")
    p_set.add_argument("--note", default="")

    # --- record delete ---
    p_del = sub.add_parser("delete", help="Record deletion of a key.")
    p_del.add_argument("key")
    p_del.add_argument("--old", default=None)
    p_del.add_argument("--note", default="")

    # --- record rename ---
    p_ren = sub.add_parser("rename", help="Record a key rename.")
    p_ren.add_argument("old_key")
    p_ren.add_argument("new_key")
    p_ren.add_argument("value")
    p_ren.add_argument("--note", default="")

    # --- replay ---
    p_rep = sub.add_parser("replay", help="Apply recorded changes to an env file.")
    p_rep.add_argument("env_file", help="Base .env file to apply changes to.")
    p_rep.add_argument("--output", default=None, help="Output path (default: overwrite input).")

    # --- show ---
    sub.add_parser("show", help="Print the audit log summary.")

    ns = parser.parse_args(args)
    log_path = Path(ns.log)
    log = _load_log(log_path)

    if ns.command == "set":
        log.record_set(ns.key, ns.old, ns.value, note=ns.note)
        _save_log(log, log_path)
        print(f"Recorded SET {ns.key}")

    elif ns.command == "delete":
        log.record_delete(ns.key, ns.old, note=ns.note)
        _save_log(log, log_path)
        print(f"Recorded DELETE {ns.key}")

    elif ns.command == "rename":
        log.record_rename(ns.old_key, ns.new_key, ns.value, note=ns.note)
        _save_log(log, log_path)
        print(f"Recorded RENAME {ns.old_key} -> {ns.new_key}")

    elif ns.command == "replay":
        env_path = Path(ns.env_file)
        base = parse_env_file(env_path)
        result = log.replay(base)
        out_path = Path(ns.output) if ns.output else env_path
        write_env_file(result, out_path)
        print(f"Replayed {len(log.entries)} change(s) → {out_path}")

    elif ns.command == "show":
        lines = log.summary()
        if not lines:
            print("Audit log is empty.")
        else:
            print("\n".join(lines))

    return 0


def main() -> None:
    sys.exit(run_audit())


if __name__ == "__main__":
    main()
