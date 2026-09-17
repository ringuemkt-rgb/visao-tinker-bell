from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .models import MissionState
from .preservation import verify_manifest
from .runtime import CaseStore
from .source_health import classify_http_status, negative_result_label


def cmd_init(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    try:
        store.create_mission(args.case_id, args.title, args.question, args.geography, args.time_range)
        print(json.dumps(store.mission(args.case_id), ensure_ascii=False, indent=2))
    finally:
        store.close()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    try:
        print(json.dumps(store.mission(args.case_id), ensure_ascii=False, indent=2))
    finally:
        store.close()
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    try:
        store.set_state(args.case_id, MissionState(args.state))
        print(json.dumps(store.mission(args.case_id), ensure_ascii=False, indent=2))
    finally:
        store.close()
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    try:
        output = store.write_case_export(args.case_id, args.output)
        print(json.dumps({"case_id": args.case_id, "export": str(output)}, ensure_ascii=False, indent=2))
    finally:
        store.close()
    return 0


def cmd_verify_manifest(args: argparse.Namespace) -> int:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    valid, reasons = verify_manifest(manifest)
    print(json.dumps({"valid": valid, "reasons": reasons, "manifest": args.manifest}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


def cmd_health(args: argparse.Namespace) -> int:
    health = classify_http_status(args.http_status)
    print(json.dumps({"health": health, "negative_interpretation": negative_result_label(health)}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vtb", description=f"Visão Tinker Bell Supreme {__version__}")
    p.add_argument("--db", default="data/vtb.sqlite3")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("mission-init")
    init.add_argument("case_id"); init.add_argument("title"); init.add_argument("question")
    init.add_argument("--geography", default=""); init.add_argument("--time-range", default="")
    init.set_defaults(func=cmd_init)
    status = sub.add_parser("mission-status"); status.add_argument("case_id"); status.set_defaults(func=cmd_status)
    move = sub.add_parser("mission-transition", help="Advance only through an allowed state-machine transition")
    move.add_argument("case_id"); move.add_argument("state", choices=[state.value for state in MissionState]); move.set_defaults(func=cmd_transition)
    export = sub.add_parser("case-export", help="Export a reproducible JSON snapshot of a case")
    export.add_argument("case_id"); export.add_argument("output"); export.set_defaults(func=cmd_export)
    verify = sub.add_parser("manifest-verify", help="Verify an artifact against its SHA-256 manifest")
    verify.add_argument("manifest"); verify.set_defaults(func=cmd_verify_manifest)
    health = sub.add_parser("source-health"); health.add_argument("http_status", type=int); health.set_defaults(func=cmd_health)
    return p


def main() -> int:
    parser = build_parser(); args = parser.parse_args(); Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
