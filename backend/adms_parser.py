from __future__ import annotations

import re
from typing import Any


_KV_RE = re.compile(r"(?P<k>[A-Za-z0-9_]+)=(?P<v>[^\t\r\n]+)")


def parse_essl_payload(raw: str) -> list[dict[str, Any]]:
    """
    eSSL ADMS pushes vary by model/firmware. Common formats include:
      - Tab-separated key/value: "PIN=1\tName=John\tDateTime=2026-03-09 10:00:00\t..."
      - CSV-ish: "1,2026-03-09 10:00:00,0,0,..."
      - Multi-line batches

    We parse each non-empty line into a dict.
    """
    events: list[dict[str, Any]] = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line:
            continue

        kvs = {m.group("k"): m.group("v") for m in _KV_RE.finditer(line)}
        if kvs:
            events.append(kvs)
            continue

        # Fallback: comma-separated, assume first column is PIN/UserID
        if "," in line:
            parts = [p.strip() for p in line.split(",")]
            if parts and parts[0]:
                events.append({"PIN": parts[0], "_raw_csv": parts})
                continue

        events.append({"_raw": line})

    return events

