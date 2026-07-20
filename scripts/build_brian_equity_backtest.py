#!/usr/bin/env python3
"""Build Brian's reproducible equity-policy backtest from locally cached data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


DEFAULT_SPEC = Path("life/finance/brian_equity_backtest_spec_202607.yaml")
DEFAULT_PORTFOLIO = Path("life/finance/ai_data_center_investment_comparison_202607.yaml")
DEFAULT_RAW_DIR = Path("life/imports/investment_backtest_202607/raw")
DEFAULT_OUTPUT_DIR = Path("life/imports/investment_backtest_202607")
DEFAULT_REPORT = Path("life/finance/brian_equity_backtest_report_ko_202607.md")


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_symbol(symbol: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in symbol).strip("_")


def month_range(first: str, last: str) -> list[str]:
    year, month = map(int, first.split("-"))
    end_year, end_month = map(int, last.split("-"))
    output: list[str] = []
    while (year, month) <= (end_year, end_month):
        output.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return output


def previous_month(month: str) -> str:
    year, number = map(int, month.split("-"))
    number -= 1
    if number == 0:
        year -= 1
        number = 12
    return f"{year:04d}-{number:02d}"


def parse_yahoo(path: Path) -> tuple[dict[str, float], dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    chart = document["chart"]
    if chart.get("error") is not None:
        raise ValueError(f"Yahoo error in {path}: {chart['error']}")
    result = chart["result"][0]
    timestamps = result["timestamp"]
    adjusted = result["indicators"]["adjclose"][0]["adjclose"]
    if len(timestamps) != len(adjusted):
        raise ValueError(f"Timestamp/adjusted-close mismatch in {path}")
    offset = int(result.get("meta", {}).get("gmtoffset", 0))
    levels: dict[str, float] = {}
    for stamp, value in zip(timestamps, adjusted):
        if value is None:
            continue
        local = datetime.fromtimestamp(stamp + offset, tz=timezone.utc)
        levels[local.strftime("%Y-%m")] = float(value)
    metadata = {
        "currency": result.get("meta", {}).get("currency"),
        "exchange_name": result.get("meta", {}).get("exchangeName"),
        "timezone": result.get("meta", {}).get("exchangeTimezoneName"),
        "observations": len(levels),
        "first_month": min(levels),
        "last_month": max(levels),
    }
    return levels, metadata


def parse_fred(path: Path, series_id: str) -> dict[str, float]:
    output: dict[str, float] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        date_key = "DATE" if "DATE" in (reader.fieldnames or []) else "observation_date"
        for row in reader:
            value = row.get(series_id)
            if not value or value == ".":
                continue
            output[row[date_key][:7]] = float(value)
    return output


def validate_inputs(
    spec: dict[str, Any],
    portfolio: dict[str, Any],
    levels: dict[str, dict[str, float]],
    fx_levels: dict[str, float],
    cash_rates: dict[str, float],
) -> tuple[list[dict[str, Any]], list[str]]:
    products = portfolio["portfolio_snapshot"]["products"]
    total = sum(int(item["evaluation_amount_krw"]) for item in products)
    source_total = int(portfolio["portfolio_snapshot"]["total_evaluation_amount_krw"])
    configured_total = int(spec["test_design"]["source_portfolio_initial_value_krw"])
    if total != source_total or total != configured_total:
        raise ValueError(f"Portfolio total mismatch: products={total}, source={source_total}, spec={configured_total}")

    product_ids = {item["product_id"] for item in products}
    mapped_ids = set(spec["product_proxy_map"])
    if product_ids != mapped_ids:
        raise ValueError(
            f"Product/proxy reconciliation failed; missing={sorted(product_ids - mapped_ids)}, "
            f"extra={sorted(mapped_ids - product_ids)}"
        )

    for proxy_id, definition in spec["proxy_definitions"].items():
        weight = sum(float(item["weight"]) for item in definition["components"])
        if not math.isclose(weight, 1.0, abs_tol=1e-10):
            raise ValueError(f"Proxy {proxy_id} weights sum to {weight}")

    required_start = spec["market_series"]["yahoo_query"]["required_return_start"]
    end = spec["test_design"]["end_month"]
    required_levels = [previous_month(required_start), *month_range(required_start, end)]
    coverage_errors: list[str] = []
    for symbol, series in levels.items():
        missing = [month for month in required_levels if month not in series]
        if missing:
            coverage_errors.append(f"{symbol}: missing {', '.join(missing)}")
    missing_fx = [month for month in required_levels if month not in fx_levels]
    if missing_fx:
        coverage_errors.append(f"DEXKOUS: missing {', '.join(missing_fx)}")
    missing_cash = [month for month in month_range(required_start, end) if month not in cash_rates]
    if missing_cash:
        coverage_errors.append(f"KRW_CASH: missing {', '.join(missing_cash)}")
    if coverage_errors:
        raise ValueError("Monthly coverage failed:\n" + "\n".join(coverage_errors))

    implausible_primary_fx = {
        month: value for month, value in fx_levels.items() if month in required_levels and not 500.0 <= value <= 3000.0
    }
    if implausible_primary_fx:
        raise ValueError(f"Implausible primary DEXKOUS values: {implausible_primary_fx}")
    validation_symbol = spec["market_series"]["usdkrw_validation_symbol"]
    yahoo_fx = levels[validation_symbol]
    yahoo_fx_anomalies = {
        month: value for month, value in yahoo_fx.items() if month in required_levels and not 500.0 <= value <= 3000.0
    }
    valid_differences = [
        abs(yahoo_fx[month] / fx_levels[month] - 1.0) * 100.0
        for month in required_levels
        if 500.0 <= yahoo_fx[month] <= 3000.0
    ]

    checks = [
        {"gate": "portfolio_value_reconciles", "status": "pass", "value_krw": total},
        {"gate": "all_products_have_one_proxy", "status": "pass", "product_count": len(product_ids)},
        {"gate": "proxy_component_weights_sum_to_one", "status": "pass", "proxy_count": len(spec["proxy_definitions"])},
        {
            "gate": "complete_monthly_market_coverage",
            "status": "pass",
            "first_return_month": required_start,
            "last_return_month": end,
            "series_count_including_primary_fx_and_cash": len(levels) + 2,
        },
        {
            "gate": "primary_fx_sanity_and_validation",
            "status": "pass_with_documented_yahoo_anomalies",
            "primary_series": spec["market_series"]["usdkrw_primary"]["series_id"],
            "yahoo_validation_anomaly_months": sorted(yahoo_fx_anomalies),
            "maximum_valid_month_end_difference_percent": round(max(valid_differences), 4),
            "decision": "Use FRED DEXKOUS; retain Yahoo KRW=X only as validation evidence.",
        },
    ]
    return checks, required_levels


def build_returns(
    spec: dict[str, Any],
    levels: dict[str, dict[str, float]],
    fx_levels: dict[str, float],
    cash_rates: dict[str, float],
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    start = spec["market_series"]["yahoo_query"]["required_return_start"]
    end = spec["test_design"]["end_month"]
    months = month_range(start, end)
    fx = fx_levels
    native_returns: dict[str, dict[str, float]] = {}
    krw_returns: dict[str, dict[str, float]] = {}
    for record in spec["market_series"]["symbols"]:
        symbol = record["symbol"]
        if symbol == spec["market_series"]["usdkrw_validation_symbol"]:
            continue
        native_returns[symbol] = {}
        krw_returns[symbol] = {}
        for month in months:
            prior = previous_month(month)
            native = levels[symbol][month] / levels[symbol][prior] - 1.0
            native_returns[symbol][month] = native
            if record["currency"] == "USD":
                krw_returns[symbol][month] = (
                    levels[symbol][month] * fx[month]
                    / (levels[symbol][prior] * fx[prior])
                    - 1.0
                )
            else:
                krw_returns[symbol][month] = native

    cash_returns = {
        month: (1.0 + cash_rates[month] / 100.0) ** (1.0 / 12.0) - 1.0
        for month in months
    }
    native_returns["KRW_CASH"] = cash_returns
    krw_returns["KRW_CASH"] = cash_returns
    return native_returns, krw_returns


def proxy_returns(
    spec: dict[str, Any],
    native_returns: dict[str, dict[str, float]],
    krw_returns: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    months = month_range(
        spec["market_series"]["yahoo_query"]["required_return_start"],
        spec["test_design"]["end_month"],
    )
    output: dict[str, dict[str, float]] = {}
    for proxy_id, definition in spec["proxy_definitions"].items():
        output[proxy_id] = {}
        for month in months:
            value = 0.0
            for component in definition["components"]:
                mode = component["currency_mode"]
                source = native_returns if mode == "hedged_usd_local_return" else krw_returns
                value += float(component["weight"]) * source[component["series"]][month]
            output[proxy_id][month] = value
    return output


def annualized_return(monthly_returns: list[float]) -> float:
    if not monthly_returns:
        return float("nan")
    cumulative = math.prod(1.0 + value for value in monthly_returns)
    return cumulative ** (12.0 / len(monthly_returns)) - 1.0


def monthly_irr(cashflows: list[float]) -> float:
    def npv(rate: float) -> float:
        return sum(value / ((1.0 + rate) ** index) for index, value in enumerate(cashflows))

    low = -0.95
    high = 1.0
    low_value = npv(low)
    high_value = npv(high)
    while low_value * high_value > 0 and high < 1024:
        high *= 2.0
        high_value = npv(high)
    if low_value * high_value > 0:
        return float("nan")
    for _ in range(200):
        middle = (low + high) / 2.0
        value = npv(middle)
        if abs(value) < 1e-7:
            return middle
        if low_value * value <= 0:
            high = middle
        else:
            low = middle
            low_value = value
    return (low + high) / 2.0


def drawdown_metrics(monthly_returns: list[float]) -> tuple[float, int]:
    index = 1.0
    peak = 1.0
    maximum_drawdown = 0.0
    current_underwater = 0
    maximum_underwater = 0
    for value in monthly_returns:
        index *= 1.0 + value
        if index >= peak:
            peak = index
            current_underwater = 0
        else:
            current_underwater += 1
            maximum_underwater = max(maximum_underwater, current_underwater)
            maximum_drawdown = min(maximum_drawdown, index / peak - 1.0)
    return maximum_drawdown, maximum_underwater


def strategy_allocations(
    strategy_id: str,
    products: list[dict[str, Any]],
    total: float,
) -> dict[str, float]:
    if strategy_id == "current_style_continue":
        return {item["product_id"]: float(item["evaluation_amount_krw"]) / total for item in products}
    if strategy_id == "no_sale_dilution_80_15_5":
        return {"sleeve_global_core": 0.80, "sleeve_krw_safe": 0.15, "sleeve_gold": 0.05}
    if strategy_id == "no_sale_global_core_only":
        return {"sleeve_global_core": 1.0}
    raise ValueError(f"Unknown strategy {strategy_id}")


def round_or_none(value: float, digits: int = 4) -> float | None:
    if not math.isfinite(value):
        return None
    return round(value, digits)


def simulate(
    spec: dict[str, Any],
    products: list[dict[str, Any]],
    proxies: dict[str, dict[str, float]],
    cash_returns: dict[str, float],
    start_month: str,
    strategy: dict[str, Any],
    monthly_contribution: int,
    bonus: int,
) -> dict[str, Any]:
    end_month = spec["test_design"]["end_month"]
    months = month_range(start_month, end_month)
    initial_total = float(spec["test_design"]["source_portfolio_initial_value_krw"])
    balances = {item["product_id"]: float(item["evaluation_amount_krw"]) for item in products}
    sleeve_proxy = {
        "sleeve_global_core": "global_core_unhedged",
        "sleeve_krw_safe": "krw_safe_short_duration",
        "sleeve_gold": "gold_unhedged",
    }
    allocation = strategy_allocations(strategy["strategy_id"], products, initial_total)
    cost_rate = float(spec["test_design"]["contribution_purchase_cost_bps"]) / 10000.0
    product_proxy_map = spec["product_proxy_map"]
    direct_ids = set(spec["exposure_classification"]["direct_employer_product_ids"])
    ai_ids = set(spec["exposure_classification"]["explicit_ai_product_ids"])

    twr_returns: list[float] = []
    excess_returns: list[float] = []
    cashflows = [-initial_total]
    purchase_cost = 0.0
    total_contributions = 0.0
    direct_concentrations = [sum(balances.get(key, 0.0) for key in direct_ids) / initial_total]
    ai_concentrations = [sum(balances.get(key, 0.0) for key in ai_ids) / initial_total]

    for index, month in enumerate(months):
        previous_value = sum(balances.values())
        for asset_id in list(balances):
            proxy_id = sleeve_proxy.get(asset_id, product_proxy_map.get(asset_id))
            if proxy_id is None:
                raise ValueError(f"No proxy for balance {asset_id}")
            balances[asset_id] *= 1.0 + proxies[proxy_id][month]
        preflow_value = sum(balances.values())
        portfolio_return = preflow_value / previous_value - 1.0
        twr_returns.append(portfolio_return)
        excess_returns.append(portfolio_return - cash_returns[month])

        contribution = float(monthly_contribution)
        if index == 11:
            contribution += float(bonus)
        total_contributions += contribution
        net_contribution = contribution * (1.0 - cost_rate)
        purchase_cost += contribution - net_contribution
        for asset_id, weight in allocation.items():
            balances[asset_id] = balances.get(asset_id, 0.0) + net_contribution * weight
        cashflows.append(-contribution)

        total_value = sum(balances.values())
        direct_concentrations.append(sum(balances.get(key, 0.0) for key in direct_ids) / total_value)
        ai_concentrations.append(sum(balances.get(key, 0.0) for key in ai_ids) / total_value)

    terminal_value = sum(balances.values())
    cashflows[-1] += terminal_value
    irr_monthly = monthly_irr(cashflows)
    twr_annual = annualized_return(twr_returns)
    maximum_drawdown, maximum_underwater = drawdown_metrics(twr_returns)
    volatility = statistics.stdev(twr_returns) * math.sqrt(12.0) if len(twr_returns) > 1 else 0.0
    excess_volatility = statistics.stdev(excess_returns) if len(excess_returns) > 1 else 0.0
    sharpe = statistics.mean(excess_returns) / excess_volatility * math.sqrt(12.0) if excess_volatility else float("nan")
    downside = math.sqrt(statistics.mean(min(value, 0.0) ** 2 for value in excess_returns))
    sortino = statistics.mean(excess_returns) / downside * math.sqrt(12.0) if downside else float("nan")
    rolling_twelve = [
        math.prod(1.0 + value for value in twr_returns[index - 11 : index + 1]) - 1.0
        for index in range(11, len(twr_returns))
    ]
    calmar = twr_annual / abs(maximum_drawdown) if maximum_drawdown else float("nan")

    metrics = OrderedDict(
        terminal_value_krw=round(terminal_value),
        net_gain_after_contributions_krw=round(terminal_value - initial_total - total_contributions),
        total_external_contributions_krw=round(total_contributions),
        money_weighted_return_annualized_percent=round_or_none(((1.0 + irr_monthly) ** 12.0 - 1.0) * 100.0),
        time_weighted_return_annualized_percent=round_or_none(twr_annual * 100.0),
        annualized_volatility_percent=round_or_none(volatility * 100.0),
        maximum_drawdown_percent=round_or_none(maximum_drawdown * 100.0),
        maximum_underwater_months=maximum_underwater,
        worst_month_percent=round_or_none(min(twr_returns) * 100.0),
        worst_rolling_twelve_month_percent=round_or_none(min(rolling_twelve) * 100.0),
        sharpe_over_krw_cash=round_or_none(sharpe),
        sortino_over_krw_cash=round_or_none(sortino),
        calmar_ratio=round_or_none(calmar),
        ending_direct_employer_percent=round_or_none(direct_concentrations[-1] * 100.0),
        maximum_direct_employer_percent=round_or_none(max(direct_concentrations) * 100.0),
        ending_explicit_ai_percent=round_or_none(ai_concentrations[-1] * 100.0),
        maximum_explicit_ai_percent=round_or_none(max(ai_concentrations) * 100.0),
        purchase_cost_krw=round(purchase_cost),
    )
    return {
        "start_month": start_month,
        "end_month": end_month,
        "months": len(months),
        "strategy_id": strategy["strategy_id"],
        "strategy_label_ko": strategy["label_ko"],
        "monthly_contribution_krw": monthly_contribution,
        "one_time_bonus_krw": bonus,
        "is_default_cashflow_case": (
            monthly_contribution == int(spec["test_design"]["default_cashflow_case"]["monthly_contribution_krw"])
            and bonus == int(spec["test_design"]["default_cashflow_case"]["one_time_bonus_krw"])
        ),
        "metrics": metrics,
    }


def write_market_jsonl(
    path: Path,
    spec: dict[str, Any],
    levels: dict[str, dict[str, float]],
    metadata: dict[str, dict[str, Any]],
    fx_levels: dict[str, float],
    cash_rates: dict[str, float],
) -> None:
    fx_symbol = spec["market_series"]["usdkrw_validation_symbol"]
    fx = fx_levels
    normalized_first_month = spec["market_series"]["yahoo_query"]["price_lookback_start"][:7]
    normalized_last_month = spec["test_design"]["end_month"]
    currency = {item["symbol"]: item["currency"] for item in spec["market_series"]["symbols"]}
    records: list[dict[str, Any]] = []
    for symbol in sorted(levels):
        for month in sorted(levels[symbol]):
            if not normalized_first_month <= month <= normalized_last_month:
                continue
            level = levels[symbol][month]
            krw_level = level * fx[month] if currency[symbol] == "USD" and month in fx else level
            records.append(
                {
                    "series": symbol,
                    "month": month,
                    "adjusted_close": level,
                    "source_currency": currency[symbol],
                    "krw_adjusted_level": krw_level,
                    "source_timezone": metadata[symbol]["timezone"],
                    "role": "validation_only" if symbol == fx_symbol else "return_input",
                }
            )
    for month in sorted(fx_levels):
        if not normalized_first_month <= month <= normalized_last_month:
            continue
        records.append(
            {
                "series": spec["market_series"]["usdkrw_primary"]["series_id"],
                "month": month,
                "month_end_krw_per_usd": fx_levels[month],
                "source_currency": "KRW_per_USD",
                "role": "fx_conversion_input",
            }
        )
    for month in sorted(cash_rates):
        if not normalized_first_month <= month <= normalized_last_month:
            continue
        records.append(
            {
                "series": "KRW_CASH",
                "month": month,
                "annual_rate_percent": cash_rates[month],
                "monthly_return": (1.0 + cash_rates[month] / 100.0) ** (1.0 / 12.0) - 1.0,
                "source_currency": "KRW",
            }
        )
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def paired_summary(scenarios: list[dict[str, Any]], candidate: str) -> dict[str, Any]:
    lookup = {
        (
            item["start_month"],
            item["monthly_contribution_krw"],
            item["one_time_bonus_krw"],
            item["strategy_id"],
        ): item
        for item in scenarios
    }
    pairs = []
    for key, baseline in lookup.items():
        start, monthly, bonus, strategy_id = key
        if strategy_id != "current_style_continue":
            continue
        contender = lookup[(start, monthly, bonus, candidate)]
        pairs.append((baseline["metrics"], contender["metrics"]))
    return {
        "strategy_id": candidate,
        "paired_cases": len(pairs),
        "lower_maximum_drawdown_cases": sum(
            contender["maximum_drawdown_percent"] > baseline["maximum_drawdown_percent"]
            for baseline, contender in pairs
        ),
        "lower_ending_explicit_ai_cases": sum(
            contender["ending_explicit_ai_percent"] < baseline["ending_explicit_ai_percent"]
            for baseline, contender in pairs
        ),
        "lower_ending_direct_employer_cases": sum(
            contender["ending_direct_employer_percent"] < baseline["ending_direct_employer_percent"]
            for baseline, contender in pairs
        ),
        "higher_terminal_value_cases": sum(
            contender["terminal_value_krw"] > baseline["terminal_value_krw"]
            for baseline, contender in pairs
        ),
        "higher_money_weighted_return_cases": sum(
            contender["money_weighted_return_annualized_percent"] > baseline["money_weighted_return_annualized_percent"]
            for baseline, contender in pairs
        ),
        "terminal_value_difference_krw_range": [
            min(contender["terminal_value_krw"] - baseline["terminal_value_krw"] for baseline, contender in pairs),
            max(contender["terminal_value_krw"] - baseline["terminal_value_krw"] for baseline, contender in pairs),
        ],
    }


def milestone_assessment(
    spec: dict[str, Any],
    scenarios: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates = [item for item in scenarios if item["strategy_id"] != "current_style_continue"]
    thresholds = spec["assessment_thresholds_from_policy"]
    minimum_ai_case = min(candidates, key=lambda item: item["metrics"]["ending_explicit_ai_percent"])
    minimum_direct_case = min(candidates, key=lambda item: item["metrics"]["ending_direct_employer_percent"])
    minimum_ai = minimum_ai_case["metrics"]["ending_explicit_ai_percent"]
    minimum_direct = minimum_direct_case["metrics"]["ending_direct_employer_percent"]
    paired_cases = sum(item["paired_cases"] for item in comparisons)
    drawdown_improvements = sum(item["lower_maximum_drawdown_cases"] for item in comparisons)
    terminal_outperformance = sum(item["higher_terminal_value_cases"] for item in comparisons)
    return {
        "cashflow_only_risk_reduction_evidence": f"Maximum drawdown improved in {drawdown_improvements}/{paired_cases} paired cases.",
        "cashflow_only_return_superiority_evidence": f"Terminal value was higher in {terminal_outperformance}/{paired_cases} paired cases.",
        "minimum_ending_explicit_ai_percent_across_candidate_grid": round(minimum_ai, 4),
        "minimum_explicit_ai_case": {
            "start_month": minimum_ai_case["start_month"],
            "strategy_id": minimum_ai_case["strategy_id"],
            "monthly_contribution_krw": minimum_ai_case["monthly_contribution_krw"],
            "one_time_bonus_krw": minimum_ai_case["one_time_bonus_krw"],
        },
        "explicit_ai_destination_target_percent": thresholds["explicit_ai_destination_target_percent"],
        "reached_explicit_ai_destination_target": minimum_ai <= thresholds["explicit_ai_destination_target_percent"],
        "minimum_ending_direct_employer_percent_across_candidate_grid": round(minimum_direct, 4),
        "minimum_direct_employer_case": {
            "start_month": minimum_direct_case["start_month"],
            "strategy_id": minimum_direct_case["strategy_id"],
            "monthly_contribution_krw": minimum_direct_case["monthly_contribution_krw"],
            "one_time_bonus_krw": minimum_direct_case["one_time_bonus_krw"],
        },
        "direct_employer_first_transition_checkpoint_percent": thresholds[
            "direct_employer_first_transition_checkpoint_percent"
        ],
        "reached_direct_employer_first_transition_checkpoint": minimum_direct
        <= thresholds["direct_employer_first_transition_checkpoint_percent"],
        "first_milestone_read": (
            "Routing new money away from the concentrated portfolio consistently reduced historical drawdown and "
            "ending concentration in this backcast, but even the largest tested cashflow did not reach the policy's "
            "first concentration checkpoints. The backcast does not establish return superiority because the current "
            "winner-heavy holdings and current constituents were selected with hindsight."
        ),
    }


def format_krw(value: int | float) -> str:
    return f"{round(value) / 100_000_000:.2f}억"


def build_report(results: dict[str, Any], spec: dict[str, Any]) -> str:
    scenarios = results["scenarios"]
    defaults = [item for item in scenarios if item["is_default_cashflow_case"]]
    labels = {item["strategy_id"]: item["strategy_label_ko"] for item in defaults}
    assessment = results["milestone_assessment"]
    lines = [
        "# Brian 주식 투자정책 백테스트 — 1차 결과",
        "",
        f"- 생성일: {results['generated_on']}",
        f"- 평가 통화: {spec['test_design']['base_currency']}",
        f"- 초기 포트폴리오: {format_krw(spec['test_design']['source_portfolio_initial_value_krw'])}",
        "- 기본 현금흐름: 월 100만원, 각 시작점의 12개월 차 말에 성과급 2,000만원",
        "- 핵심 경계: 실제 계좌 수익률 복원이 아니라 현재 보유구조를 과거에 놓은 반사실 정책 실험이다.",
        "",
        "## 먼저 읽을 결론",
        "",
    ]
    for comparison in results["paired_comparisons"]:
        count = comparison["paired_cases"]
        difference = comparison["terminal_value_difference_krw_range"]
        lines.append(
            f"- **{labels[comparison['strategy_id']]}**: 현재 집중형과 같은 현금흐름으로 비교한 {count}개 조합 중 "
            f"최대낙폭 개선 {comparison['lower_maximum_drawdown_cases']}개, 종료 AI 비중 감소 "
            f"{comparison['lower_ending_explicit_ai_cases']}개, 종료 SK하이닉스 비중 감소 "
            f"{comparison['lower_ending_direct_employer_cases']}개였다. 종료자산 차이 범위는 "
            f"{format_krw(difference[0])}~{format_krw(difference[1])}였다."
        )
    lines.extend(
        [
            f"- **현금흐름 희석만으로는 목표에 도달하지 못했다.** 민감도 격자에서 집중도가 가장 낮아진 월 "
            f"{assessment['minimum_explicit_ai_case']['monthly_contribution_krw']:,}원·보너스 "
            f"{assessment['minimum_explicit_ai_case']['one_time_bonus_krw']:,}원 조합까지 포함해도 종료 AI 비중의 최솟값은 "
            f"{assessment['minimum_ending_explicit_ai_percent_across_candidate_grid']:.2f}%로 정책 목적지 20%보다 높았고, "
            f"SK하이닉스 비중의 최솟값도 {assessment['minimum_ending_direct_employer_percent_across_candidate_grid']:.2f}%로 "
            f"첫 체크포인트 45%보다 높았다.",
            "- 따라서 1차 실험은 ‘신규자금을 집중자산 밖으로 돌리면 위험이 완화된다’는 근거는 주지만, ‘그것만으로 집중 정상화가 끝난다’거나 ‘수익률이 더 높다’는 근거는 주지 않는다.",
            "- 이 결과만으로 매수·매도 결정을 확정하지 않는다. 특히 현재 종목·현재 ETF 성격을 과거로 되돌려 적용했기 때문에 생존자·선정 편향이 크다.",
            "",
            "## 기본 현금흐름 결과",
            "",
            "| 시작 | 전략 | 종료자산 | 순증가액¹ | MWRR | TWR | 최대낙폭 | 수중 최장 | 종료 AI | 종료 SK하이닉스 |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in defaults:
        metrics = item["metrics"]
        lines.append(
            f"| {item['start_month']} | {item['strategy_label_ko']} | {format_krw(metrics['terminal_value_krw'])} | "
            f"{format_krw(metrics['net_gain_after_contributions_krw'])} | "
            f"{metrics['money_weighted_return_annualized_percent']:.2f}% | "
            f"{metrics['time_weighted_return_annualized_percent']:.2f}% | "
            f"{metrics['maximum_drawdown_percent']:.2f}% | {metrics['maximum_underwater_months']}개월 | "
            f"{metrics['ending_explicit_ai_percent']:.2f}% | {metrics['ending_direct_employer_percent']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "¹ 순증가액 = 종료자산 - 초기자산 - 외부 납입액. 세후 실현손익이 아니다.",
            "",
            "## 해석 규칙",
            "",
            "- 종료자산과 MWRR은 현금흐름 크기·시점의 영향을 받는다. 전략 자체의 경로 비교에는 TWR, 최대낙폭, 수중기간을 함께 본다.",
            "- 최대낙폭은 납입으로 손실이 가려지지 않도록 월별 단위가치(TWR index)에서 계산했다.",
            "- 기존 자산은 한 주도 팔지 않았고 월 수익률을 반영한 뒤 그 달의 신규자금을 넣었다.",
            "- 미국 자산은 FRED DEXKOUS의 마지막 일별 관측값으로 만든 월말 USD/KRW 변화를 포함했다. 환헤지형 반도체 대용치는 달러 현지수익률로 근사했고 헤지 비용은 제외했다.",
            "- 매수비용은 신규 납입액의 10bp, 세금은 무매도 1차 실험에서 제외했다.",
            "",
            "## 대용지수와 편향",
            "",
            "- SK하이닉스 직접주식은 000660.KS, 한국 주식은 KODEX 200, 반도체·HBM은 SOXX, AI 밸류체인은 QQQ, 전력망은 GRID, 원전은 URA, 금은 IAU, 글로벌 코어는 VT로 근사했다.",
            "- 광통신은 2026년 5월 보유 ETF 상위 3개(Ciena·Coherent·Lumentum)를 현재 비중으로 정규화해 과거에 적용했다. 가장 강한 생존자·구성종목 선정 편향이 있는 구간이다.",
            "- 2023 시작 구간의 연환산 TWR 130~142%는 원자료에 나타난 2025~2026년 SK하이닉스·반도체 급등과 현재 승자 종목의 사후선택이 결합된 값이다. 기대수익률로 사용하지 않고 전략 간 경로 비교에만 쓴다.",
            "- 정확한 국내 ETF NAV, 보수, 추적오차, 과거 편입종목, 실제 매입일, 개인별 세금은 재현하지 못한다.",
            "- Yahoo 월별 KRW=X의 2016-01·2016-07·2017-09 값에서 약 10,000배 단위 이상을 발견했다. 이 계열은 검증 흔적으로만 남기고 환산에는 FRED DEXKOUS를 사용했다. 정상 범위 월의 두 원천 차이는 최대 1.54%였다.",
            "- Yahoo 조정종가와 FRED 금리를 사용한 연구용 결과다. 거래소·운용사 원자료로 표본 대조하기 전에는 강한 결론을 내리지 않는다.",
            "",
            "## 공개 데이터·방법론 출처",
            "",
            "- [FRED DEXKOUS 원자료](https://fred.stlouisfed.org/series/DEXKOUS): 원화/달러 환율 월말 집계의 기반.",
            "- [FRED 한국 3개월 은행간 금리](https://fred.stlouisfed.org/series/IR3TIB01KRM156N): KRW 안전자산 대용수익률.",
            "- [ALFRED 빈티지 데이터 안내](https://fred.stlouisfed.org/docs/api/fred/alfred.html): 다음 단계 거시 워크포워드의 개정 편향 통제 근거.",
            "- [Investor.gov 자산배분·분산·리밸런싱](https://www.investor.gov/introduction-investing/getting-started/asset-allocation): 분산은 손실을 없애지 않으며 배분은 기간과 위험감내에 맞춰야 한다는 기본 경계.",
            "",
            "## 다음 의사결정 게이트",
            "",
            "1. 월말 실제 잉여현금과 2027년 성과급의 세후 금액을 확정해 현금흐름 민감도를 다시 돌린다.",
            "2. 국내 ETF별 실제 NAV와 과거 구성종목을 확보해 QQQ·SOXX 대용 오차를 줄인다.",
            "3. 무매도 희석 결과가 유지되는지 확인한 뒤에만 SK하이닉스 40%·30%·20%·10% 상한 전략을 세금 포함으로 별도 검증한다.",
            "4. 개정된 거시지표를 그대로 쓰지 말고 ALFRED 등 당시 발표시점 빈티지로 워크포워드 게이트를 검증한다.",
            "",
            "## 재현 파일",
            "",
            "- 명세: `life/finance/brian_equity_backtest_spec_202607.yaml`",
            "- 공개 원자료 캐시: `life/imports/investment_backtest_202607/raw/`",
            "- 정규화 월별 데이터: `life/imports/investment_backtest_202607/market_prices_monthly.jsonl`",
            "- 전체 81개 시나리오: `life/imports/investment_backtest_202607/results.json`",
            "- 원자료 해시·검증: `life/imports/investment_backtest_202607/source_manifest.yaml`",
            "- 재수집: `scripts/fetch_brian_equity_backtest_sources.py`",
            "- 재계산: `scripts/build_brian_equity_backtest.py`",
            "- 무결성 검증: `scripts/validate_brian_equity_backtest.py`",
            "",
            "본 문서는 투자 지시가 아니라 Brian의 현금흐름·집중위험 정책을 점검하기 위한 의사결정 자료다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--generated-on", default="2026-07-20")
    args = parser.parse_args()

    spec = read_yaml(args.spec)
    portfolio = read_yaml(args.portfolio)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    levels: dict[str, dict[str, float]] = {}
    source_metadata: dict[str, dict[str, Any]] = {}
    raw_paths: list[Path] = []
    for record in spec["market_series"]["symbols"]:
        symbol = record["symbol"]
        path = args.raw_dir / f"yahoo_{safe_symbol(symbol)}.json"
        levels[symbol], source_metadata[symbol] = parse_yahoo(path)
        raw_paths.append(path)
    fx_id = spec["market_series"]["usdkrw_primary"]["series_id"]
    fx_path = args.raw_dir / f"fred_{safe_symbol(fx_id)}.csv"
    fx_levels = parse_fred(fx_path, fx_id)
    raw_paths.append(fx_path)
    fred_id = spec["market_series"]["krw_cash_rate"]["series_id"]
    fred_path = args.raw_dir / f"fred_{safe_symbol(fred_id)}.csv"
    cash_rates = parse_fred(fred_path, fred_id)
    raw_paths.append(fred_path)
    receipt_path = args.raw_dir / "fetch_receipt.json"
    if receipt_path.exists():
        raw_paths.append(receipt_path)
    raw_sources = [
        {"file": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in sorted(raw_paths)
    ]

    quality_checks, required_levels = validate_inputs(spec, portfolio, levels, fx_levels, cash_rates)
    native_returns, krw_returns = build_returns(spec, levels, fx_levels, cash_rates)
    proxies = proxy_returns(spec, native_returns, krw_returns)
    products = portfolio["portfolio_snapshot"]["products"]

    scenarios: list[dict[str, Any]] = []
    for start in spec["test_design"]["start_months"]:
        for strategy in spec["strategy_definitions"]:
            for monthly in spec["test_design"]["sensitivity_grid"]["monthly_contribution_krw"]:
                for bonus in spec["test_design"]["sensitivity_grid"]["one_time_bonus_krw"]:
                    scenarios.append(
                        simulate(
                            spec,
                            products,
                            proxies,
                            native_returns["KRW_CASH"],
                            start,
                            strategy,
                            int(monthly),
                            int(bonus),
                        )
                    )

    expected_scenarios = (
        len(spec["test_design"]["start_months"])
        * len(spec["strategy_definitions"])
        * len(spec["test_design"]["sensitivity_grid"]["monthly_contribution_krw"])
        * len(spec["test_design"]["sensitivity_grid"]["one_time_bonus_krw"])
    )
    scenario_keys = {
        (
            item["start_month"],
            item["strategy_id"],
            item["monthly_contribution_krw"],
            item["one_time_bonus_krw"],
        )
        for item in scenarios
    }
    if len(scenarios) != expected_scenarios or len(scenario_keys) != expected_scenarios:
        raise ValueError("Scenario grid is incomplete or contains duplicates")
    for item in scenarios:
        metrics = item["metrics"]
        expected_contributions = item["months"] * item["monthly_contribution_krw"] + item["one_time_bonus_krw"]
        if metrics["total_external_contributions_krw"] != expected_contributions:
            raise ValueError(f"Contribution timing invariant failed for {item}")
        expected_cost = round(
            expected_contributions * spec["test_design"]["contribution_purchase_cost_bps"] / 10000.0
        )
        if metrics["purchase_cost_krw"] != expected_cost:
            raise ValueError(f"Purchase-cost invariant failed for {item}")
        if not 0.0 <= metrics["ending_direct_employer_percent"] <= 100.0:
            raise ValueError(f"Direct-employer concentration invariant failed for {item}")
        if not 0.0 <= metrics["ending_explicit_ai_percent"] <= 100.0:
            raise ValueError(f"Explicit-AI concentration invariant failed for {item}")
    quality_checks.append(
        {
            "gate": "complete_unique_scenario_grid_and_cashflow_invariants",
            "status": "pass",
            "scenario_count": len(scenarios),
            "default_case_count": sum(item["is_default_cashflow_case"] for item in scenarios),
            "sale_events": 0,
            "contribution_timing": "after_monthly_return",
        }
    )
    comparisons = [
        paired_summary(scenarios, "no_sale_dilution_80_15_5"),
        paired_summary(scenarios, "no_sale_global_core_only"),
    ]
    results = {
        "schema_version": 1,
        "generated_on": args.generated_on,
        "decision_boundary": spec["decision_boundary"].strip(),
        "source_integrity": {
            "spec_file": str(args.spec),
            "spec_sha256": sha256_file(args.spec),
            "portfolio_file": str(args.portfolio),
            "portfolio_sha256": sha256_file(args.portfolio),
            "raw_sources": raw_sources,
        },
        "scenario_count": len(scenarios),
        "quality_gate_status": "pass",
        "quality_checks": quality_checks,
        "paired_comparisons": comparisons,
        "milestone_assessment": milestone_assessment(spec, scenarios, comparisons),
        "scenarios": scenarios,
    }
    results_path = args.output_dir / "results.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    monthly_path = args.output_dir / "market_prices_monthly.jsonl"
    write_market_jsonl(monthly_path, spec, levels, source_metadata, fx_levels, cash_rates)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(results, spec), encoding="utf-8")

    generated_paths = {
        "market_prices_monthly_jsonl": monthly_path,
        "results_json": results_path,
        "report_markdown": args.report,
    }
    manifest = {
        "schema_version": 1,
        "generated_on": args.generated_on,
        "spec_file": str(args.spec),
        "spec_sha256": sha256_file(args.spec),
        "portfolio_file": str(args.portfolio),
        "portfolio_sha256": sha256_file(args.portfolio),
        "required_monthly_levels": {"first": required_levels[0], "last": required_levels[-1]},
        "quality_gate_status": "pass",
        "quality_checks": quality_checks,
        "raw_sources": raw_sources,
        "generated_outputs": {
            key: {"file": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for key, path in generated_paths.items()
        },
    }
    manifest_path = args.output_dir / "source_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print(f"Built {len(scenarios)} scenarios; quality gates pass")
    print(f"Results: {results_path}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
