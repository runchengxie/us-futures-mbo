from pathlib import Path

from us_futures_mbo import cli


def test_cli_output_root_precedence(monkeypatch, tmp_path, capsys):
    captured = []
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    monkeypatch.setattr(cli.QuoteConfig, "from_yaml", lambda _: None)
    monkeypatch.setattr(cli.QuoteConfig, "from_mapping", lambda _: None)
    class Config:
        def to_request_kwargs(self):
            return {}
    monkeypatch.setattr(cli.QuoteConfig, "from_yaml", lambda _: Config())
    class Gateway:
        download = None
    monkeypatch.setattr(cli, "DatabentoGateway", lambda _: Gateway())
    monkeypatch.setattr(cli, "quote_cost", lambda *_: {"cost_usd": 0})
    monkeypatch.setattr(cli, "download_dbn", lambda *_, root, **kw: captured.append(root) or {})
    args = ["download", "--start", "2026-09-01", "--end", "2026-09-02"]
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    assert cli.main(args) == 0
    assert captured[-1] == tmp_path / "us-futures-mbo"
    explicit = tmp_path / "explicit"
    assert cli.main([*args, "--output-root", str(explicit)]) == 0
    assert captured[-1] == explicit
    assert not capsys.readouterr().err
    monkeypatch.delenv("DATA_ROOT")
    assert cli.main(args) == 0
    assert captured[-1] == Path("data")
    assert "DATA_ROOT" in capsys.readouterr().err
