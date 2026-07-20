#!/usr/bin/env python3
"""Build a scope-preserving SRCE/HR-ZOO data-center and HPC registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


DATA_CENTERS = "https://www.srce.unizg.hr/podatkovni-centri"
HR_ZOO = "https://www.srce.unizg.hr/projekti/hr-zoo"
REPORT_2025 = "https://www.srce.unizg.hr/sites/default/files/srce/o-srcu/Izvjestaji_o_radu/srce_izvjestaj2025.pdf"
ADVANCED_COMPUTING = "https://www.srce.unizg.hr/en/advanced-computing"
DC_BROCHURE = "https://www.srce.unizg.hr/sites/default/files/srce/pzz/Brosura_DC_web.pdf"
FINANCIALS_2025 = "https://www.srce.unizg.hr/dokumenti/financijski-izvjestaj/2025"
FINANCIAL_RESULT_2025 = "https://www.srce.unizg.hr/sites/default/files/srce/o-srcu/financijski_izvjestaji/2025/Godi%C5%A1nji%20izvje%C5%A1taj/Izvje%C5%A1taj%20o%20prihodima%20i%20rashodima%2C%20primicima%20i%20izdacima%20za%202025.%20godinu.pdf"
PLAN_2026 = "https://www.srce.unizg.hr/sites/default/files/srce/o-srcu/planovi_rada/2026/Plan2026-Financijski_plan-20251222_ur.pdf"
PROCUREMENT_2026 = "https://www.srce.unizg.hr/sites/default/files/srce/javna-nabava/2026/Plan_nabava_2026/I.%20izmjena%20Plana%20nabava%202026_20260219.pdf"
LOCATIONS = "https://www.srce.unizg.hr/sites/default/files/srce/javna-nabava/2022/E-VV_11-01-2022-MK/prilog_2._prijedlog_okvirnog_sporazuma_odrzavanje_tehnickih_sustava_podatkovnih_centara_hr-zoo.pdf"
ABOUT = "https://www.srce.unizg.hr/en/about-srce"
PROJECT_OPEN_DAY = "https://www.srce.unizg.hr/srce-i-zajednica/otvorena-vrata-eu-projekata-20230630"


SITES = {
    "HR-ZOO_ZG1": {
        "city": "Zagreb", "address": "Josipa Marohnica 5", "gross_area_m2": 359,
        "computer_hall_area_m2": 182.28, "ICT_racks": 63, "designed_DC_power_kW": 350,
        "installed_generator": {"count": 2, "unit_kW": 352, "unit_kVA": 451},
        "installed_UPS": {"count": 4, "unit_kW": 160, "unit_kVA": 160},
        "cooling": {"count": 2, "unit_kW": 250}, "OSM_ref": "osm_node_13809854904",
    },
    "HR-ZOO_ZG2": {
        "city": "Zagreb", "address": "Borongajska cesta 83L", "gross_area_m2": 1317,
        "computer_hall_area_m2": 208.32, "ICT_racks": 35, "designed_DC_power_kW": 1100,
        "installed_generator": {"count": 1, "unit_kW": 1000, "unit_kVA": 1250},
        "installed_UPS": {"count": 2, "unit_kW": 500, "unit_kVA": 500},
        "cooling": {"count": 3, "unit_kW": 250},
        "DLC_system_kW": [100, 117, 117], "OSM_ref": "osm_node_13809854905",
    },
    "Srce_ZG3": {
        "city": "Zagreb", "address": "Borongajska cesta 83F_object_210", "gross_area_m2": 89.56,
        "computer_hall_area_m2": 52.71, "ICT_racks": 7, "designed_DC_power_kW": 50,
        "installed_generator": {"count": 1, "unit_kW": 80, "unit_kVA": 100},
        "installed_UPS": {"count": 2, "unit_kW": 40, "unit_kVA": 40},
        "cooling": {"count": 3, "unit_kW": 14}, "OSM_ref": None,
    },
    "HR-ZOO_OS": {
        "city": "Osijek", "address": "Petra Svacica 1c", "gross_area_m2": 411,
        "computer_hall_area_m2": 91.6, "ICT_racks": 10, "designed_DC_power_kW": 125,
        "installed_generator": {"count": 1, "unit_kW": 176, "unit_kVA": 220},
        "installed_UPS": {"count": 1, "unit_kW": 100, "unit_kVA": 100},
        "cooling": {"count": 1, "unit_kW": 100}, "OSM_ref": "osm_node_13809854906",
    },
    "HR-ZOO_RI": {
        "city": "Rijeka", "address": "Radmile Matejcic 2", "gross_area_m2": 213,
        "computer_hall_area_m2": 69.6, "ICT_racks": 10, "designed_DC_power_kW": 125,
        "installed_generator": {"count": 1, "unit_kW": 176, "unit_kVA": 220},
        "installed_UPS": {"count": 1, "unit_kW": 100, "unit_kVA": 100},
        "cooling": {"count": 1, "unit_kW": 100}, "OSM_ref": "osm_node_13809856865",
    },
    "HR-ZOO_ST": {
        "city": "Split", "address": "Rudera Boskovica 32", "gross_area_m2": 379,
        "computer_hall_area_m2": 84.22, "ICT_racks": 10, "designed_DC_power_kW": 125,
        "installed_generator": {"count": 1, "unit_kW": 176, "unit_kVA": 220},
        "installed_UPS": {"count": 1, "unit_kW": 100, "unit_kVA": 100},
        "cooling": {"count": 1, "unit_kW": 100}, "OSM_ref": "osm_node_13809859002",
    },
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for order, (site, values) in enumerate(SITES.items(), 1):
        osm_ref = values["OSM_ref"]
        source = osm.get(osm_ref) if osm_ref else None
        record = {
            "id": f"srce_{site.lower().replace('-', '_')}",
            "object_type": "DataCenterFacilityEvidence",
            "operator": "University_of_Zagreb_University_Computing_Centre_SRCE",
            "site": site,
            "country": "Croatia",
            "country_code": "HR",
            **{key: value for key, value in values.items() if key != "OSM_ref"},
            "OSM_ref": osm_ref,
            "OSM_in_source_sample": bool(source),
            "OSM_name": source.get("name") if source else None,
            "OSM_latitude": source.get("latitude") if source else None,
            "OSM_longitude": source.get("longitude") if source else None,
            "OSM_source_url": source.get("source_url") if source else None,
            "current_provider_roster_inclusion": True,
            "source_order": order,
            "accessed_on": accessed_on,
        }
        if site == "HR-ZOO_ZG2":
            record["current_compute"] = {
                "Supek": {"HPE_Cray": True, "processor_cores": 8384, "GPUs": 81, "GPU_model": "NVIDIA_A100_40GB", "compute_node_GPUs": 80, "access_node_GPUs": 1, "performance_PFLOPS": 1.25, "working_memory_TB": 32, "storage_usable_TB": 580},
                "Vrancic": {"OpenStack": True, "processor_cores": 11520, "GPUs": 16, "GPU_model": "NVIDIA_A100_40GB", "working_memory_TB_2025_report": 57},
                "physical_GPU_floor": 97,
                "site_evidence": "SRCE explicitly places Supek and Vrancic in HR-ZOO ZG2",
            }
        records.append(record)
    assert len(records) == 6
    assert sum(row["OSM_in_source_sample"] for row in records) == 5
    assert sum(row["designed_DC_power_kW"] for row in records) == 1875
    assert round(sum(row["computer_hall_area_m2"] for row in records), 2) == 688.73
    assert sum(row["ICT_racks"] for row in records) == 135
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    generator_kW = sum(row["installed_generator"]["count"] * row["installed_generator"]["unit_kW"] for row in records)
    generator_kVA = sum(row["installed_generator"]["count"] * row["installed_generator"]["unit_kVA"] for row in records)
    ups_kW = sum(row["installed_UPS"]["count"] * row["installed_UPS"]["unit_kW"] for row in records)
    ups_kVA = sum(row["installed_UPS"]["count"] * row["installed_UPS"]["unit_kVA"] for row in records)
    cooling_kW = sum(row["cooling"]["count"] * row["cooling"]["unit_kW"] for row in records)
    operating_revenue = 10_730_031.79
    operating_expenditure = 10_598_065.48
    return {
        "id": "srce_hr_zoo_data_center_hpc_summary_2026_07_19",
        "operator": "University of Zagreb University Computing Centre SRCE",
        "accessed_on": accessed_on,
        "portfolio": {
            "current_provider_reported_sites": 6,
            "sites": [row["site"] for row in records],
            "cities": sorted({row["city"] for row in records}),
            "OSM_operator_tagged_rows": 5,
            "off_sample_current_site": "Srce_ZG3",
            "current_provider_roster_match_rate_percent": round(5 / 6 * 100, 2),
            "HR_ZOO_project_sites": 5,
            "boundary": "The five OSM rows exactly match the five HR-ZOO sites. The current six-site SRCE roster also includes Srce ZG3, which is not present in the reviewed OSM operator sample.",
        },
        "current_2025_physical_totals": {
            "gross_area_m2": round(sum(row["gross_area_m2"] for row in records), 2),
            "computer_hall_area_m2": round(sum(row["computer_hall_area_m2"] for row in records), 2),
            "ICT_racks": sum(row["ICT_racks"] for row in records),
            "designed_DC_power_kW": sum(row["designed_DC_power_kW"] for row in records),
            "installed_generator_nameplate_kW": generator_kW,
            "installed_generator_nameplate_kVA": generator_kVA,
            "installed_UPS_nameplate_kW": ups_kW,
            "installed_UPS_nameplate_kVA": ups_kVA,
            "installed_air_or_water_cooling_nameplate_kW": cooling_kW,
            "ZG2_separately_reported_DLC_system_nameplate_kW": 334,
            "boundary": "Designed DC power, generator, UPS, cooling and DLC nameplates are different engineering denominators. They are not live IT load, usable redundancy-adjusted capacity or additive operating MW.",
        },
        "power_and_cooling_architecture": {
            "rack_power": "separate_A_and_B_branches_with_intelligent_metered_PDUs",
            "fault_tolerance": "subsystems_serviceable_and_testable_without_data_center_interruption",
            "UPS_minimum_full_load_autonomy_minutes": 6,
            "backup": "diesel_generator_sets_at_all_sites",
            "cooling_setpoints": {"cold_zone_C": 25, "relative_humidity_percent": 45, "UPS_battery_room_C": 22},
            "cooling_topology": "two_separate_pipe_routes_heat_exchangers_chilled_water_tanks_and_dual_variable_speed_pumps",
            "chiller_configuration": "2N_plus_1",
            "efficiency": ["hot_and_cold_aisles", "winter_free_cooling", "central_infrastructure_monitoring", "PUE_calculator"],
            "monitoring_points_more_than": 1600,
            "current_measured_site_PUE_WUE_energy_water_emissions_and_renewable_electricity": "not_disclosed_in_reviewed_sources",
            "complete_OEM_model_age_loading_acceptance_test_and_remaining_life_BOM": "not_disclosed",
        },
        "accelerators_and_compute": {
            "site": "HR-ZOO_ZG2_Borongaj",
            "Supek": {"HPE_Cray": True, "processor_cores": 8384, "reported_total_GPUs": 81, "GPU_model": "NVIDIA_A100_40GB", "compute_GPU_nodes": 20, "GPUs_per_compute_node": 4, "access_node_GPU": 1, "performance_PFLOPS": 1.25, "working_memory_TB": 32, "DLC_heat_removal_percent": 100},
            "Vrancic": {"OpenStack": True, "processor_cores": 11520, "GPU_nodes": 4, "GPUs_per_node": 4, "GPUs": 16, "GPU_model": "NVIDIA_A100_40GB", "working_memory_TB_2025_report": 57},
            "current_exact_physical_GPU_floor": 97,
            "GPU_floor_boundary": "Supek's 81 includes 80 GPUs in compute nodes plus one access-node GPU; it is not 81 plus 80. Vrancic's 16 are separate, and official evidence places both systems at ZG2.",
            "2025_use": {"Supek_GPU_hours": 482826, "Vrancic_vGPU_hours": 93846, "projects": 490, "institutions": 110},
            "complete_delivery_serial_rack_fabric_power_utilization_cost_and_remaining_life": "not_disclosed",
        },
        "services_and_network": {
            "inter_site_network_Gbps": 100,
            "distributed_object_storage_PB": 10,
            "hosted_infrastructure_examples": ["GEANT_node", "VeriSign_com_and_org_servers", "HAKOM_RIPE_and_eduroam_probes", "Cogent", "Hurricane_Electric", "CARNET"],
            "boundary": "Hosted third-party equipment and distributed storage do not become SRCE-owned accelerator or facility inventory.",
        },
        "ownership_and_project": {
            "institution": "University_of_Zagreb_University_Computing_Centre",
            "founded": 1971,
            "role": "national_public_academic_and_research_e_infrastructure_institution",
            "HR_ZOO_project_EUR": {"total": 24_616_609.76, "EU_ERDF": 20_924_118.30, "EU_share_percent": 85},
            "regional_site_building_context": "OS_RI_and_ST_are_in_spaces_owned_by_their_respective_universities",
            "site_land_building_and_equipment_title_by_asset": "not_completely_disclosed",
            "listed_equity": False,
        },
        "FY2025_public_budget_financials_EUR": {
            "operating_revenue": operating_revenue,
            "operating_expenditure": operating_expenditure,
            "derived_public_budget_operating_surplus": round(operating_revenue - operating_expenditure, 2),
            "total_revenue_and_receipts": 10_730_031.79,
            "total_expenditure_and_outlays": 11_068_303.30,
            "total_current_period_deficit": 338_271.51,
            "carried_surplus_before_current_deficit": 1_111_793.42,
            "surplus_available_next_period": 773_521.91,
            "operating_profit_EBIT_EBITDA_net_income": "not_applicable_or_not_reported_under_reviewed_public_budget_statement",
            "data_center_segment_and_site_revenue_cost_cash_flow_capex_and_ROIC": "undisclosed",
            "boundary": "The derived operating surplus is budget-accounting operating revenue minus operating expenditure, not commercial operating profit or EBIT. Total expenditure includes nonfinancial asset spending.",
        },
        "outlook": {
            "2026_plan": ["upgrade_ZG1_chillers", "upgrade_ZG1_and_ZG2_ventilation_security_and_environmental_monitoring", "install_second_ZG2_diesel_generator_for_2N_backup"],
            "planned_maintenance_procurement_EUR": {"VDC_hardware_software_warranty_and_licenses_payable_from_2027": 3_500_000, "Supek_and_Vrancic_payable_from_2027": 550_000},
            "new_AI_supercomputer_resource_target": 2027,
            "AI_resource_model_GPU_count_power_cost_committed_funding_and_procurement_award": "not_disclosed_or_established_in_final_plan",
            "positive_signals": ["six_current_sites", "detailed_power_and_cooling_disclosure", "97_current_A100_GPU_floor", "high_2025_GPU_use", "ZG2_power_resilience_upgrade", "planned_2027_AI_resource", "public_and_EU_infrastructure_funding"],
            "risk_signals": ["small_1_875_MW_designed_portfolio", "public_budget_dependency", "current_period_deficit", "site_PUE_WUE_energy_and_water_undisclosed", "full_asset_title_and_BOM_undisclosed", "AI_expansion_model_funding_and_delivery_not_yet_established", "no_listed_equity_or_data_center_segment_economics"],
            "analytical_view": "SRCE is a transparent national academic infrastructure operator and real AI-compute user, not an investable data-center company. Its value is demand and public-infrastructure evidence for HPE, NVIDIA, power, UPS and cooling suppliers rather than standalone equity earnings.",
        },
        "OSM_crosswalk": {
            "records": [{key: row.get(key) for key in ["site", "OSM_ref", "OSM_name", "OSM_latitude", "OSM_longitude", "OSM_in_source_sample", "designed_DC_power_kW", "ICT_racks"]} for row in records],
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [DATA_CENTERS, HR_ZOO, REPORT_2025, ADVANCED_COMPUTING, DC_BROCHURE, FINANCIALS_2025, FINANCIAL_RESULT_2025, PLAN_2026, PROCUREMENT_2026, LOCATIONS, ABOUT, PROJECT_OPEN_DAY],
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
    registry_path = args.output_dir / "srce_hr_zoo_data_center_hpc_registry.jsonl"
    summary_path = args.output_dir / "srce_hr_zoo_data_center_hpc_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
