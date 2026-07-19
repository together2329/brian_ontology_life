#!/usr/bin/env python3
"""Build Brian's AI data-center portfolio comparison and final research gap audit.

The output uses the saved 2026-07-15 holding snapshot.  ETF products are mapped
by their stated wrapper mandate only; current constituent weights are deliberately
not inferred from product names.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import yaml


def mapping(product_id: str, label: str, mandate_group: str, layers: list[str], overlap: str) -> dict:
    return {
        "product_id": product_id,
        "label": label,
        "mandate_group": mandate_group,
        "research_layers": layers,
        "overlap_note": overlap,
    }


PRODUCT_MAP = {
    "SK하이닉스 보통주": mapping("direct_sk_hynix", "SK하이닉스 직접주식", "direct_employer_linked_memory", ["compute_memory_network"], "Same company drives employment income, expected bonus and direct equity value."),
    "SK하이닉스": mapping("direct_sk_hynix", "SK하이닉스 직접주식", "direct_employer_linked_memory", ["compute_memory_network"], "Same company drives employment income, expected bonus and direct equity value."),
    "RISE 삼성전자SK하이닉스채권혼합50": mapping("rise_samsung_sk_bond_mix_50", "RISE 삼성전자SK하이닉스채권혼합50", "korea_memory_equity_bond_mix", ["compute_memory_network", "fixed_income_component"], "The wrapper mixes concentrated Samsung/SK hynix equity with bonds; exact current sleeves require a constituent capture."),
    "KODEX 200": mapping("kodex_200", "KODEX 200", "broad_korea_equity", ["broad_equity_with_embedded_semiconductors"], "Broad label still embeds Samsung Electronics, SK hynix and the Korean cycle."),
    "TIGER 미국필라델피아반도체나스닥": mapping("tiger_philadelphia_semiconductor", "TIGER 미국필라델피아반도체나스닥", "broad_semiconductor", ["compute_memory_network"], "Likely overlaps other U.S. semiconductor and NVIDIA value-chain wrappers; exact weights are not captured."),
    "PLUS 글로벌HBM반도체": mapping("plus_global_hbm", "PLUS 글로벌HBM반도체", "memory_hbm_thematic", ["compute_memory_network"], "Likely repeats memory, foundry and accelerator supply-chain holdings already owned directly or through other funds."),
    "TIME 글로벌AI인공지능액티브": mapping("time_global_ai_active", "TIME 글로벌AI인공지능액티브", "ai_value_chain_mixed", ["hyperscale_buyers_and_cloud", "compute_memory_network", "applications_and_services"], "Active mandate may change holdings and can overlap Google, NVIDIA and broad semiconductor wrappers."),
    "ACE 엔비디아밸류체인액티브": mapping("ace_nvidia_value_chain", "ACE 엔비디아밸류체인액티브", "ai_value_chain_mixed", ["compute_memory_network", "power_cooling_electrical", "physical_data_center_operators"], "Value-chain label can repeat NVIDIA and its suppliers already present in semiconductor and HBM funds."),
    "ACE 구글밸류체인액티브": mapping("ace_google_value_chain", "ACE 구글밸류체인액티브", "ai_value_chain_mixed", ["hyperscale_buyers_and_cloud", "compute_memory_network", "power_cooling_electrical"], "Google ecosystem exposure can overlap the global AI active fund and other infrastructure wrappers."),
    "RISE 미국반도체NYSE(H)": mapping("rise_us_semiconductor_nyse_h", "RISE 미국반도체NYSE(H)", "broad_semiconductor", ["compute_memory_network"], "Currency-hedged U.S. semiconductor exposure likely overlaps the unhedged U.S. semiconductor wrappers."),
    "KODEX 미국AI전력핵심인프라": mapping("kodex_us_ai_power_infra", "KODEX 미국AI전력핵심인프라", "power_grid_infrastructure", ["power_cooling_electrical", "utilities_and_generation"], "Provides a different bottleneck wrapper, but exact overlap with grid, nuclear and value-chain funds is not captured."),
    "KIWOOM 글로벌전력GRID인프라": mapping("kiwoom_global_grid", "KIWOOM 글로벌전력GRID인프라", "power_grid_infrastructure", ["power_cooling_electrical", "utilities_and_generation"], "Grid-equipment and utility holdings may overlap the AI power and nuclear wrappers."),
    "KODEX 미국AI광통신네트워크": mapping("kodex_us_ai_optical_network", "KODEX 미국AI광통신네트워크", "optical_network", ["compute_memory_network"], "Optical and networking suppliers can also be held in semiconductor and NVIDIA value-chain funds."),
    "KoAct 글로벌AI메모리반도체액티브": mapping("koact_global_ai_memory", "KoAct 글로벌AI메모리반도체액티브", "memory_hbm_thematic", ["compute_memory_network"], "Directly reinforces the existing employer, SK hynix and HBM concentration."),
    "HANARO 미국AI메모리반도체TOP4": mapping("hanaro_us_ai_memory_top4", "HANARO 미국AI메모리반도체TOP4", "memory_hbm_thematic", ["compute_memory_network"], "Concentrated top-four design increases single-name overlap despite its small current value."),
    "KODEX 미국반도체": mapping("kodex_us_semiconductor", "KODEX 미국반도체", "broad_semiconductor", ["compute_memory_network"], "Likely overlaps the Philadelphia, NYSE hedged, HBM and NVIDIA value-chain wrappers."),
    "RISE 글로벌원자력": mapping("rise_global_nuclear", "RISE 글로벌원자력", "nuclear_generation", ["utilities_and_generation"], "Generation exposure is distinct from chips but can overlap the power-infrastructure wrappers and adds policy or project risk."),
    "금 99.99_1kg": mapping("gold_9999", "금 99.99", "non_ai_gold_diversifier", ["non_AI_diversifier"], "Only visible holding in this securities snapshot whose mandate is structurally outside the AI and Korean equity chain."),
}


MANDATE_ORDER = [
    "direct_employer_linked_memory",
    "korea_memory_equity_bond_mix",
    "broad_korea_equity",
    "memory_hbm_thematic",
    "broad_semiconductor",
    "ai_value_chain_mixed",
    "power_grid_infrastructure",
    "optical_network",
    "nuclear_generation",
    "non_ai_gold_diversifier",
]


LAYER_COMPARISON = [
    {
        "layer": "compute_memory_network",
        "evidence_state": "Strong current revenue and order evidence exists for leading semiconductor, memory and networking companies, while cyclicality, valuation and customer concentration remain material.",
        "brian_exposure_state": "Very high by direct SK hynix, memory/HBM, broad semiconductor, NVIDIA value-chain and employment links.",
        "incremental_cash_view": "Not the default destination for new salary cash until household look-through concentration and liquidity are measured.",
    },
    {
        "layer": "hyperscale_buyers_and_cloud",
        "evidence_state": "Official region registries and financial profiles show broad buildout, but service Regions, AZs and architecture maxima do not equal physical buildings or returns.",
        "brian_exposure_state": "Present through Google and global-AI wrappers, with exact weights unknown.",
        "incremental_cash_view": "Compare valuation, capex burden and current constituent overlap before adding another platform wrapper.",
    },
    {
        "layer": "power_cooling_electrical",
        "evidence_state": "Backlog, orders and data-center demand are visible across electrical and cooling suppliers, but data-center-only revenue and margins are rarely disclosed.",
        "brian_exposure_state": "Explicitly present through AI power and grid wrappers and indirectly through value-chain funds; primary-mandate value is much smaller than chips.",
        "incremental_cash_view": "Best candidate for further comparison inside the AI thesis, but only after exact holdings and valuation show that it is genuinely different exposure.",
    },
    {
        "layer": "utilities_and_generation",
        "evidence_state": "Large-load agreements and generation needs are real, while permits, interconnection, cost recovery and energization create long execution paths.",
        "brian_exposure_state": "Present through power/grid and global nuclear wrappers.",
        "incremental_cash_view": "Treat as regulated or project-risk diversification, not a simple leveraged proxy for data-center MW headlines.",
    },
    {
        "layer": "physical_data_center_operators",
        "evidence_state": "Eighty-nine operators now have a scope-preserving crosswalk, but site economics, utilization and return on capital remain limited, especially for private firms.",
        "brian_exposure_state": "Possible indirect exposure through value-chain funds; exact weights are unknown.",
        "incremental_cash_view": "Do not rank by facility or GW headlines; require reporting boundary, leverage, utilization and valuation first.",
    },
    {
        "layer": "neoclouds",
        "evidence_state": "Demand and contracted pipelines are strong, but financing, depreciation, customer concentration and installed-versus-ordered GPU ambiguity are high.",
        "brian_exposure_state": "Possible indirect exposure through active AI or value-chain wrappers; exact weights are unknown.",
        "incremental_cash_view": "Not a core allocation candidate until ownership, cash generation, leverage and customer concentration pass a stricter gate.",
    },
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def evaluation_amount(lot: dict) -> tuple[int, str]:
    if "evaluation_amount_krw" in lot:
        return int(lot["evaluation_amount_krw"]), "reported"
    value = round(lot["quantity"] * lot["average_cost_krw"] + lot["evaluation_profit_krw"])
    return int(value), "derived_as_quantity_times_average_cost_plus_evaluation_profit"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_products(finance: dict) -> tuple[list[dict], int]:
    snapshot = next(row for row in finance["holding_snapshots"] if row["id"] == "holding_snapshot_20260715_current_portfolio")
    grouped: dict[str, dict] = {}
    for lot in snapshot["lots"]:
        source_name = lot["asset_name"]
        assert source_name in PRODUCT_MAP, source_name
        product_map = PRODUCT_MAP[source_name]
        amount, method = evaluation_amount(lot)
        product = grouped.setdefault(product_map["product_id"], {
            **product_map,
            "source_asset_names": [],
            "source_lot_ids": [],
            "quantity": 0,
            "evaluation_amount_krw": 0,
            "valuation_methods": [],
        })
        product["source_asset_names"].append(source_name)
        product["source_lot_ids"].append(lot["id"])
        product["quantity"] += lot["quantity"]
        product["evaluation_amount_krw"] += amount
        product["valuation_methods"].append(method)
    total = sum(row["evaluation_amount_krw"] for row in grouped.values())
    for row in grouped.values():
        row["source_asset_names"] = list(dict.fromkeys(row["source_asset_names"]))
        row["valuation_methods"] = list(dict.fromkeys(row["valuation_methods"]))
        row["snapshot_percent"] = round(row["evaluation_amount_krw"] / total * 100, 2)
        row["constituent_evidence_status"] = "direct_security" if row["product_id"] in {"direct_sk_hynix", "gold_9999"} else "current_fund_constituent_weights_not_captured"
    return sorted(grouped.values(), key=lambda row: (-row["evaluation_amount_krw"], row["product_id"])), total


def build_groups(products: list[dict], total: int) -> list[dict]:
    grouped = defaultdict(int)
    members = defaultdict(list)
    for row in products:
        grouped[row["mandate_group"]] += row["evaluation_amount_krw"]
        members[row["mandate_group"]].append(row["product_id"])
    return [{
        "mandate_group": group,
        "evaluation_amount_krw": grouped[group],
        "snapshot_percent": round(grouped[group] / total * 100, 2),
        "products": members[group],
        "boundary": "Primary wrapper mandate only; not a look-through sum of underlying companies or sectors.",
    } for group in MANDATE_ORDER]


def registry_counts(args: argparse.Namespace) -> dict:
    landscape = yaml.safe_load(args.landscape.read_text(encoding="utf-8"))
    financials = yaml.safe_load(args.financials.read_text(encoding="utf-8"))
    neocloud = load_json(args.import_dir / "neocloud_disclosure_summary.json")
    operators = load_json(args.import_dir / "physical_operator_disclosure_summary.json")
    suppliers = load_json(args.import_dir / "power_cooling_supply_chain_summary.json")
    accelerators = load_json(args.import_dir / "accelerator_disclosure_summary.json")
    coverage = load_json(args.import_dir / "global_data_center_coverage_audit_summary.json")
    return {
        "global_osm_mapped_objects": coverage["baseline"]["osm_mapped_objects"],
        "global_iso2_country_records": coverage["baseline"]["iso2_country_records"],
        "distinct_nonempty_osm_operator_labels": coverage["baseline"]["distinct_nonempty_raw_operator_labels"],
        "osm_objects_with_operator_label": coverage["baseline"]["objects_with_operator_label"],
        "osm_objects_without_operator_label": coverage["baseline"]["objects_without_operator_label"],
        "mapped_objects_routed_to_reviewed_profiles": coverage["review_join"]["mapped_objects_whose_raw_operator_label_routes_to_a_reviewed_profile"],
        "mapped_objects_not_routed_to_reviewed_profiles": coverage["baseline"]["osm_mapped_objects"] - coverage["review_join"]["mapped_objects_whose_raw_operator_label_routes_to_a_reviewed_profile"],
        "operator_tagged_objects_not_routed_to_reviewed_profiles": coverage["baseline"]["objects_with_operator_label"] - coverage["review_join"]["mapped_objects_whose_raw_operator_label_routes_to_a_reviewed_profile"],
        "percent_of_all_mapped_objects_routed_to_reviewed_profiles": coverage["review_join"]["percent_of_all_mapped_objects"],
        "percent_of_operator_tagged_objects_routed_to_reviewed_profiles": coverage["review_join"]["percent_of_operator_tagged_mapped_objects"],
        "priority_unreviewed_operator_entities": len(coverage["priority_unreviewed_operator_entities"]),
        "reviewed_campus_profiles": len(landscape["campus_profiles"]),
        "reviewed_financial_profiles": len(financials["financial_profiles"]),
        "neocloud_and_linked_host_records": neocloud["records"],
        "physical_operator_records": operators["operator_records"],
        "power_cooling_cable_utility_company_records": suppliers["company_records"],
        "atomic_accelerator_claims": accelerators["claim_records"],
    }


def build_comparison(finance: dict, products: list[dict], total: int, counts: dict, accessed_on: str) -> dict:
    groups = build_groups(products, total)
    group_index = {row["mandate_group"]: row for row in groups}
    direct = group_index["direct_employer_linked_memory"]
    ai_linked_groups = [
        "direct_employer_linked_memory", "memory_hbm_thematic", "broad_semiconductor",
        "ai_value_chain_mixed", "power_grid_infrastructure", "optical_network", "nuclear_generation",
    ]
    ai_linked = sum(group_index[key]["evaluation_amount_krw"] for key in ai_linked_groups)
    layer_comparison = [dict(row) for row in LAYER_COMPARISON]
    physical_operator_layer = next(row for row in layer_comparison if row["layer"] == "physical_data_center_operators")
    physical_operator_layer["evidence_state"] = (
        f"{counts['physical_operator_records']} operators have a scope-preserving crosswalk, but site economics, "
        "utilization and return on capital remain limited, especially for private firms."
    )
    known_total = next(row for row in finance["net_worth_estimates"] if row["id"] == "household_net_worth_estimate_20260715_all_reported_items")["assets"]["brian_stocks_etfs_gold_estimated_krw"]
    assert total == known_total
    return {
        "schema_version": 1,
        "status": "active_decision_support",
        "updated_at": accessed_on,
        "area": "FINANCE",
        "title": "Brian AI data-center investment comparison",
        "purpose": "Connect the saved portfolio snapshot to the reviewed AI data-center stack without mistaking ETF count for look-through diversification or research evidence for a trade instruction.",
        "privacy": "Personal portfolio analysis remains in Brian's local life-ontology repository; external execution is not authorized by this file.",
        "source_refs": [
            "life/finance/finance_active_log.yaml",
            "life/finance/cashflow_normalization_202607.yaml",
            "life/finance/investment_philosophy_research.yaml",
            "life/finance/ai_data_center_supply_chain_financials_202607.yaml",
            "life/knowledge/global_ai_data_center_landscape_202607.yaml",
            "life/imports/global_data_centers_20260717/power_cooling_supply_chain_registry.jsonl",
            "life/imports/global_data_centers_20260717/accelerator_disclosure_ledger.jsonl",
            "life/imports/global_data_centers_20260717/global_data_center_coverage_audit_summary.json",
        ],
        "research_inventory": counts,
        "portfolio_snapshot": {
            "as_of": "2026-07-15",
            "scope": "Brian stocks, ETFs and gold captured from multiple account screenshots",
            "total_evaluation_amount_krw": total,
            "product_records": len(products),
            "calculation": "Use reported evaluation amount when present; otherwise derive quantity times average cost plus evaluation profit.",
            "products": products,
        },
        "primary_mandate_groups": groups,
        "concentration_read": {
            "direct_SK_hynix_amount_krw": direct["evaluation_amount_krw"],
            "direct_SK_hynix_snapshot_percent": direct["snapshot_percent"],
            "clearly_AI_or_data_center_linked_primary_mandates_amount_krw": ai_linked,
            "clearly_AI_or_data_center_linked_primary_mandates_percent": round(ai_linked / total * 100, 2),
            "lower_bound_boundary": "The lower bound excludes KODEX 200 and the Samsung/SK hynix bond-mix wrapper even though both contain semiconductor exposure.",
            "household_correlation": "Employment income, expected bonus, direct SK hynix, memory and semiconductor ETFs, spouse-reported Korean semiconductor holdings and KOSPI exposure can respond to the same cycle.",
            "conclusion": "Brian is diversified across several AI infrastructure layers, but not yet proven diversified across underlying companies, the semiconductor cycle, employer income or household liquidity.",
        },
        "layer_comparison": layer_comparison,
        "cashflow_first_decision": {
            "current_state": "Brian reported near-zero monthly savings flow, no current deficit pressure and no need to sell immediately, with a future bonus expected.",
            "sequence": [
                "Complete the 2026-07-31 GPT/Codex tier and mobile-plan reductions and record actual recurring savings.",
                "Close July spending and set a sustainable August automatic-savings candidate before increasing investment risk.",
                "Define a liquid emergency reserve target separately from securities, pension, severance and home equity.",
                "Capture current underlying holdings and weights for all owned ETFs plus the spouse portfolio before claiming household diversification.",
                "Only then compare valuation and incremental exposure; inside the AI thesis, test whether power, grid and cooling add genuinely different earnings exposure versus existing chip-heavy wrappers.",
            ],
            "default_for_new_salary_cash_now": "Preserve monthly surplus and liquidity rather than automatically adding another AI or semiconductor ticker.",
            "existing_holdings_boundary": "No forced-sale conclusion follows from this review; future buy, hold, rebalance or sell decisions require tax, valuation, liquidity and concentration thresholds.",
        },
        "candidate_order_after_gates": [
            {"priority": 1, "candidate": "cash_and_liquidity_buffer", "reason": "Restores optionality and breaks the current near-zero salary-surplus pattern."},
            {"priority": 2, "candidate": "existing_broad_or_non_AI_diversifier", "reason": "Reduces dependence on employer, memory and AI-capex outcomes if look-through evidence confirms genuine diversification."},
            {"priority": 3, "candidate": "power_grid_cooling_value_pool", "reason": "Research shows real bottlenecks and order growth, while Brian's primary-mandate weight is smaller than chips; valuation and constituent overlap remain required."},
            {"priority": 4, "candidate": "additional_compute_memory_or_neocloud_risk", "reason": "Already highly represented or financially riskier; require unusually strong valuation, cash-flow and concentration evidence."},
        ],
        "decision_boundary": "This is a personalized research and sequencing record, not an instruction to buy, sell or change an external account.",
        "source_snapshot_sha256": canonical_hash({"finance": finance, "research_inventory": counts}),
    }


def build_gap_audit(counts: dict, accessed_on: str) -> dict:
    return {
        "schema_version": 1,
        "status": "priority_operator_baseline_complete_with_global_census_and_decision_gates_open",
        "updated_at": accessed_on,
        "area": "FINANCE",
        "secondary_areas": ["CAREER", "KNOWLEDGE"],
        "title": "Global AI data-center research final gap audit",
        "audited_inventory": counts,
        "completed_baseline": [
            "4,663-object OSM baseline plus 112-country and 822-operator-label coverage audit",
            f"P1/P2 named operator research queue exhausted at {counts['priority_unreviewed_operator_entities']} remaining entities",
            "official hyperscaler and Chinese cloud Region or location registries with Region, AZ and building boundaries",
            "scope-preserving neocloud and linked-host profiles",
            "major physical data-center operator crosswalk",
            "power, electrical, generation, cooling, cable and utility company crosswalk",
            "atomic accelerator disclosure ledger with overlap groups and no false fleet total",
            "company financial evidence ledger and Brian portfolio wrapper comparison",
        ],
        "coverage_interpretation": {
            "reviewed_profile_routing_percent_of_all_OSM_objects": counts["percent_of_all_mapped_objects_routed_to_reviewed_profiles"],
            "reviewed_profile_routing_percent_of_operator_tagged_OSM_objects": counts["percent_of_operator_tagged_objects_routed_to_reviewed_profiles"],
            "objects_without_operator_label": counts["osm_objects_without_operator_label"],
            "operator_tagged_objects_not_routed_to_reviewed_profiles": counts["operator_tagged_objects_not_routed_to_reviewed_profiles"],
            "boundary": "A zero P1/P2 queue completes the selected priority sequence; it does not turn OSM into an exhaustive global building, ownership or operating census.",
        },
        "remaining_gates": [
            {
                "priority": "A2",
                "gap": "Long-tail global facility, operator-alias and lifecycle resolution beyond the completed P1/P2 queue",
                "why_it_matters": "Only part of the OSM baseline routes to reviewed profiles, and OSM itself omits private, new, secure or inconsistently tagged buildings.",
                "completion_evidence": "Country-by-country official facility rosters, legal-asset and alias joins, lifecycle dates, coordinates and independent map reconciliation with explicit no-public-data outcomes.",
                "decision_impact": "Prevents the current baseline from being described as every data center worldwide or used as operator market share.",
            },
            {
                "priority": "A1",
                "gap": "Current ETF look-through holdings, weights, valuation date and cross-fund overlap",
                "why_it_matters": "Ticker count cannot establish company or factor diversification.",
                "completion_evidence": "Same-date official constituent files for every owned ETF, normalized by issuer and joined to product evaluation value.",
                "decision_impact": "Blocks a precise new-money allocation or concentration ceiling.",
            },
            {
                "priority": "A1",
                "gap": "Spouse exact holdings and household aggregation",
                "why_it_matters": "Reported SK hynix, Samsung and KOSPI exposure may materially increase the same household risk.",
                "completion_evidence": "User-approved current security names and values or weights, kept owner-separated and rolled up only analytically.",
                "decision_impact": "Blocks exact household semiconductor and Korea concentration.",
            },
            {
                "priority": "A1",
                "gap": "July cashflow actuals and liquid emergency-reserve target",
                "why_it_matters": "Monthly salary surplus is currently near zero even though net worth and future bonus reduce forced-sale risk.",
                "completion_evidence": "July income, fixed and variable spending, debt payments, liquid cash, recurring savings and August automatic-savings amount.",
                "decision_impact": "Blocks the appropriate pace of new investment from salary cash.",
            },
            {
                "priority": "A2",
                "gap": "Same-date valuation and expected-return comparison",
                "why_it_matters": "A strong industry and backlog do not establish an attractive purchase price.",
                "completion_evidence": "Price, enterprise value, earnings or cash-flow basis, growth assumptions, downside case and FX basis for each candidate or fund.",
                "decision_impact": "Blocks buy ranking even after layer exposure is known.",
            },
            {
                "priority": "A2",
                "gap": "Data-center-specific revenue, margin, cash flow and return on capital for industrial suppliers and operators",
                "why_it_matters": "Group results and broad segments can overstate direct AI economics.",
                "completion_evidence": "Company-reported segment or project allocation with accounting basis and period.",
                "decision_impact": "Limits comparison of power, cooling, utility and operator value capture.",
            },
            {
                "priority": "A2",
                "gap": "Announced, contracted, ordered, energized, utilized and billed capacity bridge",
                "why_it_matters": "Multi-GW headlines can take years to become earnings and may overlap.",
                "completion_evidence": "Site-level permits, financing, interconnection, commissioning, customer acceptance, load and revenue milestones.",
                "decision_impact": "Prevents pipeline from being valued as current operations.",
            },
            {
                "priority": "B",
                "gap": "Accelerator model, count, owner, host site, delivery, utilization, power cost and revenue bridge",
                "why_it_matters": "GPU announcements mix inventory, managed hardware, targets, architecture maxima and compute equivalents.",
                "completion_evidence": "Auditable site and ownership ledger tied to service and financial reporting.",
                "decision_impact": "Limits neocloud and campus unit economics.",
            },
            {
                "priority": "B",
                "gap": "Site-level power and cooling bill of materials and measured efficiency",
                "why_it_matters": "Vendor readiness claims do not prove installed product share, live liquid-cooled MW, PUE, WUE or water use.",
                "completion_evidence": "Commissioned equipment model, rating, quantity, topology and measured operating data by site.",
                "decision_impact": "Limits supplier attribution and physical bottleneck validation.",
            },
        ],
        "research_completion_definition": {
            "priority_operator_research_sequence": f"complete for the current {accessed_on} P1/P2 queue",
            "global_OSM_profile_routing": f"{counts['percent_of_all_mapped_objects_routed_to_reviewed_profiles']} percent of all objects and {counts['percent_of_operator_tagged_objects_routed_to_reviewed_profiles']} percent of operator-tagged objects",
            "all_global_facilities_or_future_projects": "not_claimed_and_not_possible_from_public_sources",
            "investment_execution": "intentionally_gated_by_A1_and_A2_items",
            "rule": "An explicit unknown is a completed audit result, not permission to estimate it into a fact.",
        },
        "next_update_triggers": [
            "2026-07 month-end cashflow close and fixed-cost changes",
            "same-date official ETF constituent capture",
            "material company earnings, guidance, financing or transaction update",
            "campus permit, interconnection, energization or customer-acceptance milestone",
            "bonus receipt or a material change in household assets, liabilities or income risk",
        ],
        "quality_checks": [
            "No cross-operator MW total was created from mixed power denominators.",
            "No accelerator total was created from mixed units, dates, ownership or lifecycle.",
            "No group revenue was relabeled as data-center revenue.",
            "No ETF product name was relabeled as a current underlying holding weight.",
            "No buy or sell action was executed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--finance-log", type=Path, default=Path("life/finance/finance_active_log.yaml"))
    parser.add_argument("--landscape", type=Path, default=Path("life/knowledge/global_ai_data_center_landscape_202607.yaml"))
    parser.add_argument("--financials", type=Path, default=Path("life/finance/ai_data_center_supply_chain_financials_202607.yaml"))
    parser.add_argument("--import-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    parser.add_argument("--comparison-output", type=Path, default=Path("life/finance/ai_data_center_investment_comparison_202607.yaml"))
    parser.add_argument("--audit-output", type=Path, default=Path("life/quality/global_ai_data_center_research_gap_audit_202607.yaml"))
    args = parser.parse_args()
    finance = yaml.safe_load(args.finance_log.read_text(encoding="utf-8"))
    products, total = build_products(finance)
    counts = registry_counts(args)
    comparison = build_comparison(finance, products, total, counts, args.accessed_on)
    audit = build_gap_audit(counts, args.accessed_on)
    args.comparison_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.comparison_output.write_text(yaml.safe_dump(comparison, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    args.audit_output.write_text(yaml.safe_dump(audit, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    print(json.dumps({"products": len(products), "total_krw": total, "comparison": str(args.comparison_output), "audit": str(args.audit_output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
