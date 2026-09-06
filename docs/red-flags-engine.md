# Motor de Red Flags + CEIS/CNEP

## Regras

Arquivo: `rules/red_flags.json` (25 regras implementadas na v6 Sprint A).

Categorias: contratação, empresa, parlamentar, eleitoral.

## Engine

```bash
python -c "from lib.red_flags_engine import load_engine; e=load_engine(); print(len(e.rules))"
python scripts/run_red_flags_example.py
```

## CEIS / CNEP

```bash
export PORTAL_TRANSPARENCIA_KEY="sua-chave"
# Cadastro gratuito: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email

python -c "
from lib.api_clients import sancao_resumo, build_context_from_cnpj
from lib.red_flags_engine import load_engine
print(sancao_resumo('00000000000191'))  # exemplo — use CNPJ real de interesse público
ctx = build_context_from_cnpj('CNPJ', valor_contrato=15_000_000)
print(load_engine().evaluate(ctx))
"
```

Sem chave, `count_ceis`/`count_cnep` ficam 0 e a regra de sanção não dispara por falta de dados (não por “limpo”).

## ACH

Template obrigatório: `assets/dossie-template.md` seção 6.
