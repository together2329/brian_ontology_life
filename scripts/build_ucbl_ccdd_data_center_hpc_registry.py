#!/usr/bin/env python3
"""Build a scope-preserving UCBL/INSA Lyon CCDD and P2CHPD registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


PROJECT_PAGE = "https://www.univ-lyon1.fr/actualites/le-centre-de-calcul-et-de-donnees-lyonytech-la-doua-ccdd-entre-dans-sa-phase-de-construction"
PRESS_KIT = "https://www.univ-lyon1.fr/medias/fichier/dp-data-center-lyontech-la-doua-avril2023_1682587936670-pdf?ID_FICHE=105213&INLINE=FALSE"
SUSTAINABILITY_STRATEGY = "https://icap-formations.univ-lyon1.fr/pluginfile.php/18697/mod_resource/content/1/SD%20DDRSE%20UCBL%202035%20-%20Former%2C%20innover%20et%20transformer%20pour%20un%20avenir%20durable%20_%2011%202024%20%281%29.pdf"
P2CHPD = "https://p2chpd.univ-lyon1.fr/"
P2CHPD_MANUAL = "https://p2chpd.univ-lyon1.fr/manual"
CISR = "https://www.univ-lyon1.fr/universite/organisation/centre-inter-etablissement-pour-les-services-reseaux-cisr"
ANNUAL_REPORT_2023 = "https://www.univ-lyon1.fr/medias/fichier/2023-rapportactivite-web_1734690509480-pdf"
CURRENT_SCALE_2025 = "https://master-info.univ-lyon1.fr/SRS/documents/2025_08_29_presentationSRS-rentree.key.pdf"


OSM_COMPONENTS = {
    "osm_way_1288320747": "support_or_technical_structure_exact_role_unverified",
    "osm_way_1342103498": "support_or_technical_structure_exact_role_unverified",
    "osm_way_1342103499": "main_CCDD_building_geometry",
    "osm_way_1342103500": "support_or_technical_structure_exact_role_unverified",
    "osm_way_1342103501": "support_or_technical_structure_exact_role_unverified",
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
    records = []
    for order, (osm_id, component_role) in enumerate(OSM_COMPONENTS.items(), 1):
        row = osm[osm_id]
        is_main = osm_id == "osm_way_1342103499"
        records.append(
            {
                "id": f"ucbl_ccdd_{osm_id}",
                "object_type": "DataCenterFacilityComponentEvidence",
                "operator_tag_raw": row.get("operator"),
                "operator_boundary": "UCBL_project_owner_and_CISR_operator_with_INSA_Lyon_joint_project_carrier",
                "site_group": "CCDD_LyonTech_La_Doua",
                "site_name": "Centre de Calculs et de Donnees LyonTech-la Doua",
                "country": "France",
                "country_code": "FR",
                "city": "Villeurbanne",
                "OSM_ref": osm_id,
                "OSM_name": row.get("name"),
                "OSM_latitude": row.get("latitude"),
                "OSM_longitude": row.get("longitude"),
                "OSM_footprint_area_m2": row.get("footprint_area_m2"),
                "OSM_building_levels": row.get("building_levels"),
                "OSM_source_url": row.get("source_url"),
                "component_role": component_role,
                "current_facility_group_inclusion": True,
                "current_provider_facility_count": is_main,
                "lifecycle_as_of_2026_07_19": "current_physical_facility_with_2025_2026_migration_window_and_complete_production_acceptance_undisclosed",
                "source_order": order,
                "accessed_on": accessed_on,
            }
        )
    assert len(records) == 5
    assert sum(row["current_provider_facility_count"] for row in records) == 1
    assert round(sum(row["OSM_footprint_area_m2"] for row in records), 3) == 862.953
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "ucbl_insa_ccdd_data_center_hpc_summary_2026_07_19",
        "operator_boundary": "Universite_Claude_Bernard_Lyon_1_project_owner_CISR_operator_and_INSA_Lyon_joint_project_carrier",
        "accessed_on": accessed_on,
        "physical_site_and_OSM_crosswalk": {
            "current_facility_groups": 1,
            "facility_group": "CCDD_LyonTech_La_Doua",
            "operator_tagged_OSM_geometries": 5,
            "main_building_geometries": 1,
            "support_or_technical_geometries_exact_role_unverified": 4,
            "OSM_total_footprint_area_m2": 862.953,
            "main_geometry": "osm_way_1342103499",
            "main_geometry_OSM_levels": 3,
            "boundary": "The five adjacent identically named OSM ways are components of one CCDD facility group, not five data centers. OSM footprint and levels are mapping evidence, not provider-certified gross floor area or live capacity.",
        },
        "project_scale_and_lifecycle": {
            "official_project_gross_floor_area_m2": 3280,
            "press_kit_storey_wording": "one_upper_storey_with_ground_and_roof_technical_or_office_spaces",
            "phase_one_racks": 150,
            "ultimate_racks": 300,
            "project_configuration": "two_150_rack_tranches",
            "phase_one_project_cost_EUR_million": 11.1,
            "UCBL_role": "project_owner_maitre_d_ouvrage",
            "joint_project_carriers": ["Universite_Claude_Bernard_Lyon_1", "INSA_Lyon"],
            "operating_service": "Centre_inter_etablissement_pour_les_services_reseaux_CISR",
            "timeline_evidence": {
                "2023_press_kit_planned_exploitation": "summer_2024",
                "2023_annual_report_planned_production": "October_2024",
                "November_2024_strategy_planned_delivery": "early_2025",
                "current_P2CHPD_page_migration_window": "2025_and_2026",
                "complete_current_acceptance_migration_and_rack_fill": "not_disclosed_or_independently_established",
            },
            "boundary": "The EUR11.1 million amount is first-phase project cost, not annual capex, revenue or valuation. The 150 and 300 rack values are phase and ultimate design envelopes, not current installed, accepted, occupied or utilized rack counts. The official 3,280-square-metre floor-area disclosure is not interchangeable with the 862.953-square-metre OSM footprint sum, and the press-kit storey wording is not reconciled to the OSM three-level tag.",
        },
        "power_network_and_resilience": {
            "published_design": [
                "redundant_electrical_feed_architecture",
                "dual_high_voltage_adduction",
                "dual_telecommunications_network_adduction",
                "central_and_remote_supervision",
            ],
            "current_grid_or_IT_MW": "undisclosed",
            "undisclosed": [
                "grid_service_voltage_and_contract_capacity",
                "substation_transformer_switchgear_busbar_and_PDU_counts_ratings_OEMs",
                "UPS_battery_counts_ratings_topology_runtime_OEMs_and_loading",
                "generator_counts_ratings_OEMs_fuel_runtime_and_acceptance_tests",
                "energized_available_allocated_occupied_peak_actual_and_billed_IT_load",
            ],
            "boundary": "Redundant or dual-feed architecture does not establish an operating MW value. A third-party 5 MW directory claim was excluded because no reviewed official source supported its denominator or current state.",
        },
        "cooling_energy_and_environment": {
            "published_design": [
                "optimized_high_temperature_chilled_water",
                "adiabatic_chiller_free_cooling",
                "hot_and_cold_aisle_airflow_containment",
                "variable_flow_control",
                "secondary_loop_heat_recovery_offered_to_internal_or_nearby_buildings",
            ],
            "published_water_regime_C": [17, 22],
            "dispersed_legacy_baseline_PUE": 2.15,
            "CCDD_target_PUE": 1.30,
            "legacy_baseline_annual_electricity_GWh": 12.6,
            "CCDD_target_annual_electricity_GWh": 7.6,
            "planned_annual_saving_GWh": 5.0,
            "legacy_baseline_GHG_tCO2e": 1056,
            "CCDD_target_GHG_tCO2e": 638,
            "planned_GHG_saving_tCO2e": 418,
            "planned_GHG_reduction_percent": 40,
            "current_measured_CCDD_PUE_WUE_energy_water_emissions_heat_reuse_and_renewable_matching": "not_disclosed",
            "complete_chiller_pump_heat_exchanger_CRAH_CRAC_CDU_dry_cooler_and_water_BOM": "not_disclosed",
            "boundary": "PUE 1.30, 7.6 GWh and 638 tCO2e are project targets against the prior dispersed estate, not current metered CCDD performance. Planned savings are never added to or substituted for actual consumption.",
        },
        "HPC_and_accelerators": {
            "P2CHPD_role": "UCBL_hosted_academic_HPC_centre_attached_to_CCDD",
            "current_page_migration_window": "resources_to_be_migrated_in_2025_and_2026",
            "historical_manual_snapshot": {
                "document_version": "2021-02-10",
                "last_updated": "2021-05-18",
                "GPU_partition_servers": 8,
                "GPU_model_or_label_families_listed": ["A100", "C6000_unresolved_label", "RTX3090"],
                "separate_legacy_parallel_GPU_models": ["NVIDIA_K20m", "NVIDIA_K80"],
                "interconnect_examples": ["10GbE", "InfiniBand_FDR"],
            },
            "current_exact_physical_GPU_or_accelerator_count_at_CCDD": "undisclosed",
            "current_model_count_owner_rack_site_delivery_acceptance_fabric_power_utilization_cost_and_remaining_life": "undisclosed",
            "boundary": "The dated manual proves a historical P2CHPD equipment snapshot, not current 2026 inventory. It gives eight servers in a GPU partition but no GPU-unit count and does not establish that every listed accelerator has migrated to or is operating in CCDD.",
        },
        "security_and_certification": {
            "planned_or_in_progress_in_2024": ["ISO_27001", "HDS_health_data_hosting", "DGRI_labelling", "ZRR_restricted_zone"],
            "current_achieved_certificate_identifiers_scope_and_expiry": "not_established_in_reviewed_sources",
            "boundary": "Design intent and an in-progress certification process are not recorded as achieved certification.",
        },
        "UCBL_financial_boundary_EUR": {
            "FY2023_budget_execution": "more_than_500_million",
            "FY2023_accounting_result_million": -0.3,
            "FY2023_self_financing_capacity_million": 16.7,
            "FY2023_own_source_resources_million_more_than": 102,
            "FY2023_investment_expenditure_million": 47,
            "2025_current_university_budget_million_more_than": 420,
            "commercial_revenue_operating_profit_EBIT_EBITDA_and_net_income": "not_comparable_or_not_reported_in_reviewed_public_university_sources",
            "CCDD_revenue_cost_energy_cost_cash_flow_capex_chargeback_customer_concentration_ROIC_and_social_return": "undisclosed",
            "boundary": "UCBL is a public university. Budget execution, accounting result and self-financing capacity are not commercial company revenue, operating profit or EBITDA, and none is allocated to CCDD.",
        },
        "outlook": {
            "institutional_target": "converge_100_percent_of_UCBL_digital_infrastructure_into_CCDD",
            "positive_signals": [
                "current_physical_facility_and_active_2025_2026_migration_window",
                "150_rack_first_phase_and_300_rack_ultimate_design",
                "dual_power_and_network_adduction",
                "target_PUE_1_30_and_5GWh_annual_saving",
                "academic_HPC_and_health_data_demand",
            ],
            "risk_signals": [
                "complete_production_acceptance_and_current_rack_fill_undisclosed",
                "current_IT_MW_and_full_power_cooling_BOM_undisclosed",
                "current_GPU_count_and_migration_state_undisclosed",
                "target_environmental_metrics_not_current_measurement",
                "current_certification_achievement_not_established",
                "public_budget_dependency_and_no_direct_equity_security",
                "CCDD_segment_economics_undisclosed",
            ],
            "analytical_view": "CCDD is a real public academic consolidation and efficiency project, not an investable data-center company. It is evidence of institutional HPC, electrical-resilience and cooling demand, but supplier and equity conclusions require awarded contracts and current installed-load disclosure.",
        },
        "OSM_crosswalk": {
            "records": records,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [
            PROJECT_PAGE,
            PRESS_KIT,
            SUSTAINABILITY_STRATEGY,
            P2CHPD,
            P2CHPD_MANUAL,
            CISR,
            ANNUAL_REPORT_2023,
            CURRENT_SCALE_2025,
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
    registry_path = args.output_dir / "ucbl_ccdd_data_center_hpc_registry.jsonl"
    summary_path = args.output_dir / "ucbl_ccdd_data_center_hpc_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
