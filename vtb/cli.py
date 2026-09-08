from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .runtime import CaseStore
from .source_health import classify_http_status, negative_result_label


def cmd_init(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    store.create_mission(args.case_id, args.title, args.question, args.geography, args.time_range)
    print(json.dumps(store.mission(args.case_id), ensure_ascii=False, indent=2))
    store.close()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    print(json.dumps(store.mission(args.case_id), ensure_ascii=False, indent=2))
    store.close()
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    health = classify_http_status(args.http_status)
    print(json.dumps({"health": health, "negative_interpretation": negative_result_label(health)}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vtb", description=f"Visão Tinker Bell Supreme {__version__}")
    p.add_argument("--db", default="data/vtb.sqlite3")
    sub = p.add_subparsers(dest="command", required=True)

    init = sub.add_parser("mission-init")
    init.add_argument("case_id")
    init.add_argument("title")
    init.add_argument("question")
    init.add_argument("--geography", default="")
    init.add_argument("--time-range", default="")
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("mission-status")
    status.add_argument("case_id")
    status.set_defaults(func=cmd_status)

    health = sub.add_parser("source-health")
    health.add_argument("http_status", type=int)
    health.set_defaults(func=cmd_health)
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
