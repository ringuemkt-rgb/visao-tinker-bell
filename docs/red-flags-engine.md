# Motor de Red Flags — Visão Tinker Bell

Adaptado das regras públicas do **Monitor de Gravata** (https://github.com/steinhauserhzs/monitor-de-gravata).

## Como testar agora

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell
python -m venv .venv && source .venv/bin/activate
pip install requests
python scripts/run_red_flags_example.py
```

## Arquivos

- `rules/red_flags.json` — catálogo das regras adaptadas (10 regras prioritárias implementadas)
- `lib/red_flags_engine.py` — motor determinístico
- `lib/api_clients.py` — clientes mínimos (BrasilAPI CNPJ, PNCP)
- `scripts/run_red_flags_example.py` — exemplo executável

## Princípio

Red flags são **sinais objetivos**, não acusações. Cada finding traz a regra, severidade, fonte metodológica e evidência factual usada.

## Próximos passos

- Expandir as 81 regras do Monitor
- Conectar CEIS/CNEP (precisa chave Portal da Transparência)
- Pipeline completo: PNCP → CNPJ → regras → grafo → dossiê
