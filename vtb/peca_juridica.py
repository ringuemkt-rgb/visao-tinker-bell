"""Elementos da representacao. Nao e peticao de merito nem peca para calar defesa.

Lei 14.230/2021 tirou a modalidade culposa da improbidade. O art. 1º, § 2º,
da Lei 8.429/1992 define dolo como vontade livre e consciente de alcançar
o resultado ilicito tipificado. Sem esse elemento, o fato fica em apuracao.
A hipotese da defesa entra na peca. Omissao vira fragilidade, nao arma.
"""

from __future__ import annotations

from typing import Any

ELEMENTOS = (
    "competencia",
    "ato_concreto",
    "data",
    "documento",
    "url",
    "sha256",
    "o_que_nao_se_afirma",
    "hipotese_defesa",
)

PEDIDOS_VEDADOS = (
    "condenacao",
    "indisponibilidade",
    "prisao",
    "busca e apreensao",
    "interceptacao",
    "afastamento",
)


def checar(fato: dict[str, Any]) -> list[str]:
    faltas = [chave for chave in ELEMENTOS if not str(fato.get(chave) or "").strip()]
    pedido = (fato.get("pedido") or "").lower()
    if any(termo in pedido for termo in PEDIDOS_VEDADOS):
        faltas.append("pedido_vedado_em_noticia_anonima")
    return faltas


def hipotese_defesa(fato: dict[str, Any]) -> str:
    texto = (fato.get("hipotese_defesa") or "").strip()
    if texto:
        return texto
    return (
        "Hipotese defensiva em aberto: ato regular, erro sem dolo, homonimo, "
        "empenho ainda nao pago, ou processo sem decisao. Nao ha neste conjunto "
        "prova de vontade de alcancar resultado ilicito."
    )


def nucleo(meta: dict[str, Any], fatos: list[dict[str, Any]]) -> str:
    linhas = [
        "REPRESENTACAO PARA APURACAO",
        f"Destino: {meta.get('destino', 'ouvidoria competente')}.",
        f"Orgao: {meta.get('orgao', 'nao indicado')}. Cargo citado: {meta.get('agente', 'nao indicado')}.",
        "",
        "1. Competencia e limite",
        "Noticia de fato para apuracao. Nao pede condenacao, busca, interceptacao nem afastamento.",
        "Denuncia anonima, sozinha, nao autoriza medida invasiva. STF, HC 106.152.",
        "Improbidade, apos a Lei 14.230/2021, exige dolo: vontade livre e consciente de alcancar o resultado tipificado (Lei 8.429/1992, art. 1, par. 2). Culpa grave nao basta.",
        "",
        "2. Atos concretos",
    ]
    if not fatos:
        linhas.append("Nenhum ato com documento, URL, hash e hipotese de defesa.")
    for indice, fato in enumerate(fatos, start=1):
        faltas = checar(fato)
        if faltas:
            linhas.append(f"{indice}. Fora da peca. Falta: {', '.join(faltas)}.")
            continue
        linhas.append(
            f"{indice}. Em {fato['data']}, {fato['ato_concreto']} "
            f"Documento: {fato['documento']}. URL: {fato['url']}. SHA-256: {fato['sha256']}. "
            f"Nao se afirma: {fato['o_que_nao_se_afirma']}. "
            f"Defesa possivel: {hipotese_defesa(fato)}"
        )
    linhas.extend([
        "",
        "3. Prova",
        "So entra captura do documento oficial ja citado, com a mesma URL e o mesmo hash. Print sem fonte nao e prova.",
        "",
        "4. Pedido",
        "Apuracao dos atos acima, com ciencia do apontado e contraditorio. Sem juizo de ilicito nesta peca.",
    ])
    return "\n".join(linhas)
