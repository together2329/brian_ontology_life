#!/usr/bin/env python3
"""Build a scope-safe Selectel facility and service-location registry.

Selectel publishes exact totals for six current own data-center facilities, but
its cloud-location documentation also names partner facilities and fault-domain
constructs.  This builder preserves those scopes, historical engineering
snapshots, the unconfirmed Yurlovsky development, and public-map conflicts
without turning them into a false operating-facility, IT-load or GPU census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


DATA_CENTERS = "https://selectel.ru/about/data-centers/"
LOCATIONS = "https://docs.selectel.ru/en/infrastructure/locations/"
TSVETOCHNAYA_2_2015 = "https://selectel.ru/blog/tcvetochnaya-2/"
TSVETOCHNAYA_2_ENGINEERING = "https://selectel.ru/blog/datacenter-cvt2/"
COOLING = "https://selectel.ru/blog/free-cooling-details/"
FACILITY_ENGINEERING = "https://selectel.ru/blog/data-center/"
BERZARINA_HISTORICAL = "https://selectel.ru/blog/kak-eto-rabotaet-data-centr-berzarina/"
BERZARINA_2 = "https://selectel.ru/about/newsroom/press/novyi-cod-selectel-v-moskve/"
YURLOVSKY = "https://selectel.ru/about/newsroom/press/selectelselectel-pristupila-k-stroitelstvu-v-moskve-novogo-20-mvt-data-centra-na-2-tys-stoek/"
H1_2025 = "https://selectel.ru/about/newsroom/news/selectel-obyavlyaet-finansovye-rezultaty-po-itogam-1-polugodiya-2025-vyruchka-sostavila-89-mlrd-rublej-uvelichivshis-na-46-god-k-godu/"
GPU_DOCS = "https://docs.selectel.ru/en/cloud-servers/create/gpus/"
B300 = "https://selectel.ru/about/newsroom/news/novye-videokarty-nvidia-b300-dlya-krupnomasshtabnyh-ai-nagruzok-stali-dostupny-v-selectel/"
AI_SERVER = "https://selectel.ru/about/newsroom/news/selectel-obyavil-o-zapuske-sobstvennogo-vysokoproizvoditelnogo-ai-servera/"
AI_JV = "https://selectel.ru/about/newsroom/news/selectel-investiruet-bolee-1-mlrd-v-sovmestnoe-predpriyatie-s-itmo-dlya-razvitiya-ai-servisov/"
IFRS_2025 = "https://investors.selectel.ru/wp-content/uploads/2026/03/Selectel_IFRS_Cons_FS.pdf"
Q1_2026 = "https://investors.selectel.ru/wp-content/uploads/2026/05/3m-2026_Selectel_Financial-results_Press-release.pdf"
TIER5 = "https://selectel.ru/about/newsroom/news/investicionnyj-fond-tier-5-priobrel-25-provajdera-it-infrastruktury-selectel/"
CATALYSTIC = "https://interros.ru/press/news/sovmestnoe-predpriyatie-interrosa-i-t-tekhnologiy-pokupaet-dolyu-v-krupneyshem-nezavisimom-rossiysko/"
UPTIME_RUSSIA = "https://uptimeinstitute.com/uptime-institute-awards/country/id/RU"


def record(
    record_id: str,
    name: str,
    city: str,
    address: str,
    roster_scope: str,
    lifecycle: str,
    ownership_or_operating_status: str,
    published_metrics: dict,
    electrical_and_backup: dict,
    cooling: dict,
    source_urls: list[str],
    product_location_codes: list[str] | None = None,
    publication_conflicts: list[str] | None = None,
    boundary: str | None = None,
    country_code: str = "RU",
) -> dict:
    return {
        "id": f"selectel_{record_id}",
        "name": name,
        "country_code": country_code,
        "city": city,
        "address": address,
        "roster_scope": roster_scope,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "ownership_or_operating_status": ownership_or_operating_status,
        "product_location_codes": product_location_codes or [],
        "published_metrics": published_metrics,
        "electrical_and_backup_power_evidence": electrical_and_backup,
        "cooling_evidence": cooling,
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": publication_conflicts or [],
        "boundary": boundary or "A named service location does not establish building ownership, rack capacity, IT load, actual draw, utilization, site economics or GPU inventory.",
        "source_urls": list(dict.fromkeys(source_urls)),
    }


CURRENT_COMMON_POWER = {
    "UPS": "present_exact_current_count_rating_topology_battery_chemistry_and_runtime_undisclosed",
    "diesel_generators": "present_and_load_tested_exact_current_count_rating_OEM_fuel_and_runtime_undisclosed",
}


FACILITY_EVIDENCE = [
    record(
        "tsvetochnaya_1",
        "Tsvetochnaya 1",
        "Saint_Petersburg",
        "21 Tsvetochnaya Street, litera A, Saint Petersburg",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 679, "racks": 227, "connected_power_mw": 3},
        CURRENT_COMMON_POWER,
        {"technology": "freon_direct_expansion_precision_air_conditioning", "current_portfolio_redundancy_statement": "N_plus_2"},
        [DATA_CENTERS, LOCATIONS, COOLING, FACILITY_ENGINEERING],
        ["SPB-1"],
        boundary="The 3-MW term is connected power on the current facility card, not IT load or actual draw. The nearby OSM building and Tsvetochnaya 1 node overlap and are not two data centers.",
    ),
    record(
        "tsvetochnaya_2",
        "Tsvetochnaya 2",
        "Saint_Petersburg",
        "28 Koli Tomchaka Street, litera K, Saint Petersburg",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 1885, "racks": 969, "connected_power_mw": 10, "historical_complex_area_sqm": 12000},
        {
            **CURRENT_COMMON_POWER,
            "historical_site_evidence": {
                "electrical_design": "2N",
                "independent_10_kV_lines": 2,
                "own_two_section_10_kV_distribution_substation": True,
                "per_floor_transformer_substations": "two_2500_kVA_units",
                "historical_transformer_inventory_later_article": "eight_2000_kVA_plus_two_2500_kVA",
                "UPS_cluster_article_wording": "six_400_kW_units_2N",
                "diesel_generation_redundancy": "N_plus_1",
                "diesel_start_seconds": "5_to_10",
                "fuel_runtime_hours": 48,
            },
        },
        {"technology": "chillers_and_historical_indirect_free_cooling", "current_portfolio_redundancy_statement": "N_plus_2", "historical_2015_redundancy_statement": "N_plus_1"},
        [DATA_CENTERS, LOCATIONS, TSVETOCHNAYA_2_2015, TSVETOCHNAYA_2_ENGINEERING, COOLING],
        ["SPB-2", "ru-3", "gis-2a"],
        publication_conflicts=[
            "The public facility card uses 19 Tsvetochnaya Street while the current infrastructure-location table uses the FIAS address 28 Koli Tomchaka Street, litera K.",
            "The current portfolio page states N+2 cooling while the historical 2015 engineering article states N+1; date and scope are preserved.",
        ],
        boundary="Historical transformer, UPS, diesel and fuel details are publication snapshots, not a complete current as-built bill of materials. Connected power is not IT load or actual draw.",
    ),
    record(
        "dubrovka_1",
        "Dubrovka 1",
        "Dubrovka",
        "1 Sovetskaya Street, litera A, Dubrovka, Leningrad Oblast",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 740, "racks": 424, "connected_power_mw": 2.5},
        CURRENT_COMMON_POWER,
        {"technology": "chillers", "current_portfolio_redundancy_statement": "N_plus_2"},
        [DATA_CENTERS, LOCATIONS, COOLING],
        ["SPB-4", "ru-1a"],
        boundary="The 2.5-MW connected-power card value is not IT load or actual draw.",
    ),
    record(
        "dubrovka_2",
        "Dubrovka 2",
        "Dubrovka",
        "1 Sovetskaya Street, litera B, Dubrovka, Leningrad Oblast",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 931, "racks": 291, "connected_power_mw": 2.5},
        {**CURRENT_COMMON_POWER, "diesel_generation_redundancy_historical_article": "N_plus_1"},
        {"technology": "freon_direct_expansion_precision_air_conditioning", "current_portfolio_redundancy_statement": "N_plus_2"},
        [DATA_CENTERS, LOCATIONS, COOLING, FACILITY_ENGINEERING],
        ["SPB-5", "ru-1c", "ru-9a"],
        boundary="The 2.5-MW connected-power card value is not IT load or actual draw. Historical N+1 generator wording is not a complete current generator inventory.",
    ),
    record(
        "dubrovka_3",
        "Dubrovka 3",
        "Dubrovka",
        "1 Sovetskaya Street, litera I, Dubrovka, Leningrad Oblast",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 768, "racks": 281, "connected_power_mw": 2, "published_PUE_approximately": 1.25},
        CURRENT_COMMON_POWER,
        {"technology": "direct_free_cooling_with_natural_gas_absorption_chiller_for_summer_trim", "current_portfolio_redundancy_statement": "N_plus_2"},
        [DATA_CENTERS, LOCATIONS, COOLING],
        ["SPB-3", "ru-1b"],
        boundary="The published PUE is an approximate site claim without the measurement period, load and boundary required for cross-operator ranking. Connected power is not actual IT load.",
    ),
    record(
        "berzarina",
        "Berzarina",
        "Moscow",
        "36 Berzarina Street, building 3, Moscow",
        "current_provider_enumerated_own_facility",
        "operating",
        "Selectel_own_facility_provider_statement",
        {"server_room_area_sqm": 2777, "racks": 1420, "connected_power_mw": 10, "published_PUE_approximately": 1.20},
        {
            **CURRENT_COMMON_POWER,
            "historical_original_section_evidence": {
                "independent_utility_inputs": 2,
                "UPS_OEM": "GE",
                "generator_OEM": "Gesan_with_Volvo_Penta_engines",
                "generator_peak_rating_kw_each": 504,
                "standard_fuel_runtime_hours": 10,
                "generator_command_after_seconds": 3,
                "full_mode_and_load_transfer_within_minutes": 2,
            },
            "second_phase_project_power_mw": 2.5,
        },
        {
            "current_technology": "direct_free_cooling_with_adiabatic_trim",
            "current_portfolio_redundancy_statement": "N_plus_2",
            "historical_original_section": "Uniflair_precision_cooling_and_chiller_fan_coil",
            "second_phase_publication": "ten_planned_cooling_machines_three_installed_at_publication_N_plus_1",
        },
        [DATA_CENTERS, LOCATIONS, COOLING, FACILITY_ENGINEERING, BERZARINA_HISTORICAL, BERZARINA_2],
        ["ru-2", "ru-6b", "ru-7", "gis-1a", "MSK-1", "MSK-2"],
        publication_conflicts=["The provider's current aggregate facility card, historical original section and Berzarina 2 launch article use different physical and time scopes."],
        boundary="Historical OEM, generator and second-phase facts do not establish a complete current 1,420-rack as-built BOM. One Selectel-tagged OSM node named Berzarina is far from the official address and remains an unresolved geospatial conflict.",
    ),
    record(
        "aviamotornaya",
        "Aviamotornaya",
        "Moscow",
        "69 Aviamotornaya Street, Moscow",
        "current_explicit_partner_data_center",
        "operating_service_location",
        "partner_facility_not_Selectel_owned_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [DATA_CENTERS, LOCATIONS],
        ["MSK-3"],
    ),
    record(
        "nextremum",
        "Svetlaya / Nextremum",
        "Novosibirsk",
        "21 Svetlaya Street, Kudryashovsky, Novosibirsk Oblast",
        "current_explicit_partner_data_center",
        "operating_service_location",
        "partner_facility_not_Selectel_owned_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [DATA_CENTERS, LOCATIONS],
        ["ru-8", "NSK-1"],
    ),
    record(
        "moscow_north",
        "Moscow North Data Center Group",
        "Moscow",
        "undisclosed_in_current_location_table",
        "current_product_service_location",
        "operating_service_location",
        "facility_owner_and_Selectel_tenure_undisclosed",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
    ),
    record(
        "ryabinovaya",
        "Ryabinovaya",
        "Moscow",
        "address_undisclosed_in_reviewed_location_row",
        "current_product_service_location",
        "operating_service_location",
        "facility_owner_and_Selectel_tenure_undisclosed",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
        ["ru-6c"],
    ),
    record(
        "unicon_tashkent",
        "UNICON",
        "Tashkent",
        "38 Mingbulok Street, Tashkent",
        "current_product_service_location",
        "operating_service_location",
        "third_party_named_facility_no_Selectel_ownership_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
        country_code="UZ",
    ),
    record(
        "east_telecom_tashkent",
        "East Telecom",
        "Tashkent",
        "Yangishakhar Street, Tashkent",
        "current_product_service_location",
        "operating_service_location",
        "third_party_named_facility_no_Selectel_ownership_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
        country_code="UZ",
    ),
    record(
        "kazteleport_sairam",
        "Kazteleport Sairam",
        "Almaty",
        "2A Voykova Street, Almaty",
        "current_product_service_location",
        "operating_service_location",
        "third_party_named_facility_no_Selectel_ownership_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
        country_code="KZ",
    ),
    record(
        "icolo_nbo1",
        "iColo NBO1",
        "Nairobi",
        "LRC Road off Langata South Road, Nairobi",
        "current_product_service_location",
        "operating_service_location",
        "third_party_named_facility_no_Selectel_ownership_inference",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"autonomous_power_and_redundant_communications_location_document_statement": True},
        {"autonomous_cooling_location_document_statement": True, "technology_and_capacity": "undisclosed"},
        [LOCATIONS],
        country_code="KE",
    ),
    record(
        "yurlovsky",
        "Yurlovsky",
        "Moscow",
        "Yurlovsky Proyezd area, Moscow; exact current address undisclosed",
        "announced_Selectel_development_not_in_current_operating_roster",
        "construction_or_pre_operation_current_launch_not_officially_confirmed",
        "Selectel_development_project",
        {
            "planned_racks": 2000,
            "planned_connected_power_mw": 20,
            "planned_server_capacity_up_to": 80000,
            "planned_machine_hall_area_sqm": 4500,
            "planned_average_rack_density_kw": 8,
            "planned_first_phase_year_original_statement": 2025,
        },
        {
            "planned_independent_lines": 2,
            "planned_nearby_supply_center_kV": 500,
            "planned_line_distance_m": 700,
            "planned_reliability_category": "second",
            "planned_redundancy": "six_fifths_N_per_1000_racks_five_working_clusters_plus_one_reserve",
        },
        {"planned_technology": "direct_free_cooling_with_adiabatic_mats", "target_PUE": "1.10_to_1.15"},
        [YURLOVSKY, H1_2025, DATA_CENTERS],
        publication_conflicts=["The original first-phase timing was 2025, but the current 2026 operating-facility page omits Yurlovsky and no reviewed official launch announcement confirms operation."],
        boundary="All rack, MW, server, density, cooling, PUE and Tier IV values are project targets. They are not operating, energized, accepted, leased, utilized, billed or actual-load evidence.",
    ),
]


OSM_CROSSWALK = {
    "osm_way_105594096": ("selectel_tsvetochnaya_1", "nearby_campus_building_overlaps_Tsvetochnaya_1_node_exact_phase_mapping_unresolved"),
    "osm_way_105462159": ("selectel_berzarina", "official_address_facility_candidate"),
    "osm_node_2639510695": ("selectel_tsvetochnaya_1", "named_Tsvetochnaya_1_candidate"),
    "osm_node_13068243349": (None, "Berzarina_name_but_coordinate_far_from_official_address_geospatial_conflict"),
    "osm_way_168582094": ("selectel_dubrovka_1", "named_Dubrovka_1_facility_candidate"),
    "osm_way_168582099": ("selectel_dubrovka_2", "named_Dubrovka_2_facility_candidate"),
    "osm_way_517923512": ("selectel_dubrovka_3", "named_Dubrovka_3_facility_candidate"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [
        {"object_type": "DataCenterFacilityOrServiceLocationEvidence", "source_order": order, "accessed_on": accessed_on, **item}
        for order, item in enumerate(FACILITY_EVIDENCE, 1)
    ]
    assert len(rows) == 15
    assert len({row["id"] for row in rows}) == 15
    own = [row for row in rows if row["roster_scope"] == "current_provider_enumerated_own_facility"]
    assert len(own) == 6
    assert sum(row["published_metrics"]["racks"] for row in own) == 3612
    assert sum(row["published_metrics"]["connected_power_mw"] for row in own) == 30
    assert sum(row["published_metrics"]["server_room_area_sqm"] for row in own) == 7780
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
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_candidate_ref": facility_ref,
            "classification": classification,
            "capacity_counting_rule": "An OSM object is a public-map crosswalk, not an ownership, facility-count, rack, MW, utilization, revenue or GPU record.",
        })
    assert len(rows) == 7
    assert sum(row["raw_operator"] == "Selectel" for row in rows) == 6
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    own = [row for row in records if row["roster_scope"] == "current_provider_enumerated_own_facility"]
    service = [row for row in records if row["roster_scope"] in {"current_explicit_partner_data_center", "current_product_service_location"}]
    gpu_models = [
        "NVIDIA_A100_40GB", "NVIDIA_A100_40GB_NVLink_on_request", "NVIDIA_A100_80GB",
        "NVIDIA_Tesla_T4", "NVIDIA_A30_24GB", "NVIDIA_A2_16GB", "NVIDIA_GTX_1080",
        "NVIDIA_RTX_2080_Ti", "NVIDIA_RTX_4090_24GB", "NVIDIA_RTX_4090_48GB",
        "NVIDIA_RTX_6000_Ada_48GB", "NVIDIA_A2000_6GB", "NVIDIA_A5000_24GB",
        "NVIDIA_H100_80GB", "NVIDIA_H200_141GB", "NVIDIA_L4_24GB",
        "NVIDIA_RTX_6000_Pro_documented_memory_conflict", "NVIDIA_B300_in_8_GPU_HGX_server_configuration",
    ]
    sources = list(dict.fromkeys([
        DATA_CENTERS, LOCATIONS, TSVETOCHNAYA_2_2015, TSVETOCHNAYA_2_ENGINEERING,
        COOLING, FACILITY_ENGINEERING, BERZARINA_HISTORICAL, BERZARINA_2,
        YURLOVSKY, H1_2025, GPU_DOCS, B300, AI_SERVER, AI_JV, IFRS_2025,
        Q1_2026, TIER5, CATALYSTIC, UPTIME_RUSSIA,
        *[url for row in records for url in row["source_urls"]],
    ]))
    return {
        "id": "selectel_official_facility_summary_2026_07_19",
        "operator": "AO_Selectel",
        "accessed_on": accessed_on,
        "current_own_facility_checksum": {
            "facilities": len(own),
            "racks": sum(row["published_metrics"]["racks"] for row in own),
            "connected_power_mw": sum(row["published_metrics"]["connected_power_mw"] for row in own),
            "server_room_area_sqm": sum(row["published_metrics"]["server_room_area_sqm"] for row in own),
            "cities_or_campus_groups": ["Saint_Petersburg", "Dubrovka_Leningrad_Oblast", "Moscow"],
            "boundary": "The six physical-facility cards reconcile exactly to the provider headline. Connected power is not IT load, actual draw, utilization or billed capacity.",
        },
        "roster_scope_reconciliation": {
            "current_provider_enumerated_own_physical_facilities": 6,
            "current_explicit_partner_or_other_product_service_location_records": len(service),
            "unconfirmed_development_records": 1,
            "investor_material_own_data_center_sites": 4,
            "current_product_infrastructure": {"countries": 4, "regions": 6, "availability_zones": 11, "pools": 26},
            "provider_main_page_Russia_product_scope": {"regions": 3, "availability_zones": 6, "pools": 16},
            "boundary": "The investor four-site statement likely uses a campus or platform boundary, but no exact official bridge to six physical facilities is published. Regions, availability zones and pools are service and fault-domain constructs, not buildings.",
        },
        "power_cooling_and_certification_boundary": {
            "all_six_current_facilities": "UPS_and_load_tested_diesel_generation_present",
            "current_portfolio_cooling_redundancy": "N_plus_2",
            "cooling_technologies": ["freon_direct_expansion", "chillers", "direct_free_cooling", "adiabatic_trim", "natural_gas_absorption_chiller_trim"],
            "published_site_PUE_claims": {"Dubrovka_3_approximately": 1.25, "Berzarina_approximately": 1.20},
            "network_nodes_redundancy": "N_plus_1",
            "network_carriers": 55,
            "fire_suppression": "central_autonomous_gas_Halon_125",
            "provider_reliability_wording": "six_facilities_correspond_to_Tier_III",
            "exact_Selectel_match_on_current_Uptime_Russia_roster": False,
            "boundary": "Provider Tier wording is not relabelled as a current Uptime award ledger. Historical engineering and redundancy snapshots remain scoped to their publication dates and facility sections.",
        },
        "accelerator_and_AI_boundary": {
            "currently_documented_service_models": gpu_models,
            "B300_HGX_GPUs_per_server": 8,
            "fixed_or_custom_configuration_ceiling_GPUs": 8,
            "AI_investment_since_2020_RUB_billion_approximately": 3.6,
            "planned_AI_investment_through_2031_RUB_billion": 10,
            "AI_ITMO_joint_venture_investment_RUB_billion_more_than": 1,
            "physical_GPU_total_and_per_model_units": "undisclosed",
            "host_sites_delivery_power_utilization_revenue_and_margin": "undisclosed",
            "accelerator_ledger_action": "no_numeric_physical_inventory_row_created",
            "boundary": "Eight B300 GPUs describe one HGX server configuration, and an eight-GPU product ceiling is not installed inventory. Model availability and investment plans do not disclose fleet units or economics.",
        },
        "audited_FY2025_financials_RUB_thousand": {
            "revenue": 18311791,
            "cost_of_sales": 4932248,
            "selling_expenses": 1451703,
            "administrative_expenses": 2601751,
            "depreciation_and_amortization": 2952156,
            "operating_profit": 6234426,
            "derived_operating_margin_percent": 34.05,
            "finance_income": 542596,
            "finance_expense": 2726169,
            "profit_before_tax": 3980755,
            "income_tax": 962297,
            "net_profit": 3018458,
            "operating_cash_flow": 6417110,
            "PPE_purchases": 7591112,
            "intangible_purchases": 354037,
            "dividends": 1670978,
            "data_center_services_revenue": 1452020,
            "data_center_services_revenue_share_percent": 8,
            "cloud_infrastructure_revenue": 15879579,
            "other_revenue": 980192,
            "PPE": 21852879,
            "cash": 868909,
            "long_term_debt": 10040119,
            "current_debt": 7326734,
            "equity": 6790605,
            "top_five_customer_revenue_share_percent": 17.3,
            "customers": 33000,
            "boundary": "The audited consolidated operating profit is not a data-center-services segment profit and cannot be assigned to six facilities. Cloud infrastructure and physical data-center service revenue remain separate categories.",
        },
        "management_metrics_and_latest_trend": {
            "FY2025_adjusted_EBITDA_RUB_billion": 9.692,
            "FY2025_adjusted_EBITDA_margin_percent": 53,
            "FY2025_capex_RUB_billion": 7.9,
            "FY2025_server_capex_RUB_billion": 4.7,
            "FY2025_data_center_infrastructure_capex_RUB_billion": 2.9,
            "FY2025_adjusted_free_cash_flow_RUB_billion": -1.5,
            "FY2025_net_debt_RUB_billion": 16.813,
            "FY2025_net_debt_to_adjusted_EBITDA": 1.7,
            "Q1_2026": {
                "revenue_RUB_billion": 5.0,
                "revenue_growth_percent": 14,
                "cloud_infrastructure_revenue_RUB_billion": 4.3,
                "data_center_services_revenue_RUB_billion": 0.4,
                "adjusted_EBITDA_RUB_billion": 2.7,
                "adjusted_EBITDA_growth_percent": 5,
                "adjusted_EBITDA_margin_percent": 54,
                "margin_change_percentage_points": -5,
                "net_profit_RUB_billion": 0.9,
                "customers": 36600,
                "capex_RUB_billion": 2.8,
                "data_center_infrastructure_capex_RUB_billion": 0.9,
                "adjusted_free_cash_flow_RUB_billion": -1.3,
                "net_debt_RUB_billion": 18.1,
                "net_debt_to_adjusted_EBITDA": 1.8,
            },
            "boundary": "Adjusted metrics and Q1 management results are not the same as audited accounting operating profit. Rising capex and net debt, negative adjusted FCF and slower Q1 growth are material execution and financing signals.",
        },
        "ownership_and_control": {
            "direct_parent": "Servertech_Holding_Ltd_UAE",
            "ultimate_controlling_party_at_2025_year_end": "Vyacheslav_Mikhailovich_Mirilashvili",
            "subsidiaries_percent_owned": {"Edinaya_Set": 100, "Selectel_Lab": 100, "Selectel_Invest": 100},
            "Tier_5_2023_stake_percent": 25,
            "Catalystic_People_2025_stake_percent": 25,
            "Catalystic_People_ownership": {"T_Technologies_percent": 50.01, "Interros_percent": 49.99},
            "stake_transition_bridge": "not_fully_disclosed_in_reviewed_sources",
            "boundary": "The exact 2023-to-2025 seller and shareholder-table bridge is not inferred. IFRS control and announced minority transactions are preserved as separate evidence.",
        },
        "Yurlovsky_development_boundary": {
            "planned_racks": 2000,
            "planned_connected_power_mw": 20,
            "planned_servers_up_to": 80000,
            "planned_average_rack_density_kw": 8,
            "target_PUE": "1.10_to_1.15",
            "target_reliability": "Tier_IV_design_target",
            "H1_2025_data_center_infrastructure_capex_including_Yurlovsky_RUB_billion": 1.1,
            "current_official_operating_launch_confirmed": False,
            "boundary": "The project was omitted from the current six-facility operating page. Planned capacity, PUE and reliability are not current operating facts.",
        },
        "OSM_crosswalk": {
            "Selectel_operator_objects": sum(row["raw_operator"] == "Selectel" for row in osm_rows),
            "related_objects_including_one_name_only_building": len(osm_rows),
            "objects_joined_to_facility_candidates": sum(row["facility_candidate_ref"] is not None for row in osm_rows),
            "unresolved_geospatial_conflicts": sum(row["facility_candidate_ref"] is None for row in osm_rows),
            "Tsvetochnaya_overlapping_objects": 2,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "OSM does not map an exact Tsvetochnaya 2 object, contains an off-address Berzarina node and has overlapping Tsvetochnaya objects. It is not a complete or non-overlapping roster.",
        },
        "outlook": {
            "positive_signals": [
                "FY2025_audited_revenue_growth_about_39_percent_and_operating_profit_growth_about_28_5_percent",
                "FY2025_adjusted_EBITDA_margin_53_percent",
                "Q1_2026_customers_36600_and_data_center_services_revenue_growth_10_percent",
                "broad_current_GPU_service_menu_including_H100_H200_B300",
                "RUB10_billion_AI_investment_plan_through_2031",
                "top_five_customer_share_17_3_percent",
            ],
            "risk_signals": [
                "Q1_2026_revenue_growth_slowed_to_14_percent_and_adjusted_EBITDA_growth_to_5_percent",
                "Q1_2026_adjusted_EBITDA_margin_down_5_percentage_points",
                "FY2025_net_profit_declined_and_finance_expense_increased",
                "negative_adjusted_free_cash_flow_with_high_capex",
                "net_debt_increased_to_RUB18_1_billion_and_leverage_to_1_8x",
                "Yurlovsky_operating_launch_not_confirmed",
                "GPU_procurement_import_and_supply_chain_risk",
                "private_unlisted_company_with_no_public_equity_pure_play",
            ],
            "analytical_view": "Selectel combines strong growth, high adjusted margins, a broad GPU menu and substantial infrastructure investment. The main constraints are rising debt and finance cost, negative adjusted FCF, slower Q1 2026 growth, the unconfirmed Yurlovsky launch and the absence of physical GPU, site-utilization and site-economics disclosure.",
        },
        "remaining_material_gaps": [
            "exact_bridge_between_six_physical_facilities_four_investor_sites_and_service_regions_AZs_and_pools",
            "current_Yurlovsky_construction_energization_acceptance_and_launch_status",
            "per_site_operating_energized_leased_utilized_billed_and_actual_IT_load",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_and_cooling_as_built_BOM",
            "per_site_measured_PUE_WUE_absolute_water_energy_hourly_renewable_matching_and_liquid_cooled_MW",
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin",
            "data_center_services_accounting_operating_profit_cash_flow_capex_debt_customer_concentration_site_economics_and_ROIC",
            "exact_current_shareholder_table_and_2023_to_2025_25_percent_stake_transition",
            "exact_current_Uptime_award_identifiers_types_scope_and_expiry_for_provider_Tier_wording",
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
    registry = args.output_dir / "selectel_official_facility_registry.jsonl"
    summary_path = args.output_dir / "selectel_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
