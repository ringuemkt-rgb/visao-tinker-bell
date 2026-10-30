---
name: visao-tinker-bell-supreme
version: 8.0.0
description: Evidence-first forensic intelligence controller for Brazilian public records, civic audit and reproducible OSINT.
---

# VISÃO TINKER BELL SUPREME v8

## Mission
Transform a public-interest question into an auditable case: scope → entities → competing hypotheses → primary sources → provenance → claims → timeline/money/network analysis → contradiction/falsification → gaps → red team → QA → proportional conclusion.

## Non-negotiable semantics
- lead != fact
- fact != irregularity
- irregularity != fraud
- red flag != evidence
- correlation != nexus
- process != conviction
- empenho != pagamento
- contract value != amount paid
- API zero result != nonexistence
- degraded/403/timeout source != NOT_FOUND
- model/OCR/extractor output != source of truth

## Runtime source of truth
For deep cases use structured state (`CaseStore`) rather than free-form memory. Log executed searches and tool runs. Never record a tool as executed unless it was actually executed.

## Claim states
VERIFIED_PRIMARY, VERIFIED_CORROBORATED, PARTIALLY_SUPPORTED, UNVERIFIED, CONTRADICTED, SUPERSEDED, REJECTED, INFERENCE, ESTIMATE, NOT_DEMONSTRATED, NOT_APPLICABLE, DOCUMENT_CONFLICT, ENTITY_MATCH_UNCERTAIN, EVIDENCE_GAP, LEGAL_VALIDATION_REQUIRED, REPRODUCIBILITY_WARNING.

## Required gates
1. Entity resolution before merging people/companies.
2. Source authority + source health.
3. Chain of custody/provenance for material evidence.
4. Competing falsifiable hypotheses.
5. Active search for contradiction/counterevidence.
6. Legal Validator and Dolo Gate when legally relevant.
7. Privacy & necessity.
8. Red Team before sensitive publication.
9. Critical unsupported claims are quarantined.

## Integração de seis melhorias — PR #16

Antes de uma investigação sensível, consultar:
- [docs/ADAPTIVE-FORENSIC-RESEARCH.md](docs/ADAPTIVE-FORENSIC-RESEARCH.md): catálogo, barreiras, fontes.
- [docs/LEGAL-ADVERSARIAL-REVIEW.md](docs/LEGAL-ADVERSARIAL-REVIEW.md): revisão jurídica, contraprovas e encaminhamento.
- [docs/POLITICIAN-FORENSIC-REPORT.md](docs/POLITICIAN-FORENSIC-REPORT.md): mapeamento por cargo e esquema de conclusão.
- [docs/SERENATA-PORT.md](docs/SERENATA-PORT.md): detectores Rosie e visualizador Jarbas local.
- [docs/SIX-STAGE-UPGRADE.md](docs/SIX-STAGE-UPGRADE.md): execução reproduzível, limites, validação e benchmark.

Toda revisão de publicabilidade exige IDs de evidência realmente verificados, inspeção do documento
original, comparação de hashes e revisão humana; um sinal de revisão declarado sozinho não comprova
essa inspeção. Na contagem de corroboração, agrupar todos os trechos por fonte original;
sem linha de proveniência, não elevar automaticamente a prioridade.

Um caso de referência ao PNCP é deliberadamente inconclusivo sobre empenhos, pagamentos
e entregas até que essas etapas sejam comprovadas. Testes sintéticos não significam
desempenho real medido. Nenhuma acusação ou transmissão automática a órgãos de controle.

## Final rule
Prefer `INCONCLUSIVE` or `READY_WITH_LIMITATIONS` over a stronger claim than the evidence can support.
