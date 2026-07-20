#!/usr/bin/env python3
"""Build a scope-safe Rostelecom / RTK-COD facility-evidence registry.

RTK-COD publishes a current portfolio headline but not a complete current
facility-by-facility roster.  This builder therefore records only facilities,
phases, clusters and non-production infrastructure that can be tied to an
official publication.  It preserves rack, total-power, installed-power,
per-rack, cloud-resource, certification and lifecycle denominators rather than
turning them into a false current IT-load or GPU census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


PORTFOLIO_2026 = "https://www.company.rt.ru/projects/news/d478049/"
ANNUAL_2025 = "https://www.company.rt.ru/ir/agm/files/2025/Annual_report_2025_rus.pdf"
ANNUAL_2024 = "https://www.company.rt.ru/ir/agm/files/2024/Annual_report_2024_rus.pdf"
CEO_2026 = "https://www.company.rt.ru/press/news/d477081/"
FY2025_RESULTS = "https://www.company.rt.ru/press/news_ir/news/d477115/"
Q1_2026_RESULTS = "https://www.company.rt.ru/press/news_ir/news/d478131/"
VTB_TRANSACTION = "https://www.company.rt.ru/press/news/d457686/_ftn2"
NIZHNY = "https://www.company.rt.ru/press/news_project/d473377/"
UDOMLYA = "https://www.company.rt.ru/projects/digital_economy_rf/data-centers/d473700/"
EKATERINBURG_2021 = "https://www.company.rt.ru/projects/news/d461353/"
EKATERINBURG_2025 = "https://www.company.rt.ru/press/news_fill/ural/d473668/"
ST_PETERSBURG = "https://www.company.rt.ru/projects/news/d457489/"
NORD_6 = "https://www.company.rt.ru/press/news_ir/news/d460740/"
OSTAPOVSKY = "https://www.company.rt.ru/projects/news/d455806/"
MEDVEDKOVO_CLOUD = "https://www.company.rt.ru/press/news/d473293/"
MEDVEDKOVO_RD = "https://www.company.rt.ru/projects/news/d474835/"
TURBO_GPU_2025 = "https://www.company.rt.ru/press/news/d476261/"
TURBO_GPU_2026 = "https://www.company.rt.ru/press/news/d479061/"
TURBO_INVESTMENT = "https://www.company.rt.ru/press/news/d474987/"
UPTIME_RUSSIA = "https://uptimeinstitute.com/uptime-institute-awards/country/id/RU"
UPTIME_ROSTELECOM = "https://uptimeinstitute.com/uptime-institute-awards/client/rostelecom/209"


def record(
    record_id: str,
    name: str,
    evidence_granularity: str,
    city: str,
    lifecycle: str,
    published_metrics: dict,
    power_and_backup: dict,
    cooling: dict,
    source_urls: list[str],
    address: str | None = None,
    publication_conflicts: list[str] | None = None,
    boundary: str | None = None,
) -> dict:
    return {
        "id": f"rtk_cod_{record_id}",
        "name": name,
        "country_code": "RU",
        "city": city,
        "address": address or "undisclosed_in_reviewed_source",
        "evidence_granularity": evidence_granularity,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "current_operator_or_platform": "RTK_COD_group",
        "published_metrics": published_metrics,
        "electrical_and_backup_power_evidence": power_and_backup,
        "cooling_evidence": cooling,
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": publication_conflicts or [],
        "boundary": boundary or "Published facility evidence does not establish current utilized IT load, customer acceptance, billing, site economics or GPU inventory.",
        "source_urls": list(dict.fromkeys(source_urls)),
    }


FACILITY_EVIDENCE = [
    record(
        "nizhny_novgorod",
        "Nizhny Novgorod",
        "current_provider_facility",
        "Nizhny_Novgorod",
        "operating_since_2025_05",
        {
            "provider_network_ordinal_at_launch": 25,
            "gross_floor_area_sqm": 3539,
            "machine_halls": 4,
            "rack_places": 401,
            "installed_power_mw_published_term": 5,
        },
        {
            "independent_power_routes": 2,
            "guaranteed_and_uninterruptible_power": True,
            "diesel_generation": "present_count_rating_and_runtime_undisclosed",
        },
        {"redundant_cooling": True, "technology_OEM_count_rating_and_water_use": "undisclosed"},
        [NIZHNY, ANNUAL_2025, PORTFOLIO_2026],
        "35 Fedoseenko Street, Nizhny Novgorod",
        boundary="The provider's 5-MW Russian term is retained as installed power; it is not relabelled IT load, utility feed, UPS output or actual draw. Two OSM building footprints at the address are one facility candidate, not two provider data centers.",
    ),
    record(
        "udomlya_3",
        "Udomlya-3",
        "operating_facility_phase",
        "Udomlya",
        "operating_since_2025_06",
        {
            "machine_halls": 4,
            "rack_places": 820,
            "published_power_per_rack_kw": 5.4,
            "derived_rack_nameplate_product_mw": 4.428,
            "phase_construction_investment_RUB_billion": 2,
            "possible_future_phases_4_and_5_racks": 1640,
            "provider_possible_delivery_period_months": 12,
        },
        {"grid_UPS_battery_generator_fuel_details": "undisclosed_in_reviewed_source"},
        {"technology_redundancy_capacity_and_water": "undisclosed_in_reviewed_source"},
        [UDOMLYA, ANNUAL_2025, PORTFOLIO_2026],
        publication_conflicts=["The 4.428-MW figure is the arithmetic product of 820 racks and 5.4 kW per rack; it is not a provider-stated facility, IT-load or actual-demand value."],
        boundary="Phases 4 and 5 are described as a rapid-expansion option on prepared structures, not committed, financed, operating or leased capacity.",
    ),
    record(
        "ekaterinburg",
        "Ekaterinburg campus",
        "campus_and_phase_evidence",
        "Ekaterinburg",
        "two_phases_operating_third_phase_high_readiness",
        {
            "first_phase_racks_historical": 216,
            "first_phase_total_power_mw_historical": 2,
            "second_phase_racks_historical_plan": 216,
            "second_phase_total_power_mw_historical_plan": 2,
            "operating_two_phase_capacity_2025": "more_than_400_racks",
            "third_phase_racks_2025_article": 216,
            "third_phase_racks_2024_annual_report": 214,
            "third_phase_2025_annual_report_rounded_racks": 200,
            "third_phase_prebooked_percent_2025_article": 60,
            "third_phase_planned_service_by": "2026-12-31",
        },
        {"critical_power_redundancy": True, "exact_current_campus_grid_UPS_generator_topology": "undisclosed"},
        {"critical_cooling_redundancy": True, "technology_capacity_and_OEM": "undisclosed"},
        [EKATERINBURG_2021, EKATERINBURG_2025, ANNUAL_2024, ANNUAL_2025, PORTFOLIO_2026],
        publication_conflicts=["Official publications describe the third phase as 214, 216 and rounded 0.2-thousand racks at different dates; all values are retained."],
        boundary="Historical 2-MW phase figures use an undefined total-power denominator and are not added into current IT load. High readiness and reservation are not operation or billing.",
    ),
    record(
        "st_petersburg",
        "Saint Petersburg data center and second-phase program",
        "operating_facility_and_planned_phase",
        "Saint_Petersburg",
        "base_facility_operating_second_phase_high_readiness",
        {
            "base_facility_racks": 800,
            "base_facility_total_power_kw_published_term": 7400,
            "base_facility_machine_halls": 4,
            "base_facility_racks_per_hall": 200,
            "base_facility_area_sqm": 4266,
            "second_phase_2025_annual_report_rounded_racks": 900,
            "second_phase_planned_service_by": "2026-12-31",
        },
        {"independent_power_routes": True, "exact_grid_UPS_battery_generator_fuel_details": "undisclosed"},
        {"infrastructure_redundancy": True, "technology_capacity_OEM_and_water": "undisclosed"},
        [ST_PETERSBURG, ANNUAL_2025, PORTFOLIO_2026],
        "43 Zhukova Street, Saint Petersburg",
        boundary="The 7,400-kW publication term is total facility power, not proven IT load or actual draw. The 0.9-thousand-rack second phase remains planned/high-readiness in the end-2025 report.",
    ),
    record(
        "medvedkovo_2",
        "Medvedkovo-2",
        "acquired_facility_and_cloud_location",
        "Moscow",
        "acquired_2024_cloud_location_launched_2025",
        {
            "acquired_rack_capacity_low_publication": 4000,
            "acquired_rack_capacity_high_publication": 4800,
            "published_rack_power_kw": 5,
            "incoming_power_mw": 36,
            "area_sqm": 24000,
            "preliminary_reservation_percent_at_2024_report": 100,
            "cloud_virtual_CPUs_more_than": 28000,
            "cloud_memory_TB": 64,
            "cloud_storage_PB_approximately": 1.2,
        },
        {"incoming_power_mw": 36, "grid_UPS_generator_and_fuel_details": "undisclosed"},
        {"technology_redundancy_capacity_and_water": "undisclosed"},
        [ANNUAL_2024, MEDVEDKOVO_CLOUD, ANNUAL_2025, MEDVEDKOVO_RD],
        publication_conflicts=["The same 2024 annual report uses 4,000 and 4,800 rack capacities in different sections; no value is silently selected."],
        boundary="Reservation and contracting status in the 2024 report are not current utilization. Virtual CPU, memory and storage resources are cloud-service measures, not physical server or GPU counts.",
    ),
    record(
        "ostapovsky_cluster",
        "Ostapovsky cluster and Ostapovsky-2 cloud location",
        "campus_cluster_and_cloud_location",
        "Moscow",
        "operating_with_new_phases_in_design_for_2026_2027",
        {
            "phases_4_and_5_racks_launched_2024": 1024,
            "cluster_total_racks_after_2024_launch": 2048,
            "original_project_racks": 2000,
            "original_project_power_per_rack_kw": 5,
            "original_project_total_power_mw": 17,
            "Ostapovsky_2_KII_cloud_location_launched": 2025,
            "new_phase_design_window": "2026-2027",
        },
        {"original_project_reliability_target": "Tier_IV_provider_project_target", "current_as_built_grid_UPS_generator_details": "undisclosed"},
        {"current_technology_capacity_OEM_and_water": "undisclosed"},
        [OSTAPOVSKY, ANNUAL_2024, ANNUAL_2025],
        "22 Ostapovsky Proyezd, building 4, Moscow",
        publication_conflicts=["The original 2,000-rack project and later 2,048-rack cluster total are different publication snapshots."],
        boundary="The original Tier IV certification plan is not restated as a current Uptime Constructed Facility award. New 2026-2027 phases remain project-documentation work, not operating capacity.",
    ),
    record(
        "nord_6",
        "NORD-6",
        "historically_launched_facility",
        "Moscow",
        "launched_2021_current_individual_roster_status_not_reconfirmed",
        {
            "area_sqm": 3000,
            "machine_halls": 2,
            "rack_places": 207,
            "total_power_mw_published_term": 5,
            "high_density_rack_kw": 20,
            "other_data_centers_at_NORD_site_in_2021": 5,
            "other_site_racks_in_2021": 3764,
        },
        {"critical_system_redundancy": True, "current_grid_UPS_generator_details": "undisclosed"},
        {"critical_system_redundancy": True, "technology_capacity_and_water": "undisclosed"},
        [NORD_6],
        "37 Korovinskoye Shosse, Moscow",
        boundary="The 2021 launch establishes historical operation but the reviewed 2026 provider material does not enumerate NORD-6 in a complete current 26-facility roster. A 20-kW rack is hosting capability, not installed GPU inventory.",
    ),
    record(
        "borovaya_2",
        "Borovaya-2",
        "cloud_location_evidence",
        "Moscow",
        "cloud_capacity_expanded_2025_physical_facility_metrics_undisclosed",
        {"cloud_capacity_expansion_year": 2025, "rack_power_area_and_physical_server_count": "undisclosed"},
        {"grid_UPS_generator_details": "undisclosed"},
        {"technology_capacity_and_water": "undisclosed"},
        [ANNUAL_2025],
        boundary="A named cloud location and capacity expansion do not establish a separate physical building, rack total, MW, GPU allocation or current ownership title.",
    ),
    record(
        "medvedkovo_rd_lab",
        "Medvedkovo R&D laboratory",
        "non_production_test_infrastructure",
        "Moscow",
        "operating_test_complex_since_2025",
        {"R_and_D_racks": 33, "tests_completed_in_2025": 36},
        {"domestic_power_distribution_units_used": True, "counts_ratings_and_models": "undisclosed"},
        {"test_cooling_details": "undisclosed"},
        [MEDVEDKOVO_RD, ANNUAL_2025],
        boundary="The 33-rack laboratory tests domestic servers, networking, storage, virtualization, racks and PDUs. It is not added to customer colocation capacity and does not disclose a production GPU fleet.",
    ),
]


OSM_CROSSWALK = {
    "osm_way_70659008": ("rtk_cod_ekaterinburg", "provider_named_city_facility_candidate_exact_phase_and_building_mapping_unresolved"),
    "osm_way_48910297": (None, "Moscow_V_legacy_or_provider_label_current_facility_mapping_unresolved"),
    "osm_way_149559197": ("rtk_cod_nizhny_novgorod", "first_building_footprint_at_official_facility_candidate"),
    "osm_way_149559237": ("rtk_cod_nizhny_novgorod", "second_building_footprint_at_same_official_facility_candidate"),
    "osm_way_53454428": (None, "provider_named_Novosibirsk_market_facility_current_phase_mapping_unresolved"),
    "osm_relation_16256441": ("rtk_cod_st_petersburg", "provider_named_Saint_Petersburg_campus_candidate_exact_boundary_unresolved"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [
        {"object_type": "DataCenterFacilityEvidence", "source_order": order, "accessed_on": accessed_on, **item}
        for order, item in enumerate(FACILITY_EVIDENCE, 1)
    ]
    assert len(rows) == 9
    assert len({row["id"] for row in rows}) == 9
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert source.get("operator") == "Rostelecom"
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_ref": facility_ref,
            "classification": classification,
            "capacity_counting_rule": "An OSM object is a public map crosswalk, not a current provider roster, ownership, rack, MW, utilization, revenue or GPU record.",
        })
    assert len(rows) == 6
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "rostelecom_rtk_cod_facility_summary_2026_07_19",
        "operator_or_platform": "RTK_COD_group",
        "public_parent": "PJSC_Rostelecom",
        "accessed_on": accessed_on,
        "current_portfolio_headline": {
            "data_centers": 26,
            "detailed_rack_park_after_five_year_program": 27637,
            "rounded_marketing_racks": 27800,
            "Rostelecom_Group_racks_at_end_2025_rounded": 28000,
            "published_total_power_mw_undefined_denominator": 235,
            "current_named_markets": ["Moscow", "Saint_Petersburg", "Ekaterinburg", "Novosibirsk", "Nizhny_Novgorod", "Udomlya", "Tolyatti", "Adler", "Khabarovsk", "Vladivostok"],
            "provider_market_share_percent_2025_annual_report": 30,
            "CEO_letter_market_share_percent": 32,
            "boundary": "The provider does not publish a complete current 26-facility address roster. Ten markets are not 26 facilities; 27,637, 27,800 and 28,000 are different exact, rounded and group scopes. The 235-MW term is not labelled IT load, energized, leased, utilized, billed or actual draw.",
        },
        "investment_and_growth": {
            "five_year_program_2021_2025_RUB_billion_more_than": 38,
            "2025_new_and_expansion_investment_RUB_billion": 3.6,
            "program_share_for_engineering_and_IT_equipment": "approximately_one_third",
            "2025_added_racks_approximately": 1400,
            "2025_added_racks_percent": 5,
            "2025_operating_launches": {"Nizhny_Novgorod_racks": 401, "Udomlya_3_racks": 820},
            "high_readiness_planned_by_end_2026": {"Saint_Petersburg_second_phase_racks_rounded": 900, "Ekaterinburg_third_phase_racks_rounded": 200},
            "Ostapovsky_new_phase_design_window": "2026-2027",
            "planned_Turbo_Cloud_investment_to_2030_RUB_billion_more_than": 40,
            "boundary": "The five-year program, 2025 facility investment and future cloud plan are separate scopes. Planned cloud investment is neither incurred physical-data-center capex nor current revenue.",
        },
        "ownership_and_operating_model": {
            "current_description": "joint_venture_of_Rostelecom_and_VTB",
            "last_exact_official_transaction_stakes_2020": {"VTB_percent": 44.8, "Rostelecom_implied_percent": 55.2},
            "VTB_2020_investment_RUB_billion": 35,
            "2020_transaction_EV_to_OIBDA_multiple": 7.8,
            "current_exact_stakes_reconfirmed_in_2026_source": False,
            "operator_development_models": ["own_construction_and_management", "lease", "acquisition"],
            "IPO_status": "management_preparation_task_not_completed_or_guaranteed_listing",
            "boundary": "The 2020 stakes and multiple are historical transaction evidence. They are not current valuation, market capitalization or a guarantee of the planned IPO. Ownership and tenure are not uniform across all facilities.",
        },
        "financial_scope": {
            "FY2025_RTK_COD_management_cluster_RUB_million": {
                "revenue": 75715,
                "prior_year_revenue": 69670,
                "OIBDA": 33958,
                "prior_year_OIBDA": 30362,
                "derived_OIBDA_margin_percent": 44.85,
                "accounting_operating_profit": "undisclosed",
            },
            "Q1_2026_RTK_COD_group_RUB_million": {
                "revenue": 17898,
                "prior_year_revenue": 18098,
                "revenue_growth_percent": -1,
                "OIBDA": 9578,
                "prior_year_OIBDA": 7358,
                "OIBDA_growth_percent": 30,
                "derived_OIBDA_margin_percent": 53.51,
                "accounting_operating_profit": "undisclosed",
            },
            "cluster_includes": ["colocation_and_related_data_center_services", "cloud_services", "Basis_dynamic_infrastructure_and_virtualization_software"],
            "cluster_excludes": ["hardware_and_IT_components", "IT_services", "other"],
            "reporting_basis": "standalone_management_accounting_approximated_to_IFRS_audited_segment_or_cluster_values_may_differ",
            "boundary": "RTK-COD cluster revenue and OIBDA are not pure physical-data-center earnings. No cluster accounting operating profit, cash flow, capex, debt, customer concentration, site economics or ROIC is disclosed.",
        },
        "parent_financial_context": {
            "FY2025_RUB_million": {"revenue": 872790, "OIBDA": 331048, "operating_profit": 149359, "net_profit": 18715, "capex": 158039, "free_cash_flow_RUB_billion": 37.8, "net_debt_including_leases": 689637, "net_debt_to_OIBDA": 2.1},
            "Q1_2026_RUB_million": {"revenue": 208919, "OIBDA": 83870, "operating_profit": 37483, "net_profit": 7436, "capex": 28632, "free_cash_flow": -5556, "net_debt": 712255, "net_debt_to_OIBDA": 2.1},
            "boundary": "Rostelecom is a diversified telecom and digital-services group. Parent operating profit, debt, cash flow and capex are not assigned to RTK-COD or any facility.",
        },
        "accelerator_and_AI_boundary": {
            "Turbo_Cloud_locations_more_than": 20,
            "federal_districts": 5,
            "virtual_CPUs_more_than": 500000,
            "disclosed_GPU_models": ["NVIDIA_L40S", "NVIDIA_A100", "NVIDIA_H200"],
            "Foundation_Model_Hub_accelerator": "NVIDIA_H200",
            "Foundation_Model_Hub_fabric": "InfiniBand",
            "2025_GPU_VM_demand_growth_multiple": 3,
            "2025_AI_model_resource_growth_multiple": 13,
            "physical_GPU_model_specific_units_site_delivery_power_utilization_and_revenue": "undisclosed",
            "accelerator_ledger_action": "no_numeric_physical_inventory_row_created",
            "boundary": "GPU models, service demand, virtual CPUs and a fabric establish cloud capability. They do not disclose physical accelerator units, ownership, exact host sites, installed power, utilization or GPU revenue and margin.",
        },
        "power_cooling_and_certification_boundary": {
            "facility_records_with_numeric_power_evidence": ["Nizhny_Novgorod", "Udomlya_3_per_rack", "Ekaterinburg_historical_phases", "Saint_Petersburg", "Medvedkovo_2", "Ostapovsky_historical_project", "NORD_6"],
            "provider_portfolio_Tier_III_wording": "26_data_centers_certified_in_accordance_with_Tier_III_requirements",
            "Uptime_current_Rostelecom_client_page_exact_project": "M1_Moscow_Tier_III_Design_Documents",
            "Uptime_current_DataLine_client_projects": ["Nord_4", "Nord_1_and_Nord_2", "Nord_5_server_rooms_120_and_202"],
            "exact_26_site_Uptime_award_bridge": "not_publicly_reconciled",
            "portfolio_PUE_WUE_absolute_water_renewable_matching_and_complete_equipment_BOM": "undisclosed",
            "boundary": "Provider reliability wording, an Uptime client-award entry, historical DataLine awards and an exact current 26-site certification ledger are different scopes. Power denominators and cooling details are not normalized across facilities.",
        },
        "OSM_crosswalk": {
            "Rostelecom_operator_objects": len(osm_rows),
            "objects_joined_to_reviewed_facility_candidate": sum(row["facility_ref"] is not None for row in osm_rows),
            "objects_with_current_facility_mapping_unresolved": sum(row["facility_ref"] is None for row in osm_rows),
            "Nizhny_building_objects_for_one_provider_facility": 2,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "OSM has six objects, including two Nizhny building footprints for one official facility, and misses most of the provider's 26-site portfolio. It is not a complete building, ownership, capacity or GPU census.",
        },
        "remaining_material_gaps": [
            "complete_current_26_facility_address_building_ownership_tenure_and_lifecycle_roster",
            "bridge_between_27637_27800_and_28000_rack_scopes_and_235_MW_denominator",
            "per_site_operating_energized_leased_utilized_billed_and_actual_IT_load",
            "per_site_grid_substation_transformer_switchgear_UPS_battery_generator_fuel_and_cooling_BOM",
            "per_site_live_liquid_cooled_MW_PUE_WUE_water_energy_and_hourly_matching",
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin",
            "RTK_COD_pure_data_center_revenue_accounting_operating_profit_cash_flow_capex_debt_customer_concentration_site_economics_and_ROIC",
            "current_exact_Rostelecom_VTB_ownership_and_IPO_terms",
        ],
        "sources": list(dict.fromkeys([
            PORTFOLIO_2026, ANNUAL_2025, ANNUAL_2024, CEO_2026, FY2025_RESULTS,
            Q1_2026_RESULTS, VTB_TRANSACTION, NIZHNY, UDOMLYA, EKATERINBURG_2021,
            EKATERINBURG_2025, ST_PETERSBURG, NORD_6, OSTAPOVSKY,
            MEDVEDKOVO_CLOUD, MEDVEDKOVO_RD, TURBO_GPU_2025, TURBO_GPU_2026,
            TURBO_INVESTMENT, UPTIME_RUSSIA, UPTIME_ROSTELECOM,
            *[url for row in records for url in row["source_urls"]],
        ])),
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
    registry = args.output_dir / "rostelecom_rtk_cod_facility_registry.jsonl"
    summary_path = args.output_dir / "rostelecom_rtk_cod_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
