#!/usr/bin/env python3
"""
Visão Tinker Bell — Entity Resolution básica
Match por CPF/CNPJ (exato) e nomes (fuzzy).
Apenas dados já públicos.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple


def normalize_name(name: str) -> str:
    name = (name or "").upper().strip()
    name = re.sub(r"[^\w\s]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", " ", name)
    return name


def normalize_document(doc: str) -> str:
    return re.sub(r"\D", "", doc or "")


class EntityResolver:
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}

    def add_entity(
        self,
        entity_id: str,
        name: str,
        documents: Optional[List[str]] = None,
        aliases: Optional[List[str]] = None,
        meta: Optional[Dict] = None,
    ) -> None:
        self.entities[entity_id] = {
            "id": entity_id,
            "name": name,
            "name_norm": normalize_name(name),
            "documents": [normalize_document(d) for d in (documents or []) if d],
            "aliases": [normalize_name(a) for a in (aliases or [])],
            "meta": meta or {},
        }

    def match_documents(self, doc1: str, doc2: str) -> bool:
        return normalize_document(doc1) == normalize_document(doc2) and bool(
            normalize_document(doc1)
        )

    def match_names(
        self, name1: str, name2: str, threshold: float = 0.85
    ) -> Tuple[bool, float]:
        n1, n2 = normalize_name(name1), normalize_name(name2)
        if not n1 or not n2:
            return False, 0.0
        ratio = SequenceMatcher(None, n1, n2).ratio()
        return ratio >= threshold, ratio

    def find_matches(
        self,
        name: str,
        documents: Optional[List[str]] = None,
        threshold: float = 0.85,
    ) -> List[Tuple[str, str, float]]:
        """Retorna lista de (entity_id, method, confidence)."""
        results: List[Tuple[str, str, float]] = []
        docs_norm = [normalize_document(d) for d in (documents or []) if d]
        name_norm = normalize_name(name)

        for eid, ent in self.entities.items():
            # Documento exato
            for d in docs_norm:
                if d and d in ent["documents"]:
                    results.append((eid, "DOCUMENT_EXACT", 1.0))
                    break
            else:
                # Nome fuzzy
                candidates = [ent["name_norm"]] + ent["aliases"]
                best = 0.0
                for c in candidates:
                    ok, ratio = self.match_names(name_norm, c, threshold)
                    if ok and ratio > best:
                        best = ratio
                if best >= threshold:
                    results.append((eid, "NAME_FUZZY", best))

        # Dedup por id (melhor confiança)
        best_by_id: Dict[str, Tuple[str, float]] = {}
        for eid, method, conf in results:
            if eid not in best_by_id or conf > best_by_id[eid][1]:
                best_by_id[eid] = (method, conf)
        return sorted(
            [(eid, m, c) for eid, (m, c) in best_by_id.items()],
            key=lambda x: x[2],
            reverse=True,
        )


if __name__ == "__main__":
    r = EntityResolver()
    r.add_entity(
        "P1",
        "Reges Jonas Aragão Santos",
        documents=["006.362.775-26"],
        aliases=["Reges Aragão", "Reges Aragão Santos"],
    )
    matches = r.find_matches("REGES ARAGÃO", ["00636277526"])
    print("Matches:", matches)
