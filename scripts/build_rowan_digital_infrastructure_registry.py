#!/usr/bin/env python3
"""Build a scope-preserving Rowan project, OSM and disclosure registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


HOME_URL = "https://rowan.digital/"
PORTFOLIO_URL = "https://rowan.digital/portfolio/"
CINCO_URL = "https://rowan.digital/portfolio/cinco-texas/"
PERCHERON_URL = "https://rowan.digital/portfolio/percheron/"
TEMPLE_URL = "https://rowan.digital/portfolio/temple/"
BAUXITE_URL = "https://rowan.digital/portfolio/bauxite-i-ii-iii/"
SITE_SELECTION_URL = "https://rowan.digital/expertise/site-selection-land-development/"
ENERGY_URL = "https://rowan.digital/expertise/energy-strategy-infrastructure/"
SUSTAINABILITY_URL = "https://rowan.digital/responsibility/sustainable-impact/"
BAUXITE_APPROVAL_URL = "https://rowan.digital/bauxite-data-center-in-frederick-maryland-receives-site-development-plan-approval/"
CINCO_GROUNDBREAKING_URL = "https://rowan.digital/curabitur-blandit-ligula-sed-ante-euismod-et-efficitur-risus-mollis/"
TEMPLE_CONSTRUCTION_URL = "https://rowan.digital/rowan-powers-texas-growth-as-construction-begins-on-300-mw-temple-data-center/"
FINANCING_2025_URL = "https://rowan.digital/rowan-secures-1-2-billion-for-hyperscale-data-center-expansion-and-sustainability-initiatives/"
FINANCING_2026_URL = "https://rowan.digital/rowan-closes-3b-green-financing-for-turnkey-hyperscale-campus-in-high-growth-texas-market/"
BRAND_SCALE_URL = "https://rowan.digital/rowans-new-mark/"
QUINBROOK_ROWAN_URL = "https://www.quinbrook.com/our-portfolio/rowan-digital-infrastructure/"
QUINBROOK_BAUXITE_URL = "https://www.quinbrook.com/projects/bauxite/"
QUINBROOK_CINCO_URL = "https://www.quinbrook.com/projects/cinco/"
QUINBROOK_TEMPLE_URL = "https://www.quinbrook.com/projects/temple/"
QUINBROOK_UPP_URL = "https://www.quinbrook.com/news-insights/upp-invests-in-data-center-developer-rowan-digital-infrastructure/"
QUINBROOK_RECAP_URL = "https://www.quinbrook.com/news-insights/rowan-digital-infrastructure-announces-strategic-recapitalization/"
QUINBROOK_HISTORY_URL = "https://www.quinbrook.com/news-insights/quinbrook-expands-rowan-green-data-center-platform/"
MORROW_PAGE_URL = "https://www.co.morrow.or.us/planning/page/june-27-2023-rowan-green-data-llc-pending-action"
MORROW_APPLICATION_URL = "http://www.morrowcountyor.gov/sites/default/files/fileattachments/planning/page/16692/rowan_percheron_data_center_land_use_application_05182023.pdf"


PROJECTS = [
    {
        "code": "CINCO",
        "project_name": "Cinco",
        "provider_card_group": "Cinco",
        "state": "Texas",
        "market": "Medina_County_near_San_Antonio",
        "current_card_capacity_MW": 300,
        "current_card_acres": 440,
        "current_lifecycle": "construction_with_provider_completion_target_2027",
        "current_customer_evidence": "Top_5_US_technology_company_long_term_needs",
        "minimum_local_investment_USD": 900_000_000,
        "provider_url": CINCO_URL,
        "scope_conflict": "Current Rowan card says 440 acres and 300MW. Quinbrook also describes a 1GW power envelope, while a separate Quinbrook page says 220 acres, 300MW near-term plus 400MW secured before 2030. These are not selected or added as one current capacity.",
    },
    {
        "code": "PERCHERON",
        "project_name": "Percheron",
        "provider_card_group": "Percheron",
        "state": "Oregon",
        "market": "Morrow_County_near_Boardman",
        "current_card_capacity_MW": 300,
        "current_card_acres": 275,
        "current_lifecycle": "phased_buildout_targeting_completion_by_2030",
        "current_customer_evidence": "undisclosed",
        "minimum_local_investment_USD": None,
        "provider_url": PERCHERON_URL,
        "scope_conflict": "The current provider card says 275 acres; the 2023 Morrow County application concerns approximately 274 acres. Four OSM building polygons do not establish four operating facilities or current construction state.",
    },
    {
        "code": "TEMPLE",
        "project_name": "Temple_first_300MW_phase",
        "provider_card_group": "Temple",
        "state": "Texas",
        "market": "Temple_and_Bell_County",
        "current_card_capacity_MW": 300,
        "current_card_acres": 700,
        "current_lifecycle": "construction_with_substantial_completion_target_2027",
        "current_customer_evidence": "top_global_technology_company_long_term_customer",
        "minimum_local_investment_USD": 700_000_000,
        "provider_url": TEMPLE_URL,
        "scope_conflict": "The Rowan card and January 2026 release describe a 300MW, roughly 700-acre first campus. Quinbrook separately describes more than 1,350 acres and 1.6GW across the broader Temple region through 2030.",
    },
    {
        "code": "BAUXITE1",
        "project_name": "Bauxite_I",
        "provider_card_group": "Bauxite_1_2_3",
        "state": "Maryland",
        "market": "Frederick_County_Quantum_Loophole_campus",
        "current_card_capacity_MW": None,
        "provider_or_investor_phase_capacity_MW": 231,
        "current_card_group_acres": 375,
        "current_lifecycle": "substantial_completion_July_2025_and_fully_delivered_late_2025_per_Quinbrook",
        "current_customer_evidence": "hyperscale_customer_unnamed",
        "minimum_local_investment_USD": None,
        "provider_url": BAUXITE_URL,
        "phase_financing_USD": 975_000_000,
        "scope_conflict": "The 231MW phase is part of a grouped card showing 600MW while its prose says more than 630MW and Quinbrook gives approximately 625MW or 626MW utility load for all three phases.",
    },
    {
        "code": "BAUXITE2",
        "project_name": "Bauxite_II",
        "provider_card_group": "Bauxite_1_2_3",
        "state": "Maryland",
        "market": "Frederick_County_Quantum_Loophole_campus",
        "current_card_capacity_MW": None,
        "provider_or_investor_phase_capacity_MW": None,
        "current_card_group_acres": 375,
        "current_lifecycle": "construction_or_advancing_toward_2026_delivery",
        "current_customer_evidence": "hyperscale_customer_unnamed",
        "minimum_local_investment_USD": None,
        "provider_url": BAUXITE_URL,
        "phase_financing_USD": 1_200_000_000,
        "scope_conflict": "Bauxite II and III together account for a Quinbrook-reported remaining 395MW; no reviewed primary source allocates that amount between the two phases.",
    },
    {
        "code": "BAUXITE3",
        "project_name": "Bauxite_III",
        "provider_card_group": "Bauxite_1_2_3",
        "state": "Maryland",
        "market": "Frederick_County_Quantum_Loophole_campus",
        "current_card_capacity_MW": None,
        "provider_or_investor_phase_capacity_MW": None,
        "current_card_group_acres": 375,
        "current_lifecycle": "construction_or_advancing_toward_2027_delivery",
        "current_customer_evidence": "hyperscale_customer_unnamed",
        "minimum_local_investment_USD": None,
        "provider_url": BAUXITE_URL,
        "phase_financing_USD": 925_000_000,
        "scope_conflict": "Bauxite II and III together account for a Quinbrook-reported remaining 395MW; no reviewed primary source allocates that amount between the two phases.",
    },
]


OSM_CROSSWALK = {
    "osm_way_1501824326": "PERCHERON",
    "osm_way_1501824327": "PERCHERON",
    "osm_way_1501824328": "PERCHERON",
    "osm_way_1501824329": "PERCHERON",
}


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CROSSWALK:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CROSSWALK)
    return rows


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for project in PROJECTS:
        records.append({
            "id": f"rowan_provider_project_{project['code'].lower()}",
            "object_type": "ProviderProjectIdentifierEvidence",
            "developer": "Rowan_Digital_Infrastructure",
            "legacy_legal_or_operator_name": "Rowan_Green_Data_LLC",
            "country": "United_States",
            **project,
            "count_boundary": "A provider card, project phase, data-hall pod, building, campus, regional power envelope and operating facility are different scopes. Six project identifiers are not six confirmed operating buildings.",
            "capacity_boundary": "Utility load, contracted power, card capacity, development capacity, leased capacity, operational capacity, live IT load and actual draw are different denominators.",
            "accessed_on": accessed_on,
        })
    for osm_id, row in osm_rows.items():
        records.append({
            "id": f"rowan_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityEvidence",
            "developer": "Rowan_Digital_Infrastructure",
            "OSM_ref": osm_id,
            "matched_provider_code": OSM_CROSSWALK[osm_id],
            "match_classification": "exact_Percheron_name_operator_and_owner_family_match_inside_provider_campus_scope",
            "raw_operator": row.get("operator"),
            "raw_owner": row.get("owner"),
            "raw_name": row.get("name"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "OSM_footprint_area_m2": row.get("footprint_area_m2"),
            "OSM_lifecycle": row.get("tags", {}).get("construction") or row.get("tags", {}).get("proposed") or "not_tagged",
            "source_url": row["source_url"],
            "count_boundary": "Four OSM polygons are retained as four mapped geometries inside one Percheron campus. They do not prove four provider facilities, title, construction completion, operation, floor area, IT load, equipment or financial contribution.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 10
    assert sum(row["object_type"] == "ProviderProjectIdentifierEvidence" for row in records) == 6
    assert sum(row["object_type"] == "OSMFacilityEvidence" for row in records) == 4
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    projects = [row for row in records if row["object_type"] == "ProviderProjectIdentifierEvidence"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityEvidence"]
    return {
        "id": "rowan_digital_infrastructure_summary_2026_07_19",
        "developer": "Rowan Digital Infrastructure",
        "legacy_legal_or_operator_name": "Rowan Green Data LLC",
        "accessed_on": accessed_on,
        "current_roster_and_capacity_reconciliation": {
            "current_portfolio_cards": 4,
            "current_project_identifiers": len(projects),
            "active_sites_provider_metric": 6,
            "states_provider_metric": 3,
            "acreage_provider_metric": 1790,
            "under_development_GW_provider_metric": 1.6,
            "four_card_capacity_MW_checksum_using_600MW_Bauxite_label": 1500,
            "homepage": {"leased_GW": 1.2, "operational_MW": 230, "contracted_power_GW": 1.6, "pipeline_GW": 6},
            "June_2026_brand_release": {"employees": "more_than_200", "under_construction_GW": "more_than_2", "states": 3, "construction_financing_USD": "more_than_7_billion"},
            "Quinbrook_platform": {"sites_across_US": "20_plus", "states": 20, "capacity_under_evaluation_or_active_development_GW": "5_to_6_plus"},
            "boundary": "The four cards, six named projects, six active-site metric, 1.5GW card checksum, 1.6GW development or contracted metrics, 1.2GW leased, 230MW operational and 6GW pipeline are retained separately. None is substituted for live utilized IT load.",
        },
        "project_scope_conflicts": {
            "Bauxite": {"current_card_label_MW": 600, "current_card_prose_MW": "more_than_630", "Quinbrook_total_MW": "approximately_625_or_626_utility_load", "Bauxite_I_delivered_MW": 231, "Bauxite_II_and_III_remaining_MW": 395, "broader_planned_utility_load_GW": "more_than_1"},
            "Cinco": {"current_Rowan_card": "440_acres_300MW_completion_2027", "Quinbrook_current_portfolio": "440_acres_1GW_power_between_2026_and_2030_with_Cinco_1_300MW", "separate_Quinbrook_project_page": "220_acres_300MW_near_term_plus_400MW_secured_before_2030"},
            "Temple": {"first_phase": "roughly_700_acres_300MW", "broader_region": "more_than_1350_acres_and_1_6GW_through_2030"},
            "Percheron": {"provider_acres": 275, "county_application_acres": "approximately_274", "provider_capacity_MW": 300, "completion_target": 2030},
            "boundary": "Phase, card, campus, regional land-control, utility-load and future-expansion measures are not added as a current operating fleet.",
        },
        "lifecycle_boundary": {
            "Bauxite_I": "fully_delivered_late_2025_per_Quinbrook",
            "Bauxite_II": "broke_ground_February_2025_and_advancing_toward_2026_delivery",
            "Bauxite_III": "broke_ground_August_2025_and_advancing_toward_2027_delivery",
            "Cinco": "under_construction_with_provider_2027_completion_and_conflicting_Quinbrook_late_2026_first_phase_delivery",
            "Temple": "under_construction_with_2027_operations_or_substantial_completion_target",
            "Percheron": "phased_buildout_targeting_2030_with_no_current_provider_operational_allocation",
            "boundary": "Delivery, substantial completion, construction start, target operation and the aggregate 230MW operational headline are different states. The 230MW headline is not silently assigned to Bauxite I despite numerical proximity.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "Rowan_Green_Data_operator_tagged_objects": sum(row["raw_operator"] == "Rowan Green Data LLC" for row in osm),
            "Percheron_geometry_objects": len(osm),
            "footprint_area_m2_sum_not_floor_area": sum(row["OSM_footprint_area_m2"] or 0 for row in osm),
            "raw_owner_label": "Rowan Digital Infrastructure Pty Ltd",
            "lifecycle_tags": "absent",
            "boundary": "The four similar approximately 23,335-square-metre polygons are mapped building geometries within one provider campus. They are not a current building count, gross floor area, legal-title record or operating-state proof.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "Percheron_2023_conceptual_power_water_and_equipment_boundary": {
            "electrical": {"adjacent_existing_transmission_kV": 230, "provider": "Pacific_Power", "proposed_new_transmission_kV": 230, "distribution_kV": 34.5, "onsite_substations": "conceptual_component", "backup_generators": "onsite_systems_sufficient_for_reliability_without_count_rating_fuel_or_topology"},
            "nearby_Carty_context_not_dedicated_supply": {"PGE_combined_cycle_generation_MW": 450, "switchyard_and_substation": True, "distance_from_project_line_route_miles": 1.6},
            "water_and_cooling": {"industrial_process_and_cooling_water_gallons_per_year": "20_to_60_million", "black_and_grey_water_gallons_per_day": "10000_to_15000", "initial_exempt_potable_well_gallons_per_day": "up_to_5000", "industrial_wastewater": "recycle_onsite_then_treat_or_manage_in_retention_or_evaporation_ponds", "cooling_towers": "mentioned_as_possible_noise_source_not_as_built_inventory"},
            "land_and_layout": {"parcel_acres": 274, "estimated_permanent_project_footprint_acres": 190, "multiple_data_warehouse_buildings": True, "specific_number_and_size": "explicitly_variable_in_application"},
            "boundary": "This is a May 2023 land-use application and conceptual example layout, not an as-built or currently commissioned bill of materials. It does not establish current generator, transformer, UPS, battery, switchgear, chiller, cooling-tower or CDU counts and ratings.",
        },
        "power_cooling_sustainability_and_equipment_boundary": {
            "Bauxite_I": {"energy_efficiency_increase_percent": 17, "embodied_carbon_reduction_percent": 23, "trees_planted_or_preserved_acres": 28, "measurement_baselines_and_current_site_metering": "undisclosed"},
            "Cinco": {"water_offset_percent": 250, "measurement_period_and_operational_WUE_bridge": "not_a_site_WUE_or_actual_consumption_disclosure"},
            "Temple": {"construction_waste_recycling_target_percent": "more_than_85", "utility": "Oncor"},
            "portfolio": {"substation_and_transmission_integration": "provider_capability", "high_density_support": "provider_capability", "renewable_pathways": "where_appropriate"},
            "complete_per_site_grid_transformer_switchgear_busway_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_test_age_and_remaining_life": "undisclosed_or_incomplete",
            "measured_site_PUE_WUE_energy_water_emissions_hourly_renewable_matching_and_live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "Relative improvements, offsets, targets and design capability do not establish current physical equipment, efficiency, actual load, water use or remaining life.",
        },
        "AI_GPU_boundary": {
            "workload_evidence": "Bauxite_marketed_for_cloud_and_AI_and_Cinco_or_Temple_for_top_technology_customers",
            "platform_evidence": "Quinbrook_describes_AI_boom_and_hyperscale_AI_cloud_customer_demand",
            "exact_current_Rowan_customer_or_partner_GPU_accelerator_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "Cloud, AI, hyperscale customers and high-density engineering describe demand and facility capability, not Rowan-owned hardware or an installed accelerator count. No GPU total is inferred.",
        },
        "ownership_financing_and_investability_boundary": {
            "formation_and_control_history": {"founded": "November_2020", "initial_JV": "Quinbrook_and_Birch_Infrastructure", "January_2023": "wholly_owned_by_Quinbrook", "August_2024": "UPP_co_investment_terms_undisclosed", "April_2026": "Blackstone_affiliated_funds_acquired_significant_minority_terms_undisclosed"},
            "project_debt_not_revenue": {"Bauxite_I_USD": 975_000_000, "Bauxite_II_USD": 1_200_000_000, "Bauxite_III_USD": 925_000_000, "Bauxite_total_USD": "more_than_3_1_billion", "Cinco_USD": 550_000_000, "Temple_USD": "nearly_3_billion", "Green_Finance_Framework_three_projects_USD": 4_400_000_000, "June_2026_portfolio_construction_financing_USD": "more_than_7_billion"},
            "corporate_credit_facility_USD": 300_000_000,
            "current_sustainability_page_conflict": "1_4_billion_financed_through_Green_Loan_Framework_versus_May_2026_release_4_4_billion_under_Green_Finance_Framework",
            "standalone_audited_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_debt_assets_customer_concentration_utilization_and_ROIC": "not_publicly_disclosed_in_reviewed_primary_sources",
            "direct_public_equity_security": "unavailable",
            "indirect_listed_exposure": "Blackstone_parent_is_public_but_the_stake_is_fund_affiliated_significant_minority_with_undisclosed_amount_and_Rowan_attribution",
            "boundary": "Construction debt, corporate credit, project investment, fund stakes and cumulative financing are not revenue, profit, enterprise value, equity value, spent capex or unrestricted cash. Exact current ownership percentages and consolidation are undisclosed.",
        },
        "named_parties_without_revenue_attribution": {
            "equity_or_platform_capital": ["Quinbrook", "UPP", "Blackstone_affiliated_funds"],
            "utilities": ["AEP_for_Cinco", "Oncor_for_Temple", "Pacific_Power_for_Percheron"],
            "Bauxite_III_lenders": ["SMBC", "MUFG", "Mizuho", "Societe_Generale"],
            "corporate_credit_parties": ["Apterra", "Investec", "Standard_Chartered", "Celtic_Bank"],
            "customers": ["unnamed_Top_5_US_technology_company_at_Cinco", "unnamed_top_global_technology_company_at_Temple", "unnamed_hyperscalers_at_Bauxite"],
            "boundary": "A named relationship does not establish a material equipment award, contract value, attributable revenue, operating profit, margin or repeat business.",
        },
        "outlook": {
            "positive_signals": ["Bauxite_I_delivery_and_230MW_scale_proximity", "1_2GW_leased_and_1_6GW_contracted_platform_headlines", "multiple_top_technology_customer_relationships", "more_than_7_billion_USD_construction_financing", "Blackstone_and_UPP_capital_support", "power_first_site_strategy", "six_GW_pipeline"],
            "conversion_tests": ["reconcile_card_project_active_site_and_platform_capacity_denominators", "allocate_230MW_operational_and_1_2GW_leased_to_assets", "deliver_Bauxite_II_III_Cinco_and_Temple_to_customer_acceptance_and_billing", "publish_current_cap_table_and_project_ownership", "bridge_project_debt_to_revenue_cash_flow_and_returns", "publish_as_built_equipment_and_measured_efficiency", "identify_installed_accelerators_and_live_liquid_cooled_load"],
            "risks": ["large_debt_funded_construction_program", "customer_concentration", "power_and_interconnection_timing", "project_and_region_scope_conflicts", "private_financial_opacity", "unclear_ownership_percentages", "no_site_level_utilization_or_returns", "no_GPU_inventory_or_AI_revenue_bridge"],
            "analytical_view": "Rowan has moved beyond a paper pipeline because Bauxite I is delivered and the platform reports 230MW operational. The next investment test is whether more than 7 billion dollars of financing converts into accepted, leased, utilized and cash-generating capacity without leverage, power or customer concentration eroding returns. Direct investment is unavailable; listed read-through remains conditional on disclosed contracts and revenue materiality.",
        },
        "records": records,
        "sources": [HOME_URL, PORTFOLIO_URL, CINCO_URL, PERCHERON_URL, TEMPLE_URL, BAUXITE_URL, SITE_SELECTION_URL, ENERGY_URL, SUSTAINABILITY_URL, BAUXITE_APPROVAL_URL, CINCO_GROUNDBREAKING_URL, TEMPLE_CONSTRUCTION_URL, FINANCING_2025_URL, FINANCING_2026_URL, BRAND_SCALE_URL, QUINBROOK_ROWAN_URL, QUINBROOK_BAUXITE_URL, QUINBROOK_CINCO_URL, QUINBROOK_TEMPLE_URL, QUINBROOK_UPP_URL, QUINBROOK_RECAP_URL, QUINBROOK_HISTORY_URL, MORROW_PAGE_URL, MORROW_APPLICATION_URL],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()

    osm_rows = load_osm(args.osm)
    records = build_records(osm_rows, args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "rowan_digital_infrastructure_registry.jsonl"
    summary_path = args.output_dir / "rowan_digital_infrastructure_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "provider_project_identifiers": 6,
        "OSM_objects": 4,
        "OSM_footprint_area_m2_sum": sum(row.get("footprint_area_m2") or 0 for row in osm_rows.values()),
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
