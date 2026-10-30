---
name: investigative-reasoning-br
description: Use when planning, auditing or reviewing Brazilian public-record investigations, forensic dossiers, competing hypotheses, contract reviews, financial reconciliation, and source-grounded misconduct allegations before human legal review.
user-invocable: true
---
# Investigative Reasoning BR — VTB

Implement investigative thinking without copying private tactics or impersonating real investigators.

**Mandatory methodology:** read `docs/INVESTIGATIVE-REASONING-BR.md`, `docs/FORENSIC-REPORT-STANDARD.md`, `docs/METHODOLOGY.md`, and `AGENTS.md`.

## When researching
- Begin with the falsifiable administrative question and controlling date/jurisdiction.
- Preserve the origin of every factual assertion: source, ID, URL, timestamp, location, hash.
- Build a timeline, source lineage and entity-resolution ledger before relating people, entities, payments and contracts.
- Distinguish estimated, awarded, contracted, committed, liquidated and paid amounts.
- Form **at least one legitimate administrative hypothesis** and a rival hypothesis; state evidence that could refute both.
- Search for a contradictory document, superior version, official response and current procedural state.
- A blank search, 403 or 429 is never evidence of non-existence. Similar names and graph paths are not proof of identity or wrongdoing.
- Call `forensic_reasoning_contract` to inspect the expected input. After creating a case and recording sources/evidence/claims/hypotheses, call `audit_forensic_dossier` with explicit criteria and evidence assessments.
- Treat `READY_WITH_LIMITATIONS` as structurally reviewable, **not approved for sending**.
- For public-interest legal issues, provide authority and competence, detailed but proportionate legal questions and pending evidence; never assert intent from statistical signals.
- Integrate `human-writing-os` only after grounding every fact.
- Keep all real personal dossiers out of the public repository and do not auto-submit a representation.

## Dossier sections
Question/period; audited sources; lineage; document versions; matrix of findings; payment stages; role-function comparison; hypotheses including regularity; unknowns and contraprovas; legal version; limitation; next best records; status; human approval gate.
