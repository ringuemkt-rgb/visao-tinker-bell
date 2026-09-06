#!/usr/bin/env python3
"""
Visão Tinker Bell — CLI PNCP
Exemplos:
  python scripts/pncp_fetch.py contratacao --orgao 14195333000128 --ano 2024 --seq 11
  python scripts/pncp_fetch.py publicacao --de 20250101 --ate 20250115 --modalidade 6
  python scripts/pncp_fetch.py flags --orgao 14195333000128 --ano 2024 --seq 11
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.pncp import (
    MODALIDADES,
    consultar_contratacao,
    extrair_contexto_red_flags,
    listar_contratacoes_publicacao,
    listar_contratos,
    pipeline_contratacao_para_flags,
)
from lib.red_flags_engine import load_engine


def cmd_contratacao(args):
    data = consultar_contratacao(args.orgao, args.ano, args.seq)
    if not data:
        print("Não encontrado ou erro de API.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def cmd_publicacao(args):
    data = listar_contratacoes_publicacao(
        args.de, args.ate, args.modalidade, pagina=args.pagina
    )
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def cmd_contratos(args):
    data = listar_contratos(args.de, args.ate, pagina=args.pagina, cnpj=args.cnpj)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def cmd_flags(args):
    ctx = pipeline_contratacao_para_flags(
        args.orgao, args.ano, args.seq, enriquecer_fornecedor=not args.sem_enriquecer
    )
    if ctx.get("erro"):
        print(json.dumps(ctx, ensure_ascii=False, indent=2))
        sys.exit(1)
    engine = load_engine()
    findings = engine.evaluate(ctx)
    out = {
        "contexto_resumo": {
            k: ctx[k]
            for k in (
                "valorGlobal",
                "modalidadeId",
                "fornecedor_cnpj",
                "fornecedor_nome",
                "objeto",
                "count_ceis",
                "count_cnep",
                "capital_social",
                "data_inicio_atividade",
            )
            if k in ctx
        },
        "sinais": [
            {
                "id": f.rule_id,
                "nome": f.nome,
                "severidade": f.severidade,
                "categoria": f.categoria,
            }
            for f in findings
        ],
        "n_sinais": len(findings),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))


def cmd_modalidades(_args):
    for k, v in sorted(MODALIDADES.items()):
        print(f"{k:2d}  {v}")


def main():
    p = argparse.ArgumentParser(description="PNCP — Visão Tinker Bell")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("contratacao", help="Detalhe de uma compra")
    s1.add_argument("--orgao", required=True, help="CNPJ do órgão")
    s1.add_argument("--ano", type=int, required=True)
    s1.add_argument("--seq", type=int, required=True)
    s1.set_defaults(func=cmd_contratacao)

    s2 = sub.add_parser("publicacao", help="Listar contratações por publicação")
    s2.add_argument("--de", required=True, help="YYYYMMDD ou YYYY-MM-DD")
    s2.add_argument("--ate", required=True)
    s2.add_argument("--modalidade", type=int, required=True, help="código (6=pregão el.)")
    s2.add_argument("--pagina", type=int, default=1)
    s2.set_defaults(func=cmd_publicacao)

    s3 = sub.add_parser("contratos", help="Listar contratos por período")
    s3.add_argument("--de", required=True)
    s3.add_argument("--ate", required=True)
    s3.add_argument("--pagina", type=int, default=1)
    s3.add_argument("--cnpj", help="Filtrar por CNPJ órgão/fornecedor se API aceitar")
    s3.set_defaults(func=cmd_contratos)

    s4 = sub.add_parser("flags", help="PNCP + red flags (+ CNPJ/CEIS se possível)")
    s4.add_argument("--orgao", required=True)
    s4.add_argument("--ano", type=int, required=True)
    s4.add_argument("--seq", type=int, required=True)
    s4.add_argument("--sem-enriquecer", action="store_true")
    s4.set_defaults(func=cmd_flags)

    s5 = sub.add_parser("modalidades", help="Lista códigos de modalidade")
    s5.set_defaults(func=cmd_modalidades)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
