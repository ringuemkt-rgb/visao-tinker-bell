# Arquitetura Visão Tinker Bell v7.0

Data: 07/09/2026
Princípio: evidence-only · ACH · cadeia de custódia

## Camadas

1. Apresentação: dossiê, ACH, grafo, planilha
2. Orquestração: pipeline.py, ach.py, graph_export
3. Análise: red_flags, analytics, entity_resolution
4. Ingestão: pncp, api_clients, tse, html_fetch, pdf_extract
5. Custódia: evidence.py (hash, URL, data, tier)

## Ordem de fonte

1. API / dump oficial
2. PDF oficial + SHA-256
3. Extração local (Docling / PyMuPDF)
4. HTML público com robots.txt
5. HF / LLM — auxílio, nunca evidência

## Hipóteses ACH

- H0 conduta regular no registro público
- H1 anomalia sem irregularidade demonstrada
- H2 irregularidade possível — falta documento primário
- H3 evidência insuficiente

Saída = hipótese menos refutada.
