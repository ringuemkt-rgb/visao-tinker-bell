#!/usr/bin/env python3
"""
Exemplo operacional — Visão Tinker Bell
Roda o motor de red flags com dados de exemplo (e opcionalmente consulta APIs públicas).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.red_flags_engine import load_engine


def main():
    print("=" * 60)
    print("Visão Tinker Bell — Motor de Red Flags (exemplo)")
    print("=" * 60)

    engine = load_engine()
    print(f"Regras carregadas: {len(engine.rules)}")

    contextos = [
        {
            "nome": "Contrato alto + empresa nova + capital baixo",
            "ctx": {
                "valorGlobal": 12_500_000,
                "data_inicio_atividade": "2025-02-01",
                "dataAssinatura": "2025-08-15",
                "capital_social": 5_000,
                "descricao_situacao_cadastral": "ATIVA",
            },
        },
        {
            "nome": "Candidato com salto patrimonial + sem bens anteriores",
            "ctx": {
                "totalDeBens": 0,
                "totalDeBens_atual": 3_200_000,
                "totalDeBens_anterior": 450_000,
            },
        },
        {
            "nome": "Empresa sancionada (simulado)",
            "ctx": {
                "count_ceis": 1,
                "count_cnep": 0,
                "valorGlobal": 800_000,
            },
        },
    ]

    for item in contextos:
        print(f"\n--- {item['nome']} ---")
        findings = engine.evaluate(item["ctx"])
        if not findings:
            print("  Nenhum sinal disparado.")
        for f in findings:
            print(f"  [{f.severidade.upper():5}] {f.nome}")
            print(f"         Fonte: {f.fonte}")

    print("\n" + "=" * 60)
    print("Para uso real: alimente o contexto com dados de")
    print("  - PNCP (contratos)")
    print("  - BrasilAPI / Receita (CNPJ + QSA)")
    print("  - Portal da Transparência (CEIS/CNEP)")
    print("  - TSE DivulgaCandContas (bens)")
    print("  - Câmara API (CEAP)")
    print("=" * 60)


if __name__ == "__main__":
    main()
