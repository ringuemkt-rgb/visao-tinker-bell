#!/usr/bin/env python3
"""Exemplo: fallback HTML com cadeia de custódia."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.html_fetch import fetch_public_html


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    out_dir = Path("data/raw/html")
    result = fetch_public_html(url, save_dir=out_dir, stealth=False)
    print("engine:", result.get("engine"))
    print("status:", result.get("status"))
    print("sha256:", (result.get("sha256") or "")[:16], "...")
    print("evidence:", result.get("evidence_path"))
    if result.get("erro"):
        print("erro:", result["erro"])


if __name__ == "__main__":
    main()
