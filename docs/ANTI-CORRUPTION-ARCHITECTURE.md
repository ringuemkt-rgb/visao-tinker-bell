# VTB Anti-Corruption Architecture

A Visão Tinker Bell é um sistema de **triagem, reconstrução documental e priorização de auditoria**. Não é um classificador de culpa.

## Pergunta central

> Quais sinais objetivos em registros públicos justificam aprofundamento, quais documentos os sustentam e quais explicações alternativas permanecem plausíveis?

## Cinco planos de análise

1. **Contratação** — necessidade → procedimento → adjudicação → contrato → aditivos → fiscalização.
2. **Execução financeira** — empenho → liquidação → pagamento → nota/medição → entrega documentada.
3. **Rede econômica** — empresa → QSA → alterações → vínculos temporais → contratos → sanções/PEP como enriquecimento.
4. **Eleitoral/patrimonial** — candidaturas → bens declarados → contrapartes eleitorais → fornecedores públicos.
5. **Controle e justiça** — auditorias → cautelares → decisões → recursos → trânsito/situação final.

## Taxonomia de saída

`ANOMALY_FOR_VERIFICATION` é a saída padrão dos detectores. Para converter um sinal em claim material é necessário:

- resolver entidade;
- preservar a fonte;
- demonstrar temporalidade;
- buscar documento primário;
- testar explicações legítimas;
- buscar contraprova;
- aplicar Legal/Dolo Gate quando pertinente;
- passar Red Team e revisão humana.

## Grafo canônico

```text
PUBLIC_AGENT ─ACTED_ON→ PROCUREMENT ─AWARDED_TO→ COMPANY
     │                                      │
     ├─DECLARED→ ASSET                      ├─HAS_PARTNER→ PERSON
     ├─ELECTORAL_TX→ COUNTERPARTY           ├─RECEIVED→ PAYMENT
     └─SUBJECT_OF→ CONTROL_CASE             └─HAS_SANCTION→ SANCTION_RECORD
```

Toda aresta material exige `evidence_ids` e deve possuir janela temporal quando a relação não for permanente.

## Sinais que merecem busca, não acusação

- competição reduzida;
- concentração de fornecedor;
- emergência recorrente;
- recorrência de vencedor;
- valores próximos a limiar juridicamente validado;
- inconsistência contrato/empenho/liquidação/pagamento;
- duplicidade candidata de pagamento;
- atributos cadastrais compartilhados;
- sobreposição entre contraparte eleitoral e fornecedor público;
- variação patrimonial comparável que exige reconciliação;
- preços normalizados fora da faixa de comparáveis;
- nós de alta conectividade em grafo baseado em evidência;
- decisões/documentos contraditórios ou versões divergentes.

Nenhum item acima, isolado ou somado mecanicamente, prova corrupção, fraude, cartel, lavagem, interposição de pessoa ou dolo.
