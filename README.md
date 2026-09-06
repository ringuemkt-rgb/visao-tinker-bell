# Visão Tinker Bell 🧚‍♀️

**Plataforma open-source de inteligência forense baseada em evidência pública**  
Mapeamento rigoroso de redes, contratos, patrimônio declarado e anomalias envolvendo políticos e figuras públicas — **somente com dados públicos**.

**Brasil-first** + cobertura global | Multi-fonte | ACH obrigatório | Grafos | Pipelines operacionais | Evidence-only

> "Mostramos os números. Não presumimos a origem. Documentamos a cadeia."

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Evidence-Only](https://img.shields.io/badge/Evidence-Only-green.svg)]()
[![Brasil First](https://img.shields.io/badge/Brasil-First-yellow.svg)]()
[![Arch v6](https://img.shields.io/badge/Architecture-v6.0-blueviolet.svg)](docs/ARCHITECTURE-v6.md)

## Princípios Invioláveis

1. **Somente evidência pública e oficial** (TSE, Portal da Transparência, PNCP, Receita, CEIS/CNEP, OpenSanctions, etc.).
2. **Multi-fonte** (≥ 2 fontes independentes de alta confiabilidade para claims materiais).
3. **Scores e anomalias são sinais estatísticos**, nunca julgamento jurídico.
4. **Analysis of Competing Hypotheses (ACH)** obrigatório antes de qualquer conclusão.
5. **Cadeia de evidência completa e reproduzível** (URL, data de acesso, hash quando possível).
6. **Zero playbook de crime** — não descrevemos métodos de lavagem, laranja ou fraude.
7. Mesma régua para todos os partidos e cargos.

## Arquitetura v6.0 (estado da arte)

Documento completo de arquitetura, gaps, fontes, técnicas e roadmap:

- **[docs/ARCHITECTURE-v6.md](docs/ARCHITECTURE-v6.md)** — visão sistêmica BIAC-S3 / Visão Tinker Bell v6.0
- **[docs/DATA-SOURCES.md](docs/DATA-SOURCES.md)** — catálogo de fontes (Tier 1–3)
- **[docs/TECHNIQUES.md](docs/TECHNIQUES.md)** — técnicas forenses (sinais, não acusações)
- **[docs/ROADMAP.md](docs/ROADMAP.md)** — sprints de implementação

## O que já está operacional neste repo

| Componente | Caminho |
|------------|---------|
| Motor de Red Flags | `lib/red_flags_engine.py` + `rules/red_flags.json` |
| Clientes de API (CNPJ) | `lib/api_clients.py` |
| Exemplo de teste de regras | `scripts/run_red_flags_example.py` |
| Script TSE | `scripts/tse_download.py` |
| Metodologia | `docs/methodology.md` |
| Integração Monitor de Gravata | `docs/integrations/monitor-de-gravata.md` |
| Visualização de grafos | `docs/graph-visualization.md` |
| Template de dossiê | `assets/dossie-template.md` |

## Início Rápido

```bash
git clone https://github.com/ringuemkt-rgb/visao-tinker-bell.git
cd visao-tinker-bell

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Testar motor de red flags
python scripts/run_red_flags_example.py
```

## Estrutura do Repositório

```
visao-tinker-bell/
├── README.md
├── LICENSE                    # AGPL-3.0
├── requirements.txt
├── docs/
│   ├── ARCHITECTURE-v6.md     # Arquitetura completa v6.0
│   ├── DATA-SOURCES.md
│   ├── TECHNIQUES.md
│   ├── ROADMAP.md
│   ├── methodology.md
│   ├── tools-catalog.md
│   ├── brazil-pipeline.md
│   ├── graph-visualization.md
│   ├── red-flags-engine.md
│   └── integrations/
│       └── monitor-de-gravata.md
├── lib/
│   ├── red_flags_engine.py
│   └── api_clients.py
├── rules/
│   └── red_flags.json
├── scripts/
│   ├── run_red_flags_example.py
│   └── tse_download.py
├── assets/
│   └── dossie-template.md
└── data/                      # Placeholders (não commitar dados sensíveis)
```

## Integração com a Skill Grok

Esta plataforma é a implementação operacional da skill **Visão Tinker Bell** (political-corruption-forensics).  
Quando ativada no Grok, a skill segue a metodologia, o catálogo de fontes e os princípios deste repositório.

## Contribuição e Ética

- PRs de pipelines, conectores de fonte **pública**, red flags determinísticas e visualizações são bem-vindos.
- Contribuições que quebrem o princípio *evidence-only* ou que descrevam métodos de crime serão rejeitadas.
- Uso legítimo: accountability, jornalismo de dados, pesquisa e controle social.

## Licença

AGPL-3.0 — código aberto, copyleft.

---

**Visão Tinker Bell** — porque a verdade precisa de luz, evidência e método.
