#!/usr/bin/env python3
"""Build the current SoftBank / legacy-IDCF Japan data-center registry.

IDC Frontier's public directory still exposes the inherited facility labels,
but SoftBank Corp. succeeded the complete data-center business on 2026-04-01.
This builder preserves that operating boundary, keeps provider locations apart
from physical buildings, and does not allocate SoftBank's companywide GPU fleet
to an individual site without a public source bridge.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY = "https://www.idcf.jp/datacenter/location/?bid=gnav_dc"
SERVICE_TERMS = "https://www.idcf.jp/pdf/common/dcservices.pdf"
SUCCESSION = "https://www.softbank.jp/en/corp/news/press/sbkk/2025/20251225_02/"
IDCF_PROFILE = "https://www.idcf.jp/en/company/about/company_profile/"
IDCF_HISTORY = "https://www.idcf.jp/company/about/history/"
FUCHU_DLC = "https://www.idcf.jp/news/pressrelease/20250707001/"
FUCHU_HIGH_LOAD = "https://www.idcf.jp/news/newsrelease/20250115001/"
KITAKYUSHU_SOFTBANK = "https://www.softbank.jp/business/service/platform/datacenter/asian"
KITAKYUSHU_2016 = "https://www.idcf.jp/pdf/pressrelease/IDCF20160325_kikakyusyu6_shirakawa4.pdf"
SHIRAKAWA_2018 = "https://cdn.www.idcf.jp/pressrelease/2018/20180418001.html"
SOFTBANK_CLIMATE = "https://www.softbank.jp/corp/sustainability/esg/environment/climate-change/"
IKOMA_OPENING = "https://www.idcf.jp/news/topics/20250730001"
IKOMA_BROCHURE = "https://www.idcf.jp/pdf/inquiry/download/datacenter/pdf/ikoma.pdf"
TOMAKOMAI_2023 = "https://www.softbank.jp/corp/news/press/sbkk/2023/20231107_01/"
TOMAKOMAI_2026 = "https://www.softbank.jp/corp/news/info/2026/20260630_01/"
SOFTBANK_GPU = "https://www.softbank.jp/en/corp/news/press/sbkk/2025/20250723_01/"
SOFTBANK_GPU_CLOUD = "https://www.softbank.jp/en/corp/news/press/sbkk/2026/20260525_01/"
SOFTBANK_FINANCIAL = "https://www.softbank.jp/en/corp/set/data/ir/documents/financial_reports/fy2025/pdf/sbkk_financial_report_20260511_en.pdf"
SOFTBANK_INVESTOR = "https://www.softbank.jp/en/corp/set/data/ir/documents/presentations/fy2025/investors/pdf/sbkk_investors_presentation_20260511_en.pdf"
SOFTBANK_FORECAST = "https://www.softbank.jp/en/corp/ir/financials/forecast/"


def page(slug: str) -> str:
    return f"https://www.idcf.jp/datacenter/location/{slug}/"


FACILITIES = [
    {
        "id": "softbank_idcf_tokyo_fuchu",
        "label": "Tokyo Fuchu",
        "slug": "fuchu",
        "prefecture": "Tokyo",
        "locality": "Fuchu",
        "lifecycle": "operating_current_inherited_directory",
        "opened": "2020-12",
        "technical_profile": {
            "maximum_receiving_capacity_mw": 50,
            "server_rooms": 25,
            "rack_capacity_approximate": 4000,
            "standard_effective_kVA_per_rack_average": 7,
            "high_density_kVA_per_rack": 15,
            "server_room_kVA_per_space_options": [1204, 1113],
            "utility": "loop_receiving",
            "UPS": "installed_topology_and_unit_ratings_undisclosed",
            "generation": "gas_turbine_emergency_generators",
            "fuel_autonomy_hours": 48,
            "cooling": ["air_cooled_chiller", "turbo_refrigerator", "water_cooled_wall_blow", "hot_aisle_capping"],
            "structure": "SRC_base_isolated",
            "high_load_service_racks_approximate_after_2025_expansion": 100,
            "DLC_service_kW_per_rack_up_to": 150,
        },
        "publication_conflicts": ["DLC_150kW_service_ceiling_and_general_high_density_15kVA_offer_are_different_products"],
        "source_urls": [page("fuchu"), FUCHU_DLC, FUCHU_HIGH_LOAD],
    },
    {
        "id": "softbank_idcf_tokyo_ariake",
        "label": "Tokyo Ariake",
        "slug": "ariake",
        "prefecture": "Tokyo",
        "locality": "Koto",
        "lifecycle": "operating_current_inherited_directory",
        "technical_profile": {
            "foundation": "63_piles_1_3_to_2_0m_diameter_driven_more_than_30m_to_rock",
            "utility": "three_spot_network_power",
            "UPS_kVA_per_floor": 1000,
            "generation": "gas_turbine_emergency_generators",
            "fuel_autonomy_hours": 18,
            "rack_units": ["half_EIA", "full_EIA"],
            "cooling": "type_capacity_redundancy_and_OEM_undisclosed",
        },
        "source_urls": [page("ariake")],
    },
    {
        "id": "softbank_idcf_tokyo_nihombashi",
        "label": "Tokyo Nihombashi",
        "slug": "nihombashi",
        "prefecture": "Tokyo",
        "locality": "Chuo",
        "lifecycle": "operating_current_inherited_directory",
        "technical_profile": {
            "structure": "confirmed_new_seismic_standard",
            "utility": "main_and_backup_receiving",
            "UPS": "continuous_service_during_statutory_inspection",
            "generation": "batteries_and_emergency_generation",
            "cooling": "type_capacity_redundancy_and_OEM_undisclosed",
            "capacity": "MW_racks_floor_area_and_live_load_undisclosed",
        },
        "source_urls": [page("nihombashi")],
    },
    {
        "id": "softbank_idcf_kanagawa_yokohama",
        "label": "Kanagawa Yokohama",
        "slug": None,
        "prefecture": "Kanagawa",
        "locality": "Yokohama",
        "lifecycle": "operating_current_directory_label",
        "technical_profile": {
            "address": "undisclosed_in_reviewed_current_directory",
            "power_cooling_capacity_and_equipment": "undisclosed_in_reviewed_current_directory",
        },
        "source_urls": [DIRECTORY, SERVICE_TERMS],
    },
    {
        "id": "softbank_idcf_osaka_suita",
        "label": "Osaka Suita",
        "slug": "osaka",
        "prefecture": "Osaka",
        "locality": "Suita",
        "lifecycle": "operating_current_inherited_directory",
        "technical_profile": {
            "elevation_m_approximate": 15,
            "structure": "strong_seismic_design",
            "utility": "multiple_receiving_circuits",
            "UPS": "installed_topology_and_unit_ratings_undisclosed",
            "generation": "gas_turbine_emergency_generators",
            "fuel_autonomy_hours": 18,
            "rack_units": ["quarter_EIA", "half_EIA", "full_EIA"],
            "cooling": "type_capacity_redundancy_and_OEM_undisclosed",
        },
        "source_urls": [page("osaka")],
    },
    {
        "id": "softbank_idcf_fukuoka_kitakyushu",
        "label": "Fukuoka Kitakyushu",
        "slug": "asianfrontier",
        "prefecture": "Fukuoka",
        "locality": "Kitakyushu",
        "lifecycle": "operating_current_inherited_directory",
        "technical_profile": {
            "design": "modular_building_by_building_expansion",
            "current_OSM_named_building_candidates": 8,
            "provider_maximum_expansion_buildings": 11,
            "provider_maximum_expansion_receiving_mw": 60,
            "typical_building_racks_approximate": 500,
            "utility": "two_special_high_voltage_systems_main_and_backup",
            "UPS": "N_plus_1",
            "generation": "gas_turbine_emergency_generators",
            "fuel_autonomy_hours": 72,
            "cooling": ["high_sensible_air_cooling", "fresh_air_cooling", "HVAC_N_plus_2"],
            "natural_air_share_of_annual_cooling_load_approximate_percent": 80,
            "historical_buildings_1_to_6_2016": {
                "campus_area_sqm": 39900,
                "total_floor_area_sqm": 27800,
                "racks_approximate": 3340,
                "receiving_capacity_MVA": 30,
                "rack_kVA_range": [6, 8],
            },
        },
        "publication_conflicts": ["eleven_buildings_and_60MW_are_maximum_expansion_not_current_operating_scope", "OSM_eight_buildings_are_map_evidence_not_provider_current_building_count"],
        "source_urls": [page("asianfrontier"), KITAKYUSHU_SOFTBANK, KITAKYUSHU_2016],
        "OSM_refs": [
            "osm_way_1239264177", "osm_way_1239264178", "osm_way_1239264179", "osm_way_1239264180",
            "osm_way_1239264181", "osm_way_1239264183", "osm_way_1272790322", "osm_way_1272790323",
        ],
    },
    {
        "id": "softbank_idcf_fukushima_shirakawa",
        "label": "Fukushima Shirakawa",
        "slug": "shirakawa",
        "prefecture": "Fukushima",
        "locality": "Shirakawa",
        "lifecycle": "operating_current_inherited_directory",
        "opened": "2012",
        "technical_profile": {
            "site_area_sqm_approximate": 67600,
            "design": "modular",
            "provider_maximum_expansion_buildings": 8,
            "provider_maximum_expansion_receiving_mw": 50,
            "utility": "main_and_backup_receiving",
            "UPS": "installed_topology_and_unit_ratings_undisclosed",
            "generation": "gas_turbine_emergency_generators",
            "fuel_autonomy_hours": 48,
            "cooling": "outside_air_plus_water_cooled_hybrid",
            "outside_air_share_of_annual_cooling_load_more_than_percent": 90,
            "fifth_building_2018": {"racks_approximate": 1400, "five_building_total_racks_approximate": 3320, "server_capacity_more_than": 165000, "design_PUE_approximate": 1.2},
        },
        "publication_conflicts": ["eight_buildings_and_50MW_are_maximum_expansion_not_current_operating_scope"],
        "source_urls": [page("shirakawa"), SHIRAKAWA_2018, SOFTBANK_CLIMATE],
    },
    {
        "id": "softbank_idcf_nara_ikoma",
        "label": "Nara Ikoma",
        "slug": "ikoma",
        "prefecture": "Nara",
        "locality": "Ikoma",
        "lifecycle": "operating_first_building_with_second_building_future",
        "opened": "2025-10",
        "technical_profile": {
            "first_building_completed": "2025-07",
            "two_building_future_receiving_capacity_mw": 50,
            "two_building_future_floor_area_sqm_approximate": 40000,
            "standard_rack_kVA": 9,
            "air_cooled_rack_kVA_range": [9, 30],
            "DLC_rack_kVA_range": [50, 120],
            "server_room_kVA_per_space": 855,
            "utility": "main_and_backup_receiving",
            "UPS": "N_plus_1_ten_minute_design_hold",
            "generation": "N_plus_1_emergency_generators",
            "fuel_autonomy_hours_up_to": 72,
            "cooling": "N_plus_1_water_cooled_wall_blow_hot_aisle_capping_plus_DLC",
            "structure": "SRC_base_isolated",
            "elevation_m": 135,
        },
        "publication_conflicts": ["50MW_and_40000sqm_apply_after_second_building_not_current_first_building", "current_page_DLC_50_to_120kVA_and_2025_service_release_up_to_150kW_are_different_published_scopes"],
        "source_urls": [page("ikoma"), IKOMA_OPENING, IKOMA_BROCHURE, FUCHU_DLC],
    },
    {
        "id": "softbank_idcf_hokkaido_tomakomai_development",
        "label": "Hokkaido Tomakomai",
        "slug": "tomakomai",
        "prefecture": "Hokkaido",
        "locality": "Tomakomai",
        "lifecycle": "development_targeting_opening_during_Japanese_FY2026",
        "technical_profile": {
            "program": "Brain_DataCenter",
            "phase_one_receiving_capacity_mw": 50,
            "ultimate_site_area_sqm": 700000,
            "ultimate_receiving_capacity_mw_more_than": 300,
            "green_area_sqm": 200000,
            "nature_coexistence_certified_area_sqm": 135000,
            "renewable_energy_target_percent": 100,
            "power_cooling_as_built_equipment": "undisclosed_before_opening",
        },
        "publication_conflicts": ["FY2026_opening_target_is_not_current_operating_status", "300MW_plus_is_ultimate_capacity_not_phase_one"],
        "source_urls": [page("tomakomai"), TOMAKOMAI_2023, TOMAKOMAI_2026, SOFTBANK_INVESTOR],
    },
]


OSM_CROSSWALK = {
    "osm_way_1239264177": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1239264178": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1239264179": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1239264180": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1239264181": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1239264183": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1272790322": "softbank_idcf_fukuoka_kitakyushu",
    "osm_way_1272790323": "softbank_idcf_fukuoka_kitakyushu",
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(FACILITIES, start=1):
        source_urls = source.get("source_urls", [])
        records.append({
            "object_type": "DataCenterFacilityEvidence",
            "source_order": order,
            "operator_current": "SoftBank_Corp",
            "provider_directory_brand": "IDC_Frontier_legacy_directory",
            "operating_boundary_effective": "2026-04-01",
            "country_code": "JP",
            "address": "not_publicly_disclosed_at_reviewed_provider_granularity",
            "physical_GPU_or_accelerator_inventory_at_site": "undisclosed",
            "OSM_refs": source.get("OSM_refs", []),
            "accessed_on": accessed_on,
            **{key: value for key, value in source.items() if key not in {"OSM_refs", "source_urls"}},
            "source_urls": source_urls,
        })
    assert len(records) == 9
    assert len({row["id"] for row in records}) == 9
    assert Counter(row["lifecycle"].startswith("operating") for row in records) == {True: 8, False: 1}
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, facility_ref in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert source.get("operator") == "IDCフロンティア"
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "current_operator_route": "SoftBank_Corp_since_2026_04_01",
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_ref": facility_ref,
            "crosswalk_status": "exact_numbered_Kitakyushu_building_name_candidate",
            "source_url": source["source_url"],
            "boundary": "OSM geometry and the legacy operator tag are not current title, provider-certified floor area, live IT load, utilization or GPU inventory.",
        })
    assert len(rows) == 8
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    sources = sorted({url for row in records for url in row["source_urls"]} | {
        DIRECTORY, SERVICE_TERMS, SUCCESSION, IDCF_PROFILE, IDCF_HISTORY,
        SOFTBANK_GPU, SOFTBANK_GPU_CLOUD, SOFTBANK_FINANCIAL,
        SOFTBANK_INVESTOR, SOFTBANK_FORECAST,
    })
    return {
        "id": "softbank_idcf_data_center_summary_2026_07_19",
        "object_type": "SoftBankIDCFPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator_and_roster_boundary": {
            "current_operator": "SoftBank_Corp",
            "succession_effective": "2026-04-01",
            "legacy_directory_publisher": "IDC_Frontier",
            "current_directory_labels": 9,
            "operating_labels": 8,
            "development_labels": 1,
            "operating_labels_list": [row["label"] for row in records if row["lifecycle"].startswith("operating")],
            "development_labels_list": [row["label"] for row in records if not row["lifecycle"].startswith("operating")],
            "boundary": "The nine provider labels are not a physical-building census. Tomakomai is a development, and Kitakyushu and Shirakawa are multi-building campuses.",
        },
        "succession_financial_boundary": {
            "FY2025_transferred_data_center_division_revenue_JPY_million_excluding_sales_to_SoftBank": 16552,
            "transferred_assets_at_2025_09_30_JPY_million": {"current": 1648, "non_current": 9055, "total": 10703},
            "transferred_liabilities_at_2025_09_30_JPY_million": {"current": 8419, "non_current": 2284, "total": 10703},
            "transferred_division_operating_profit": "undisclosed",
            "IDCF_FY2025_standalone_JPY_million": {"revenue": 27181, "operating_income": 3933, "net_income": 2527, "total_assets": 34760, "net_assets": 8261},
            "boundary": "IDCF standalone results include both data center and cloud activity. The 16.552-billion-yen transferred-division revenue excludes sales to SoftBank, while no transferred-division operating profit was published.",
        },
        "SoftBank_current_financial_context": {
            "FY_ended_2026_03_31_JPY_million": {"revenue": 7038680, "operating_income": 1042576, "operating_margin_percent": 14.8, "net_income_attributable": 550759, "operating_cash_flow": 1393760, "investing_cash_flow": -1270806},
            "Enterprise_FY2026_revenue_JPY_million": 970136,
            "Enterprise_business_solutions_and_other_revenue_JPY_million": 483060,
            "FY_ending_2027_forecast_JPY_million": {"revenue": 7500000, "operating_income": 1100000, "net_income_attributable": 560000},
            "FY2026_to_FY2028_AI_related_committed_investments_JPY_trillion": 0.3,
            "boundary": "SoftBank consolidated and Enterprise results are not inherited data-center-only earnings. The forecast includes active AI-infrastructure investment and execution risk.",
        },
        "GPU_and_AI_compute_boundary": {
            "SoftBank_companywide_platform_as_of_2025_07_23": {
                "total_GPUs_more_than": 10000,
                "compute_exaflops": 13.7,
                "Blackwell_B200_GPUs_more_than": 4000,
                "Hopper_GPUs_historical_deployment_more_than": 4000,
                "Ampere_GPUs_historical_deployment_more_than": 2000,
                "network": "NVIDIA_Quantum_2_InfiniBand_for_B200_SuperPOD",
            },
            "2026_GPU_cloud": "NVIDIA_GB200_NVL72_and_other_advanced_GPU_infrastructure_in_unnamed_Japan_data_centers",
            "physical_site_allocation": "undisclosed",
            "facility_level_action": "do_not_allocate_companywide_GPU_counts_to_Fuchu_Ikoma_Tomakomai_or_any_other_site",
            "density_capability": {"Fuchu_DLC_kW_per_rack_up_to": 150, "Ikoma_current_DLC_kVA_per_rack_range": [50, 120]},
        },
        "broader_SoftBank_AI_pipeline_outside_inherited_nine_label_roster": {
            "Sakai_AI_data_center_receiving_capacity_mw": 140,
            "Sakai_target_compute_exaflops": 110,
            "Tomakomai_phase_one_mw": 50,
            "committed_AI_investment_JPY_trillion": 0.3,
            "boundary": "Sakai is kept outside the inherited nine-label registry. Tomakomai appears in both the legacy directory and SoftBank's AI pipeline but remains one development record, not two sites.",
        },
        "public_map_crosswalk": {
            "legacy_IDCF_operator_tagged_OSM_objects": len(osm_rows),
            "all_routed_to": "Fukuoka_Kitakyushu_campus",
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_rows), 3),
            "objects": osm_rows,
            "boundary": "Eight numbered footprints are not eight provider-certified current operating buildings until an official current physical roster bridges them.",
        },
        "unresolved_gaps": [
            "nine_provider_labels_to_exact_non_overlapping_physical_buildings_parcels_title_lease_and_current_lifecycle",
            "current_Kitakyushu_and_Shirakawa_building_counts_and_per_building_RFS_status",
            "Ikoma_first_building_current_receiving_capacity_floor_area_rooms_racks_live_load_and_second_building_schedule",
            "Tomakomai_final_opening_date_grid_energization_customer_acceptance_equipment_BOM_and_GPU_delivery",
            "per_site_operating_energized_leased_utilized_billed_and_actual_metered_IT_load",
            "per_site_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CDU_models_counts_ratings_OEMs_and_as_built_topology",
            "per_site_measured_PUE_WUE_water_energy_renewable_hourly_matching_and_live_liquid_cooled_MW",
            "SoftBank_companywide_10000_plus_GPU_exact_model_current_active_retired_owner_host_site_power_utilization_customer_revenue_and_margin_bridge",
            "inherited_data_center_division_operating_profit_EBITDA_capex_cash_flow_customer_concentration_utilization_and_ROIC",
            "Sakai_140MW_and_110_exaflops_hardware_model_count_delivery_grid_construction_RFS_utilization_and_economics",
        ],
        "sources": sources,
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
    registry = args.output_dir / "softbank_idcf_data_center_registry.jsonl"
    summary_path = args.output_dir / "softbank_idcf_data_center_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
