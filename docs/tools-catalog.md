# Catálogo de Ferramentas — Visão Tinker Bell

## Fontes Oficiais Brasil (Tier 1)

- **TSE** — https://dadosabertos.tse.jus.br/ e https://divulgacandcontas.tse.jus.br/  
  Candidaturas, bens declarados, prestações de contas eleitorais e partidárias.
- **Portal da Transparência (CGU)** — API + downloads de contratos, emendas, transferências, CEIS, CNEP, lista de PEPs.
- **Receita Federal** — Dumps mensais de CNPJ (QSA, sócios, capital, endereços).
- **Câmara dos Deputados e Senado** — dadosabertos.camara.leg.br e legis.senado.leg.br (votações, CEAP/CEAPS).
- **TCU** — Listas de inidôneos e desqualificados.
- **Querido Diário** — Diários oficiais e nomeações.

## Projetos Open-Source Brasileiros

| Projeto | Repositório | Função |
|---------|-------------|--------|
| Enriquecimetro | iosbilario/enriquecimetro | Evolução de patrimônio declarado (TSE bens) |
| Tribuna | rafapolo/tribuna | Prestações de contas TSE em banco relacional + SQL |
| VigiaBR | devitese/vigiabr | Multi-fonte + Score de Consistência (SCI) + Neo4j |
| Olho Neles | olhoneles/olhoneles | Gastos parlamentares (CEAP etc.) |
| OPS | ops-org/operacao-politica-supervisionada | Auditoria de cota parlamentar |

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
