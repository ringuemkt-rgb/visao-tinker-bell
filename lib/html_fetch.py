#!/usr/bin/env python3
"""
Visão Tinker Bell — Fallback HTML (quando NÃO há API oficial)
Usa Scrapling se instalado; senão requests simples.
Sempre grava snapshot + SHA-256 (cadeia de custódia).

Política:
  1) Preferir APIs oficiais (PNCP, TSE, Portal, BrasilAPI).
  2) Este módulo só para portais públicos sem API.
  3) Respeitar robots.txt quando possível.
  4) Não usar stealth para contornar autenticação ou áreas privadas.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

HEADERS = {
    "User-Agent": "VisaoTinkerBell/0.4 (+https://github.com/ringuemkt-rgb/visao-tinker-bell; pesquisa-transparencia; evidence-only)",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8", errors="replace"))


def allowed_by_robots(url: str, user_agent: str = "VisaoTinkerBell") -> bool:
    """Consulta robots.txt. Em falha de rede, retorna True (não bloqueia coleta pública legítima)."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def _fetch_requests(url: str, timeout: int = 30) -> Dict[str, Any]:
    import requests

    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    text = r.text
    return {
        "url": url,
        "status": r.status_code,
        "html": text,
        "engine": "requests",
        "final_url": str(r.url),
        "sha256": _sha256_text(text),
    }


def _fetch_scrapling(
    url: str,
    stealth: bool = False,
    headless: bool = True,
) -> Dict[str, Any]:
    if stealth:
        from scrapling.fetchers import StealthyFetcher

        page = StealthyFetcher.fetch(url, headless=headless, network_idle=True)
        engine = "scrapling.StealthyFetcher"
    else:
        from scrapling.fetchers import Fetcher

        page = Fetcher.get(url)
        engine = "scrapling.Fetcher"

    html = getattr(page, "html_content", None) or getattr(page, "body", None) or str(page)
    if not isinstance(html, str):
        html = str(html)
    status = getattr(page, "status", 200)
    return {
        "url": url,
        "status": status,
        "html": html,
        "engine": engine,
        "final_url": getattr(page, "url", url),
        "sha256": _sha256_text(html),
        "page": page,  # objeto para css/xpath se caller quiser
    }


def fetch_public_html(
    url: str,
    *,
    respect_robots: bool = True,
    prefer_scrapling: bool = True,
    stealth: bool = False,
    save_dir: Optional[Path] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Baixa HTML público e opcionalmente persiste evidência.

    Retorno:
      url, status, html, engine, sha256, final_url,
      evidence_path (se save_dir), robots_allowed
    """
    if respect_robots and not allowed_by_robots(url):
        return {
            "url": url,
            "status": None,
            "html": None,
            "engine": None,
            "sha256": None,
            "robots_allowed": False,
            "erro": "robots.txt Disallow para este user-agent",
        }

    result: Dict[str, Any] = {"robots_allowed": True}
    used_scrapling = False

    if prefer_scrapling:
        try:
            result.update(_fetch_scrapling(url, stealth=stealth))
            used_scrapling = True
        except ImportError:
            result.update(_fetch_requests(url, timeout=timeout))
        except Exception as e:
            # fallback requests se scrapling falhar
            try:
                result.update(_fetch_requests(url, timeout=timeout))
                result["scrapling_error"] = str(e)
            except Exception as e2:
                return {
                    "url": url,
                    "erro": f"scrapling: {e}; requests: {e2}",
                    "robots_allowed": True,
                }
    else:
        result.update(_fetch_requests(url, timeout=timeout))

    result["access_date"] = datetime.now(timezone.utc).isoformat()

    if save_dir is not None and result.get("html"):
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        host = re.sub(r"[^\w.-]", "_", urlparse(url).netloc)[:80]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = save_dir / f"{host}_{stamp}"
        html_path = base.with_suffix(".html")
        evidence_path = base.with_suffix(".evidence.yaml")
        html_path.write_text(result["html"], encoding="utf-8")
        evidence = (
            f"# Evidência HTML — Visão Tinker Bell\n"
            f"source: {url}\n"
            f"final_url: {result.get('final_url')}\n"
            f"access_date: {result['access_date']}\n"
            f"engine: {result.get('engine')}\n"
            f"status: {result.get('status')}\n"
            f"sha256: {result.get('sha256')}\n"
            f"file: {html_path.name}\n"
            f"size_bytes: {html_path.stat().st_size}\n"
            f"stealth: {stealth}\n"
            f"scrapling_used: {used_scrapling}\n"
        )
        evidence_path.write_text(evidence, encoding="utf-8")
        result["html_path"] = str(html_path)
        result["evidence_path"] = str(evidence_path)

    # não serializar objeto page em dumps padrão
    result.pop("page", None)
    return result


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m lib.html_fetch URL [--save DIR] [--stealth]")
        sys.exit(0)
    url = sys.argv[1]
    save = None
    stealth = "--stealth" in sys.argv
    if "--save" in sys.argv:
        i = sys.argv.index("--save")
        save = Path(sys.argv[i + 1])
    out = fetch_public_html(url, save_dir=save, stealth=stealth)
    # não imprimir HTML inteiro
    slim = {k: v for k, v in out.items() if k != "html"}
    if out.get("html"):
        slim["html_len"] = len(out["html"])
    print(json.dumps(slim, ensure_ascii=False, indent=2))
