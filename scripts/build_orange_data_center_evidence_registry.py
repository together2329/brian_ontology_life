#!/usr/bin/env python3
"""Build Orange data-center, cloud-platform and OSM evidence records.

Orange publishes at least four incompatible denominators: the Orange Business
infrastructure estate, the Cloud Avenue service footprint, selected French
colocation campuses, and physical or legacy network sites.  This builder keeps
those scopes separate and joins the eleven Orange/Orange Business OSM objects
without turning public-map tags into an official building, ownership or live-load
census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


ORANGE_2025_URD = "https://assets.orange.com/medias/domain12751/media101746/523986-yvts1td99t-75.pdf"
ORANGE_FY2025 = "https://www.orange.com/en/assets/document/387974/download"
ORANGE_Q1_2026 = "https://assets.orange.com/medias/domain12751/media101762/528618-b6xgiexxgx-75.pdf"
ORANGE_STRATEGY = "https://www.orange.com/en/press-release/orange-unveils-trust-the-future-a-new-strategic-chapter-built-on-trust-to-unlock-growth-440093-440093"
ORANGE_TWO_NEW = "https://www.orange.com/fr/communiques/deux-nouveaux-datacenters-233480"
ORANGE_VDR_2019 = "https://newsroom.orange.com/orange-builds-a-new-data-centre-in-val-de-reuil-to-tackle-the-digital-challenges-of-the-future/?lang=eng"
COLOCATION = "https://www.orange-business.com/fr/solutions/cloud/colocation"
GREEN_WHITE_PAPER = "https://www.orange-business.com/sites/default/files/ADVAES-WHITE-PAPER-ORANGE-BUSINESS-GREEN-DATA-CENTER-FINAL-EN_0_0.pdf"
CLOUD_AVENUE = "https://www.orange-business.com/en/our-solutions/cloud/cloud-avenue"
CLOUD_AVENUE_SERVICE = "https://www.orange-business.com/sites/default/files/sd_cloud_avenue_osl_sthlm_ber_gbl_2025-12.pdf"
SECNUMCLOUD = "https://www.orange-business.com/en/about-us/our-certifications/secnumcloud"
GENAI = "https://www.orange-business.com/en/press/orange-business-launches-new-trusted-genai-offers-end-end-french-customers"
NVIDIA = "https://www.orange-business.com/en/press/orange-business-nvidia-strengthen-strategic-collaboration-deliver-trusted-sovereign-ai"
HPE = "https://www.orange-business.com/en/about-us/partners/hewlett-packard-enterprise-hpe"
AI_READY = "https://www.orange-business.com/be-en/solutions/cloud/ai-ready-infrastructure"
INGEROP_DC2020 = "https://www.ingerop.fr/projet/data-center-dc2020/"
A26_CHARTRES = "https://a26.diizz.com/portfolio/data-center/"
CARRIER_VDR = "https://www.carrier.com/commercial/en/se/media/fiche-reference-chantier-data-center-orange-en_tcm215-211619.pdf"
GEORISQUES_VDR = "https://www.georisques.gouv.fr/risques/installations/donnees/details/0005804966"
GEORISQUES_VDR_INSPECTION = "https://www.georisques.gouv.fr/webappReport/ws/installations/inspection/Bsbo7OaXtwPVs0JSGzPn87Z1hHsJcnSE"


RECORDS = [
    {
        "id": "orange_business_global_infrastructure_denominator",
        "record_kind": "group_infrastructure_headline",
        "scope": "Orange_Business_provider_described_own_infrastructure",
        "geography": "global",
        "provider_data_center_count": 70,
        "cloud_experts": 2500,
        "lifecycle": "current_FY2025_description",
        "boundary": "The annual report's 70-data-center statement is not accompanied by a complete address, building, legal-owner, capacity or lifecycle roster and must not be reconciled by adding Cloud Avenue or partner colocation sites.",
        "source_urls": [ORANGE_2025_URD],
    },
    {
        "id": "orange_cloud_avenue_europe_service_denominator",
        "record_kind": "cloud_service_footprint",
        "scope": "Cloud_Avenue_marketing_surface",
        "geography": "Europe",
        "provider_data_center_count_more_than_or_equal": 10,
        "provider_France_data_center_count": 4,
        "availability_percent": 99.99,
        "platform": ["HPE_Synergy", "HPE_GreenLake", "VMware_vCloud_Director", "VMware_NSX"],
        "lifecycle": "current_service_marketing",
        "boundary": "A service location can be an Orange facility, leased facility, partner site, region or availability zone. The 10-plus/four-France headline is not a physical-building or owned-asset roster.",
        "source_urls": [CLOUD_AVENUE, HPE],
    },
    {
        "id": "orange_flexible_datacenter_val_de_reuil",
        "record_kind": "selected_French_colocation_campus",
        "scope": "Val_de_Reuil_campus_and_Normandie_2_regulatory_building",
        "country_code": "FR",
        "locality": "Val-de-Reuil",
        "campus_hectares": 18,
        "provider_operating_data_centers": 2,
        "provider_future_data_centers_possible": 2,
        "operating_since": [2012, 2021],
        "Normandie_2": {
            "building_received": "2021-07-27",
            "operation_notified": "2021-09-10",
            "constructed_IT_rooms": 6,
            "initial_active_IT_rooms": 3,
            "planned_full_active_IT_rooms_by_approximately": 2030,
            "planned_generators_total": 17,
            "planned_replacement_generators_with_non_simultaneous_boundary": 5,
            "initial_generators_in_service": 8,
            "initial_generators_simultaneous": 6,
            "other_power_evidence": ["batteries", "electrical_distribution_rooms"],
            "cooling_equipment": ["air_handling_units", "chiller_groups"],
            "Carrier_2022_scope": {
                "liquid_chillers": 14,
                "condenser_model": "Carrier_AquaForce_30XA_1002_air_cooled",
                "control_upgrade": "floating_high_pressure_system",
                "PED_compliance_scope_chillers": 4,
            },
        },
        "shared_DC2020_scope_with_Chartres": {
            "active_IT_room_sqm": 8400,
            "IT_equipment_kw": 25000,
            "tier_range": "Tier_II_plus_to_III_plus",
            "cooling": "direct_free_cooling",
            "design_PUE": 1.3,
        },
        "lifecycle": "operating_and_phased_expansion",
        "boundary": "The 25-MW and 8,400-square-metre DC2020 values are combined Chartres/Val-de-Reuil project scope and cannot be allocated between campuses. Regulatory generator counts are Normandie 2 project/phase facts, not a campus-wide as-built fleet.",
        "source_urls": [COLOCATION, GREEN_WHITE_PAPER, ORANGE_VDR_2019, INGEROP_DC2020, CARRIER_VDR, GEORISQUES_VDR, GEORISQUES_VDR_INSPECTION],
    },
    {
        "id": "orange_flexible_datacenter_chartres_mainvilliers",
        "record_kind": "selected_French_colocation_campus",
        "scope": "Chartres_Mainvilliers_current_service_and_project_evidence",
        "country_code": "FR",
        "locality": "Chartres / Mainvilliers",
        "provider_data_center_count_conflict": {
            "2023_2024_white_paper": 1,
            "current_colocation_page": 2,
            "resolution": "unresolved_do_not_sum_or_choose_silently",
        },
        "provider_IT_room_sqm": 5000,
        "provider_opened": 2022,
        "synchronous_replication_to_Val_de_Reuil_ms_less_than": 3,
        "project_building_scope": {
            "gross_surface_sqm": 18989,
            "works_value_EUR_million": 67,
            "delivery": 2020,
            "cooling": "direct_free_cooling",
        },
        "shared_DC2020_scope_with_Val_de_Reuil": {
            "active_IT_room_sqm": 8400,
            "IT_equipment_kw": 25000,
            "tier_range": "Tier_II_plus_to_III_plus",
            "design_PUE": 1.3,
        },
        "lifecycle": "operating_with_count_conflict",
        "boundary": "The current page's two-data-center wording conflicts with the Orange Business white paper's one. Gross building surface, IT-room surface and the two-site DC2020 total remain different measures.",
        "source_urls": [COLOCATION, GREEN_WHITE_PAPER, INGEROP_DC2020, A26_CHARTRES],
    },
    {
        "id": "orange_flexible_datacenter_grenoble",
        "record_kind": "selected_French_colocation_campus",
        "scope": "Grenoble_Orange_Business_managed_data_center",
        "country_code": "FR",
        "locality": "Grenoble",
        "provider_data_center_count": 1,
        "managed_since": 2011,
        "building_history": "former_Alstom_industrial_radiography_site_rehabilitated",
        "building_envelope": {"concrete_wall_m": 2, "ceiling_m": 1.5},
        "cooling": {
            "technology": "groundwater_heat_exchange",
            "aquifer_depth_m": 30,
            "inlet_temperature_C": 13,
            "discharge_temperature_C_approximately": 17,
            "additives": "none",
            "WUE_claim": 0,
        },
        "electrical": {
            "transformers": ["very_low_loss", "vegetable_oil_transformers"],
            "UPS_efficiency_percent_more_than": 95,
            "UPS_efficiency_load_threshold_percent": 25,
            "rack_level_PDU_metering": True,
            "backup_replacement_study": "hydrogen_fuel_cells_under_discussion_not_deployed_fact",
        },
        "energy": "rooftop_and_facade_photovoltaics_supplement_grid_energy",
        "cloud": "Cloud_Avenue_SecNum_service_deployed_through_Orange_Business_La_Fabrique",
        "lifecycle": "operating",
        "boundary": "The white paper describes selected equipment and studies, not a complete current bill of materials. A hydrogen discussion is not installed generation, and the OSM Eolas footprint is an exact service-site candidate rather than verified gross area.",
        "source_urls": [COLOCATION, GREEN_WHITE_PAPER, SECNUMCLOUD],
    },
    {
        "id": "orange_amilly_network_data_center",
        "record_kind": "Orange_group_network_and_customer_data_center",
        "scope": "2022_corporate_release_not_current_Flexible_Datacenter_roster",
        "country_code": "FR",
        "locality": "Amilly",
        "building_surface_sqm": 16000,
        "IT_room_sqm": 5000,
        "cooling": "outside_air_free_cooling_more_than_10_months_per_year",
        "energy_impact_reduction_percent_vs_old_generation": 30,
        "renewable_electricity_equivalence": "three-site consumption covered by Boralex_Engie_TotalEnergies_PPAs",
        "lifecycle": "announced_operating_2022",
        "boundary": "The release groups Amilly, Val-de-Reuil Normandie 2 and the earlier Val-de-Reuil building as three data centers. Amilly is not silently treated as one of the current three Flexible Datacenter campuses.",
        "source_urls": [ORANGE_TWO_NEW],
    },
    {
        "id": "orange_cloud_avenue_dynamic_nordic_germany_gpu_service",
        "record_kind": "regional_cloud_and_accelerator_service",
        "scope": "Cloud_Avenue_Dynamic_OSL_STHLM_BER_service_description",
        "country_codes": ["DE", "NO", "SE"],
        "service_city_labels": ["Stockholm", "Oslo", "Berlin", "Frankfurt"],
        "GPU_service": {
            "models": ["NVIDIA_L4", "NVIDIA_L40", "NVIDIA_H100"],
            "physical_quantity": "undisclosed",
            "exact_host_site_by_model": "undisclosed",
            "allocation": "entire_GPU_dedicated_unit_available_to_customer_environment",
            "Orange_responsibility": ["operating_platform", "network_availability", "hardware_and_software_maintenance", "monitoring"],
        },
        "French_GPU_service": {
            "hardware_provider_and_commercial_model": "HPE_GreenLake",
            "platform": "Cloud_Avenue",
            "host_scope": "Orange_data_centers_in_France",
            "exact_model_count_site_and_owner": "undisclosed",
        },
        "lifecycle": "current_service_description_and_offer",
        "boundary": "The service description confirms supported physical GPU models but no model-by-site count, install date, utilization or fleet total. France and Nordic/German offers are separate evidence scopes and are not added.",
        "source_urls": [CLOUD_AVENUE_SERVICE, AI_READY, GENAI, NVIDIA, HPE],
    },
]


OSM_IDS = [
    "osm_node_9068705141",
    "osm_way_138943505",
    "osm_node_7902351616",
    "osm_node_8930909348",
    "osm_node_8930909347",
    "osm_way_68937644",
    "osm_way_68947782",
    "osm_way_72995274",
    "osm_way_80158243",
    "osm_way_683531738",
    "osm_way_50210667",
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for source_order, source in enumerate(RECORDS, start=1):
        row = dict(source)
        row.update({
            "object_type": "OrangeDataCenterEvidenceRecord",
            "source_order": source_order,
            "accessed_on": accessed_on,
            "comparison_contract": {
                "facility": "building, campus, market, service region, availability zone, partner site and OSM object remain separate",
                "power": "IT equipment kW, grid import, apparent power, generator output, design capacity and utilized load remain separate",
                "accelerator": "supported model, dedicated allocation, physical inventory, ownership, delivery and utilization remain separate",
                "finance": "Orange Group and Orange Business segment figures are not data-center-segment economics",
            },
        })
        records.append(row)
    assert len(records) == 7
    assert len({row["id"] for row in records}) == 7
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_id in OSM_IDS:
        source = osm[osm_id]
        assert source.get("operator") in {"Orange", "orange", "Orange Business"}
        exact = osm_id == "osm_way_50210667"
        landing_station = osm_id == "osm_way_683531738"
        rows.append({
            "osm_ref": osm_id,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "country_codes": sorted({candidate["iso2"] for candidate in source.get("country_candidates", [])}),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "crosswalk_status": "exact_Grenoble_La_Fabrique_service_site_candidate" if exact else ("submarine_landing_station_not_assumed_data_center" if landing_station else "Orange_current_or_legacy_network_site_not_in_current_official_roster"),
            "profile_ref": "orange_flexible_datacenter_grenoble" if exact else None,
            "boundary": "OSM is public-map evidence, not provider confirmation of current lifecycle, legal ownership, service availability, gross floor area, IT capacity, equipment, GPU inventory or utilization.",
            "source_url": source["source_url"],
        })
    assert len(rows) == 11
    assert Counter(row["raw_operator"] for row in rows) == {"Orange": 9, "orange": 1, "Orange Business": 1}
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    sources = sorted({url for row in records for url in row["source_urls"]})
    return {
        "id": "orange_data_center_evidence_summary_2026_07_19",
        "object_type": "OrangeDataCenterPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator": "Orange Group / Orange Business",
        "records": len(records),
        "denominator_reconciliation": {
            "Orange_Business_2025_own_infrastructure_data_centers": 70,
            "Cloud_Avenue_Europe_data_centers_more_than_or_equal": 10,
            "Cloud_Avenue_France_data_centers": 4,
            "current_selected_Flexible_Datacenter_France_campuses": 3,
            "Flexible_Datacenter_campus_labels": ["Val-de-Reuil", "Chartres-Mainvilliers", "Grenoble"],
            "2022_separately_named_network_data_center": "Amilly",
            "current_complete_physical_building_roster": "undisclosed",
            "boundary": "The 70, 10-plus, four-France, three-campus and facility-building numbers answer different questions and are never added into one estate count.",
        },
        "French_engineering": {
            "DC2020_two_site_scope": {"sites": ["Chartres", "Val-de-Reuil"], "active_IT_room_sqm": 8400, "IT_equipment_mw": 25, "cooling": "direct_free_cooling", "design_PUE": 1.3},
            "Val_de_Reuil_Normandie_2": {"constructed_IT_rooms": 6, "initial_active_IT_rooms": 3, "planned_generators": 17, "initial_generators": 8, "Carrier_liquid_chillers": 14, "Carrier_model": "AquaForce_30XA_1002_air_cooled_condenser"},
            "Grenoble": {"cooling": "13C_groundwater_heat_exchange_to_approximately_17C", "WUE_claim": 0, "UPS_efficiency_percent_more_than": 95, "transformers": ["very_low_loss", "vegetable_oil"], "rack_level_PDU_metering": True},
            "selected_colocation_metrics": {"PUE_range_from_white_paper": [1.29, 1.34], "current_page_PUE_less_than": 1.3, "current_page_WUE_near": 0, "current_page_CUE": 0.0087, "France_fleet_average_PUE_2025": 1.49},
            "group_cooling_boundary": "No Orange Group data center uses open-sky adiabatic cooling under current design policy; three use closed-loop adiabatic cooling in normal operation. This group statement is not allocated to sites.",
        },
        "accelerators": {
            "confirmed_models_in_2025_12_service_description": ["NVIDIA_L4", "NVIDIA_L40", "NVIDIA_H100"],
            "EU_EEA_service": "Cloud_Avenue_Dynamic_GPUaaS",
            "French_service_hardware_context": "HPE_GreenLake",
            "Orange_owned_or_managed_physical_GPU_count": "undisclosed",
            "site_allocation_utilization_power_draw_revenue_and_margin": "undisclosed",
            "boundary": "GPUaaS and dedicated units prove service availability, not an Orange-owned portfolio inventory or additive site count.",
        },
        "FY2025_financials_EUR_million": {
            "Orange_Group": {"revenue": 40396, "EBITDAaL": 12470, "operating_income": 3422, "net_income": 1139, "eCAPEX": 6208, "organic_cash_flow": 3653, "free_cash_flow_all_in": 2793},
            "Orange_Business": {"revenue": 7325, "EBITDAaL": 577, "EBITDAaL_margin_percent": 7.9, "operating_income": -277, "eCAPEX": 279, "tangible_and_intangible_investment": 383, "average_employees": 29415},
            "Orange_Business_operating_loss_context": {"goodwill_impairment": 332, "specific_personnel_charges": 165, "restructuring_costs": 108},
            "boundary": "Orange Business contains fixed, mobile, integration, cloud, data, AI and cybersecurity activities. No reviewed filing allocates revenue, operating income, capex, cash flow or ROIC to data centers or GPUaaS.",
        },
        "Q1_2026_EUR_million": {
            "Orange_Group": {"revenue": 10095, "EBITDAaL": 2601, "eCAPEX": 1542},
            "Orange_Business": {"revenue": 1753, "year_over_year_percent": -2.6, "IT_and_integration_revenue": 888, "IT_and_integration_year_over_year_percent": 1.3},
            "guidance": {"Group_EBITDAaL_growth_percent_more_than": 3, "eCAPEX_to_revenue_percent_approximately": 15, "organic_cash_flow_EUR_billion_approximately": 4},
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_rows),
            "operator_labels": Counter(row["raw_operator"] for row in osm_rows),
            "exact_service_site_candidates": 1,
            "landing_station_boundary_objects": 1,
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_rows), 3),
            "objects": osm_rows,
        },
        "unresolved_gaps": [
            "complete_current_70_data_center_address_building_lifecycle_owner_and_lease_roster",
            "reconciliation_of_Cloud_Avenue_10_plus_Europe_four_France_and_three_selected_colocation_campuses",
            "Chartres_one_versus_two_data_center_provider_publication_conflict",
            "per_site_grid_import_critical_IT_energized_leased_utilized_billed_and_customer_accepted_load",
            "complete_substation_transformer_switchgear_UPS_battery_generator_PDU_and_cooling_BOM",
            "physical_GPU_count_owner_financier_model_site_delivery_power_utilization_revenue_and_margin",
            "data_center_and_GPUaaS_revenue_operating_profit_capex_cash_flow_ROIC_and_customer_concentration",
            "measured_site_level_PUE_WUE_water_energy_emissions_and_hourly_renewable_matching",
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
    registry_path = args.output_dir / "orange_data_center_evidence_registry.jsonl"
    summary_path = args.output_dir / "orange_data_center_evidence_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
