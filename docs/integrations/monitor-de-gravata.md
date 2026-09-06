# Integração: Monitor de Gravata → Visão Tinker Bell

**Repositório oficial:** https://github.com/steinhauserhzs/monitor-de-gravata  
**Site ao vivo:** https://monitordegravata.vercel.app

## Por que é prioritário

O Monitor de Gravata é o projeto brasileiro open-source mais completo e alinhado com os princípios da Visão Tinker Bell:

- **Evidence-only** rigoroso (todo dado tem link + data de coleta).
- **Red flags como código** (regras públicas, determinísticas, com severidade e fonte metodológica).
- **Ficha 360** de políticos (cota nota a nota, presença, votações, produtividade, emendas, vínculos por sobrenome como hipótese, notícias).
- **Manual do Candidato 2026** (TSE bens + evolução patrimonial + receitas + processos).
- **Radar de contratos** (PNCP + cruzamento com Receita/CNPJ + sanções CEIS/CNEP).
- **Ficha da empresa** + **Comparador de preços** (CATMAT/CATSER).
- **Catálogo de APIs públicas** testado e versionado no próprio repositório.
- Sem banco de dados na v1 (o git é a fonte da verdade).
- Direito de resposta e revisão por pares para casos da comunidade.
- Zero acusação — só sinais objetivos e hipóteses marcadas.

## Como usar na Visão Tinker Bell

1. **Catálogo de APIs** (`data/apis/*.json` do Monitor) → referência oficial de endpoints e status.
2. **Regras de red flags** (`data/red-flags.json` + `lib/rules/`) → adaptar e expandir no nosso motor de scoring.
3. **Módulos de Ficha 360 e Radar de Contratos** → modelo de cruzamento e UI de referência.
4. **Casos da comunidade** → padrão de documentação de hipóteses com fontes e ciclo de vida.
5. **PNCP + Compras.gov.br + CATMAT** → fontes prioritárias para o pipeline de contratos e comparador de preços.

## Fontes que o Monitor já consome ao vivo

- Câmara API v2
- Senado Dados Abertos
- TSE DivulgaCandContas
- PNCP
- BrasilAPI / Receita (CNPJ/QSA)
- Portal da Transparência (chave opcional)
- Compras.gov.br
- Wikidata
- Google News RSS / fact-check

## Próximos passos de integração

- [ ] Clonar e estudar a estrutura de `data/red-flags.json` e `lib/rules`
- [ ] Mapear as 24 regras já automatizadas para o nosso scoring
- [ ] Incorporar o catálogo de APIs como referência viva
- [ ] Avaliar reutilização de componentes de Ficha 360 e Radar
- [ ] Documentar diferenças de governança (nós focamos em perícia profunda + grafos + ACH; eles focam em portal comunitário + UI)

## Licença e ética

Respeitar a licença e a política editorial do Monitor de Gravata. Qualquer adaptação deve manter o princípio "nada é acusação — só sinais objetivos com fonte".
