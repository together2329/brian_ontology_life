#!/usr/bin/env python3
"""Build OVHcloud's current location, ownership, engineering and OSM registry.

The current OVHcloud location table exposes 19 region locations whose stated
datacenter counts sum to 46.  The FY2025 Universal Registration Document uses
an earlier 44-datacenter, 18-site boundary and separately identifies 31
directly held datacenters.  This builder preserves the current location table,
the FY2025 ownership boundary, environmental measurements, GPU service
availability and OSM objects without turning any of them into live IT MW or a
physical GPU inventory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


REGIONS_URL = "https://www.ovhcloud.com/en/about-us/global-infrastructure/regions/"
DATACENTER_URL = "https://www.ovhcloud.com/en/datacenter/"
URD_2025_URL = "https://corporate.ovhcloud.com/sites/default/files/2025-11/ovh_urd_2025_en_mel_25_11_14.pdf"
ENVIRONMENT_URL = "https://corporate.ovhcloud.com/asia/sustainability/environment/"
GPU_URL = "https://www.ovhcloud.com/en/public-cloud/gpu/"
GPU_LOCATION_URL = "https://docs.ovhcloud.com/en/guides/public-cloud/compute/deploy-a-gpu-instance"
SMART_COOLING_URL = "https://corporate.ovhcloud.com/en/newsroom/news/ovhcloud-smart-datacenter/"
H1_FY2026_URL = "https://corporate.ovhcloud.com/en-gb/newsroom/news/financial-results-h1-fy26/"
Q3_FY2026_URL = "https://corporate.ovhcloud.com/en/newsroom/news/financial-results-q3-fy26/"


def location(
    code: str,
    geography: str,
    country_code: str,
    country: str,
    official_region_location: str,
    site_or_submarket: str,
    year_opened: int,
    availability_zones: int,
    current_datacenters: int,
    FY2025_ownership_boundary: str,
    FY2025_directly_held_datacenters: int = 0,
    details: dict | None = None,
) -> dict:
    row = {
        "record_code": code,
        "geography": geography,
        "country_code": country_code,
        "country": country,
        "official_region_location": official_region_location,
        "site_or_submarket": site_or_submarket,
        "year_opened": year_opened,
        "current_availability_zones": availability_zones,
        "current_official_datacenter_count": current_datacenters,
        "FY2025_ownership_boundary": FY2025_ownership_boundary,
        "FY2025_directly_held_datacenter_count": FY2025_directly_held_datacenters,
        "current_location_power_MW_or_MVA": "undisclosed",
        "current_energized_leased_utilized_customer_accepted_and_billed_IT_load": "undisclosed",
        "source_urls": [REGIONS_URL, URD_2025_URL],
    }
    if details:
        row["selected_location_evidence"] = details
    return row


LOCATIONS = [
    location("FR_BOD", "Europe", "FR", "France", "Bordeaux", "Bordeaux", 2023, 1, 1, "shared_datacenter_at_FY2025_boundary"),
    location("FR_CRX", "Europe", "FR", "France", "Croix", "Croix", 2023, 1, 1, "directly_held_at_FY2025_boundary", 1, {
        "functions": ["small_datacenter_for_magnetic_tapes", "European_server_assembly_site"],
        "building_origin": "former_hygiene_products_factory",
    }),
    location("FR_GRA", "Europe", "FR", "France", "Gravelines", "Gravelines", 2013, 1, 4, "directly_held_at_FY2025_boundary", 4, {
        "building_origin": "former_can_production_site",
        "SecNumCloud": "contains_highly_secure_zone",
        "GPU_service_locations": {
            "legacy_V100_or_V100S": ["GRA7", "GRA9", "GRA11"],
            "newer_A100_H100_L4_L40S": ["GRA11"],
            "boundary": "Service-region codes and available instance models do not disclose physical card count, utilization, rack power or revenue; the numeric suffix is not a facility-count denominator.",
        },
    }),
    location("FR_GNB", "Europe", "FR", "France", "Grenoble", "Grenoble", 2023, 1, 1, "shared_datacenter_at_FY2025_boundary"),
    location("FR_PAR", "Europe", "FR", "France", "Paris", "Paris", 2024, 3, 3, "shared_three_AZ_datacenters_at_FY2025_boundary", 0, {
        "architecture": "three_independent_availability_zones",
        "ISO_22301": "three_AZ_datacenters_certified_in_2025",
        "boundary": "Three availability zones and three datacenters align in the current table but do not disclose individual buildings, MW or ownership counterparties.",
    }),
    location("FR_RBX", "Europe", "FR", "France", "Roubaix", "Roubaix", 2006, 1, 9, "directly_held_at_FY2025_boundary", 9, {
        "building_origin": "eight_of_nine_FY2025_datacenters_in_refurbished_industrial_buildings",
        "modernization": ["RBX1_energy_upgrade_underway", "RBX8_cooling_improvements_in_2025", "RBX10_new_cooling_system_in_2025"],
        "smart_rack_pilot": "nearly_60_racks_and_2000_servers_in_one_room; current deployment evidence, not fleet count",
        "smart_cooling": "fifth_generation_direct_to_chip_CPU_and_GPU_waterblocks, external_multi_row_CDU, closed_loop, more_than_30_sensors and predictive controls",
    }),
    location("FR_SBG", "Europe", "FR", "France", "Strasbourg", "Strasbourg", 2012, 1, 2, "directly_held_at_FY2025_boundary", 2, {
        "current_count_boundary": "The current table reports two datacenters after the 2021 fire and resilience rebuild; OSM labels SBG3 and SBG5 do not establish the complete historic roster.",
        "waste_heat_recovery": "studies_underway_at_FY2025",
    }),
    location("FR_TUF", "Europe", "FR", "France", "Tours", "Tours", 2023, 1, 1, "shared_datacenter_at_FY2025_boundary"),
    location("IT_MIL", "Europe", "IT", "Italy", "Milan", "ZVF / Milan", 2025, 3, 3, "mixed_and_time_variant_one_directly_held_datacenter_at_FY2025_plus_two_current_incremental_datacenters_with_ownership_boundary_undisclosed", 1, {
        "FY2025_direct_site": "one_refurbished_former_telecommunications_building_near_Milan",
        "three_AZ_launch": "current_table_reports_three_AZ_and_three_DC_after_FY2025",
        "boundary": "The two-datacenter increase from the FY2025 one-DC Italy map to the current three-DC table is not assigned to owned versus shared property without additional evidence.",
    }),
    location("DE_LIM", "Europe", "DE", "Germany", "Frankfurt", "Limburg an der Lahn", 2016, 1, 2, "directly_held_at_FY2025_boundary", 2, {
        "building_origin": "former_printing_works",
        "current_count_boundary": "Official current count is two; the OSM name LIM1-3 is retained as a stale_or_non_counting_label conflict, not evidence for three current datacenters.",
    }),
    location("PL_WAW", "Europe", "PL", "Poland", "Warsaw", "Ozarow Mazowiecki", 2016, 1, 1, "directly_held_at_FY2025_boundary", 1, {
        "building_origin": "former_logistics_building",
        "provider_code": "WAW1",
    }),
    location("GB_ERI", "Europe", "GB", "United Kingdom", "London", "Erith", 2016, 1, 1, "directly_held_at_FY2025_boundary", 1, {
        "building_origin": "former_telecommunications_building",
        "provider_code": "ERI",
    }),
    location("CA_BHS", "North_America", "CA", "Canada", "Montreal", "Beauharnois", 2012, 1, 8, "directly_held_at_FY2025_boundary", 8, {
        "building_origin": "former_Rio_Tinto_aluminium_plant",
        "energy_context": "nearby_Hydro_Quebec_hydropower",
        "functions": ["North_American_server_assembly_site", "datacenter_campus"],
        "production_capacity_servers_per_week_up_to": 1000,
        "cooling_upgrade": "BHS8_improvements_in_2025",
        "GPU_service_locations": {
            "legacy_V100_or_V100S": ["BHS5"],
            "newer_model_current_documentation": "not_listed_outside_GRA11",
            "boundary": "Service availability is not physical card inventory or utilization.",
        },
    }),
    location("CA_YYZ", "North_America", "CA", "Canada", "Toronto", "Cambridge", 2024, 1, 1, "shared_datacenter_at_FY2025_boundary"),
    location("US_HIL", "North_America", "US", "United States", "Seattle", "Hillsboro, Oregon", 2017, 1, 1, "directly_held_at_FY2025_boundary", 1, {
        "building_origin": "refurbished_manufacturing_industry_building",
        "provider_code": "HIL",
    }),
    location("US_VIN", "North_America", "US", "United States", "Washington DC", "Vint Hill, Virginia", 2016, 1, 1, "directly_held_at_FY2025_boundary", 1, {
        "building_origin": "refurbished_telecommunications_building",
        "provider_code": "VIN",
    }),
    location("AU_SYD", "Asia_Pacific", "AU", "Australia", "Sydney", "Sydney", 2016, 1, 3, "shared_datacenters_at_FY2025_boundary"),
    location("SG_SGP", "Asia_Pacific", "SG", "Singapore", "Singapore", "Singapore", 2016, 1, 2, "shared_datacenters_at_FY2025_boundary"),
    location("IN_BOM", "Asia_Pacific", "IN", "India", "Mumbai", "Mumbai", 2023, 1, 1, "shared_datacenter_at_FY2025_boundary"),
]


ENVIRONMENTAL_FY2025 = {
    "FR_RBX": {"energy_GWh": 128, "PUE": 1.30, "PUE_category": 2, "WUE_L_per_kWh": 0.29, "water_stress": "High", "renewable_energy_from_PPA_and_EAC_GWh": 127, "REF_percent": 100},
    "FR_GRA": {"energy_GWh": 130, "PUE": 1.21, "PUE_category": 2, "WUE_L_per_kWh": 0.20, "water_stress": "Medium", "renewable_energy_from_PPA_and_EAC_GWh": 130, "REF_percent": 100},
    "FR_SBG": {"energy_GWh": 47, "PUE": 1.19, "PUE_category": 2, "WUE_L_per_kWh": 0.39, "water_stress": "Low", "renewable_energy_from_PPA_and_EAC_GWh": 46, "REF_percent": 100},
    "GB_ERI": {"energy_GWh": 21, "PUE": 1.19, "PUE_category": 2, "WUE_L_per_kWh": 0.18, "water_stress": "High", "renewable_energy_from_PPA_and_EAC_GWh": 21, "REF_percent": 100},
    "DE_LIM": {"energy_GWh": 43, "PUE": 1.19, "PUE_category": 2, "WUE_L_per_kWh": 0.21, "water_stress": "Low", "renewable_energy_from_PPA_and_EAC_GWh": 43, "REF_percent": 100},
    "PL_WAW": {"energy_GWh": 19, "PUE": 1.25, "PUE_category": 2, "WUE_L_per_kWh": 0.42, "water_stress": "Low", "renewable_energy_from_PPA_and_EAC_GWh": 19, "REF_percent": 100},
    "US_VIN": {"energy_GWh": 39, "PUE": 1.36, "PUE_category": 1, "WUE_L_per_kWh": 0.40, "water_stress": "High", "renewable_energy_from_PPA_and_EAC_GWh": 39, "REF_percent": 100},
    "US_HIL": {"energy_GWh": 17, "PUE": 1.28, "PUE_category": 1, "WUE_L_per_kWh": 1.32, "water_stress": "Low", "renewable_energy_from_PPA_and_EAC_GWh": 17, "REF_percent": 100},
    "CA_BHS": {"energy_GWh": 73, "PUE": 1.21, "PUE_category": 2, "WUE_L_per_kWh": 0.86, "water_stress": "Low", "renewable_energy_from_PPA_and_EAC_GWh": 72, "REF_percent": 100, "measurement_boundary": "energy_and_efficiency_extrapolated_from_BHS8_IT_energy; water_metrics_exclude_BHS1_through_BHS7"},
}


OSM_DISPOSITIONS = {
    "osm_relation_1701662": {"provider_record_code": "CA_BHS", "disposition": "official_location_match_campus_object_not_eight_building_census"},
    "osm_way_229184178": {"provider_record_code": "DE_LIM", "disposition": "official_location_match_with_OSM_LIM1_3_name_conflicting_with_current_two_DC_count"},
    "osm_node_6222911368": {"provider_record_code": "FR_PAR", "disposition": "official_location_match_point_not_three_AZ_building_census"},
    "osm_way_38354559": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX1", "disposition": "exact_facility_code_match"},
    "osm_relation_8812014": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX2", "disposition": "exact_facility_code_match"},
    "osm_way_176779630": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX3", "disposition": "exact_facility_code_match"},
    "osm_way_234729371": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX4", "disposition": "exact_facility_code_match"},
    "osm_way_80148463": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX5", "disposition": "exact_facility_code_match"},
    "osm_way_80144821": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX6", "disposition": "exact_facility_code_match"},
    "osm_way_80150630": {"provider_record_code": "FR_RBX", "provider_facility_code": "RBX7", "disposition": "exact_facility_code_match"},
    "osm_way_551480870": {"provider_record_code": "FR_GRA", "disposition": "official_location_match_one_of_two_overlapping_or_campus_scale_OSM_footprints_not_four_DC_census"},
    "osm_way_551480895": {"provider_record_code": "FR_GRA", "disposition": "official_location_match_one_of_two_overlapping_or_campus_scale_OSM_footprints_not_four_DC_census"},
    "osm_way_875244715": {"provider_record_code": "FR_SBG", "provider_facility_code": "SBG3", "disposition": "exact_facility_code_match"},
    "osm_way_1257814939": {"provider_record_code": "FR_SBG", "provider_facility_code": "SBG5", "disposition": "exact_facility_code_match"},
    "osm_way_29120456": {"provider_record_code": "GB_ERI", "disposition": "official_location_match_by_operator_and_coordinates_name_missing"},
    "osm_relation_19065757": {"provider_record_code": "IT_MIL", "provider_facility_code": "MIL1", "disposition": "exact_facility_code_match_one_of_three_current_DC"},
    "osm_way_216811192": {"provider_record_code": "PL_WAW", "provider_facility_code": "WAW1", "disposition": "exact_facility_code_match"},
    "osm_way_225745958": {"provider_record_code": "US_VIN", "provider_facility_code": "VIN", "disposition": "exact_facility_code_match"},
    "osm_relation_4645970": {"provider_record_code": "US_HIL", "provider_facility_code": "HIL", "disposition": "exact_facility_code_match"},
}


PORTFOLIO_CONTEXT = {
    "current_official_region_location_rows": 19,
    "current_official_datacenter_count": 46,
    "current_official_country_count_from_location_table": 10,
    "current_official_availability_zone_checksum": 23,
    "FY2025_URD_datacenters": 44,
    "FY2025_URD_sites": 18,
    "FY2025_URD_countries": 10,
    "FY2025_directly_held_datacenters": 31,
    "FY2025_shared_or_not_directly_operated_datacenters_arithmetic_remainder": 13,
    "FY2025_installed_servers": 500000,
    "FY2025_servers_produced": 58000,
    "power_architecture": {
        "general": "double_power_supply_and_autonomous_generators; high_yield_UPS_or_inverters_and_busbars_named_but_per_site_counts_ratings_OEMs_and_topology_undisclosed",
        "one_AZ_marketing": "fully_redundant_power_and_network_with_2N_plus_1_design_distributed_across_several_datacenters",
        "three_AZ_marketing": "each_AZ_has_independent_and_redundant_power_cooling_and_network",
        "boundary": "General architecture statements do not prove each current location's as-built configuration; some one-AZ rows contain one datacenter despite the multi-datacenter marketing description.",
    },
    "cooling_architecture": {
        "legacy_and_current_core": "direct_to_chip_watercooling_for_CPU_and_other_high_energy_components; in_rack_air_to_water_heat_exchanger for remaining components; closed_loop; dry_coolers; no server-room air conditioning in the core design",
        "fifth_generation": "higher_temperature_water, direct_to_chip_CPU_and_GPU_blocks, external_multi_row_CDU, more_than_30_sensors, predictive pump_fan_valve control",
        "partial_PUE_latest_generation": 1.06,
        "boundary": "Design and pilot metrics are not current fleet-wide equipment deployment, live liquid-cooled MW or individual facility BOM.",
    },
    "GPU_service_boundary": {
        "current_marketed_models": ["NVIDIA_H200", "NVIDIA_H100", "NVIDIA_V100S", "NVIDIA_A100", "NVIDIA_A10", "NVIDIA_L40S", "NVIDIA_L4", "NVIDIA_Quadro_RTX_5000"],
        "instance_GPUs": "one_to_four_per_instance",
        "current_physical_GPU_inventory_by_model_site_count_delivery_state_power_and_utilization": "undisclosed",
        "location_evidence": "current deployment guide places legacy V100_or_V100S in GRA7_GRA9_GRA11_BHS5 and newer A100_H100_L4_L40S in GRA11; current H200 marketing page does not disclose a site",
    },
    "comparison_boundary": "Do not equate or sum region rows, availability zones, datacenters, sites, directly held buildings, shared facilities, OSM objects, installed servers, GPU instance models, physical GPUs, energy, subscribed power or live IT load.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        combined = f"{row.get('name') or ''} {row.get('operator') or ''}".casefold()
        if "ovh" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(LOCATIONS) == 19
    assert len({row["record_code"] for row in LOCATIONS}) == len(LOCATIONS)
    assert sum(row["current_official_datacenter_count"] for row in LOCATIONS) == 46
    assert sum(row["current_availability_zones"] for row in LOCATIONS) == 23
    assert sum(row["FY2025_directly_held_datacenter_count"] for row in LOCATIONS) == 31
    assert len(candidates) == 19, [row["id"] for row in candidates]
    assert set(OSM_DISPOSITIONS) == {row["id"] for row in candidates}
    reviews = []
    for object_id, disposition in OSM_DISPOSITIONS.items():
        source = osm[object_id]
        reviews.append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            **disposition,
            "boundary": "OSM identity and footprint do not prove provider lifecycle, ownership, capacity, power topology, customer load, GPU inventory or facility economics.",
        })
    records = []
    for position, source in enumerate(LOCATIONS, 1):
        row = {
            "id": f"ovhcloud_{source['record_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterRegionLocationRecord",
            "source_order": position,
            "operator": "OVHcloud",
            "record_granularity": "current_provider_region_location_with_aggregate_datacenter_and_AZ_counts_not_uniform_physical_building_or_property",
            **source,
            "portfolio_context": PORTFOLIO_CONTEXT,
            "accessed_on": accessed_on,
        }
        if source["record_code"] in ENVIRONMENTAL_FY2025:
            row["FY2025_environmental_measurements"] = ENVIRONMENTAL_FY2025[source["record_code"]]
            row["source_urls"] = [*row["source_urls"], ENVIRONMENT_URL]
        records.append(row)
    return records, reviews


def build_summary(records: list[dict], osm_reviews: list[dict], accessed_on: str) -> dict:
    return {
        "registry": "OVHcloud current region-location and datacenter-count registry",
        "records": len(records),
        "current_official_region_location_rows": len(records),
        "current_official_datacenter_count_checksum": sum(row["current_official_datacenter_count"] for row in records),
        "current_official_availability_zone_checksum": sum(row["current_availability_zones"] for row in records),
        "current_country_counts_by_location_row": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "current_geography_datacenter_counts": {
            geography: sum(row["current_official_datacenter_count"] for row in records if row["geography"] == geography)
            for geography in sorted({row["geography"] for row in records})
        },
        "FY2025_directly_held_datacenter_checksum": sum(row["FY2025_directly_held_datacenter_count"] for row in records),
        "FY2025_earlier_datacenter_headline": 44,
        "FY2025_earlier_site_headline": 18,
        "current_minus_FY2025_datacenter_headline": 2,
        "locations_with_site_environmental_measurements": len(ENVIRONMENTAL_FY2025),
        "related_OSM_objects": len(osm_reviews),
        "raw_current_OVHcloud_operator_tagged_OSM_objects": sum(row["osm_operator"] == "OVHcloud" for row in osm_reviews),
        "raw_legacy_OVH_operator_tagged_OSM_objects": sum(row["osm_operator"] in {"OVH", "OVH GmbH", "OVH Sp. z o.o."} for row in osm_reviews),
        "raw_name_only_OSM_objects": sum(bool(row["osm_name"]) and not row["osm_operator"] for row in osm_reviews),
        "exact_facility_code_OSM_matches": sum(row["disposition"].startswith("exact_facility_code") for row in osm_reviews),
        "location_or_campus_OSM_evidence_not_exact_current_building_census": sum(not row["disposition"].startswith("exact_facility_code") for row in osm_reviews),
        "osm_reviews": sorted(osm_reviews, key=lambda row: row["osm_object_id"]),
        "portfolio_context": PORTFOLIO_CONTEXT,
        "FY2025_environmental_group": {
            "directly_held_datacenter_energy_GWh": 516,
            "average_PUE": 1.24,
            "average_WUE_L_per_kWh": 0.34,
            "renewable_energy_GWh": 515,
            "renewable_source_energy_rate_percent": 100,
            "total_water_withdrawal_m3": 128522,
            "water_withdrawal_in_high_water_stress_areas_m3": 42821,
            "boundary": "Site table covers nine directly operated locations; Beauharnois values are extrapolated from BHS8 and water metrics exclude BHS1-7. Shared facilities and several directly held sites lack site rows.",
        },
        "FY2025_financial_snapshot_EUR_million": {
            "revenue": 1084.6,
            "adjusted_EBITDA": 437.8,
            "accounting_operating_income_EBIT": 69.4,
            "net_income": 0.4,
            "net_operating_cash_flow": 419.0,
            "unlevered_free_cash_flow": 57.6,
            "capex_excluding_business_acquisitions": 361.4,
            "datacenter_capex": 271.1,
            "net_debt_excluding_leases": 1102.8,
        },
        "H1_FY2026_financial_snapshot_EUR_million": {
            "revenue": 555.3,
            "adjusted_EBITDA": 227.2,
            "accounting_operating_income_EBIT": 35.4,
            "net_income": 5.9,
            "capex_excluding_acquisitions": 238.5,
            "unlevered_free_cash_flow": 32.3,
            "net_debt_excluding_leases": 1125,
        },
        "official_sources": [REGIONS_URL, DATACENTER_URL, URD_2025_URL, ENVIRONMENT_URL, GPU_URL, GPU_LOCATION_URL, SMART_COOLING_URL, H1_FY2026_URL, Q3_FY2026_URL],
        "records_sha256": canonical_hash(records),
        "comparison_boundary": PORTFOLIO_CONTEXT["comparison_boundary"],
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/ovhcloud_official_location_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/ovhcloud_official_location_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, osm_reviews = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
