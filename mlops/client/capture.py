from __future__ import annotations

import importlib.metadata
import sys
from typing import Any

import httpx

from mlops.shared.config import settings


def installed_packages() -> dict[str, str]:
    packages: dict[str, str] = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name")
        if name:
            packages[name] = dist.version
    return dict(sorted(packages.items()))


def capture_env(config: dict[str, Any], image_digest: str | None = None) -> str:
    payload = {
        "python_version": sys.version.split()[0],
        "packages": installed_packages(),
        "image_digest": image_digest,
        "config": config,
    }
    response = httpx.post(f"{settings.api_url.rstrip('/')}/snapshots", json=payload, timeout=30.0)
    response.raise_for_status()
    return str(response.json()["id"])
