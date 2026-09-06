# Catálogo de Ferramentas — Visão Tinker Bell

## Fontes Oficiais Brasil (Tier 1)

- **TSE** — https://dadosabertos.tse.jus.br/ e https://divulgacandcontas.tse.jus.br/  
  Candidaturas, bens declarados, prestações de contas eleitorais e partidárias.
- **Portal da Transparência (CGU)** — API + downloads de contratos, emendas, transferências, CEIS, CNEP, lista de PEPs.
- **Receita Federal** — Dumps mensais de CNPJ (QSA, sócios, capital, endereços).
- **Câmara dos Deputados e Senado** — dadosabertos.camara.leg.br e legis.senado.leg.br (votações, CEAP/CEAPS).
- **PNCP** — contratos, dispensas e inexigibilidades (ver `lib/pncp.py`, `docs/pncp.md`).
- **TCU** — Listas de inidôneos e desqualificados.
- **Querido Diário** — Diários oficiais e nomeações.
- **Compras.gov.br** — preços homologados, CATMAT/CATSER.

## Projetos Open-Source Brasileiros (prioridade alta)

| Projeto | Repositório | Função principal | Integração Tinker Bell |
|---------|-------------|------------------|------------------------|
| **Monitor de Gravata** | [steinhauserhzs/monitor-de-gravata](https://github.com/steinhauserhzs/monitor-de-gravata) | Ficha 360, red flags, radar de contratos, catálogo de APIs | Prioridade máxima — regras adaptadas em `rules/red_flags.json` |
| Enriquecimetro | iosbilario/enriquecimetro | Evolução de patrimônio (TSE bens) | Pipeline de wealth gap |
| Tribuna | rafapolo/tribuna | Prestações TSE em SQL | Receitas/despesas eleitorais |
| VigiaBR | devitese/vigiabr | Multi-fonte + SCI + Neo4j | Scoring + grafo |
| Olho Neles / OPS | olhoneles / ops-org | Gastos parlamentares (CEAP) | Cota parlamentar |
| BidRadarBrasil | matheushexsel/bidradarbrasil | Anomalias em licitações | Radar PNCP |

## Coleta HTML (fallback — Tier 3)

| Ferramenta | Repo | Uso na VTB |
|------------|------|------------|
| **Scrapling** | [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | Parser adaptativo + fetchers (HTTP / stealth). **Só** quando não há API oficial. Wrapper: `lib/html_fetch.py`. Ética: `docs/html-fetch-ethics.md`. |

Ordem: API → dump oficial → HTML com hash. Nunca o inverso.

## Bases Globais e Cross-Border

- **OpenSanctions** + PoliLoom + EveryPolitician — PEPs.
- **OCCRP Aleph** — entity resolution, follow-the-money.
- **OpenCorporates** + OpenOwnership — sociedades e beneficiários.
- **ICIJ Offshore Leaks** · **LittleSis**.

## Visualização de Grafos

- Desktop: **Gephi**, Cytoscape.
- Python: **NetworkX**, **PyVis**, PyGraphistry.
- Schema: FollowTheMoney → Neo4j.
- Export VTB: `scripts/graph_export.py` (GraphML/GEXF).

## Bancos e padrões

- **DuckDB** (tabular) · **Neo4j** (grafo) · **FollowTheMoney (FtM)**.

## Hugging Face

Apenas NLP auxiliar em textos públicos — nunca como fonte de fato.

---

Sempre registre proveniência. Prefira Tier 1 e 2.
