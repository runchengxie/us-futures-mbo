from __future__ import annotations

from typing import Any

from .config import QuoteConfig


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "__dict__"):
        return vars(value)
    return {"value": value}


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def quote_cost(config: QuoteConfig, gateway: Any) -> dict[str, Any]:
    request = config.to_request_kwargs()
    raw = _as_mapping(gateway.get_cost(**request))
    return {
        "request": request,
        "cost_usd": _first(raw, "cost", "cost_usd", "price", "value"),
        "billable_size_bytes": _first(raw, "billable_size", "billable_size_bytes", "size"),
        "raw_summary": raw,
    }
