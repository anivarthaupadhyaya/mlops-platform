from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def snapshot_id(python_version: str, packages: dict[str, str], image_digest: str | None, config: dict[str, Any]) -> str:
    payload = {
        "config": config,
        "image_digest": image_digest,
        "packages": packages,
        "python_version": python_version,
    }
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()
