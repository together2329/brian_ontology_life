#!/usr/bin/env python3
"""Verify hashes, schemas and core invariants for Brian's equity backtest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MANIFEST = Path("life/imports/investment_backtest_202607/source_manifest.yaml")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_record(record: dict[str, Any], label: str) -> Path:
    path = Path(record["file"])
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    actual = sha256_file(path)
    if actual != record["sha256"]:
        raise ValueError(f"{label} hash mismatch: {path}; expected {record['sha256']}, got {actual}")
    if path.stat().st_size != int(record["bytes"]):
        raise ValueError(f"{label} byte-size mismatch: {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    if manifest["quality_gate_status"] != "pass":
        raise ValueError("Manifest quality gate is not pass")
    for key in ("spec", "portfolio"):
        path = Path(manifest[f"{key}_file"])
        if sha256_file(path) != manifest[f"{key}_sha256"]:
            raise ValueError(f"{key} hash mismatch: {path}")
    for index, record in enumerate(manifest["raw_sources"]):
        verify_record(record, f"raw source {index}")
    outputs = {
        key: verify_record(record, f"generated output {key}")
        for key, record in manifest["generated_outputs"].items()
    }

    results = json.loads(outputs["results_json"].read_text(encoding="utf-8"))
    if results["quality_gate_status"] != "pass" or results["scenario_count"] != 81:
        raise ValueError("Result quality gate or scenario count failed")
    if len(results["scenarios"]) != results["scenario_count"]:
        raise ValueError("Scenario count does not match serialized scenarios")
    if any(check["status"] not in {"pass", "pass_with_documented_yahoo_anomalies"} for check in results["quality_checks"]):
        raise ValueError("One or more serialized quality checks failed")
    for scenario in results["scenarios"]:
        metrics = scenario["metrics"]
        expected = scenario["months"] * scenario["monthly_contribution_krw"] + scenario["one_time_bonus_krw"]
        if metrics["total_external_contributions_krw"] != expected:
            raise ValueError(f"Contribution invariant failed: {scenario}")
        if metrics["maximum_direct_employer_percent"] < metrics["ending_direct_employer_percent"]:
            raise ValueError(f"Direct-employer maximum invariant failed: {scenario}")
        if metrics["maximum_explicit_ai_percent"] < metrics["ending_explicit_ai_percent"]:
            raise ValueError(f"Explicit-AI maximum invariant failed: {scenario}")

    normalized_records = 0
    with outputs["market_prices_monthly_jsonl"].open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["month"] > "2026-06":
                raise ValueError(f"Partial post-window month leaked into normalized data: {record}")
            normalized_records += 1
    if normalized_records == 0:
        raise ValueError("Normalized market data are empty")

    print(
        f"Backtest validation passed: {results['scenario_count']} scenarios, "
        f"{len(manifest['raw_sources'])} hashed sources, {normalized_records} normalized records"
    )


if __name__ == "__main__":
    main()
