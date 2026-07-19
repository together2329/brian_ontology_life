#!/usr/bin/env python3
"""Reconcile six EDF-labelled OSM objects to EDF's internal data-center estate.

EDF's current ISO 14001 certificate names two operating data-center sites: NOE
at Val-de-Reuil and Pacy-sur-Eure.  Five OSM objects are building or campus
geometries for those two sites; the sixth is a lone point beside RTE's national
control centre in Saint-Ouen and is not in the certified EDF roster.  The output
therefore preserves all six source objects without turning buildings, a works
polygon, or an uncorroborated point into six facilities.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path


AFNOR_2024 = "https://www.edf.fr/sites/groupe/files/2024-06/edfgroup_rse_certificat-iso14001_edf-sa_2024.pdf"
EDF_ENERGY_EFFICIENCY_2016 = "https://www.edf.fr/sites/groupe/files/contrib/groupe-edf/espaces-dedies/espace-medias/cp/2016/cp_edf_20160217_datacenters_vf.pdf"
EDF_GAIA_2019 = "https://www.edf.fr/sites/default/files/EDF_RechercheDeveloppement/Pages_CommunauteScientifique/Kiosque/2019.07.03_-_rd_inside_-_hpc.pdf"
EDF_SELENA_2025 = "https://www.edf.fr/groupe-edf/innover/rd-un-savoir-faire-mondial/toutes-les-actualites-de-la-rd/mise-en-service-du-supercalculateur-selena-une-nouvelle-etape-pour-le-calcul-haute-performance"
EDF_TRUSTED_CLOUD_2025 = "https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/tous-les-communiques-de-presse/edf-renforce-la-souverainete-de-ses-donnees-en-se-dotant-de-son-cloud-de-confiance-et-selectionne-bleu-et-s3ns-deux-acteurs-francais-de-l-hebergement-de-donnees"
TOP500_EDF = "https://top500.org/site/50679/"
ENIA_NOE = "https://www.enia.fr/en/projet/edf-projet-noe"
CLIMATELEC_PACY = "https://www.climatelec.fr/sites/climatelec/files/2024-07/C1%20C2%20C3%20EDF%20%20Data%20Center.pdf"
EDF_2025_RESULTS = "https://www.edf.fr/en/2025-annual-results"
EDF_2025_RESULTS_PDF = "https://www.edf.fr/sites/groupe/files/2026-02/PR%202025%20annual%20results.pdf"
EDF_OWNERSHIP = "https://www.edf.fr/en/the-edf-group/dedicated-sections/investors/articles-of-association"
EDF_DATA_CENTER_R_AND_D = "https://www.edf.fr/groupe-edf/inventer-l-avenir-de-l-energie/rd-un-savoir-faire-mondial/les-pepites-de-la-rd/data-centers/les-enjeux"
EDF_BOUCHAIN = "https://www.edf.fr/en/the-edf-group/dedicated-sections/journalists/all-press-releases/edf-selects-softbank-group-as-preferred-bidder-for-the-development-of-a-large-scale-data-center-at-its-bouchain-site"
EDF_CREYS_MEPIEU = "https://www.edf.fr/en/the-edf-group/supporting-our-clients/cei-data-centers"
EDF_DATA4_CAPN = "https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/tous-les-communiques-de-presse/data4-signe-un-accord-avec-edf-pour-lapprovisionnement-en-electricite-bas-carbone-de-ses-datacenters-en-france"


EDF_OSM_RECONCILIATION = {
    "osm_way_226250681": {
        "site": "Pacy-sur-Eure",
        "classification": "current_official_enterprise_data_center_site_representative",
        "count": True,
        "physical_role": "main_mapped_data_center_building",
    },
    "osm_way_226246636": {
        "site": "Pacy-sur-Eure",
        "classification": "ancillary_building_within_official_data_center_site_not_separate_facility",
        "count": False,
        "physical_role": "small_campus_building_geometry",
    },
    "osm_way_226246780": {
        "site": "Pacy-sur-Eure",
        "classification": "ancillary_building_within_official_data_center_site_not_separate_facility",
        "count": False,
        "physical_role": "small_campus_building_geometry",
    },
    "osm_way_226247994": {
        "site": "Pacy-sur-Eure",
        "classification": "ancillary_building_within_official_data_center_site_not_separate_facility",
        "count": False,
        "physical_role": "small_campus_building_geometry",
    },
    "osm_way_952744491": {
        "site": "NOE_Val-de-Reuil",
        "classification": "current_official_enterprise_data_center_site_representative",
        "count": True,
        "physical_role": "works_or_campus_boundary_not_data_hall_area",
    },
    "osm_node_8297551605": {
        "site": "Saint-Ouen-sur-Seine_candidate",
        "classification": "uncorroborated_OSM_point_not_in_current_certified_EDF_data_center_roster",
        "count": False,
        "physical_role": "lone_point_beside_RTE_national_control_center",
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    pacy_main = osm["osm_way_226250681"]
    records = []
    for position, (osm_ref, reconciliation) in enumerate(EDF_OSM_RECONCILIATION.items(), 1):
        source = osm[osm_ref]
        record = {
            "id": f"edf_{osm_ref}",
            "object_type": "DataCenterFacilityOrGeometryEvidence",
            "operator": "EDF",
            "country": "France",
            "country_code": "FR",
            "site_group": reconciliation["site"],
            "classification": reconciliation["classification"],
            "physical_role": reconciliation["physical_role"],
            "current_verified_site_count_inclusion": reconciliation["count"],
            "OSM_ref": osm_ref,
            "OSM_name": source.get("name"),
            "OSM_latitude": source["latitude"],
            "OSM_longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_source_url": source["source_url"],
            "source_order": position,
            "accessed_on": accessed_on,
        }
        if reconciliation["site"] == "Pacy-sur-Eure":
            record["official_roster_name"] = "Datacenter de Pacy-sur-Eure"
            record["official_roster_address"] = "141 rue Isambard, FR-27120 Pacy-sur-Eure"
            record["distance_to_OSM_main_building_centroid_m"] = round(
                distance_m(source["latitude"], source["longitude"], pacy_main["latitude"], pacy_main["longitude"]), 1
            )
            record["counting_boundary"] = "Four nearby OSM building geometries form one certified Pacy data-center site; footprint area is not data-hall or IT area."
        elif reconciliation["site"] == "NOE_Val-de-Reuil":
            record["official_roster_name"] = "Datacenter NOE"
            record["official_roster_address"] = "2 voie de l'Orée, FR-27100 Val-de-Reuil"
            record["current_OSM_API_geometry_context"] = "man_made=works"
            record["counting_boundary"] = "The 104,506.128-square-metre OSM works polygon is a campus or industrial boundary, not gross building, server-room or IT area."
        else:
            record["official_roster_name"] = None
            record["official_roster_address"] = None
            record["counting_boundary"] = "A lone 2021 OSM point beside RTE's national electricity-control centre is absent from EDF's current certified two-site roster and adds no facility count."
        records.append(record)
    assert len(records) == 6
    assert sum(row["current_verified_site_count_inclusion"] for row in records) == 2
    assert sum(row["site_group"] == "Pacy-sur-Eure" for row in records) == 4
    assert max(row.get("distance_to_OSM_main_building_centroid_m", 0) for row in records) < 70
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "edf_internal_data_center_summary_2026_07_19",
        "operator": "EDF",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "related_OSM_rows": len(records),
            "current_official_certified_data_center_sites": 2,
            "current_official_site_names": ["Datacenter NOE", "Datacenter de Pacy-sur-Eure"],
            "Pacy_OSM_building_geometries": 4,
            "NOE_OSM_works_or_campus_geometries": 1,
            "uncorroborated_Saint_Ouen_OSM_points_excluded": 1,
            "boundary": "Five OSM objects reconcile to two current AFNOR-listed EDF internal data-center sites. Buildings and a works polygon are not separately counted; the sixth point lacks current official corroboration.",
        },
        "site_engineering": {
            "NOE": {
                "location": "Val-de-Reuil_France",
                "official_address": "2 voie de l'Orée, FR-27100 Val-de-Reuil",
                "role": "internal_EDF_Group_data_center_and_HPC_host",
                "design_firm_published_project": {"completed": 2010, "gross_project_area_m2": 16000, "server_area_m2": 4600, "cost_EUR_million_ex_tax": 69},
                "2016_availability_estimate_percent": 99.995,
                "2016_features": ["fiber_connections", "high_hosting_capacity_for_EDF_applications", "very_high_speed_communications"],
                "current_HPC": {
                    "location_evidence": "TOP500_EDF_site_Val_de_Reuil",
                    "systems": [
                        {"name": "CRONOS", "vendor": "Bull", "platform": "BullSequana_X", "CPU": "Intel_Xeon_Platinum_8260", "cores": 81600, "Rmax_GFLOPS": 4299330, "Rpeak_GFLOPS": 7136870, "deployed": 2021},
                        {"name": "SELENA", "vendor": "Bull", "platform": "BullSequana_XH3000", "CPU": "AMD_EPYC_9354", "cores": 107904, "Rmax_GFLOPS": 5420100, "Rpeak_GFLOPS": 5501180, "commissioned": 2025},
                    ],
                    "combined_EDF_group_compute_power_petaflops_more_than": 15,
                },
                "current_cooling": {"SELENA": "direct_liquid_cooling", "SELENA_PUE_before": 1.4, "SELENA_PUE_after_approx": 1.04},
                "historical_accelerator_inventory": {"system": "GAIA", "installed": 2019, "replaced_by_SELENA": 2025, "GPU_model": "NVIDIA_V100", "GPU_count": 64, "GPU_nodes": 32, "racks_42U": 37, "water_door_cooled_racks": 18, "air_cooled_cold_aisle_racks": 19, "storage_PB": 15},
                "current_GPU_model_count_and_owner": "not_publicly_disclosed; the 64-V100 GAIA count is historical and must not be presented as current after SELENA replaced GAIA",
            },
            "Pacy_sur_Eure": {
                "official_address": "141 rue Isambard, FR-27120 Pacy-sur-Eure",
                "role": "internal_EDF_Group_data_center",
                "OSM_main_building_footprint_m2": 7806.54,
                "OSM_three_small_building_footprint_checksum_m2": 1350.111,
                "cooling_modernization": {
                    "contractor_context": "Dalkia_group_with_Climatelec_reference",
                    "scope": "migration_to_multiple_chillers_and_chilled_water_air_conditioning_cabinets_with_capacity_and_continuity_upgrade",
                    "preinsulated_PE_pipe_metres": 1000,
                    "roof_304L_stainless_pipe_metres": 2500,
                    "pipe_diameter_range": "DN100_to_DN350",
                    "project_duration_months": 24,
                    "contractor_revenue_EUR_million": 1.8,
                    "work_hours": 12000,
                },
                "current_GPU_model_count_and_owner": "not_publicly_disclosed_or_established",
            },
            "shared_2015_energy_context": {"two_sites_annual_energy_GWh": 70, "boundary": "Historical portfolio energy consumption is not IT load, power capacity, current energy, or a site allocation."},
            "complete_current_grid_feed_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_redundancy_loading_acceptance_age_and_remaining_life": "undisclosed",
            "operating_energized_available_contracted_customer_accepted_leased_utilized_billed_peak_and_actual_IT_MW_by_site": "undisclosed",
            "current_rack_count_server_count_and_measured_site_PUE_WUE_water": "undisclosed_except_SELENA_system_PUE_and_historical_GAIA_racks",
        },
        "digital_strategy": {
            "2025_private_cloud_share_of_EDF_data_near_percent": 80,
            "trusted_cloud_providers_selected": ["BLEU", "THALES_S3NS"],
            "boundary": "Cloud migration and service-provider selection do not identify additional EDF-owned physical sites or transfer ownership of NOE and Pacy.",
        },
        "ownership_and_financials": {
            "ownership": "100_percent_French_State",
            "public_listing": "delisted_from_Euronext_Paris_on_2023_06_08",
            "FY2025_EUR_million": {"sales": 113266, "EBITDA": 29256, "operating_profit": 13104, "net_income_group_share": 8367, "operating_cash_flow": 9600, "net_financial_debt": 51500},
            "FY2024_comparatives_EUR_million": {"sales": 118690, "EBITDA": 36523, "operating_profit": 18327, "net_income_group_share": 11406, "net_financial_debt": 54300},
            "data_center_segment_and_site_revenue_operating_profit_capex_customer_concentration_and_ROIC": "undisclosed",
            "boundary": "EDF Group energy and network earnings are not internal-data-center earnings and are not allocated to NOE, Pacy, HPC systems, or external data-center power customers.",
        },
        "external_data_center_growth_exposure": {
            "Data4_CAPN": {"allocated_nuclear_power_MW": 40, "term_years": 12, "first_delivery": 2026, "forecast_annual_volume_GWh_approx": 230},
            "Bouchain_SoftBank": {"planned_data_center_MW": 400, "state": "preferred_bidder_selected_2026_05_30_not_operating"},
            "Creys_Mepieu": {"state": "2026_call_for_expressions_of_interest_for_large_scale_data_center_under_building_lease"},
            "six_site_program": "EDF said six former industrial sites would be proposed by 2026; individual proposals, grid connection potential and operator projects are not current EDF-operated data centers.",
            "economics_boundary": "Contract prices, EDF revenue, margin, required grid capex and returns are undisclosed. Planned customer MW and site potential are not internal operating data-center MW.",
        },
        "outlook": {
            "positive_signals": ["two_current_certified_internal_sites", "current_15_plus_petaflop_HPC_platform", "SELENA_direct_liquid_cooling_and_approx_1_04_PUE", "trusted_cloud_hybrid_strategy", "long_term_nuclear_power_contracts", "brownfield_industrial_land_and_grid_connection_strategy", "FY2025_positive_operating_cash_flow_and_lower_net_financial_debt"],
            "risk_signals": ["FY2025_sales_EBITDA_and_operating_profit_declined", "large_nuclear_and_grid_capital_program", "state_policy_and_regulatory_exposure", "internal_data_center_economics_undisclosed", "site_level_MW_utilization_and_complete_BOM_undisclosed", "current_GPU_count_undisclosed", "external_data_center_projects_are_pre_operating_and_execution_dependent"],
            "analytical_view": "EDF is not a data-center pure play. Its strongest AI-infrastructure exposure is as a low-carbon electricity producer, long-term supplier, grid and brownfield-site partner, while NOE and Pacy provide internal operating expertise. The opportunity is potentially large, but contract economics and data-center-specific earnings are not disclosed and the group outlook remains dominated by nuclear, network, market-price and capital-execution risks.",
        },
        "OSM_crosswalk": {
            "related_objects": len(records),
            "records": [{key: row.get(key) for key in ["OSM_ref", "OSM_name", "site_group", "classification", "physical_role", "OSM_footprint_area_m2", "current_verified_site_count_inclusion"]} for row in records],
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [AFNOR_2024, EDF_ENERGY_EFFICIENCY_2016, EDF_GAIA_2019, EDF_SELENA_2025, EDF_TRUSTED_CLOUD_2025, TOP500_EDF, ENIA_NOE, CLIMATELEC_PACY, EDF_2025_RESULTS, EDF_2025_RESULTS_PDF, EDF_OWNERSHIP, EDF_DATA_CENTER_R_AND_D, EDF_BOUCHAIN, EDF_CREYS_MEPIEU, EDF_DATA4_CAPN],
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
    registry_path = args.output_dir / "edf_internal_data_center_registry.jsonl"
    summary_path = args.output_dir / "edf_internal_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
