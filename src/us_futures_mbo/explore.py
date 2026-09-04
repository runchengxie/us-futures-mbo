from __future__ import annotations

from datetime import timedelta
from typing import Any

from .config import QuoteConfig


def explore_window(config: QuoteConfig, gateway: Any, *, allow_large_window: bool = False) -> dict[str, Any]:
    duration = config.end - config.start
    if duration > timedelta(hours=24) and not allow_large_window:
        raise ValueError("exploration window must be 24 hours or less")
    summary = gateway.describe(**config.to_request_kwargs())
    raw_fields = summary.get("fields", [])
    fields = [item.get("name", item) if isinstance(item, dict) else item for item in raw_fields]
    return {
        "dataset": config.dataset,
        "schema": config.schema,
        "symbols": config.symbols,
        "start": config.start.isoformat(),
        "end": config.end.isoformat(),
        "fields": fields,
        "record_count": summary.get("record_count"),
        "raw_data_downloaded": False,
    }
