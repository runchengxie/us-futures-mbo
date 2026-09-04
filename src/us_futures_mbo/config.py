from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DEFAULTS = {
    "dataset": "GLBX.MDP3",
    "schema": "mbo",
    "symbols": ["NQ.c.0", "MNQ.c.0"],
    "stype_in": "continuous",
    "start": "2021-09-04T00:00:00Z",
    "end": "2026-09-04T00:00:00Z",
}


def _as_utc(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class QuoteConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    dataset: str = DEFAULTS["dataset"]
    schema_: str = Field(default=DEFAULTS["schema"], alias="schema")
    symbols: list[str] = Field(default_factory=lambda: list(DEFAULTS["symbols"]))
    stype_in: str = DEFAULTS["stype_in"]
    start: datetime = DEFAULTS["start"]
    end: datetime = DEFAULTS["end"]

    @field_validator("start", "end", mode="before")
    @classmethod
    def normalize_datetime(cls, value: datetime | str) -> datetime:
        return _as_utc(value)

    @field_validator("schema_")
    @classmethod
    def validate_schema(cls, value: str) -> str:
        if value != "mbo":
            raise ValueError("schema must be mbo")
        return value

    @property
    def schema(self) -> str:
        return self.schema_

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, value: list[str]) -> list[str]:
        if not value or any(not symbol.strip() for symbol in value):
            raise ValueError("symbols must contain at least one non-empty symbol")
        return value

    @model_validator(mode="after")
    def validate_range(self) -> "QuoteConfig":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "QuoteConfig":
        values = {**DEFAULTS, **mapping}
        return cls.model_validate(values)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "QuoteConfig":
        content = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if not isinstance(content, dict):
            raise ValueError("configuration YAML must contain a mapping")
        return cls.from_mapping(content)

    def to_request_kwargs(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "schema": self.schema,
            "symbols": self.symbols,
            "stype_in": self.stype_in,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }
