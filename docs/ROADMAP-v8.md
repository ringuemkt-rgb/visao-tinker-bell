# Roadmap v8

## Entregue no PR v8
- pacote `vtb/` isolado do legado v7;
- state machine e SQLite CaseStore;
- Claim Ledger com independência de linhagem;
- source-health e regra zero-result != absence;
- ACH/falsificação, Red Team, QA e publication gates;
- money-flow por estágio;
- entity resolution conservador;
- Tool Registry S0–S10 e preservação SHA-256;
- procurement/payment/corporate/electoral/assets/price engines;
- HHI, Benford com applicability gate e sinais explicáveis;
- evidence-backed graph + temporal graph;
- timeline e document drift;
- control-external semantics;
- catálogo nacional de fontes por domínio/autoridade;
- Yente adapter com match como lead;
- watchlists, checkpoints e coleta incremental;
- contratos para linkage probabilístico e human review;
- schemas, documentação, CI e testes.

## Próximos EPICs
1. Adapters oficiais versionados e testados: PNCP, TCU, TSE, SICONFI, CEIS/CNEP e portais locais.
2. Data Lake DuckDB/Parquet para datasets nacionais e manifests de dataset.
3. Parser de PDF com seleção Docling/PyMuPDF/OCRmyPDF e quality scoring.
4. Backend opcional Neo4j com export/import sem perder evidence IDs e temporalidade.
5. Backend opcional Splink com calibration/eval suite em dados sintéticos e saneados.
6. Backend opcional Aleph para ingestão documental/XREF via API versionada.
7. Backend opcional Timesketch para timeline colaborativa.
8. Scheduler adapter (Airflow ou Prefect) com source health e retry policy fail-closed.
9. Eval suite anticorrupção: falsos positivos, falsos negativos e regressões sem dados pessoais reais.
10. Dashboard de coverage/readiness e triage priority — nunca score de culpa.
11. Evidence book exportável com anexos, hashes e matriz claim→evidence.
12. Preset municipal/estadual automático com fontes do respectivo ente e tribunal de contas.
