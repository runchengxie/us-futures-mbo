from pathlib import Path

from us_futures_mbo.cache import cache_key, is_valid_dbn, manifest_path
from us_futures_mbo.config import QuoteConfig


def test_cache_key_is_stable_and_changes_with_request():
    config = QuoteConfig.from_mapping({})
    first = cache_key(config)
    second = cache_key(config)
    changed = cache_key(QuoteConfig.from_mapping({"symbols": ["NQ.c.0"]}))
    assert first == second
    assert first != changed
    assert len(first) == 16
    reordered = cache_key(QuoteConfig.from_mapping({"symbols": ["MNQ.c.0", "NQ.c.0"]}))
    assert first == reordered


def test_manifest_path_is_separate_from_raw_file():
    root = Path("tests/_cache_root")
    assert manifest_path(root, "abc123") == root / "manifest" / "abc123.json"


def test_invalid_or_missing_dbn_is_not_a_cache_hit():
    config = QuoteConfig.from_mapping({})
    root = Path("tests/_cache_root")
    assert not is_valid_dbn(root / "missing.dbn.zst", config)
    bad = root / "bad.dbn.zst"
    root.mkdir(exist_ok=True)
    bad.write_bytes(b"not dbn")
    try:
        assert not is_valid_dbn(bad, config)
    finally:
        bad.unlink(missing_ok=True)
        root.rmdir()
