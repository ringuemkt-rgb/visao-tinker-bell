# Arquitetura — Visão Tinker Bell Supreme v8.0

## Objetivo
A v8 transforma a v7 de um pipeline analítico em um **runtime pericial reproduzível**. O sistema não tenta decidir culpa; ele controla evidência, hipóteses, lacunas e a qualidade do caminho até uma conclusão.

## Camadas

```text
CLI / relatórios
    ↓
TinkerBellEngine (orchestrator)
    ↓
State Machine ─ Claim Ledger ─ Hypotheses/ACH ─ Red Team ─ Gates
    ↓              ↓                 ↓              ↓
CaseStore       Provenance       Falsification   Publication decision
(SQLite)           ↓
              Sources/Evidence
    ↓
Adapters públicos + source-health
    ↓
PNCP / TCU / TCE / TCM / CGU / TSE / DataJud / transparência / diários / documentos
```

## Estados
INTAKE → SCOPE → PLAN → RESEARCH → INGEST → RESOLVE → ANALYZE → HYPOTHESIS → FALSIFY → GAP_ANALYSIS ↔ RESEARCH → RED_TEAM → SYNTHESIS → LEGAL_REVIEW → QA → DECISION → READY | READY_WITH_LIMITATIONS | INCONCLUSIVE | QUARANTINED.

## Regra de independência
Duas páginas que copiam a mesma fonte original compartilham a mesma linhagem e **não contam como duas corroborações independentes**.

## Source-health
Toda consulta deve distinguir saúde da fonte de conteúdo negativo. HTTP 403, timeout, DNS/connection error e 5xx bloqueiam inferência de ausência.

## Money flow
Estimated → Awarded → Contracted/Amended → Committed → Liquidated → Paid → Executed. Totais dessas fases não são somados como se fossem despesas distintas.

## Tool registry
Ferramenta localizada não é ferramenta operacional. S0–S10 registra descoberta, instalação, teste, limitações, degradação e bloqueio de governança.

## Segurança metodológica
- somente dados públicos/legitimamente acessíveis;
- sem credenciais, tokens ou segredos no audit log;
- sem atribuição automática de dolo;
- red flags são triagem;
- análise estatística é sinal, não prova;
- revisão humana para achados sensíveis.
