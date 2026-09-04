from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path
from typing import Any, Callable

import databento as db

from .config import QuoteConfig


def cache_key(config: QuoteConfig) -> str:
    request = config.to_request_kwargs()
    request["symbols"] = sorted(request["symbols"])
    payload = json.dumps(request, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_path(root: Path, key: str) -> Path:
    return root / "manifest" / f"{key}.json"


def raw_path(root: Path, config: QuoteConfig) -> Path:
    return root / "raw" / config.dataset / config.schema / f"{cache_key(config)}.dbn.zst"


def is_valid_dbn(path: Path, config: QuoteConfig) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        with warnings.catch_warnings(record=True) as caught:
            store = db.DBNStore.from_file(path)
        return (
            not caught
            and str(store.schema) == config.schema
            and store.dataset == config.dataset
            and store.symbols == config.symbols
            and store.start == config.start
            and store.end == config.end
            and not store.metadata.partial
            and not store.metadata.not_found
        )
    except Exception:
        return False


def download_dbn(
    config: QuoteConfig,
    downloader: Callable[..., Any],
    *,
    root: Path = Path("data"),
    quote_usd: float | None = None,
) -> dict[str, Any]:
    key = cache_key(config)
    destination = raw_path(root, config)
    if is_valid_dbn(destination, config):
        return {"status": "skipped_existing", "cache_key": key, "path": str(destination)}

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = Path(f"{destination}.part")
    partial.unlink(missing_ok=True)
    downloader(path=partial, **config.to_request_kwargs())
    if not is_valid_dbn(partial, config):
        partial.unlink(missing_ok=True)
        raise ValueError("downloaded DBN failed metadata validation")
    partial.replace(destination)

    digest = _sha256_file(destination)
    record = {
        "cache_key": key,
        "request": config.to_request_kwargs(),
        "path": str(destination),
        "bytes": destination.stat().st_size,
        "sha256": digest,
        "quote_usd": quote_usd,
        "schema": config.schema,
        "start": config.start.isoformat(),
        "end": config.end.isoformat(),
    }
    target = manifest_path(root, key)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "downloaded", **record}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
