#!/usr/bin/env python3
"""Verify hashes and policy invariants for Brian's second backtest milestone."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MANIFEST = Path("life/imports/investment_policy_comparison_202607/source_manifest.yaml")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(record: dict[str, Any]) -> Path:
    path = Path(record["file"])
    if not path.is_file():
        raise ValueError(f"Missing comparison artifact: {path}")
    if sha256_file(path) != record["sha256"]:
        raise ValueError(f"Hash mismatch: {path}")
    if path.stat().st_size != int(record["bytes"]):
        raise ValueError(f"Byte-size mismatch: {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    if manifest["quality_gate_status"] != "pass":
        raise ValueError("Comparison manifest is not in pass state")
    for record in manifest["source_files"]:
        verify(record)
    outputs = [verify(record) for record in manifest["generated_outputs"]]
    results_path = next(path for path in outputs if path.name == "results.json")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    if results["quality_gate_status"] != "pass":
        raise ValueError("Comparison result is not in pass state")
    if results["strategy_count"] != 15 or results["scenario_count"] != 135:
        raise ValueError("Unexpected strategy or scenario count")
    if len(results["scenarios"]) != results["scenario_count"]:
        raise ValueError("Serialized scenario count mismatch")
    if any(summary["cases"] != 9 for summary in results["strategy_summaries"]):
        raise ValueError("A strategy summary does not contain all nine cases")

    keys = set()
    friction_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for scenario in results["scenarios"]:
        key = (scenario["start_month"], scenario["strategy_id"], scenario["sale_friction_bps"])
        if key in keys:
            raise ValueError(f"Duplicate scenario: {key}")
        keys.add(key)
        friction_groups[(scenario["start_month"], scenario["strategy_id"])].append(scenario)
        metrics = scenario["metrics"]
        component_cost = (
            metrics["initial_policy_cost_krw"]
            + metrics["annual_policy_cost_krw"]
            + metrics["contribution_purchase_cost_krw"]
        )
        if abs(metrics["total_modeled_cost_krw"] - component_cost) > 1:
            raise ValueError(f"Cost reconciliation failed: {key}")
        initial_event = scenario["transaction_events"][0]
        if scenario["strategy_kind"] == "cap":
            if not math.isclose(initial_event["post_direct_percent"], scenario["cap_percent"], abs_tol=1e-5):
                raise ValueError(f"Initial cap failed: {key}")
            if scenario["month_end_cap_trigger"] and metrics["ending_direct_employer_percent"] > scenario["cap_percent"] + 1e-4:
                raise ValueError(f"Month-end trigger ending cap failed: {key}")
        else:
            if any(not math.isclose(event["post_direct_percent"], 5.0, abs_tol=1e-5) for event in scenario["transaction_events"]):
                raise ValueError(f"Destination rebalance direct weight failed: {key}")
            if scenario["destination_band_trigger"]:
                if metrics["ending_direct_employer_percent"] > 10.5 + 1e-4:
                    raise ValueError(f"Destination direct band failed: {key}")
                if metrics["ending_explicit_ai_percent"] > 25.5 + 1e-4:
                    raise ValueError(f"Destination AI band failed: {key}")

    if len(keys) != results["scenario_count"]:
        raise ValueError("Unique scenario count mismatch")
    for key, scenarios in friction_groups.items():
        ordered = sorted(scenarios, key=lambda item: item["sale_friction_bps"])
        terminal_values = [item["metrics"]["terminal_value_krw"] for item in ordered]
        modeled_costs = [item["metrics"]["total_modeled_cost_krw"] for item in ordered]
        if terminal_values != sorted(terminal_values, reverse=True):
            raise ValueError(f"Terminal value is not monotonic with sale friction: {key}")
        if modeled_costs != sorted(modeled_costs):
            raise ValueError(f"Modeled cost is not monotonic with sale friction: {key}")
    print(
        f"Policy comparison validation passed: {results['strategy_count']} strategies, "
        f"{results['scenario_count']} scenarios, {len(manifest['source_files'])} hashed inputs"
    )


if __name__ == "__main__":
    main()
