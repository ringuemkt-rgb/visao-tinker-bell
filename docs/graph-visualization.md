# Visualização de Grafos — Visão Tinker Bell

## Por que grafos?

Redes de doações, contratos, sociedades e parentesco só se revelam plenamente quando visualizadas como nós (pessoas/empresas) e arestas (fluxos de dinheiro, controle, parentesco declarado).

## Stack Recomendada

1. **Construção**: NetworkX ou Neo4j (com FollowTheMoney schema).
2. **Análise**: centrality (betweenness, degree), community detection (Louvain), pathfinding.
3. **Exploração interativa**:
   - Médio porte → Gephi
   - Grande porte / GPU → PyGraphistry
   - Notebooks → neo4j-viz ou PyVis
   - Web / relatórios → Sigma.js ou Cytoscape.js
4. **Persistência de investigação**: Neo4j + kipi ou Flowsint.

## Fluxo Operacional

```
Dados normalizados (TSE + Transparência + CNPJ)
        ↓
Entity resolution + joins
        ↓
NetworkX / DuckDB → export GraphML / GEXF / CSV nodes+edges
        ↓
Gephi (layouts + analytics)  ou  Neo4j (queries + Bloom)
        ↓
Export final ou embed (Sigma.js / PyGraphistry)
```

## Propriedades obrigatórias nos nós e arestas

- `source` (URL ou identificador do dump)
- `access_date`
- `confidence` (entity resolution)
- `value` / `amount` (quando aplicável)
- `relationship_type` (doacao, contrato, socio, familiar, etc.)

## Exemplos de queries úteis (Neo4j)

- Caminhos mais curtos entre doador e empresa contratada
- Comunidades de empresas ligadas a um mesmo político
- Nós com alta betweenness (intermediários)

Consulte `scripts/graph_export.py` e a pasta `graph/` para configurações prontas.
