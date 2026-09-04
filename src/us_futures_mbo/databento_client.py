from __future__ import annotations

from typing import Any

import databento as db


class DatabentoConfigurationError(ValueError):
    """Raised when the local Databento configuration is incomplete."""


class DatabentoGateway:
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise DatabentoConfigurationError(
                "DATABENTO_API_KEY is not set; configure it in the environment or .env"
            )
        self._client = db.Historical(api_key.strip())

    def get_cost(self, **request_kwargs: Any) -> Any:
        return self._client.metadata.get_cost(**request_kwargs)
