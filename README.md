# Visão Tinker Bell 🦊 — Supreme v8.0

**Runtime open-source de inteligência forense evidence-first para auditoria cívica, contratações públicas e investigação documental de interesse público no Brasil.**

> Encontrar não é provar. Correlação não é nexo. Red flag não é evidência. Fonte quebrada não é ausência.

## Objetivo

A VTB localiza e prioriza sinais objetivos em registros públicos, reconstrói fluxo financeiro e relacionamentos temporais, e preserva a cadeia de evidência. Ela é desenhada para responder: **o que os documentos demonstram, o que contradizem e qual evidência ainda falta?**

Nenhum detector retorna automaticamente `CORRUPTION`, `FRAUD`, `CARTEL`, `LARANJA` ou dolo. A saída padrão é `ANOMALY_FOR_VERIFICATION`, com método, evidence IDs, falso-positivo e explicações alternativas.

## Motores v8

- CaseStore SQLite + state machine;
- Claim Ledger + source lineage;
- Source Health + catálogo nacional de fontes;
- preservação SHA-256 + manifestos;
- ACH, falsificação, Contradiction/Red Team e Next-Best-Query;
- procurement, payment e money-flow forensics;
- corporate, electoral e asset forensics;
- price intelligence, HHI e Benford com applicability gate;
- evidence-backed graph + temporal graph;
- timeline forensics + document version drift;
- controle externo/judicial com estágio processual;
- watchlists como candidate match;
- coleta incremental/checkpoints;
- linkage probabilístico com human-review gate;
- Yente/OpenSanctions adapter como enrichment;
- Tool Registry/TOOLCHECK S0–S10;
- QA, Legal/Dolo e publication gates.

## Servidor MCP interoperável

O runtime inclui um servidor MCP para conexão com clientes de IA compatíveis. Instale com `pip install -e '.[mcp]'` e execute `VTB_DB=data/vtb.sqlite3 vtb-mcp`. O transporte padrão é `stdio`; para HTTP controlado, use `VTB_MCP_TRANSPORT=streamable-http` atrás de autenticação, TLS e autorização. As ferramentas expostas são documentadas em [`docs/MCP-SERVER.md`](docs/MCP-SERVER.md).

O plano de evolução dessas integrações está em [`docs/ROADMAP-MCP-INTELLIGENCE.md`](docs/ROADMAP-MCP-INTELLIGENCE.md). Componentes invasivos, execução arbitrária e coleta indiscriminada permanecem fora do núcleo.

Relatórios estruturados devem seguir [`docs/FORENSIC-REPORT-STANDARD.md`](docs/FORENSIC-REPORT-STANDARD.md) e o contrato [`schemas/forensic_report.schema.json`](schemas/forensic_report.schema.json). Dossiês reais com dados pessoais não devem ser versionados no repositório.

## Arquitetura

```text
Pergunta
 → Escopo + hipóteses concorrentes
 → Plano de fontes
 → Coleta incremental + source health
 → Preservação / hash / provenance
 → Entity resolution / linkage
 → Claim Ledger
 → Procurement / money / corporate / electoral
 → Timeline / graph / price / statistics
 → Controle externo / judicial
 → Contradição + falsificação + gaps
 → Red Team
 → Legal / Privacy / QA
 → READY | READY_WITH_LIMITATIONS | INCONCLUSIVE | QUARANTINED
```

## Cobertura Brasil

`config/sources_br_v8.yaml` mapeia PNCP, Compras.gov, Transparência, TCU, CGU, CEIS/CNEP/CEPIM, SICONFI, Transferegov, TSE, Câmara/Senado, DataJud/tribunais, Receita/CNPJ, diários oficiais, TCE/TCM, MPs, juntas comerciais, SINAPI/SICRO, FNDE/FNS/SIOPS/SIOPE e fontes derivadas de enrichment.

**Catálogo ≠ disponibilidade.** Toda missão mede a saúde da fonte; 403/timeout/5xx não viram `NOT_FOUND`.

## Backends opcionais verificados no catálogo

- **Aleph** — busca/navegação documental e de entidades;
- **Splink** — record linkage probabilístico escalável;
- **Timesketch** — timeline forense colaborativa;
- **Yente/OpenSanctions** — matching/enrichment de entidades;
- **Neo4j/Gephi/OpenRefine** — grafo e reconciliação quando aprovados no TOOLCHECK.

Repositório encontrado não significa ferramenta instalada ou operacional. O status S0–S10 é atualizado somente após teste real.

## Início rápido

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

vtb --db data/vtb.sqlite3 mission-init caso-001 "Auditoria" "Quais fatos as fontes públicas sustentam?"
vtb source-health 403
pytest
```

## Documentação central

- `SKILL.md`
- `docs/ANTI-CORRUPTION-ARCHITECTURE.md`
- `docs/FULL-CYCLE-INTELLIGENCE.md`
- `docs/DETECTION-CATALOG.md`
- `docs/BRAZIL-DATA-LAYERS.md`
- `docs/SOURCE-COVERAGE-v8.md`
- `docs/ENTITY-MATCHING.md`
- `docs/STATISTICAL-FORENSICS.md`
- `docs/METHODOLOGY.md`
- `docs/ROADMAP-v8.md`

## Regras invioláveis

1. Fonte primária primeiro.
2. Red flag/anomalia/score não é prova de crime.
3. Corroboração exige linhagens independentes.
4. Contratado ≠ empenhado ≠ liquidado ≠ pago.
5. Match nominal não fecha identidade.
6. Probabilistic linkage não faz auto-merge sensível.
7. Processo/cautelar/representação não equivalem a condenação.
8. Benford/HHI/outliers/grafos são triagem.
9. Contraprova e Red Team antes de conclusão sensível.
10. Revisão humana para imputações sensíveis.
11. Ferramenta só aparece como executada se realmente foi executada.
12. Scores são prioridade de revisão, nunca probabilidade de culpa.

## Licença

AGPL-3.0-only
