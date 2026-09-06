#!/usr/bin/env python3
"""
Visão Tinker Bell — Script de download e normalização básica de dados do TSE.
Uso: apenas dados públicos oficiais.
Não faz joins avançados nem scoring (veja outros scripts e a metodologia).
"""

import argparse
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Exemplo de estrutura. Em produção expandir com requests + zipfile + pandas
# Fontes oficiais: https://dadosabertos.tse.jus.br/

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Download e registro de evidência TSE (Visão Tinker Bell)")
    parser.add_argument("--ano", type=int, help="Ano da eleição (ex: 2022, 2024, 2026)")
    parser.add_argument("--tipo", choices=["candidatos", "bens", "receitas", "despesas"], default="bens")
    parser.add_argument("--outdir", default="data/raw/tse", help="Diretório de saída")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"[Visão Tinker Bell] Preparando download TSE — tipo={args.tipo} ano={args.ano}")
    print("Implementação completa deve usar as URLs oficiais do Portal de Dados Abertos do TSE.")
    print("Sempre registrar: URL, data de acesso, hash SHA-256 do arquivo baixado.")
    print("Exemplo de registro de evidência:")
    print(f"  access_date: {datetime.utcnow().isoformat()}Z")
    print("  source: https://dadosabertos.tse.jus.br/...")
    print("  sha256: <calcular após download>")

    # Placeholder — usuário deve completar com a lógica de download real
    # usando as APIs/dumps públicos documentados no portal do TSE.

if __name__ == "__main__":
    main()
