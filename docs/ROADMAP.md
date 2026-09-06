# Roadmap — Visão Tinker Bell v6

## Feito

- [x] Motor de red flags (25 regras) — `lib/red_flags_engine.py` + `rules/red_flags.json`
- [x] Analytics (Benford, Z-score, HHI) — `lib/analytics.py`
- [x] BrasilAPI CNPJ + CEIS/CNEP — `lib/api_clients.py`
- [x] **PNCP completo** — `lib/pncp.py` + `scripts/pncp_fetch.py` + `docs/pncp.md`
- [x] Entity resolution — `scripts/entity_resolution.py`
- [x] Graph export GraphML/GEXF — `scripts/graph_export.py`
- [x] TSE download com hash — `scripts/tse_download.py`
- [x] Template dossiê + ACH — `assets/dossie-template.md`
- [x] Arquitetura v6 e catálogos de fontes/técnicas

## Sprint B (restante)

- [ ] DuckDB para datasets TSE/PNCP em lote
- [ ] Entity resolution com persistência
- [ ] Exemplo PyVis + métricas NetworkX
- [ ] Paginação completa + cache local PNCP

## Sprint C

- [ ] SICONFI / Querido Diário (piloto)
- [ ] NER opcional (BERTimbau)
- [ ] Dashboard mínimo

## Princípios

Evidence-only · Multi-fonte · ACH · Sem playbook de crime · Mesma régua para todos.
