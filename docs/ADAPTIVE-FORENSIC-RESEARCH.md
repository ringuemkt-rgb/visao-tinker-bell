# Tinker Bell — Protocolo Adaptativo de Perícia v1.0

Inventário de ferramentas e fontes verificado em 2026-10-30. Documento operacional proposto, não prova de instalação ou de execução.

## Objetivo
Pesquisar, testar e aproveitar ferramentas open source apenas quando melhorarem a capacidade de obter ou avaliar evidências relevantes. A análise deve ser reprodutível, contestável, proporcional e limitada a dados de acesso legítimo. Não afirmar que uma varredura é exaustiva se fontes, períodos ou documentos faltarem.

Sinal estatístico não é infração; contrato não é pagamento; coincidência de nome não é identidade; participação política não é fluxo financeiro; indicador não é prova de crime. Nunca atribuir índice de corrupção, fraude ou culpa a pessoas. Avaliar cada hipótese por qualidade, suficiência e documentação.

## Estados obrigatórios das ferramentas
- CANDIDATE: encontrada em documentação ou repositório.
- ACCESSIBLE: código/documentação consultáveis.
- INSTALLED: software e dependências realmente instalados.
- SMOKE_TESTED: casos sintéticos reproduzidos e validados.
- SOURCE_VERIFIED: consulta real e documento primário confrontado.
- PRODUCTION_VALIDATED: avaliação de precisão, cobertura, segurança e monitoramento.
- DEGRADED/BLOCKED: falha, limitação de licença ou de acesso registrada.

Cada registro identifica versão/commit, licença, URLs, data, fonte, limites, teste, custo e opção substituta. Proibido afirmar que executou Qwen, OCR ou grafo quando a etapa foi apenas pesquisada.

## Catálogo de referência

| Camada | Solução candidata | Papel e limite |
|---|---|---|
| Extração | Docling https://github.com/docling-project/docling ; PaddleOCR https://github.com/PaddlePaddle/PaddleOCR ; ICIJ Datashare https://github.com/ICIJ/datashare | Texto, OCR, tabelas e páginas; conferir visualmente valores materiais |
| Acervo e busca | OpenAleph https://github.com/openaleph/openaleph ; Datashare | Ingestão de documentos e pesquisa, inclusive local |
| Entidades | FollowTheMoney https://github.com/opensanctions/followthemoney ; Splink https://github.com/moj-analytical-services/splink ; OpenRefine https://github.com/OpenRefine/OpenRefine | Relações documentadas e candidatos a correspondência; sem auto-merge de homônimos |
| Controle societário | BODS https://github.com/openownership/data-standard | Padrão de modelagem de beneficiário final, NÃO base pública de indivíduos |
| Relações | NetworkX https://github.com/networkx/networkx ; Neo4j https://github.com/neo4j/neo4j | Grafo temporal com documentos por aresta |
| Financeiro | DuckDB https://github.com/duckdb/duckdb ; Polars https://github.com/pola-rs/polars | Conciliar contrato, empenho, liquidação, pagamento e prestação de contas |
| Busca semântica | pgvector https://github.com/pgvector/pgvector ; BGE-M3 https://huggingface.co/BAAI/bge-m3 ; Qwen3 Embedding https://huggingface.co/Qwen/Qwen3-Embedding-0.6B ; Qwen3 Reranker https://huggingface.co/Qwen/Qwen3-Reranker-0.6B | Recuperar trechos, não certificar sua veracidade |
| IA especializada | Qwen3.5 9B https://huggingface.co/Qwen/Qwen3.5-9B ; Qwen3.8 27B https://huggingface.co/Qwen/Qwen3.8-27B ; GLiNER https://huggingface.co/urchade/gliner_multi-v2.1 ; PaddleOCR-VL 1.5 https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.5 | Extração, hipóteses e revisão sempre subordinadas às fontes |
| Agentes | LangGraph https://github.com/langchain-ai/langgraph | Estado, retomada e revisão humana |
| Contratações | OCDS Cardinal https://github.com/open-contracting/cardinal-rs ; metodologia OCP https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/ | Regras transparentes; guia contém 73 indicadores possíveis, NÃO 73 regras implantadas |
| Diários | Querido Diário https://github.com/okfn-brasil/querido-diario-api | Busca suplementar; consultar saúde, cobertura municipal e issue #113 |
| Proteção de PII | Presidio https://github.com/microsoft/presidio | Revisão/redação de cópias; originais preservados com acesso controlado |

Verificar licença de cada versão. Código FollowTheMoney (MIT) não transfere licença para dados OpenSanctions, cujas condições comerciais são próprias. Distribuição de derivados com a VTB AGPL-3.0-only precisa de avaliação de compatibilidade.

## Fontes brasileiras e prioridade probatória

1. Documento oficial original: contratos assinados, edital, publicação no diário, parecer, ata, ordem de pagamento, NF, relatório de execução e prestação de contas.
2. Registro estruturado oficial: chave única, emissor, documento vinculado e data de coleta.
3. Agregador, notícia ou dado secundário: somente pista, até revalidar em fonte primária.

Fontes:
- PNCP https://www.gov.br/pncp/pt-br/acesso-a-informacao/dados-abertos — contrato, compra, aditivo e artefatos.
- Transparência/CGU https://portaldatransparencia.gov.br/api-de-dados — CEIS, CNEP, CEPIM, convênios, contratos e despesas federais; API pode exigir credencial e possui limites.
- TSE https://dadosabertos.tse.jus.br/ — candidatura, bens DECLARADOS, financiamento e contas, com recorte por pleito.
- Tribunal de contas competente (TCM-BA, TCE-BA, TCU), diários oficiais, portal da Câmara, Executivo e e-SIC/LAI.
- Receita/Junta Comercial/RCPJ — confirmação de CNPJ, sócios e representantes por período.
- Órgão concedente de transferências culturais — processo, extratos permitidos, execução e contas.

## Ciclo de investigação: 12 gates

1. INTAKE — pergunta investigável, identidade, órgão, território, mandato, período, hipótese que pode ser refutada.
2. SOURCE MAP — matriz de todos os documentos indispensáveis, origem, cobertura e alternativa.
3. TOOLCHECK — consultar ferramentas existentes antes de adicionar bibliotecas; escolher menor conjunto funcional.
4. INGEST — obter legitimamente, preservar URL, dados originais, parâmetros, timestamp e SHA-256 REAL sobre os bytes.
5. PARSE — ler texto nativo; para digitalizados, OCR + verificação visual da página; revisar datas, moedas, casas decimais e identificadores.
6. RESOLVE — preferir identificadores exatos; sem eles, relacionar somente candidatos, nunca fusão automática de pessoas.
7. TIE-OUT — separar valor previsto, contratado, aditado, empenhado, liquidado, pago e produto entregue; comparar documentos de duas fontes sem somar fases.
8. GRAPH — toda relação contém papel, início/fim, URL, source_id, evidence_id, status documentado ou candidato.
9. DETECT — red flag com regra, população comparável, explicação alternativa, norma, lacuna e documento de teste.
10. ADVERSARIAL — buscar resultados que refutem irregularidade: execução lícita, cronologia, razão administrativa, erro de OCR, duplicação de bases, mudança de diretoria.
11. LEGAL/PRIVACY — competência, ato, obrigação, causalidade, período, proteção de dados de terceiros, contraditório e revisão humana.
12. REPORT/QA — números recontados, links inspecionados, afirmações suportadas em trecho localizado, saída com limites explícitos.

Gate forte de evidência material: original baixado + hash real calculado + trecho/página identificado + trecho realmente sustenta alegação + conferência por revisor. Uma cadeia SHA-256 preenchida manualmente não demonstra preservação.

## Resposta automática a obstáculos (não evasão)

| Problema | Procedimento | Conclusão proibida |
|---|---|---|
| 403, CAPTCHA ou necessidade de login | Não contornar; conferir docs, token oficial autorizado, alternativa pública e LAI | Tratar bloqueio como ocultação ou ausência de registros |
| HTTP 429 | Backoff, reduzir volume, obedecer quota ou utilizar dump oficial | Forçar endpoint indiscriminadamente |
| Timeout, 5xx, erro de JSON | Registrar falha, instante e filtros; consultar órgão de origem/diário | Transformar indisponibilidade em zero resultados |
| PNCP busca não encontra | Verificar paginação, fornecedor_ni e CNPJ exato; usar endpoint de detalhe; complementar com órgão/diário | Certidão de inexistência |
| Querido Diário indisponível | Consultar diário do próprio órgão, páginas oficiais e acervo preservado; referência https://github.com/okfn-brasil/querido-diario-api/issues/113 | Ausência de publicação |
| PDF com números mal extraídos | Usar parser estrutural, OCR controlado, conferir imagem, solicitar cópia pesquisável | Declarar centavos e nomes sem revisão |
| Pessoas homônimas | RCPJ/Junta/CNPJ, atas, poderes de representação, vigência e identifiers permitidos | Presumir mesma identidade |
| Contrato muito acima dos pares | Normalizar escopo, quantidade, tempo, unidade, serviços, localidade e desembolsos | Concluir superfaturamento por comparação simples |
| Portal municipal parcial | TCM/TCE, prestação de contas, e-SIC; registrar consulta de controle | Concluir que não houve pagamentos |
| Limitação de hardware | Regra SQL/lexical, parser leve, modelo menor ou serviço autorizado com licença adequada | Declarar IA maior executada se não foi |
| Limite de tempo/ferramenta | Concluir a rodada com cobertura, fonte, hipótese, falha, diligências e qual próximo insumo decidiria a questão | Prometer trabalho invisível ou resultado futuro sem tarefa/agendamento habilitado |

## Multiagentes (arquitetura proposta)

Supervisor (Qwen) distribui atividades separadas: coleta, documentos/OCR, entidade, conciliação financeira, revisão adversarial e qualidade jurídico-documental. Módulos compartilham objetos estruturados com case_id, tool_id, versão, status, query, source_id, evidence_id, URL, hash, trecho, data, hipótese, contraprova e cobertura. DuckDB realiza aritmética determinística; LangGraph apenas orquestra; o supervisor não inventa números. Duas IAs repetindo o mesmo trecho não são fontes independentes.

Nenhum agente pode realizar denúncia, publicar dossiês sensíveis, alterar contas ou divulgar dados pessoais sem autorização explícita e revisão adequada.

## Métricas para autoaperfeiçoamento

A cada caso registrar:
- cobertura das fontes necessárias (fonte x período x documento x status);
- taxa de fontes bloqueadas e procedimentos substitutos;
- acurácia de campos monetários e datas após conferência;
- precisão/recall de resolução de entidades em corpus rotulado;
- aderência trecho-alegação e origem verificada;
- taxa de falso positivo de red flags;
- proporção de despesas reconciliadas de empenho a pagamento;
- volume de hipóteses refutadas e revisão entre avaliadores;
- custo computacional e versões fixadas.

Comparar modelos no mesmo conjunto de documentos brasileiros, incluir casos regulares como controles negativos e só promover substituição se demonstrar melhora. Não confundir capacidade anunciada no README com sucesso de teste no caso.

## Resultado final padrão da perícia

- Identidade e cronologia.
- Matriz de evidências, vínculos, contratos e fases financeiras.
- Red flags e hipóteses concorrentes com contraprovas.
- Linhagem (source_id, evidence_id, URLs, hashes e páginas).
- Lista real de ferramentas executadas e falhas.
- Itens NÃO LOCALIZADOS somente com cobertura discriminada.
- Limitações e documentos de maior poder de confirmação/refutação.
- Viabilidade documental de solicitação por LAI ou encaminhamento a órgão competente; nunca nota pessoal de corrupção.

O fechamento deve preferir INCONCLUSIVE ou READY_WITH_LIMITATIONS quando faltarem documentos essenciais. Não há promessa de investigação ilimitada ou acesso a dados não públicos.

## Atualização do catálogo

Antes de cada perícia importante, verificar saúde do repositório VTB, disponibilidade dos conectores e, quando a lacuna justificar, pesquisar GitHub/Hugging Face novamente. Registrar decisões e testes reprodutíveis. Melhoria permanente de software deve entrar via PR independente para revisão; não equivale a atualização dos pesos ou capacidades do modelo conversacional.
