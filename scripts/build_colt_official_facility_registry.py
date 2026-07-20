#!/usr/bin/env python3
"""Build a scope-preserving Colt DCS facility, transaction and OSM registry.

Colt DCS publishes a 15-operational/12-development headline, while its current
navigation, combined facility pages, partially operating Inzai 4 site, older
official datasheets and newer joint ventures expose different physical and
lifecycle scopes.  This builder preserves those boundaries and prevents former
Colt assets or Colt Technology Services network nodes from being counted as
current Colt DCS hyperscale capacity.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://www.coltdatacentres.net/en-GB"
MAP = "https://www.coltdatacentres.net/en-GB/map"
AI = "https://www.coltdatacentres.net/en-GB/solutions/ai"
SUSTAINABILITY = "https://www.coltdatacentres.net/en-GB/sustainability/decarbonising-our-business"
SUSTAINABILITY_2025 = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2026/06/sustainability-report-2025"
OWNERSHIP = "https://www.coltdatacentres.net/en-GB/about/ownership-and-investment"
COMPANY_LIST = "https://www.coltdatacentres.net/en-GB/list-of-companies"
GERMAN_EXPANSION = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2025/04/german-expansion"
PARIS_EXPANSION = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2025/05/paris-ground-breaking"
HAYES_EXPANSION = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2025/11/colt-dcs-london-hayes-expansion"
MINOH_JV = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2025/10/colt-and-esr-announce-joint-venture"
INDIA_JV = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2024/11/colt-dcs-rmz-joint-venture"
JAPAN_JV = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2021/07/fidelity-and-mitsui-form-joint-venture"
INZAI4_LAUNCH = "https://www.coltdatacentres.net/en-GB/press-releases/data-centres/2025/02/inzai-4-opening-ceremony"
ATLAS_EDGE_ACQUISITION = "https://atlasedge.com/atlasedge-further-expands-coverage-across-europe-with-acquisition-of-twelve-data-centres-from-colt-data-centre-services/"
ATLAS_EDGE_TEMPLUS_COMPLETION = "https://atlasedge.com/atlasedge-completes-sale-of-selected-data-centre-sites-accelerating-focus-on-scalable-high-growth-markets/"
ATLAS_EDGE_BRUSSELS = "https://atlasedge.com/data-centres/brussels/"
TEMPLUS_AMSTERDAM = "https://templus.com/data-centers/amsterdam-ams01/"
TEMPLUS_LOCATIONS = "https://templus.com/data-centers/"
COLT_TECH_SALE = "https://www.colt.net/resources/insights/colt-technology-services-announces-sale-of-eight-european-data-centres"
UK_DCS_ACCOUNTS = "https://find-and-update.company-information.service.gov.uk/company/07306352/filing-history/MzQ3NTA1NDM4MmFkaXF6a2N4/document?download=0&format=pdf"
COLT_GROUP_ACCOUNTS = "https://find-and-update.company-information.service.gov.uk/company/11530966/filing-history/MzQ2NjcxODM4M2FkaXF6a2N4/document?download=0&format=pdf"


def page(region: str, slug: str) -> str:
    return f"{HOME}/our-locations/data-centre-locations-{region}/{slug}"


def facility(
    code: str,
    country_code: str,
    market: str,
    lifecycle: str,
    source_urls: list[str],
    published_metrics: dict | None = None,
    engineering: dict | None = None,
    roster_role: str = "current_provider_navigation",
    conflicts: list[str] | None = None,
) -> dict:
    return {
        "id": f"colt_{code.lower().replace('-', '_')}",
        "facility_code": code,
        "country_code": country_code,
        "market": market,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "roster_role": roster_role,
        "published_metrics": published_metrics or {},
        "engineering_and_equipment_evidence": engineering or {},
        "publication_conflicts": conflicts or [],
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "AI_or_liquid_cooling_readiness_is_not_GPU_inventory": True,
        "source_urls": list(dict.fromkeys(source_urls)),
    }


OPERATING = [
    facility("Frankfurt_City", "DE", "Frankfurt", "operating", [page("europe", "frankfurt-city")],
             {"IT_power_mw": 1.2, "gross_technical_site_area_sqm": 2620},
             {"resilience": "Colt_tier_3", "power_and_UPS": "N+N", "generators": "N+1", "full_load_fuel_hours": 72}),
    facility("Frankfurt_West", "DE", "Frankfurt", "operating_fully_let", [page("europe", "frankfurt-west")],
             {"IT_power_mw": 25, "gross_technical_area_sqm": 10000},
             {"renewable_electricity_percent": 100}),
    facility("London_North", "GB", "Welwyn_Garden_City", "operating", [page("europe", "london-north")],
             {"IT_power_mw": 35, "gross_technical_area_sqm": 21339}),
    facility("London_West", "GB", "Park_Royal", "operating", [page("europe", "london-west")],
             {"IT_power_mw": 9.4, "gross_technical_site_area_sqm": 9553}),
    facility("Paris_South_West", "FR", "Les_Ulis", "operating", [page("europe", "paris-south-west")],
             {"IT_power_mw": 24, "gross_technical_site_area_sqm": 9384}),
    facility("Rotterdam", "NL", "Roosendaal", "operating_with_potential_capacity_measure", [page("europe", "rotterdam")],
             {"potential_maximum_IT_power_mw": 15, "data_hall_space_sqm": 11400},
             conflicts=["15MW_is_described_as_potential_maximum_and_is_not_current_live_or_utilized_load"]),
    facility("Mumbai_1", "IN", "Mumbai", "operating_shared_two_building_page", [page("asia", "mumbai"), INDIA_JV],
             {"Mumbai_1_and_2_combined_IT_power_mw": 22, "larger_campus_potential_IT_power_mw": 134, "individual_building_IT_power_mw": "undisclosed"},
             roster_role="current_provider_navigation_shared_page"),
    facility("Mumbai_2", "IN", "Mumbai", "operating_shared_two_building_page", [page("asia", "mumbai"), INDIA_JV],
             {"Mumbai_1_and_2_combined_IT_power_mw": 22, "larger_campus_potential_IT_power_mw": 134, "individual_building_IT_power_mw": "undisclosed"},
             roster_role="current_provider_navigation_shared_page"),
    facility("Osaka_City", "JP", "Osaka_Kita_ku", "operating_reconciliation_candidate_from_current_official_datasheet", [
        "https://www.coltdatacentres.net/en-GB/our-locations/data-centre-locations-asia/-/media/Files/asia-data-sheets/2021/colt-osaka-datasheet.pdf"],
        {"IT_power_mw": "undisclosed", "datasheet_PUE": 1.4},
        {"resilience": "Tier_3", "UPS": "N+1", "generators": "N+1", "full_load_fuel_hours": 48, "cooling": ["free_cooling", "outdoor_air_cooling"], "solar_energy_system": True},
        roster_role="current_official_datasheet_omitted_current_navigation",
        conflicts=["Current_official_datasheet_and_15_site_headline_support_a_roster_bridge_but_the_site_is_omitted_from_current_navigation"]),
    facility("Osaka_Keihanna", "JP", "Keihanna_Science_City", "operating_second_phase_completed", [page("asia", "osaka-keihanna")],
             {"fully_built_IT_power_mw": 45, "gross_technical_site_area_sqm": 42000},
             conflicts=["Current_page_says_second_phase_completed_and_fully_built_but_also_uses_once_complete_language"]),
    facility("Tokyo_Shiohama", "JP", "Tokyo", "operating", [page("asia", "tokyo-shiohama")],
             {"IT_power_mw": 5.6, "gross_technical_floor_area_sqm": 21348}),
    facility("Tokyo_Inzai_1", "JP", "Inzai", "operating", [page("asia", "inzai")],
             {"IT_power_mw": 8, "white_space_sqm": 4000}),
    facility("Tokyo_Inzai_2", "JP", "Inzai", "operating_fully_let", [page("asia", "inzai-2")],
             {"IT_power_mw": 15, "white_space_sqm": 5000}),
    facility("Tokyo_Inzai_3", "JP", "Inzai", "operating_fully_let", [page("asia", "inzai-3")],
             {"IT_power_mw": 27, "white_space_sqm": 8000}),
    facility("Tokyo_Inzai_4", "JP", "Inzai", "partially_operating_with_remaining_buildout", [page("asia", "inzai-4"), INZAI4_LAUNCH],
             {"operational_phase_IT_power_mw": 4.8, "full_build_IT_power_mw": 20, "white_space_sqm": 8747, "fully_prelet": True},
             {"global_reference_design": True, "base_isolation_building": True},
             conflicts=["Current_navigation_places_Inzai_4_under_data_centres_but_the_page_still_calls_the_20MW_site_in_development"]),
]


DEVELOPMENTS = [
    facility("Berlin_1", "DE", "Berlin", "development_first_phase_target_end_2028", [page("europe", "berlin-1-and-2"), GERMAN_EXPANSION],
             {"Berlin_1_and_2_combined_IT_power_mw": 54, "site_acres": 9.5, "secured_power_MVA": 80, "individual_IT_power_mw": "undisclosed"}, roster_role="development_navigation_shared_page"),
    facility("Berlin_2", "DE", "Berlin", "development", [page("europe", "berlin-1-and-2"), GERMAN_EXPANSION],
             {"Berlin_1_and_2_combined_IT_power_mw": 54, "site_acres": 9.5, "secured_power_MVA": 80, "individual_IT_power_mw": "undisclosed"}, roster_role="development_navigation_shared_page"),
    facility("Frankfurt_3", "DE", "Frankfurt_Sossenheim", "under_construction_first_phase", [page("europe", "frankfurt-three")],
             {"IT_power_mw": 32.4, "gross_floor_area_sqm": 17500}),
    facility("Frankfurt_4", "DE", "Wiesbaden", "development_first_phase_target_end_2028", [page("europe", "frankfurt-4-and-5"), GERMAN_EXPANSION],
             {"Frankfurt_4_and_5_combined_IT_power_mw": 63, "site_acres": 18, "secured_power_MVA": 100, "individual_IT_power_mw": "undisclosed"}, roster_role="development_navigation_shared_page"),
    facility("Frankfurt_5", "DE", "Wiesbaden", "development", [page("europe", "frankfurt-4-and-5"), GERMAN_EXPANSION],
             {"Frankfurt_4_and_5_combined_IT_power_mw": 63, "site_acres": 18, "secured_power_MVA": 100, "individual_IT_power_mw": "undisclosed"}, roster_role="development_navigation_shared_page"),
    facility("London_4", "GB", "Hayes", "under_construction_fully_let", [f"{HOME}/our-locations/data-centre-locations-europe/london-4"],
             {"IT_power_mw": 31, "floors": 5}, conflicts=["Older_expected_2025_phase_one_date_has_not_been_promoted_to_completion_without_current_confirmation"]),
    facility("London_5", "GB", "Hayes", "planning_permission_construction_not_confirmed", [page("europe", "london-5")],
             {"IT_power_mw": 31.5, "data_halls": 5, "data_hall_sqm_each": 1000},
             {"high_density_AI_ready": True, "waste_heat_ready": True}),
    facility("London_6", "GB", "Hayes", "approved_construction_expected_mid_2026_first_live_early_2029", [page("europe", "london-6-7-8"), HAYES_EXPANSION],
             {"page_IT_power_mw": 27, "data_halls": 9, "data_hall_sqm_each": 1000, "shared_press_scope_IT_power_mw": 97},
             {"design_density_kw_per_sqm_range": [3, 4.5], "design_PUE": 1.35, "high_voltage_supply_due": "2027-10"},
             conflicts=["Current_page_three_site_sum_is_98MW_while_official_approval_release_says_97MW"]),
    facility("London_7", "GB", "Hayes", "approved_planned", [page("europe", "london-6-7-8"), HAYES_EXPANSION],
             {"page_IT_power_mw": 48, "data_halls": 15, "data_hall_sqm_each": 1000, "shared_press_scope_IT_power_mw": 97},
             {"design_density_kw_per_sqm_range": [3, 4.5], "design_PUE": 1.35}, conflicts=["Current_page_three_site_sum_is_98MW_while_official_approval_release_says_97MW"]),
    facility("London_8", "GB", "Hayes", "approved_planned", [page("europe", "london-6-7-8"), HAYES_EXPANSION],
             {"page_IT_power_mw": 23, "data_halls_1000_sqm": 4, "data_halls_680_sqm": 4, "shared_press_scope_IT_power_mw": 97},
             {"design_density_kw_per_sqm_range": [3, 4.5], "design_PUE": 1.35}, conflicts=["Current_page_three_site_sum_is_98MW_while_official_approval_release_says_97MW"]),
    facility("Paris_2", "FR", "Villebon_sur_Yvette", "under_construction_fully_let", [page("europe", "paris-2"), PARIS_EXPANSION],
             {"IT_power_mw": 40, "shared_three_site_contracted_power_mw": 120, "site_acres": 12.5, "rack_density_kw_more_than": 100},
             {"cooling": ["air", "liquid_to_chip", "hybrid"], "cooling_water_waste": "zero_as_provider_design_claim", "waste_heat_recovery": True}),
    facility("Paris_3", "FR", "Villebon_sur_Yvette", "design_underway", [page("europe", "paris-3"), PARIS_EXPANSION],
             {"IT_power_mw": 32, "shared_three_site_contracted_power_mw": 120, "site_acres": 12.5, "rack_density_kw_more_than": 100},
             {"cooling": ["air", "direct_liquid_to_chip"]}),
    facility("Paris_4", "FR", "Villebon_sur_Yvette", "planned", [page("europe", "paris-4"), PARIS_EXPANSION],
             {"IT_power_mw": 9.6, "shared_three_site_contracted_power_mw": 120, "site_acres": 12.5}),
    facility("Paris_5", "FR", "Les_Ulis_2", "planned", [page("europe", "paris-5-and-6"), PARIS_EXPANSION],
             {"Paris_5_and_6_combined_IT_power_mw": 55, "shared_contracted_power_mw": 85, "site_acres": 5.3, "individual_IT_power_mw": "undisclosed"},
             {"workload_design": "cloud_and_high_density_AI", "cooling": ["air", "liquid_to_chip"]}, roster_role="development_navigation_shared_page"),
    facility("Paris_6", "FR", "Les_Ulis_2", "planned", [page("europe", "paris-5-and-6"), PARIS_EXPANSION],
             {"Paris_5_and_6_combined_IT_power_mw": 55, "shared_contracted_power_mw": 85, "site_acres": 5.3, "individual_IT_power_mw": "undisclosed"},
             {"workload_design": "enterprise_colocation"}, roster_role="development_navigation_shared_page"),
    facility("Chennai", "IN", "Chennai_Ambattur", "planned", [page("asia", "chennai"), INDIA_JV],
             {"current_page_IT_power_mw": 96}, conflicts=["Older_official_new_data_centres_material_said_72MW_while_current_page_says_96MW"]),
    facility("Tokyo_Inzai_5", "JP", "Inzai", "planned", [page("asia", "inzai-5")],
             {"IT_power_mw": 32, "gross_floor_area_sqm": 30158.78}),
    facility("Tokyo_Yoshikawa", "JP", "Yoshikawa_Saitama", "phase_one_underway", [page("asia", "tokyo-yoshikawa")],
             {"site_IT_power_mw": 80, "site_acres": 9.5, "physical_building_scope_up_to": 2}, conflicts=["80MW_is_a_site_scope_and_is_not_allocated_to_the_two_possible_buildings"]),
]


OTHER_EVIDENCE = [
    facility("Minoh_City", "JP", "Minoh_Osaka", "joint_venture_development_construction_target_2027", [MINOH_JV],
             {"master_site_IT_power_mw": 130, "phase_one_IT_power_mw": 65, "land_sqm_approximate": 140000, "phase_one_RFS": "late_2029"},
             roster_role="announced_joint_venture_outside_current_navigation"),
    facility("Tokyo_Otemachi", "JP", "Tokyo", "legacy_official_datasheet_current_lifecycle_unresolved", [
        "https://www.coltdatacentres.net/en-GB/our-locations/data-centre-locations-asia/-/media/Files/asia-data-sheets/2021/colt-tokyo-otemachi-datasheet.pdf"],
        {"IT_power_mw": "undisclosed"},
        {"resilience": "Tier_3_level", "UPS": "N+1", "gas_turbine_generators": "N+1", "full_load_fuel_hours": 72, "air_conditioning": "N+1"},
        roster_role="legacy_official_datasheet_omitted_current_navigation_and_headline_reconciliation"),
]


OSM_CROSSWALK = {
    "osm_way_30450893": ("former_Colt_DCS_AtlasEdge_BRU001", "former_colt_dcs_asset_current_AtlasEdge", "address_coordinate_match_to_Mercuriusstraat_30_Nossegem"),
    "osm_node_6215733985": ("Colt_Technology_Services_Belgium_node", "telecom_or_network_node_not_current_DCS_roster", "no_official_DCS_facility_match"),
    "osm_way_769969773": ("Colt_Technology_Services_Evere", "telecom_or_network_facility_not_current_DCS_roster", "exact_OSM_operator_is_Colt_Technology_Services_nv"),
    "osm_way_1417621831": ("colt_frankfurt_3", "current_DCS_development", "name_and_same_Sossenheim_cluster"),
    "osm_way_981463618": ("colt_frankfurt_west", "current_DCS_operating_candidate", "adjacent_FRA3_cluster_and_legacy_FRA74_label"),
    "osm_node_6121906640": ("Colt_Technology_Services_Lyon_node", "telecom_or_network_node_not_current_DCS_roster", "Lyon_absent_current_DCS_and_2021_sale_city_rosters"),
    "osm_node_6121873072": ("Colt_Technology_Services_Paris_1_node", "telecom_or_network_node_not_current_DCS_roster", "coordinate_does_not_match_current_DCS_or_former_CDG001"),
    "osm_node_6121864803": ("former_Colt_DCS_Templus_PAR01", "former_colt_dcs_asset_current_Templus", "postcode_and_coordinate_match_former_AtlasEdge_CDG001_Boulevard_Bessieres"),
    "osm_way_1141021688": ("colt_paris_south_west", "current_DCS_operating_building", "Les_Ulis_current_site_building"),
    "osm_way_79145624": ("colt_paris_south_west", "current_DCS_operating_building", "Les_Ulis_current_site_building"),
    "osm_way_83795984": ("Colt_Technology_Services_Malakoff", "telecom_or_network_facility_not_current_DCS_roster", "2025_public_authority_still_names_Colt_Paris_Malakoff_but_it_is_absent_current_DCS_roster"),
    "osm_way_98134606": ("colt_london_north", "current_DCS_operating_building", "exact_current_provider_website"),
    "osm_way_706624303": ("colt_london_west", "current_DCS_operating_building", "name_and_coordinate_match"),
    "osm_way_746750722": ("colt_tokyo_shiohama", "current_DCS_operating_building", "name_and_coordinate_match"),
    "osm_way_1124852913": ("colt_osaka_keihanna", "current_DCS_operating_building", "exact_DCS_operator_label_and_name"),
    "osm_node_2827483282": ("former_Colt_DCS_Templus_AMS01", "former_colt_dcs_asset_current_Templus", "Van_der_Madeweg_address_and_postcode_match"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = OPERATING + DEVELOPMENTS + OTHER_EVIDENCE
    records = [{"object_type": "DataCenterFacilityEvidence", "source_order": order, "operator": "Colt DCS", "accessed_on": accessed_on, **item} for order, item in enumerate(rows, 1)]
    assert len(OPERATING) == 15
    assert len(DEVELOPMENTS) == 18
    assert len(OTHER_EVIDENCE) == 2
    assert len(records) == 35
    assert len({row["facility_code"] for row in records}) == 35
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, current_classification, match_basis) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_or_boundary_ref": facility_ref,
            "current_classification": current_classification,
            "match_basis": match_basis,
            "source_url": source["source_url"],
            "boundary": "OSM labels and geometry do not establish current title, operator, lifecycle, IT load, utilization, equipment or GPU inventory.",
        })
    assert len(rows) == 16
    assert sum(row["current_classification"].startswith("current_DCS") for row in rows) == 8
    assert sum("former_colt_dcs_asset" in row["current_classification"] for row in rows) == 3
    assert sum("telecom_or_network" in row["current_classification"] for row in rows) == 5
    assert sum(row["raw_operator"] is not None for row in rows) == 8
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    operating_codes = [row["facility_code"] for row in OPERATING]
    development_codes = [row["facility_code"] for row in DEVELOPMENTS]
    return {
        "id": "colt_official_facility_summary_2026_07_19",
        "object_type": "ColtDCSPortfolioReconciliation",
        "accessed_on": accessed_on,
        "facility_roster": {
            "current_company_operational_headline": 15,
            "current_navigation_operating_page_groups": 13,
            "current_navigation_operating_physical_facility_labels_after_splitting_Mumbai_1_and_2": 14,
            "current_official_datasheet_only_reconciliation_candidate": ["Osaka_City"],
            "reconciled_operating_facility_labels": operating_codes,
            "partially_operating_mixed_lifecycle_site": {"Tokyo_Inzai_4_operational_mw": 4.8, "full_build_mw": 20},
            "legacy_datasheet_not_counted_current": ["Tokyo_Otemachi"],
            "current_company_development_headline": 12,
            "current_navigation_development_page_groups": 13,
            "development_facility_labels_after_splitting_grouped_pages": len(development_codes),
            "development_facility_codes": development_codes,
            "announced_JV_outside_navigation": ["Minoh_City"],
            "dated_2024_sustainability_release": {"operating_data_centres": 13, "facilities_in_development": 19},
            "boundary": "Headlines, navigation pages, named facilities, physical buildings, partially operating phases, legacy datasheets and joint-venture sites use different counts. The 15/12 marketing pair is not forced onto the 13 operating and 13 development page groups.",
        },
        "capacity_reconciliation": {
            "operating_or_fully_built_page_value_checksum_mw_excluding_Rotterdam_potential_Osaka_undisclosed_and_duplicate_Mumbai_shared_value": 222.0,
            "Rotterdam_potential_maximum_IT_mw": 15,
            "Mumbai_1_and_2_combined_current_IT_mw": 22,
            "Mumbai_campus_potential_IT_mw": 134,
            "Inzai_4_operational_phase_mw": 4.8,
            "Inzai_4_full_build_mw": 20,
            "current_navigation_development_design_checksum_mw_using_London_page_98": 655.5,
            "Minoh_master_site_design_mw_outside_navigation": 130,
            "Minoh_phase_one_mw": 65,
            "country_and_project_scopes": {
                "new_Germany_four_facilities_IT_mw": 117,
                "new_Germany_investment_EUR_billion": 2,
                "five_new_Paris_facilities_IT_mw": 136.6,
                "France_total_capacity_target_mw_by_2031": 170,
                "France_investment_EUR_billion": 2.3,
                "London_6_7_8_page_sum_mw": 98,
                "London_6_7_8_press_release_mw": 97,
                "Hayes_total_after_expansion_press_scope_mw": 160,
                "Hayes_investment_GBP_billion": 2.5,
                "India_RMZ_JV_investment_USD_billion": 1.7,
            },
            "boundary": "Page IT values are design, fully-built, potential, combined, operational-phase or contracted-power measures. The checksums are evidence controls, not current energized, customer-accepted, utilized or billed load.",
        },
        "electrical_cooling_and_sustainability": {
            "2025_global_PUE": 1.41,
            "greenhouse_gas_reduction_vs_2019_percent": 27,
            "Scope_2_renewable_electricity_percent": 100,
            "renewable_share_of_total_energy_percent": 90,
            "net_zero_target_year": 2045,
            "new_GRD_annualized_PUE_target_below": 1.2,
            "new_GRD_cooling": ["near_zero_wastewater_chilled_water", "closed_loop_liquid_cooling", "air", "direct_liquid_to_chip", "hybrid"],
            "new_German_GRD_rack_density_kw_up_to": 130,
            "Paris_2_and_3_rack_density_kw_more_than": 100,
            "TRUE_zero_waste_sites": ["London_North", "Tokyo_Inzai_1", "Tokyo_Inzai_2", "Tokyo_Inzai_3", "Osaka_Keihanna"],
            "site_specific_power_fragments": {
                "Frankfurt_City": ["N+N_power_and_UPS", "N+1_generators", "72_hours_full_load_fuel"],
                "Osaka_City": ["N+1_UPS", "N+1_generators", "48_hours_full_load_fuel", "PUE_1.4", "free_and_outdoor_air_cooling", "solar"],
                "London_6_7_8": ["National_Grid_contract", "high_voltage_supply_due_2027_10", "PPA_100_percent_renewable", "generator_use_max_15_hours_per_year_under_permission"],
            },
            "exact_per_site_current_grid_feeds_substations_transformers_switchgear_UPS_batteries_generators_chillers_CRAH_CRAC_CDU_models_counts_ratings_and_single_line_topology": "undisclosed",
        },
        "AI_and_GPU_boundary": {
            "AI_ready_new_markets": ["London", "Paris", "Frankfurt", "Mumbai", "Chennai", "Tokyo", "Yoshikawa"],
            "liquid_to_chip_and_hybrid_cooling_capability": True,
            "published_rack_density_context_kw": [100, 130],
            "Colt_DCS_owned_GPU_model_count_site_delivery_power_utilization_revenue_and_margin": "undisclosed",
            "customer_GPU_inventory_assignable_to_Colt_DCS": False,
            "accelerator_ledger_action": "no_numeric_row_created",
            "boundary": "AI-ready design, rack-density support and liquid cooling are data-centre capabilities, not proof that Colt DCS owns or operates GPUs.",
        },
        "ownership_and_financial_boundary": {
            "separate_entity_since": 2023,
            "immediate_parent": "Colt Data Centre Services Holdings S.a.r.l.",
            "intermediary_parent": "Colt Group Holdings Limited",
            "ultimate_parent_and_control": "SHM Lightning Investors LLC",
            "UK_legal_entity_scope": "two_UK_data_centres_near_London_plus_group_consulting_services",
            "UK_legal_entity_2024_GBP_million": {"turnover": 71.177, "EBITDA": 29.841, "operating_profit": 7.529, "loss_before_tax": 0.931, "profit_after_tax": 1.648, "net_assets": 206.831, "tangible_asset_additions": 7.355},
            "Colt_Group_2024_DCS_segment_revenue_EUR_million": 158.0,
            "Colt_Group_2023_DCS_segment_revenue_EUR_million": 161.8,
            "DCS_segment_operating_profit_and_EBITDA": "undisclosed",
            "boundary": "The GBP71.177m UK legal-entity turnover is contained within but is not equal to the EUR158.0m global DCS segment revenue. Currency and perimeter differ, and Colt Group operating loss or EBITDA is not assigned to DCS.",
        },
        "transactions_and_joint_ventures": {
            "2021_AtlasEdge_acquisition": {"former_Colt_DCS_data_centres": 12, "markets": ["Amsterdam", "Barcelona", "Berlin", "Brussels", "Copenhagen", "Hamburg", "London", "Madrid", "Milan", "Paris", "Zurich"]},
            "2026_05_Templus_completion_from_AtlasEdge": {"sites": 9, "markets": ["Madrid", "Barcelona", "Milan", "Zurich", "Paris", "Amsterdam", "London", "Leeds", "Copenhagen"]},
            "Japan_JV": ["Devonshire_Investors", "Mitsui_and_Mitsui_Asset_Management"],
            "India_JV": {"partner": "RMZ", "investment_USD_billion": 1.7},
            "Minoh_JV": {"partner": "ESR", "master_site_mw": 130, "phase_one_mw": 65},
            "Colt_Technology_Services_2025_data_centre_sale_boundary": "entirely_unrelated_to_Colt_DCS_according_to_official_release",
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_rows),
            "current_DCS_operating_or_development_objects": sum(row["current_classification"].startswith("current_DCS") for row in osm_rows),
            "former_DCS_assets_now_AtlasEdge_or_Templus": sum("former_colt_dcs_asset" in row["current_classification"] for row in osm_rows),
            "Colt_Technology_Services_network_or_telecom_objects": sum("telecom_or_network" in row["current_classification"] for row in osm_rows),
            "operator_tagged_objects": sum(row["raw_operator"] is not None for row in osm_rows),
            "rows": osm_rows,
        },
        "source_urls": list(dict.fromkeys([
            HOME, MAP, AI, SUSTAINABILITY, SUSTAINABILITY_2025, OWNERSHIP, COMPANY_LIST,
            GERMAN_EXPANSION, PARIS_EXPANSION, HAYES_EXPANSION, MINOH_JV, INDIA_JV,
            JAPAN_JV, INZAI4_LAUNCH, ATLAS_EDGE_ACQUISITION,
            ATLAS_EDGE_TEMPLUS_COMPLETION, ATLAS_EDGE_BRUSSELS, TEMPLUS_AMSTERDAM,
            TEMPLUS_LOCATIONS, COLT_TECH_SALE, UK_DCS_ACCOUNTS, COLT_GROUP_ACCOUNTS,
            *(url for row in records for url in row["source_urls"]),
        ])),
        "unresolved_gaps": [
            "15_operational_12_development_headlines_to_exact_current_non_overlapping_building_parcel_title_lease_and_lifecycle_roster",
            "Osaka_City_and_Tokyo_Otemachi_current_service_ownership_customer_and_headline_count_status",
            "222MW_operating_page_checksum_Rotterdam_15MW_potential_and_655_5MW_development_checksum_to_energized_leased_utilized_customer_accepted_billed_and_actual_load",
            "London_6_7_8_97MW_press_release_vs_98MW_page_scope",
            "Chennai_72MW_older_vs_96MW_current_page_scope",
            "per_site_power_and_cooling_as_built_equipment_BOM_PUE_WUE_water_energy_and_live_liquid_cooled_MW",
            "GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin",
            "global_DCS_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_site_economics_and_ROIC",
            "2021_AtlasEdge_twelve_asset_exact_building_level_crosswalk_and_remaining_legacy_Colt_labels",
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
    registry = args.output_dir / "colt_official_facility_registry.jsonl"
    summary_path = args.output_dir / "colt_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
