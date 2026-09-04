from datetime import timedelta

import pytest

from us_futures_mbo.config import QuoteConfig
from us_futures_mbo.explore import explore_window


class FakeExploreGateway:
    def describe(self, **kwargs):
        return {"schema": kwargs["schema"], "fields": ["ts_event", "order_id", "action"]}


def test_exploration_rejects_windows_longer_than_one_day():
    config = QuoteConfig.from_mapping({"start": "2026-01-01", "end": "2026-01-03"})
    with pytest.raises(ValueError, match="24 hours"):
        explore_window(config, FakeExploreGateway())


def test_exploration_returns_schema_and_requested_symbols():
    config = QuoteConfig.from_mapping({"start": "2026-01-01", "end": "2026-01-01T12:00:00Z"})
    result = explore_window(config, FakeExploreGateway())
    assert result["schema"] == "mbo"
    assert result["symbols"] == ["NQ.c.0", "MNQ.c.0"]
    assert "order_id" in result["fields"]
