#!/usr/bin/env python3
"""Build a scope-preserving PowerHouse Data Centers project and OSM registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


HOME_URL = "https://www.powerhousedata.com/"
SITEMAP_URL = "https://www.powerhousedata.com/sitemap.xml"
APPROACH_URL = "https://www.powerhousedata.com/approach"
SUSTAINABILITY_URL = "https://www.powerhousedata.com/sustainability"
AREP_HOME_URL = "https://www.americanrepartners.com/"
AREP_FUND_IV_URL = "https://www.americanrepartners.com/news/arep-fund-iv-oversubscribed-at-309m"
HARRISON_JV_URL = "https://www.powerhousedata.com/news/arep-and-harrison-street-joint-venture-commits-1-billion-to-develop-2-1-million-square-feet-of-powered-shell-data-centers-across-northern-virginias-data-center-alley"
BLUE_OWL_URL = "https://www.powerhousedata.com/news/blue-owl-chirisa-technology-parks-and-powerhouse-data-centers-announce-next-phase-of-5-billion-joint-venture-development-partnership"
CTP_DIGITAL_DRIVE_URL = "https://www.powerhousedata.com/news/chirisa-powerhouse-launching-hyperscale-campus-in-chesterfield"
ARCOLA_LEASE_URL = "https://www.powerhousedata.com/news/powerhouse-lease-arcola"
CHARLOTTE_JV_URL = "https://www.powerhousedata.com/news/town-lane-and-powerhouse-data-centers-joint-venture-acquires-future-data-center-land-site-in-charlotte-nc-2"
LOUISVILLE_JV_URL = "https://www.powerhousedata.com/news/powerhouse-data-centers-and-poe-companies-partner-to-develop-kentuckys-first-hyperscale-data-center-campus"
GRAND_PRAIRIE_URL = "https://www.powerhousedata.com/news/powerhouse-and-provident-rewrite-the-data-center-playbook-with-new-texas-hyperscale-campus"
PAX_URL = "https://www.powerhousedata.com/news/pennsylvania-data-center-partners-and-powerhouse-data-centers-launch-joint-venture-to-build-next-gen-1-35-gw-hyperscale-data-center-campus-in-carlisle-pennsylvania"
QUANTUM_URL = "https://www.powerhousedata.com/news/20mw-data-center-planned-at-areps-quantum-park-in-ashburn-virginia"
ABX_LEASE_URL = "https://www.powerhousedata.com/news/powerhouse-data-centers-announces-lease-agreement-with-cyrusone-for-abx-1-data-center-powered-shell"
RENO_URL = "https://www.powerhousedata.com/news/powerhouse-data-centers-plans-new-nova-campus-in-spotsylvania-moves-nationally-into-reno-nv-2"


def card(code: str, name: str, slug: str, city: str, state: str, **extra: object) -> dict:
    return {
        "code": code,
        "project_name": name,
        "url": f"https://www.powerhousedata.com/data-center/{slug}",
        "city_or_market": city,
        "state": state,
        **extra,
    }


PROJECT_CARDS = [
    card("ABX1", "PowerHouse ABX-1", "powerhouse-abx-1", "Ashburn", "Virginia", acreage=10, developable_sq_ft=265850, maximum_buildings=1, maximum_stories=2, max_utility_power_MW=60, delivery="October_2023", lifecycle="delivered_October_2023_and_current_card_says_sold_Q4_2024", program_or_partner="Harrison_Street_JV_with_30_year_CyrusOne_whole_building_lease_announced_2023", address_evidence="official_material_conflict_21529_versus_21629_Beaumeade_Circle"),
    card("PAC", "PowerHouse Pacific", "powerhouse-pacific", "Ashburn", "Virginia", acreage=43, developable_sq_ft=1131350, maximum_buildings=3, maximum_stories=3, max_utility_power_MW=265, delivery="Q3_2026_to_Q2_2027", power_delivery="Q3_2026", lifecycle="development_current_page_delivery_window_in_progress", program_or_partner="initial_Northern_Virginia_Harrison_Street_JV_scope"),
    card("ARC", "PowerHouse Arcola", "powerhouse-arcola", "Arcola", "Virginia", acreage=30, developable_sq_ft=615000, maximum_buildings=2, maximum_stories=2, max_utility_power_MW=120, delivery="Q4_2026_to_Q1_2027", power_delivery="Q3_2027", lifecycle="development_with_long_term_hyperscale_lease_announced_January_2026", program_or_partner="initial_2022_Harrison_Street_program_but_2026_release_says_initial_development_funded_by_AREP_Strategic_Opportunity_Fund_III", current_release_acreage=37, acreage_conflict="current_project_card_30_acres_versus_2026_release_37_acres"),
    card("PH95", "PowerHouse 95", "powerhouse-95", "Spotsylvania_County", "Virginia", acreage=227, developable_sq_ft=3600000, maximum_buildings=12, maximum_stories=2, max_utility_power_MW=900, delivery="Q3_2026", power_delivery="Q3_2027", lifecycle="development_with_delivery_and_power_timing_conflict_on_current_card", program_or_partner="Harrison_Street_JV", dated_release_boundary="older_145_acre_800MW_eight_building_3_5m_sq_ft_scope_not_substituted_for_current_card"),
    card("IRV", "PowerHouse Irving", "powerhouse-irving", "Irving_Las_Colinas", "Texas", acreage=50, developable_sq_ft=946200, maximum_buildings=3, maximum_stories=3, max_utility_power_MW=201, delivery="Q1_2026", power_delivery="Q1_2026", lifecycle="current_card_retains_passed_delivery_and_power_targets_without_current_commissioning_confirmation", program_or_partner="Harrison_Street_JV", address_evidence="111_Customer_Way_Irving_Texas"),
    card("CTP23", "CTP-02 and CTP-03", "ctp-2", "Chesterfield_County", "Virginia", acreage=42, developable_sq_ft=None, maximum_buildings=2, maximum_stories=None, max_utility_power_MW=120, delivery="Q1_2027", power_delivery="Q1_2027", lifecycle="construction_build_to_suit_fully_leased_per_current_card", program_or_partner="Chirisa_Technology_Parks_and_Blue_Owl_program_with_CoreWeave_as_initial_customer_boundary"),
    card("DD", "1600 Digital Drive", "digital-drive", "Chesterfield_County", "Virginia", acreage=100, developable_sq_ft=695000, maximum_buildings=5, maximum_stories=1, max_utility_power_MW=300, power_qualifier="plus", delivery="Q3_2027", power_delivery="Q3_2027", lifecycle="development", program_or_partner="Chirisa_Technology_Parks_and_PowerHouse_JV", dated_release_area="more_than_600000_sq_ft", dated_release_completion="first_facility_2026_and_full_campus_2028"),
    card("CLT", "PowerHouse Charlotte", "powerhouse-charlotte", "Charlotte", "North_Carolina", acreage=122, developable_sq_ft=1500000, maximum_buildings=5, maximum_stories=2, max_utility_power_MW=300, future_utility_power_MW=400, delivery="Q2_2027", power_delivery="Q2_2027", lifecycle="development", program_or_partner="Town_Lane_JV", transaction_release_sq_ft=2500000, transaction_release_power_MW=300, transaction_release_potential_power_MW=500, disclosure_conflict="current_card_1_5m_sq_ft_and_400MW_future_versus_2024_release_2_5m_sq_ft_and_500MW_potential"),
    card("LOU", "PowerHouse Louisville", "ph-louisville", "Louisville", "Kentucky", acreage=154, developable_sq_ft=1800000, maximum_buildings=6, maximum_stories=None, max_utility_power_MW=525, delivery="Q4_2026", power_delivery="Q4_2026", lifecycle="development", program_or_partner="Poe_Companies_JV", utility="Louisville_Gas_and_Electric_PPL_Corporation", staged_power_MW={"first_building": 130, "initial_secured": 335, "near_term_expansion": 402, "current_card_max_utility": 525}, staged_power_boundary="provider_homepage_rollup_402MW_and_current_card_525MW_use_different_stages"),
    card("GP", "PowerHouse Grand Prairie", "powerhouse-grand-prairie", "Grand_Prairie_or_northern_Ellis_County", "Texas", acreage=810, developable_sq_ft=8500000, maximum_buildings=28, maximum_stories=2, max_utility_power_MW=1800, delivery="Q1_2027", power_delivery="Q4_2026", lifecycle="development", program_or_partner="Provident_Data_Centers_JV", release_acreage=768, first_ERCOT_approved_tranche_MW=500, disclosure_boundary="current_card_810_acres_and_1_8GW_switchyard_envelope_versus_release_768_acres_and_first_500MW_approved_tranche"),
    card("PAX1", "PAX-1", "pax-1", "Carlisle", "Pennsylvania", acreage=693, developable_sq_ft=4200000, maximum_buildings=18, maximum_stories=2, max_utility_power_MW=1350, future_utility_power_MW=1800, delivery="phase_1_Q2_2027", power_delivery="Q2_2027", lifecycle="development_2025_to_2031", program_or_partner="Pennsylvania_Data_Center_Partners_JV", announced_project_investment_USD=15000000000, near_term_power_delivery_MW=300, investment_boundary="announced_three_campus_project_cost_not_PowerHouse_revenue_enterprise_value_committed_equity_or_spent_capex"),
    card("HOB", "PowerHouse Hobart", "powerhouse-hobart", "Hobart", "Indiana", acreage=170, developable_sq_ft=1890000, maximum_buildings=6, maximum_stories=2, max_utility_power_MW=450, delivery="Q2_2027", power_delivery="Q2_2027", lifecycle="development_with_current_card_timeline_conflict_2025_to_2026_versus_construction_2027_to_2030", program_or_partner="not_disclosed_on_current_card"),
    card("RENO", "PowerHouse Reno", "powerhouse-reno", "Tahoe_Reno_Industrial_Center_Storey_County", "Nevada", acreage=49, developable_sq_ft=900000, maximum_buildings=3, maximum_stories=2, max_utility_power_MW=200, delivery="April_2026", power_delivery="Q4_2025", lifecycle="current_card_retains_passed_delivery_and_power_targets_without_current_commissioning_confirmation", program_or_partner="Harrison_Street_JV", address_evidence="junction_of_Britain_Drive_and_Waltham_Way", dated_bridging_power_MW=65, power_boundary="current_card_200MW_envelope_versus_dated_more_than_65MW_bridging_power"),
]


MARKET_ONLY = [
    {
        "code": "QC",
        "project_name": "PowerHouse QC or Quantum Connect",
        "city_or_market": "Ashburn",
        "state": "Virginia",
        "current_homepage_evidence": "QC_is_named_inside_PH_Ashburn_515MW_rollup_without_a_current_project_card",
        "detailed_project_evidence": "Quantum_Connect_at_22001_Loudoun_County_Parkway_has_20MW_total_with_13MW_target_Q4_2026_and_7MW_first_half_2028",
        "maximum_rack_density_kW": 30,
        "lifecycle": "planned",
        "boundary": "QC, Quantum Park and the 20MW Quantum Connect facility may use campus, building and service scopes. The 70MW residual between the three Ashburn cards and the 515MW market rollup is not silently assigned to QC.",
        "url": QUANTUM_URL,
    },
    {
        "code": "JOL",
        "project_name": "PowerHouse Joliet",
        "city_or_market": "Joliet",
        "state": "Illinois",
        "current_homepage_evidence": "current_homepage_market_rollup_1_8GW",
        "lifecycle": "underway_or_planning_headline_without_current_project_card",
        "boundary": "No current sitemap project card establishes acreage, address, buildings, area, delivery, grid stage, customer or exact asset ownership. The 1.8GW label is not current IT load.",
        "url": HOME_URL,
    },
]


OSM_CROSSWALK = {
    "osm_way_800436891": ("CTP23", "name_only_CTP03_construction_land_or_campus_polygon_without_operator_tag"),
    "osm_way_1085712184": ("CTP23", "PowerHouse_operator_tagged_unnamed_component_inside_CTP_cluster"),
    "osm_way_1188715508": ("ABX1", "exact_name_and_provider_website_match"),
    "osm_way_1449347339": ("CTP23", "PowerHouse_operator_tagged_CTP02_named_building_geometry"),
    "osm_way_1493522242": ("CTP23", "PowerHouse_operator_tagged_CTP02_named_construction_geometry"),
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
    for row in PROJECT_CARDS:
        records.append({
            "id": f"powerhouse_provider_project_{row['code'].lower()}",
            "object_type": "ProviderProjectCardEvidence",
            "developer": "PowerHouse_Data_Centers",
            "parent": "American_Real_Estate_Partners",
            "country": "United_States",
            **row,
            "count_boundary": "A project card, building maximum, powered shell, campus, market, JV asset, sold asset and operating tenant facility are different scopes. Maximum buildings are not counted as current operating data centers.",
            "capacity_boundary": "Maximum utility power, future power, approved tranche, bridging power, critical capacity and live IT load are different denominators. No card value is treated as energized, accepted, sold, billed or utilized IT load without evidence.",
            "accessed_on": accessed_on,
        })
    for row in MARKET_ONLY:
        records.append({
            "id": f"powerhouse_provider_market_only_{row['code'].lower()}",
            "object_type": "ProviderMarketOnlyEvidence",
            "developer": "PowerHouse_Data_Centers",
            "parent": "American_Real_Estate_Partners",
            "country": "United_States",
            **row,
            "accessed_on": accessed_on,
        })
    for osm_id, row in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"powerhouse_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityEvidence",
            "developer": "PowerHouse_Data_Centers",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_operator": row.get("operator"),
            "raw_name": row.get("name"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "OSM_footprint_area_m2": row.get("footprint_area_m2"),
            "OSM_opening_date": row.get("tags", {}).get("opening_date"),
            "source_url": row["source_url"],
            "count_boundary": "The OSM object is a location and geometry crosswalk, not proof of title, operating state, building role, gross floor area, white space, MW, GPU inventory or financial contribution. Four Chesterfield objects remain one provider project-card scope covering two named buildings, not four data centers.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 20
    assert sum(row["object_type"] == "ProviderProjectCardEvidence" for row in records) == 13
    assert sum(row["object_type"] == "ProviderMarketOnlyEvidence" for row in records) == 2
    assert sum(row["object_type"] == "OSMFacilityEvidence" for row in records) == 5
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    cards = [row for row in records if row["object_type"] == "ProviderProjectCardEvidence"]
    market_only = [row for row in records if row["object_type"] == "ProviderMarketOnlyEvidence"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityEvidence"]
    return {
        "id": "powerhouse_data_centers_project_summary_2026_07_19",
        "developer": "PowerHouse Data Centers",
        "parent": "American Real Estate Partners",
        "accessed_on": accessed_on,
        "current_roster_and_headline_reconciliation": {
            "current_sitemap_project_cards": len(cards),
            "project_identifiers_inside_cards": 14,
            "current_homepage_labels_without_project_cards": [row["code"] for row in market_only],
            "reconstructed_project_or_location_identifiers": 16,
            "homepage_facilities_underway_planning_or_completed_sq_ft": 32200000,
            "homepage_data_centers_underway_or_planning": 118,
            "homepage_power_GW": "more_than_8_1",
            "homepage_major_US_markets": 9,
            "visible_homepage_location_rollups": 11,
            "numeric_card_developable_area_sq_ft_checksum_excluding_CTP23": sum(row["developable_sq_ft"] or 0 for row in cards),
            "card_maximum_building_checksum": sum(row["maximum_buildings"] or 0 for row in cards),
            "card_maximum_utility_power_MW_checksum": sum(row["max_utility_power_MW"] for row in cards),
            "card_acreage_checksum": sum(row["acreage"] for row in cards),
            "boundary": "The live homepage headline, visible market list, sitemap cards, project identifiers, maximum buildings, developable area and maximum utility power do not reconcile to one denominator. They mix completed, sold, leased, construction and long-dated development states and are not an operating-fleet total.",
        },
        "lifecycle_boundary": {
            "delivered_and_currently_marked_sold": ["ABX1"],
            "fully_leased_development_cards": ["CTP23"],
            "lease_announced_development_cards": ["ARC"],
            "cards_with_passed_delivery_or_power_targets_but_no_current_commissioning_confirmation": ["IRV", "RENO"],
            "other_development_or_planning_cards": [row["code"] for row in cards if row["code"] not in {"ABX1", "CTP23", "ARC", "IRV", "RENO"}],
            "boundary": "ABX-1 is the only card explicitly complete and sold. A past target date, lease, full lease, construction start, utility approval or current marketing card does not establish energized, tenant-accepted or operating status.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "PowerHouse_operator_tagged_objects": sum(row["raw_operator"] == "PowerHouse" for row in osm),
            "name_only_object": "osm_way_800436891_CTP03",
            "ABX1_objects": 1,
            "CTP_cluster_objects": 4,
            "footprint_area_m2_sum_not_floor_area": sum(row["OSM_footprint_area_m2"] or 0 for row in osm),
            "boundary": "The very large CTP-03 construction polygon appears to include land or campus scope. Two CTP-02 geometries and an unnamed component are not counted as additional provider projects. OSM footprint is not provider developable area or floor area.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "power_cooling_and_equipment_boundary": {
            "portfolio_baseline": {
                "minimum_redundancy": "N_plus_1_design_parameter",
                "PUE_design_target": "1_2_to_1_3",
                "baseline_cooling": "air_cooled_rooftop_chillers_with_optional_evaporative_component",
                "full_fit_out_partner": "Integra_Mission_Critical_for_power_cooling_and_IT_modules_procurement_and_commissioning",
            },
            "site_specific": {
                "Arcola": "onsite_substations_Tier_III_plus_or_IV_ready_and_high_density_GPU_liquid_cooled_environment_support",
                "CTP23": "initial_120MW_critical_program_and_CTP_direct_on_chip_liquid_cooling_marketed_as_almost_twice_as_energy_efficient_as_air_cooling",
                "Louisville": "new_LGE_switch_station_and_dedicated_onsite_substation_with_water_infrastructure_access",
                "Grand_Prairie": "1_8GW_switchyard_envelope_with_first_500MW_ERCOT_approved_tranche",
                "PAX1": "three_450MW_substations_and_PPL_Electric_transmission_connection_plan",
                "Reno": "water_reuse_design_and_claimed_50_percent_lighting_and_30_percent_cooling_energy_reduction",
            },
            "complete_per_site_grid_transformer_switchgear_busway_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_test_age_and_remaining_life": "undisclosed_or_incomplete",
            "measured_site_PUE_WUE_energy_water_emissions_and_live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "Design targets, readiness, grid approvals, maximum utility capacity and comparative cooling claims do not establish as-built equipment, current condition, measured efficiency, actual energy or water use, or live IT load.",
        },
        "AI_GPU_boundary": {
            "homepage_capability": "HPC_high_density_power_immersive_cooling_OCP_ready_and_DGX_ready_environments",
            "CoreWeave_boundary": "initial_120MW_CTP_program_is_for_CoreWeave_but_exact_building_allocation_and_physical_accelerator_inventory_are_not_disclosed",
            "exact_current_PowerHouse_AREP_JV_tenant_or_partner_GPU_accelerator_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "DGX-ready, OCP-ready, AI-ready, GPU-support and a named AI cloud tenant describe capability and commercial demand, not PowerHouse-owned GPUs or an installed unit count. No GPU total is inferred.",
        },
        "ownership_financial_and_investability_boundary": {
            "PowerHouse": "fully_owned_and_operated_subsidiary_or_division_of_private_AREP_per_provider_material",
            "AREP_homepage": {"acquired_sq_ft": 38000000, "acquisitions_to_date_USD": "21_billion_plus"},
            "AREP_Fund_IV": {"equity_commitments_USD": 309000000, "target_allocation_to_PowerHouse_percent": 80},
            "selected_non_additive_program_values_USD": {"Harrison_Street_JV_commitment": 1000000000, "Blue_Owl_CTP_PowerHouse_capacity_to_deploy": 5000000000, "Blue_Owl_second_tranche_transaction": 750000000, "PAX_three_campus_project": 15000000000},
            "PowerHouse_or_AREP_audited_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_debt_assets_customer_concentration_utilization_and_ROIC": "not_publicly_disclosed_in_reviewed_primary_sources",
            "direct_public_equity_security": "unavailable_for_PowerHouse_and_AREP",
            "boundary": "Fund commitments, acquisitions to date, JV capacity, transaction tranches and project-cost announcements are not PowerHouse revenue, profit, enterprise value, available cash, spent capex or owned asset value. Ownership percentages and accounting consolidation vary by project and remain incomplete.",
        },
        "named_parties_without_revenue_attribution": {
            "capital_and_development": ["Harrison_Street", "Blue_Owl_Capital", "Chirisa_Technology_Parks", "Town_Lane", "Poe_Companies", "Provident_Data_Centers", "Pennsylvania_Data_Center_Partners"],
            "customers_or_lessees": ["CyrusOne", "CoreWeave", "undisclosed_Arcola_hyperscaler"],
            "utilities_or_grid": ["Dominion_Energy", "NV_Energy", "Duke_Energy", "Louisville_Gas_and_Electric_PPL", "PPL_Electric", "ERCOT"],
            "design_construction_and_fit_out": ["Integra_Mission_Critical", "DPR_Construction", "Corgan", "kW_Mission_Critical_Engineering", "Rosendin_Electric"],
            "boundary": "Participation in a project does not establish contract value, equipment award, revenue, profit, margin or future repeat business for any named party.",
        },
        "outlook": {
            "positive_signals": ["large_power_secured_or_planned_pipeline", "multiple_institutional_capital_partners", "CoreWeave_and_hyperscale_lease_demand", "AI_HPC_and_liquid_cooling_design_capability", "utility_and_substation_relationships", "national_market_expansion", "PAX_and_Joliet_GW_scale_optionalities"],
            "conversion_tests": ["reconcile_118_8_1GW_32_2m_sq_ft_and_current_cards", "commission_passed_and_near_term_targets", "convert_grid_and_switchyard_envelopes_to_energized_customer_accepted_billed_IT_load", "publish_project_ownership_and_financial_allocation", "publish_measured_efficiency_and_live_liquid_cooled_MW", "identify_installed_accelerators_and_supplier_awards"],
            "risks": ["pipeline_not_operating_capacity", "multi_JV_ownership_and_accounting_complexity", "power_and_transmission_timing", "card_and_press_release_conflicts", "customer_concentration", "construction_financing_and_cost_inflation", "private_financial_opacity", "no_GPU_inventory_or_AI_revenue_bridge"],
            "analytical_view": "PowerHouse is one of the clearest examples of AI demand being translated into land, utility and construction pipelines, including a named CoreWeave program and liquid-cooling design. It is also a private developer whose headline GW and buildings are mostly future envelopes. Investment evidence should follow commissioning, customer acceptance, billed load and supplier awards rather than treating the entire pipeline as operating capacity or revenue.",
        },
        "records": records,
        "sources": [HOME_URL, SITEMAP_URL, APPROACH_URL, SUSTAINABILITY_URL, AREP_HOME_URL, AREP_FUND_IV_URL, HARRISON_JV_URL, BLUE_OWL_URL, CTP_DIGITAL_DRIVE_URL, ARCOLA_LEASE_URL, CHARLOTTE_JV_URL, LOUISVILLE_JV_URL, GRAND_PRAIRIE_URL, PAX_URL, QUANTUM_URL, ABX_LEASE_URL, RENO_URL] + [row["url"] for row in PROJECT_CARDS],
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
    registry_path = args.output_dir / "powerhouse_data_centers_registry.jsonl"
    summary_path = args.output_dir / "powerhouse_data_centers_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "current_project_cards": 13,
        "market_only_labels": 2,
        "OSM_objects": 5,
        "card_max_utility_power_MW_checksum": sum(row["max_utility_power_MW"] for row in PROJECT_CARDS),
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
