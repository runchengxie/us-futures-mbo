from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .cache import download_dbn
from .config import QuoteConfig
from .databento_client import DatabentoGateway
from .explore import explore_window
from .quote import quote_cost


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NQ/MNQ Databento MBO research tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    quote = subparsers.add_parser("quote", help="estimate Databento historical data cost")
    quote.add_argument("--config", type=Path, default=Path("config/quote.yaml"))

    explore = subparsers.add_parser("explore", help="inspect a bounded MBO metadata window")
    explore.add_argument("--config", type=Path, default=Path("config/quote.yaml"))
    explore.add_argument("--start")
    explore.add_argument("--end")
    explore.add_argument("--allow-large-window", action="store_true")

    download = subparsers.add_parser("download", help="download one validated DBN cache object")
    download.add_argument("--config", type=Path, default=Path("config/quote.yaml"))
    download.add_argument("--start", required=True)
    download.add_argument("--end", required=True)
    download.add_argument("--output-root", type=Path, default=Path("data"))
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    try:
        config = QuoteConfig.from_yaml(args.config)
        if args.command in ("explore", "download"):
            config = QuoteConfig.from_mapping({**config.to_request_kwargs(), "start": args.start, "end": args.end})
        gateway = DatabentoGateway(os.environ.get("DATABENTO_API_KEY", ""))
        if args.command == "quote":
            result = quote_cost(config, gateway)
        elif args.command == "download":
            quote = quote_cost(config, gateway)
            result = download_dbn(config, gateway.download, root=args.output_root, quote_usd=quote["cost_usd"])
        else:
            result = explore_window(config, gateway, allow_large_window=args.allow_large_window)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
