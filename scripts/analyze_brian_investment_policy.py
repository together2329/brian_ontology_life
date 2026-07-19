#!/usr/bin/env python3
"""Build Brian's investment-policy execution and stress-test ledger.

The calculator uses the saved 2026-07-15 securities snapshot. Stress scenarios
are sensitivities, not forecasts. ETF shocks are applied by primary mandate only
because same-date constituent weights have not yet been captured.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

import yaml


ROLE_MAP = {
    "direct_sk_hynix": {
        "holding_mode": "legacy_concentrated_cyclical_conviction",
        "portfolio_job": "Domain-edge business position, but also employer-linked household risk.",
        "default_action_now": "freeze_additions_and_review_quarterly",
        "review_focus": ["HBM qualification and yield", "DRAM supply discipline", "free-cash-flow conversion", "employer and household correlation"],
        "duplicate_risk": "very_high",
    },
    "ace_nvidia_value_chain": {
        "holding_mode": "secular_trend_satellite",
        "portfolio_job": "AI picks-and-shovels exposure across multiple layers.",
        "default_action_now": "hold_without_new_cash_until_constituents_and_valuation_are_checked",
        "review_focus": ["NVIDIA and semiconductor overlap", "top holdings", "valuation", "active-manager drift"],
        "duplicate_risk": "very_high",
    },
    "rise_samsung_sk_bond_mix_50": {
        "holding_mode": "transition_hybrid",
        "portfolio_job": "Partial fixed-income wrapper that still carries concentrated Korean memory equity.",
        "default_action_now": "hold_and_capture_current_equity_bond_split",
        "review_focus": ["current equity and bond weights", "Samsung and SK hynix weights", "duration", "fees"],
        "duplicate_risk": "high",
    },
    "time_global_ai_active": {
        "holding_mode": "secular_trend_satellite",
        "portfolio_job": "Active cross-layer AI exposure.",
        "default_action_now": "hold_without_new_cash_until_constituents_and_style_drift_are_checked",
        "review_focus": ["current constituents", "platform and semiconductor overlap", "turnover", "fees"],
        "duplicate_risk": "very_high",
    },
    "plus_global_hbm": {
        "holding_mode": "cyclical_trend_satellite",
        "portfolio_job": "Explicit HBM and memory value-chain conviction.",
        "default_action_now": "freeze_additions",
        "review_focus": ["memory supplier weights", "HBM capacity and pricing", "foundry and packaging overlap", "valuation"],
        "duplicate_risk": "very_high",
    },
    "ace_google_value_chain": {
        "holding_mode": "compounder_trend_hybrid",
        "portfolio_job": "Google ecosystem and AI value-chain exposure.",
        "default_action_now": "hold_without_new_cash_until_constituents_and_capex_returns_are_checked",
        "review_focus": ["Google weight", "AI capex returns", "supplier overlap", "active-manager drift"],
        "duplicate_risk": "high",
    },
    "kodex_us_semiconductor": {
        "holding_mode": "cyclical_sector_satellite",
        "portfolio_job": "Broad U.S. semiconductor cycle exposure.",
        "default_action_now": "freeze_additions_and_compare_with_other_semiconductor_funds",
        "review_focus": ["index methodology", "top holdings", "memory and NVIDIA overlap", "fees"],
        "duplicate_risk": "very_high",
    },
    "kodex_us_ai_power_infra": {
        "holding_mode": "secular_infrastructure_satellite",
        "portfolio_job": "Power, grid, cooling and electrical bottleneck exposure.",
        "default_action_now": "hold_and_research_value_capture_without_adding",
        "review_focus": ["top-five concentration", "orders to cash conversion", "data-center revenue boundary", "valuation"],
        "duplicate_risk": "medium",
    },
    "kodex_200": {
        "holding_mode": "regional_core_not_global_core",
        "portfolio_job": "Broad Korean equity exposure with embedded semiconductor concentration.",
        "default_action_now": "hold_but_do_not_count_as_global_core",
        "review_focus": ["Samsung and SK hynix index weights", "household Korea exposure", "fees"],
        "duplicate_risk": "high",
    },
    "rise_us_semiconductor_nyse_h": {
        "holding_mode": "cyclical_sector_satellite",
        "portfolio_job": "Currency-hedged U.S. semiconductor exposure.",
        "default_action_now": "freeze_additions_and_compare_for_consolidation",
        "review_focus": ["hedging cost", "index methodology", "overlap", "fees"],
        "duplicate_risk": "very_high",
    },
    "kodex_us_ai_optical_network": {
        "holding_mode": "secular_infrastructure_satellite",
        "portfolio_job": "Optical and networking bottleneck exposure.",
        "default_action_now": "hold_at_satellite_size_without_adding",
        "review_focus": ["top-three concentration", "port-speed transition", "component commoditization", "valuation"],
        "duplicate_risk": "medium_high",
    },
    "rise_global_nuclear": {
        "holding_mode": "long_cycle_policy_project_satellite",
        "portfolio_job": "Firm-generation and nuclear-policy exposure.",
        "default_action_now": "hold_at_satellite_size_without_adding",
        "review_focus": ["fund constituents", "project timelines", "policy risk", "power-fund overlap"],
        "duplicate_risk": "medium",
    },
    "gold_9999": {
        "holding_mode": "non_ai_diversifier",
        "portfolio_job": "Visible non-AI diversifier and geopolitical hedge.",
        "default_action_now": "retain_and_review_inside_total_household_assets",
        "review_focus": ["total gold weight", "spread and custody", "role versus KRW liabilities"],
        "duplicate_risk": "low",
    },
    "tiger_philadelphia_semiconductor": {
        "holding_mode": "cyclical_sector_satellite",
        "portfolio_job": "Additional U.S. semiconductor index exposure.",
        "default_action_now": "freeze_additions_and_compare_for_consolidation",
        "review_focus": ["overlap", "index methodology", "fees", "tax treatment"],
        "duplicate_risk": "very_high",
    },
    "koact_global_ai_memory": {
        "holding_mode": "small_cyclical_trend_satellite",
        "portfolio_job": "Small active AI-memory exposure.",
        "default_action_now": "freeze_additions_and_test_whether_the_wrapper_is_redundant",
        "review_focus": ["current constituents", "SK hynix and Micron weights", "turnover", "fees"],
        "duplicate_risk": "very_high",
    },
    "kiwoom_global_grid": {
        "holding_mode": "small_secular_infrastructure_satellite",
        "portfolio_job": "Small global grid-infrastructure exposure.",
        "default_action_now": "hold_without_adding_until_overlap_is_known",
        "review_focus": ["utilities versus equipment split", "power-fund overlap", "fees", "valuation"],
        "duplicate_risk": "medium_high",
    },
    "hanaro_us_ai_memory_top4": {
        "holding_mode": "tiny_concentrated_option",
        "portfolio_job": "Very small top-four memory option that duplicates the dominant thesis.",
        "default_action_now": "do_not_add_and_review_for_simplification",
        "review_focus": ["top-four names", "weighting method", "fees", "redundancy"],
        "duplicate_risk": "very_high",
    },
}


STRESS_SCENARIOS = [
    {
        "scenario_id": "direct_employer_stock_minus_50",
        "name": "Direct employer stock shock",
        "purpose": "Isolate the effect of a fifty-percent SK hynix decline while every other captured asset is unchanged.",
        "shocks_percent": {"direct_employer_linked_memory": -50},
    },
    {
        "scenario_id": "semiconductor_downcycle",
        "name": "Correlated semiconductor downcycle",
        "purpose": "Test a memory and semiconductor contraction that also weakens Korean equities and AI wrappers.",
        "shocks_percent": {
            "direct_employer_linked_memory": -50,
            "korea_memory_equity_bond_mix": -20,
            "broad_korea_equity": -20,
            "memory_hbm_thematic": -40,
            "broad_semiconductor": -35,
            "ai_value_chain_mixed": -25,
            "power_grid_infrastructure": -15,
            "optical_network": -25,
            "nuclear_generation": -10,
            "non_ai_gold_diversifier": 10,
        },
    },
    {
        "scenario_id": "ai_capex_and_financing_bust",
        "name": "AI capex and financing reversal",
        "purpose": "Test Soros-style reflexive reversal across compute, network, power and project-financed infrastructure.",
        "shocks_percent": {
            "direct_employer_linked_memory": -45,
            "korea_memory_equity_bond_mix": -20,
            "broad_korea_equity": -20,
            "memory_hbm_thematic": -45,
            "broad_semiconductor": -40,
            "ai_value_chain_mixed": -35,
            "power_grid_infrastructure": -30,
            "optical_network": -40,
            "nuclear_generation": -25,
            "non_ai_gold_diversifier": 15,
        },
    },
    {
        "scenario_id": "ai_reflexive_upside",
        "name": "AI reflexive upside and concentration drift",
        "purpose": "Show that success can increase concentration and create a rebalance need even without a broken thesis.",
        "shocks_percent": {
            "direct_employer_linked_memory": 40,
            "korea_memory_equity_bond_mix": 15,
            "broad_korea_equity": 15,
            "memory_hbm_thematic": 35,
            "broad_semiconductor": 30,
            "ai_value_chain_mixed": 25,
            "power_grid_infrastructure": 20,
            "optical_network": 30,
            "nuclear_generation": 15,
            "non_ai_gold_diversifier": -5,
        },
    },
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def additional_capital_for_target(amount: int, total: int, target_percent: float) -> int:
    return max(0, math.ceil(amount / (target_percent / 100) - total))


def months_needed(required_krw: int, monthly_surplus_krw: int, bonus_krw: int) -> int | None:
    residual = max(0, required_krw - bonus_krw)
    if residual == 0:
        return 0
    if monthly_surplus_krw <= 0:
        return None
    return math.ceil(residual / monthly_surplus_krw)


def build_holdings(products: list[dict]) -> list[dict]:
    product_ids = {row["product_id"] for row in products}
    assert product_ids == set(ROLE_MAP), {
        "missing_roles": sorted(product_ids - set(ROLE_MAP)),
        "unused_roles": sorted(set(ROLE_MAP) - product_ids),
    }
    rows = []
    for product in products:
        rows.append({
            "product_id": product["product_id"],
            "label": product["label"],
            "mandate_group": product["mandate_group"],
            "evaluation_amount_krw": product["evaluation_amount_krw"],
            "snapshot_percent": product["snapshot_percent"],
            **ROLE_MAP[product["product_id"]],
        })
    return rows


def build_stress_tests(products: list[dict], total: int) -> list[dict]:
    rows = []
    for scenario in STRESS_SCENARIOS:
        contributions = []
        ending_values = {}
        for product in products:
            shock = scenario["shocks_percent"].get(product["mandate_group"], 0)
            impact = round(product["evaluation_amount_krw"] * shock / 100)
            ending = product["evaluation_amount_krw"] + impact
            ending_values[product["product_id"]] = ending
            contributions.append({
                "product_id": product["product_id"],
                "shock_percent": shock,
                "impact_krw": impact,
            })
        total_impact = sum(row["impact_krw"] for row in contributions)
        ending_total = total + total_impact
        nonzero_contributions = [row for row in contributions if row["impact_krw"] != 0]
        largest = sorted(nonzero_contributions, key=lambda row: abs(row["impact_krw"]), reverse=True)[:5]
        rows.append({
            **scenario,
            "result": {
                "portfolio_impact_krw": total_impact,
                "portfolio_impact_percent": round(total_impact / total * 100, 2),
                "ending_securities_value_krw": ending_total,
                "ending_direct_sk_hynix_percent": round(ending_values["direct_sk_hynix"] / ending_total * 100, 2),
                "largest_absolute_contributors": largest,
            },
            "boundary": "Sensitivity only; not a probability-weighted forecast. Income loss, tax, trading restrictions and ETF look-through are excluded.",
        })
    return rows


def build_checkpoints(total: int, sk_amount: int, ai_amount: int) -> list[dict]:
    specs = [
        ("first_transition", 45, 80),
        ("second_transition", 40, 60),
        ("destination", 10, 20),
    ]
    rows = []
    for checkpoint_id, sk_target, ai_target in specs:
        sk_required = additional_capital_for_target(sk_amount, total, sk_target)
        ai_required = additional_capital_for_target(ai_amount, total, ai_target)
        rows.append({
            "checkpoint_id": checkpoint_id,
            "direct_sk_hynix_target_percent": sk_target,
            "explicit_ai_target_percent": ai_target,
            "non_sk_capital_required_krw": sk_required,
            "non_ai_capital_required_krw": ai_required,
            "binding_no_sale_requirement_krw": max(sk_required, ai_required),
            "binding_constraint": "direct_sk_hynix" if sk_required >= ai_required else "explicit_ai",
        })
    return rows


def build_glide_matrix(checkpoints: list[dict]) -> list[dict]:
    first = next(row for row in checkpoints if row["checkpoint_id"] == "first_transition")
    second = next(row for row in checkpoints if row["checkpoint_id"] == "second_transition")
    rows = []
    for monthly in [500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000]:
        for bonus in [0, 10_000_000, 20_000_000, 30_000_000]:
            rows.append({
                "monthly_non_ai_surplus_krw": monthly,
                "one_time_non_ai_bonus_krw": bonus,
                "months_to_first_transition": months_needed(first["binding_no_sale_requirement_krw"], monthly, bonus),
                "months_to_second_transition": months_needed(second["binding_no_sale_requirement_krw"], monthly, bonus),
            })
    return rows


def personalized_projection(checkpoints: list[dict], monthly: int | None, bonus: int | None) -> dict:
    if monthly is None and bonus is None:
        return {
            "status": "awaiting_actual_monthly_surplus_and_bonus",
            "monthly_non_ai_surplus_krw": None,
            "one_time_non_ai_bonus_krw": None,
            "checkpoint_projection": [],
        }
    monthly_value = monthly or 0
    bonus_value = bonus or 0
    return {
        "status": "scenario_not_commitment",
        "monthly_non_ai_surplus_krw": monthly_value,
        "one_time_non_ai_bonus_krw": bonus_value,
        "checkpoint_projection": [{
            "checkpoint_id": row["checkpoint_id"],
            "months_if_prices_are_unchanged_and_all_new_money_is_outside_the_concentration": months_needed(
                row["binding_no_sale_requirement_krw"], monthly_value, bonus_value
            ),
        } for row in checkpoints],
    }


def build_execution(
    comparison: dict,
    policy: dict,
    accessed_on: str,
    monthly_surplus_krw: int | None,
    bonus_krw: int | None,
) -> dict:
    snapshot = comparison["portfolio_snapshot"]
    products = snapshot["products"]
    total = snapshot["total_evaluation_amount_krw"]
    concentration = comparison["concentration_read"]
    sk_amount = concentration["direct_SK_hynix_amount_krw"]
    ai_amount = concentration["clearly_AI_or_data_center_linked_primary_mandates_amount_krw"]
    checkpoints = build_checkpoints(total, sk_amount, ai_amount)
    stress_tests = build_stress_tests(products, total)
    downcycle = next(row for row in stress_tests if row["scenario_id"] == "semiconductor_downcycle")
    ai_bust = next(row for row in stress_tests if row["scenario_id"] == "ai_capex_and_financing_bust")
    upside = next(row for row in stress_tests if row["scenario_id"] == "ai_reflexive_upside")
    return {
        "schema_version": 1,
        "status": "active_execution_draft_awaiting_household_inputs",
        "created_at": accessed_on,
        "updated_at": accessed_on,
        "area": "FINANCE",
        "title": "Brian investment policy execution, stress and glide-path ledger",
        "privacy": "Personal holdings and scenario inputs remain local; no external trade is authorized.",
        "purpose": "Turn the investment policy into repeatable stress tests, holding roles, concentration checkpoints and monthly decision gates.",
        "human_readable_summary_ko": {
            "core_read": f"반도체 동반 하락 민감도에서는 포착된 증권자산이 {abs(downcycle['result']['portfolio_impact_percent']):.2f}% 감소하고, AI 설비투자 반전 민감도에서는 {abs(ai_bust['result']['portfolio_impact_percent']):.2f}% 감소한다.",
            "success_risk": f"AI 상승 민감도에서는 포트폴리오가 {upside['result']['portfolio_impact_percent']:.2f}% 증가하지만 SK하이닉스 비중도 {upside['result']['ending_direct_sk_hynix_percent']:.2f}%로 올라가므로 성공 자체가 리밸런싱 사유가 될 수 있다.",
            "action_now": "현금흐름과 비상자금을 먼저 복구하고, 신규 AI 매수를 멈춘 채 ETF 실구성·세금·가계 전체 노출을 측정한다.",
        },
        "source_snapshot": {
            "as_of": snapshot["as_of"],
            "securities_and_gold_total_krw": total,
            "product_records": len(products),
            "direct_sk_hynix_amount_krw": sk_amount,
            "explicit_ai_lower_bound_amount_krw": ai_amount,
            "source_refs": [
                "life/finance/ai_data_center_investment_comparison_202607.yaml",
                "life/finance/brian_investment_policy_202607.yaml",
            ],
        },
        "holding_role_register": build_holdings(products),
        "stress_test_method": {
            "type": "deterministic_sensitivity_not_forecast",
            "method": "Apply the stated shock to every product's primary mandate and sum KRW impacts.",
            "known_limitations": [
                "Current ETF constituent weights are not yet captured.",
                "Income, bonus, pension, cash, debt, housing, tax and spouse assets are excluded.",
                "Cross-asset correlations and recovery paths are not estimated.",
                "A stress result is not a prediction or probability statement.",
            ],
        },
        "stress_tests": stress_tests,
        "income_interruption_overlay": {
            "status": "awaiting_essential_monthly_spending",
            "six_month_income_gap_formula": "6 * essential_monthly_spending_krw - reliable_other_income_during_gap_krw",
            "combined_downcycle_formula": f"{abs(downcycle['result']['portfolio_impact_krw'])} + six_month_income_gap_krw",
            "reason": "The household risk is larger than the securities drawdown when salary and bonus are correlated with the semiconductor cycle.",
        },
        "concentration_checkpoints": checkpoints,
        "no_sale_glide_path_matrix": {
            "assumption": "Prices remain unchanged and every contribution and bonus is invested outside both SK hynix and explicit AI exposure.",
            "rows": build_glide_matrix(checkpoints),
            "interpretation": "If the second checkpoint takes too long, the policy calls for a tax-aware staged-sale discussion after liquidity and household inputs are complete.",
        },
        "personalized_glide_path": personalized_projection(checkpoints, monthly_surplus_krw, bonus_krw),
        "monthly_dashboard_template": {
            "month": None,
            "take_home_income_krw": None,
            "essential_spending_krw": None,
            "discretionary_spending_krw": None,
            "total_outflow_krw": None,
            "monthly_surplus_krw": None,
            "savings_rate_percent": None,
            "liquid_reserve_krw": None,
            "reserve_months": None,
            "direct_sk_hynix_percent": None,
            "explicit_ai_percent": None,
            "broad_global_core_percent": None,
            "new_ai_purchase_krw": 0,
            "policy_breach": None,
            "one_decision_for_next_month": None,
        },
        "decision_tree": [
            {"gate": 1, "question": "Is monthly cashflow positive and measured?", "if_no": "No new discretionary investment; close spending and fixed costs."},
            {"gate": 2, "question": "Is the liquid reserve at least three months of essential spending?", "if_no": "Send one hundred percent of new surplus to liquidity."},
            {"gate": 3, "question": "Is the liquid reserve at the nine-month target?", "if_no": "Use the policy's seventy-percent reserve and thirty-percent global-core rule."},
            {"gate": 4, "question": "Are employer stock and explicit AI inside their transition bands?", "if_no": "Send no new money to AI; use global core, safe assets and non-AI diversifiers."},
            {"gate": 5, "question": "Are exact ETF holdings, valuation, taxes and household overlap known?", "if_no": "Research only; do not add the position."},
            {"gate": 6, "question": "Does the investment score at least eighty with written falsifiers?", "if_no": "Reject or watchlist."},
            {"gate": 7, "question": "Does the initial size remain inside every cap after a fifty-percent loss?", "if_no": "Reduce size or do not buy."},
            {"gate": 8, "question": "Has operating evidence improved after the initial position?", "if_yes": "Scale only if valuation remains attractive; otherwise hold or exit."},
        ],
        "simplification_queue": [
            {
                "priority": 1,
                "group": "semiconductor_and_memory_wrappers",
                "products": ["plus_global_hbm", "kodex_us_semiconductor", "rise_us_semiconductor_nyse_h", "tiger_philadelphia_semiconductor", "koact_global_ai_memory", "hanaro_us_ai_memory_top4"],
                "decision_needed": "After same-date holdings and tax lots are captured, determine whether one or two wrappers can express the intended exposure with less duplication.",
            },
            {
                "priority": 2,
                "group": "active_ai_value_chain_wrappers",
                "products": ["ace_nvidia_value_chain", "time_global_ai_active", "ace_google_value_chain"],
                "decision_needed": "Compare current constituents, fees, turnover and unique exposure before retaining all three.",
            },
            {
                "priority": 3,
                "group": "power_grid_generation_wrappers",
                "products": ["kodex_us_ai_power_infra", "kiwoom_global_grid", "rise_global_nuclear"],
                "decision_needed": "Separate equipment, utility and generation economics and keep only genuinely distinct roles.",
            },
        ],
        "next_required_inputs": [
            "verified essential monthly spending",
            "current liquid cash and deposits",
            "expected after-tax bonus range and timing",
            "tax lot and account type for every holding",
            "same-date official ETF constituent files",
            "spouse holdings and household income dependency",
            "maximum tolerable drawdown in KRW and percent",
        ],
        "external_reference_notes": [
            {
                "title": "Concentrate on Concentration Risk",
                "publisher": "FINRA",
                "url": "https://www.finra.org/investors/insights/concentration-risk",
                "relevance": "ETF count can conceal correlated company, sector and employer exposure; look under each fund's hood.",
            },
            {
                "title": "Love Your Company Stock? Here's What to Know.",
                "publisher": "FINRA",
                "url": "https://www.finra.org/investors/insights/love-your-company-stock-what-to-know",
                "relevance": "Employer problems can hit employment and investments together; the page notes that some experts use ten percent as a ceiling, while circumstances can justify less.",
            },
            {
                "title": "Asset Allocation and Diversification",
                "publisher": "Investor.gov",
                "url": "https://www.investor.gov/introduction-investing/getting-started/asset-allocation",
                "relevance": "Several narrow ETFs do not necessarily provide diversification; top holdings and overlap should be checked.",
            },
        ],
        "decision_boundary": "No trade follows automatically from this artifact. User confirmation, current account data, tax review and employer compliance remain required.",
        "source_snapshot_sha256": canonical_hash({"comparison": comparison, "policy": policy}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--comparison", type=Path, default=Path("life/finance/ai_data_center_investment_comparison_202607.yaml"))
    parser.add_argument("--policy", type=Path, default=Path("life/finance/brian_investment_policy_202607.yaml"))
    parser.add_argument("--output", type=Path, default=Path("life/finance/brian_investment_policy_execution_202607.yaml"))
    parser.add_argument("--monthly-surplus-krw", type=int)
    parser.add_argument("--bonus-krw", type=int)
    args = parser.parse_args()
    comparison = load_yaml(args.comparison)
    policy = load_yaml(args.policy)
    result = build_execution(comparison, policy, args.accessed_on, args.monthly_surplus_krw, args.bonus_krw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "holdings": len(result["holding_role_register"]),
        "stress_tests": len(result["stress_tests"]),
        "glide_rows": len(result["no_sale_glide_path_matrix"]["rows"]),
        "source_snapshot_sha256": result["source_snapshot_sha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
