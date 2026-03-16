from __future__ import annotations

import hashlib
import json
from typing import Any


def fingerprint_payload(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode()).hexdigest()


def detect_changed_fields(previous: dict[str, Any], current: dict[str, Any]) -> set[str]:
    changed: set[str] = set()
    for key in sorted(set(previous) | set(current)):
        if previous.get(key) != current.get(key):
            changed.add(key)
    return changed
