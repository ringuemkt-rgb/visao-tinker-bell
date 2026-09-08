from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def normalize_cnpj(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) != 14:
        raise ValueError("CNPJ must contain 14 digits")
    return digits


class JsonlCNPJSnapshot:
    """Adapter local para snapshots previamente adquiridos de fonte pública legítima.

    Não baixa dump, não contorna CAPTCHA e não presume origem. O manifest do dataset
    deve registrar autoridade, competência, data de obtenção, hash e licença/termos.
    """

    def __init__(self, path: str | Path, *, cnpj_field: str = "cnpj") -> None:
        self.path = Path(path)
        self.cnpj_field = cnpj_field
        self._index: dict[str, dict[str, Any]] | None = None

    def _load(self) -> None:
        index: dict[str, dict[str, Any]] = {}
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                raw = str(row.get(self.cnpj_field, ""))
                try:
                    index[normalize_cnpj(raw)] = row
                except ValueError:
                    continue
        self._index = index

    def get_company(self, cnpj: str) -> dict[str, Any] | None:
        if self._index is None:
            self._load()
        assert self._index is not None
        return self._index.get(normalize_cnpj(cnpj))
