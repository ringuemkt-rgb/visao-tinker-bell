# Coleta HTML e ética — Visão Tinker Bell

## Ordem de preferência (obrigatória)

1. **API oficial** (PNCP, TSE Dados Abertos, Portal da Transparência, BrasilAPI, Câmara/Senado)
2. **Download bulk / dump oficial** com hash (`scripts/tse_download.py`)
3. **HTML público** via `lib/html_fetch.py` **somente** se não houver API

## Scrapling ([D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling))

- Dependência **opcional**: `pip install scrapling` (e extras de fetcher se necessário)
- Uso padrão: `Fetcher` (HTTP)
- `StealthyFetcher` **só** quando o portal público legítimo bloqueia com WAF/Cloudflare e o conteúdo é de interesse público
- **Proibido** neste projeto: contornar login, áreas autenticadas, sistemas privados ou termos que proíbem coleta

## robots.txt

- `fetch_public_html(..., respect_robots=True)` é o padrão
- Se `Disallow` para o user-agent da VTB, a função **não baixa** e retorna erro explícito
- Em dúvida, preferir canal oficial de dados abertos do órgão

## Cadeia de custódia

Todo HTML salvo deve gerar:

- arquivo `.html`
- arquivo `.evidence.yaml` com `source`, `access_date`, `sha256`, `engine`

Referenciar esses arquivos no apêndice do dossiê (`assets/dossie-template.md`).

## O que NÃO fazer

- Scraping massivo que degrade serviço público
- Ignorar rate limits / AutoThrottle
- Tratar HTML raspado como superior a API oficial
- Usar bypass stealth como padrão (é exceção documentada)

## Ativação no analista (Grok / skill)

Quando a perícia exigir página sem API:

1. Registrar que a API foi verificada e não existe / não cobre o dado
2. Chamar `lib.html_fetch.fetch_public_html` com `save_dir`
3. Extrair fatos objetivos do HTML
4. Anexar evidência no ACH / dossiê
