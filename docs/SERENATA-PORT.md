# Serenata de Amor → Tinker Bell — portabilidade de motores

Pesquisa de 30/10/2026. Código e ideias de referência: https://github.com/okfn-brasil/serenata-de-amor e https://github.com/okfn-brasil/serenata-toolbox. Ambos com licença MIT (Serenata: Copyright © 2017 Data Science Brigade; toolbox © 2016). A presente implementação é uma reescrita de conceitos, e não uma cópia literal do código.

## Diagnóstico de compatibilidade

Rosie é um sistema de classificadores de despesas e comprovantes, não um LLM autônomo. Seu núcleo (rosie/rosie/core/__init__.py) aplica classificadores ao conjunto de dados e exporta colunas de suspeitas. Jarbas é uma interface de inspeção, filtragem e consulta de notas e fornecedores. A documentação original relata execução periódica manual e redução de atualizações.

A stack original contém Django 2.1.7, Celery 4.2.1, SciPy 1.2.1, scikit-learn 0.20.2, Python/Node antigos e arquivos de dados específicos. Transplantar a stack integral para a VTB atual criaria conflitos, riscos de segurança e baixa portabilidade. Não copiar sem reengenharia e auditoria.

## Mapeamento dos classificadores

| Serenata (Rosie) | Tinker Bell nesta entrega | Limites |
|---|---|---|
| Core: dataset → classificadores → suspeitas | Módulo vtb/serenata_screening.py, RiskSignal, saída estruturada JSON | Dados fornecidos, sem acesso automático a fontes |
| InvalidCnpjCpfClassifier | Checksum CNPJ de fornecedores | CPF privado não é coletado; erro de checksum pode ser digitação |
| IrregularCompaniesClassifier | Situação cadastral comparada com data do gasto | Exige status histórico e evidência independente |
| MonthlySubquotaLimitClassifier | Soma mensal por ator/categoria com regra vigente documentada | Não portar limites CEAP antigos para outras jurisdições |
| MealPriceOutlierClassifier | Outlier robusto por mediana e desvio absoluto mediano, com grupo mínimo | Não foi portado o KMeans antigo; comparabilidade do objeto é requisito |
| TraveledSpeedsClassifier | Distância em datas iguais com contexto mínimo de localização e presença documentada | Não se infere deslocamento impossível ou presença física pela nota |
| ElectionExpensesClassifier | Natureza cadastral 409-0 como alerta para verificar adequação | Pode ser despesa legítima |
| Jarbas: filtros, notas e comparações de mesma data | Sinais com ID de origem, explicação, parâmetros e JSON para auditoria | Interface navegável e detalhes de nota pendentes |
| Serenata toolbox | Referenciada como arquitetura de aquisição de dados, sem instalação | Dados históricos podem estar defasados ou ter outras licenças |
| Publicação automática de suspeitas em redes | Não implantada | Exige revisão humana e autorização explícita |

A VTB acrescenta confronto de identificador de nota fiscal por CNPJ em registros diferentes: sinal que pode corresponder a parcelas, lançamentos duplicados, estorno ou erro, não dupla despesa comprovada.

## Uso

A função screen_expenses recebe lista de PublicExpense e políticas de QuotaPolicy. Cada registro exige expense_id, actor_id, issue_date, amount_brl e evidence_ids. Campos opcionais: supplier_cnpj, supplier_status, supplier_status_from, supplier_status_evidence_ids, supplier_legal_nature, subquota, peer_group, invoice_id, latitude, longitude, personal_presence_evidenced. Nenhum desses campos prova identidade pessoal sem verificação externa.

Execução local:

    python -m vtb.serenata_screening ./dados_privados.json --output ./relatorio_privado.json

Formato JSON sintético de entrada:

    {
      "expenses": [
        {
          "expense_id": "FICTICIO-001",
          "actor_id": "AGENTE-TESTE",
          "issue_date": "2026-06-10",
          "amount_brl": "150.00",
          "evidence_ids": ["EVIDENCIA-TESTE-01"],
          "supplier_cnpj": "11.222.333/0001-81",
          "subquota": "REFEICAO",
          "peer_group": "refeicao-mesma-especificacao"
        }
      ],
      "quota_policies": [
        {
          "category": "REFEICAO",
          "limit_brl": "100.00",
          "valid_from": "2026-01-01",
          "valid_to": "2026-12-31",
          "evidence_ids": ["NORMA-FICTICIA-01"]
        }
      ]
    }

Todos os dados do exemplo são fictícios. Não inserir dossiês reais, CPFs, documentos sensíveis ou endereços residenciais no repositório público. Um evidence_id no JSON não certifica que o original foi coletado; a validação de documentos pertence à trilha de evidências da VTB.

A saída registra: total de registros, sinais, parâmetros, alternativas lícitas, limitações, cobertura por regra, prioridade de auditoria e declaração expressa de que o dado foi fornecido pelo analista e não conferido em origem oficial.

## Garantias

- Rejeitar expense_id duplicado, em vez de inflar índices de frequência.
- Não afirmar que ausência de sinal equivale a legalidade.
- Não aplicar histórico cadastral retroativamente.
- Em regra mensal, nenhuma norma ou normas conflitantes significam NÃO APLICÁVEL.
- Usar Decimal para valores, evitar erros monetários de float.
- Comparar pares realmente similares, não preços de objetos diferentes.
- No mesmo dia, fornecedor distante não demonstra viagem de parlamentar.
- Documento fiscal repetido não é pagamento repetido sem reconciliação de liquidação/ordem bancária.
- Relações políticas, familiares e de vizinhança não são prova de controle oculto.
- Nunca automatizar imputação de corrupção ou denúncia/publicação.

## Interface Jarbas-like de revisão local

Além dos detectores, foi implementado um visualizador HTML local em vtb/serenata_review.py.
Ele agrupa alertas por método, descreve os fundamentos e permite navegar entre registros
de despesas de mesma data/pessoa, com conteúdo HTML escapado e sem publicar dados em servidor.
Este visualizador NÃO busca recibos, não certifica documentos e não é uma instância Django/Jarbas.

Execução:

    python -m vtb.serenata_review ./dados_privados.json --screening ./relatorio_privado.json --output ./revisao_privada.html

Se a opção --screening for omitida, os registros são reavaliados com as regras padrão.
Use um arquivo de saída local e privado. É proibido publicar a página contendo informações
de indivíduos sem revisão específica de privacidade e pertinência.

## Próximas etapas não entregues

1. Interface Jarbas-like para navegação por documento com autorização e privacidade.
2. Adaptadores documentados CEAP/CEAPS, órgãos municipais, CNPJ histórico e prestação de contas; schema e dados versionados.
3. Benchmark representativo de despesas brasileiras para recalibrar outlier e distância sem taxas falsas excessivas.
4. Migração de partes úteis da toolbox com validação de licenças, cobertura e séries.
5. Treinamento/inferência de modelos opcionais sobre corpus legal; não há LLM instalado ou executado neste PR.
6. Segurança e testes antes de qualquer publicação de interface de consulta.

## Referências da análise original

- https://github.com/okfn-brasil/serenata-de-amor/blob/main/README.md
- https://github.com/okfn-brasil/serenata-de-amor/blob/main/LICENSE
- https://github.com/okfn-brasil/serenata-de-amor/blob/main/rosie/README.md
- https://github.com/okfn-brasil/serenata-de-amor/blob/main/rosie/rosie/core/__init__.py
- https://github.com/okfn-brasil/serenata-de-amor/blob/main/rosie/rosie/chamber_of_deputies/settings.py
- https://github.com/okfn-brasil/serenata-de-amor/tree/main/rosie/rosie/chamber_of_deputies/classifiers
- https://github.com/okfn-brasil/serenata-de-amor/blob/main/jarbas/README.md
- https://github.com/okfn-brasil/serenata-toolbox/blob/main/LICENSE
