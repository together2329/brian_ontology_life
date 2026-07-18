#!/usr/bin/env python3
"""Build a scope-preserving Teraco facility and public-map registry.

Teraco publishes current directory codes, campus-level critical-power totals,
individual-facility milestones, a marketing total that includes construction,
and Digital Realty transaction metrics with another reporting boundary.  This
builder preserves those scopes and joins the related South African OSM objects
without converting AI or liquid-cooling readiness into GPU inventory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://www.teraco.co.za/"
DIRECTORY = "https://www.teraco.co.za/data-centre-locations/"
JOHANNESBURG = "https://www.teraco.co.za/data-centre-locations/johannesburg/"
CAPE_TOWN = "https://www.teraco.co.za/data-centre-locations/cape-town/"
DURBAN = "https://www.teraco.co.za/data-centre-locations/durban/"
JB3_COMPLETION = "https://www.teraco.co.za/news/teracos-hyper-connected-campus/"
JB4_INITIAL = "https://www.teraco.co.za/news/teraco-completes-jb4-hyperscale-data-centre-expansion-to-bredell-campus/"
JB4_COMPLETION = "https://www.teraco.co.za/news/teraco-completes-significant-jb4-hyperscale-data-centre-expansion-incorporating-new-sustainability-designs/"
JB5_GROUNDBREAKING = "https://www.teraco.co.za/news/teraco-breaks-ground-on-jb5-a-30mw-data-centre-expansion-to-isando-campus/"
JB7_ANNOUNCEMENT = "https://www.teraco.co.za/news/teraco-announces-jb7-and-a-new-r8-billion-syndicated-loan/"
CT2_COMPLETION = "https://www.teraco.co.za/news/teraco-completes-ct2-data-centre-expansion/"
CT1_EXPANSION = "https://www.teraco.co.za/news/teraco-announces-ct1-data-centre-expansion-in-rondebosch-cape-town/"
DB1_COMPLETION = "https://www.teraco.co.za/news/teraco-completes-durban-data-centre-expansion-to-double-existing-facility-capacity/"
SUSTAINABILITY = "https://www.teraco.co.za/about/sustainability/"
CERTIFICATIONS = "https://www.teraco.co.za/about/certifications-and-compliance/"
AI_INFRASTRUCTURE = "https://www.teraco.co.za/platform-teraco/infrastructure-for-artificial-intelligence/"
DLR_TRANSACTION = "https://investor.digitalrealty.com/news-releases/news-release-details/digital-realty-announces-transactions-drive-continued-platform"
DLR_TRANSACTION_DECK = "https://investor.digitalrealty.com/static-files/c48b8fee-1eb8-4830-87b3-6c9d7bdd5396"
DLR_2025_10K = "https://investor.digitalrealty.com/static-files/a444db72-d0c1-45e2-b082-ed6363542a9e"


def facility(
    code: str,
    metro: str,
    campus: str,
    lifecycle: str,
    address: str,
    coordinates: list[float] | None,
    current_metrics: dict,
    engineering: dict | None = None,
    lifecycle_evidence: dict | None = None,
    conflicts: list[str] | None = None,
    sources: list[str] | None = None,
) -> dict:
    regional_page = JOHANNESBURG if metro == "Johannesburg" else CAPE_TOWN if metro == "Cape_Town" else DURBAN
    return {
        "id": f"teraco_{code.lower()}",
        "facility_code": code,
        "country_code": "ZA",
        "metro": metro,
        "campus": campus,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "current_provider_directory_label": code != "JB7",
        "address": address,
        "provider_coordinates_lat_lon": coordinates,
        "current_provider_metrics": current_metrics,
        "engineering_and_equipment_evidence": engineering or {},
        "lifecycle_evidence": lifecycle_evidence or {},
        "publication_conflicts": conflicts or [],
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "AI_liquid_cooling_or_DGX_ready_is_not_GPU_inventory": True,
        "source_urls": list(dict.fromkeys([DIRECTORY, regional_page, *(sources or [])])),
    }


FACILITIES = [
    facility(
        "JB1", "Johannesburg", "Isando", "operating_two_building_facility_code",
        "5 Brewery Street, Isando, Johannesburg", [-26.138, 28.19802],
        {"shared_Isando_campus_white_space_sqm": 32000, "shared_Isando_campus_critical_IT_mw": 70, "individual_JB1_critical_IT_mw": "undisclosed", "physical_buildings": ["JB1_East", "JB1_West"]},
        {"historical_Isando_total_after_JB3_mw": 40, "historical_JB3_individual_mw": 29, "derived_JB1_residual_mw_not_promoted_to_current_fact": 11, "dated_diesel_storage_litres": 210000, "dated_full_load_generator_runtime_hours_minimum": 40},
        conflicts=["Current_70MW_Isando_total_includes_JB1_JB3_JB5_and_is_not_allocated_to_JB1", "11MW_is_only_a_historical_arithmetic_residual_and_not_a_current_provider_JB1_measure"],
        sources=[JB3_COMPLETION, "https://www.teraco.co.za/news/building-africas-biggest-data-centre-in-isando/"],
    ),
    facility(
        "JB2", "Johannesburg", "Bredell", "operating",
        "0A 1st Road, Bredell, Johannesburg", [-26.0751953, 28.2783355],
        {"white_space_sqm": 5400, "critical_IT_mw": 13, "completed": "2017-11", "technical_deployment_space_sqm_more_than": 6000},
        {"utility_power_MVA": 24, "topology": "concurrently_maintainable_with_added_fault_tolerance", "exact_grid_transformer_switchgear_UPS_battery_generator_and_cooling_BOM": "undisclosed"},
        conflicts=["2025_provider_release_rounds_combined_JB2_JB4_to_64MW_while_current_individual_values_13_plus_50_equal_63MW"],
    ),
    facility(
        "JB3", "Johannesburg", "Isando", "operating",
        "14 Kiln Road, Isando, Johannesburg", [-26.136132, 28.199605],
        {"shared_Isando_campus_white_space_sqm": 32000, "shared_Isando_campus_critical_IT_mw": 70, "individual_completion_critical_IT_mw": 29},
        {"building_structure_sqm": 45000, "data_hall_space_sqm": 12000},
        {"completion_date": "2021-08-19"},
        conflicts=["Current_70MW_Isando_total_includes_JB1_JB3_JB5_and_is_not_an_individual_JB3_measure"],
        sources=[JB3_COMPLETION],
    ),
    facility(
        "JB4", "Johannesburg", "Bredell", "operating_expansion_completed_2025_08_12",
        "Birkenhead Street, Bredell, Johannesburg", [-26.0250175, 28.2697322],
        {"white_space_sqm_current_directory": 16000, "critical_IT_mw": 50},
        {"building_structure_sqm": 80000, "utility_power_mw": 80, "data_halls": 14, "release_data_hall_area_sqm": 17000, "expansion_halls": 6, "critical_IT_mw_per_expansion_hall": 5, "liquid_to_liquid_and_direct_to_chip_enabled": True, "cooling": "closed_loop_chilled_water_with_free_air_and_AI_enabled_controls", "ongoing_cooling_water": "zero_as_provider_claim"},
        {"initial_phase_completed": "2022-11-02", "initial_phase_critical_IT_mw": 19, "final_expansion_completed": "2025-08-12", "added_critical_IT_mw": 30},
        conflicts=["Current_directory_16000sqm_white_space_vs_2025_release_17000sqm_data_halls", "Current_JB2_13_plus_JB4_50_equals_63MW_vs_2025_release_Bredell_64MW"],
        sources=[JB4_INITIAL, JB4_COMPLETION],
    ),
    facility(
        "JB5", "Johannesburg", "Isando", "operating_completion_confirmed_without_exact_completion_date_in_reviewed_release",
        "29 Kiln Road, Isando, Johannesburg", [-26.135302, 28.201401],
        {"shared_Isando_campus_white_space_sqm": 32000, "shared_Isando_campus_critical_IT_mw": 70, "individual_critical_IT_mw": 30},
        {"building_structure_sqm": 55000, "utility_power_MVA": 120, "data_halls": 12, "data_hall_sqm_each": 1000, "cooling": "closed_loop_chilled_water_with_100_percent_free_air", "ongoing_cooling_water": "zero_as_provider_design_claim"},
        {"construction_announced": "2022-11-07", "scheduled_completion_in_original_release": 2024, "later_completion_confirmation": "JB4_2025_08_12_release_says_recently_completed", "exact_completion_date": "undisclosed"},
        conflicts=["Current_70MW_Isando_total_includes_JB1_JB3_JB5_and_is_not_an_additional_facility_sum"],
        sources=[JB5_GROUNDBREAKING, JB4_COMPLETION],
    ),
    facility(
        "CT1", "Cape_Town", "Rondebosch", "operating_with_2MW_expansion_under_construction",
        "Great Westerford Building, 240 Main Road, Rondebosch, Cape Town", [-33.9712, 18.4649],
        {"white_space_sqm": 2500, "critical_IT_mw": 3},
        {"expansion_additional_data_hall_sqm": 1000, "expansion_additional_critical_IT_mw": 2, "post_expansion_critical_IT_mw": 5},
        {"first_opened": 2008, "expansion_commenced": "2025-11-12", "expected_completion": "early_2027", "completion_confirmed": False},
        conflicts=["191MW_post_expansion_portfolio_value_is_forward_looking_and_excludes_JB7"],
        sources=[CT1_EXPANSION],
    ),
    facility(
        "CT2", "Cape_Town", "Brackenfell", "operating_expansion_completed_2025_11_10",
        "57 Tiber Road, Brackenfell, Cape Town", [-33.907417, 18.67936],
        {"white_space_sqm": 18000, "critical_IT_mw": 50},
        {"building_structure_sqm": 73000, "utility_power_mw": 90, "data_halls": 16, "expansion_data_halls": 8, "five_mw_halls": 4, "liquid_to_liquid_enabled": True, "cooling": "closed_loop_free_air_with_AI_enhanced_controls", "ongoing_cooling_water": "zero_as_provider_claim"},
        {"expansion_completed": "2025-11-10", "added_critical_IT_mw": 32},
        sources=[CT2_COMPLETION],
    ),
    facility(
        "DB1", "Durban", "Riverhorse_Valley", "operating",
        "Riverhorse Close, Riverhorse Valley, Durban", None,
        {"white_space_sqm": 1500, "current_directory_critical_IT_mw_rounded": 2, "completion_release_critical_IT_mw": 2.2},
        {"building_structure_sqm": 5800, "utility_power_MVA": 4, "racks_more_than": 700},
        conflicts=["Current_directory_rounds_2_2MW_completion_measure_to_2MW"],
        sources=[DB1_COMPLETION],
    ),
    facility(
        "JB7", "Johannesburg", "Isando", "under_construction_not_in_current_facility_directory",
        "Isando Campus, Ekurhuleni, Johannesburg", None,
        {"planned_critical_IT_mw": 40, "current_operating_critical_IT_mw": 0},
        {"planned_building_structure_sqm": 71000, "planned_utility_power_MVA": 68, "planned_data_halls": 8, "planned_data_hall_sqm_each": 1500, "cooling_design": "closed_loop_chilled_water_and_direct_free_air", "planned_liquid_cooling": ["liquid_to_air", "liquid_to_liquid"], "planned_ongoing_cooling_water": "zero_as_provider_design_claim"},
        {"construction_commenced": "2024-11-13_announced", "scheduled_completion": 2026, "completion_confirmed_as_of_2026_07_19": False},
        conflicts=["Homepage_228MW_marketing_total_includes_this_40MW_under_construction_facility"],
        sources=[JB7_ANNOUNCEMENT],
    ),
]


OSM_CROSSWALK = {
    "osm_way_823191092": ("teraco_jb1", "facility_building"),
    "osm_way_823191093": ("teraco_jb1", "facility_building"),
    "osm_way_706815676": ("teraco_jb1", "campus_polygon_with_operator_typo"),
    "osm_way_1109619855": ("teraco_jb3", "facility_building"),
    "osm_way_823111182": ("teraco_jb3", "campus_polygon"),
    "osm_way_1349217287": ("teraco_jb5", "facility_building"),
    "osm_way_1230572491": ("teraco_jb5", "campus_polygon"),
    "osm_way_1116366727": ("teraco_jb2", "facility_building"),
    "osm_way_718213807": ("teraco_jb2", "campus_polygon"),
    "osm_way_1222015736": ("teraco_jb4", "facility_building"),
    "osm_way_1024334708": ("teraco_ct2", "facility_building"),
    "osm_way_823111183": ("teraco_teleport", "satellite_earth_station_not_a_data_center_facility_code"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = [{"object_type": "DataCenterFacilityEvidence", "source_order": order, "operator": "Teraco", "accessed_on": accessed_on, **item} for order, item in enumerate(FACILITIES, 1)]
    assert len(records) == 9
    assert len({row["facility_code"] for row in records}) == 9
    assert sum(row["current_provider_directory_label"] for row in records) == 8
    assert Counter("operating" in row["lifecycle_as_of_2026_07_19"] for row in records) == {True: 8, False: 1}
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, role) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_ref": facility_ref,
            "map_object_role": role,
            "source_url": source["source_url"],
            "boundary": "OSM geometry and labels do not certify title, lifecycle, floor area, IT load, utilization, equipment or GPU inventory.",
        })
    assert len(rows) == 12
    assert sum(row["raw_operator"] == "Teraco" for row in rows) == 7
    assert sum(row["raw_operator"] == "Terao Data Environments" for row in rows) == 1
    assert sum(row["facility_ref"] == "teraco_teleport" for row in rows) == 1
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    return {
        "id": "teraco_official_facility_summary_2026_07_19",
        "object_type": "TeracoPortfolioReconciliation",
        "accessed_on": accessed_on,
        "facility_roster": {
            "current_provider_directory_codes": 8,
            "current_provider_directory_code_list": ["JB1", "JB2", "JB3", "JB4", "JB5", "CT1", "CT2", "DB1"],
            "operating_codes_from_reviewed_sources": 8,
            "under_construction_not_current_directory": ["JB7"],
            "JB1_physical_buildings": ["JB1_East", "JB1_West"],
            "non_data_center_connectivity_asset": ["Teleport"],
            "boundary": "Facility codes, physical buildings, campuses, a satellite earth station and development projects are different granularities.",
        },
        "capacity_reconciliation": {
            "current_homepage_marketing_IT_load_mw": 228,
            "current_homepage_marketing_scope": {"Isando_including_JB7_under_construction": 110, "Bredell": 63, "Cape_Town": 53, "Durban": 2},
            "2025_08_completed_platform_release_critical_power_load_mw": 189,
            "2025_08_release_scope": {"Isando_JB1_JB3_JB5": 70, "Bredell_JB2_JB4": 64, "Cape_Town_CT1_CT2": 53, "Durban_DB1": 2},
            "current_individual_directory_arithmetic_mw": 188,
            "current_individual_directory_arithmetic": {"Isando_shared": 70, "JB2": 13, "JB4": 50, "CT1": 3, "CT2": 50, "DB1_rounded": 2},
            "Digital_Realty_transaction_metrics_as_of_2026_03_31": {"in_place_IT_capacity_mw": 126, "under_construction_IT_capacity_mw": 41},
            "CT1_post_expansion_projection_excluding_JB7_mw": 191,
            "boundary": "228 MW includes JB7 construction; 189 MW is a dated completed-platform release; 188 MW is arithmetic from current page values; 126 plus 41 MW uses Digital Realty's transaction reporting scope. They are not silently normalized or summed.",
        },
        "equipment_and_sustainability": {
            "facility_specific_public_evidence": {
                "JB4": ["80MW_utility", "closed_loop_chilled_water", "free_air", "AI_enabled_controls", "liquid_to_liquid", "direct_to_chip"],
                "CT2": ["90MW_utility", "closed_loop_zero_water_cooling", "free_air", "AI_enhanced_controls", "liquid_to_liquid"],
                "JB7_design": ["68MVA_utility", "closed_loop_chilled_water", "direct_free_air", "liquid_to_air", "liquid_to_liquid"],
                "JB5": ["120MVA_utility", "closed_loop_chilled_water", "100_percent_free_air"],
                "JB1_historical": ["210000_litre_diesel_storage", "minimum_40_hours_at_full_load"],
            },
            "portfolio_2024_blended_PUE": 1.47,
            "portfolio_2024_water_litres_per_IT_kwh": 0.05,
            "portfolio_2024_total_water_kl": 34006,
            "portfolio_2024_borehole_water_kl": 3522,
            "portfolio_2024_rainwater_kl": 483,
            "portfolio_2024_waste_diverted_percent": 52,
            "utility_solar_PV_under_construction_mw": 120,
            "solar_operation_due_in_source": 2026,
            "solar_completion_confirmed_as_of_2026_07_19": False,
            "exact_current_per_site_transformer_switchgear_UPS_battery_generator_chiller_CRAH_CDU_models_counts_and_single_line_topology": "undisclosed",
        },
        "AI_and_GPU_boundary": {
            "NVIDIA_DGX_Ready_certified": True,
            "published_AI_infrastructure_density_context_kw_per_rack_up_to": 150,
            "exact_Teraco_facility_supported_or_live_rack_density_kw": "undisclosed",
            "liquid_cooling_capability": True,
            "Teraco_owned_GPU_model_count_site_delivery_utilization_and_power": "undisclosed",
            "customer_GPU_inventory_assignable_to_Teraco": False,
            "accelerator_ledger_action": "no_numeric_row_created",
            "boundary": "DGX-Ready certification, high-density support and liquid-cooling designs establish infrastructure capability, not accelerator ownership or inventory.",
        },
        "ownership_and_financial_boundary": {
            "Digital_Realty_completed_controlling_interest_percent_from_2022": 61.1,
            "additional_interest_agreed_2026_06_22_percent": 16,
            "consideration_USD_million_approximate": 650,
            "post_close_target_ownership_percent": 77,
            "expected_close": "H2_2026",
            "customary_closing_conditions": True,
            "completion_confirmed_as_of_2026_07_19": False,
            "transaction_deck_revenue_USD_million": 352,
            "revenue_period_and_accounting_basis": "not_explicit_beyond_metrics_as_of_2026_03_31",
            "standalone_statutory_operating_profit_cash_flow_capex_debt_and_ROIC": "undisclosed",
            "boundary": "The transaction-deck revenue metric is not relabeled as annual or statutory revenue, and Digital Realty group or noncontrolling-interest FFO is not Teraco standalone operating profit.",
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_rows),
            "exact_Teraco_operator_tagged_objects": sum(row["raw_operator"] == "Teraco" for row in osm_rows),
            "legacy_typo_operator_objects": sum(row["raw_operator"] == "Terao Data Environments" for row in osm_rows),
            "objects_without_operator_tag": sum(row["raw_operator"] is None for row in osm_rows),
            "data_center_related_objects": sum(row["facility_ref"] != "teraco_teleport" for row in osm_rows),
            "non_data_center_connectivity_objects": sum(row["facility_ref"] == "teraco_teleport" for row in osm_rows),
            "rows": osm_rows,
        },
        "source_urls": [HOME, DIRECTORY, JOHANNESBURG, CAPE_TOWN, DURBAN, JB3_COMPLETION, JB4_INITIAL, JB4_COMPLETION, JB5_GROUNDBREAKING, JB7_ANNOUNCEMENT, CT2_COMPLETION, CT1_EXPANSION, DB1_COMPLETION, SUSTAINABILITY, CERTIFICATIONS, AI_INFRASTRUCTURE, DLR_TRANSACTION, DLR_TRANSACTION_DECK, DLR_2025_10K],
        "unresolved_gaps": [
            "current_non_overlapping_physical_building_roster_title_lease_and_lifecycle",
            "126MW_in_place_41MW_construction_189MW_completed_release_188MW_directory_arithmetic_and_228MW_marketing_scope_bridge",
            "facility_level_energized_leased_utilized_customer_accepted_billed_and_actual_IT_load",
            "Teraco_standalone_statutory_revenue_operating_profit_cash_flow_capex_debt_customer_concentration_and_ROIC",
            "GPU_model_count_owner_host_site_delivery_power_utilization_revenue_and_margin",
            "per_site_grid_substation_transformer_switchgear_UPS_battery_generator_fuel_runtime_and_single_line_topology",
            "per_site_cooling_equipment_OEM_model_count_rating_live_liquid_cooled_MW_PUE_WUE_water_and_actual_load",
            "Digital_Realty_additional_16_percent_transaction_completion",
            "JB7_and_CT1_expansion_completion_grid_energization_customer_acceptance_and_revenue_commencement",
            "120MW_solar_project_completion_generation_wheeling_hourly_matching_and_site_allocation",
        ],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_rows = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_rows, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "teraco_official_facility_registry.jsonl"
    summary_path = args.output_dir / "teraco_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
