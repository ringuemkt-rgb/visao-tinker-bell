# Padrão de relatório pericial VTB

Este padrão transforma um dossiê investigativo em um contrato reutilizável. Ele não autoriza publicar dados pessoais, imputar ilícitos ou tratar score como probabilidade de culpa.

## Princípio de evidência

Todo relatório deve separar **fato**, **fato negativo dentro de escopo verificado**, **sinal**, **hipótese**, **lacuna** e **conclusão de publicação**. Uma fonte bloqueada, incompleta, desatualizada ou não exaustiva não sustenta uma afirmação negativa.

A linguagem recomendada é: “não demonstrado nas fontes e no escopo consultados”. Evite: “não existe”, “é inocente” ou “é culpado”, salvo quando a afirmação jurídica estiver ancorada em fonte oficial apropriada e for necessária ao escopo.

## Desambiguação obrigatória

Antes de cruzar dados, o relatório deve registrar candidatos de entidade e uma decisão para cada um: `MATCH_CONFIRMED`, `MATCH_CANDIDATE`, `MATCH_REJECTED` ou `UNRESOLVED`. Cada decisão deve citar evidências e explicar o motivo. Nome semelhante, cidade igual ou marca igual não são suficientes para unir entidades.

## Estrutura mínima

O schema em [`schemas/forensic_report.schema.json`](../schemas/forensic_report.schema.json) exige:

1. identificador, corte temporal e escopo;
2. metodologia e fontes;
3. ledger de resolução de entidades;
4. achados classificados;
5. hipóteses concorrentes e evidências pró/contra;
6. lacunas de evidência, fonte necessária e impacto;
7. limitações e status de publicação.

## Red team e hipóteses

A análise deve formular pelo menos uma hipótese de regularidade ou explicação legítima, além das hipóteses de irregularidade. Cada red flag precisa de uma explicação alternativa plausível e de um próximo teste que possa falsificá-la. A hipótese “menos refutada” não equivale a prova jurídica.

## Scores e watchlists

Scores como SAIS, bandas de triagem, centralidade, HHI, Benford e outliers devem ser descritos como **prioridade de revisão**. Watchlists devem ser passivas, com finalidade, prazo de retenção, revisão periódica e critério de remoção. Não devem gerar vigilância contínua ou ação adversa automática.

## Privacidade e publicação

Dados pessoais devem ser minimizados. O repositório de código deve conter templates e dados sintéticos, nunca um dossiê real identificável. Relatórios públicos devem aplicar revisão de finalidade, base legal, necessidade, proporcionalidade, direito de resposta quando aplicável e remoção de campos que não sejam necessários à verificação do achado.

## Decisão recomendada

Use `READY_WITH_LIMITATIONS` quando há achados documentados, mas existem lacunas relevantes. Use `INCONCLUSIVE` quando o conjunto não permite discriminar hipóteses. Use `QUARANTINED` quando gates de evidência, segurança, privacidade ou revisão não foram cumpridos.
