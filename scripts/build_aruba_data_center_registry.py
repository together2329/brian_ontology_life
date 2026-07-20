#!/usr/bin/env python3
"""Build a scope-preserving Aruba owned data-center and OSM registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


ABOUT = "https://www.aruba.it/chisiamo.aspx"
DIRECTORY = "https://www.datacenter.it/en/"
IT1_PAGE = "https://www.datacenter.it/en/italy-arezzo-dc-it1/"
IT1_SHEET = "https://www.datacenter.it/doc/jcr%3A514291b4-f531-4fd2-bced-6d0617401d5d/IT1-EN-2025.pdf/lang%3Aen/IT1-EN-2025.pdf"
IT2_PAGE = "https://www.datacenter.it/en/italy-arezzo-dc-it2/"
IT2_SHEET = "https://www.datacenter.it/doc/jcr%3A7a8a9d56-0041-42a4-9c75-e40e88323039/IT2-EN-2025.pdf/lang%3Aen/IT2-EN-2025.pdf"
IT3_PAGE = "https://www.datacenter.it/en/italy-bergamo-dc-it3"
IT3_A_SHEET = "https://www.datacenter.it/en/doc/jcr%3A1723df0e-3865-4118-a377-ebe436d9ceb3/lang%3Aen/EN-DC-Schede-tecniche-IT3-%28DC-A%29.pdfEN-DC-Schede-tecniche-IT3-%28DC-A%29.pdf"
IT3_B_SHEET = "https://www.datacenter.it/en/doc/jcr%3A6b7ccf32-f8e9-4c2d-b4a0-0626063a2c96/lang%3Aen/EN-DC-B-Schede-tecniche-IT3.pdfEN-DC-B-Schede-tecniche-IT3.pdf"
IT3_C_SHEET = "https://www.datacenter.it/en/doc/jcr%3A342c04e0-1e7f-46bd-8bce-8b14e4e46642/lang%3Aen/EN-DC-C-Schede-tecniche-IT3.pdfEN-DC-C-Schede-tecniche-IT3.pdf"
IT4_PAGE = "https://www.datacenter.it/en/italy-rome-dc-it4/"
IT4_SHEET = "https://www.datacenter.it/doc/jcr%3Adf4926e6-32ed-4130-b6a6-0818982056e1/DCIT4-DCA-EN-2025.pdf/lang%3Aen/DCIT4-DCA-EN-2025.pdf"
IT4_CURRENT = "https://www.aruba.it/press-kit/visita-dei-consiglieri-comunali-di-roma-capitale-riccardo-corbucci-e-antonella-melito-al-tecnopolo-tiburtino.aspx"
CZ2_PAGE = "https://www.datacenter.it/en/czech-republic-ktis-dc-cz2/"
CZ2_SHEET = "https://www.datacenter.it/en/doc/jcr%3Aed5cb8a1-967d-4a6c-a463-4300399bceb0/lang%3Aen/CZ1-EN%20%283%29.pdfCZ1-EN%20%283%29.pdf"
CERT_22237 = "https://www.aruba.it/documents/certifications/it/aruba-spa-iso-22237.aspx"
CERT_50001 = "https://www.aruba.it/documents/certifications/it/aruba-spa-iso-50001.aspx"
CERTIFICATIONS = "https://www.datacenter.it/en/aruba-certifications"
TECHNOLOGY = "https://www.datacenter.it/en/technology"
XFERENCE = "https://www.aruba.it/en/press-kit/pivate-ai-xference-launches-its-european-infrastructure.aspx"
VMWARE_GPU = "https://www.aruba.it/press-kit/aruba-rafforza-offerta-private-cloud-con-vmware-cloud-foundation.aspx"
MEGAPORT = "https://www.aruba.it/en/press-kit/new-megaport-pops-activated-in-aruba-data-centers.aspx"
FINANCIAL_SECONDARY = "https://www.aziende.it/aruba-s-p-a"


OSM_COMPONENTS = {
    "osm_way_182828550": {"site_code": "IT1", "role": "provider_named_data_center_building_geometry"},
    "osm_way_45840658": {"site_code": "IT2", "role": "provider_named_data_center_building_geometry"},
    "osm_way_1269297685": {"site_code": "IT4_DC_A", "role": "IT4_DC_A_facility_component_geometry_exact_function_unverified"},
    "osm_way_1269297686": {"site_code": "IT4_DC_A", "role": "IT4_DC_A_facility_component_geometry_exact_function_unverified"},
}


FACILITIES = [
    {
        "id": "aruba_IT1_arezzo",
        "site_code": "IT1",
        "facility_name": "Data Center Arezzo IT1",
        "country": "Italy",
        "city": "Arezzo",
        "address": "Via Piero Gobetti 96, 52100 Arezzo",
        "lifecycle": "current_operating_provider_directory_and_current_certification_site",
        "gross_surface_m2": 4152,
        "data_hall_surface_m2": 1300,
        "data_rooms": None,
        "power_value_MW": 2.5,
        "power_denominator": "IT_power_redundant",
        "power_label": "Total power: 2.5 MW IT (redundant)",
        "rack_power_kW_up_to": 40,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_30min_standard_15min_minimum",
        "generators": "2N_diesel_48h_full_load_without_refueling",
        "cooling": "multiple_chilled_water_direct_expansion_dynamic_free_cooling_and_absorption_machine_2N",
        "fire_suppression": "inert_gas_IG_100",
        "source": IT1_SHEET,
    },
    {
        "id": "aruba_IT2_arezzo",
        "site_code": "IT2",
        "facility_name": "Data Center Arezzo IT2",
        "country": "Italy",
        "city": "Arezzo",
        "address": "Via Sergio Ramelli 8, 52100 Arezzo",
        "lifecycle": "current_operating_provider_directory_and_current_certification_site",
        "gross_surface_m2": 2500,
        "data_hall_surface_m2": 1000,
        "data_rooms": 3,
        "power_value_MW": 1.5,
        "power_denominator": "total_power_unspecified_IT_or_facility_redundant",
        "power_label": "Total power: 1.5 MW (redundant)",
        "rack_power_kW_up_to": 40,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_30min_standard_15min_minimum",
        "generators": "diesel_32h_full_load_without_refueling_count_and_redundancy_not_stated",
        "cooling": "direct_expansion_with_dynamic_free_cooling_CRAH_N_plus_2",
        "fire_suppression": "inert_gas_IG_55",
        "source": IT2_SHEET,
    },
    {
        "id": "aruba_IT3_DC_A_bergamo",
        "site_code": "IT3_DC_A",
        "facility_name": "Global Cloud Data Center IT3 DC-A",
        "country": "Italy",
        "city": "Ponte San Pietro",
        "address": "Via San Clemente 53, 24036 Ponte San Pietro",
        "lifecycle": "current_operating_provider_sheet_and_current_ISO22237_site",
        "gross_surface_m2": 17600,
        "data_hall_surface_m2": 8050,
        "data_rooms": 10,
        "power_value_MW": 12,
        "power_denominator": "IT_power_2N_redundant",
        "power_label": "Total power: 12 MW IT 2N (redundant)",
        "rack_power_kW_up_to": 40,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_15min_emergency_40min_standard",
        "generators": "2N_diesel_26h_emergency_52h_standard",
        "cooling": "groundwater_primary_chilled_water_water_to_water_and_water_to_air_2N_heat_exchangers_5_wells_emergency_air_water_chillers_CRAH_2N",
        "fire_suppression": "inert_gas_IG_541_cylinders_2N",
        "source": IT3_A_SHEET,
    },
    {
        "id": "aruba_IT3_DC_B_bergamo",
        "site_code": "IT3_DC_B",
        "facility_name": "Global Cloud Data Center IT3 DC-B",
        "country": "Italy",
        "city": "Ponte San Pietro",
        "address": "Via San Clemente 53, 24036 Ponte San Pietro",
        "lifecycle": "current_operating_provider_sheet_and_current_ISO22237_site",
        "gross_surface_m2": 17110,
        "data_hall_surface_m2": 4950,
        "data_rooms": 3,
        "power_value_MW": 9,
        "power_denominator": "IT_power_2N_redundant",
        "power_label": "Total power: 9 MW IT 2N (redundant)",
        "rack_power_kW_up_to": 40,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_15min_emergency_40min_standard",
        "generators": "2N_diesel_26h_emergency_52h_standard",
        "cooling": "groundwater_primary_chilled_water_water_to_water_and_water_to_air_2N_heat_exchangers_5_wells_emergency_air_water_chillers_CRAH_2N",
        "fire_suppression": "inert_gas_IG_541_cylinders_2N",
        "source": IT3_B_SHEET,
    },
    {
        "id": "aruba_IT3_DC_C_bergamo",
        "site_code": "IT3_DC_C",
        "facility_name": "Global Cloud Data Center IT3 DC-C",
        "country": "Italy",
        "city": "Ponte San Pietro",
        "address": "Via San Clemente 53, 24036 Ponte San Pietro",
        "lifecycle": "current_operating_provider_sheet_and_current_ISO22237_site",
        "gross_surface_m2": 13910,
        "data_hall_surface_m2": 5950,
        "data_rooms": 8,
        "power_value_MW": 8,
        "power_denominator": "IT_power_2N_redundant",
        "power_label": "Total power: 8 MW IT 2N (redundant)",
        "rack_power_kW_up_to": 40,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_15min_emergency_40min_standard",
        "generators": "2N_diesel_26h_emergency_52h_standard",
        "cooling": "groundwater_primary_chilled_water_water_to_water_and_water_to_air_2N_heat_exchangers_5_wells_emergency_air_water_chillers_CRAH_2N",
        "fire_suppression": "inert_gas_IG_541_cylinders_2N",
        "source": IT3_C_SHEET,
    },
    {
        "id": "aruba_IT4_DC_A_rome",
        "site_code": "IT4_DC_A",
        "facility_name": "Hyper Cloud Data Center IT4 DC-A",
        "country": "Italy",
        "city": "Rome",
        "address": "Via Giacomo Peroni 380, 00131 Rome",
        "lifecycle": "current_operating_first_campus_data_center_inaugurated_2024_and_current_ISO22237_site",
        "gross_surface_m2": 10730,
        "data_hall_surface_m2": 3120,
        "data_rooms": 6,
        "power_value_MW": 6,
        "power_denominator": "IT_power_2N_redundant",
        "power_label": "Total power: 6 MW IT 2N (redundant)",
        "rack_power_kW_up_to": 40,
        "rack_power_kW_standard": 14,
        "UPS": "2N_plus_1_double_conversion_static_500kVA_each_15min_emergency_30min_standard",
        "generators": "2N_diesel_24h_emergency_48h_standard_refill_within_12h",
        "cooling": "chilled_water_water_to_air_indirect_free_cooling_air_water_chillers_2N_and_CRAH_2N",
        "fire_suppression": "inert_gas_IG_541_cylinders_2N",
        "source": IT4_SHEET,
    },
    {
        "id": "aruba_CZ2_ktis",
        "site_code": "CZ2",
        "provider_navigation_legacy_label": "CZ1",
        "facility_name": "Data Center Ktis Forpsi CZ2",
        "country": "Czech Republic",
        "city": "Ktis",
        "address": "Ktis 54, 384 03 Ktis",
        "lifecycle": "current_operating_provider_directory_site",
        "gross_surface_m2": 1500,
        "data_hall_surface_m2": None,
        "data_rooms": 2,
        "server_capacity": 5000,
        "power_value_MW": 1,
        "power_denominator": "power_supply_unspecified_IT_or_facility",
        "power_label": "1 MW power supply",
        "rack_power_kW_up_to": 6,
        "UPS": "2N_double_conversion_static_20min",
        "generators": "external_diesel_units_24h_full_load_without_refueling_legacy_linked_sheet",
        "cooling": "direct_expansion_dynamic_free_cooling_CRAC_N_plus_2_legacy_linked_sheet",
        "fire_suppression": "inert_gas_exact_type_not_stated",
        "source": CZ2_PAGE,
        "datasheet_boundary": "The current CZ2 page still links a PDF whose title and filename say CZ1; current page identity controls, while the legacy nomenclature mismatch is retained.",
    },
]


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
    for facility in FACILITIES:
        row = dict(facility)
        row.update(
            {
                "object_type": "DataCenterFacilityDisclosure",
                "operator": "Aruba_SpA",
                "current_provider_owned_data_center_count": True,
                "OSM_status": "off_sample_current_provider_facility",
                "accessed_on": accessed_on,
            }
        )
        if facility["site_code"] == "IT1":
            row["OSM_ref"] = "osm_way_182828550"
            row["OSM_status"] = "exact_provider_named_OSM_building"
        elif facility["site_code"] == "IT2":
            row["OSM_ref"] = "osm_way_45840658"
            row["OSM_status"] = "exact_provider_named_OSM_building"
        elif facility["site_code"] == "IT4_DC_A":
            row["OSM_refs"] = ["osm_way_1269297685", "osm_way_1269297686"]
            row["OSM_status"] = "two_adjacent_OSM_component_geometries_grouped_to_one_current_facility"
        records.append(row)

    for osm_id, metadata in OSM_COMPONENTS.items():
        row = osm[osm_id]
        records.append(
            {
                "id": f"aruba_{osm_id}",
                "object_type": "DataCenterFacilityComponentEvidence",
                "operator": "Aruba_SpA",
                "operator_tag_raw": row.get("operator"),
                "site_code": metadata["site_code"],
                "component_role": metadata["role"],
                "OSM_ref": osm_id,
                "OSM_name": row.get("name"),
                "OSM_latitude": row.get("latitude"),
                "OSM_longitude": row.get("longitude"),
                "OSM_footprint_area_m2": row.get("footprint_area_m2"),
                "OSM_source_url": row.get("source_url"),
                "current_provider_owned_data_center_count": False,
                "count_boundary": "Component evidence is linked to a facility disclosure record and never increments Aruba's provider headline.",
                "accessed_on": accessed_on,
            }
        )
    assert len(records) == 11
    assert sum(row["current_provider_owned_data_center_count"] for row in records) == 7
    assert sum(row["object_type"] == "DataCenterFacilityComponentEvidence" for row in records) == 4
    assert round(sum(row.get("OSM_footprint_area_m2", 0) for row in records), 3) == 10568.844
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    facilities = [r for r in records if r["object_type"] == "DataCenterFacilityDisclosure"]
    exact_it_power = sum(
        r["power_value_MW"] for r in facilities if r["power_denominator"].startswith("IT_power")
    )
    return {
        "id": "aruba_owned_data_center_summary_2026_07_19",
        "operator": "Aruba S.p.A.",
        "legal_entity": {
            "VAT": "01573850516",
            "tax_code": "04552920482",
            "REA": "BG-434483",
            "share_capital_EUR": 4_000_000,
            "ownership_wording": "entirely_Italian_capital",
            "current_shareholder_names_and_percentages": "not_disclosed_in_reviewed_free_primary_sources",
        },
        "accessed_on": accessed_on,
        "provider_roster_reconciliation": {
            "official_company_owned_data_center_headline": 7,
            "current_provider_site_codes": ["IT1", "IT2", "IT3", "IT4", "CZ2"],
            "reconstructed_current_physical_facilities": [
                "IT1",
                "IT2",
                "IT3_DC_A",
                "IT3_DC_B",
                "IT3_DC_C",
                "IT4_DC_A",
                "CZ2",
            ],
            "reconstructed_count": 7,
            "reconciliation_method": "The official seven-owned headline is reconciled to IT1, IT2, current ISO-22237-listed IT3 DC-A/B/C and IT4, plus current owned CZ2. No single reviewed page publishes this seven-row bridge verbatim.",
            "partner_countries": ["United_Kingdom", "France", "Germany", "Poland"],
            "partner_facility_count": "not_disclosed",
            "boundary": "Five provider site codes are not seven physical facilities: IT3 contains three currently certified data-center buildings. Partner facilities and the four additional ultimate IT4 buildings are excluded from the current owned-seven count.",
        },
        "OSM_crosswalk": {
            "operator_tagged_objects": 4,
            "exact_current_provider_facilities_represented": 3,
            "represented_facilities": ["IT1", "IT2", "IT4_DC_A"],
            "off_sample_current_provider_facilities": ["IT3_DC_A", "IT3_DC_B", "IT3_DC_C", "CZ2"],
            "IT4_component_geometries": ["osm_way_1269297685", "osm_way_1269297686"],
            "IT4_component_footprint_sum_m2": 7702.606,
            "all_four_OSM_footprint_sum_m2": 10568.844,
            "boundary": "The two similarly sized Rome ways are adjacent components of one current IT4 DC-A facility group. Their exact data-hall-versus-power-center functions are not established, so neither is promoted to a second provider facility. OSM footprints are not provider gross-floor area.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "facility_scale": {
            "current_owned_facilities": 7,
            "published_gross_surface_checksum_m2": sum(r["gross_surface_m2"] for r in facilities),
            "published_data_hall_surface_checksum_m2_excluding_CZ2_undisclosed": sum(
                r["data_hall_surface_m2"] for r in facilities if r["data_hall_surface_m2"] is not None
            ),
            "current_detailed_facility_exact_IT_power_label_checksum_MW": exact_it_power,
            "other_current_facility_mixed_power_labels_MW": 2.5,
            "other_current_facility_mixed_power_label_components": {"IT2_total_power": 1.5, "CZ2_power_supply": 1.0},
            "portfolio_IT_power_achievable_MW": 80,
            "IT3_IT_power_achievable_MW": 45,
            "IT3_total_power_MW": 60,
            "IT4_IT_power_achievable_MW": 30,
            "IT3_current_named_DC_A_B_C_IT_power_checksum_MW": 29,
            "IT4_current_DC_A_IT_power_MW": 6,
            "boundary": "The 37.5-MW exact-IT checksum covers current named IT3 A/B/C, IT4 DC-A and IT1; IT3 plus IT4 alone is 35 MW. IT2 and CZ2 add 2.5 MW under different unspecified power labels, producing a 40-MW mixed-label arithmetic bridge rather than a normalized current IT total. The 80-MW headline is achievable portfolio capacity, not current energized, sold, occupied, utilized, billed or actual IT load. Redundant 2N paths are not doubled.",
        },
        "IT4_lifecycle": {
            "campus_area_m2": 74000,
            "current_first_data_center": "DC_A_inaugurated_October_2024_and_visited_as_first_module_in_2026",
            "current_DC_A_IT_power_MW": 6,
            "ultimate_independent_data_center_buildings": 5,
            "ultimate_IT_power_each_MW": 6,
            "ultimate_IT_power_MW": 30,
            "remaining_four_buildings": "future_full_capacity_not_current_operating_facilities",
            "boundary": "A 2026 release repeats 30 MW while describing the first module; the facility page explicitly defines 30 MW as full-capacity five-building achievable power, so it is not assigned to the current first building.",
        },
        "power_resilience_and_equipment": {
            "common_architecture": [
                "UPS_generators_and_redundant_cooling",
                "two_PDUs_per_rack",
                "segregated_power_paths",
                "modular_containerized_power_centers_with_battery_and_UPS_containers",
                "BMS_24_7_monitoring",
            ],
            "site_details": {
                r["site_code"]: {
                    "power_label": r["power_label"],
                    "UPS": r["UPS"],
                    "generators": r["generators"],
                    "rack_power_kW_up_to": r.get("rack_power_kW_up_to"),
                }
                for r in facilities
            },
            "undisclosed": [
                "grid_service_voltage_contract_capacity_and_current_draw_by_site",
                "substation_transformer_switchgear_busbar_PDU_counts_ratings_and_OEMs",
                "UPS_battery_generator_models_counts_serials_loading_test_acceptance_age_and_remaining_life",
                "energized_available_allocated_sold_occupied_billed_peak_and_actual_IT_load",
            ],
            "boundary": "Datasheet total or IT power is design/nameplate disclosure. UPS and generator runtime and redundancy do not disclose current load, utilization or a complete as-built bill of materials.",
        },
        "cooling_energy_and_environment": {
            "IT3": "groundwater_primary_2N_heat_exchangers_emergency_air_water_chillers_and_CRAH_2N",
            "IT4_DC_A": "chilled_water_indirect_free_cooling_air_water_chillers_2N_and_CRAH_2N",
            "IT1": "chilled_water_direct_expansion_dynamic_free_cooling_and_absorption_machine_2N",
            "IT2": "direct_expansion_dynamic_free_cooling_CRAH_N_plus_2",
            "CZ2": "dynamic_free_cooling_below_about_16_to_18C_with_compressor_cooling_as_needed",
            "renewable_electricity": "Guarantee_of_Origin_renewable_electricity_for_provider_data_centers",
            "onsite_or_owned_generation": ["photovoltaic", "owned_hydroelectric_plants"],
            "current_measured_site_PUE_WUE_energy_water_emissions_and_hourly_renewable_matching": "not_disclosed_in_reviewed_sources",
            "complete_cooling_BOM": "not_disclosed",
            "boundary": "Renewable certificates and owned generation do not establish hourly physical supply or site-specific consumption. Cooling methods and redundancy are not measured PUE, WUE or live liquid-cooled capacity.",
        },
        "AI_GPU_and_network": {
            "provider_owned_current_GPU_model_and_count_by_site": "not_disclosed_or_established",
            "VMware_hosted_private_cloud": "GPU_option_available_for_Private_AI_model_count_and_site_undisclosed",
            "Xference_IT3": {
                "status": "production_beta_launched_April_2026",
                "role": "Aruba_colocation_and_Hardware_as_a_Service_server_procurement_deployment_networking_and_security",
                "rack_density_kW_more_than": 20,
                "GPU_model_count_owner_and_server_configuration": "undisclosed",
            },
            "Megaport_active_PoPs": ["IT3", "IT4"],
            "internet_interconnection_Tbps_more_than": 1,
            "boundary": "GPU-enabled services and an AI customer's high-density workload prove demand and capability, not Aruba's exact physical GPU fleet. Hardware-as-a-Service wording does not by itself settle balance-sheet title for every server or accelerator.",
        },
        "certification": {
            "current_ISO22237_and_EN50600_as_built_sites": ["IT3_DC_A", "IT3_DC_B", "IT3_DC_C", "IT4_Roma_Peroni"],
            "availability_class": 4,
            "protection_security_class": 4,
            "EN50600_energy_efficiency_level": 3,
            "certificate_expiry": "2028-10-19",
            "current_ISO50001_Italian_sites": ["IT3_Ponte_San_Pietro", "IT1", "IT2", "IT4"],
            "current_ANSI_TIA_or_EU_CoC_roster_boundary": "IT1_and_IT3_DC_A_B_C_and_IT4_DC_A_are specifically listed; IT2 and CZ2 have other current certification evidence but are not silently promoted into the same award roster.",
        },
        "Aruba_SpA_financial_boundary_EUR": {
            "period": "FY2024",
            "legal_entity_scope": "Aruba_SpA_not_data_center_segment_or_entire_Aruba_Group",
            "revenue": 300_407_397,
            "revenue_growth_percent_reported": 13.7,
            "net_profit": 22_339_752,
            "net_margin_percent_derived": round(22_339_752 / 300_407_397 * 100, 2),
            "FY2023_revenue": 264_223_630,
            "FY2023_net_profit": 22_841_579,
            "operating_profit_EBIT_EBITDA_cash_flow_capex_debt_and_data_center_segment_results": "not_available_in_reviewed_free_sources",
            "source_quality": "secondary_transcription_says_Italian_Companies_Register_updated_2026_07_07_original_filed_statement_not_reviewed",
            "employee_count": "excluded_due_conflicting_secondary_values_and_scope_uncertainty",
            "boundary": "Net profit is not operating profit. Legal-entity revenue and profit include hosting, domains, email, cloud, trust and other digital services and cannot be allocated to data centers, individual sites or AI workloads.",
        },
        "outlook": {
            "positive_signals": [
                "official_80MW_achievable_portfolio_and_IT4_four_building_expansion_option",
                "IT3_and_IT4_active_Megaport_PoPs",
                "current_high_density_Xference_IT3_AI_workload",
                "GPU_enabled_private_cloud_offer",
                "FY2024_legal_entity_revenue_growth_13_7_percent",
                "owned_renewable_generation_and_GO_matching",
                "current_Rating4_ISO22237_and_energy_management_evidence",
            ],
            "risk_signals": [
                "80MW_is_achievable_not_current_live_or_utilized_load",
                "future_IT4_buildings_and_demand_timing_undisclosed",
                "current_GPU_fleet_and_liquid_cooling_not_disclosed",
                "site_level_PUE_WUE_energy_water_and_complete_BOM_undisclosed",
                "private_company_primary_financial_statements_and_ownership_percentages_not_reviewed",
                "no_data_center_segment_revenue_operating_profit_cash_flow_or_ROIC",
                "power_grid_permitting_customer_concentration_and_supplier_awards_undisclosed",
            ],
            "analytical_view": "Aruba is a growing private European digital-infrastructure operator with unusually detailed facility engineering and a credible 40-MW named-facility power-label bridge to an 80-MW achievable portfolio. It is not directly exchange-listed, and AI demand evidence is stronger than disclosed accelerator inventory or data-center segment economics.",
        },
        "records": records,
        "sources": [
            ABOUT,
            DIRECTORY,
            IT1_PAGE,
            IT1_SHEET,
            IT2_PAGE,
            IT2_SHEET,
            IT3_PAGE,
            IT3_A_SHEET,
            IT3_B_SHEET,
            IT3_C_SHEET,
            IT4_PAGE,
            IT4_SHEET,
            IT4_CURRENT,
            CZ2_PAGE,
            CZ2_SHEET,
            CERT_22237,
            CERT_50001,
            CERTIFICATIONS,
            TECHNOLOGY,
            XFERENCE,
            VMWARE_GPU,
            MEGAPORT,
            FINANCIAL_SECONDARY,
        ],
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
    registry_path = args.output_dir / "aruba_owned_data_center_registry.jsonl"
    summary_path = args.output_dir / "aruba_owned_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
