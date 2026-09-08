# Catálogo de sinais VTB v8

Todo sinal nasce como `ANOMALY_FOR_VERIFICATION`.

| Família | Sinal | O que mede | Não demonstra sozinho |
|---|---|---|---|
| Procurement | baixa competição | poucos participantes | direcionamento/conluio |
| Procurement | concentração HHI | concentração no universo | cartel |
| Procurement | emergência recorrente | repetição temporal | fraude/dolo |
| Procurement | vencedor recorrente | frequência de vitórias | favorecimento |
| Procurement | proximidade de limiar | distância de limiar validado | fracionamento intencional |
| Payment | duplicidade candidata | mesma chave forte repetida | pagamento indevido sem validar estorno/parcelamento |
| Payment | linkage gap | ausência de contrato/empenho no dataset | inexistência documental real |
| Corporate | atributo compartilhado | endereço/telefone/e-mail/sócio comum | interposição/conluio |
| Corporate | capital/contrato | relação cadastral/valor | incapacidade econômica |
| Electoral | contraparte ↔ fornecedor | sobreposição temporal de entidade | troca de favor |
| Assets | variação patrimonial | mudança em série comparável | enriquecimento ilícito |
| Network | grau elevado | conectividade de nó | centralidade criminosa |
| Price | preço relativo | diferença vs comparáveis normalizados | sobrepreço provado |
| Documents | version drift | alteração de campo material | adulteração dolosa |
| Timeline | ordem incompatível | violação de constraint temporal | fraude documental |
| Statistics | Benford | divergência de primeira casa | manipulação contábil |
| Control | estágio processual | situação do procedimento | culpa antes da decisão final |
| Watchlist | candidate match | possível correspondência | identidade confirmada |
| Linkage | probabilistic match | probabilidade do modelo | identidade definitiva |

## Composição

A VTB eleva **prioridade de revisão**, não probabilidade de corrupção. Sinais de famílias independentes, apoiados em evidências distintas, podem justificar uma diligência mais profunda. A passagem de sinal para claim material exige resolução de entidade, fonte primária quando possível, temporalidade, contraprova, análise jurídica pertinente e revisão humana.

## Regras proibidas como conclusão automática

- "capital baixo + contrato alto = laranja";
- "mesmo sobrenome = parente";
- "mesmo endereço = conluio";
- "idoso/baixa renda aparente = sócio incompatível";
- "HHI alto = cartel";
- "Benford χ² alto = manipulação";
- "valor perto do limite = fracionamento";
- "PEP match por nome = mesma pessoa".
