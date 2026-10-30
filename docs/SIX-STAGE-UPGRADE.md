# Tinker Bell — Seis melhorias de maturidade pericial (pacote de integração)

Data de criação: 2026-10-30. Local: PR de integração, não branch main até aprovação.
Objetivo: executar melhorias em uma cadeia auditável, sem substituir indícios por acusações.

## 1. Riscos de evidência e independência de fontes

- vtb/signals.py: publication_safe exige evidência previamente verificada e revisão humana; regra jurídica adicional se legal_validation_required. Sem argumentos permanece False.
- triage_band: evidências são contadas por documento/fonte de proveniência fornecida, não por ID textual. Sem provenance map não elevar a P1/P2 automaticamente.
- vtb/ensemble.py: mesma correção no agregador secundário.
- vtb/qa.py: revisão requer IDs explicitamente verificados para alegações críticas e sinais, não apenas valores de texto.
- tests/test_evidence_independence.py e tests/test_ensemble_lineage.py.
- Identificador de fonte não certifica autoria: valores fornecidos pelo operador devem ser verificados no original.

## 2. Integração das melhorias anteriores

PRs independentes #11–#15 foram copiados **para a branch integrada**, mantendo intacta a branch main:
- PNCP por CNPJ exato, paginação e estados de falha: vtb/pncp_watch.py, workflow agendado e testes.
- Pesquisa adaptativa: docs/ADAPTIVE-FORENSIC-RESEARCH.md.
- Revisão jurídica e contraditório: docs/LEGAL-ADVERSARIAL-REVIEW.md.
- Perícias por agente político: vtb/politician_cases.py e CLI politician-init.
- Rosie/Serenata e painel de gastos Jarbas local: vtb/serenata_screening.py e vtb/serenata_review.py.

O agendamento do GitHub só é ativado após merge na branch principal e habilitação do Actions. Não equivale a teste online da lista de CNPJs. Há tarefa separada de monitoramento no ChatGPT, que não substitui CI nem a reconciliação.

## 3. Fluxo de referência end-to-end (escopo real, conclusão limitada)

Foi conferido em resposta HTTP 200 do PNCP, em 30/10/2026, o registro:
https://pncp.gov.br/api/pncp/v1/orgaos/13120613000295/contratos/2026/2

- NumeroControlePNCP: 13120613000295-2-000002/2026.
- Órgão publicador: MUNICIPIO DE LARANJEIRAS.
- Assinatura: 2026-01-05.
- Valor inicial/global publicado: R$ 18.000.
- Fornecedor institucional no registro: CNPJ 01.061.616/0001-35.

**Esse registro não é uma suspeita nem demonstra pagamento, execução, dano ou irregularidade.** As duas últimas etapas requerem documentos independentes que este fluxo não obteve. O teste não reproduz operações bancárias nem prestações de contas.

Comando para conferir novamente e gerar o pacote local em ambiente com internet:

    python -m vtb.e2e_reference CASE-REF-PNCP --output-dir ./data/private/reference

Saída local: banco SQLite, case-export.json, forensic-report.json, validation.json,
source-summary.json e index.html. O fluxo foi testado com respostas PNCP gravadas como
fixtures sintéticas/equivalentes; a **consulta ao vivo do comando** ainda não foi feita em
ambiente de execução da Tinker Bell. A checagem ao vivo mencionada acima ocorreu por ferramenta
de navegação separada e não valida os arquivos gerados pelo código.

A conclusão do caso é INCONCLUSIVE sobre pagamentos e entregas. Não versionar o pacote local
de casos reais no GitHub público; o código e testes não incluem dados pessoais privados.

## 4. Validador jurídico-documental de relatórios

- vtb/report_validator.py implementa jsonschema Draft 2020-12 mais gates de ID de evidência,
fonte, saúde, qualidade, localizador, original presente e hash SHA-256 conferido para fatos
materiais. A validação não afirma que SHA garante autoria ou texto autêntico.
- Estados READY_WITH_LIMITATIONS requerem revisão humana, busca de contraprovas e revisão
jurídica declaradas, além de ao menos um fato material com evidência conferida.
- Um relatório DRAFT/INCONCLUSIVE pode passar estruturalmente sem prova de gasto, sem que isso
permita descrevê-lo como factual ou pronto para publicação.
- Saída de falhas lista códigos e mantém o estado QUARANTINED. Saída de sucesso é
VALIDATED_FOR_REVIEW, não uma homologação por autoridade pública.

Exemplo:

    python -m vtb.report_validator ./forensic-report.json --case-export ./case-export.json

Para análise de fatos como verificados, além do arquivo de caso, informar mapa de arquivos
originais por source_id (JSON) e documentar o processo de revisão. Sem os originais, não
validar como FACT e não publicar conclusões materialmente acusatórias.

## 5. Dashboard local de perícia

- vtb/case_dashboard.py renderiza HTML offline: linha de revisão, fontes, evidências, alegações,
status, hipóteses e grafo SVG de relações.
- Aresta DOCUMENTED sem evidence_ids resolvidos cai para candidata.
- Texto externo é escapado em HTML; URLs aceitam http(s) sem credenciais; sem JS remoto.
- Sem publicação em internet, autenticação de usuários ou acesso a arquivos externos.

Comando:

    python -m vtb.case_dashboard ./case-export.json --output ./index.html

Para grafo, usar --links ./relationships.json com from, to, relation, evidence_ids, status.
O grafo é uma visualização de associações fornecidas, não prova independente de vínculo.

## 6. Benchmark

- vtb/benchmark.py + tests/test_benchmark.py: 12 controles sintéticos equilibrados de
regras de triagem, incluindo CNPJ válido/inválido, status temporal, notas repetidas,
limite com/sem política, distância com/sem evidência de presença e preço com/sem amostra.
- Métricas TP/TN/FP/FN, precisão, recall e especificidade **somente sobre essas entradas
synthetic**. Elas NÃO representam taxa de falso positivo ou qualidade de perícia real.
- Execução:

    python -m vtb.benchmark --output ./benchmark-synthetic.json

Referências qualitativas oficiais, sem avaliação automática: arquivo
config/judicial_reference_cases.json, com quatro acórdãos/decisões STJ de resultados
jurídicos distintos e fonte oficial individual. Estão marcados como corpus NÃO
pontuado, sem revisão cega e sem originais integrais arquivados. Não converter
esse conjunto em taxa de sensibilidade/especificidade real.

**Benchmark externo ainda necessário:** corpus independente de decisões auditadas e atos regulares
comparáveis, revisão cega, várias esferas/anos, acesso a originais, amostra enviesada controlada
e relatório de incerteza. Decisão judicial não é rótulo automaticamente transferível a outro caso.

## Gates antes de integrar à main ou divulgar material sensível

- CI em Python 3.11 e 3.12: Ruff, compileall, pytest e smoke.
- Revisão humana de segurança, privacidade e eventuais conflitos entre PRs.
- Teste de recuperação dos endereços de API sem credenciais e com falhas 403/429/5xx.
- Inventário de originais e suas licenças; não incluir CPFs ou arquivos confidenciais.
- End-to-end real só é completo para materialidade financeira se existir reconciliação
contrato → empenho → liquidação → pagamento → entrega.
- Remediar o gatilho de P1 por ID duplicado e evitar atribuição de dolo automática.
- Nada de publicação/acusação/denúncia sem pedido expresso e revisão de evidências.

## Interpretação final

As seis frentes possuem implementação em código, porém o PR estar green prova apenas a suíte
exercitada; não basta para alegar sistema em produção, cobertura integral de qualquer político,
laudo equivalente à PF ou taxa de acerto geral. A versão final deve manter essas limitações
até que as validações reais sejam completas.
