#!/usr/bin/env python3
"""Build a scope-preserving O2 Czech/CETIN data-center registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


SERVICE_URL = "https://www.o2.cz/podnikatele-a-firmy/cloud/datove-centrum"
SUPPORT_URL = "https://www.o2.cz/podpora/it-reseni-pro-firmy/datove-centrum"
HISTORY_URL = "https://blog.o2.cz/2018/07/12/prijdte-si-pohovorit-spolehlivosti-datovych-center"
KB_REFERENCE_URL = "https://www.o2.cz/podnikatele-a-firmy/reference/komercni-banka-datacentrum"
O2_IT_SERVICES_URL = "https://www.o2its.cz/reference/provoz-it/"
SOC3_URL = "https://www.o2.cz/spolecnost/soubory-certifikaty/soc3-report/SOC-3-Report-O2-EN-a-CZ.pdf"
CETIN_2024_URL = "https://www.cetin.cz/documents/105239/147890/KonsoVZ_2024_CETIN_CZ_signed.pdf/b344fd4c-a5c9-3718-974d-6fb2dd734f73?t=1743769297560"
PPF_2024_URL = "https://www.datocms-assets.com/40359/1746540335-ppfgroup_annual_accounts_2024.pdf"
PPF_2025_URL = "https://www.datocms-assets.com/40359/1777974326-ppfgroup_annual_accounts_2025_public.pdf"


def location(code: str, name: str, address: str | None, **extra: object) -> dict:
    return {
        "code": code,
        "service_location": name,
        "current_provider_address": address,
        "address_status": "current_provider_address_published" if address else "current_service_identifier_without_public_address_on_current_provider_page",
        **extra,
    }


LOCATIONS = [
    location(
        "STOD",
        "DC Stodulky",
        "K Zahradkam 2065/2, Praha 13 - Stodulky",
        certification_statement="provider_says_built_to_Tier_III_specifications_but_does_not_list_Stodulky_among_the_three_currently_certified_sites",
        final_reserved_input_MW=3.5,
        power_denominator="total_final_reserved_input_not_IT_load_current_draw_or_customer_load",
        power_topology="two_utility_feeds_two_independent_rack_circuits_two_PDUs_per_rack_UPS_N_plus_1_each_branch_and_diesel_generators_N_plus_1",
        diesel_runtime="minimum_24_hours_provider_fleet_statement",
        rack_power="standard_42U_service_up_to_5_9_kW_with_other_offers_possible",
        electrical_outputs="AC_230V_or_400V",
        availability="99_982_percent_power_and_cooling",
        maximum_PUE=1.5,
        PUE_denominator="provider_guaranteed_max_design_or_service_value_not_current_measured_annual_PUE",
        cooling="hot_and_cold_aisle_separation_23_plus_or_minus_2_C_and_30_to_70_percent_humidity",
        fire_suppression="inert_gas",
        raised_floor_load_kg_per_m2=1000,
        connectivity="three_independent_optical_directions_up_to_100_Gbps",
    ),
    location(
        "CHO",
        "DC Chodov",
        "V lomech 2339/1, 149 00 Praha 4 - Chodov",
        certification_statement="provider_identifies_current_Tier_III_certification_without_certificate_identifier_expiry_or_precise_award_type_on_the_reviewed_page",
    ),
    location(
        "NAG",
        "DC Nagano",
        None,
        certification_statement="provider_identifies_current_Tier_III_certification_without_certificate_identifier_expiry_or_precise_award_type_on_the_reviewed_page",
        history_statement="provider_blog_says_first_O2_data_center_opened_in_2002",
    ),
    location(
        "HKR",
        "DC Hradec Kralove",
        None,
        certification_statement="provider_identifies_current_Tier_III_certification_without_certificate_identifier_expiry_or_precise_award_type_on_the_reviewed_page",
    ),
    location(
        "BRN",
        "DC Brno - FASTER CZ",
        "Jarni 44g, Brno",
        certification_statement="provider_says_all_O2_data_centers_are_built_to_Tier_III_specifications_but_does_not_list_Brno_among_the_three_currently_certified_sites",
        partner_label="FASTER_CZ",
    ),
    location(
        "UHR",
        "DC Uherske Hradiste - DC Monaco",
        "Jaktare 1475, Uherske Hradiste",
        certification_statement="provider_says_all_O2_data_centers_are_built_to_Tier_III_specifications_but_does_not_list_Uherske_Hradiste_among_the_three_currently_certified_sites",
        partner_label="DC_Monaco",
    ),
]


OSM_CROSSWALK = {
    "osm_way_281398489": ("BRN", "exact_current_provider_name_and_city_match"),
    "osm_way_127931842": ("CHO", "exact_current_provider_name_and_address_area_match"),
    "osm_node_11436652400": ("UHR", "exact_current_provider_partner_name_and_city_match"),
    "osm_way_49548520": ("STOD", "exact_current_provider_name_and_postcode_area_match"),
}


COMMON_NON_STODULKY_ENGINEERING = {
    "rack_power_delivery": "two_PDUs_and_two_independent_rack_power_circuits",
    "UPS_topology": "N_plus_1",
    "diesel_topology": "N_plus_1",
    "diesel_runtime": "minimum_24_hours_provider_fleet_statement",
    "fire_detection_and_suppression": "VESDA_and_FM200_or_Inergen",
    "connectivity": "internet_or_MPLS_100_Mbps_to_10_Gbps",
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
    for row in LOCATIONS:
        engineering = {}
        if row["code"] != "STOD":
            engineering = COMMON_NON_STODULKY_ENGINEERING
        records.append({
            "id": f"o2_czech_provider_service_{row['code'].lower()}",
            "object_type": "ProviderServiceLocationEvidence",
            "country": "Czech_Republic",
            "physical_owner": "CETIN_a_s",
            "physical_facility_operations": "CETIN_a_s_outside_O2_IT_and_security_services_per_O2_SOC3",
            "service_provider_and_customer_interface": "O2_Czech_Republic_a_s",
            "service_state": "current_service_location_identifier",
            **engineering,
            **row,
            "count_boundary": "A service identifier, address, partner label, building, certified site, owned asset and operating data center are different scopes. The current six-name service roster is not converted into six verified CETIN-owned buildings without site-level title and address evidence.",
            "capacity_boundary": "Power topology, reserved input, availability and PUE labels are preserved at their published denominator and are not converted into current IT load, sold load, utilization, energy use or facility revenue.",
            "accessed_on": accessed_on,
        })
    for osm_id, row in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"o2_czech_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityEvidence",
            "country": "Czech_Republic",
            "physical_owner": "CETIN_a_s_per_portfolio_level_SOC3_not_object_level_title_search",
            "service_provider": "O2_Czech_Republic_a_s",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_operator": row.get("operator"),
            "raw_name": row.get("name"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "OSM_footprint_area_m2": row.get("footprint_area_m2"),
            "OSM_building_levels": row.get("building_levels"),
            "OSM_start_date": row.get("tags", {}).get("start_date"),
            "source_url": row["source_url"],
            "count_boundary": "The OSM object is a location crosswalk, not object-level proof of title, lease, operating responsibility, building count, gross floor area, white space, MW, utilization, GPU inventory or financial contribution.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 10
    assert sum(row["object_type"] == "ProviderServiceLocationEvidence" for row in records) == 6
    assert sum(row["object_type"] == "OSMFacilityEvidence" for row in records) == 4
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    provider = [row for row in records if row["object_type"] == "ProviderServiceLocationEvidence"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityEvidence"]
    return {
        "id": "o2_czech_cetin_data_center_summary_2026_07_19",
        "operator_boundary": "CETIN_owned_O2_service_and_customer_interface",
        "accessed_on": accessed_on,
        "roster_reconciliation": {
            "current_service_location_identifiers": len(provider),
            "current_provider_address_entries": sum(row["current_provider_address"] is not None for row in provider),
            "service_identifiers_without_current_public_address": [row["code"] for row in provider if row["current_provider_address"] is None],
            "exact_current_address_roster_OSM_matches": len(osm),
            "matched_provider_codes": [row["matched_provider_code"] for row in osm],
            "boundary": "The support and technical sections identify six service locations, while the current address directory lists four. Nagano and Hradec Kralove remain valid service identifiers but are not assigned invented current addresses or extra OSM objects.",
        },
        "ownership_and_operating_boundary": {
            "physical_title": "O2_SOC3_says_data_centers_are_owned_by_sister_company_CETIN_a_s",
            "non_IT_facility_and_access_operations": "CETIN_a_s",
            "customer_service_IT_and_security_interface": "O2_Czech_Republic_a_s",
            "group_control": "O2_Czech_Republic_and_CETIN_are_both_100_percent_PPF_group_companies",
            "contract_evidence": "CETIN_2024_accounts_identify_data_center_services_as_one_of_three_key_contracts_with_O2",
            "boundary": "The O2 operator label in OSM and commercial service page does not mean O2 holds physical title or recognizes all facility assets, capex and energy costs. CETIN ownership is not an object-level cadastral search for every service location.",
        },
        "power_cooling_and_equipment_boundary": {
            "Stodulky": {
                "final_reserved_input_MW": 3.5,
                "topology": "two_utility_feeds_two_independent_rack_circuits_two_PDUs_UPS_N_plus_1_each_branch_generators_N_plus_1",
                "diesel_runtime": "minimum_24_hours",
                "maximum_PUE": 1.5,
                "temperature_C": "23_plus_or_minus_2",
                "humidity_percent": "30_to_70",
                "raised_floor_load_kg_per_m2": 1000,
                "connectivity": "three_independent_optical_directions_up_to_100_Gbps",
            },
            "other_five": COMMON_NON_STODULKY_ENGINEERING,
            "provider_certification_statement": "Chodov_Nagano_and_Hradec_Kralove_are_identified_as_Tier_III_certified_while_all_six_are_described_as_built_to_Tier_III_specifications",
            "undisclosed_or_unestablished": [
                "site_level_utility_contract_capacity_current_draw_and_live_IT_load_except_Stodulky_reserved_input",
                "transformer_switchgear_busway_PDU_UPS_battery_generator_and_fuel_OEM_model_count_rating_loading_test_age_and_remaining_life",
                "chiller_CRAH_CRAC_CDU_pump_heat_exchanger_and_cooling_tower_OEM_model_count_rating_loading_and_live_liquid_cooled_MW",
                "measured_site_PUE_WUE_absolute_energy_water_emissions_and_hourly_renewable_matching",
                "current_racks_cabinets_white_space_available_sold_occupied_billed_and_utilized_capacity",
            ],
            "boundary": "Stodulky's 3.5MW is final reserved input, not IT load. Design redundancy, maximum PUE and rack-service power do not establish as-built equipment inventory, current draw, efficiency or fleet capacity.",
        },
        "AI_GPU_boundary": {
            "O2_IT_Services_companywide_operations_claim": "more_than_5000_servers_and_500_applications",
            "Dataclair_ai": "PPF_describes_it_as_an_in_house_AI_competence_center",
            "exact_current_O2_CETIN_customer_or_partner_physical_GPU_accelerator_model_count_owner_site_delivery_acceptance_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "A companywide managed-server statement and software AI competence center do not identify physical server ownership, site placement, GPU inventory or data-center AI revenue. No GPU total is inferred.",
        },
        "financial_and_investability_boundary": {
            "O2_Czech_2024_PPF_segment_EUR_m": {
                "external_revenue": 1473,
                "total_revenue": 1483,
                "operating_profit_excluding_depreciation_amortization_and_impairments": 470,
                "net_profit": 182,
                "capex": 195,
                "depreciation_and_amortization": 182,
                "assets": 1652,
                "liabilities": 1021,
                "equity": 631,
            },
            "PPF_Czech_telecom_subgroup_2025_EUR_m": {
                "scope": "PPF_TMT_Holdco_2_combines_O2_Czech_and_CETIN_Czech_not_data_center_only",
                "revenue": 1961,
                "EBITDA": 1000,
                "net_profit_from_continuing_operations": 357,
                "assets": 4635,
                "equity": 1151,
            },
            "data_center_only_revenue_operating_profit_EBITDA_capex_assets_energy_cost_customer_concentration_utilization_and_ROIC": "undisclosed",
            "direct_public_equity_security": "unavailable_O2_was_squeezed_out_and_both_O2_and_CETIN_are_100_percent_PPF_owned_while_PPF_is_private",
            "boundary": "O2's 2024 segment is diversified telecom and ICT, while the 2025 Czech telecom subgroup combines O2 and CETIN. Neither perimeter isolates data-center revenue, operating profit or asset returns.",
        },
        "outlook": {
            "positive_signals": ["six_location_national_service_footprint", "CETIN_physical_infrastructure_and_O2_enterprise_customer_distribution", "redundant_power_and_network_architecture", "PPF_group_AI_and_managed_ICT_capabilities", "hosting_cloud_and_managed_services_cross_sell"],
            "conversion_tests": ["reconcile_four_address_and_six_service_rosters", "publish_current_certification_identifiers_and_scopes", "bridge_Stodulky_reserved_input_to_live_IT_and_billed_load", "publish_site_equipment_and_measured_efficiency", "identify_installed_accelerators_and_liquid_cooling", "separate_O2_CETIN_and_data_center_financials"],
            "risks": ["diversified_telecom_scope", "sister_company_asset_and_cost_allocation", "no_fleet_MW_or_utilization", "no_GPU_or_AI_revenue_bridge", "private_parent_and_no_direct_security", "vendor_and_equipment_opacity"],
            "analytical_view": "O2 and CETIN provide a credible Czech enterprise hosting footprint, but the investable read-through is indirect. The strongest evidence is demand for power, electrical redundancy, cooling and connectivity; vendor winners and data-center economics cannot be assigned without contracts, equipment inventories and separated financials.",
        },
        "OSM_crosswalk": {
            "related_operator_tagged_objects": len(osm),
            "footprint_values_available": sum(row["OSM_footprint_area_m2"] is not None for row in osm),
            "footprint_area_m2_sum_not_floor_area": sum(row["OSM_footprint_area_m2"] or 0 for row in osm),
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "OSM footprint area is not gross floor area, white space, data-hall area, owned area or revenue-producing capacity. The Monaco point has no footprint.",
        },
        "records": records,
        "sources": [SERVICE_URL, SUPPORT_URL, HISTORY_URL, KB_REFERENCE_URL, O2_IT_SERVICES_URL, SOC3_URL, CETIN_2024_URL, PPF_2024_URL, PPF_2025_URL],
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
    registry_path = args.output_dir / "o2_czech_data_center_registry.jsonl"
    summary_path = args.output_dir / "o2_czech_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "provider_service_locations": 6,
        "provider_address_entries": 4,
        "OSM_objects": 4,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
