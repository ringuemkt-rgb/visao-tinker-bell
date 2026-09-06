# Integração PNCP — Visão Tinker Bell

**Portal Nacional de Contratações Públicas** (Lei 14.133/2021)

- API consulta (pública, sem chave): `https://pncp.gov.br/api/consulta`
- Swagger: https://pncp.gov.br/api/consulta/swagger-ui/index.html

## Módulo

`lib/pncp.py`

| Função | Uso |
|--------|-----|
| `consultar_contratacao(cnpj, ano, seq)` | Detalhe de uma compra |
| `listar_contratacoes_publicacao(de, ate, modalidade, pagina)` | Lista por data de publicação |
| `listar_contratos(de, ate, pagina, cnpj?)` | Contratos/empenhos |
| `extrair_contexto_red_flags(dict)` | Normaliza campos → motor de regras |
| `pipeline_contratacao_para_flags(...)` | PNCP + BrasilAPI + CEIS/CNEP → contexto completo |

## CLI

```bash
# Modalidades (6 = pregão eletrônico, 8 = dispensa, 9 = inexigibilidade)
python scripts/pncp_fetch.py modalidades

# Detalhe
python scripts/pncp_fetch.py contratacao --orgao 14195333000128 --ano 2024 --seq 11

# Publicações (datas YYYYMMDD)
python scripts/pncp_fetch.py publicacao --de 20250101 --ate 20250107 --modalidade 6

# Pipeline completo → red flags
python scripts/pncp_fetch.py flags --orgao CNPJ_ORGAO --ano 2024 --seq 1
```

CNPJ de exemplo Ituberá (prefeitura): `14.195.333/0001-28` → `14195333000128`.

## Fluxo recomendado na perícia

1. Localizar contratação no portal ou via `publicacao` / `contratos`.
2. Rodar `flags` para gerar sinais objetivos.
3. Cruzar fornecedor com CEIS/CNEP (`PORTAL_TRANSPARENCIA_KEY`).
4. Registrar URL + data + hash no dossiê (template ACH).

## Limitações

- Campos JSON variam entre tipos de instrumento; o extrator tenta várias chaves.
- Rate limit: use pausa entre páginas (`iter_contratacoes_publicacao`).
- API pode retornar 5xx intermitente — retry manual.
- Sem autenticação na API de **consulta**; a API de **integração** (envio) exige credencial de órgão e não é usada aqui.
