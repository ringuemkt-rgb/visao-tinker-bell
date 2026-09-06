# Catálogo de Fontes de Dados — Visão Tinker Bell

Prioridade: fontes **oficiais e públicas**. Atualizar status de integração conforme o código evolui.

## Tier 1 — Críticas

| Fonte | URL base | Dados | Status no repo |
|-------|----------|-------|----------------|
| TSE Dados Abertos | https://dadosabertos.tse.jus.br | Candidatos, bens, doações, despesas | Script exemplo (`scripts/tse_download.py`) |
| Portal da Transparência | https://portaldatransparencia.gov.br | Gastos, convênios, sanções | Manual / a integrar |
| PNCP | https://pncp.gov.br | Contratos (Lei 14.133) | Placeholder em `lib/api_clients.py` |
| CEIS / CNEP / CEPIM | Portal Transparência → Sanções | Empresas inidôneas / sancionadas | A integrar |
| Receita CNPJ | dados.gov.br + BrasilAPI | QSA, situação, capital | BrasilAPI em `api_clients.py` |
| SICONFI | https://siconfi.tesouro.gov.br | Contas públicas | Não |
| DataJud | https://datajud.cnj.gov.br | Processos | Não |

## Tier 2 — Qualidade

- Querido Diário (OKBR): diários oficiais municipais
- Brasil.io: dados normalizados
- Portais estaduais (ex.: Bahia — transparência + TCM)

## Tier 3 — Internacionais (quando relevantes)

- OpenSanctions
- OCCRP Aleph
- ICIJ Offshore Leaks (consulta)

## Regras de uso

1. Registrar URL + data de coleta + hash quando houver arquivo.
2. Preferir download oficial a scraping agressivo.
3. Respeitar rate limits e termos de uso.
4. Não armazenar dado sensível (CPF completo de terceiros, etc.) além do necessário e público.
