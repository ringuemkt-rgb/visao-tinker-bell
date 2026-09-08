from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True, frozen=True)
class DocumentVersion:
    document_id: str
    version_id: str
    evidence_id: str
    fields: dict[str, Any]
    published_at: str | None = None


def diff_versions(a: DocumentVersion, b: DocumentVersion) -> dict[str, tuple[Any, Any]]:
    keys = set(a.fields) | set(b.fields)
    return {key: (a.fields.get(key), b.fields.get(key)) for key in keys if a.fields.get(key) != b.fields.get(key)}


def material_drift_signal(
    a: DocumentVersion,
    b: DocumentVersion,
    *,
    material_fields: set[str],
) -> RiskSignal | None:
    changes = diff_versions(a, b)
    material = {key: values for key, values in changes.items() if key in material_fields}
    if not material:
        return None
    return RiskSignal(
        signal_id=f"DOC-DRIFT-{a.document_id}-{a.version_id}-{b.version_id}",
        category=SignalCategory.DOCUMENT,
        title="Alteração material entre versões documentais",
        description=f"Campos materiais alterados: {', '.join(sorted(material))}.",
        severity=SignalSeverity.MEDIUM,
        evidence_ids=[a.evidence_id, b.evidence_id],
        method="structured document version diff",
        false_positive_risk="medium",
        alternative_explanations=["retificação legítima", "erro material corrigido", "aditivo regularmente publicado"],
    )
