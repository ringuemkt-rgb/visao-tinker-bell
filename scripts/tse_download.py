#!/usr/bin/env python3
"""
Visão Tinker Bell — Download de dados públicos do TSE
Fontes: https://dadosabertos.tse.jus.br / CDN estatística TSE
Registra hash SHA-256 (cadeia de custódia).
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("tse_download")

TSE_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"

# Padrões comuns (podem variar por ano — verificar no portal se falhar)
DATASETS = {
    "candidatos": TSE_CDN + "/consulta_cand/consulta_cand_{ano}.zip",
    "bens": TSE_CDN + "/bem_candidato/bem_candidato_{ano}.zip",
    "receitas": TSE_CDN + "/prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{ano}.zip",
}

HEADERS = {
    "User-Agent": "VisaoTinkerBell/0.2 (pesquisa-transparencia; evidence-only)",
    "Accept": "*/*",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> str:
    logger.info("GET %s", url)
    with requests.get(url, headers=HEADERS, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(65536):
                if chunk:
                    f.write(chunk)
    return sha256_file(dest)


def write_evidence(url: str, path: Path, digest: str, evidence_path: Path) -> None:
    text = (
        f"# Evidência — Visão Tinker Bell\n"
        f"source: {url}\n"
        f"file: {path.name}\n"
        f"access_date: {datetime.now(timezone.utc).isoformat()}\n"
        f"sha256: {digest}\n"
        f"size_bytes: {path.stat().st_size}\n"
    )
    evidence_path.write_text(text, encoding="utf-8")
    logger.info("Evidência: %s", evidence_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download TSE — Visão Tinker Bell")
    parser.add_argument("--ano", type=int, required=True, help="Ano da eleição (ex: 2024)")
    parser.add_argument(
        "--tipo",
        choices=list(DATASETS.keys()) + ["url"],
        required=True,
        help="Dataset ou 'url' com --url",
    )
    parser.add_argument("--url", help="URL direta (quando --tipo=url)")
    parser.add_argument("--outdir", default="data/raw/tse")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.tipo == "url":
        if not args.url:
            parser.error("--url é obrigatório com --tipo=url")
        url = args.url
        name = Path(args.url).name or f"tse_{args.ano}.zip"
    else:
        url = DATASETS[args.tipo].format(ano=args.ano)
        name = f"{args.tipo}_{args.ano}.zip"

    dest = outdir / name
    evidence = outdir / f"{dest.stem}.evidence.yaml"

    try:
        digest = download(url, dest)
        write_evidence(url, dest, digest, evidence)
        logger.info("OK %s sha256=%s...", dest, digest[:16])
    except requests.HTTPError as e:
        logger.error(
            "Falha HTTP %s. URLs do TSE mudam; confira em https://dadosabertos.tse.jus.br/ "
            "e use --tipo=url --url=...", e
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
