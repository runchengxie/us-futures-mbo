from us_futures_mbo.config import QuoteConfig
from us_futures_mbo.quote import quote_cost


class RecordingGateway:
    def __init__(self):
        self.calls = []

    def get_cost(self, **kwargs):
        self.calls.append(kwargs)
        return {"cost": 12.34, "billable_size": 987654}


def test_quote_passes_config_and_normalizes_cost():
    gateway = RecordingGateway()
    result = quote_cost(QuoteConfig.from_mapping({}), gateway)

    assert gateway.calls[0]["dataset"] == "GLBX.MDP3"
    assert gateway.calls[0]["schema"] == "mbo"
    assert result["cost_usd"] == 12.34
    assert result["billable_size_bytes"] == 987654
    assert "api_key" not in result


def test_quote_accepts_databento_value_response():
    class ValueGateway:
        def get_cost(self, **kwargs):
            return {"value": 4783.616625089943}

    result = quote_cost(QuoteConfig.from_mapping({}), ValueGateway())
    assert result["cost_usd"] == 4783.616625089943
