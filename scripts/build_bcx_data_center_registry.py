#!/usr/bin/env python3
"""Build a scope-preserving BCX data-center, OSM and financial registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


BCX_CERTIFICATIONS = "https://www.bcx.co.za/certifications/"
BCX_LOCATIONS_IMAGE = "https://www.bcx.co.za/wp-content/uploads/2023/04/BCX-data-centre-locations.png"
BCX_MANAGED_INFRASTRUCTURE = "https://www.bcx.co.za/solutions/services/managed-infrastructure-and-cloud-services/"
BCX_OFFICES = "https://www.bcx.co.za/our-offices/"
BCX_ALP_OFFERING = "https://www.bcx.co.za/bcx-alibaba-cloud-offering/"
BCX_ALP_DETAIL = "https://www.bcx.co.za/bcx-alibaba-apl-cloud-offering/"
BCX_DELL_AI = "https://www.bcx.co.za/insights/unlocking-the-power-of-generative-ai-for-organisations/"
TELKOM_SITE_TOUR = "https://group.telkom.co.za/documents/ir/financial-information/presentation-2023/Telkom_Investors_Site_Tours_Presentations.pdf"
TELKOM_AFS_2026 = "https://group.telkom.co.za/documents/ir/financial-information/annual-results-2026/Annual%20Financial%20Statements%20FY2026.pdf"
TELKOM_RESULTS_2026 = "https://group.telkom.co.za/about-us/mediacentre/currentreleases/2026/Telkom-financial-results-20260602.html"
UPTIME_ZA = "https://uptimeinstitute.com/uptime-institute-awards/country/id/ZA"
MIDRAND_UPGRADE_2011 = "https://companies.mybroadband.co.za/bcx/2011/06/01/what-it-takes-to-power-a-tier-iv-cloud-data-centre/"
BELLVILLE2_2009 = "https://mybroadband.co.za/news/telecoms/10606-telkom-s-r350-million-cybernest-details.html"
DATACENTERMAP_BCX = "https://www.datacentermap.com/c/bcx/"


FACILITIES_2023 = [
    {
        "site_code": "HUB_DC",
        "facility_name": "Centurion HUB DC",
        "region": "Gauteng",
        "locality": "Centurion",
        "current_provider_exact_address": "Telkom Park, 61 Oak Avenue (Gate 1), Technopark, Highveld, Centurion",
        "white_space_m2": 2850,
        "rack_capacity": 884,
        "critical_load_MW": 1.8,
        "tier_claim_2023": "Tier III Certified (2002)",
    },
    {
        "site_code": "HBDC",
        "facility_name": "HBDC",
        "region": "Gauteng",
        "locality": "Hartbeeshoek_map_label_alignment_exact_address_unpublished",
        "white_space_m2": 600,
        "rack_capacity": 179,
        "critical_load_MW": 0.48,
        "tier_claim_2023": "Tier 3 Compliant (2009)",
    },
    {
        "site_code": "NEXUS_DC",
        "facility_name": "Centurion NEXUS DC",
        "region": "Gauteng",
        "locality": "Centurion",
        "current_provider_exact_address": "Telkom Park, 61 Oak Avenue (Gate 3), Technopark, Highveld, Centurion",
        "white_space_m2": 2650,
        "rack_capacity": 742,
        "critical_load_MW": 1.8,
        "tier_claim_2023": "Tier 3 Compliant (2002)",
    },
    {
        "site_code": "NDC1",
        "facility_name": "Midrand NDC 1",
        "region": "Gauteng",
        "locality": "Midrand",
        "current_provider_exact_address": "International Business Gateway Park, corner New Road and 6th Street, 12A Challenger Avenue",
        "white_space_m2": 920,
        "rack_capacity": 326,
        "critical_load_MW": 1.0,
        "tier_claim_2023": "Tier IV Certified (2004)",
        "current_uptime_award": "Tier_IV_Certification_of_Design_Documents_only",
        "OSM_refs": ["osm_way_248815424", "osm_way_803853242"],
    },
    {
        "site_code": "NDC2",
        "facility_name": "Midrand NDC 2",
        "region": "Gauteng",
        "locality": "Midrand",
        "current_provider_exact_address": "International Business Gateway Park, corner New Road and 6th Street, 113 Elizabeth Road",
        "white_space_m2": 1920,
        "rack_capacity": 633,
        "critical_load_MW": 1.4,
        "tier_claim_2023": "Tier IV Certified (2006)",
        "current_uptime_award": "Tier_IV_Certification_of_Design_Documents_only",
        "OSM_refs": ["osm_way_1286206068", "osm_way_1286206067"],
    },
    {
        "site_code": "BELLVILLE1",
        "facility_name": "Bellville 1",
        "region": "Western Cape",
        "locality": "Bellville",
        "white_space_m2": 1200,
        "rack_capacity": 466,
        "critical_load_MW": 1.25,
        "tier_claim_2023": "Tier 3 Compliant (1987)",
    },
    {
        "site_code": "BELLVILLE2",
        "facility_name": "Bellville 2",
        "region": "Western Cape",
        "locality": "Bellville",
        "white_space_m2": 1600,
        "rack_capacity": 586,
        "critical_load_MW": 1.97,
        "tier_claim_2023": "Tier IV Certified (2009)",
        "current_uptime_award": "Tier_IV_Certification_of_Design_Documents_only_under_Telkom_SA_Limited",
    },
    {
        "site_code": "DHF2",
        "facility_name": "KZN Umhlanga DHF 2",
        "region": "KwaZulu-Natal",
        "locality": "Umhlanga",
        "white_space_m2": 190,
        "rack_capacity": 39,
        "critical_load_MW": 0.09,
        "tier_claim_2023": "Tier 2 Compliant (2003)",
    },
    {
        "site_code": "DHF1",
        "facility_name": "KZN Umhlanga DHF 1",
        "region": "KwaZulu-Natal",
        "locality": "Umhlanga",
        "white_space_m2": 240,
        "rack_capacity": 67,
        "critical_load_MW": 0.09,
        "tier_claim_2023": "Tier 2 Compliant (2003)",
    },
    {
        "site_code": "CENTREX",
        "facility_name": "KZN Durban Centrex",
        "region": "KwaZulu-Natal",
        "locality": "Durban",
        "white_space_m2": 150,
        "rack_capacity": 56,
        "critical_load_MW": 0.1,
        "tier_claim_2023": "Tier 2 Compliant (2012)",
    },
]


OSM_COMPONENTS = {
    "osm_way_248815424": {"site_code": "NDC1", "role": "provider_ref_NDC1_building_geometry"},
    "osm_way_803853242": {"site_code": "NDC1", "role": "NDC1_site_or_campus_boundary_geometry_overlapping_building"},
    "osm_way_1286206068": {"site_code": "NDC2", "role": "provider_ref_NDC2_building_geometry"},
    "osm_way_1286206067": {"site_code": "NDC2", "role": "NDC2_site_or_campus_boundary_geometry_overlapping_building"},
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {
        row["id"]: row
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
        for row in [json.loads(line)]
    }


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records: list[dict] = []
    for facility in FACILITIES_2023:
        row = dict(facility)
        row.update(
            {
                "id": f"bcx_{facility['site_code'].lower()}",
                "object_type": "DatedDataCenterFacilityDisclosure",
                "operator": "BCX_Business_Connexion_Group",
                "country": "South Africa",
                "disclosure_date": "2023-11-21",
                "disclosure_scope": "Telkom_investor_site_tour_national_10_data_center_footprint",
                "current_operating_count": None,
                "current_status_boundary": "The site appears in the official 2023 ten-site footprint. Current BCX pages publish conflicting 9, 12 and 21 counts and no complete current provider roster, so this row is not silently promoted to a verified 2026 operating site.",
                "source": TELKOM_SITE_TOUR,
                "accessed_on": accessed_on,
            }
        )
        records.append(row)

    for osm_id, metadata in OSM_COMPONENTS.items():
        row = osm[osm_id]
        records.append(
            {
                "id": f"bcx_{osm_id}",
                "object_type": "DataCenterFacilityComponentEvidence",
                "operator": "BCX_Business_Connexion_Group",
                "operator_tag_raw": row.get("operator"),
                "site_code": metadata["site_code"],
                "component_role": metadata["role"],
                "OSM_ref": osm_id,
                "OSM_latitude": row.get("latitude"),
                "OSM_longitude": row.get("longitude"),
                "OSM_footprint_area_m2": row.get("footprint_area_m2"),
                "OSM_source_url": row.get("source_url"),
                "facility_count_increment": 0,
                "count_boundary": "The building and enclosing site or campus geometry overlap. Each pair is one NDC facility group and areas are not added as physical floor area.",
                "accessed_on": accessed_on,
            }
        )
    assert len(records) == 14
    assert sum(r["object_type"] == "DatedDataCenterFacilityDisclosure" for r in records) == 10
    assert sum(r["object_type"] == "DataCenterFacilityComponentEvidence" for r in records) == 4
    assert sum(r["rack_capacity"] for r in records if "rack_capacity" in r) == 3978
    assert round(sum(r["critical_load_MW"] for r in records if "critical_load_MW" in r), 2) == 9.98
    assert round(sum(r.get("OSM_footprint_area_m2", 0) for r in records), 3) == 23104.757
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    facilities = [r for r in records if r["object_type"] == "DatedDataCenterFacilityDisclosure"]
    return {
        "id": "bcx_data_center_summary_2026_07_19",
        "operator": "BCX / Business Connexion Group Ltd",
        "parent": "Telkom SA SOC Limited",
        "accessed_on": accessed_on,
        "portfolio_count_reconciliation": {
            "current_provider_own_data_centers_service_page": 12,
            "current_provider_PCI_wording_South_Africa_data_centers": 9,
            "current_provider_global_marketing_page_data_centers": 21,
            "current_provider_Veeam_disaster_recovery_scope_data_centers": 5,
            "current_certification_page_hosting_space_m2_more_than": 16000,
            "official_2023_national_footprint_data_centers": 10,
            "official_2023_national_capacity_m2": 12600,
            "official_2023_national_IT_capacity_MW": 9.82,
            "official_2023_line_item_white_space_checksum_m2": sum(r["white_space_m2"] for r in facilities),
            "official_2023_line_item_white_space_difference_from_headline_m2": 12600 - sum(r["white_space_m2"] for r in facilities),
            "official_2023_line_item_critical_load_checksum_MW": round(sum(r["critical_load_MW"] for r in facilities), 2),
            "official_2023_line_item_critical_load_difference_from_headline_MW": round(sum(r["critical_load_MW"] for r in facilities) - 9.82, 2),
            "official_2023_rack_capacity_checksum": sum(r["rack_capacity"] for r in facilities),
            "secondary_current_twelve_name_bridge": ["NDC1", "NDC2", "HUB", "NEXUS", "Crown_Mines", "Hartbeeshoek", "KZN_DC1", "KZN_DC2", "KZN_DC3", "Century_City", "Bellville_DC1", "Bellville_DC2"],
            "boundary": "The provider's live pages expose multiple counts with different ownership, geography, certification and service denominators. The 2023 official line items sum to 12,320 m2 and 9.98 MW, not the slide headlines of 12,600 m2 and 9.82 MW. A third-party directory supplies a plausible twelve-name bridge by adding Crown Mines and Century City, but it is not treated as a complete provider-published current roster.",
        },
        "current_provider_exact_location_slice": {
            "source": BCX_LOCATIONS_IMAGE,
            "rows": {
                "NDC1": "International Business Gateway Park, corner New Road and 6th Street, 12A Challenger Avenue",
                "NDC2": "International Business Gateway Park, corner New Road and 6th Street, 113 Elizabeth Road",
                "HUB": "Telkom Park, 61 Oak Avenue (Gate 1), Technopark, Highveld, Centurion",
                "NEXUS": "Telkom Park, 61 Oak Avenue (Gate 3), Technopark, Highveld, Centurion",
            },
            "NDC2_address_conflict": "The provider image says 113 Elizabeth Road; one secondary directory says 113 Enterprise Avenue. The provider wording controls this registry pending cadastral confirmation.",
            "boundary": "The current certifications-page image discloses four exact rows, not a complete nine-, twelve- or twenty-one-site roster.",
        },
        "OSM_crosswalk": {
            "operator_tagged_objects": 4,
            "facility_groups": 2,
            "groups": {
                "NDC1": {"building": "osm_way_248815424", "site_or_campus_boundary": "osm_way_803853242"},
                "NDC2": {"building": "osm_way_1286206068", "site_or_campus_boundary": "osm_way_1286206067"},
            },
            "NDC1_building_footprint_m2": 2592.658,
            "NDC1_enclosing_geometry_area_m2": 11404.842,
            "NDC2_building_footprint_m2": 1716.533,
            "NDC2_enclosing_geometry_area_m2": 7390.724,
            "all_four_geometry_arithmetic_checksum_m2": 23104.757,
            "boundary": "The enclosing geometry and building footprint overlap at each site. The four-object checksum is only a source-integrity check and is not gross floor, white space, campus area or two facilities per pair.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "power_resilience_and_cooling": {
            "current_or_2023_site_level": {r["site_code"]: {"critical_load_MW": r["critical_load_MW"], "white_space_m2": r["white_space_m2"], "racks": r["rack_capacity"], "provider_tier_wording": r["tier_claim_2023"]} for r in facilities},
            "Midrand_2011_upgrade_unallocated_between_NDC1_and_NDC2": {
                "incremental_supply_MVA": 1,
                "post_upgrade_generators": 8,
                "post_upgrade_UPS_devices": 6,
                "additional_air_conditioning_units": 6,
                "installed_cable_m": 1300,
                "PUE_metering": "meters_on_all_power_boards",
                "boundary": "The dated release says Midrand data centre but does not identify NDC1 or NDC2. It is historical upgrade evidence, not a current equipment count or current available power.",
            },
            "Bellville2_2009_design_secondary": {
                "grid": "dual_Eskom_substations_Stikland_and_Oakdale",
                "data_floor_UPS": "dual_2400kW_each_capable_of_full_data_room",
                "cooling_power_supplies": "dual_2300kW",
                "diesel_generation": "off_site_exact_count_rating_and_runtime_unreported",
                "cooling_modules": 14,
                "free_cooling_threshold_outdoor_C_below": 24,
                "raised_floor_m": 1.2,
                "airflow": "cold_aisle_hot_aisle_with_roof_exhaust",
                "boundary": "A 2009 news report describes design-era equipment. It is not a current as-built bill of materials, operating load, efficiency measurement or maintenance assessment.",
            },
            "current_complete_BOM_and_operations": "not_disclosed",
            "undisclosed": ["per_site_grid_contract_voltage_and_current_draw", "substation_transformer_switchgear_busbar_PDU_OEM_model_count_rating", "current_UPS_battery_generator_fuel_count_rating_loading_test_age_and_remaining_life", "current_cooling_OEM_model_count_rating_redundancy_PUE_WUE_water_and_liquid_cooled_MW", "energized_available_allocated_sold_occupied_billed_peak_and_actual_IT_load"],
        },
        "certification_boundary": {
            "provider_page_claim": "three_Tier_IV_and_one_Tier_III_design_certified_data_centers_over_16000m2",
            "current_Uptime_rows": {
                "NDC1": "Tier_IV_Certification_of_Design_Documents",
                "NDC2": "Tier_IV_Certification_of_Design_Documents",
                "Bellville2_under_Telkom": "Tier_IV_Certification_of_Design_Documents",
                "NBSC2_under_Telkom": "Tier_III_Certification_of_Design_Documents",
            },
            "boundary": "The current Uptime directory shows design-document awards only for these BCX or Telkom rows, not constructed-facility or operational-sustainability awards. Provider shorthand such as certified or compliant is retained but not upgraded.",
        },
        "AI_GPU_cloud_boundary": {
            "ALP_region": {"primary_AZ": "Teraco_Isando_JB3_third_party", "secondary_AZ": "BCX_NDC1_Midrand"},
            "technology": "Alibaba_Cloud_Apsara_Stack",
            "catalog": ["E_HPC_GPU_instance", "E_HPC_FPGA_instance", "bare_metal", "elastic_compute", "storage", "network", "AI_and_big_data_services"],
            "Dell_relationship": "BCX describes Dell-based generative-AI architecture and implementation services",
            "current_BCX_owned_GPU_model_count_owner_site_delivery_rack_fabric_power_utilization_and_economics": "not_disclosed_or_established",
            "boundary": "A product catalog and an NDC1 availability zone establish a cloud-service and site relationship, not that a specific GPU SKU or count is physically installed, owned by BCX, available today or allocated to NDC1. The Teraco primary AZ is not BCX-owned inventory.",
        },
        "FY2026_financial_boundary_ZAR_million": {
            "period_end": "2026-03-31",
            "BCX_subsidiary_interest_before_eliminations": {"revenue": 11412, "EBITDA": 1104, "EBIT_operating_profit": 614, "net_profit": 472},
            "FY2025_comparison_before_eliminations": {"revenue": 12345, "EBITDA": 1189, "EBIT_operating_profit": 599, "net_profit": 406},
            "reportable_segment": {"external_revenue": 10308, "intersegment_revenue": 1104, "total_revenue": 11412, "adjusted_EBITDA_including_intersegment": 1076, "adjusted_EBITDA_margin_percent_derived": round(1076 / 11412 * 100, 2), "capex": 359},
            "parent_Telkom_group": {"revenue": 44477, "EBITDA": 12480, "operating_profit": 5933, "free_cash_flow": 3068},
            "ownership": {"Telkom_ownership_of_Business_Connexion_Group_percent": 100, "South_African_government_Telkom_share_percent": 40.5, "PIC_Telkom_share_percent": 11.08},
            "boundary": "The subsidiary-interest EBITDA of R1,104m and reportable-segment adjusted EBITDA of R1,076m use different pre-elimination and segment scopes and are not averaged. BCX results combine connectivity, IT services, hardware, software, cybersecurity, cloud and data centers. No data-center-only revenue, operating profit, cash flow, capex, occupancy, customer concentration or return on capital is disclosed.",
        },
        "outlook": {
            "positive_signals": ["twelve_own_data_center_service_page_headline", "NDC1_local_Apsara_Stack_AVailability_Zone", "cybersecurity_revenue_growth_21_1_percent_FY2026", "IT_hardware_and_software_revenue_growth_5_6_percent_FY2026", "FY2026_BCX_EBIT_and_net_profit_growth", "three_current_Uptime_Tier_IV_design_rows_across_BCX_and_Telkom"],
            "risk_signals": ["FY2026_total_revenue_decline_7_6_percent", "FY2026_adjusted_EBITDA_decline_from_R1376m_to_R1076m", "conflicting_current_9_12_21_and_5_site_counts", "2023_area_and_power_line_items_do_not_reconcile_to_headlines", "no_complete_current_provider_roster_or_current_site_engineering_BOM", "no_exact_GPU_inventory_or_live_liquid_cooling", "legacy_connectivity_migration_and_challenging_IT_market", "no_data_center_segment_economics"],
            "management_direction": "Under new leadership BCX is repositioning as a connectivity provider for digital services, while management emphasizes cloud and software expansion and operational efficiency.",
            "analytical_view": "BCX is a real, state-influenced African enterprise ICT and data-center platform with audited positive earnings and a local sovereign-cloud role. Its direct investment access is through listed parent Telkom, but data-center economics, current physical capacity and accelerator inventory remain too blended for pure-play valuation.",
        },
        "records": records,
        "sources": [BCX_CERTIFICATIONS, BCX_LOCATIONS_IMAGE, BCX_MANAGED_INFRASTRUCTURE, BCX_OFFICES, BCX_ALP_OFFERING, BCX_ALP_DETAIL, BCX_DELL_AI, TELKOM_SITE_TOUR, TELKOM_AFS_2026, TELKOM_RESULTS_2026, UPTIME_ZA, MIDRAND_UPGRADE_2011, BELLVILLE2_2009, DATACENTERMAP_BCX],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(load_osm(args.osm), args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    summary["records_sha256"] = canonical_hash(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "bcx_data_center_registry.jsonl"
    summary_path = args.output_dir / "bcx_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
