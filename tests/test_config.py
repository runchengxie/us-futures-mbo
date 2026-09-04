import pytest

from us_futures_mbo.config import QuoteConfig


def test_defaults_match_five_year_mbo_quote():
    config = QuoteConfig.from_mapping({})
    assert config.dataset == "GLBX.MDP3"
    assert config.schema == "mbo"
    assert config.symbols == ["NQ.c.0", "MNQ.c.0"]
    assert config.stype_in == "continuous"
    assert config.to_request_kwargs()["start"] == "2021-09-04T00:00:00+00:00"


def test_rejects_invalid_date_order():
    with pytest.raises(ValueError, match="end must be after start"):
        QuoteConfig.from_mapping({"start": "2026-01-01", "end": "2025-01-01"})


def test_rejects_unsupported_schema():
    with pytest.raises(ValueError, match="schema must be mbo"):
        QuoteConfig.from_mapping({"schema": "trades"})
