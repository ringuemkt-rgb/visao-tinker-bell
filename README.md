# Visão Tinker Bell 🦊 v7.0

**Plataforma open-source de inteligência forense baseada em evidência pública.**  
Cruzamento de contratos, CNPJ, sanções, patrimônio declarado, grafos e ACH — **somente dados públicos**.

> Mostramos os números. Não presumimos a origem. Documentamos a cadeia.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Evidence-Only](https://img.shields.io/badge/Evidence-Only-green.svg)]()
[![Arch v7](https://img.shields.io/badge/Architecture-v7.0-blueviolet.svg)](docs/ARCHITECTURE-v7.md)
[![HF Card](https://img.shields.io/badge/HuggingFace-dataset%20card-yellow.svg)](huggingface/README.md)

Repositório operacional: https://github.com/ringuemkt-rgb/visao-tinker-bell

## O que a v7.0 adiciona

| Peça | Função |
|------|--------|
| `lib/pipeline.py` | Orquestrador: entidade → fontes → red flags → grafo → ACH → dossiê |
| `lib/ach.py` | Matriz Analysis of Competing Hypotheses (obrigatória) |
| `lib/evidence.py` | Cadeia de custódia (URL, data, SHA-256, tier) |
| `lib/pdf_extract.py` | Extração local de PDF (Docling → PyMuPDF → AIPDF opcional) |
| `scripts/pericia_run.py` | CLI de perícia reproduzível |
| `huggingface/` | Card para dataset/espaço de **processamento**, nunca evidência |

## Princípios invioláveis

1. Somente evidência pública e oficial.
2. Multi-fonte (≥ 2 fontes independentes para claims materiais).
3. Scores são sinais estatísticos, nunca sentença.
4. ACH antes de qualquer conclusão.
5. Cadeia de evidência reproduzível.
6. Zero playbook de crime.
7. Mesma régua para todos os partidos e cargos.

## Início rápido

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/run_red_flags_example.py
python scripts/pericia_run.py --caso cases/itubera-reges/caso.yaml
```

Chaves opcionais:

```bash
export PORTAL_TRANSPARENCIA_KEY="..."
export AIPDF_API_KEY="..."
```

## Pipeline estratégico

```
Escopo
  → Resolução de entidade
  → Coleta Tier 1 (TSE, PNCP, BrasilAPI, Transparência)
  → Fallback HTML ético
  → Extração de PDF local (Docling)
  → Red flags + analytics
  → Grafo pessoa–órgão–empresa–contrato
  → ACH (H0/H1/H2/H3)
  → Dossiê + apêndice
```

## Stack open-source

| Camada | Ferramentas |
|--------|-------------|
| Fontes BR | TSE, PNCP, Transparência, BrasilAPI, CEIS/CNEP |
| Regras | Monitor de Gravata adaptado + rules/red_flags.json |
| Grafos | NetworkX, GraphML, PyVis, Gephi |
| PDF local | Docling, PyMuPDF, AIPDF opcional |
| HTML | requests → Scrapling |
| Analytics | pandas, DuckDB |
| HF | NER/layout — nunca fato |

Arquitetura: [docs/ARCHITECTURE-v7.md](docs/ARCHITECTURE-v7.md)

## Hugging Face

Card em `huggingface/README.md`. Nenhum modelo HF é fonte de fato.

## Licença

AGPL-3.0
