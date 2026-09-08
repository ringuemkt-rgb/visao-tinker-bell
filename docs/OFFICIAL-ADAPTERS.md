# Adapters oficiais — VTB v8

Os adapters desta camada são **somente leitura**. Eles não fazem login em áreas restritas, não contornam CAPTCHA/WAF e não transformam erro de fonte em ausência de registro.

## PNCP

`vtb.adapters.pncp.PNCPAdapter`

Implementa endpoints de consulta documentados no Manual de Integração PNCP v2.6 para:

- contrato/empenho específico;
- documentos de contrato/empenho;
- contratos/empenhos vinculados a uma contratação;
- itens da contratação;
- histórico da contratação;
- histórico do contrato/empenho.

O adapter preserva CNPJ/ano/sequencial como identificadores da requisição. CNPJ é normalizado para 14 dígitos.

## Portal da Transparência

`vtb.adapters.transparency.PortalTransparenciaAdapter`

Implementa consultas read-only aos cadastros:

- CEIS;
- CNEP;
- CEPIM.

A chave da API é enviada apenas no header `chave-api-dados`. Ela não é registrada no `AdapterResult`, audit log ou metadata.

Uma ocorrência em CEIS/CNEP/CEPIM deve preservar escopo, datas, autoridade sancionadora e situação do registro; o sistema não extrapola o significado jurídico do cadastro.

## TSE Dados Abertos

`vtb.adapters.tse_open_data.TSEOpenDataAdapter`

O portal publica datasets anuais de candidatos com recursos como candidatos, informações complementares, bens, coligações, vagas e redes sociais. O adapter consulta o catálogo CKAN e utiliza **as URLs devolvidas pelo próprio catálogo**, em vez de inventar caminhos de CDN.

Um recurso baixado deve receber manifesto de dataset: URL, data de geração quando disponível, retrieved_at, SHA-256, tamanho, encoding, layout detectado e versão/schema interno de ingestão.

## Semântica comum

- `ok=False + BLOCKED/TIMEOUT/DEGRADED` → fonte indisponível/degradada; nunca `NOT_FOUND`;
- resposta vazia → `NO_RESULT_NO_ABSENCE_INFERENCE`, salvo consulta comprovadamente exaustiva em fonte saudável e com negativo explícito;
- mudança de schema deve falhar de forma observável e acionar fixture/regression test;
- todo adapter possui timeout finito;
- segredos nunca entram em metadata ou fixtures.
