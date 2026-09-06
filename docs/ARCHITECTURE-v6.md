# 🔬 Arquitetura Visão Tinker Bell / BIAC-S3 v6.0

**Sistema Brasileiro de Perícia Anticorrupção — Estado da Arte (Evidence-Only)**  
**Data:** 06/09/2026  
**Versão:** 6.0  
**Classificação:** Documento de Arquitetura Técnica  
**Princípio inegociável:** Apenas evidência pública. Sinais objetivos ≠ acusação.

---

## 📋 RESUMO EXECUTIVO

Esta revisão consolida a arquitetura-alvo da **Visão Tinker Bell** (repositório operacional) alinhada a práticas forenses de evidência pública. Integra:

- Técnicas forenses implementáveis (financeiras, grafos, NLP, temporal, geo)
- Fontes de dados públicas brasileiras (Tier 1–4)
- Frameworks legais aplicáveis (referência, não aconselhamento jurídico)
- Ferramentas open source de referência
- Metodologias estruturadas (ACH obrigatório)
- Protocolo de cadeia de custódia (hash SHA-256 por fonte)

**Meta:** Referência nacional para perícia anticorrupção baseada **exclusivamente** em registros públicos, com multi-fonte, ACH e red flags determinísticos.

> **Aviso:** Scores, achados ou conclusões de casos específicos mencionados em documentos externos **não** são adotados como fato neste repositório até verificação independente em fontes primárias (TSE, PNCP, Portal da Transparência, CGU, etc.).

---

## 1️⃣ INVENTÁRIO ATUAL (o que o repositório já tem)

### 1.1 Módulos presentes

| Área | Status | Artefatos no repo |
|------|--------|-------------------|
| Red Flags Engine | ✅ Operacional | `rules/red_flags.json`, `lib/red_flags_engine.py` |
| Clientes de API mínimos | ✅ | `lib/api_clients.py` (BrasilAPI CNPJ, PNCP placeholder) |
| Pipeline TSE exemplo | ✅ | `scripts/tse_download.py` |
| Metodologia | ✅ | `docs/methodology.md` |
| Catálogo de ferramentas | ✅ | `docs/tools-catalog.md` |
| Integração Monitor de Gravata | ✅ | `docs/integrations/monitor-de-gravata.md` |
| Visualização de grafos | ✅ | `docs/graph-visualization.md` |
| Template de dossiê | ✅ | `assets/dossie-template.md` |

### 1.2 Stack atual

- Python 3.11+
- requests, pandas (recomendado), networkx (recomendado)
- SHA-256 para integridade de fontes
- JSON para regras e outputs

---

## 2️⃣ GAP ANALYSIS (prioridades)

### 2.1 Gaps técnicos (P0–P2)

| Gap | Prioridade | Solução proposta |
|-----|------------|------------------|
| NER só regex | P0 | BERTimbau / transformers (fine-tune jurídico PT-BR) |
| Grafos só NetworkX | P0 | Neo4j + export GraphML/GEXF para Gephi |
| Processamento em lote | P1 | DuckDB (OLAP) |
| Visualização interativa | P1 | PyVis / Plotly |
| Orquestração ETL | P1 | Prefect ou scripts determinísticos |
| Fontes globais | P2 | OpenSanctions, OCCRP Aleph (quando aplicável) |

### 2.2 Gaps de dados (fontes brasileiras)

| Fonte | Status | Prioridade |
|-------|--------|------------|
| TSE Dados Abertos | Parcial (script exemplo) | P0 |
| Portal da Transparência Federal | Manual | P0 |
| PNCP | Placeholder | P0 |
| CEIS / CNEP / CEPIM (CGU) | Não integrado | P0 |
| Receita CNPJ (dumps mensais) | Parcial (BrasilAPI) | P0 |
| SICONFI | Não | P1 |
| DataJud (CNJ) | Não | P1 |
| Querido Diário (OKBR) | Não | P1 |
| Portais estaduais/municipais (BA, etc.) | Caso a caso | P1 |

### 2.3 Gaps metodológicos

- ACH (Analysis of Competing Hypotheses) — **obrigatório** antes de qualquer conclusão
- GRADE / qualidade de evidência
- Taxonomia de indicadores (OCP Red Flags, FATF red flags de alto nível, sem playbook de crime)
- Cadeia de custódia formal (hash + timestamp + URL + data de coleta)

---

## 3️⃣ ARQUITETURA ALVO v6.0

```
CAMADA 1 — INGESTÃO
  TSE | Portal Transparência | PNCP | Receita CNPJ | CEIS/CNEP
  SICONFI | DataJud | Querido Diário | Portais estaduais | OpenSanctions

CAMADA 2 — NORMALIZAÇÃO / LAKEHOUSE
  DuckDB + Pandas + Schema versionado + Evidence Ledger (SHA-256)

CAMADA 3 — ENTITY RESOLUTION
  Match exato CPF/CNPJ | Fuzzy nomes | Deduplicação | PEPs

CAMADA 4 — ENRIQUECIMENTO
  Benford | Z-score/IQR | HHI | Structuring flags | Network metrics
  Geo (Haversine) | Temporal | NER (BERTimbau)

CAMADA 5 — ANÁLISE
  RedFlagsEngine | ACH Engine | GraphAnalyzer | Relatórios

CAMADA 6 — OUTPUT
  JSON estruturado | PyVis/Plotly | Template dossiê | Export Gephi
```

### Stack alvo (resumo)

```yaml
core: python>=3.11, duckdb, pandas, numpy, scipy
ml_nlp: transformers, torch, sentence-transformers  # opcional
graph: networkx, neo4j (opcional), pyvis
osint: requests, beautifulsoup4
visualization: plotly
etl: scripts determinísticos (preferir simplicidade)
```

---

## 4️⃣ FONTES DE DADOS (catálogo prioritário)

### Tier 1 (obrigatórias)

| Fonte | Uso principal |
|-------|---------------|
| TSE Dados Abertos | Candidatos, bens, doações, despesas |
| Portal da Transparência | Gastos, convênios, sanções |
| PNCP | Contratos (Lei 14.133) |
| CEIS / CNEP / CEPIM | Empresas sancionadas / inidôneas |
| Receita Federal CNPJ | QSA, situação, capital, CNAE |
| SICONFI | Contas municipais/estaduais |
| DataJud | Processos (quando público) |

### Tier 2–3

Querido Diário, Brasil.io, portais estaduais (BA: TCM/Transparência), Jusbrasil/Escavador (consulta pontual), OpenSanctions.

---

## 5️⃣ TÉCNICAS FORENSES (catálogo de alto nível)

**Financeiras:** Benford (1º/2º dígito), Z-score, IQR, HHI, flags de valor redondo, anomalias temporais.  
**Redes:** PageRank, betweenness, detecção de comunidades, centralidade.  
**NLP:** NER (meta: BERTimbau), tópicos.  
**Outras:** Timeline, geo-distância, entity resolution.

Todas as técnicas geram **sinais**. Nenhuma gera automaticamente “prova de crime”.

---

## 6️⃣ FRAMEWORK LEGAL (referência)

Dispositivos relevantes para **contexto** de perícia (não aconselhamento jurídico):

- Lei 12.846/2013 (Anticorrupção Empresarial)
- Lei 8.429/1992 (Improbidade)
- Lei 14.133/2021 (Licitações)
- Lei 9.613/1998 (Lavagem)
- Lei 12.527/2011 (LAI)
- Código Penal (artigos de peculato, corrupção, fraude em licitação — referência)
- LC 64/90 (Ficha Limpa) e resoluções TSE de prestação de contas

A Visão Tinker Bell **não** substitui Ministério Público, Polícia Federal, TCU/TCM ou Judiciário.

---

## 7️⃣ FERRAMENTAS OPEN SOURCE DE REFERÊNCIA

- **Grafos:** NetworkX, Gephi, Neo4j, PyVis, Sigma.js
- **Dados:** DuckDB, Pandas
- **OSINT/plataforma:** OpenSanctions, OCCRP Aleph (consulta)
- **NLP:** BERTimbau / Hugging Face (quando habilitado)
- **Visualização:** Plotly, export GraphML/GEXF

Ver também `docs/tools-catalog.md` e integração Monitor de Gravata.

---

## 8️⃣ METODOLOGIAS OBRIGATÓRIAS

### ACH (Analysis of Competing Hypotheses)

1. Listar hipóteses (incluindo a nula / “dados consistentes com regularidade”).
2. Listar evidências públicas significativas.
3. Matriz Evidência × Hipótese (C / I / NA).
4. Refutar o que for inconsistente.
5. Preferir a hipótese **menos refutada**, não a “mais favorável”.
6. Documentar sensibilidade: quais novas evidências mudariam o quadro.

### Cadeia de custódia mínima

Para cada fato:

- URL ou identificador oficial
- Data de coleta
- Hash SHA-256 do arquivo/conteúdo quando aplicável
- Trecho factual citado (sem adjetivo)

---

## 9️⃣ ROADMAP DE IMPLEMENTAÇÃO

**Sprint A (imediato)**  
- Expandir `rules/red_flags.json`  
- Cliente CEIS/CNEP + PNCP mais completo  
- Documentar ACH no template de dossiê  

**Sprint B**  
- DuckDB + pipeline TSE/PNCP  
- Export GraphML + PyVis  
- Entity resolution básica (CNPJ/CPF)

**Sprint C**  
- NER com modelo PT-BR (opcional)  
- Integração SICONFI / Querido Diário  
- Dashboard mínimo (Plotly)

---

## 🔟 PRINCÍPIOS INEGOCIÁVEIS (Visão Tinker Bell)

1. **Só evidência pública** — fonte primária ou não entra.
2. **Linguagem factual** — número, data, link; sem adjetivo acusatório.
3. **Multi-fonte** — preferir ≥2 fontes independentes de alta confiabilidade.
4. **ACH antes de conclusão**.
5. **Mesma régua para todos** — partido, cargo ou ideologia não alteram a regra.
6. **Nunca playbook de crime** — não descrever “como se faz” lavagem, laranja ou fraude.
7. **Direito de resposta e atualização** — dossiês são vivos e corrigíveis.

---

*Documento gerado para o repositório [ringuemkt-rgb/visao-tinker-bell](https://github.com/ringuemkt-rgb/visao-tinker-bell).  
Alinhado à skill Visão Tinker Bell e ao motor de red flags adaptado do Monitor de Gravata.*
