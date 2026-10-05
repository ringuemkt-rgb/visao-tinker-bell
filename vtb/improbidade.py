"""Teste de improbidade. Tema 1199 do STF e pratica do STJ. Nao condena.

STF, ARE 843.989, Tema 1199: arts. 9, 10 e 11 da Lei 8.429/1992 exigem dolo.
A revogacao da culpa nao desfaz coisa julgada. Em processo sem transito, o juizo
reexamina o dolo. A prescricao nova nao volta no tempo.

STJ, Tema 1397: afetado para dizer se o dolo especifico vale para todos os tipos.
Em maio de 2026 o relator votou pela exigencia e o julgamento parou em vista.
Ate o tema fechar, a peca nao chama o fato de improbidade.
"""

from __future__ import annotations

from typing import Any

TEMA_1199 = (
    "Dolo exigido nos arts. 9, 10 e 11.",
    "Culpa revogada nao desfaz coisa julgada nem execucao.",
    "Sem transito, o juizo reexamina o dolo.",
    "Prescricao nova nao retroage.",
)

ROTULO_PERMITIDO = "ANOMALY_FOR_VERIFICATION"


def avaliar(fato: dict[str, Any]) -> dict[str, Any]:
    faltas: list[str] = []
    if not fato.get("ato_concreto"):
        faltas.append("ato_concreto")
    if not fato.get("resultado_tipificado"):
        faltas.append("resultado_tipificado")
    if not fato.get("vontade_de_alcancar_resultado"):
        faltas.append("dolo_nao_demonstrado")
    if fato.get("so_culpa") or fato.get("so_culpa_grave"):
        faltas.append("culpa_nao_basta")
    if not fato.get("hipotese_defesa"):
        faltas.append("hipotese_defesa")
    if not fato.get("sha256") or not fato.get("url"):
        faltas.append("fonte_primaria")
    rotulo = (fato.get("rotulo") or "").lower()
    if any(termo in rotulo for termo in ("improbo", "improbidade", "corrup")):
        faltas.append("rotulo_vedado")
    return {
        "label": ROTULO_PERMITIDO,
        "improbidade_afirmavel": False,
        "tema": "STF 1199",
        "stj": "Tema 1397 em aberto; nao tratar dolo especifico como tese fechada",
        "teses": list(TEMA_1199),
        "faltas": faltas,
    }


def bloco(fato: dict[str, Any]) -> str:
    exame = avaliar(fato)
    faltas = ", ".join(exame["faltas"]) or "nenhuma lacuna formal, ainda sem dolo bastante para rotulo"
    return (
        "Enquadramento. Nao e improbidade nesta peca. "
        "Tema 1199: dolo nos arts. 9, 10 e 11; culpa nao basta; sem transito o juizo reexamina. "
        f"Tema 1397 do STJ em aberto. Lacunas: {faltas}."
    )
