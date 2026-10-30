# Visão Tinker Bell — engineering agent guide

Follow `SKILL.md`, `docs/METHODOLOGY.md`, `docs/FORENSIC-REPORT-STANDARD.md`, and `docs/AUTONOMY-GROK.md`.

## Development
- Run `python -m compileall -q vtb lib scripts`, `ruff check vtb tests` and `pytest -q` on affected changes.
- Prefer unit tests and allowlisted, read-only adapters. Public-source calls need finite timeouts, source-health semantics and source identifiers.
- Keep original document != extracted text != derived claim. Missing fields, unavailable APIs or 403 never imply zero/absence.
- Never auto-submit complaints or expose credentials, local dossiers or personal data in public commits.
- Modifying legal-sensitive conclusions requires a review gate which defaults to incomplete until a reviewer explicitly confirms it.
- Before a Grok integration claim, verify MCP connectivity in the actual user environment. GitHub code alone is not an active connection.

## Agent skills
- `.grok/skills/forensic-intelligence-br/SKILL.md`: source-bound public investigation.
- `.grok/skills/human-writing-os/SKILL.md`: verified, polished, natural writing.
- `vtb/autonomy.py`: small real, bounded read-only query execution; no external publishing.
- `vtb/investigative_reasoning.py`: read-only TCU/CGU-style findings, document provenance, falsification, and deterministic dossier QA. No judgments of guilt.
- `.grok/skills/investigative-reasoning-br/SKILL.md`: investigatory reasoning playbook grounded in public sources.
