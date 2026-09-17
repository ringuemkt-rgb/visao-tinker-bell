from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Claim, EvidenceRecord, Hypothesis, MissionState, SourceRecord, utcnow
from .state_machine import transition

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS missions (
  case_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  question TEXT NOT NULL,
  geography TEXT,
  time_range TEXT,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (
  case_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, source_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS evidence (
  case_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, evidence_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE,
  FOREIGN KEY(case_id, source_id) REFERENCES sources(case_id, source_id)
);
CREATE TABLE IF NOT EXISTS claims (
  case_id TEXT NOT NULL,
  claim_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, claim_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS hypotheses (
  case_id TEXT NOT NULL,
  hypothesis_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, hypothesis_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS searches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL,
  query TEXT NOT NULL,
  source TEXT,
  result_class TEXT,
  source_health TEXT,
  executed_at TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS tool_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL,
  tool_id TEXT NOT NULL,
  status TEXT NOT NULL,
  input_json TEXT,
  output_json TEXT,
  error TEXT,
  executed_at TEXT NOT NULL,
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(case_id) REFERENCES missions(case_id) ON DELETE CASCADE
);
"""


class CaseStore:
    """SQLite case ledger with enforced integrity and an append-only audit trail."""

    def __init__(self, path: str | Path = "data/vtb.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=30.0)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA busy_timeout = 30000")
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def _audit(self, case_id: str, event_type: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO audit_events(case_id,event_type,payload,created_at) VALUES(?,?,?,?)",
            (case_id, event_type, json.dumps(payload, ensure_ascii=False, default=str), utcnow()),
        )

    def create_mission(
        self, case_id: str, title: str, question: str, geography: str = "", time_range: str = ""
    ) -> None:
        now = utcnow()
        self.db.execute(
            "INSERT INTO missions(case_id,title,question,geography,time_range,state,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (case_id, title, question, geography, time_range, MissionState.INTAKE, now, now),
        )
        self._audit(case_id, "MISSION_CREATED", {"title": title, "question": question})
        self.db.commit()

    def mission(self, case_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM missions WHERE case_id=?", (case_id,)).fetchone()
        if not row:
            raise KeyError(case_id)
        return dict(row)

    def set_state(self, case_id: str, state: MissionState) -> None:
        current = MissionState(self.mission(case_id)["state"])
        target = MissionState(state)
        transition(current, target)
        self.db.execute("UPDATE missions SET state=?, updated_at=? WHERE case_id=?", (target, utcnow(), case_id))
        self._audit(case_id, "MISSION_STATE_CHANGED", {"from": current, "to": target})
        self.db.commit()

    def _upsert_payload(
        self, table: str, case_id: str, key_name: str, key: str, payload: dict[str, Any]
    ) -> None:
        if table not in {"sources", "evidence", "claims", "hypotheses"}:
            raise ValueError("unsupported table")
        self.mission(case_id)
        columns = f"case_id,{key_name},payload"
        values: tuple[Any, ...] = (case_id, key, json.dumps(payload, ensure_ascii=False, default=str))
        if table == "evidence":
            source_id = str(payload.get("source_id", ""))
            if not source_id:
                raise ValueError("evidence requires source_id")
            columns = f"case_id,{key_name},source_id,payload"
            values = (case_id, key, source_id, json.dumps(payload, ensure_ascii=False, default=str))
        sql = (
            f"INSERT INTO {table}({columns}) VALUES({','.join('?' for _ in values)}) "
            f"ON CONFLICT(case_id,{key_name}) DO UPDATE SET payload=excluded.payload"
        )
        self.db.execute(sql, values)
        self._audit(case_id, f"{table.upper()}_UPSERTED", {key_name: key})
        self.db.commit()

    def add_source(self, case_id: str, source: SourceRecord) -> None:
        self._upsert_payload("sources", case_id, "source_id", source.source_id, source.to_dict())

    def add_evidence(self, case_id: str, evidence: EvidenceRecord) -> None:
        self._upsert_payload("evidence", case_id, "evidence_id", evidence.evidence_id, evidence.to_dict())

    def add_claim(self, case_id: str, claim: Claim) -> None:
        self._upsert_payload("claims", case_id, "claim_id", claim.claim_id, claim.to_dict())

    def add_hypothesis(self, case_id: str, hypothesis: Hypothesis) -> None:
        self._upsert_payload("hypotheses", case_id, "hypothesis_id", hypothesis.hypothesis_id, hypothesis.to_dict())

    def log_search(
        self, case_id: str, query: str, source: str = "", result_class: str = "",
        source_health: str = "", notes: str = ""
    ) -> None:
        self.mission(case_id)
        self.db.execute(
            "INSERT INTO searches(case_id,query,source,result_class,source_health,executed_at,notes) "
            "VALUES(?,?,?,?,?,?,?)",
            (case_id, query, source, result_class, source_health, utcnow(), notes),
        )
        self._audit(case_id, "SEARCH_LOGGED", {"source": source, "result_class": result_class})
        self.db.commit()

    def log_tool_run(
        self, case_id: str, tool_id: str, status: str, input_data: Any = None,
        output_data: Any = None, error: str = ""
    ) -> None:
        self.mission(case_id)
        self.db.execute(
            "INSERT INTO tool_runs(case_id,tool_id,status,input_json,output_json,error,executed_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (case_id, tool_id, status, json.dumps(input_data, default=str),
             json.dumps(output_data, default=str), error, utcnow()),
        )
        self._audit(case_id, "TOOL_RUN_LOGGED", {"tool_id": tool_id, "status": status})
        self.db.commit()

    def audit_events(self, case_id: str) -> list[dict[str, Any]]:
        self.mission(case_id)
        rows = self.db.execute(
            "SELECT id,event_type,payload,created_at FROM audit_events WHERE case_id=? ORDER BY id", (case_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def export_case(self, case_id: str) -> dict[str, Any]:
        """Return a deterministic, JSON-safe case snapshot for evidence books and replay."""
        mission = self.mission(case_id)
        tables = {"sources": "source_id", "evidence": "evidence_id", "claims": "claim_id", "hypotheses": "hypothesis_id"}
        snapshot: dict[str, Any] = {"mission": mission}
        for table, key in tables.items():
            rows = self.db.execute(
                f"SELECT {key},payload FROM {table} WHERE case_id=? ORDER BY {key}", (case_id,)
            ).fetchall()
            snapshot[table] = [{key: row[key], "payload": json.loads(row["payload"])} for row in rows]
        snapshot["searches"] = [dict(row) for row in self.db.execute(
            "SELECT query,source,result_class,source_health,executed_at,notes FROM searches WHERE case_id=? ORDER BY id",
            (case_id,),
        ).fetchall()]
        snapshot["tool_runs"] = [dict(row) for row in self.db.execute(
            "SELECT tool_id,status,input_json,output_json,error,executed_at FROM tool_runs WHERE case_id=? ORDER BY id",
            (case_id,),
        ).fetchall()]
        snapshot["audit_events"] = self.audit_events(case_id)
        return snapshot

    def write_case_export(self, case_id: str, destination: str | Path) -> Path:
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.export_case(case_id), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return output
