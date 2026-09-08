from __future__ import annotations

import hashlib


def stable_id(prefix: str, *parts: object, length: int = 16) -> str:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:length]
    return f"{prefix}-{digest}"
