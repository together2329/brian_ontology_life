#!/usr/bin/env python3
"""Build position-cap and destination-allocation comparisons for Brian's policy Goal."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import OrderedDict
from pathlib import Path
from typing import Any

import yaml

import build_brian_equity_backtest as core


DEFAULT_SPEC = Path("life/finance/brian_equity_policy_comparison_spec_202607.yaml")
DEFAULT_FIRST_SPEC = Path("life/finance/brian_equity_backtest_spec_202607.yaml")
DEFAULT_PORTFOLIO = Path("life/finance/ai_data_center_investment_comparison_202607.yaml")
DEFAULT_FIRST_RESULTS = Path("life/imports/investment_backtest_202607/results.json")
DEFAULT_FIRST_MANIFEST = Path("life/imports/investment_backtest_202607/source_manifest.yaml")
DEFAULT_RAW_DIR = Path("life/imports/investment_backtest_202607/raw")
DEFAULT_OUTPUT_DIR = Path("life/imports/investment_policy_comparison_202607")
DEFAULT_REPORT = Path("life/finance/brian_equity_policy_comparison_report_ko_202607.md")


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_first_milestone_manifest(path: Path) -> dict[str, Any]:
    manifest = read_yaml(path)
    if manifest["quality_gate_status"] != "pass":
        raise ValueError("First-milestone manifest is not in pass state")
    records = [
        {"file": manifest["spec_file"], "sha256": manifest["spec_sha256"]},
        {"file": manifest["portfolio_file"], "sha256": manifest["portfolio_sha256"]},
        *manifest["raw_sources"],
        *manifest["generated_outputs"].values(),
    ]
    for record in records:
        source = Path(record["file"])
        if not source.is_file() or sha256_file(source) != record["sha256"]:
            raise ValueError(f"First-milestone source hash mismatch: {source}")
    return manifest


def load_market_returns(
    first_spec: dict[str, Any],
    portfolio: dict[str, Any],
    raw_dir: Path,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]], list[dict[str, Any]]]:
    levels: dict[str, dict[str, float]] = {}
    for record in first_spec["market_series"]["symbols"]:
        symbol = record["symbol"]
        path = raw_dir / f"yahoo_{core.safe_symbol(symbol)}.json"
        levels[symbol], _ = core.parse_yahoo(path)
    fx_id = first_spec["market_series"]["usdkrw_primary"]["series_id"]
    fx_path = raw_dir / f"fred_{core.safe_symbol(fx_id)}.csv"
    fx_levels = core.parse_fred(fx_path, fx_id)
    cash_id = first_spec["market_series"]["krw_cash_rate"]["series_id"]
    cash_path = raw_dir / f"fred_{core.safe_symbol(cash_id)}.csv"
    cash_rates = core.parse_fred(cash_path, cash_id)
    quality_checks, _ = core.validate_inputs(first_spec, portfolio, levels, fx_levels, cash_rates)
    native, krw = core.build_returns(first_spec, levels, fx_levels, cash_rates)
    return core.proxy_returns(first_spec, native, krw), native["KRW_CASH"], quality_checks


def strategy_definitions(spec: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for cap in spec["cap_strategy_design"]["caps_percent"]:
        for mode in spec["cap_strategy_design"]["enforcement_modes"]:
            annual = mode == "initial_and_each_december"
            month_end_trigger = mode == "initial_and_month_end_trigger"
            output.append(
                {
                    "strategy_id": f"direct_cap_{cap}_{'annual' if annual else 'month_end_trigger' if month_end_trigger else 'initial_once'}",
                    "label_ko": f"SK {cap}% 상한 {'월말 초과시' if month_end_trigger else '초기+연말' if annual else '초기 1회'}",
                    "kind": "cap",
                    "cap_percent": float(cap),
                    "annual": annual,
                    "month_end_trigger": month_end_trigger,
                    "band_trigger": False,
                }
            )
    output.extend(
        [
            {
                "strategy_id": "destination_initial_buy_and_hold",
                "label_ko": "정책 목적지 초기배분",
                "kind": "destination",
                "annual": False,
                "month_end_trigger": False,
                "band_trigger": False,
            },
            {
                "strategy_id": "destination_initial_and_annual_rebalance",
                "label_ko": "정책 목적지 연 1회",
                "kind": "destination",
                "annual": True,
                "month_end_trigger": False,
                "band_trigger": False,
            },
            {
                "strategy_id": "destination_policy_band_triggered_rebalance",
                "label_ko": "정책 목적지 밴드 이탈시",
                "kind": "destination",
                "annual": False,
                "month_end_trigger": False,
                "band_trigger": True,
            },
        ]
    )
    return output


def asset_proxy(asset_id: str, first_spec: dict[str, Any]) -> str:
    if asset_id.startswith("legacy_"):
        return first_spec["product_proxy_map"][asset_id.removeprefix("legacy_")]
    if asset_id.startswith("dest_"):
        return asset_id.removeprefix("dest_")
    cap_proxy = {
        "cap_global_core": "global_core_unhedged",
        "cap_safe": "krw_safe_short_duration",
        "cap_gold": "gold_unhedged",
    }
    return cap_proxy.get(asset_id, first_spec["product_proxy_map"].get(asset_id, asset_id))


def concentration(
    balances: dict[str, float],
    first_spec: dict[str, Any],
) -> tuple[float, float]:
    direct_products = set(first_spec["exposure_classification"]["direct_employer_product_ids"])
    ai_products = set(first_spec["exposure_classification"]["explicit_ai_product_ids"])
    destination_ai = {
        "dest_direct_sk_hynix",
        "dest_semiconductor_unhedged",
        "dest_power_grid_unhedged",
        "dest_ai_value_chain_unhedged",
        "dest_optical_current_top_three_backcast",
        "dest_nuclear_unhedged",
    }
    total = sum(balances.values())
    direct = sum(
        value
        for asset_id, value in balances.items()
        if asset_id in direct_products or asset_id == "legacy_direct_sk_hynix" or asset_id == "dest_direct_sk_hynix"
    )
    explicit_ai = sum(
        value
        for asset_id, value in balances.items()
        if asset_id in ai_products
        or (asset_id.startswith("legacy_") and asset_id.removeprefix("legacy_") in ai_products)
        or asset_id in destination_ai
    )
    return direct / total, explicit_ai / total


def transaction_haircut(sale_friction: float, purchase_cost: float) -> float:
    return sale_friction + (1.0 - sale_friction) * purchase_cost


def enforce_direct_cap(
    balances: dict[str, float],
    cap: float,
    sale_friction: float,
    purchase_cost: float,
) -> dict[str, float]:
    direct_key = "direct_sk_hynix"
    direct = balances.get(direct_key, 0.0)
    total = sum(balances.values())
    if total == 0.0 or direct / total <= cap + 1e-12:
        return {"gross_sales_krw": 0.0, "cost_krw": 0.0, "post_direct_percent": direct / total * 100.0}
    haircut = transaction_haircut(sale_friction, purchase_cost)
    gross_sale = (direct - cap * total) / (1.0 - cap * haircut)
    net_reinvested = gross_sale * (1.0 - sale_friction) * (1.0 - purchase_cost)
    balances[direct_key] -= gross_sale
    balances["cap_global_core"] = balances.get("cap_global_core", 0.0) + net_reinvested * 0.80
    balances["cap_safe"] = balances.get("cap_safe", 0.0) + net_reinvested * 0.15
    balances["cap_gold"] = balances.get("cap_gold", 0.0) + net_reinvested * 0.05
    post_total = sum(balances.values())
    post_percent = balances[direct_key] / post_total * 100.0
    modeled_cost = gross_sale * haircut
    if not math.isclose(total - post_total, modeled_cost, abs_tol=1e-5):
        raise ValueError("Cap transaction cash conservation failed")
    if not math.isclose(post_percent, cap * 100.0, abs_tol=1e-8):
        raise ValueError(f"Cap transaction failed: expected {cap * 100}, got {post_percent}")
    return {
        "gross_sales_krw": gross_sale,
        "cost_krw": modeled_cost,
        "post_direct_percent": post_percent,
    }


def destination_weights(spec: dict[str, Any]) -> dict[str, float]:
    output = {f"dest_{proxy}": float(weight) for proxy, weight in spec["destination_strategy_design"]["target_weights"].items()}
    if not math.isclose(sum(output.values()), 1.0, abs_tol=1e-12):
        raise ValueError("Destination weights do not sum to one")
    return output


def consolidate_for_destination(
    products: list[dict[str, Any]],
    first_spec: dict[str, Any],
    spec: dict[str, Any],
) -> dict[str, float]:
    matching = spec["destination_strategy_design"]["initial_matching_rule"]
    balances: dict[str, float] = {}
    for product in products:
        product_id = product["product_id"]
        proxy = first_spec["product_proxy_map"][product_id]
        asset_id = f"dest_{matching[proxy]}" if proxy in matching else f"legacy_{product_id}"
        balances[asset_id] = balances.get(asset_id, 0.0) + float(product["evaluation_amount_krw"])
    return balances


def rebalance_to_target(
    balances: dict[str, float],
    weights: dict[str, float],
    sale_friction: float,
    purchase_cost: float,
) -> dict[str, float]:
    total = sum(balances.values())
    haircut = transaction_haircut(sale_friction, purchase_cost)

    def gross_sales(final_total: float) -> float:
        keys = set(balances) | set(weights)
        return sum(max(balances.get(key, 0.0) - weights.get(key, 0.0) * final_total, 0.0) for key in keys)

    low, high = 0.0, total
    for _ in range(200):
        middle = (low + high) / 2.0
        residual = middle - (total - haircut * gross_sales(middle))
        if residual > 0:
            high = middle
        else:
            low = middle
    final_total = (low + high) / 2.0
    sales = gross_sales(final_total)
    modeled_cost = sales * haircut
    if not math.isclose(total - final_total, modeled_cost, abs_tol=1e-5):
        raise ValueError("Destination rebalance cash conservation failed")
    balances.clear()
    balances.update({key: weight * final_total for key, weight in weights.items()})
    tracking_error = 0.5 * sum(abs(value / final_total - weights[key]) for key, value in balances.items())
    if tracking_error > 1e-10:
        raise ValueError(f"Destination tracking error after rebalance: {tracking_error}")
    return {"gross_sales_krw": sales, "cost_krw": modeled_cost, "tracking_error_percent": tracking_error * 100.0}


def contribution_allocation(strategy: dict[str, Any], spec: dict[str, Any]) -> dict[str, float]:
    if strategy["kind"] == "cap":
        return {"cap_global_core": 0.80, "cap_safe": 0.15, "cap_gold": 0.05}
    return destination_weights(spec)


def target_tracking_error(balances: dict[str, float], weights: dict[str, float]) -> float:
    total = sum(balances.values())
    keys = set(balances) | set(weights)
    return 0.5 * sum(abs(balances.get(key, 0.0) / total - weights.get(key, 0.0)) for key in keys)


def destination_band_breached(
    balances: dict[str, float],
    first_spec: dict[str, Any],
    spec: dict[str, Any],
) -> bool:
    total = sum(balances.values())
    direct, explicit_ai = concentration(balances, first_spec)
    global_core = balances.get("dest_global_core_unhedged", 0.0) / total
    safe = balances.get("dest_krw_safe_short_duration", 0.0) / total
    gold = balances.get("dest_gold_unhedged", 0.0) / total
    trigger = spec["destination_strategy_design"]["band_trigger"]
    tolerance = float(trigger["tolerance_percent_points"]) / 100.0
    rules = trigger["rebalance_to_target_if_any"]

    def outside(value: float, band: list[float]) -> bool:
        return value < band[0] / 100.0 - tolerance or value > band[1] / 100.0 + tolerance

    return any(
        [
            outside(global_core, rules["broad_global_core_outside_percent"]),
            outside(safe, rules["safe_short_duration_outside_percent"]),
            outside(gold, rules["gold_outside_percent"]),
            explicit_ai > rules["explicit_ai_above_percent"] / 100.0 + tolerance,
            direct > rules["direct_employer_above_percent"] / 100.0 + tolerance,
        ]
    )


def simulate(
    spec: dict[str, Any],
    first_spec: dict[str, Any],
    products: list[dict[str, Any]],
    proxies: dict[str, dict[str, float]],
    cash_returns: dict[str, float],
    start_month: str,
    strategy: dict[str, Any],
    sale_friction_bps: int,
) -> dict[str, Any]:
    sale_friction = sale_friction_bps / 10000.0
    purchase_cost = spec["test_design"]["contribution_purchase_cost_bps"] / 10000.0
    initial_total = float(spec["test_design"]["source_portfolio_initial_value_krw"])
    target = destination_weights(spec) if strategy["kind"] == "destination" else None
    if strategy["kind"] == "destination":
        balances = consolidate_for_destination(products, first_spec, spec)
        initial_event = rebalance_to_target(balances, target or {}, sale_friction, purchase_cost)
    else:
        balances = {item["product_id"]: float(item["evaluation_amount_krw"]) for item in products}
        initial_event = enforce_direct_cap(
            balances,
            strategy["cap_percent"] / 100.0,
            sale_friction,
            purchase_cost,
        )
    allocation = contribution_allocation(strategy, spec)
    months = core.month_range(start_month, spec["test_design"]["end_month"])
    monthly_contribution = int(spec["test_design"]["monthly_contribution_krw"])
    bonus = int(spec["test_design"]["one_time_bonus_krw"])

    twr_returns: list[float] = []
    excess_returns: list[float] = []
    cashflows = [-initial_total]
    initial_policy_cost = initial_event["cost_krw"]
    annual_policy_cost = 0.0
    contribution_cost = 0.0
    gross_sales = initial_event["gross_sales_krw"]
    transaction_events = [
        {
            "month": "initial",
            "gross_sales_krw": round(initial_event["gross_sales_krw"]),
            "cost_krw": round(initial_event["cost_krw"]),
            "post_direct_percent": round(concentration(balances, first_spec)[0] * 100.0, 6),
        }
    ]
    direct_start, ai_start = concentration(balances, first_spec)
    direct_path = [direct_start]
    ai_path = [ai_start]
    tracking_path = [target_tracking_error(balances, target)] if target else []

    for index, month in enumerate(months):
        previous_value = initial_total if index == 0 else sum(balances.values())
        for asset_id in list(balances):
            proxy_id = asset_proxy(asset_id, first_spec)
            balances[asset_id] *= 1.0 + proxies[proxy_id][month]
        pre_event_direct, pre_event_ai = concentration(balances, first_spec)
        direct_path.append(pre_event_direct)
        ai_path.append(pre_event_ai)
        if target:
            tracking_path.append(target_tracking_error(balances, target))

        scheduled_annual = strategy["annual"] and month.endswith("-12")
        cap_triggered = (
            strategy["kind"] == "cap"
            and strategy["month_end_trigger"]
            and pre_event_direct > strategy["cap_percent"] / 100.0 + 1e-12
        )
        destination_triggered = (
            strategy["kind"] == "destination"
            and strategy["band_trigger"]
            and destination_band_breached(balances, first_spec, spec)
        )
        if scheduled_annual or cap_triggered or destination_triggered:
            if strategy["kind"] == "cap":
                event = enforce_direct_cap(
                    balances,
                    strategy["cap_percent"] / 100.0,
                    sale_friction,
                    purchase_cost,
                )
            else:
                event = rebalance_to_target(balances, target or {}, sale_friction, purchase_cost)
            annual_policy_cost += event["cost_krw"]
            gross_sales += event["gross_sales_krw"]
            transaction_events.append(
                {
                    "month": month,
                    "gross_sales_krw": round(event["gross_sales_krw"]),
                    "cost_krw": round(event["cost_krw"]),
                    "post_direct_percent": round(concentration(balances, first_spec)[0] * 100.0, 6),
                }
            )

        post_event_value = sum(balances.values())
        portfolio_return = post_event_value / previous_value - 1.0
        twr_returns.append(portfolio_return)
        excess_returns.append(portfolio_return - cash_returns[month])

        contribution = float(monthly_contribution + (bonus if index == 11 else 0))
        net_contribution = contribution * (1.0 - purchase_cost)
        contribution_cost += contribution - net_contribution
        for asset_id, weight in allocation.items():
            balances[asset_id] = balances.get(asset_id, 0.0) + net_contribution * weight
        cashflows.append(-contribution)
        direct, ai = concentration(balances, first_spec)
        direct_path.append(direct)
        ai_path.append(ai)
        if target:
            tracking_path.append(target_tracking_error(balances, target))

    terminal_value = sum(balances.values())
    cashflows[-1] += terminal_value
    irr_monthly = core.monthly_irr(cashflows)
    twr_annual = core.annualized_return(twr_returns)
    maximum_drawdown, maximum_underwater = core.drawdown_metrics(twr_returns)
    volatility = statistics.stdev(twr_returns) * math.sqrt(12.0)
    excess_volatility = statistics.stdev(excess_returns)
    sharpe = statistics.mean(excess_returns) / excess_volatility * math.sqrt(12.0) if excess_volatility else float("nan")
    downside = math.sqrt(statistics.mean(min(value, 0.0) ** 2 for value in excess_returns))
    sortino = statistics.mean(excess_returns) / downside * math.sqrt(12.0) if downside else float("nan")
    rolling_twelve = [
        math.prod(1.0 + value for value in twr_returns[offset - 11 : offset + 1]) - 1.0
        for offset in range(11, len(twr_returns))
    ]
    calmar = twr_annual / abs(maximum_drawdown) if maximum_drawdown else float("nan")
    external = len(months) * monthly_contribution + bonus
    ending_direct, ending_ai = concentration(balances, first_spec)
    total_cost = initial_policy_cost + annual_policy_cost + contribution_cost
    metrics = OrderedDict(
        terminal_value_krw=round(terminal_value),
        net_gain_after_contributions_krw=round(terminal_value - initial_total - external),
        total_external_contributions_krw=external,
        money_weighted_return_annualized_percent=core.round_or_none(((1.0 + irr_monthly) ** 12.0 - 1.0) * 100.0),
        time_weighted_return_annualized_percent=core.round_or_none(twr_annual * 100.0),
        annualized_volatility_percent=core.round_or_none(volatility * 100.0),
        maximum_drawdown_percent=core.round_or_none(maximum_drawdown * 100.0),
        maximum_underwater_months=maximum_underwater,
        worst_month_percent=core.round_or_none(min(twr_returns) * 100.0),
        worst_rolling_twelve_month_percent=core.round_or_none(min(rolling_twelve) * 100.0),
        sharpe_over_krw_cash=core.round_or_none(sharpe),
        sortino_over_krw_cash=core.round_or_none(sortino),
        calmar_ratio=core.round_or_none(calmar),
        ending_direct_employer_percent=core.round_or_none(ending_direct * 100.0),
        maximum_direct_employer_after_initial_policy_percent=core.round_or_none(max(direct_path) * 100.0),
        ending_explicit_ai_percent=core.round_or_none(ending_ai * 100.0),
        maximum_explicit_ai_after_initial_policy_percent=core.round_or_none(max(ai_path) * 100.0),
        gross_sales_krw=round(gross_sales),
        initial_policy_cost_krw=round(initial_policy_cost),
        annual_policy_cost_krw=round(annual_policy_cost),
        contribution_purchase_cost_krw=round(contribution_cost),
        total_modeled_cost_krw=round(total_cost),
        ending_target_tracking_error_percent=core.round_or_none(target_tracking_error(balances, target) * 100.0) if target else None,
        maximum_target_tracking_error_percent=core.round_or_none(max(tracking_path) * 100.0) if target else None,
        maximum_direct_cap_breach_percent_points=(
            core.round_or_none(max(direct_path) * 100.0 - strategy["cap_percent"])
            if strategy["kind"] == "cap"
            else None
        ),
    )
    return {
        "start_month": start_month,
        "end_month": spec["test_design"]["end_month"],
        "months": len(months),
        "strategy_id": strategy["strategy_id"],
        "strategy_label_ko": strategy["label_ko"],
        "strategy_kind": strategy["kind"],
        "annual_policy_event": strategy["annual"],
        "month_end_cap_trigger": strategy["month_end_trigger"],
        "destination_band_trigger": strategy["band_trigger"],
        "cap_percent": strategy.get("cap_percent"),
        "sale_friction_bps": sale_friction_bps,
        "metrics": metrics,
        "transaction_events": transaction_events,
    }


def baseline_lookup(first_results: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (item["start_month"], item["strategy_id"]): item
        for item in first_results["scenarios"]
        if item["is_default_cashflow_case"]
        and item["strategy_id"] in {"current_style_continue", "no_sale_dilution_80_15_5"}
    }


def summarize_strategy(
    strategy: dict[str, Any],
    scenarios: list[dict[str, Any]],
    baselines: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    rows = [item for item in scenarios if item["strategy_id"] == strategy["strategy_id"]]
    terminal_vs_dilution = []
    mdd_vs_dilution = []
    mdd_vs_current = []
    for item in rows:
        start = item["start_month"]
        metrics = item["metrics"]
        dilution = baselines[(start, "no_sale_dilution_80_15_5")]["metrics"]
        current = baselines[(start, "current_style_continue")]["metrics"]
        terminal_vs_dilution.append(metrics["terminal_value_krw"] - dilution["terminal_value_krw"])
        mdd_vs_dilution.append(metrics["maximum_drawdown_percent"] - dilution["maximum_drawdown_percent"])
        mdd_vs_current.append(metrics["maximum_drawdown_percent"] - current["maximum_drawdown_percent"])
    return {
        "strategy_id": strategy["strategy_id"],
        "strategy_label_ko": strategy["label_ko"],
        "cases": len(rows),
        "maximum_drawdown_improved_vs_current_style_cases": sum(value > 0 for value in mdd_vs_current),
        "maximum_drawdown_improved_vs_no_sale_dilution_cases": sum(value > 0 for value in mdd_vs_dilution),
        "terminal_value_higher_vs_no_sale_dilution_cases": sum(value > 0 for value in terminal_vs_dilution),
        "terminal_difference_vs_no_sale_dilution_krw_range": [min(terminal_vs_dilution), max(terminal_vs_dilution)],
        "ending_direct_percent_range": [
            min(item["metrics"]["ending_direct_employer_percent"] for item in rows),
            max(item["metrics"]["ending_direct_employer_percent"] for item in rows),
        ],
        "maximum_direct_after_policy_percent_range": [
            min(item["metrics"]["maximum_direct_employer_after_initial_policy_percent"] for item in rows),
            max(item["metrics"]["maximum_direct_employer_after_initial_policy_percent"] for item in rows),
        ],
        "ending_explicit_ai_percent_range": [
            min(item["metrics"]["ending_explicit_ai_percent"] for item in rows),
            max(item["metrics"]["ending_explicit_ai_percent"] for item in rows),
        ],
        "maximum_explicit_ai_after_policy_percent_range": [
            min(item["metrics"]["maximum_explicit_ai_after_initial_policy_percent"] for item in rows),
            max(item["metrics"]["maximum_explicit_ai_after_initial_policy_percent"] for item in rows),
        ],
        "maximum_drawdown_percent_range": [
            min(item["metrics"]["maximum_drawdown_percent"] for item in rows),
            max(item["metrics"]["maximum_drawdown_percent"] for item in rows),
        ],
        "maximum_underwater_months_range": [
            min(item["metrics"]["maximum_underwater_months"] for item in rows),
            max(item["metrics"]["maximum_underwater_months"] for item in rows),
        ],
        "total_modeled_cost_krw_range": [
            min(item["metrics"]["total_modeled_cost_krw"] for item in rows),
            max(item["metrics"]["total_modeled_cost_krw"] for item in rows),
        ],
        "gross_sales_krw_range": [
            min(item["metrics"]["gross_sales_krw"] for item in rows),
            max(item["metrics"]["gross_sales_krw"] for item in rows),
        ],
        "policy_event_count_range": [
            min(len(item["transaction_events"]) for item in rows),
            max(len(item["transaction_events"]) for item in rows),
        ],
    }


def fmt_krw(value: float) -> str:
    sign = "−" if value < 0 else "+" if value > 0 else ""
    absolute = abs(value)
    if absolute >= 100_000_000:
        return f"{sign}{absolute / 100_000_000:.2f}억"
    return f"{sign}{absolute / 10_000:.0f}만"


def fmt_amount(value: float) -> str:
    absolute = abs(value)
    if absolute >= 100_000_000:
        return f"{absolute / 100_000_000:.2f}억"
    return f"{absolute / 10_000:.0f}만"


def build_report(results: dict[str, Any], spec: dict[str, Any]) -> str:
    summaries = results["strategy_summaries"]
    summary_by_id = {item["strategy_id"]: item for item in summaries}
    annual_40 = summary_by_id["direct_cap_40_annual"]
    triggered_40 = summary_by_id["direct_cap_40_month_end_trigger"]
    annual_destination = summary_by_id["destination_initial_and_annual_rebalance"]
    triggered_destination = summary_by_id["destination_policy_band_triggered_rebalance"]
    total_cases = sum(item["cases"] for item in summaries)
    mdd_improved_vs_dilution = sum(item["maximum_drawdown_improved_vs_no_sale_dilution_cases"] for item in summaries)
    terminal_higher_vs_dilution = sum(item["terminal_value_higher_vs_no_sale_dilution_cases"] for item in summaries)
    medium_cost = [item for item in results["scenarios"] if item["sale_friction_bps"] == 100]
    lines = [
        "# Brian 비중상한·목표배분 백테스트 — 2차 결과",
        "",
        f"- 생성일: {results['generated_on']}",
        "- 공통 현금흐름: 월 100만원, 12개월 차 말 보너스 2,000만원",
        "- 처분 마찰비용 민감도: 0.1%·1%·5% (세금·수수료·스프레드의 추상적 합계; 실제 세율 아님)",
        "- 기간: 2016-01, 2020-01, 2023-01 시작부터 2026-06까지",
        "",
        "## 정책 판정",
        "",
        f"- **위험·수익 교환은 선명했다.** 무매도 80/15/5와 비교해 최대낙폭은 {mdd_improved_vs_dilution}/{total_cases}개 경우에서 개선됐지만 종료자산이 더 큰 경우는 {terminal_higher_vs_dilution}/{total_cases}개였다. 현재 승자를 사후선택한 백캐스트이므로 후자는 미래 열위의 증명이 아니다.",
        "- **당장 실행 기준:** 세금 lot과 계좌유형이 없으므로 어떤 처분도 이 결과만으로 실행하지 않는다. 그 전까지는 1차의 무매도 80/15/5 신규자금 희석이 기본 대기정책이다.",
        f"- **연말 점검은 진짜 상한이 아니었다.** 40%로 시작·연말 조정해도 월말 관측 최대가 {annual_40['maximum_direct_after_policy_percent_range'][1]:.1f}%까지 올라갔다. 월말 초과 트리거는 같은 최대치를 {triggered_40['maximum_direct_after_policy_percent_range'][1]:.1f}%로 줄였으므로 40% 전환 후보는 달력형보다 초과 트리거형이 더 일관적이다.",
        f"- **하지만 40% 트리거를 자동매매 규칙으로 채택할 근거도 없다.** 승자 경로를 계속 잘라낸 결과 총매도는 {fmt_amount(triggered_40['gross_sales_krw_range'][0])}~{fmt_amount(triggered_40['gross_sales_krw_range'][1])}, 이벤트는 {triggered_40['policy_event_count_range'][0]}~{triggered_40['policy_event_count_range'][1]}회, 총 모델비용은 최대 {fmt_amount(triggered_40['total_modeled_cost_krw_range'][1])}원이었다. 따라서 ‘월말 모니터링 후 세금·거래제한을 확인하는 의사결정 트리거’로만 남긴다.",
        "- **장기 목적지 후보:** 60% 글로벌 코어·15% 안전자산·20% 명시적 AI·5% 금(그중 SK하이닉스 5%)은 장기 정책의 기준 포트폴리오다. 이는 한 번에 갈아타라는 뜻이 아니라 도착점 비교선이다.",
        "- **10% 상한은 스트레스 경계:** 장기 ceiling과 맞지만 즉시 적용 시 큰 회전율이 필요하므로, 비용·세금·고용주 거래제한을 확인하지 않은 상태의 실행안으로 보지 않는다.",
        f"- **목적지 밴드도 모니터링이 필요했다.** 연 1회 목적지 전략의 기간중 AI 최대는 {annual_destination['maximum_explicit_ai_after_policy_percent_range'][1]:.1f}%였고, 밴드 이탈 트리거에서는 {triggered_destination['maximum_explicit_ai_after_policy_percent_range'][1]:.1f}%였다. 트리거는 위험을 더 묶지만 회전율과 비용을 함께 비교해야 한다.",
        "",
        "## 전략별 9개 경우 요약",
        "",
        "각 전략은 3개 시작점 × 3개 처분 마찰비용이다. 종료자산 차이는 같은 시작점의 무매도 80/15/5 대비다.",
        "",
        "| 전략 | 집중형 대비 MDD 개선 | 무매도 희석 대비 MDD 개선 | 종료 SK 범위 | 기간중 SK 최대 | 종료/기간중 최대 AI | MDD 범위 | 수중 최장 | 종료자산 차이 | 매도총액 | 이벤트 | 총비용 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        terminal = item["terminal_difference_vs_no_sale_dilution_krw_range"]
        costs = item["total_modeled_cost_krw_range"]
        sales = item["gross_sales_krw_range"]
        lines.append(
            f"| {item['strategy_label_ko']} | {item['maximum_drawdown_improved_vs_current_style_cases']}/{item['cases']} | "
            f"{item['maximum_drawdown_improved_vs_no_sale_dilution_cases']}/{item['cases']} | "
            f"{item['ending_direct_percent_range'][0]:.1f}~{item['ending_direct_percent_range'][1]:.1f}% | "
            f"{item['maximum_direct_after_policy_percent_range'][0]:.1f}~{item['maximum_direct_after_policy_percent_range'][1]:.1f}% | "
            f"{item['ending_explicit_ai_percent_range'][0]:.1f}~{item['ending_explicit_ai_percent_range'][1]:.1f}% / "
            f"{item['maximum_explicit_ai_after_policy_percent_range'][1]:.1f}% | "
            f"{item['maximum_drawdown_percent_range'][0]:.1f}~{item['maximum_drawdown_percent_range'][1]:.1f}% | "
            f"{item['maximum_underwater_months_range'][0]}~{item['maximum_underwater_months_range'][1]}개월 | "
            f"{fmt_krw(terminal[0])}~{fmt_krw(terminal[1])} | {fmt_amount(sales[0])}~{fmt_amount(sales[1])} | "
            f"{item['policy_event_count_range'][0]}~{item['policy_event_count_range'][1]}회 | "
            f"{fmt_amount(costs[0])}~{fmt_amount(costs[1])} |"
        )
    lines.extend(
        [
            "",
            "## 1% 처분 마찰비용의 상세 결과",
            "",
            "| 시작 | 전략 | 종료자산 | MWRR | MDD | 종료 SK | 기간중 SK 최대 | 종료 AI | 총 모델비용 |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in medium_cost:
        metrics = item["metrics"]
        lines.append(
            f"| {item['start_month']} | {item['strategy_label_ko']} | {metrics['terminal_value_krw'] / 100_000_000:.2f}억 | "
            f"{metrics['money_weighted_return_annualized_percent']:.2f}% | {metrics['maximum_drawdown_percent']:.2f}% | "
            f"{metrics['ending_direct_employer_percent']:.2f}% | "
            f"{metrics['maximum_direct_employer_after_initial_policy_percent']:.2f}% | "
            f"{metrics['ending_explicit_ai_percent']:.2f}% | {fmt_amount(metrics['total_modeled_cost_krw'])} |"
        )
    lines.extend(
        [
            "",
            "## 읽는 법과 한계",
            "",
            "- 상한 초기 1회 전략은 이후 가격 상승으로 다시 상한을 넘을 수 있다. 연말 전략도 연중 초과를 허용하므로 ‘항상 지켜지는 ceiling’이 아니다.",
            "- 목표배분은 같은 대용지수인 기존 자산을 매도 없이 버킷으로 통합하고, 나머지 차이만 회전율로 잡았다. 실제 종목·계좌·lot별 거래와 다르다.",
            "- 미국 대용자산은 1차와 동일하게 FRED DEXKOUS 월말 원화환산을 사용했고, 명시적 환헤지 반도체 대용치만 달러 현지수익률을 썼다. 환율 효과는 결과에 포함되지만 미래 환율 전망은 아니다.",
            "- 처분 마찰비용 0.1%·1%·5%는 세법 주장이 아니라 민감도다. 실제 국내주식·국내상장 해외ETF·연금·일반계좌의 세금은 각각 확인해야 한다.",
            "- 현재 승자 종목과 2026 구성종목을 과거에 적용한 사후선택 편향 때문에 집중형의 높은 과거 종료자산을 미래 기대수익으로 해석할 수 없다.",
            "- 2023 시작 구간의 매우 높은 연환산 수익률은 2025~2026년 원자료 급등 경로의 영향이며 전망치가 아니다.",
            "",
            "## 다음 실행 전 게이트",
            "",
            "1. SK하이닉스와 각 ETF의 계좌별 수량·취득가·세금 lot·거래 가능기간을 저장한다.",
            "2. 실제 처분세·거래세·수수료를 계좌별로 계산해 추상적 0.1%·1%·5%를 교체한다.",
            "3. 국내 ETF 실제 NAV·분배금·과거 구성종목으로 대용지수 오차를 줄인다.",
            "4. 세후 성과급과 월 잉여현금 확정값으로 전환기간과 필요한 처분 규모를 다시 계산한다.",
            "5. 고용소득 6개월 중단과 성과급 축소를 증권 경로 밖의 가계 스트레스에 결합한다.",
            "",
            "## 재현 파일",
            "",
            "- 명세: `life/finance/brian_equity_policy_comparison_spec_202607.yaml`",
            "- 전체 결과: `life/imports/investment_policy_comparison_202607/results.json`",
            "- 해시·검증: `life/imports/investment_policy_comparison_202607/source_manifest.yaml`",
            "- 계산기: `scripts/build_brian_equity_policy_comparison.py`",
            "- 검증기: `scripts/validate_brian_equity_policy_comparison.py`",
            "",
            "본 문서는 정책 후보 비교이며 매수·매도 지시가 아니다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--first-spec", type=Path, default=DEFAULT_FIRST_SPEC)
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--first-results", type=Path, default=DEFAULT_FIRST_RESULTS)
    parser.add_argument("--first-manifest", type=Path, default=DEFAULT_FIRST_MANIFEST)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--generated-on", default="2026-07-20")
    args = parser.parse_args()

    first_manifest = verify_first_milestone_manifest(args.first_manifest)
    spec = read_yaml(args.spec)
    first_spec = read_yaml(args.first_spec)
    portfolio = read_yaml(args.portfolio)
    first_results = json.loads(args.first_results.read_text(encoding="utf-8"))
    proxies, cash_returns, inherited_checks = load_market_returns(first_spec, portfolio, args.raw_dir)
    products = portfolio["portfolio_snapshot"]["products"]
    strategies = strategy_definitions(spec)

    scenarios = [
        simulate(spec, first_spec, products, proxies, cash_returns, start, strategy, friction)
        for start in spec["test_design"]["start_months"]
        for strategy in strategies
        for friction in spec["test_design"]["sale_friction_bps_grid"]
    ]
    expected = (
        len(spec["test_design"]["start_months"])
        * len(strategies)
        * len(spec["test_design"]["sale_friction_bps_grid"])
    )
    keys = {(item["start_month"], item["strategy_id"], item["sale_friction_bps"]) for item in scenarios}
    if len(scenarios) != expected or len(keys) != expected:
        raise ValueError("Policy scenario grid is incomplete or duplicated")
    for item in scenarios:
        if item["metrics"]["total_modeled_cost_krw"] < item["metrics"]["contribution_purchase_cost_krw"]:
            raise ValueError(f"Modeled cost invariant failed: {item}")
        if item["strategy_kind"] == "cap":
            initial = item["transaction_events"][0]["post_direct_percent"]
            if not math.isclose(initial, item["cap_percent"], abs_tol=1e-5):
                raise ValueError(f"Initial cap audit failed: {item}")
            if item["annual_policy_event"] or item["month_end_cap_trigger"]:
                for event in item["transaction_events"][1:]:
                    if event["gross_sales_krw"] and not math.isclose(
                        event["post_direct_percent"], item["cap_percent"], abs_tol=1e-5
                    ):
                        raise ValueError(f"Recurring cap audit failed: {item}")
            if item["month_end_cap_trigger"] and item["metrics"]["ending_direct_employer_percent"] > item["cap_percent"] + 1e-4:
                raise ValueError(f"Month-end cap ending audit failed: {item}")
        else:
            for event in item["transaction_events"]:
                if not math.isclose(event["post_direct_percent"], 5.0, abs_tol=1e-5):
                    raise ValueError(f"Destination rebalance direct weight failed: {item}")
            if item["destination_band_trigger"]:
                if item["metrics"]["ending_direct_employer_percent"] > 10.5 + 1e-4:
                    raise ValueError(f"Destination ending direct band failed: {item}")
                if item["metrics"]["ending_explicit_ai_percent"] > 25.5 + 1e-4:
                    raise ValueError(f"Destination ending AI band failed: {item}")

    baselines = baseline_lookup(first_results)
    summaries = [summarize_strategy(strategy, scenarios, baselines) for strategy in strategies]
    for start in spec["test_design"]["start_months"]:
        for strategy in strategies:
            rows = sorted(
                [item for item in scenarios if item["start_month"] == start and item["strategy_id"] == strategy["strategy_id"]],
                key=lambda item: item["sale_friction_bps"],
            )
            terminal_values = [item["metrics"]["terminal_value_krw"] for item in rows]
            modeled_costs = [item["metrics"]["total_modeled_cost_krw"] for item in rows]
            if terminal_values != sorted(terminal_values, reverse=True) or modeled_costs != sorted(modeled_costs):
                raise ValueError(f"Sale-friction monotonicity failed: {start}, {strategy['strategy_id']}")
    quality_checks = [
        {
            "gate": "first_milestone_hash_chain",
            "status": "pass",
            "first_manifest_sha256": sha256_file(args.first_manifest),
            "inherited_raw_sources": len(first_manifest["raw_sources"]),
        },
        *inherited_checks,
        {
            "gate": "complete_unique_policy_grid",
            "status": "pass",
            "strategy_count": len(strategies),
            "scenario_count": len(scenarios),
        },
        {
            "gate": "cap_and_destination_transaction_invariants",
            "status": "pass",
            "cap_scenarios": sum(item["strategy_kind"] == "cap" for item in scenarios),
            "destination_scenarios": sum(item["strategy_kind"] == "destination" for item in scenarios),
        },
        {
            "gate": "sale_friction_monotonicity",
            "status": "pass",
            "rule": "Higher modeled sale friction never increases terminal value and never lowers total modeled cost.",
        },
    ]
    results = {
        "schema_version": 1,
        "generated_on": args.generated_on,
        "decision_boundary": spec["decision_boundary"].strip(),
        "quality_gate_status": "pass",
        "quality_checks": quality_checks,
        "strategy_count": len(strategies),
        "scenario_count": len(scenarios),
        "baseline_default_scenarios": list(baselines.values()),
        "strategy_summaries": summaries,
        "scenarios": scenarios,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "results.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(build_report(results, spec), encoding="utf-8")

    sources = [
        args.spec,
        args.first_spec,
        args.portfolio,
        args.first_results,
        args.first_manifest,
        Path("scripts/build_brian_equity_policy_comparison.py"),
        Path("scripts/validate_brian_equity_policy_comparison.py"),
    ]
    outputs = [results_path, args.report]
    manifest = {
        "schema_version": 1,
        "generated_on": args.generated_on,
        "quality_gate_status": "pass",
        "quality_checks": quality_checks,
        "source_files": [
            {"file": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in sources
        ],
        "generated_outputs": [
            {"file": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in outputs
        ],
    }
    manifest_path = args.output_dir / "source_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Built {len(scenarios)} position-cap and destination scenarios; quality gates pass")
    print(f"Results: {results_path}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
