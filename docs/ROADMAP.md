# Roadmap — Visão Tinker Bell v6

## Feito

- [x] Motor de red flags (regras determinísticas) — `lib/red_flags_engine.py`
- [x] **25 red flags** em `rules/red_flags.json` (Sprint A)
- [x] Analytics (Benford, Z-score, HHI, structuring) — `lib/analytics.py`
- [x] Clientes BrasilAPI CNPJ + **CEIS/CNEP** — `lib/api_clients.py`
- [x] Entity resolution — `scripts/entity_resolution.py`
- [x] Graph export GraphML/GEXF — `scripts/graph_export.py`
- [x] TSE download com hash — `scripts/tse_download.py`
- [x] **Template de dossiê com ACH formal** — `assets/dossie-template.md`
- [x] Docs: ARCHITECTURE-v6, DATA-SOURCES, TECHNIQUES, methodology, tools-catalog, Monitor de Gravata

## Sprint B

- [ ] DuckDB para datasets TSE/PNCP
- [ ] Entity resolution com persistência
- [ ] Exemplo PyVis + métricas NetworkX
- [ ] Cliente PNCP busca/listagem mais completa

## Sprint C

- [ ] SICONFI / Querido Diário (piloto)
- [ ] NER opcional (BERTimbau)
- [ ] Dashboard mínimo

## Princípios que não mudam

Evidence-only · Multi-fonte · ACH · Sem playbook de crime · Mesma régua para todos.
