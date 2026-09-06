#!/usr/bin/env python3
"""
Visão Tinker Bell — Export de grafos
Gera GraphML / GEXF a partir de nós e arestas simples.
Compatível com Gephi e NetworkX.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import networkx as nx

    HAS_NX = True
except ImportError:
    HAS_NX = False


def build_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    id_key: str = "id",
    source_key: str = "source",
    target_key: str = "target",
):
    if not HAS_NX:
        raise RuntimeError("networkx não instalado. pip install networkx")

    G = nx.DiGraph()
    for n in nodes:
        nid = n.get(id_key)
        if nid is None:
            continue
        attrs = {k: v for k, v in n.items() if k != id_key}
        G.add_node(nid, **attrs)
    for e in edges:
        s, t = e.get(source_key), e.get(target_key)
        if s is None or t is None:
            continue
        attrs = {k: v for k, v in e.items() if k not in (source_key, target_key)}
        G.add_edge(s, t, **attrs)
    return G


def export_graphml(G, path: Path) -> None:
    nx.write_graphml(G, path)


def export_gexf(G, path: Path) -> None:
    nx.write_gexf(G, path)


def main():
    parser = argparse.ArgumentParser(description="Export GraphML/GEXF — Visão Tinker Bell")
    parser.add_argument("--nodes", required=True, help="JSON array de nós")
    parser.add_argument("--edges", required=True, help="JSON array de arestas")
    parser.add_argument("--out", default="graph_export", help="Prefixo de saída")
    parser.add_argument("--format", choices=["graphml", "gexf", "both"], default="both")
    args = parser.parse_args()

    nodes = json.loads(Path(args.nodes).read_text(encoding="utf-8"))
    edges = json.loads(Path(args.edges).read_text(encoding="utf-8"))
    G = build_graph(nodes, edges)

    out = Path(args.out)
    if args.format in ("graphml", "both"):
        p = out.with_suffix(".graphml")
        export_graphml(G, p)
        print(f"GraphML: {p} ({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)")
    if args.format in ("gexf", "both"):
        p = out.with_suffix(".gexf")
        export_gexf(G, p)
        print(f"GEXF: {p}")


if __name__ == "__main__":
    if not HAS_NX:
        print("Instale networkx: pip install networkx")
    else:
        # Demo mínima
        G = build_graph(
            [
                {"id": "A", "label": "Prefeitura", "tipo": "orgao"},
                {"id": "B", "label": "Fornecedor X", "tipo": "empresa"},
            ],
            [{"source": "A", "target": "B", "valor": 1000000, "tipo": "contrato"}],
        )
        print(f"Demo: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
        print("Use --nodes/--edges para export real.")
