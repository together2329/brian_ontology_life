#!/usr/bin/env python3
"""Build a scope-preserving Yandex data-center and legacy-Nebius registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


YANDEX_PHYSICAL_ADDRESS_URL = "https://yandex.cloud/ru/docs/troubleshooting/legal/how-to/data-centers-physical-addresses"
YANDEX_GEO_SCOPE_URL = "https://yandex.cloud/en/docs/overview/concepts/geo-scope"
YANDEX_RU_E_URL = "https://yandex.cloud/ru/blog/ru-central1-e-exploitation"
YANDEX_SUSTAINABILITY_2025_URL = "https://ir.yandex.ru/press-releases?id=17-06-2026-01&year=2026"
YANDEX_RELIABILITY_2020_URL = "https://yandex.cloud/ru-kz/blog/posts/2020/09/reliability-episode-1"
YANDEX_SERVER_2021_URL = "https://yandex.ru/company/news/2021-11-19"
YANDEX_GPU_DOCS_URL = "https://yandex.cloud/en/docs/compute/concepts/gpus"
YANDEX_GPU_CLUSTER_URL = "https://yandex.cloud/en/docs/compute/operations/gpu-cluster/gpu-cluster-create"
YANDEX_SUPERCOMPUTERS_URL = "https://yandex.com/supercomputers"
YANDEX_SUPERCOMPUTER_LOCATIONS_URL = "https://yandex.ru/company/news/superkompyuter-yandeksa-priznali-samym-moschnym-v-rossii"
YANDEX_CLOUD_2025_RESULTS_URL = "https://ir.yandex.ru/press-releases?id=12-03-2026-01&year=2026"
YANDEX_GROUP_2025_URL = "https://ir.yandex.ru/financial-releases?report=q4&year=2025"
YANDEX_GROUP_Q1_2026_URL = "https://ir.yandex.ru/financial-releases?report=q1&year=2026"
YANDEX_DIVESTMENT_INITIAL_URL = "https://yandex.com/company/news/01-17-05-2024"
NEBIUS_DIVESTMENT_FINAL_URL = "https://nebius.com/newsroom/ynv-announces-successful-completion-of-the-divestment-of-its-russia-based-businesses"
NEBIUS_NAME_CHANGE_URL = "https://nebius.com/newsroom/nebius-group-n-v-announces-official-name-change-and-new-ticker-symbol"
NEBIUS_FINLAND_310MW_URL = "https://nebius.com/newsroom/nebius-to-construct-310-mw-ai-factory-in-finland"
NEBIUS_FINLAND_75MW_URL = "https://nebius.com/newsroom/nebius-to-triple-capacity-at-finland-data-center-to-75-mw"
NEBIUS_FINLAND_SUSTAINABILITY_URL = "https://nebius.com/sustainability/our-greenfield-data-center-in-finland"


OSM_CROSSWALK = {
    "osm_relation_17163450": ("Russia", "Vladimir", "current_Yandex_address_roster_exact_name_and_locality_match", True),
    "osm_way_1156034466": ("Russia", "Kaluga", "current_Yandex_address_roster_exact_name_and_locality_match", True),
    "osm_way_192215351": ("Russia", "Sasovo", "current_Yandex_address_roster_exact_name_and_locality_match", True),
    "osm_relation_17163169": ("Finland", "Mantsala", "legacy_Yandex_owner_label_current_Nebius_successor_campus_relation", False),
    "osm_way_1246864464": ("Finland", "Mantsala", "legacy_Global_DC_OY_name_current_Nebius_successor_campus_building", False),
    "osm_way_846760920": ("Finland", "Mantsala", "legacy_Yandex_operator_label_current_Nebius_successor_campus_building", False),
}


SUPERCOMPUTERS = [
    {
        "system": "Chervonenkis",
        "site": "Sasovo",
        "commissioned": "2021-06",
        "nodes": 199,
        "GPU_model": "NVIDIA_A100_80GB",
        "GPU_count": 1_592,
        "performance_PF": 21.53,
        "power_kW": 583,
        "RAM_TB": 199,
        "TOP500_June_2026_url": "https://top500.org/system/180029/",
    },
    {
        "system": "Galushkin",
        "site": "Vladimir",
        "commissioned": "2021-06",
        "nodes": 136,
        "GPU_model": "NVIDIA_A100_80GB",
        "GPU_count": 1_088,
        "performance_PF": 16.02,
        "power_kW": 330,
        "RAM_TB": 136,
        "TOP500_June_2026_url": "https://www.top500.org/system/180037/",
    },
    {
        "system": "Lyapunov",
        "site": "Sasovo",
        "commissioned": "2020-12",
        "nodes": 137,
        "GPU_model": "NVIDIA_A100_40GB",
        "GPU_count": 1_096,
        "performance_PF": 12.81,
        "power_kW": 323,
        "RAM_TB": 68.5,
        "TOP500_June_2026_url": "https://www.top500.org/system/180030/",
    },
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CROSSWALK:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CROSSWALK)
    return rows


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    addresses = [
        ("Vladimir", "Energetik_microdistrict_Poiskovaya_Street_1_building_2", "osm_relation_17163450"),
        ("Sasovo", "Pushkina_Street_21", "osm_way_192215351"),
        ("Kaluga", "1st_Avtomobilny_passage_8", "osm_way_1156034466"),
        ("Mytishchi", "Silikatnaya_Street_19", None),
    ]
    records = [{
        "id": f"yandex_current_address_roster_{site.lower()}",
        "object_type": "ProviderPhysicalAddressRosterEntry",
        "operator": "Yandex_Group",
        "country": "Russia",
        "site": site,
        "address_transliterated": address,
        "OSM_ref": osm_ref,
        "provider_page_last_updated": "2025-07-23",
        "lifecycle": "current_address_entry_on_reviewed_provider_page",
        "boundary": "The provider page predates the March 2026 launch of ru-central1-e. It is exact address evidence, but it is not used to assign availability-zone letters or to prove a complete post-launch building roster.",
        "source_url": YANDEX_PHYSICAL_ADDRESS_URL,
        "accessed_on": accessed_on,
    } for site, address, osm_ref in addresses]

    records.extend([
        {
            "id": "yandex_cloud_current_geographic_scope_2026_07_13",
            "object_type": "CurrentCloudGeographicScopeDisclosure",
            "operator": "Yandex_Group",
            "country": "Russia",
            "page_updated": "2026-07-13",
            "Yandex_data_centers": 4,
            "availability_zones": ["ru-central1-a", "ru-central1-b", "ru-central1-d", "ru-central1-e"],
            "separate_BareMetal_service_zone": "ru-central1-m",
            "boundary": "Five zone identifiers do not establish five owned physical data centers. The BareMetal m zone is a separate service-zone scope, and no reviewed official source maps zone letters to the four physical addresses.",
            "source_url": YANDEX_GEO_SCOPE_URL,
            "accessed_on": accessed_on,
        },
        {
            "id": "yandex_cloud_ru_central1_e_current_capacity_2026",
            "object_type": "CurrentAvailabilityZoneAndDataCenterCapacityDisclosure",
            "operator": "Yandex_Group",
            "country": "Russia",
            "availability_zone": "ru-central1-e",
            "launched": "2026-03-16",
            "facility_wording": "full_fledged_data_center_with_independent_power_and_network",
            "power_MW": 40,
            "racks": 2_800,
            "network_capacity_Tbps": 25.6,
            "average_PUE": 1.1,
            "cooling": "year_round_outdoor_air_free_cooling",
            "latency_to_ru_central1_a_ms_less_than": 1,
            "physical_address_and_bridge_to_current_four_data_center_statement": "undisclosed_or_unestablished",
            "boundary": "The 40-MW and 2,800-rack values are not added as a fifth physical data center. No exact address or official zone-to-building crosswalk was found, and power is not identified as critical IT load, live load, sold load or billed load.",
            "source_url": YANDEX_RU_E_URL,
            "accessed_on": accessed_on,
        },
    ])

    for osm_id, source in osm_rows.items():
        country, campus, classification, current_russia = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"yandex_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityLocationEvidence",
            "operator_boundary": "current_Yandex_Russia" if current_russia else "legacy_Yandex_label_current_Nebius_successor_Finland",
            "country": country,
            "campus_or_site": campus,
            "OSM_ref": osm_id,
            "match_classification": classification,
            "raw_name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_start_date": source.get("tags", {}).get("start_date"),
            "source_url": source["source_url"],
            "count_boundary": "An OSM relation or way is mapped geometry, not a complete provider roster, physical-building count, title record, gross floor area, IT capacity, live load, equipment inventory or financial contribution. The three Finland geometries are grouped as one legacy Mantsala campus rather than three data centers.",
            "accessed_on": accessed_on,
        })

    for system in SUPERCOMPUTERS:
        records.append({
            "id": f"yandex_historical_supercomputer_{system['system'].lower()}",
            "object_type": "DatedInstalledSupercomputerDisclosure",
            "operator": "Yandex_Group",
            "country": "Russia",
            **system,
            "interconnect": "InfiniBand_HDR",
            "source_url": YANDEX_SUPERCOMPUTERS_URL,
            "site_source_url": YANDEX_SUPERCOMPUTER_LOCATIONS_URL,
            "boundary": "This exact installed system disclosure dates to 2020-2021. Continued TOP500 listing in June 2026 does not prove unchanged current hardware, service state, utilization or the complete Yandex GPU fleet.",
            "accessed_on": accessed_on,
        })

    records.append({
        "id": "yandex_legacy_finland_current_nebius_successor_boundary",
        "object_type": "CorporateDivestitureAndSuccessorFacilityBoundary",
        "country": "Finland",
        "campus": "Mantsala",
        "legacy_operator": "Yandex",
        "current_operator": "Nebius_Group",
        "corporate_transition": "Yandex_NV_retained_Finland_and_international_businesses_then_became_Nebius_Group_after_the_July_2024_final_Russian_divestment",
        "current_existing_campus_power_MW": 75,
        "current_existing_campus_expansion_completed": "early_2026",
        "current_GPU_disclosure": "Europe_inaugural_operational_NVIDIA_GB300_NVL72_deployment_unit_count_undisclosed",
        "dated_design_placement_ceiling_GPU_up_to": 60_000,
        "separate_new_AI_factory_announced_power_MW": 310,
        "existing_fleet_cooling": "filtered_outdoor_air_free_cooling_without_chillers_water_loops_or_refrigerants",
        "PUE_at_full_capacity": 1.13,
        "future_liquid_cooling_density_kW_per_rack_up_to": 200,
        "boundary": "Mantsala is current Nebius infrastructure and is not counted as current Russian Yandex physical inventory. The 60,000-GPU value is a dated placement ceiling, 310 MW is a separate future project, and neither is current installed GPU count or live load.",
        "source_urls": [YANDEX_DIVESTMENT_INITIAL_URL, NEBIUS_DIVESTMENT_FINAL_URL, NEBIUS_NAME_CHANGE_URL, NEBIUS_FINLAND_310MW_URL, NEBIUS_FINLAND_75MW_URL, NEBIUS_FINLAND_SUSTAINABILITY_URL],
        "accessed_on": accessed_on,
    })

    assert len(records) == 16
    assert sum(row["object_type"] == "ProviderPhysicalAddressRosterEntry" for row in records) == 4
    assert sum(row["object_type"] == "OSMFacilityLocationEvidence" for row in records) == 6
    assert sum(row["object_type"] == "DatedInstalledSupercomputerDisclosure" for row in records) == 3
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    osm = [row for row in records if row["object_type"] == "OSMFacilityLocationEvidence"]
    russia = [row for row in osm if row["operator_boundary"] == "current_Yandex_Russia"]
    finland = [row for row in osm if row["country"] == "Finland"]
    systems = [row for row in records if row["object_type"] == "DatedInstalledSupercomputerDisclosure"]
    all_footprint = round(sum(row["OSM_footprint_area_m2"] or 0 for row in osm), 3)
    russia_footprint = round(sum(row["OSM_footprint_area_m2"] or 0 for row in russia), 3)
    finland_footprint = round(sum(row["OSM_footprint_area_m2"] or 0 for row in finland), 3)
    raw_operator_tagged = [row for row in osm if row["raw_operator"] == "Yandex"]
    gpu_count = sum(row["GPU_count"] for row in systems)
    system_power = sum(row["power_kW"] for row in systems)
    system_nodes = sum(row["nodes"] for row in systems)
    assert all_footprint == 641_054.154
    assert russia_footprint == 562_659.004
    assert finland_footprint == 78_395.150
    assert len(raw_operator_tagged) == 4
    assert gpu_count == 3_776
    assert system_power == 1_236
    assert system_nodes == 472

    return {
        "id": "yandex_data_center_summary_2026_07_19",
        "operator_boundary": "current_Russian_Yandex_Group_separated_from_legacy_Finland_current_Nebius_Group",
        "accessed_on": accessed_on,
        "current_Russian_physical_and_zone_scope": {
            "current_geo_scope_document_Yandex_data_centers": 4,
            "availability_zones": ["ru-central1-a", "ru-central1-b", "ru-central1-d", "ru-central1-e"],
            "separate_BareMetal_zone": "ru-central1-m",
            "physical_address_page_last_updated": "2025-07-23",
            "address_roster": ["Vladimir", "Sasovo", "Kaluga", "Mytishchi"],
            "OSM_exact_current_address_matches": ["Vladimir", "Sasovo", "Kaluga"],
            "ru_central1_e": {"launched": "2026-03-16", "power_MW": 40, "racks": 2_800, "network_Tbps": 25.6, "average_PUE": 1.1, "cooling": "year_round_outdoor_air_free_cooling"},
            "unresolved_bridge": "The pre-launch four-address article, current four-data-center statement and post-launch ru-central1-e facility disclosure lack an official zone-to-address crosswalk. No fifth building or zone-address assignment is inferred.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "raw_Yandex_operator_tagged_objects_routed_by_coverage_audit": len(raw_operator_tagged),
            "current_Russia_objects": len(russia),
            "legacy_Finland_current_Nebius_objects_grouped_as_one_campus": len(finland),
            "current_Russia_mapped_footprint_area_m2_sum_not_floor_area": russia_footprint,
            "legacy_Finland_mapped_footprint_area_m2_sum_not_floor_area": finland_footprint,
            "all_six_mapped_footprint_area_m2_sum_not_floor_area": all_footprint,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "OSM geometry is not provider floor area or a physical-building census. The coverage audit routes only four raw operator-tagged Yandex objects; two additional Finland geometries are related page-registry evidence.",
        },
        "power_cooling_and_equipment": {
            "current_2026_ru_central1_e": {"independent_power_and_network": True, "power_MW_undefined_capacity_class": 40, "average_PUE": 1.1, "year_round_outdoor_air_free_cooling": True},
            "current_2025_largest_Yandex_data_centers_PUE": 1.12,
            "dated_2020_portfolio_engineering": {"grid_connection": "direct_110kV_or_higher_connections_with_owned_cable_lines_and_substations", "backup_power": "DRUPS_from_multiple_unnamed_vendors_with_kinetic_flywheel_bridging_diesel_start", "cooling": "filtered_outdoor_air_cold_aisle_hot_collector_exhaust_and_recirculation_mixing", "Sasovo_and_Vladimir_PUE_range": "1.05_to_1.07"},
            "dated_2021_servers": {"server_CPU_families": ["AMD_EPYC_Milan", "Intel_Ice_Lake"], "operation_temperature_C_up_to": 40, "Vladimir_and_Mantsala_PUE": 1.1},
            "exact_current_per_site_grid_contract_substation_transformer_switchgear_busway_PDU_DRUPS_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_test_state_age_and_remaining_life": "undisclosed_or_unestablished",
            "current_per_site_measured_PUE_WUE_energy_water_emissions_heat_reuse_and_live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "The 2020 and 2021 engineering disclosures are dated portfolio evidence and are not propagated as the current bill of materials for every site. The 2025 PUE is scoped to the largest Yandex data centers, not the full fleet.",
        },
        "AI_GPU_and_supercomputers": {
            "dated_2020_2021_named_systems": {"systems": [row["system"] for row in systems], "nodes": system_nodes, "NVIDIA_A100_GPU_count": gpu_count, "system_power_kW": system_power, "sites": {"Sasovo": ["Chervonenkis", "Lyapunov"], "Vladimir": ["Galushkin"]}},
            "current_Yandex_Cloud_GPU_VM_models": ["NVIDIA_V100_32GB", "NVIDIA_A100_80GB", "NVIDIA_T4_16GB", "T4i_24GB"],
            "V100_and_A100_VM_zone_availability": ["ru-central1-a", "ru-central1-b"],
            "GPU_cluster_creation_zones": ["ru-central1-a", "ru-central1-d"],
            "Gen2_GPU_cluster_customer_configuration_ceiling": {"VMs": 20, "GPUs_per_VM": 8, "GPUs": 160, "condition": "subject_to_technical_availability"},
            "exact_current_total_physical_GPU_accelerator_model_count_owner_site_delivery_acceptance_service_state_server_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "The 3,776 A100s are an exact dated floor for three named systems, not current total inventory. Product availability and a 160-GPU customer cluster ceiling do not disclose installed fleet size.",
        },
        "legacy_Finland_current_Nebius_boundary": {
            "current_operator": "Nebius_Group",
            "existing_Mantsala_power_MW": 75,
            "expansion_completed": "early_2026",
            "operational_GPU_disclosure": "Europe_inaugural_NVIDIA_GB300_NVL72_deployment_count_undisclosed",
            "dated_GPU_placement_ceiling_up_to": 60_000,
            "separate_announced_new_AI_factory_MW": 310,
            "PUE_at_full_capacity": 1.13,
            "existing_fleet_cooling": "filtered_outdoor_air_without_chillers_water_loops_or_refrigerants",
            "future_liquid_cooling_density_kW_per_rack_up_to": 200,
            "boundary": "Legacy Yandex and Global DC OY OSM labels do not make Mantsala current Yandex Russia inventory. The current facility, current operator and separate future project are recorded without combining their power or GPU scopes.",
        },
        "financial_and_investability": {
            "Yandex_Cloud_2025_RUB_b": {"revenue": 27.6, "year_over_year_growth_percent": 39, "positive_EBITDA_margin_year_in_sequence": 4, "exact_EBITDA_operating_profit_and_margin": "undisclosed", "external_revenue_percent": 93, "external_customers": 51_000, "partner_count": 883, "AI_Studio_revenue": 2.0},
            "Yandex_Group_FY2025_RUB_b": {"revenue": 1_441.1, "IFRS_operating_profit": 173.6, "net_income": 79.6, "adjusted_EBITDA": 280.8, "adjusted_EBITDA_margin_percent": 19.5, "adjusted_net_income": 141.4, "cash_cash_equivalents_and_deposits": 250.2, "adjusted_net_debt_to_adjusted_EBITDA": 0.2},
            "B2B_Tech_FY2025_RUB_b": {"revenue": 48.2, "adjusted_EBITDA": 9.4, "adjusted_EBITDA_margin_percent": 19.6, "scope": "Cloud_360_and_other_businesses_not_Cloud_only"},
            "Yandex_Group_Q1_2026_RUB_b": {"revenue": 372.7, "operating_profit": 46.0, "adjusted_EBITDA": 73.3, "adjusted_EBITDA_margin_percent": 19.7, "net_income": 28.9, "adjusted_net_income": 34.7},
            "B2B_Tech_Q1_2026_RUB_b": {"revenue": 13.6, "year_over_year_growth_percent": 36, "adjusted_EBITDA": 2.6, "year_over_year_adjusted_EBITDA_growth_percent": 49, "adjusted_EBITDA_margin_percent": 19.4},
            "direct_listed_exposure": "MKPAO_Yandex_MOEX_YDEX_diversified_Russian_technology_group",
            "not_current_Yandex_exposure": "NASDAQ_NBIS_is_Nebius_successor_not_current_Russian_Yandex",
            "data_center_or_Yandex_Cloud_exact_operating_profit_cash_flow_capex_assets_debt_customer_concentration_physical_utilization_and_ROIC": "not_separately_disclosed",
            "boundary": "B2B Tech includes Cloud, Yandex 360 and other businesses. Group revenue and operating profit cannot be attributed to data centers or Cloud, and the current Russian Yandex security is not the former Nasdaq Yandex N.V. successor.",
        },
        "outlook": {
            "Yandex_Group_2026_guidance": {"revenue_growth_percent_approx": 20, "adjusted_EBITDA_RUB_b_approx": 350},
            "positive_signals": ["Yandex_Cloud_2025_revenue_growth_39_percent", "fourth_consecutive_positive_Cloud_EBITDA_margin_year", "ru_central1_e_40MW_and_2800_racks_live", "Q1_2026_B2B_Tech_growth", "low_group_adjusted_leverage"],
            "conversion_tests": ["publish_post_launch_physical_roster_and_zone_address_crosswalk", "disclose_current_installed_GPU_inventory", "allocate_site_power_to_live_sold_billed_load", "disclose_Cloud_only_profit_cash_flow_capex_and_ROIC", "publish_current_site_equipment_and_efficiency_ledgers", "track_2026_group_guidance_delivery"],
            "risks": ["Russia_market_access_geopolitical_regulatory_and_sanctions", "currency", "diversified_group_not_data_center_pure_play", "Cloud_segment_profitability_opacity", "capital_intensity", "GPU_and_site_utilization_opacity", "corporate_name_and_legacy_asset_confusion"],
            "analytical_view": "Yandex provides fast-growing listed-parent cloud and AI-demand exposure, but the investment case is a diversified Russian technology-group case rather than a data-center pure play. The critical proofs are Cloud-only cash economics, current GPU inventory, physical utilization and a resolved post-launch site roster.",
        },
        "records": records,
        "sources": [YANDEX_PHYSICAL_ADDRESS_URL, YANDEX_GEO_SCOPE_URL, YANDEX_RU_E_URL, YANDEX_SUSTAINABILITY_2025_URL, YANDEX_RELIABILITY_2020_URL, YANDEX_SERVER_2021_URL, YANDEX_GPU_DOCS_URL, YANDEX_GPU_CLUSTER_URL, YANDEX_SUPERCOMPUTERS_URL, YANDEX_SUPERCOMPUTER_LOCATIONS_URL, YANDEX_CLOUD_2025_RESULTS_URL, YANDEX_GROUP_2025_URL, YANDEX_GROUP_Q1_2026_URL, YANDEX_DIVESTMENT_INITIAL_URL, NEBIUS_DIVESTMENT_FINAL_URL, NEBIUS_NAME_CHANGE_URL, NEBIUS_FINLAND_310MW_URL, NEBIUS_FINLAND_75MW_URL, NEBIUS_FINLAND_SUSTAINABILITY_URL],
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
    registry_path = args.output_dir / "yandex_data_center_registry.jsonl"
    summary_path = args.output_dir / "yandex_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "OSM_related_objects": 6,
        "OSM_raw_operator_tagged_objects": 4,
        "historical_disclosed_A100_GPU_count": 3_776,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
