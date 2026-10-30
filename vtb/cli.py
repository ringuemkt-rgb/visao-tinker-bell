from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .case_bundle import verify_case_bundle, write_case_bundle
from .models import Hypothesis, MissionState
from .politician_cases import OFFICE_ALIASES, build_politician_case
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


def cmd_bundle(args: argparse.Namespace) -> int:
    store = CaseStore(args.db)
    try:
        bundle = write_case_bundle(store, args.case_id, args.output)
        print(json.dumps({"case_id": args.case_id, "bundle": str(bundle)}, ensure_ascii=False, indent=2))
    finally:
        store.close()
    return 0


def cmd_bundle_verify(args: argparse.Namespace) -> int:
    valid, reasons = verify_case_bundle(args.bundle)
    print(json.dumps({"valid": valid, "reasons": reasons, "bundle": args.bundle}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


def cmd_verify_manifest(args: argparse.Namespace) -> int:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    valid, reasons = verify_manifest(manifest)
    print(json.dumps({"valid": valid, "reasons": reasons, "manifest": args.manifest}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


def cmd_health(args: argparse.Namespace) -> int:
    health = classify_http_status(args.http_status)
    print(json.dumps({"health": health, "negative_interpretation": negative_result_label(health)}, ensure_ascii=False))
    return 0


def cmd_politician_init(args: argparse.Namespace) -> int:
    """Open an evidence-empty political investigation without implying wrongdoing."""
    plan = build_politician_case(
        args.case_id,
        args.name,
        office=args.office,
        uf=args.uf,
        municipality=args.municipality,
        start_year=args.start_year,
        end_year=args.end_year,
    )
    path = Path(args.output)
    if path.exists():
        raise FileExistsError(f"Refusing to replace existing case plan: {path}")
    store = CaseStore(args.db)
    try:
        store.create_mission(
            args.case_id,
            f"Perícia documental — {plan['person']['name_provided']}",
            plan["report_template"]["scope"]["question"],
            plan["report_template"]["scope"]["jurisdiction"],
            plan["report_template"]["scope"]["time_range"],
        )
        for item in plan["report_template"]["hypotheses"]:
            store.add_hypothesis(args.case_id, Hypothesis(item["id"], item["statement"]))
    finally:
        store.close()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(plan, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({
        "case_id": args.case_id,
        "output": str(path),
        "identity": "UNRESOLVED",
        "coverage": "NOT_STARTED",
        "publication_status": "QUARANTINED",
    }, ensure_ascii=False))
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
    bundle = sub.add_parser("case-bundle", help="Create a Git-friendly case package with hash manifest")
    bundle.add_argument("case_id"); bundle.add_argument("output"); bundle.set_defaults(func=cmd_bundle)
    bundle_verify = sub.add_parser("case-bundle-verify", help="Verify a case package manifest")
    bundle_verify.add_argument("bundle"); bundle_verify.set_defaults(func=cmd_bundle_verify)
    verify = sub.add_parser("manifest-verify", help="Verify an artifact against its SHA-256 manifest")
    verify.add_argument("manifest"); verify.set_defaults(func=cmd_verify_manifest)
    health = sub.add_parser("source-health"); health.add_argument("http_status", type=int); health.set_defaults(func=cmd_health)
    politician = sub.add_parser(
        "politician-init", help="Create an evidence-empty, jurisdiction-aware political case plan"
    )
    politician.add_argument("case_id")
    politician.add_argument("name")
    politician.add_argument("--office", choices=sorted(OFFICE_ALIASES))
    politician.add_argument("--uf", help="Two-letter state code")
    politician.add_argument("--municipality")
    politician.add_argument("--start-year", type=int)
    politician.add_argument("--end-year", type=int)
    politician.add_argument("--output", required=True, help="Local JSON path; do not commit real-case data")
    politician.set_defaults(func=cmd_politician_init)
    return p


def main() -> int:
    parser = build_parser(); args = parser.parse_args(); Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
