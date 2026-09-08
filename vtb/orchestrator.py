from __future__ import annotations

from dataclasses import dataclass, field

from .claims import ClaimLedger
from .gates import GateResult, final_state, publication_gate
from .hypotheses import CompetingHypotheses
from .models import Claim, EvidenceRecord, Hypothesis, MissionState, SourceRecord
from .next_best_query import QueryCandidate, next_best_query
from .red_team import RedTeamResult
from .runtime import CaseStore
from .state_machine import transition


@dataclass
class MissionContext:
    case_id: str
    state: MissionState = MissionState.INTAKE
    ledger: ClaimLedger = field(default_factory=ClaimLedger)
    hypotheses: CompetingHypotheses = field(default_factory=CompetingHypotheses)
    red_team: RedTeamResult = field(default_factory=RedTeamResult)
    gaps: list[str] = field(default_factory=list)
    queries: list[QueryCandidate] = field(default_factory=list)


class TinkerBellEngine:
    def __init__(self, store: CaseStore | None = None):
        self.store = store
        self.cases: dict[str, MissionContext] = {}

    def create_case(self, case_id: str, title: str, question: str, geography: str = "", time_range: str = "") -> MissionContext:
        if case_id in self.cases:
            raise ValueError(f"duplicate case: {case_id}")
        ctx = MissionContext(case_id)
        self.cases[case_id] = ctx
        if self.store:
            self.store.create_mission(case_id, title, question, geography, time_range)
        return ctx

    def advance(self, case_id: str, target: MissionState) -> MissionState:
        ctx = self.cases[case_id]
        ctx.state = transition(ctx.state, target)
        if self.store:
            self.store.set_state(case_id, ctx.state)
        return ctx.state

    def add_source(self, case_id: str, source: SourceRecord) -> None:
        ctx = self.cases[case_id]
        ctx.ledger.add_source(source)
        if self.store:
            self.store.add_source(case_id, source)

    def add_evidence(self, case_id: str, evidence: EvidenceRecord) -> None:
        ctx = self.cases[case_id]
        ctx.ledger.add_evidence(evidence)
        if self.store:
            self.store.add_evidence(case_id, evidence)

    def add_claim(self, case_id: str, claim: Claim, reconcile: bool = True) -> None:
        ctx = self.cases[case_id]
        ctx.ledger.add_claim(claim)
        if reconcile:
            ctx.ledger.reconcile(claim.claim_id)
        if self.store:
            self.store.add_claim(case_id, claim)

    def add_hypothesis(self, case_id: str, hypothesis: Hypothesis) -> None:
        ctx = self.cases[case_id]
        ctx.hypotheses.add_hypothesis(hypothesis.hypothesis_id, hypothesis.statement)
        if self.store:
            self.store.add_hypothesis(case_id, hypothesis)

    def add_gap(self, case_id: str, gap: str) -> None:
        self.cases[case_id].gaps.append(gap)

    def add_query_candidate(self, case_id: str, candidate: QueryCandidate) -> None:
        self.cases[case_id].queries.append(candidate)

    def next_query(self, case_id: str) -> QueryCandidate | None:
        return next_best_query(self.cases[case_id].queries)

    def decision(self, case_id: str, legal_review_done: bool = True) -> tuple[GateResult, MissionState]:
        ctx = self.cases[case_id]
        gate = publication_gate(ctx.ledger, ctx.red_team.passed, legal_review_done)
        material = any(c.materiality in {"high", "critical"} for c in ctx.ledger.claims.values())
        state = final_state(gate, material, bool(ctx.gaps))
        return gate, state
