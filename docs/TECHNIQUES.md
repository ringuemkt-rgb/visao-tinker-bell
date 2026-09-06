# Técnicas Forenses — Visão Tinker Bell

Todas as técnicas abaixo produzem **sinais objetivos**. Nenhuma substitui investigação oficial nem gera acusação automática.

## Financeiras

- Lei de Benford (1º e 2º dígitos)
- Z-score / IQR (outliers)
- HHI (concentração de fornecedores)
- Flags de valores redondos e fracionamento (structuring) como *sinal*, não prova
- Análise temporal de séries de gastos

## Redes / grafos

- PageRank, betweenness, degree centrality
- Detecção de comunidades
- Export GraphML/GEXF para Gephi

## NLP

- NER (regex atual; meta BERTimbau)
- Classificação de documentos por tipo (contrato, diário, notícia)

## Entity resolution

- Match exato por CPF/CNPJ
- Fuzzy de nomes (com limiar documentado)

## Metodologia obrigatória

- **ACH** antes de qualquer conclusão (ver `docs/methodology.md` e `docs/ARCHITECTURE-v6.md`)
- Cadeia de custódia (fonte + data + hash)

Implementações atuais: `lib/red_flags_engine.py` + `rules/red_flags.json`.
