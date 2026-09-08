# VTB — ciclo completo de inteligência pública

A VTB implementa um ciclo de trabalho genérico e auditável:

```text
DIREÇÃO / PERGUNTA
  → PLANO DE COLETA
  → COLETA INCREMENTAL
  → PRESERVAÇÃO + HASH
  → NORMALIZAÇÃO
  → ENTITY RESOLUTION
  → CLAIM LEDGER
  → MONEY FLOW / PROCUREMENT / CORPORATE / ELECTORAL
  → GRAFO TEMPORAL
  → ANOMALIAS / PRICE / ESTATÍSTICA
  → HIPÓTESES CONCORRENTES
  → CONTRADIÇÃO / FALSIFICAÇÃO
  → RED TEAM
  → QA / LEGAL / PRIVACY GATES
  → DISSEMINAÇÃO PROPORCIONAL
```

Não é necessário atribuir esse fluxo a uma agência específica: direção, coleta, processamento, análise e disseminação são princípios amplamente usados em inteligência e investigação.

## Watchlists

Watchlists são listas de entidades de interesse público legitimamente definido. Um hit é `CANDIDATE_MATCH`, nunca identidade automática. Toda watchlist deve registrar finalidade pública e identificadores usados.

## Coleta incremental

Coletores devem manter cursor/checkpoint, hash do último conteúdo e parâmetros da consulta. Isso reduz reprocessamento e permite provar o que foi consultado em cada rodada.

## Linkage probabilístico

Splink e sistemas equivalentes podem ser acoplados como backend. O contrato VTB exige:

- manifest de modelo;
- campos usados;
- calibração documentada;
- revisão de falso match e missed match;
- nenhuma fusão automática de identidade sensível;
- revisão humana antes de consolidar entidade.

## Aleph

Aleph é um backend opcional para documentos e entidades. VTB não delega a ele a verdade probatória: resultados importados continuam sujeitos a provenance, source lineage e validação contra a fonte original.

## Timesketch

Timesketch pode ser usado como workspace colaborativo de timeline. O runtime canônico continua armazenando os eventos e evidence IDs de forma independente para evitar lock-in.
