# Núcleo de raciocínio investigativo VTB — matriz de hipóteses e achados

**Status:** implementação incremental na branch `feature/forensic-reasoning-matrix-v1`. Não confundir a análise metodológica pública com protocolos internos ou atribuição de métodos exclusivos a indivíduos.

## Proveniência pública da metodologia

1. **Lincoln Gakiya — Promotor de Justiça, Gaeco/MPSP.** Na 4ª reunião da CPI do Crime Organizado do Senado, em 25/11/2025, descreveu a reconstrução de estrutura organizacional e funções a partir de investigações e a relevância da cooperação e da qualificação técnica. Princípio adaptado à VTB: **cada relação deve indicar função, tempo, origem e confiabilidade do documento**. Técnicas invasivas ou dados sigilosos não são reproduzidos pela VTB.
   - Primária: https://www25.senado.leg.br/web/atividade/notas-taquigraficas/-/notas/r/14271
   - Sessão: https://legis.senado.leg.br/atividade/comissoes/comissao/2793/reuniao/14271
2. **Leandro Almada da Costa — diretor de inteligência da Polícia Federal (oitiva 2025).** Na mesma audiência, discutiu integração e qualificação das bases e ferramentas analíticas. Adaptação: interoperabilidade, fonte, versionamento, ausência de inferência a partir de fonte indisponível.
3. **MPF — investigação financeira.** Referência institucional à investigação de delitos econômicos, rastreamento financeiro e análise de tipologias; a VTB reconcilia exclusivamente dados públicos legitimamente acessíveis. Dados bancários sigilosos não podem ser simulados por informações de redes sociais.
   - https://www.mpf.mp.br/atuacao/ccr2/coordenacao/comissoes-e-grupos-de-trabalho/lavagem-de-dinheiro-e-crimes-fiscais
4. **TCU — Manual de Auditoria Operacional (4ª edição) e matriz de achados.** A estrutura `situação encontrada → critério → evidências → causas → efeitos → propostas de encaminhamento` orienta nosso modelo. Causa, efeito e autoria permanecem **não determinados** na ausência de documentação própria.
   - https://apoioauditoria.tcu.gov.br/normas-controle-externo/auditoria-operacional/
5. **CGU — Manual de Orientações Técnicas de Auditoria Interna.** Fontes suficientes, relevantes e confiáveis, matriz de planejamento, manifestação do auditado e controles de qualidade.
   - https://wiki.cgu.gov.br/index.php/Manual_de_Orienta%C3%A7%C3%B5es_T%C3%A9cnicas_da_Atividade_de_Auditoria_Interna_Governamental_do_Poder_Executivo_Federal
6. **Abraji — CruzaGrafos, metodologia e prevenção de homônimos.** Normalização de bases, resolução conservadora de entidade, identificação de fonte original e limitações de histórico.
   - https://cruzagrafos.abraji.org.br/conteudo/metodologia/
   - https://www.abraji.org.br/projetos/cruzagrafos

## Modelo de raciocínio aplicado

1. **Pergunta falsificável.** Que fato administrativo, período, órgão, valor e critério precisam ser demonstrados?
2. **Reconstrução documental.** IDs, ente, instrumento, versões, estágio financeiro, página, data, hash, órgão emissor e contexto.
3. **Hipóteses rivais.** Formular hipótese de regularidade e hipótese de possível inconformidade, ambas com critérios explícitos de refutação.
4. **Matriz ACH.** Para cada evidência real, declarar `SUPPORTS`, `REFUTES`, `NEUTRAL` ou `NOT_AVAILABLE`. Avaliação é anotação analítica, não constatação automática da verdade.
5. **Matriz de achados.** Registrar condição (descrição do documento), critério normativo verificado, evidência e localização, contraprovas, causas e efeitos **não determinados** quando não comprovados.
6. **Contraditório.** Buscar manifestação oficial e argumentos de regularidade; não tratar ausência de resposta como culpa.
7. **Proveniência e linhagem.** Espelhos não se tornam duas fontes independentes. Documentos devem ter integridade verificável.
8. **Red Team.** Testar: homônimos, valores e unidades, erro temporal, quadro funcional, escopo de consultoria, norma vigente, decisão superveniente, licitação por inexigibilidade, dano efetivo e nexo causal.
9. **Gate jurídico.** De irregularidade formal não se concluem dolo, improbidade, crime ou ressarcimento automático.
10. **Saída.** Dossiê verificável, contraditado e com pedidos de diligência proporcionais, jamais protocolo automático.

## API

`vtb.investigative_reasoning.reasoning_contract()` descreve os campos e limites.

`vtb.investigative_reasoning.audit_dossier(store, case_id, review)` lê um caso já armazenado no `CaseStore`, não navega na internet, e entrega matriz, status, hipóteses, lacunas, ações e relatório Markdown.

### Exemplo sem pessoas ou contratos reais

```json
{
  "criteria": {
    "CLAIM-1": {
      "criterion": "Comparar o objeto com a necessidade administrativa demonstrada",
      "source_url": "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm"
    }
  },
  "hypotheses": [
    {
      "hypothesis_id": "H-REG",
      "kind": "regular",
      "checks": [{"evidence_id": "EV-1", "assessment": "NEUTRAL"}]
    },
    {
      "hypothesis_id": "H-ALT",
      "kind": "irregularity",
      "checks": [{"evidence_id": "EV-1", "assessment": "NEUTRAL"}]
    }
  ]
}
```

Os IDs, `Claim`, `SourceRecord`, `EvidenceRecord` e `Hypothesis` precisam **existir previamente** no caso. Critérios declarados pelo usuário não substituem validação jurídica; as avaliações de hipóteses também precisam ser justificadas e conferidas no documento. Os estados da análise referem-se à **completude estrutural**: `QUARANTINED`, `INCONCLUSIVE` ou `READY_WITH_LIMITATIONS`. Não há estado de culpa nem autorização de divulgação.

### Campos de dossiê completo propostos

Escopo e método; cadeia de fontes; índice de peças; mapa de órgãos e funções; cronologia; contratação e aditivos; execução financeira por estágio; metodologia de preço; atribuições regimentais e quadro próprio; hipóteses regulares/alternativas; matriz de evidências favoráveis/contrárias; decisões e atos supervenientes; diligências pendentes; manifestação de responsáveis; parecer jurídico independente; danos efetivos demonstrados; competências institucionais; pedidos condicionais; anexos hashes e limitações.

## Escopo de autonomia

O motor realiza **checagem determinística**. Não infere intenção, não acessa sigilo bancário ou fiscal, não investiga pessoas de forma invasiva, não publica, não protocola. Um modelo de linguagem pode propor perguntas e leitura do material, mas a prova substantiva necessita conferência humana e do órgão competente. `README` e `docs/AUTONOMY-GROK.md` descrevem a conexão MCP.
