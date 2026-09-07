from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Claim, EvidenceRecord, Hypothesis, MissionState, SourceRecord, utcnow


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
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
);
CREATE TABLE IF NOT EXISTS evidence (
  case_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, evidence_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
);
CREATE TABLE IF NOT EXISTS claims (
  case_id TEXT NOT NULL,
  claim_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, claim_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
);
CREATE TABLE IF NOT EXISTS hypotheses (
  case_id TEXT NOT NULL,
  hypothesis_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  PRIMARY KEY (case_id, hypothesis_id),
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
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
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
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
  FOREIGN KEY(case_id) REFERENCES missions(case_id)
);
"""


class CaseStore:
    def __init__(self, path: str | Path = "data/vtb.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def create_mission(self, case_id: str, title: str, question: str, geography: str = "", time_range: str = "") -> None:
        now = utcnow()
        self.db.execute(
            "INSERT INTO missions(case_id,title,question,geography,time_range,state,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
            (case_id, title, question, geography, time_range, MissionState.INTAKE, now, now),
        )
        self.db.commit()

    def mission(self, case_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM missions WHERE case_id=?", (case_id,)).fetchone()
        if not row:
            raise KeyError(case_id)
        return dict(row)

    def set_state(self, case_id: str, state: MissionState) -> None:
        self.db.execute("UPDATE missions SET state=?, updated_at=? WHERE case_id=?", (state, utcnow(), case_id))
        self.db.commit()

    def _upsert_payload(self, table: str, case_id: str, key_name: str, key: str, payload: dict[str, Any]) -> None:
        if table not in {"sources", "evidence", "claims", "hypotheses"}:
            raise ValueError("unsupported table")
        sql = f"INSERT INTO {table}(case_id,{key_name},payload) VALUES(?,?,?) ON CONFLICT(case_id,{key_name}) DO UPDATE SET payload=excluded.payload"
        self.db.execute(sql, (case_id, key, json.dumps(payload, ensure_ascii=False, default=str)))
        self.db.commit()

    def add_source(self, case_id: str, source: SourceRecord) -> None:
        self._upsert_payload("sources", case_id, "source_id", source.source_id, source.to_dict())

    def add_evidence(self, case_id: str, evidence: EvidenceRecord) -> None:
        self._upsert_payload("evidence", case_id, "evidence_id", evidence.evidence_id, evidence.to_dict())

    def add_claim(self, case_id: str, claim: Claim) -> None:
        self._upsert_payload("claims", case_id, "claim_id", claim.claim_id, claim.to_dict())

    def add_hypothesis(self, case_id: str, hypothesis: Hypothesis) -> None:
        self._upsert_payload("hypotheses", case_id, "hypothesis_id", hypothesis.hypothesis_id, hypothesis.to_dict())

    def log_search(self, case_id: str, query: str, source: str = "", result_class: str = "", source_health: str = "", notes: str = "") -> None:
        self.db.execute(
            "INSERT INTO searches(case_id,query,source,result_class,source_health,executed_at,notes) VALUES(?,?,?,?,?,?,?)",
            (case_id, query, source, result_class, source_health, utcnow(), notes),
        )
        self.db.commit()

    def log_tool_run(self, case_id: str, tool_id: str, status: str, input_data: Any = None, output_data: Any = None, error: str = "") -> None:
        self.db.execute(
            "INSERT INTO tool_runs(case_id,tool_id,status,input_json,output_json,error,executed_at) VALUES(?,?,?,?,?,?,?)",
            (case_id, tool_id, status, json.dumps(input_data, default=str), json.dumps(output_data, default=str), error, utcnow()),
        )
        self.db.commit()
