#!/usr/bin/env python3
"""Reconcile BNP Paribas OSM evidence to its internal and hosted compute estate.

The source inventory contains five BNP-operator-labelled objects plus a name-only
Marne Est campus relation.  Current JRC evidence identifies three French site
groups, while a 2026 BNP job advert confirms the two Belgian sites.  Marne Est
2 is a second building inside the Marne Est campus, and Val-de-Reuil was sold
in 2021 and is now Nation Data Center's NDC Rouen.  Hosted atNorth and IBM Cloud
capacity is retained separately from BNP-owned or BNP-operated physical sites.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


JRC_PARTICIPANTS = "https://e3p.jrc.ec.europa.eu/de/groups/data-centres-code-conduct/participants?order=field_adhesion_date&page=0&partner_search=&sort=desc"
MRAE_MAE2 = "https://www.drieat.ile-de-france.developpement-durable.gouv.fr/IMG/pdf/avis_mrae_-_projet_d_extension_d_un_data_center_-_bailly-romainvilliers_-_18082021.pdf"
SEINE_ET_MARNE_MAE2 = "https://www.seine-et-marne.gouv.fr/Publications/Enquetes-publiques/BAILLY-ROMAINVILLIERS-77-700-BNP-Paribas"
BNP_BELGIUM_2013 = "https://www.bnpparibasfortis.com/newsroom/press-release/bnp_paribas_group_breaks_ground_for_new_data_centres_in_belgium"
BNP_BELGIUM_JOB_2026 = "https://group.bnpparibas/en/careers/job-offer/data-center-facility-manager-bastogne-et-vaux-sur-sure-1"
BPC_BELGIUM = "https://bpcgroup.be/realisation/bnp-data-centers/"
DORSALYS_BELGIUM = "https://www.dorsalys.com/en/references/ibm-extension-data-centres"
SEMACO_BELGIUM = "https://semaco.com/portfolio-items/bnp/"
VAL_DE_REUIL_COUNCIL_2024 = "https://www.valdereuil.fr/wp-content/uploads/2024/12/Proces-verbal-du-Conseil-municipal-du-18-novembre-2024.pdf"
NDC_ROUEN = "https://nationdatacenter.fr/en/ndc-rouen/"
ARTELIA_NDC_ROUEN = "https://www.arteliagroup.com/fr/project/bnp-paribas-marne-est/"
BNP_ENERGY_EFFICIENCY = "https://group.bnpparibas/en/news/bnp-paribas-wins-awards-for-optimising-energy-consumption-in-its-data-centres"
BNP_ATNORTH = "https://group.bnpparibas/actualite/comment-les-data-centers-de-nouvelle-generation-peuvent-ils-contribuer-a-leconomie-circulaire"
ATNORTH_SWE01 = "https://www.atnorth.com/nordic-data-centers/sweden-data-centers/stockholm-metro-site/"
ATNORTH_BNP = "https://www.atnorth.com/news/atnorth-announces-bnp-paribas-at-swe01-facility/"
ATNORTH_DELL_CASE = "https://www.atnorth.com/uploads/Dell_atNorth_case-study.pdf"
BNP_IBM_CLOUD = "https://group.bnpparibas/en/press-release/bnp-paribas-signs-a-new-multi-year-partnership-agreement-with-ibm-cloud"
BNP_2025_RESULTS = "https://group.bnpparibas/en/press-release/bnp-paribas-group-results-as-of-31-december-2025"
BNP_2025_RESULTS_PDF = "https://invest.bnpparibas/document/4q25-pr"
BNP_2028_TRAJECTORY = "https://group.bnpparibas/en/news/we-intend-to-play-a-full-role-in-supporting-european-competitiveness"


OSM_RECONCILIATION = {
    "osm_relation_19660889": {
        "site_group": "Marne_Est",
        "classification": "current_OSM_campus_relation_not_separate_facility",
        "physical_role": "site_relation_containing_MAE1_MAE2_and_campus_objects",
        "count": False,
    },
    "osm_way_113172925": {
        "site_group": "Marne_Nord",
        "classification": "current_JRC_listed_internal_data_center_site_representative",
        "physical_role": "main_mapped_data_center_building",
        "count": True,
    },
    "osm_way_115416148": {
        "site_group": "Marne_Sud",
        "classification": "current_JRC_listed_internal_data_center_site_representative",
        "physical_role": "main_mapped_data_center_building",
        "count": True,
    },
    "osm_way_73137489": {
        "site_group": "Val_de_Reuil_legacy",
        "classification": "legacy_BNP_data_center_sold_2021_current_Nation_Data_Center_NDC_Rouen",
        "physical_role": "former_bank_data_center_building",
        "count": False,
    },
    "osm_relation_11087732": {
        "site_group": "Marne_Est",
        "classification": "current_JRC_listed_internal_data_center_site_representative",
        "physical_role": "MAE1_existing_operating_building",
        "count": True,
    },
    "osm_way_1299040068": {
        "site_group": "Marne_Est",
        "classification": "constructed_and_mapped_MAE2_campus_building_not_separate_site",
        "physical_role": "MAE2_second_data_center_building",
        "count": False,
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for source_order, (osm_ref, disposition) in enumerate(OSM_RECONCILIATION.items(), 1):
        source = osm[osm_ref]
        record = {
            "id": f"bnp_paribas_{osm_ref}",
            "object_type": "DataCenterFacilityOrGeometryEvidence",
            "operator_label": source.get("operator"),
            "portfolio_owner_or_operator": "BNP Paribas" if disposition["site_group"] != "Val_de_Reuil_legacy" else "Nation Data Center_current_BNP_legacy_label",
            "country": "France",
            "country_code": "FR",
            "site_group": disposition["site_group"],
            "classification": disposition["classification"],
            "physical_role": disposition["physical_role"],
            "current_BNP_site_count_inclusion": disposition["count"],
            "OSM_ref": osm_ref,
            "OSM_name": source.get("name"),
            "OSM_latitude": source["latitude"],
            "OSM_longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_source_url": source["source_url"],
            "source_order": source_order,
            "accessed_on": accessed_on,
        }
        if disposition["site_group"] == "Marne_Est":
            record["official_current_roster_context"] = "JRC lists BNP Paribas Marne Est 1 MAE1 as one participant site; MAE2 and the umbrella relation do not create additional site counts."
            record["counting_boundary"] = "One physical campus site group. Building, multipolygon and umbrella-site geometries are not independently counted."
            if osm_ref == "osm_way_1299040068":
                record["operational_status_boundary"] = "MAE2 is visibly constructed and mapped, but reviewed current official participant evidence still names MAE1; current customer acceptance, energized load and production use were not established."
        elif disposition["site_group"] == "Marne_Nord":
            record["official_current_roster_context"] = "JRC current participant list names BNP Paribas Marne Nord MN."
            record["counting_boundary"] = "One current French internal data-center site group. OSM footprint is not gross floor, data-hall or IT area."
        elif disposition["site_group"] == "Marne_Sud":
            record["official_current_roster_context"] = "JRC current participant list names BNP Paribas Marne Sud MS."
            record["counting_boundary"] = "One current French internal data-center site group. OSM footprint is not gross floor, data-hall or IT area."
        else:
            record["current_operator"] = "Nation Data Center"
            record["current_facility_name"] = "NDC Rouen"
            record["ownership_transition"] = "BNP municipal evidence says sale to Altarea Cogedim in 2021; Nation Data Center subsequently modernized the former banking facility."
            record["counting_boundary"] = "Preserved as legacy-label evidence only; adds no current BNP physical facility."
        records.append(record)
    assert len(records) == 6
    assert sum(row["current_BNP_site_count_inclusion"] for row in records) == 3
    assert sum(row["site_group"] == "Marne_Est" for row in records) == 3
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "bnp_paribas_internal_and_hosted_data_center_summary_2026_07_19",
        "operator": "BNP Paribas",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "related_OSM_rows": len(records),
            "OSM_operator_tagged_rows": 5,
            "OSM_name_only_campus_relations": 1,
            "current_minimum_BNP_operated_site_groups": 5,
            "current_France_site_groups": ["Marne_Est", "Marne_Nord", "Marne_Sud"],
            "current_Belgium_site_groups": ["Bastogne", "Vaux_sur_Sure"],
            "current_France_OSM_site_representatives": 3,
            "Marne_Est_related_OSM_geometries": 3,
            "Val_de_Reuil_legacy_rows_excluded": 1,
            "boundary": "Five is a current evidence-backed minimum across France and Belgium, not a complete global building census. MAE2 is a second building inside Marne Est, Val-de-Reuil is no longer BNP, and third-party hosted capacity is not BNP physical-site inventory.",
        },
        "France_sites": {
            "Marne_Est": {
                "current_site_group_count": 1,
                "JRC_current_participant_name": "BNP Paribas Marne Est 1 MAE1",
                "campus_land_hectares_2021": 7.4,
                "MAE1": {
                    "first_authorized": 2012,
                    "MRAe_2021_building_footprint_m2": 3180,
                    "MRAe_2021_IT_rooms": 2,
                    "OSM_multipolygon_area_m2": 5829.914,
                    "boundary": "The regulatory building footprint and current OSM multipolygon area use different geometry perimeters and are not reconciled or added.",
                },
                "MAE2": {
                    "state": "constructed_and_mapped_current_production_acceptance_not_established",
                    "planned_length_m": 110,
                    "planned_height_m": 15,
                    "planned_building_footprint_m2": 6008,
                    "planned_floor_area_m2": 10891,
                    "planned_IT_rooms": 2,
                    "planned_IT_room_area_each_m2": 1000,
                    "OSM_current_footprint_area_m2": 5348.676,
                    "planned_generator_count": 6,
                    "planned_generator_unit_kW": 6300,
                    "planned_generator_nameplate_total_MW": 37.8,
                    "planned_UPS_or_battery_bank_count": 32,
                    "published_UPS_total_kW": 928,
                    "published_UPS_runtime_minutes": 10,
                    "planned_rooftop_chiller_count": 16,
                    "planned_chiller_refrigerant": "R1234ze",
                    "planned_chiller_refrigerant_kg": 2576,
                    "planned_rooftop_heat_pump_count": 5,
                    "planned_heat_pump_refrigerant": "R410A",
                    "planned_heat_pump_refrigerant_kg": 350,
                    "planned_additional_underground_double_wall_fuel_tanks": 3,
                    "planned_fuel_tank_each_m3": 100,
                    "planned_daily_fuel_tanks": 6,
                    "planned_daily_fuel_tank_each_m3": 0.5,
                    "planned_additional_fuel_mass_tonnes": 254,
                    "planned_main_low_voltage_switchboards": 8,
                },
                "energy_context_2021": {
                    "site_electricity_2019_GWh": 37.6,
                    "MAE2_2025_increment_forecast_GWh": 7.8,
                    "MAE2_2040_forecast_GWh": 50.8,
                    "two_building_2040_forecast_GWh": 126.95,
                    "permit_MAE2_apparent_electrical_need_MVA": 8.7,
                    "permit_site_apparent_electrical_need_MVA": 22.2,
                    "MRAe_quality_warning": "The authority explicitly requested correction or clarification of the electrical-power figures; forecast energy and apparent power must not be treated as current measured IT load.",
                    "current_site_PUE_estimate_in_2021": 1.6,
                    "planned_final_site_PUE": 1.4,
                    "cooling_and_efficiency": ["partial_free_chilling_below_10C", "high_performance_chillers", "optimized_IT_room_airflow", "heat_pumps_for_waste_heat", "LED_lighting"],
                    "forecast_post_project_generator_count_sitewide": 15,
                    "forecast_post_project_annual_fuel_m3": 123,
                },
            },
            "Marne_Nord": {
                "current_site_group_count": 1,
                "JRC_current_participant_name": "BNP Paribas Marne Nord MN",
                "OSM_building_footprint_area_m2": 13149.426,
                "current_operating_IT_MW_racks_and_complete_BOM": "undisclosed",
            },
            "Marne_Sud": {
                "current_site_group_count": 1,
                "JRC_current_participant_name": "BNP Paribas Marne Sud MS",
                "OSM_building_footprint_area_m2": 3577.703,
                "current_operating_IT_MW_racks_and_complete_BOM": "undisclosed",
            },
            "Val_de_Reuil_legacy": {
                "current_BNP_site_count": 0,
                "sale_year": 2021,
                "current_operator": "Nation Data Center",
                "current_name": "NDC Rouen",
                "modernization_design": {
                    "old_banking_data_center_rehabilitation": True,
                    "initial_IT_MW": 1.2,
                    "target_IT_MW": 1.8,
                    "IT_area_m2": 2000,
                    "target_PUE": 1.2,
                    "cooling": ["surface_geothermal", "free_cooling"],
                    "power_resilience": "two_redundant_generator_plants",
                    "onsite_energy": ["photovoltaic_roof", "photovoltaic_parking"],
                },
                "boundary": "NDC engineering values describe the post-sale redevelopment and are not BNP current capacity.",
            },
        },
        "Belgium_sites": {
            "current_site_groups": 2,
            "sites": ["Bastogne", "Vaux_sur_Sure"],
            "current_evidence": "A BNP job listing updated 2026-06-30 describes the Belgian data-center estate, a Bastogne Nord base and travel among Belgian and Marne-la-Vallee data sites.",
            "original_program_2013": {
                "investment_EUR_more_than_million": 200,
                "required_electrical_power_per_site_MW": 30,
                "planned_each_site_technical_and_IT_buildings": 3,
                "planned_each_technical_and_IT_building_area_m2_approx": 8000,
                "planned_each_site_logistics_building_m2": 1200,
                "planned_combined_building_area_m2_more_than": 50000,
                "planned_certification": "ISO_27001",
                "design_tier": "Tier_3_plus",
                "planned_PUE": 1.3,
                "planned_efficiency_improvement_percent": 30,
                "cooling": "free_cooling_using_outdoor_air",
                "planned_phases": [2015, 2020, 2025],
            },
            "contractor_disclosures_non_additive": {
                "BPC": {"construction_period": "2014_01_to_2015_11", "combined_surface_m2": 43680},
                "Semaco": {"period": "2016_to_2017", "budget_EUR_million": 140, "stated_surface_m2_each": 30000},
                "Dorsalys": {"year": 2016, "design": "dual_site_IT_Tier_III", "computer_or_storage_room_area": "4_x_1500_m2", "new_rooms_operated_by": "IBM"},
                "boundary": "These contractor scopes differ by phase, area perimeter and work package. They are not added into one current portfolio area or capex total.",
            },
            "current_operating_IT_MW_racks_PUE_WUE_energy_water_utilization_and_complete_equipment_BOM": "undisclosed",
        },
        "hosted_and_cloud_boundary": {
            "atNorth": {
                "relationship": "BNP_compute_hosted_in_third_party_atNorth_facilities",
                "Iceland": {"reported_capacity_effect": "2018_migration_increased_total_BNP_compute_capacity_nearly_30_percent", "reported_energy_reduction_percent_more_than": 50, "reported_CO2_reduction_percent": 85, "hardware": "Dell_PowerEdge_HPC_servers", "exact_site_code": "not_established_in_reviewed_case_study"},
                "SWE01": {"location": "Kista_Stockholm_Sweden", "provider_site_power_MW": 12, "provider_facility_area_m2": 6400, "provider_PUE_up_to": 1.2, "BNP_grid_capacity_increase_percent": 20, "cooling": "direct_liquid_cooling_and_chilled_water_mechanical_cooling_N_plus_1", "power": "UPS_backed_with_generator_fuel_for_34_hours", "waste_heat": "up_to_85_percent_of_electricity_reused_as_district_heat_for_up_to_20000_homes", "reported_DLC_operational_efficiency_improvement_percent_at_least": 30},
                "ownership_boundary": "atNorth owns or operates the physical facility. Provider site MW and area are not BNP-owned site capacity, and the complete BNP contracted or utilized share is undisclosed.",
            },
            "IBM_Cloud": {
                "hosted_in_BNP_data_centers_since": 2019,
                "new_dedicated_area_target": 2028,
                "partnership_term_years": 10,
                "stated_capability": "GPUs_as_a_service_and_dedicated_cloud_native_environment",
                "boundary": "Service capability does not disclose physical GPU model, count, owner, site allocation, delivery, acceptance, rack, fabric, power, utilization or economics.",
            },
        },
        "energy_management": {
            "data_center_energy_management_certification": "ISO_50001",
            "all_buildings_including_data_centers_environmental_management": "ISO_14001",
            "monitored_or_optimized_components": ["chillers", "chilled_water_loop", "IT_room_temperature", "HVAC_fan_speed", "air_handling_units", "free_cooling"],
            "first_CUBE_Datacenter_competition": {"overall_energy_reduction_percent": 2.81, "building_energy_efficiency_improvement_percent": 28.25},
            "boundary": "Competition-period improvements are portfolio performance indicators, not a current per-site PUE, energy baseline or IT load.",
        },
        "accelerators": {
            "current_BNP_owned_or_leased_physical_GPU_model_count_by_site": "not_publicly_disclosed_or_established",
            "current_atNorth_hosted_BNP_GPU_count": "not_publicly_disclosed_or_established",
            "IBM_GPU_as_a_service_physical_inventory_allocated_to_BNP": "not_publicly_disclosed_or_established",
            "boundary": "HPC, high-density CPU servers, generative-AI language, direct liquid cooling and GPUs-as-a-service do not prove a physical BNP GPU inventory.",
        },
        "ownership_and_financials": {
            "ownership": "public_listed_group",
            "listing": "Euronext_Paris_BNP",
            "FY2025_EUR_million": {"revenues_net_banking_income": 51223, "operating_expenses": 31374, "gross_operating_income": 19849, "operating_income": 16296, "pre_tax_income": 17065, "net_income_group_share": 12225},
            "FY2025_ratios": {"cost_income_percent": 61.2, "RoTE_percent": 11.6, "CET1_percent": 12.6},
            "data_center_segment_and_site_revenue_operating_profit_cash_flow_capex_ROIC_and_customer_economics": "undisclosed",
            "boundary": "BNP Paribas banking results are not data-center earnings and cannot be allocated to Marne, Belgium, IBM Cloud or hosted atNorth workloads.",
        },
        "outlook": {
            "company_targets": {"2026_RoTE_percent": 12, "2024_to_2026_revenue_CAGR_percent_more_than": 5, "2028_RoTE_percent_more_than": 13, "2025_to_2028_net_income_group_share_CAGR_percent_more_than": 10, "2028_cost_income_percent_less_than": 56, "2027_and_2028_post_FRTB_CET1_percent": 13},
            "positive_signals": ["five_site_current_minimum_across_France_and_Belgium", "MAE2_capacity_expansion", "IBM_Cloud_dedicated_environment_through_2028", "atNorth_low_carbon_HPC_and_heat_reuse", "ISO_50001_energy_management", "FY2025_revenue_operating_income_and_net_income_growth", "strong_capital_ratio_and_raised_2028_targets"],
            "risk_signals": ["data_center_site_and_segment_economics_undisclosed", "current_site_MW_utilization_and_complete_BOM_undisclosed", "current_GPU_inventory_undisclosed", "MAE2_current_production_acceptance_unverified", "bank_operational_resilience_cybersecurity_and_regulatory_risk", "outsourced_hosting_and_cloud_dependency", "large_group_results_dominate_the_small_internal_infrastructure_perimeter"],
            "analytical_view": "BNP Paribas is an internal enterprise operator and hosted-compute customer, not a data-center pure play. The estate demonstrates resilient private-cloud, efficiency and circular-HPC demand, but investable returns are driven by banking and no site-level infrastructure economics are disclosed.",
        },
        "OSM_crosswalk": {
            "related_objects": len(records),
            "records": [{key: row.get(key) for key in ["OSM_ref", "OSM_name", "site_group", "classification", "physical_role", "OSM_footprint_area_m2", "current_BNP_site_count_inclusion"]} for row in records],
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [JRC_PARTICIPANTS, MRAE_MAE2, SEINE_ET_MARNE_MAE2, BNP_BELGIUM_2013, BNP_BELGIUM_JOB_2026, BPC_BELGIUM, DORSALYS_BELGIUM, SEMACO_BELGIUM, VAL_DE_REUIL_COUNCIL_2024, NDC_ROUEN, ARTELIA_NDC_ROUEN, BNP_ENERGY_EFFICIENCY, BNP_ATNORTH, ATNORTH_SWE01, ATNORTH_BNP, ATNORTH_DELL_CASE, BNP_IBM_CLOUD, BNP_2025_RESULTS, BNP_2025_RESULTS_PDF, BNP_2028_TRAJECTORY],
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
    registry_path = args.output_dir / "bnp_paribas_internal_and_hosted_data_center_registry.jsonl"
    summary_path = args.output_dir / "bnp_paribas_internal_and_hosted_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
