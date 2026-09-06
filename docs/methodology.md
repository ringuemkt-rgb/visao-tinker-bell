# Metodologia Visão Tinker Bell

## 1. Princípios Operacionais

- Evidence-only: apenas registros públicos oficiais ou dumps públicos com proveniência clara.
- Multi-fonte obrigatória para qualquer claim material.
- Anomaly scores = sinais estatísticos (inspirados em CongressWatch e VigiaBR SCI).
- ACH (Analysis of Competing Hypotheses) + red-team antes de output final.
- Toda evidência deve ser linkável e datada.

## 2. Workflow Padrão (8 etapas)

1. **Clarificar escopo** — alvo, período, jurisdição, perguntas específicas.
2. **Entity Resolution** — normalizar nome, CPF/CNPJ, aliases, cargos, partidos. Fontes: OpenSanctions, TSE, CGU PEPs, Wikidata, EveryPolitician.
3. **Coleta primária** (prioridade Brasil):
   - TSE Dados Abertos (candidaturas, bens, prestações de contas)
   - Portal da Transparência / CGU API (contratos, emendas, CEIS/CNEP)
   - Receita Federal CNPJ dumps (QSA / sócios)
   - Câmara e Senado dados abertos (votações, CEAP)
   - OpenSanctions Brazil + TCU
4. **Cruzamento** — doações ↔ contratos ↔ crescimento de bens ↔ sociedades familiares ↔ votações.
5. **Scoring de anomalia e consistência**.
6. **ACH + Red-team**.
7. **Visualização em grafo** (NetworkX → Gephi / PyGraphistry / Neo4j / Sigma.js).
8. **Output estruturado** (template de dossiê + apêndice de evidências).

## 3. Tiers de Evidência

| Tier | Descrição | Exemplos |
|------|-----------|----------|
| 1 | Oficial direto (API/dump governamental) | TSE, Portal Transparência, FEC, SEC EDGAR, Receita CNPJ |
| 2 | Bases curadas com proveniência | OpenSanctions, OCCRP Aleph, OpenCorporates, ICIJ |
| 3 | Ferramentas analíticas open-source que citam Tier 1/2 | CongressWatch, Enriquecimetro, VigiaBR, Tribuna |
| 4 | Secundário / índices | CPI, V-Dem (apenas contexto) |

Nenhum claim material pode se apoiar apenas em Tier 4.

## 4. Template ACH

| Hipótese | Evidência a favor | Evidência contra | Diagnosticidade | Notas |
|----------|-------------------|------------------|-----------------|-------|
| H1 Legítimo / explicado por rendimentos públicos | | | | |
| H2 Anomalia estatística sem indício adicional | | | | |
| H3 Possível conflito / interesse não declarado (precisa mais dados) | | | | |
| H4 Dados insuficientes | | | | |

## 5. Red-Team Checklist

- Todo número tem fonte primária?
- Hipóteses rivais foram listadas e pontuadas?
- Linguagem limita-se ao que os dados mostram?
- Cadeia de evidência é reproduzível por terceiro?
- Algum método não-público foi usado? (Se sim → descartar)

## 6. Pipeline Brasil (resumo)

Ver `docs/brazil-pipeline.md` para detalhes operacionais de download, normalização de CPF/CNPJ, joins e exportação para grafo.
