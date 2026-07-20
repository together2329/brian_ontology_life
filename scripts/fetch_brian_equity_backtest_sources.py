#!/usr/bin/env python3
"""Fetch and cache the public inputs for Brian's equity-policy backtest.

Run this script with the Python interpreter bundled with the installed
``insane-search`` skill.  The skill's adaptive fetch engine is used because
Yahoo's chart endpoint rejects ordinary clients intermittently.  Only public
ticker symbols and the public FRED series are sent over the network; Brian's
portfolio values never leave the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import yaml


DEFAULT_SPEC = Path("life/finance/brian_equity_backtest_spec_202607.yaml")
DEFAULT_RAW_DIR = Path("life/imports/investment_backtest_202607/raw")
DEFAULT_ENGINE_ROOT = Path.home() / ".codex/skills/insane-search"


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def epoch_utc(value: str) -> int:
    parsed = date.fromisoformat(value)
    return int(datetime.combine(parsed, time.min, tzinfo=timezone.utc).timestamp())


def safe_symbol(symbol: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", symbol).strip("_")


def import_fetch(engine_root: Path):
    sys.path.insert(0, str(engine_root.resolve()))
    try:
        from engine import fetch  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local skill runtime
        raise SystemExit(
            "Could not import insane-search's fetch engine. Run with its venv, for example:\n"
            f"  {engine_root}/.venv/bin/python {Path(__file__).name} "
            f"--engine-root {engine_root}\nOriginal error: {exc}"
        ) from exc
    return fetch


def fetch_text(fetch, url: str) -> tuple[str, dict[str, Any]]:
    result = fetch(url)
    if not result.ok:
        raise RuntimeError(f"insane-search could not fetch {url}: {result.summary}")
    content = result.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"Empty response from {url}")
    receipt = {
        "url": url,
        "final_url": result.final_url,
        "verdict": result.verdict,
        "profile_used": result.profile_used,
        "summary": result.summary,
        "executed_attempts": result.executed_attempts,
        "stop_reason": result.stop_reason,
        "content_trust": result.content_trust,
        "prompt_injection_risk": result.prompt_injection_risk,
        "content_sha256": sha256_text(content),
        "content_bytes": len(content.encode("utf-8")),
    }
    return content, receipt


def fetch_or_reuse(fetch, url: str, output: Path, validator, require_fresh: bool) -> tuple[str, dict[str, Any]]:
    try:
        content, receipt = fetch_text(fetch, url)
        validator(content)
        output.write_text(content, encoding="utf-8")
        receipt["cache_reused"] = False
        return content, receipt
    except Exception as exc:
        if require_fresh or not output.exists():
            raise
        content = output.read_text(encoding="utf-8")
        validator(content)
        return content, {
            "url": url,
            "final_url": None,
            "verdict": "validated_cached_reuse_after_fetch_failure",
            "profile_used": None,
            "summary": f"Fresh fetch failed; retained validated local cache ({type(exc).__name__}: {str(exc)[:300]})",
            "executed_attempts": None,
            "stop_reason": "cached_reuse",
            "content_trust": "previously_fetched_public_source",
            "prompt_injection_risk": None,
            "content_sha256": sha256_text(content),
            "content_bytes": len(content.encode("utf-8")),
            "cache_reused": True,
        }


def validate_yahoo_json(text: str, symbol: str) -> None:
    document = json.loads(text)
    chart = document.get("chart", {})
    if chart.get("error") is not None:
        raise RuntimeError(f"Yahoo returned an error for {symbol}: {chart['error']}")
    results = chart.get("result") or []
    if len(results) != 1 or not results[0].get("timestamp"):
        raise RuntimeError(f"Yahoo response for {symbol} has no monthly observations")


def validate_fred_csv(text: str, series_id: str) -> None:
    header = text.splitlines()[0].strip() if text.splitlines() else ""
    if header not in {f"DATE,{series_id}", f"observation_date,{series_id}"}:
        raise RuntimeError(f"Unexpected FRED header: {header!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--engine-root", type=Path, default=DEFAULT_ENGINE_ROOT)
    parser.add_argument("--accessed-on", default=date.today().isoformat())
    parser.add_argument(
        "--require-fresh",
        action="store_true",
        help="Fail instead of retaining a validated existing cache when a public endpoint is temporarily blocked.",
    )
    args = parser.parse_args()

    spec = read_yaml(args.spec)
    query = spec["market_series"]["yahoo_query"]
    endpoint = spec["market_series"]["yahoo_chart_endpoint_template"]
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    fetch = import_fetch(args.engine_root)

    receipts: list[dict[str, Any]] = []
    for series in spec["market_series"]["symbols"]:
        symbol = series["symbol"]
        params = urlencode(
            {
                "period1": epoch_utc(query["price_lookback_start"]),
                "period2": epoch_utc(query["period_end_exclusive"]),
                "interval": query["interval"],
                "events": query["events"],
            }
        )
        url = f"{endpoint.format(symbol=symbol)}?{params}"
        output = args.raw_dir / f"yahoo_{safe_symbol(symbol)}.json"
        content, receipt = fetch_or_reuse(
            fetch,
            url,
            output,
            lambda text, current_symbol=symbol: validate_yahoo_json(text, current_symbol),
            args.require_fresh,
        )
        receipt.update(
            {
                "provider": "Yahoo Finance chart endpoint",
                "series": symbol,
                "file": str(output),
            }
        )
        receipts.append(receipt)

    for fred in (
        spec["market_series"]["usdkrw_primary"],
        spec["market_series"]["krw_cash_rate"],
    ):
        output = args.raw_dir / f"fred_{safe_symbol(fred['series_id'])}.csv"
        content, receipt = fetch_or_reuse(
            fetch,
            fred["url"],
            output,
            lambda text, series_id=fred["series_id"]: validate_fred_csv(text, series_id),
            args.require_fresh,
        )
        receipt.update(
            {
                "provider": fred["provider"],
                "series": fred["series_id"],
                "file": str(output),
            }
        )
        receipts.append(receipt)

    fetch_receipt = {
        "schema_version": 1,
        "accessed_on": args.accessed_on,
        "privacy_boundary": "Only public ticker symbols, date ranges and a public macro series were requested.",
        "fetch_engine": "installed insane-search adaptive fetch engine",
        "records": receipts,
    }
    receipt_path = args.raw_dir / "fetch_receipt.json"
    receipt_path.write_text(
        json.dumps(fetch_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(receipts)} public sources and {receipt_path}")


if __name__ == "__main__":
    main()
