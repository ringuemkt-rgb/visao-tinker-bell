from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .signals import RiskSignal, SignalCategory, SignalSeverity


@dataclass(slots=True)
class CompanyProfile:
    company_id: str
    legal_name: str
    evidence_ids: list[str]
    opened_on: str | None = None
    status: str | None = None
    capital: float | None = None
    activities: list[str] = field(default_factory=list)
    partners: set[str] = field(default_factory=set)
    addresses: set[str] = field(default_factory=set)
    phones: set[str] = field(default_factory=set)
    emails: set[str] = field(default_factory=set)


def shared_attribute_signals(companies: list[CompanyProfile]) -> list[RiskSignal]:
    """Compartilhamento cadastral é correlação para revisão, não prova de interposição ou conluio."""
    indexes: dict[str, dict[str, set[str]]] = {
        "address": defaultdict(set),
        "phone": defaultdict(set),
        "email": defaultdict(set),
        "partner": defaultdict(set),
    }
    evidence_by_company = {company.company_id: company.evidence_ids for company in companies}
    for company in companies:
        for value in company.addresses:
            indexes["address"][value].add(company.company_id)
        for value in company.phones:
            indexes["phone"][value].add(company.company_id)
        for value in company.emails:
            indexes["email"][value].add(company.company_id)
        for value in company.partners:
            indexes["partner"][value].add(company.company_id)

    signals: list[RiskSignal] = []
    for kind, values in indexes.items():
        for value, company_ids in values.items():
            if len(company_ids) < 2:
                continue
            evidence_ids = sorted({e for cid in company_ids for e in evidence_by_company[cid]})
            signals.append(
                RiskSignal(
                    signal_id=f"CORP-SHARED-{kind.upper()}-{abs(hash((kind, value))) % 10**10}",
                    category=SignalCategory.CORPORATE,
                    title=f"Atributo cadastral compartilhado: {kind}",
                    description=f"{len(company_ids)} empresas compartilham o mesmo atributo no dataset.",
                    severity=SignalSeverity.LOW,
                    entity_ids=sorted(company_ids),
                    evidence_ids=evidence_ids,
                    method=f"shared {kind} exact match",
                    false_positive_risk="high",
                    alternative_explanations=["escritório compartilhado", "grupo econômico legítimo", "prestador comum"],
                )
            )
    return signals


def capital_contract_signal(
    company: CompanyProfile,
    contract_value: float,
    review_ratio: float = 0.01,
) -> RiskSignal | None:
    if company.capital is None or company.capital <= 0 or contract_value <= 0:
        return None
    ratio = company.capital / contract_value
    if ratio >= review_ratio:
        return None
    return RiskSignal(
        signal_id=f"CORP-CAPITAL-CONTRACT-{company.company_id}",
        category=SignalCategory.CORPORATE,
        title="Relação capital social/valor contratual para revisão",
        description=f"Relação observada={ratio:.4f}. Capital social baixo não prova incapacidade econômica.",
        severity=SignalSeverity.LOW,
        entity_ids=[company.company_id],
        evidence_ids=company.evidence_ids,
        method="capital / contract value",
        threshold={"review_ratio": review_ratio},
        false_positive_risk="high",
        alternative_explanations=["capital social não mede caixa", "garantias", "consórcio", "capacidade operacional externa"],
    )
