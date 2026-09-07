#!/usr/bin/env python3
"""CLI de perícia pública — Visão Tinker Bell v7."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.pipeline import load_caso, run_pericia


def main() -> int:
    p = argparse.ArgumentParser(description="Perícia evidence-only a partir de um caso YAML/JSON")
    p.add_argument("--caso", required=True)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    caso_path = Path(args.caso)
    entity, contracts = load_caso(caso_path)
    result = run_pericia(entity, contracts)
    out = Path(args.out) if args.out else caso_path.parent / "dossie-gerado.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.dossier_markdown, encoding="utf-8")
    print(f"Dossiê gravado em {out}")
    print()
    print(result.ach_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
