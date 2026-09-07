# Visão Tinker Bell 🦊 — Supreme v8.0

**Runtime open-source de inteligência forense evidence-first para auditoria cívica e registros públicos brasileiros.**

> Encontrar não é provar. Correlação não é nexo. Red flag não é evidência. Fonte quebrada não é ausência.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Evidence First](https://img.shields.io/badge/Evidence--First-fail--closed-success.svg)](SKILL.md)
[![Architecture v8](https://img.shields.io/badge/Architecture-v8.0-blueviolet.svg)](docs/ARCHITECTURE-v8.md)

## O que mudou na v8

A v7 já possuía PNCP/APIs, analytics, ACH, evidência, PDF e pipeline. A v8 acrescenta uma camada de controle pericial que impede o sistema de transformar sinais em conclusões fortes sem cumprir protocolo.

- `vtb/runtime.py` — memória SQLite persistente por caso;
- `vtb/state_machine.py` — fluxo investigativo obrigatório;
- `vtb/claims.py` — Claim Ledger + independência de fontes;
- `vtb/source_health.py` — 403/timeout/5xx nunca viram NOT_FOUND;
- `vtb/hypotheses.py` — hipóteses concorrentes e falsificação;
- `vtb/next_best_query.py` — busca orientada por ganho de informação;
- `vtb/money_flow.py` — contratado ≠ empenhado ≠ liquidado ≠ pago;
- `vtb/entity_resolution.py` — bloqueio de fusão precipitada de homônimos/empresas;
- `vtb/legal.py` — Legal Validator + Dolo Gate estrutural;
- `vtb/red_team.py` — ataque obrigatório à conclusão dominante;
- `vtb/gates.py` — claims críticos sem prova são quarentenados;
- `vtb/tool_registry.py` — TOOLCHECK S0–S10;
- `schemas/` — contratos machine-readable;
- `.github/workflows/ci.yml` — testes em Python 3.11/3.12.

## Início rápido

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

vtb --db data/vtb.sqlite3 mission-init itubera-001 "Auditoria Ituberá" "Quais fatos os documentos públicos sustentam?" --geography "Ituberá, Bahia"
vtb --db data/vtb.sqlite3 mission-status itubera-001
vtb source-health 403
pytest
```

## Arquitetura

```text
Pergunta
  → Escopo
  → Entidades
  → Hipóteses concorrentes
  → Fontes primárias + source-health
  → Provenance / cadeia
  → Claim Ledger
  → Timeline / money flow / grafo
  → Contradição + falsificação
  → Evidence gaps + Next-Best-Query
  → Red Team
  → Legal/Privacy/QA gates
  → READY | READY_WITH_LIMITATIONS | INCONCLUSIVE | QUARANTINED
```

## Fontes brasileiras

O mapa inicial inclui PNCP, Compras.gov.br, Transparência, TCU, CGU, TCE/TCM, MPs, TSE/TRE, DataJud/tribunais, SICONFI, CEIS/CNEP/CEPIM, diários oficiais, portais municipais/estaduais e registros empresariais legitimamente públicos. **Disponibilidade é medida por execução; não presumida pelo catálogo.** Veja `docs/SOURCE-MAP-BRAZIL.md`.

## Ferramentas

O catálogo contém Trafilatura, PyMuPDF, OCRmyPDF, Docling, DuckDB, NetworkX, OpenRefine, SpiderFoot e Gephi como componentes candidatos/auxiliares. Eles não entram automaticamente como “operacionais”: passam por TOOLCHECK e modelos/extratores nunca substituem a fonte original.

## Regras invioláveis

1. Fonte primária primeiro.
2. Claim material deve ter provenance e status explícito.
3. Corroboração exige linhagens independentes.
4. Red flags/HHI/Benford/outliers/grafos são triagem, não prova de fraude.
5. Processo, representação ou cautelar não equivalem a condenação.
6. Valor contratado não equivale a valor pago.
7. Ausência em API só pode ser inferida em fonte saudável, escopo exaustivo e negativo explícito.
8. Contraprova e Red Team são obrigatórios antes de conclusão sensível.
9. Ferramenta só é marcada como executada se realmente executada.
10. Revisão humana é exigida para imputações sensíveis.

## Legado v7

`lib/` e `scripts/pericia_run.py` continuam presentes durante a migração. A v8 nasce em `vtb/` para permitir adoção progressiva sem quebrar o pipeline existente.

## Documentação

- [Arquitetura v8](docs/ARCHITECTURE-v8.md)
- [Metodologia](docs/METHODOLOGY.md)
- [Mapa de fontes Brasil](docs/SOURCE-MAP-BRAZIL.md)
- [Roadmap](docs/ROADMAP-v8.md)
- [Skill canônica](SKILL.md)
- [Segurança e uso responsável](SECURITY.md)

## Licença

AGPL-3.0-only
