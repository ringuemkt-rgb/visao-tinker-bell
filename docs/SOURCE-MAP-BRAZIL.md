# Source Map — Brasil

Este mapa define **prioridade**, não disponibilidade garantida.

| Domínio | Fontes preferenciais | Observação |
|---|---|---|
| Contratações | PNCP, Compras.gov.br, portal do órgão, Diário Oficial | confirmar edital/contrato/aditivos e execução |
| Pagamentos | Transparência do ente, SIAFIC/portais, CGU quando aplicável | separar empenho/liquidação/pagamento |
| Controle externo | TCU, TCE, TCM | cautelar, parecer, acórdão e trânsito/estado processual são categorias diferentes |
| Eleitoral | TSE/TRE | candidatura, bens e contas no período correspondente |
| Judicial | tribunal competente; DataJud para descoberta | indexador não substitui decisão original |
| Empresas | Receita/Junta quando pública; BrasilAPI como ponte | resolver CNPJ e histórico temporal |
| Sanções | CEIS/CNEP/CEPIM | verificar entidade, período e situação |
| Fiscal | SICONFI, Tesouro, dados do ente | comparar denominadores e competência |
| Legislativo | Câmara/Senado/AL/Câmara Municipal/SAPL | foco em ato concreto do agente |

## Regra de falha
Se a fonte estiver BLOCKED, TIMEOUT, CONNECTION_ERROR ou DEGRADED, registrar a falha e procurar upstream/rota oficial alternativa. Nunca converter a falha em ausência do fato.
