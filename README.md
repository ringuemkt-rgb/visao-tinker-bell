# Visão Tinker Bell 🧚‍♀️

**Plataforma open-source de inteligência forense baseada em evidência pública**  
Mapeamento rigoroso de redes de corrupção, desvio de recursos e anomalias envolvendo políticos e figuras públicas.

**Brasil-first** + cobertura global | Multi-fonte | ACH obrigatório | Grafos | Pipelines operacionais | Evidence-only

> "Mostramos os números. Não presumimos a origem. Documentamos a cadeia."

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Evidence-Only](https://img.shields.io/badge/Evidence-Only-green.svg)]()
[![Brasil First](https://img.shields.io/badge/Brasil-First-yellow.svg)]()

## Princípios Invioláveis

1. **Somente evidência pública e oficial** (TSE, Portal da Transparência, Receita, OpenSanctions, OCCRP Aleph, FEC, SEC, etc.).
2. **Multi-fonte** (≥ 2 fontes independentes de alta confiabilidade para claims materiais).
3. **Scores e anomalias são sinais estatísticos**, nunca julgamento jurídico.
4. **Analysis of Competing Hypotheses (ACH)** + red-team obrigatórios antes de qualquer conclusão.
5. **Cadeia de evidência completa e reproduzível** (URL, data de acesso, hash quando possível).
6. Zero métodos ilegais, zero doxxing de privados além do que já é público em declarações oficiais.

## O que a Visão Tinker Bell entrega

- Entity resolution robusta (CPF/CNPJ, PEPs, aliases)
- Cruzamento: doações ↔ contratos ↔ bens declarados ↔ sociedades ↔ votações ↔ offshore
- Scoring de consistência e anomalia (inspirado em CongressWatch + VigiaBR)
- Visualização de grafos interativa (Gephi, PyGraphistry, Neo4j, Sigma.js, NetworkX+PyVis)
- Pipelines operacionais prontos (TSE dumps, Portal da Transparência API, CNPJ)
- Templates de dossiê forense e ACH
- Catálogo completo de ferramentas (open-source + oficiais)

## Estrutura do Repositório

```
visao-tinker-bell/
├── README.md                 # Este arquivo
├── LICENSE                   # AGPL-3.0
├── docs/
│   ├── methodology.md        # Metodologia completa + ACH
│   ├── tools-catalog.md      # Catálogo de ferramentas
│   ├── brazil-pipeline.md    # Pipeline Brasil detalhado
│   └── graph-visualization.md
├── scripts/
│   ├── tse_download.py       # Download e normalização TSE
│   ├── entity_resolution.py  # Matching básico
│   └── graph_export.py       # Export para Gephi / GraphML
├── references/               # Documentação de apoio
├── assets/                   # Templates de relatório
├── examples/                 # Exemplos de uso
├── graph/                    # Configurações Neo4j / layouts
└── data/                     # Placeholders (nunca commitar dados sensíveis)
```

## Início Rápido

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell

# Ambiente recomendado
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Exemplo: baixar e inspecionar dados TSE (veja scripts/)
python scripts/tse_download.py --help
```

## Integração com a Skill Grok

Esta plataforma é a implementação operacional da skill **political-corruption-forensics** (renomeada e expandida como **Visão Tinker Bell**).  
Quando a skill é ativada no Grok, ela segue exatamente a metodologia e o catálogo deste repositório.

## Contribuição e Ética

- Pull requests de melhorias de pipeline, novos conectores de fonte pública e visualizações são bem-vindos.
- Qualquer contribuição que quebre o princípio "evidence-only" será rejeitada.
- Use apenas para accountability, jornalismo de investigação e pesquisa acadêmica legítima.

## Licença

AGPL-3.0 — código aberto, copyleft, uso livre desde que o código fonte de derivações seja disponibilizado.

---

**Visão Tinker Bell** — porque a verdade precisa de luz, evidência e método.
