# Roadmap — Visão Tinker Bell v6

## Feito

- [x] Motor de red flags (regras determinísticas) — `lib/red_flags_engine.py` + `rules/red_flags.json`
- [x] Analytics (Benford, Z-score, HHI, structuring flags) — `lib/analytics.py`
- [x] Clientes mínimos (BrasilAPI CNPJ) — `lib/api_clients.py`
- [x] Entity resolution básica — `scripts/entity_resolution.py`
- [x] Graph export GraphML/GEXF — `scripts/graph_export.py`
- [x] TSE download com hash de evidência — `scripts/tse_download.py`
- [x] Exemplos executáveis — `scripts/run_red_flags_example.py`, `scripts/run_analytics_example.py`
- [x] Docs: methodology, tools-catalog, brazil-pipeline, ARCHITECTURE-v6, DATA-SOURCES, TECHNIQUES
- [x] Integração documentada Monitor de Gravata

## Sprint A (próximo)

- [ ] Expandir `rules/red_flags.json` (mais regras do Monitor)
- [ ] Cliente CEIS/CNEP (chave opcional Portal da Transparência)
- [ ] Cliente PNCP mais completo
- [ ] Seção ACH formal no `assets/dossie-template.md`

## Sprint B

- [ ] DuckDB para datasets TSE/PNCP
- [ ] Entity resolution com persistência
- [ ] Exemplo PyVis + métricas NetworkX

## Sprint C

- [ ] SICONFI / Querido Diário (piloto)
- [ ] NER opcional (BERTimbau)
- [ ] Dashboard mínimo

## Princípios que não mudam

Evidence-only · Multi-fonte · ACH · Sem playbook de crime · Mesma régua para todos.
