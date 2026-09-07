from __future__ import annotations

from .claims import ClaimLedger


def render_claim_ledger(ledger: ClaimLedger) -> str:
    lines = ["| Claim | Status | Statement | Support | Contradiction |", "|---|---|---|---:|---:|"]
    for claim in ledger.claims.values():
        lines.append(
            f"| `{claim.claim_id}` | {claim.status} | {claim.statement.replace('|', '/')} | {len(claim.evidence_ids)} | {len(claim.contradicting_evidence_ids)} |"
        )
    return "\n".join(lines)


def render_limits(ledger: ClaimLedger) -> str:
    items: list[str] = []
    for claim in ledger.claims.values():
        for limitation in claim.limitations:
            items.append(f"- `{claim.claim_id}`: {limitation}")
    return "\n".join(items) if items else "- Nenhuma limitação registrada no ledger (isso não elimina limitações externas)."
