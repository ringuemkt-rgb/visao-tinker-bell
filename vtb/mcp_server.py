from __future__ import annotations

import json
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .case_bundle import verify_case_bundle, write_case_bundle
from .models import MissionState
from .next_best_query import QueryCandidate, rank_queries
from .preservation import preserve_bytes, verify_manifest, write_manifest
from .runtime import CaseStore
from .signals import RiskSignal, SignalCategory, SignalSeverity, triage_band
from .source_health import classify_http_status, negative_result_label

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised when optional extra is missing
    raise RuntimeError("Instale o extra MCP com: pip install -e '.[mcp]'") from exc


mcp = FastMCP(
    "Tinker Bell Forensic Intelligence",
    instructions=(
        "Use o Tinker Bell para investigação defensiva baseada em fontes autorizadas ou públicas. "
        "Sinais, matches e anomalias são triagem, nunca prova de crime ou identidade. "
        "Não faça bypass de autenticação, scraping agressivo, deanonymização ou vigilância indiscriminada."
    ),
)


def _db_path() -> str:
    return os.environ.get("VTB_DB", "data/vtb.sqlite3")


def _store() -> CaseStore:
    return CaseStore(_db_path())


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _safe_artifact_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    if not name:
        raise ValueError("artifact_id inválido")
    return name[:120]


@mcp.tool()
def source_health(http_status: int | None) -> str:
    """Classifica a saúde de uma fonte HTTP sem inferir ausência de informação."""
    health = classify_http_status(http_status)
    return _json({"health": health, "negative_interpretation": negative_result_label(health)})


@mcp.tool()
def mission_init(case_id: str, title: str, question: str, geography: str = "", time_range: str = "") -> str:
    """Cria um caso investigativo local, com pergunta e escopo explícitos."""
    store = _store()
    try:
        store.create_mission(case_id, title, question, geography, time_range)
        return _json(store.mission(case_id))
    finally:
        store.close()


@mcp.tool()
def mission_status(case_id: str) -> str:
    """Retorna o estado atual e o escopo registrado de um caso."""
    store = _store()
    try:
        return _json(store.mission(case_id))
    finally:
        store.close()


@mcp.tool()
def mission_transition(case_id: str, target_state: str) -> str:
    """Avança um caso somente por uma transição permitida pela máquina de estados."""
    store = _store()
    try:
        target = MissionState(target_state)
        store.set_state(case_id, target)
        return _json(store.mission(case_id))
    finally:
        store.close()


@mcp.tool()
def case_export(case_id: str) -> str:
    """Exporta um snapshot JSON reproduzível de missão, evidências e auditoria."""
    store = _store()
    try:
        return _json(store.export_case(case_id))
    finally:
        store.close()


@mcp.tool()
def case_bundle(case_id: str, destination: str) -> str:
    """Cria um pacote de caso versionável por Git com case.json e manifesto SHA-256."""
    store = _store()
    try:
        bundle = write_case_bundle(store, case_id, destination)
        return _json({"case_id": case_id, "bundle": str(bundle), "format": "vtb-case-bundle-v1"})
    finally:
        store.close()


@mcp.tool()
def case_bundle_verify(bundle_path: str) -> str:
    """Verifica arquivos e hashes de um pacote de caso versionável."""
    valid, reasons = verify_case_bundle(bundle_path)
    return _json({"valid": valid, "reasons": reasons, "bundle": bundle_path})


@mcp.tool()
def case_audit(case_id: str) -> str:
    """Lista os eventos de auditoria append-only de um caso."""
    store = _store()
    try:
        return _json(store.audit_events(case_id))
    finally:
        store.close()


@mcp.tool()
def manifest_verify(manifest_path: str) -> str:
    """Verifica SHA-256 e tamanho de um artefato preservado por manifesto."""
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    valid, reasons = verify_manifest(manifest)
    return _json({"valid": valid, "reasons": reasons, "manifest_path": str(path)})


@mcp.tool()
def evaluate_red_flags(context: dict[str, Any]) -> str:
    """Avalia regras determinísticas locais; retorna sinais para revisão, não acusações."""
    from lib.red_flags_engine import load_engine

    findings = load_engine().evaluate(context)
    normalized = []
    for finding in findings:
        if hasattr(finding, "__dataclass_fields__"):
            normalized.append(asdict(finding))
        else:
            normalized.append({"finding": str(finding)})
    return _json({"status": "ANOMALY_FOR_VERIFICATION", "findings": normalized, "disclaimer": "Red flag não é prova."})


@mcp.tool()
def red_flag_catalog() -> str:
    """Lista regras declarativas, seus dados necessários e estado de implementação."""
    path = Path(__file__).parent.parent / "rules" / "red_flags.json"
    rules = json.loads(path.read_text(encoding="utf-8"))
    return _json({
        "count": len(rules),
        "implemented": sum(bool(rule.get("implementada")) for rule in rules),
        "rules": [
            {key: rule.get(key) for key in ("id", "nome", "categoria", "descricao", "dados_necessarios", "apis", "severidade", "implementada")}
            for rule in rules
        ],
    })


@mcp.tool()
def next_best_queries(candidates: list[dict[str, Any]]) -> str:
    """Classifica consultas candidatas por ganho informacional, materialidade e fonte primária."""
    parsed = [
        QueryCandidate(
            query=str(item["query"]),
            purpose=str(item.get("purpose", "")),
            expected_information_gain=float(item.get("expected_information_gain", 0)),
            materiality=float(item.get("materiality", 1)),
            primary_source_bonus=float(item.get("primary_source_bonus", 0)),
            contradiction_bonus=float(item.get("contradiction_bonus", 0)),
            cost=float(item.get("cost", 1)),
        )
        for item in candidates
    ]
    return _json({"queries": [{"query": q.query, "purpose": q.purpose, "score": q.score} for q in rank_queries(parsed)], "human_review_required": True})


@mcp.tool()
def preserve_navigation_snapshot(artifact_id: str, source_url: str, content: str, case_id: str = "") -> str:
    """Preserva conteúdo fornecido pelo cliente com URL, timestamp, hash e manifesto; não navega na internet."""
    safe_id = _safe_artifact_name(artifact_id)
    root = Path(os.environ.get("VTB_ARTIFACT_DIR", "data/artifacts")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    destination = (root / f"{safe_id}.txt").resolve()
    if root not in destination.parents:
        raise ValueError("destino de artefato inválido")
    manifest = preserve_bytes(content.encode("utf-8"), destination, safe_id, source_url, "mcp-client-supplied")
    manifest_path = root / f"{safe_id}.manifest.json"
    write_manifest(manifest, manifest_path)
    return _json({"case_id": case_id, "manifest": asdict(manifest), "manifest_path": str(manifest_path), "navigation_performed": False})


@mcp.tool()
def triage_signals(signals: list[dict[str, Any]]) -> str:
    """Calcula uma banda de prioridade a partir de sinais já documentados."""
    parsed: list[RiskSignal] = []
    for item in signals:
        parsed.append(
            RiskSignal(
                signal_id=str(item["signal_id"]),
                category=SignalCategory(str(item.get("category", "DOCUMENT"))),
                title=str(item.get("title", "")),
                description=str(item.get("description", "")),
                severity=SignalSeverity(str(item.get("severity", "INFO"))),
                entity_ids=[str(x) for x in item.get("entity_ids", [])],
                evidence_ids=[str(x) for x in item.get("evidence_ids", [])],
                method=str(item.get("method", "")),
                threshold=dict(item.get("threshold", {})),
                false_positive_risk=str(item.get("false_positive_risk", "unknown")),
                alternative_explanations=[str(x) for x in item.get("alternative_explanations", [])],
            )
        )
    return _json({"triage_band": triage_band(parsed), "signal_count": len(parsed), "not_a_finding_of_guilt": True})


def main() -> None:
    transport = os.environ.get("VTB_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "streamable-http", "sse"}:
        raise SystemExit("VTB_MCP_TRANSPORT deve ser stdio, streamable-http ou sse")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
