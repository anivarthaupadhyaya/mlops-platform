from __future__ import annotations

from uuid import UUID

from mlops.shared.models import Metric


def parse_stream_entry(fields: dict[str, str]) -> Metric | None:
    try:
        return Metric(
            run_id=UUID(fields["run_id"]),
            name=fields["name"],
            value=float(fields["value"]),
            step=int(fields["step"]),
        )
    except (KeyError, ValueError, TypeError):
        return None
