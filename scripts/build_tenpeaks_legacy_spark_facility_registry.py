#!/usr/bin/env python3
"""Build a scope-safe TenPeaks and legacy Spark NZ data-centre registry.

TenPeaks launched in 2026 after Spark transferred eleven facilities into a
standalone company.  The current site publishes campus, metro and edge labels,
not an exact legal-asset schedule.  This builder therefore preserves the
provider's eleven-facility headline, a plausible but unconfirmed component
reconciliation, historical Spark rosters, capacity vintages, the ownership
transaction and legacy OSM labels without inventing a current building census,
live IT load, as-built equipment bill or GPU inventory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


TENPEAKS_HOME = "https://tenpeaks.co.nz/"
TENPEAKS_DATA_CENTRES = "https://tenpeaks.co.nz/data-centres"
TENPEAKS_SOUTH = "https://tenpeaks.co.nz/data-centres/south"
TENPEAKS_CENTRAL = "https://tenpeaks.co.nz/data-centres/central"
TENPEAKS_NORTH = "https://tenpeaks.co.nz/data-centres/north"
TENPEAKS_SOLUTIONS = "https://tenpeaks.co.nz/solutions"
TENPEAKS_SUSTAINABILITY = "https://tenpeaks.co.nz/sustainability"
TENPEAKS_ABOUT = "https://tenpeaks.co.nz/about"
NZX_COMPLETION = "https://www.nzx.com/announcements/466723"
OIO_DECISION = "https://www.linz.govt.nz/our-work/overseas-investment-regulation/decisions/2025-11/202500523"
SPARK_FY23_RESULTS = "https://investors.sparknz.co.nz/FormBuilder/_Resource/_module/gXbeer80tkeL4nEaF-kwFA/FY23_Results_Summary_FINAL.pdf"
SPARK_FY24_PRESENTATION = "https://investors.sparknz.co.nz/DownloadFile.axd?file=Announcements%2FNZX%2F20240823%2F425426.pdf"
SPARK_FY24_ANNUAL = "https://investors.sparknz.co.nz/FormBuilder/_Resource/_module/gXbeer80tkeL4nEaF-kwFA/doc/2024_Spark_Annual_Report.pdf"
SPARK_FY25_RESULTS = "https://investors.sparknz.co.nz/DownloadFile.axd?file=Announcements%2FNZX%2F20250820%2F449909.pdf"
SPARK_H1_FY26 = "https://investors.sparknz.co.nz/FormBuilder/_Resource/_module/gXbeer80tkeL4nEaF-kwFA/doc/H1-FY26-Detailed-Financials.pdf"
SPARK_FY16_ESG = "https://investors.sparknz.co.nz/FormBuilder/_Resource/_module/gXbeer80tkeL4nEaF-kwFA/doc/FY16_H2/2016_ESG_Report.pdf"
LEGACY_CUSTOMER_HANDBOOK = "https://www.sparkdigital.co.nz/content/dam/sparkdigital/docs/data-centre-services/spark-data-centre-customer-handbook.pdf"


def record(
    record_id: str,
    name: str,
    market: str,
    roster_scope: str,
    lifecycle: str,
    current_operator_status: str,
    address_evidence: str,
    capacity_evidence: dict,
    power_and_backup_evidence: dict,
    cooling_and_sustainability_evidence: dict,
    source_urls: list[str],
    *,
    possible_current_facility_component: bool = False,
    overlap_group: str | None = None,
    publication_conflicts: list[str] | None = None,
    boundary: str | None = None,
) -> dict:
    return {
        "id": f"tenpeaks_{record_id}",
        "name": name,
        "country_code": "NZ",
        "market": market,
        "roster_scope": roster_scope,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "current_operator_status": current_operator_status,
        "address_evidence": address_evidence,
        "possible_current_facility_component": possible_current_facility_component,
        "component_reconciliation_overlap_group": overlap_group,
        "capacity_evidence": capacity_evidence,
        "power_and_backup_evidence": power_and_backup_evidence,
        "cooling_and_sustainability_evidence": cooling_and_sustainability_evidence,
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": publication_conflicts or [],
        "boundary": boundary or "A current map label or historical address does not establish an exact current legal asset, building, capacity, live load, utilization, equipment, GPU or financial allocation.",
        "source_urls": list(dict.fromkeys(source_urls)),
    }


CURRENT_EQUIPMENT_GAP = {
    "current_grid_feed_substation_transformer_switchgear_and_PDU": "undisclosed",
    "current_UPS_battery_topology_count_rating_OEM_chemistry_and_runtime": "undisclosed",
    "current_generator_count_rating_OEM_fuel_and_runtime": "undisclosed",
    "current_as_built_single_line_diagram": "undisclosed",
}


FACILITY_EVIDENCE = [
    record(
        "south_takanini_pod_1",
        "South Takanini Pod 1",
        "Auckland",
        "current_provider_campus_component_reconciliation_candidate",
        "operating",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current site identifies Takanini; the 2022 Spark handbook historically used 23 Popes Road.",
        {"shared_campus_current_capacity_mw": 12.3, "shared_campus_operating_pods": 2, "shared_value_do_not_sum_across_pods": True},
        CURRENT_EQUIPMENT_GAP,
        {"newest_Takanini_data_centre_achieved_PUE_below": 1.2, "historical_design": "free_air_cooling_and_liquid_cooling_flexibility"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_SOUTH, TENPEAKS_SUSTAINABILITY, SPARK_FY24_PRESENTATION, SPARK_FY24_ANNUAL, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
        overlap_group="south_current_12_3MW_two_pods",
        boundary="The 12.3 MW is a shared current campus value across Pods 1 and 2 and must not be assigned to or summed for this pod. The historical street address has not been republished on the current TenPeaks page.",
    ),
    record(
        "south_takanini_pod_2",
        "South Takanini Pod 2",
        "Auckland",
        "current_provider_campus_component_reconciliation_candidate",
        "operating_and_recent_expansion_fully_leased",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current site identifies Takanini; the 2022 Spark handbook historically used 23 Popes Road.",
        {"shared_campus_current_capacity_mw": 12.3, "shared_campus_operating_pods": 2, "shared_value_do_not_sum_across_pods": True},
        CURRENT_EQUIPMENT_GAP,
        {"newest_Takanini_data_centre_achieved_PUE_below": 1.2, "historical_FY25_renewable_exception": "Pod_2_not_yet_matched_at_disclosure_date"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_SOUTH, TENPEAKS_SUSTAINABILITY, SPARK_FY25_RESULTS, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
        overlap_group="south_current_12_3MW_two_pods",
        boundary="The 12.3 MW is a shared current campus value across Pods 1 and 2. Fully leased describes the recent expansion and does not disclose energized, utilized or actual IT load.",
    ),
    record(
        "central_mayoral_drive",
        "Central Campus - Mayoral Drive Exchange",
        "Auckland",
        "current_provider_named_central_campus_building",
        "operating",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Mayoral Drive building is current; an exact current street number is not disclosed on the reviewed TenPeaks page.",
        {"shared_campus_total_potential_capacity_mw": 19, "proposed_additional_capacity_mw": 15, "historical_FY2024_Aotea_built_mw": 2.9, "shared_values_do_not_sum_across_buildings": True},
        CURRENT_EQUIPMENT_GAP,
        {"current_campus_design_alignment": "TIA_942_C_Rating_3", "measured_building_PUE_WUE": "undisclosed"},
        [TENPEAKS_CENTRAL, SPARK_FY24_ANNUAL, SPARK_FY25_RESULTS],
        possible_current_facility_component=True,
        overlap_group="central_campus_shared_capacity",
        boundary="The 19 MW is total potential campus capacity, including a proposed additional 15 MW, and is not current Mayoral Drive capacity. Historical Aotea built MW is not allocated between the two buildings.",
    ),
    record(
        "central_airedale_exchange",
        "Central Campus - Airedale Exchange",
        "Auckland",
        "current_provider_named_central_campus_building",
        "operating",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current building name; the 2022 Spark handbook historically used 31 Airedale Street.",
        {"shared_campus_total_potential_capacity_mw": 19, "proposed_additional_capacity_mw": 15, "historical_FY2024_Aotea_built_mw": 2.9, "shared_values_do_not_sum_across_buildings": True},
        CURRENT_EQUIPMENT_GAP,
        {"current_campus_design_alignment": "TIA_942_C_Rating_3", "measured_building_PUE_WUE": "undisclosed"},
        [TENPEAKS_CENTRAL, SPARK_FY24_ANNUAL, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
        overlap_group="central_campus_shared_capacity",
        boundary="The current page names Airedale Exchange, but the street address is retained only as historical handbook evidence. Campus potential and historical built MW are not building-level capacity.",
    ),
    record(
        "albany",
        "Albany",
        "Auckland",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Albany; exact current address and building count are undisclosed.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, SPARK_FY23_RESULTS],
        possible_current_facility_component=True,
        boundary="Two nearby name-only OSM building footprints do not prove whether Albany is one or two current facilities.",
    ),
    record(
        "hamilton",
        "Hamilton",
        "Hamilton",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Hamilton; the 2022 handbook historically used 7 Caro Street, while a 2024 partnership added management and investment at the University of Waikato facility.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"FY25_renewable_exception": "University_of_Waikato_recent_addition_not_yet_matched_at_disclosure_date", "cooling_and_PUE": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_ABOUT, SPARK_FY24_ANNUAL, SPARK_FY25_RESULTS, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
        publication_conflicts=["The current Hamilton map label does not specify whether it is Caro Street, the University of Waikato facility, or a portfolio grouping covering both."],
    ),
    record(
        "upper_hutt",
        "Upper Hutt / legacy Trentham",
        "Wellington",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Upper Hutt; TenPeaks timeline says Trentham opened in May 2012, but no exact current address bridge is published.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_ABOUT],
        possible_current_facility_component=True,
        publication_conflicts=["The current Upper Hutt label is likely related to legacy Trentham, but the provider does not explicitly publish a current identity bridge."],
    ),
    record(
        "wellington_central",
        "Wellington Central",
        "Wellington",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Central; the 2022 handbook historically used 60-70 Featherston Street.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
    ),
    record(
        "christchurch_west",
        "Christchurch West / legacy Christchurch Airport candidate",
        "Christchurch",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names West; the timeline says Christchurch Airport opened in August 2013 and the 2022 handbook historically used 18 Perimeter Road.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"historical_FY16_CCL_Christchurch_evidence": "artesian_free_cooling", "current_cooling_and_PUE": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_ABOUT, SPARK_FY16_ESG, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
        publication_conflicts=["The current West label, legacy Christchurch Airport name, historical address and nearby Spark-labelled OSM footprint are strong candidates but lack an explicit current provider bridge."],
    ),
    record(
        "christchurch_central",
        "Christchurch Central",
        "Christchurch",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Central; exact current address is undisclosed.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, SPARK_FY23_RESULTS],
        possible_current_facility_component=True,
    ),
    record(
        "dunedin",
        "Dunedin",
        "Dunedin",
        "current_provider_map_metro_location",
        "operating_map_label",
        "TenPeaks_current_operator_after_2026_01_30_transfer",
        "Current map names Dunedin; the 2022 handbook historically used 18 Tennyson Street.",
        {"facility_capacity_mw": "undisclosed", "rack_count": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [TENPEAKS_DATA_CENTRES, LEGACY_CUSTOMER_HANDBOOK],
        possible_current_facility_component=True,
    ),
    record(
        "north_development",
        "North Data Centre Campus",
        "Auckland",
        "current_provider_development_page",
        "coming_soon_pre_operation",
        "TenPeaks_development",
        "North-East zone; exact address undisclosed.",
        {"initial_potential_capacity_mw": 40, "expansion_potential_mw_more_than": 80, "site_hectares": 4, "adjacent_area_rights": "similar_size", "resource_consent_approved": "2024-06", "power_secured_provider_statement": True},
        {**CURRENT_EQUIPMENT_GAP, "planned_behind_the_meter_solar_mw": "5_to_7"},
        {"planned_waste_heat_reuse": "adjacent_surf_lagoon", "flood_and_seismic_due_diligence": "exceeds_Tier_3_TIA_requirements"},
        [TENPEAKS_DATA_CENTRES, TENPEAKS_NORTH, TENPEAKS_SUSTAINABILITY, TENPEAKS_ABOUT, SPARK_FY25_RESULTS],
        boundary="All MW, solar, heat-reuse and resilience statements are development potential or design evidence. North is explicitly coming soon and is excluded from current operating capacity and the eleven-facility headline.",
    ),
    record(
        "south_pod_3_development",
        "South Takanini Pod 3",
        "Auckland",
        "current_provider_development_component",
        "consented_pre_operation",
        "TenPeaks_development",
        "South Takanini campus; exact component boundary undisclosed.",
        {"additional_potential_capacity_mw": 15, "historical_target_first_stage": "FY2028"},
        CURRENT_EQUIPMENT_GAP,
        {"target_new_build_standard": "LEED", "actual_PUE_WUE": "not_operating"},
        [TENPEAKS_SOUTH, SPARK_FY25_RESULTS],
        boundary="The 15 MW is consented planned capacity, not operating, energized, customer-accepted, leased, utilized or billed load.",
    ),
    record(
        "south_pods_4_5_development",
        "South Takanini Pods 4 and 5",
        "Auckland",
        "current_provider_development_components",
        "planned_pre_operation",
        "TenPeaks_development",
        "South Takanini campus and additional contracted land; exact parcel and component boundary undisclosed.",
        {"future_expansion_capacity_mw_more_than": 50, "historical_contracted_land_hectares": 2.6},
        CURRENT_EQUIPMENT_GAP,
        {"actual_PUE_WUE": "not_operating"},
        [TENPEAKS_SOUTH, SPARK_FY25_RESULTS],
        boundary="The more-than-50-MW statement is future expansion potential across two pods and must not be added to current operating capacity.",
    ),
    record(
        "central_15MW_development",
        "Central Campus proposed multi-level data centre",
        "Auckland",
        "current_provider_development_component",
        "design_and_site_planning_pre_operation",
        "TenPeaks_development",
        "Central Auckland campus; exact building parcel undisclosed.",
        {"proposed_additional_capacity_mw": 15, "total_campus_potential_capacity_mw": 19},
        CURRENT_EQUIPMENT_GAP,
        {"design_alignment": "Tier_3_TIA_942_C_Rating_3", "actual_PUE_WUE": "not_operating"},
        [TENPEAKS_CENTRAL],
        boundary="The 15 MW and 19 MW are proposed additional and total potential capacity, not current live capacity and not additive to each other.",
    ),
    record(
        "papakura_historical",
        "Papakura historical Spark handbook facility",
        "Auckland",
        "historical_2022_handbook_label_not_on_current_TenPeaks_map",
        "current_status_unresolved",
        "legacy_Spark_label_current_TenPeaks_inclusion_not_confirmed",
        "Historical handbook address: 40 O'Shannessey Street.",
        {"capacity_mw": "undisclosed", "racks": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [LEGACY_CUSTOMER_HANDBOOK, TENPEAKS_DATA_CENTRES, SPARK_FY23_RESULTS],
    ),
    record(
        "tauranga_historical",
        "Tauranga historical Spark handbook facility",
        "Tauranga",
        "historical_2022_handbook_label_not_on_current_TenPeaks_map",
        "current_status_unresolved",
        "legacy_Spark_label_current_TenPeaks_inclusion_not_confirmed",
        "Historical handbook address: Level 1, 570 Cameron Road.",
        {"capacity_mw": "undisclosed", "racks": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [LEGACY_CUSTOMER_HANDBOOK, TENPEAKS_DATA_CENTRES, SPARK_FY23_RESULTS],
    ),
    record(
        "nelson_historical",
        "Nelson historical Spark edge location",
        "Nelson",
        "historical_FY2023_edge_location_not_on_current_TenPeaks_map",
        "current_status_unresolved",
        "legacy_Spark_label_current_TenPeaks_inclusion_not_confirmed",
        "Exact historical and current address undisclosed in reviewed investor material.",
        {"capacity_mw": "undisclosed", "racks": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [SPARK_FY23_RESULTS, TENPEAKS_DATA_CENTRES],
    ),
    record(
        "invercargill_historical",
        "Invercargill historical Spark edge location",
        "Invercargill",
        "historical_FY2023_edge_location_not_on_current_TenPeaks_map",
        "current_status_unresolved",
        "legacy_Spark_label_current_TenPeaks_inclusion_not_confirmed",
        "Exact historical and current address undisclosed in reviewed investor material.",
        {"capacity_mw": "undisclosed", "racks": "undisclosed"},
        CURRENT_EQUIPMENT_GAP,
        {"cooling_PUE_WUE_and_water": "undisclosed"},
        [SPARK_FY23_RESULTS, TENPEAKS_DATA_CENTRES],
    ),
]


OSM_CROSSWALK = {
    "osm_way_1480092702": ("tenpeaks_albany", "name_only_Albany_building_candidate_one_of_two_nearby_footprints"),
    "osm_way_318922364": ("tenpeaks_albany", "name_only_Albany_building_candidate_one_of_two_nearby_footprints"),
    "osm_way_444102062": ("tenpeaks_south_takanini_pod_1", "legacy_Spark_Takanini_campus_footprint_exact_pod_mapping_unresolved"),
    "osm_way_243876089": ("tenpeaks_central_airedale_exchange", "exact_current_named_Central_campus_building_candidate"),
    "osm_way_24238369": ("tenpeaks_central_mayoral_drive", "exact_current_named_Central_campus_building_candidate"),
    "osm_way_243876090": (None, "Central_campus_sub_footprint_exact_Mayoral_or_Airedale_assignment_unresolved"),
    "osm_way_292861387": (None, "Central_campus_sub_footprint_exact_Mayoral_or_Airedale_assignment_unresolved"),
    "osm_way_292861441": (None, "Central_campus_sub_footprint_exact_Mayoral_or_Airedale_assignment_unresolved"),
    "osm_way_409891677": ("tenpeaks_christchurch_west", "legacy_Spark_Christchurch_Airport_or_West_candidate_exact_current_bridge_unresolved"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [
        {"object_type": "DataCenterFacilityCampusComponentOrHistoricalEvidence", "source_order": order, "accessed_on": accessed_on, **item}
        for order, item in enumerate(FACILITY_EVIDENCE, 1)
    ]
    assert len(rows) == 19
    assert len({row["id"] for row in rows}) == len(rows)
    candidates = [row for row in rows if row["possible_current_facility_component"]]
    assert len(candidates) == 11
    assert sum(row["id"].startswith("tenpeaks_south_takanini") for row in candidates) == 2
    assert sum(row["id"].startswith("tenpeaks_central_") for row in candidates) == 2
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_candidate_ref": facility_ref,
            "classification": classification,
            "capacity_counting_rule": "An OSM footprint is a legacy public-map crosswalk, not a current operator, ownership, facility-count, MW, utilization, revenue or GPU record.",
        })
    assert len(rows) == 9
    assert sum(row["raw_operator"] == "Spark New Zealand" for row in rows) == 6
    assert sum(row["raw_operator"] == "Spark" for row in rows) == 1
    assert sum(row["raw_operator"] is None for row in rows) == 2
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    candidates = [row for row in records if row["possible_current_facility_component"]]
    sources = list(dict.fromkeys([
        TENPEAKS_HOME, TENPEAKS_DATA_CENTRES, TENPEAKS_SOUTH,
        TENPEAKS_CENTRAL, TENPEAKS_NORTH, TENPEAKS_SOLUTIONS,
        TENPEAKS_SUSTAINABILITY, TENPEAKS_ABOUT, NZX_COMPLETION,
        OIO_DECISION, SPARK_FY23_RESULTS, SPARK_FY24_PRESENTATION,
        SPARK_FY24_ANNUAL, SPARK_FY25_RESULTS, SPARK_H1_FY26,
        SPARK_FY16_ESG, LEGACY_CUSTOMER_HANDBOOK,
        *[url for row in records for url in row["source_urls"]],
    ]))
    return {
        "id": "tenpeaks_legacy_spark_facility_summary_2026_07_19",
        "current_operator": "TenPeaks_Data_Centres",
        "legal_entity": "TenPeaks_Limited",
        "legacy_operator": "Spark_New_Zealand",
        "accessed_on": accessed_on,
        "ownership_and_transaction": {
            "completion_date": "2026-01-30",
            "assets_and_operations_transferred_to": "TenPeaks_Data_Centres",
            "Pacific_Equity_Partners_Secure_Assets_Fund_interest_percent": 75,
            "Spark_New_Zealand_retained_interest_percent": 25,
            "Spark_board_seats": 2,
            "Spark_status": "minority_shareholder_key_customer_and_service_partner",
            "headline_enterprise_value_NZD_million_up_to": 705,
            "base_enterprise_value_NZD_million": 575,
            "earnout_enterprise_value_NZD_million_up_to": 130,
            "initial_cash_proceeds_NZD_million": 453,
            "deferred_cash_proceeds_NZD_million_up_to_approximately": 98,
            "FY2025_transaction_perimeter_pro_forma_EBITDA_NZD_million": 22.9,
            "announced_transaction_multiple_x": 30.8,
            "OIO_consent_allowed_PEP_managed_funds_to_increase_to_percent": 100,
            "evidence_of_consent_option_exercised": False,
            "boundary": "OIO consent permission is not evidence that Spark sold its retained 25 percent. Transaction value, cash proceeds and earnout are not TenPeaks revenue, operating profit or market capitalization.",
        },
        "current_portfolio_headline": {
            "facilities": 11,
            "operating_capacity_mw_more_than": 23,
            "racks_more_than": 2500,
            "development_pipeline_mw_more_than": 130,
            "customers_approximately_at_FY2025": 270,
            "current_provider_map_operating_location_labels": ["South_Takanini", "Central_Aotea", "Albany", "Hamilton", "Upper_Hutt", "Wellington_Central", "Christchurch_West", "Christchurch_Central", "Dunedin"],
            "current_provider_map_development_labels": ["North_Auckland"],
            "boundary": "The current site discloses eleven facilities but maps nine operating location labels plus North as coming soon. A legal-asset and exact building schedule is not published.",
        },
        "eleven_facility_component_reconciliation_candidate": {
            "candidate_count": len(candidates),
            "candidate_ids": [row["id"] for row in candidates],
            "logic": "two operating South pods plus two named Central buildings plus seven other operating map locations",
            "official_one_to_one_bridge_published": False,
            "counting_conflicts": ["Albany_has_two_name_only_OSM_footprints", "Central_has_three_additional_OSM_sub_footprints", "Hamilton_may_span_Caro_Street_and_University_of_Waikato", "Christchurch_West_to_Airport_identity_not_explicit"],
            "boundary": "The arithmetic reconciles to eleven but remains an analytical candidate, not an asserted current legal facility roster.",
        },
        "capacity_vintages": {
            "FY2024_built_mw": 22.3,
            "FY2024_breakdown_mw": {"Takanini": 12.3, "Aotea": 2.9, "other_sites": 7.1},
            "FY2025_built_mw": 23,
            "FY2025_contracted_utilisation_percent": 88,
            "H1_FY2026_contracted_utilisation_dedicated_data_centres_percent": 87,
            "South_current_mw_across_two_pods": 12.3,
            "South_total_potential_mw_more_than": 75,
            "Central_total_potential_mw": 19,
            "North_initial_potential_mw": 40,
            "North_expansion_potential_mw_more_than": 80,
            "boundary": "Built, current operating headline, contracted utilization, campus potential and development pipeline use different dates and denominators and are not summed.",
        },
        "power_cooling_and_sustainability": {
            "newest_Takanini_achieved_PUE_below": 1.2,
            "H1_FY2026_target_PUE": 1.2,
            "H1_FY2026_legacy_data_centre_PUE": 1.61,
            "H1_FY2026_estimated_data_centre_electricity_cost_NZD_million": 4,
            "historical_Takanini_passive_cooling_share_percent": 95,
            "historical_Mayoral_Drive_Vigilent_expected_saving_kWh_per_year": 517000,
            "historical_Mayoral_Drive_expected_tCO2e_saving_per_year": 274,
            "Takanini_current_design_evidence": ["free_air_cooling", "liquid_cooling_flexibility", "closed_loop_or_air_based_future_design_preference"],
            "ten_year_Genesis_renewable_partnership_announced": "2024-05",
            "FY25_expected_100_percent_matched_renewable_from_FY26_with_disclosed_exceptions": ["Takanini_Pod_2", "University_of_Waikato_recent_addition"],
            "current_independently_verified_hourly_matching": False,
            "North_planned_behind_meter_solar_mw": "5_to_7",
            "North_planned_waste_heat_reuse": "surf_lagoon",
            "exact_current_per_site_power_and_cooling_BOM": "undisclosed",
            "boundary": "Historical engineering, current portfolio targets, one newest-site PUE claim and future designs do not form a current per-site as-built equipment or measured environmental ledger.",
        },
        "accelerator_and_AI_boundary": {
            "Takanini_FY2024_description": "equipped_for_high_density_AI_requirements",
            "liquid_cooling_flexibility": True,
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "customer_or_hyperscaler_hardware_not_operator_inventory": True,
            "accelerator_ledger_action": "no_numeric_physical_inventory_row_created",
        },
        "historical_roster_boundary": {
            "FY2023_sites": 16,
            "FY2023_hyperscale_locations": ["Auckland_Takanini", "additional_Auckland_campus_planned"],
            "FY2023_carrier_hotel": ["Auckland_CBD_Aotea_Mayoral_Drive", "Auckland_CBD_Aotea_Airedale"],
            "FY2023_metro_counts": {"Auckland": 2, "Wellington": 2, "Christchurch": 4},
            "FY2023_edge_locations": ["Hamilton", "Tauranga", "Nelson", "Dunedin", "Invercargill"],
            "historical_2022_handbook_addresses_recovered_from_currently_missing_official_PDF_index": 8,
            "historical_labels_not_on_current_map": ["Papakura", "Tauranga", "Nelson", "Invercargill"],
            "boundary": "The historical 16-site and address rosters predate the eleven-facility transaction and are not treated as current TenPeaks assets. The old handbook URL currently returns 404, so its indexed addresses remain historical evidence only.",
        },
        "financial_boundary": {
            "FY2025_pre_sale_data_centre_business_NZD_million": {"revenue": 50, "prior_revenue": 45, "gross_margin": 47, "prior_gross_margin": 43, "derived_gross_margin_percent": 94},
            "H1_FY2026_discontinued_operation_NZD_million": {"revenue": 24, "prior_revenue": 23, "gross_margin": 24, "prior_gross_margin": 23, "EBITDAI": 14, "prior_EBITDAI": 13, "net_earnings": 10, "prior_net_earnings": 4, "strategic_data_centre_capex": 54, "prior_capex": 14},
            "H1_FY2026_WALE_years_with_options": 14.4,
            "H1_FY2026_prior_WALE_years": 15.4,
            "FY2025_global_cloud_provider_share_of_data_centre_revenue_percent": 30,
            "FY2025_historical_customer_churn_percent_below": 1.5,
            "transaction_perimeter_FY2025_pro_forma_EBITDA_NZD_million": 22.9,
            "current_post_close_TenPeaks_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_and_ROIC": "undisclosed",
            "boundary": "FY2025 Spark business results, H1 FY2026 discontinued-operation results and transaction-perimeter pro forma EBITDA have different scopes. No implied EBITDA margin is calculated, and Spark Group earnings are not assigned to TenPeaks.",
        },
        "public_parent_look_through": {
            "Spark_interest_percent": 25,
            "FY2025_adjusted_group_NZD_million": {"revenue": 3700, "EBITDAI": 1060, "net_profit_after_tax": 227, "capex": 429, "free_cash_flow": 330},
            "FY2025_group_net_debt_NZD_million": 1475,
            "FY2025_group_net_debt_to_EBITDA_x": 2.2,
            "H1_FY2026_continuing_NZD_million": {"revenue": 1893, "EBITDAI": 448, "net_profit_after_tax": 64, "BAU_capex": 217, "free_cash_flow": 107},
            "boundary": "Spark is a diversified listed telecom and a 25-percent TenPeaks minority holder; group revenue, profit, debt and cash flow are not TenPeaks financials or pure data-centre exposure.",
        },
        "OSM_crosswalk": {
            "Spark_New_Zealand_operator_objects": sum(row["raw_operator"] == "Spark New Zealand" for row in osm_rows),
            "Spark_operator_objects": sum(row["raw_operator"] == "Spark" for row in osm_rows),
            "name_only_Spark_Data_Centre_objects": sum(row["raw_operator"] is None for row in osm_rows),
            "related_objects": len(osm_rows),
            "objects_joined_to_candidate_records": sum(row["facility_candidate_ref"] is not None for row in osm_rows),
            "Central_campus_OSM_footprints": 5,
            "Albany_OSM_footprints": 2,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "OSM retains legacy Spark labels after the transfer, contains multiple footprints within Central and Albany, and omits most current map locations. It is not a current operator roster or capacity census.",
        },
        "outlook": {
            "positive_signals": [
                "more_than_23MW_current_capacity_and_more_than_2500_racks",
                "87_to_88_percent_contracted_utilisation_and_near_full_Takanini_pods",
                "approximately_270_customers_low_historical_churn_and_long_cloud_contract_WALE",
                "130MW_plus_development_pipeline_across_three_strategic_Auckland_campuses",
                "PEP_funding_pathway_with_Spark_as_25_percent_owner_key_customer_and_service_partner",
                "newest_Takanini_PUE_below_1_2_and_ten_year_renewable_partnership",
            ],
            "risk_signals": [
                "30_8x_headline_transaction_multiple_includes_earnout_and_requires_execution",
                "130MW_plus_pipeline_is_not_built_and_requires_capex_grid_permits_customers_and_delivery",
                "post_close_standalone_financials_and_site_economics_not_public",
                "exact_current_eleven_facility_legal_roster_not_public",
                "legacy_PUE_1_61_highlights_mixed_efficiency_across_the_portfolio",
                "H1_FY2026_contracted_utilisation_down_one_point_and_WALE_down_one_year",
                "no_physical_GPU_inventory_or_GPU_economics",
                "Spark_equity_exposure_is_a_25_percent_associate_not_control_or_a_pure_play",
            ],
            "analytical_view": "TenPeaks begins with a highly contracted national platform, strong customer-retention indicators and a large Auckland pipeline, while PEP capital and Spark's continuing relationship can support growth. The valuation is demanding, most future MW is not built, legacy efficiency is mixed, and current standalone earnings, leverage, exact assets, live load, equipment and GPU inventory remain undisclosed.",
        },
        "remaining_material_gaps": [
            "exact_current_eleven_facility_legal_asset_building_address_ownership_lease_and_lifecycle_roster",
            "historical_sixteen_site_and_current_eleven_facility_transition_bridge",
            "per_site_operating_energized_leased_utilized_billed_and_actual_IT_load",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_and_cooling_as_built_BOM",
            "per_site_measured_PUE_WUE_absolute_water_energy_hourly_renewable_matching_and_live_liquid_cooled_MW",
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin",
            "post_close_standalone_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_site_economics_and_ROIC",
            "exact_current_PE_fund_beneficial_ownership_and_any_future_exercise_of_100_percent_consent",
            "exact_current_TIA_or_Uptime_awards_identifiers_types_scope_and_expiry",
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
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "tenpeaks_legacy_spark_facility_registry.jsonl"
    summary_path = args.output_dir / "tenpeaks_legacy_spark_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
