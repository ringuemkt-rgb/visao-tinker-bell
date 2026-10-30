# Tinker Bell — Relatório nacional de perícia documental de agente político

Versão 1.0. Método de auditoria cívica sobre atos e recursos públicos, não laudo oficial da PF/Receita. Não pressupõe crime ou ilegalidade. Início por nome/cargo geográfico, sempre com desambiguação da identidade. Sem acesso próprio a sigilo fiscal, bancário, telemático ou aos relatórios RIF do Coaf.

## Fontes metodológicas públicas examinadas

- REDE-LAB/Ministério da Justiça: https://www.gov.br/mj/pt-br/assuntos/sua-protecao/lavagem-de-dinheiro/lab-ld — análises de grandes volumes, redes, ativos e beneficiários; as informações restritas pertencem às autoridades.
- Receita Federal/Malha Fiscal Digital: https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/declaracoes-e-demonstrativos/revisao-de-declaracao-malha/malha-fiscal-digital — divergências entre declarações, informações fiscais e terceiros.
- Coaf: https://www.gov.br/coaf/pt-br/acesso-a-informacao/Institucional/a-producao-de-inteligencia-financeira/analise-de-informacoes — triagem de risco e revisão aprofundada por analista; RIF é sigiloso.
- Alice/CGU: https://www.gov.br/cgu/pt-br/assuntos/auditoria-e-fiscalizacao/alice — coleta recorrente, cruzamentos, alertas e revisão por auditor.
- Orientação Prática da CGU: https://wiki.cgu.gov.br/wiki/Orienta%C3%A7%C3%A3o_Pr%C3%A1tica%3A_Relat%C3%B3rio_de_Auditoria — matriz de achados por critério, condição, evidência, causa, efeito e providência.

## 1. Contrato mínimo de dados por investigação

### Pessoas e entidades (identidades)
Campos: entity_id; nome conforme documento; tipo (pessoa, empresa, OSC, órgão, contrato); ID público validado; papel e mandato; início/fim do papel; source_id; status de identificação. 
- Nome coincidente, sobrenome, partido e cidade são apenas pistas.
- CPF completo, telefone privado, residência e dados sensíveis não entram no relatório.
- CNPJ da empresa, identificadores de contrato e atos públicos podem ser registrados quando necessários.

### Contratos e fluxo
Campos: contract_id; numero_controle_pncp; orgao_contratante; CNPJ fornecedor; objeto; data; vigência; valor_inicial; aditivos; empenhado; liquidado; pago; entrega_atestada; fonte; saúde da fonte; data da coleta.
- Separar sempre os estágios. Valor global de projeto, rubrica e pagamento NÃO devem ser somados como quantias distintas.
- Valor desconhecido é DESCONHECIDO, não zero.
- Instrumentos de fomento e OSC exigem plano de trabalho e prestação de contas próprios.

### Livro de vínculos (grafo)
Cada aresta: edge_id; origem; destino; tipo; papel/descrição; de_até; source_id; evidence_id; localizador exato (página/ato); status; explicação alternativa.
Tipos exemplares: mandato; presidência da Câmara; assinatura; representação de associação; sócio registrado; vencedor de licitação; fornecedor; ordem de pagamento; relação política noticiada; hipótese de controle oculto.
Estados: DOCUMENTED, CANDIDATE, REFUTED ou UNKNOWN. 
Uma ligação política não pode virar automaticamente ligação financeira. Uma empresa ser pequena ou recente não comprova fachada. Uma prova de controle real oculto exige elementos positivos específicos e avaliação jurídica.

### Registro de evidência
Campos: source_id; emissor; URL oficial; parâmetros; data e hora; arquivo original; SHA-256 REAL dos bytes originais; versão; página/cláusula; trecho; evidence_id; claim_id; contraprovas; resultado de revisão humana.
Um hash da resposta JSON ou um código parecido com SHA não substitui a validação de bytes originais.

### Alertas
Campos: flag_id; método e regra; universo de comparação; limiar; valor; evidências; falso positivo possível; explicação regular; documento decisivo; prioridade de diligência.
Indicador de risco não é porcentagem de corrupção.

## 2. Encadeamento investigativo

1. Confirmar pessoa e mandato por dados eleitorais e atos de nomeação/posse.
2. Confirmar entidade/órgão competente e período da decisão.
3. Levantar leis, votações, emendas, contratos, fomento, convênios e recursos por fonte.
4. Confirmar fornecedores por CNPJ e representantes/sócios no período de cada ato.
5. Recuperar processos de contratação, justificativas, preços, proposta, pareceres, atestos, notas e prestação de contas.
6. Conciliar contrato, empenho, liquidação, pagamento e execução sem duplicar valores.
7. Construir grafo com documentação POR ARESTA e data de vigência, distinguindo fatos e candidatos.
8. Investigar hipóteses de controle econômico efetivo ou simulação somente se documentos as sustentarem.
9. Identificar inconsistências e testar hipóteses legítimas: erro cadastral, aditivo, mudança de diretoria, subcontratação regular, execução comprovada.
10. Confrontar normas, precedentes, cronologia, competência, nexo, efeitos e requisitos de eventual notícia de fato.
11. Fazer revisão adversarial por pessoa, documento e valor; registrar falhas e contraprovas.
12. Publicar apenas o que foi efetivamente verificado e descrever lacunas e diligências.

## 3. Formato obrigatório em toda perícia

### Parte A — Resumo executivo em linguagem simples
Perguntas que a primeira página responde:
- Quem foi examinado e qual cargo/período foi confirmado?
- Que contratos e verbas foram encontrados, e em qual FASE financeira?
- Quais vínculos são de fato documentados e quais são hipóteses?
- Quais três pontos exigem maior fiscalização e por quê?
- Qual documento falta e quem o detém?
- O que NÃO podemos concluir com as fontes disponíveis?

### Parte B — Corpo analítico
1. Escopo, geografia, período, fontes consultadas, metodologia e data de corte.
2. Identidade e linha do tempo de mandatos, nomes e homônimos.
3. Contratos, atos e decisões com identificadores oficiais e links.
4. Mapa de relações pessoais, societárias, institucionais e políticas sem confundi-las.
5. Grafo temporal com legenda DOCUMENTED/CANDIDATE/REFUTED e fonte por ligação.
6. Fluxo financeiro: contratado, empenhado, liquidado, pago, entregue.
7. Matriz de achados CGU: critério, condição, evidência, causa conhecida/hipótese, efeito confirmado/potencial, explicações e providência.
8. Red flags, parâmetros, população comparável e alertas explicados.
9. Hipóteses concorrentes e contraevidências pesquisadas ativamente.
10. Revisão jurídica e proporcionalidade de eventual encaminhamento.
11. Limites, cobertura por fonte, saúde das consultas, pendências e recomendações.
12. Anexos numerados, fontes, páginas, SHA original, carimbos de coleta e trilha de operações.

### Parte C — Conclusão técnica reproduzível
Para cada achado classificar:
FACT_VERIFIED (original verificado), PARTIAL, ANOMALY_FOR_VERIFICATION, LEAD_ONLY, NOT_DEMONSTRATED, REFUTED ou SOURCE_UNAVAILABLE.

Para a peça de encaminhamento:
INSUFFICIENT_IDENTIFICATION; RESEARCH_NEEDED; FACT_BASED_INQUIRY_POSSIBLE; LEGAL_REVIEW_REQUIRED; NOT_SUPPORTED.

Os estados representam suficiência documental, NÃO probabilidade de culpa. O padrão não atribui nota ou nível de corrupção a pessoas. Explicar motivo e documentos decisivos de maneira acessível.

## 4. Exemplo hipotético, sem caso real

- O Município X contrata empresa E por R$ 100 mil; registro oficial e CNPJ são confirmados.
- O portal mostra empenho de R$ 60 mil, liquidação de R$ 40 mil e pagamento de R$ 30 mil.
- Essa diferença de fases é natural em inúmeros contratos: não somar R$ 100 mil + R$ 60 mil + R$ 40 mil + R$ 30 mil.
- Pessoa P assinou o contrato: vínculo SIGNED/DOCUMENTED se o ato original a identifica e foi verificado.
- Pessoa Q era administradora da empresa E no período: vínculo REGISTERED_ADMIN/DOCUMENTED se o ato registral confirma.
- Pessoa R participou de um evento com P: relação social não prova fluxo financeiro nem intervenção.
- Se falta atestado de entrega, a conclusão correta é EVIDENCE_GAP, e a diligência é obter atestos, notas e produto, não declarar inexecução.

## 5. Garantias e governança

- É proibido conectar nomes por suposições, atribuir culpa automática, revelar vida privada irrelevante ou obter dados protegidos sem autorização.
- Comparar fontes conflitantes e decisões favoráveis a investigados.
- Trabalhos de inteligência não substituem prova de crime nem laudo de autoridade oficial.
- Não protocolar denúncias, compartilhar dados sensíveis ou publicar material acusatório automaticamente.
- O usuário recebe uma conclusão que descreve o que os documentos sustentam, o que é inconclusivo e a próxima diligência com melhor capacidade de esclarecimento.
- A qualidade do dossiê se mede por completude das fontes necessárias, validação do original, precisão dos vínculos, conciliação financeira e contraprovas, nunca por porcentagem de acusações.

Referências locais: SKILL.md; docs/METHODOLOGY.md; docs/FORENSIC-REPORT-STANDARD.md e schemas/forensic_report.schema.json. O módulo politician_cases prepara intake e planejamento; NÃO realiza coleta, verificação de identidade, pagamentos ou relatório final automaticamente.
