# Roadmap de inteligência interoperável do Tinker Bell

Este documento transforma as propostas do plano estratégico anexado em lotes implementáveis e controlados. O objetivo é aumentar a capacidade investigativa sem converter sinais em acusações, sem coletar dados de forma invasiva e sem incorporar componentes não auditados ao núcleo.

## Entregas incorporadas nesta atualização

O servidor MCP agora expõe o catálogo de red flags declarativas, a priorização de próximas consultas e a preservação passiva de conteúdo fornecido pelo cliente. A captura passiva registra URL, timestamp, SHA-256, tamanho, método e manifesto. Ela não navega na internet e não contorna bloqueios.

## Próximos lotes recomendados

### Lote 1 — Pacote de caso versionável

**Implementado nesta atualização:** `case-bundle` e `case_bundle` geram um pacote `vtb-case-bundle-v1` com `case.json`, manifesto SHA-256, tamanho dos arquivos e nota de governança. `case-bundle-verify` e `case_bundle_verify` detectam arquivos ausentes, adulteração e divergência de tamanho. O pacote pode ser versionado em Git para revisão por pares, Pull Requests e rollback. O Git é uma camada editorial e de revisão; a cadeia de custódia primária continua dependente de manifestos, hashes, armazenamento append-only e controles de acesso.

### Lote 2 — Interface investigativa

Construir uma interface separada para casos autorizados, exibindo grafo, timeline, evidência, fonte, timestamp, confiança, contradições e filtros. A interface deve evitar layouts que atribuam culpa visualmente. O backend MCP e o CaseStore permanecem como autoridade dos dados.

### Lote 3 — Matching e grafo persistente

Avaliar Splink para resolução de entidades e Apache AGE para persistência relacional-grafo. Cada match deve manter score, campos contribuintes, versão de configuração, hipótese de homônimo e revisão humana. Nenhum match sensível deve ser promovido automaticamente a identidade confirmada.

### Lote 4 — Proveniência de pipeline

Avaliar OpenLineage para registrar origem, transformação, modelo, versão de regra e dataset de cada resultado. OpenLineage deve complementar, não substituir, manifestos, hashes, auditoria e retenção.

### Lote 5 — Enriquecimento jurídico e documental

Avaliar NER e indexação documental para diários oficiais e processos quando houver base legal, licença e fonte verificável. Aleph deve ser tratado como referência histórica ou legado, pois não é recomendado como nova dependência sem plano de manutenção.

## Itens deliberadamente não incorporados

Não serão incorporados ao núcleo mecanismos de varredura indiscriminada de infraestrutura, deanonymização, exploração de redes, esteganografia, execução de comandos externos, destruição ou criptografia in-place, nem coleta automática de serviços como Shodan, Censys ou VirusTotal sem autorização, escopo, rate limit, política de retenção e revisão de privacidade.

A ausência de estrutura digital não prova que uma empresa seja fictícia. Metadados de PDF não provam autoria ou fraude. Uma ferramenta de OSINT só pode gerar evidência contextual e verificável, nunca uma conclusão automática.
