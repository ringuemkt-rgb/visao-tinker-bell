# Catálogo de Ferramentas — Visão Tinker Bell

## Fontes Oficiais Brasil (Tier 1)

- **TSE** — https://dadosabertos.tse.jus.br/ e https://divulgacandcontas.tse.jus.br/  
  Candidaturas, bens declarados, prestações de contas eleitorais e partidárias.
- **Portal da Transparência (CGU)** — API + downloads de contratos, emendas, transferências, CEIS, CNEP, lista de PEPs.
- **Receita Federal** — Dumps mensais de CNPJ (QSA, sócios, capital, endereços).
- **Câmara dos Deputados e Senado** — dadosabertos.camara.leg.br e legis.senado.leg.br (votações, CEAP/CEAPS).
- **PNCP** (Portal Nacional de Contratações Públicas) — contratos, dispensas e inexigibilidades de União, estados e municípios.
- **TCU** — Listas de inidôneos e desqualificados.
- **Querido Diário** — Diários oficiais e nomeações.
- **Compras.gov.br** — preços homologados, CATMAT/CATSER.

## Projetos Open-Source Brasileiros (prioridade alta)

| Projeto | Repositório | Função principal | Integração Tinker Bell |
|---------|-------------|------------------|------------------------|
| **Monitor de Gravata** | [steinhauserhzs/monitor-de-gravata](https://github.com/steinhauserhzs/monitor-de-gravata) | Portal da Transparência 2.0: Ficha 360 de políticos, Manual do Candidato 2026, Radar de contratos + red flags, Ficha da empresa, Comparador de preços, 81 regras de red flags, casos comunitários, catálogo de APIs. Next.js, evidence-only, repo-as-database. | **Prioridade máxima**. Usar como referência de UI, regras de red flags e catálogo de APIs. Adaptar regras e módulos de ficha 360 / radar de contratos. |
| Enriquecimetro | iosbilario/enriquecimetro | Evolução de patrimônio declarado (TSE bens) entre eleições | Pipeline de bens + wealth gap |
| Tribuna | rafapolo/tribuna | Prestações de contas TSE em banco relacional + SQL para inquéritos | Base de receitas/despesas eleitorais |
| VigiaBR | devitese/vigiabr | Multi-fonte + Score de Consistência (SCI 0–1000) + Neo4j | Scoring de consistência + grafo |
| Olho Neles | olhoneles/olhoneles | Gastos parlamentares (CEAP etc.) de várias casas | Monitoramento de cota |
| OPS | ops-org/operacao-politica-supervisionada | Auditoria de cota parlamentar | Auditoria de gastos |
| BidRadarBrasil | matheushexsel/bidradarbrasil | Anomalias em licitações (PNCP + TSE + Receita + CGU): preço, relacionamento, objeto, estrutural, sanção | Radar de contratos e scoring de risco em licitações |
| Basômetro | estadao/basometro | Monitoramento de governismo na Câmara | Análise de coerência de votos |

## Bases Globais e Cross-Border

- **OpenSanctions** + PoliLoom + EveryPolitician — PEPs mundiais e Brasil.
- **OCCRP Aleph** — Bilhões de registros, entity resolution, follow-the-money.
- **OpenCorporates** + OpenOwnership — Registros societários e beneficiários finais.
- **ICIJ Offshore Leaks Database**.
- **LittleSis** — Redes de poder.

## Ferramentas de Anomaly Scoring e Monitoramento

- CongressWatch (US) — Anomaly Score 0–100 (trades, wealth gap, donor-vote).
- UNREDACTED — Agentes de IA para gastos + doadores.
- Capitol Trace / Open Cabinet — Trades e disclosures.

## Visualização de Grafos (essenciais)

### Desktop
- **Gephi** — Layouts, community detection, centrality, publicação.
- **Cytoscape**.

### Python / Notebooks
- **NetworkX** + **PyVis** / streamlit-d3-network.
- **PyGraphistry** (GPU, escala grande).
- **neo4j-viz**.
- **followthemoney-neomodel** (C4ADS) — Schema OpenSanctions → Neo4j.

### Web / Embed
- **Sigma.js**, **Cytoscape.js**, **G6**, **React Flow**.

### Plataformas OSINT com grafo
- kipi, SpectraGraph, Flowsint, OpenGraph Intel (OGI), PivotGraph.

## Bancos e Padrões

- **Neo4j** (recomendado para path queries e grafos vivos).
- **DuckDB** (análise tabular rápida + export).
- **FollowTheMoney (FtM)** — padrão de dados anti-corrupção do OpenSanctions.

## Hugging Face (apenas processamento)

Modelos de entity extraction e NLP financeiro — usar somente para ajudar na extração de textos públicos, nunca como fonte de fato.

---

Sempre registre a proveniência. Prefira Tier 1 e 2. Atualize este catálogo conforme novas fontes oficiais ou ferramentas open-source relevantes aparecerem.
