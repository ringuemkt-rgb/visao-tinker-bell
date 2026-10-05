"""Busca e leitura de documento oficial. O texto extraido nao e fato juridico.

So entra URL https de host publico da lista. O arquivo ganha SHA-256.
Termo achado no texto e ocorrencia, nao irregularidade e nao improbidade.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HOSTS = (
    "portaldatransparencia.gov.br",
    "pncp.gov.br",
    "in.gov.br",
    "tse.jus.br",
    "cgu.gov.br",
    "camara.leg.br",
    "senado.leg.br",
    "dados.gov.br",
    "gov.br",
)
MAX_BYTES = 15 * 1024 * 1024


def host_ok(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and any(host == item or host.endswith("." + item) for item in HOSTS)


def baixar(url: str, destino: str | Path) -> Path:
    if not host_ok(url):
        raise ValueError("host fora da lista oficial")
    path = Path(destino)
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "VisaoTinkerBell/documentos"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_BYTES + 1)
        status = getattr(response, "status", 0)
    if status and status >= 400:
        raise ValueError(f"http {status}")
    if len(data) > MAX_BYTES:
        raise ValueError("arquivo acima de 15 MB")
    path.write_bytes(data)
    return path


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ler_texto(path: str | Path) -> str:
    file_path = Path(path)
    raw = file_path.read_bytes()
    if raw.startswith(b"%PDF"):
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""
        reader = PdfReader(str(file_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return raw.decode("utf-8", errors="replace")


def analisar(path: str | Path, url: str, termos: list[str]) -> dict[str, Any]:
    texto = ler_texto(path)
    achados = []
    for termo in termos:
        if not termo:
            continue
        for match in re.finditer(re.escape(termo), texto, flags=re.IGNORECASE):
            inicio = max(0, match.start() - 80)
            achados.append({"termo": termo, "trecho": texto[inicio:match.end() + 80].replace("\n", " ")})
            if len(achados) >= 20:
                break
    return {
        "url": url,
        "sha256": sha256(path),
        "bytes": Path(path).stat().st_size,
        "ocorrencias": achados,
        "label": "ANOMALY_FOR_VERIFICATION",
        "improbidade_afirmavel": False,
        "nota": "Ocorrencia no documento. Nao e irregularidade nem dolo.",
    }


def buscar_pncp(data_inicial: str, data_final: str, pagina: int = 1) -> dict[str, Any]:
    query = urllib.parse.urlencode({
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": 6,
        "pagina": pagina,
    })
    url = f"https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?{query}"
    if not host_ok(url):
        raise ValueError("host fora da lista oficial")
    request = urllib.request.Request(url, headers={"User-Agent": "VisaoTinkerBell/documentos", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read(MAX_BYTES))
    itens = payload.get("data") or payload.get("items") or []
    return {
        "url": url,
        "total": payload.get("totalRegistros") or payload.get("count") or len(itens),
        "itens": itens[:20],
        "label": "LEAD",
        "nota": "Lista publica. Nao e fato sobre um alvo.",
    }
