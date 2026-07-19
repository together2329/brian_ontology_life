#!/usr/bin/env python3
"""Build a scope-safe IXcellerate facility and evidence registry.

IXcellerate's current facility cards, launch announcements and campus plans use
different rack, power and lifecycle denominators.  This builder preserves those
boundaries and joins public-map objects without turning design capacity, grid
power, contracted racks or hosted AI systems into current load or operator-owned
GPU inventory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


DIRECTORY = "https://www.ixcellerate.com/data-centers/"
NORTH = "https://www.ixcellerate.com/data-centers/moscow-north-campus/"
SOUTH = "https://www.ixcellerate.com/data-centers/moscow-south-campus/"
VESHKI = "https://www.ixcellerate.com/data-centers/moscow-veshki-campus/"
MOS3_LAUNCH = "https://www.ixcellerate.com/news/ixcellerate-opens-mos3-data-center-the-capacity-of-the-providers-entire-ecosystem-exceeds-10000-rack-spaces/"
MOS5_POWER = "https://www.ixcellerate.com/news/ixcellerate-povysil-moshhnost-data-tsentra-mos5-do-64mvt/"
MOS5_TELEHOUSE = "https://www.ixcellerate.com/news/ixcellerate-strengthens-russian-connectivity-ecosystem-and-expands-capacity-of-its-telehouse-in-the-moscow-south-campus/"
MOS7_CONSTRUCTION = "https://www.ixcellerate.com/news/a-time-capsule-laid-in-the-mos7-data-center/"
VESHKI_LAUNCH = "https://www.ixcellerate.com/news/ixcellerate-expands-its-presence-in-the-moscow-region-with-the-launch-of-new-130-mw-campus/"
CEO_INTERVIEW = "https://www.ixcellerate.com/news/launching-the-third-campus-we-are-investing-in-the-digital-infrastructure-of-the-future-said-andrei-aksenov-ceo-of-ixcellerate/"
HIGH_DENSITY = "https://www.ixcellerate.com/services/high-power-density-solutions/"
REQUISITES = "https://www.ixcellerate.com/requisites/"
CERTIFICATES = "https://www.ixcellerate.com/certificates/"
UPTIME = "https://airs.uptimeinstitute.com/uptime-institute-awards/list/client/ixcellerate/618"
UK_COMPANY = "https://find-and-update.company-information.service.gov.uk/company/07265372"
UK_ACCOUNTS_2024 = "https://find-and-update.company-information.service.gov.uk/company/07265372/filing-history/MzUxNDEwNDkzNWFkaXF6a2N4/document?download=1"
UK_PSC = "https://find-and-update.company-information.service.gov.uk/company/07265372/persons-with-significant-control"
UK_CONFIRMATION_2026 = "https://find-and-update.company-information.service.gov.uk/company/07265372/filing-history/MzUyNzIxMzQ3MWFkaXF6a2N4/document?download=1"
BFO_MAIN = "https://bo.nalog.gov.ru/organizations-card/1414458?period=2025"
BFO_3 = "https://bo.nalog.gov.ru/organizations-card/11209915?period=2025"
BFO_4 = "https://bo.nalog.gov.ru/organizations-card/11412971?period=2025"


def facility(
    code: str,
    campus: str,
    lifecycle: str,
    metrics: dict,
    power: dict,
    cooling: dict,
    sources: list[str],
    *,
    density: dict | None = None,
    certifications: list[dict] | None = None,
    conflicts: list[str] | None = None,
    boundary: str | None = None,
) -> dict:
    return {
        "id": f"ixcellerate_{code.lower()}",
        "name": code,
        "campus": campus,
        "country_code": "RU",
        "metro": "Moscow",
        "lifecycle_as_of_2026_07_19": lifecycle,
        "published_metrics": metrics,
        "electrical_and_backup_power_evidence": power,
        "cooling_evidence": cooling,
        "rack_density_and_AI_evidence": density or {"per_rack_density_kw": "undisclosed"},
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "certification_evidence": certifications or [],
        "publication_conflicts": conflicts or [],
        "boundary": boundary or "Published rack and MW values do not establish current energized, leased, utilized, billed or actual IT load, site economics or GPU inventory.",
        "source_urls": list(dict.fromkeys(sources)),
    }


FACILITIES = [
    facility(
        "MOS1", "Moscow_North", "operating",
        {"racks_full_design": 1835, "useful_area_sqm": 6000, "published_power_mw": 13.7, "power_term": "provider_card_unspecified"},
        {"UPS_topology": "undisclosed", "diesel_redundancy": "N_plus_1", "battery": "lithium_ion", "battery_runtime_minutes_at_full_load": 10},
        {"redundancy": "N_plus_1", "technology": "adiabatic_chillers", "airflow": "cold_and_hot_aisles", "design_PUE_below": 1.6},
        [NORTH, CERTIFICATES, UPTIME], density={"maximum_kw_per_rack": 10},
        certifications=[{"provider_wording": "Tier_III_and_IBM_Level_3"}, {"independent_Uptime_public_award": "Moscow_One_Datacentre_Phase_3"}],
    ),
    facility(
        "MOS2", "Moscow_North", "operating",
        {"racks_full_design": 1580, "useful_area_sqm": 3300, "published_power_mw": 13, "power_term": "provider_card_unspecified"},
        {"UPS_topology": "2N", "diesel_redundancy": "N_plus_1", "battery": "lithium_ion", "battery_runtime_minutes_at_full_load": 10},
        {"redundancy": "N_plus_1", "technology": "Vertiv_PDX_and_EconoPhase", "design_PUE_below": 1.5},
        [NORTH, CERTIFICATES, UPTIME], density={"maximum_kw_per_rack": 12},
        certifications=[{"provider_wording": "Tier_III"}, {"independent_Uptime_public_award": "Moscow_Two_Datacentre"}],
    ),
    facility(
        "MOS3", "Moscow_North", "operating_launched_2025_10_29_with_staged_rack_delivery",
        {"racks_full_design": 2400, "racks_functioning_at_launch": 1400, "racks_contracted_or_due_by_2026_01": 1000, "useful_area_sqm": 7367, "published_power_mw": 30, "floors": 4, "data_halls": 6},
        {"city_10_kV_inputs": 6, "rack_level_topology_launch_news": "2N", "UPS_redundancy_current_card": "4_of_3", "diesel_redundancy": "8_of_7", "SLA_percent": 99.982},
        {"redundancy": "N_plus_1", "technology": "chiller_fan_coil_with_year_round_free_cooling", "precision_air_conditioners": 12, "heat_recovery": True, "design_PUE_below_at_full_load": 1.3},
        [NORTH, MOS3_LAUNCH], density={"average_design_kw_per_rack": 8, "maximum_kw_per_rack": 25},
        conflicts=["The stale campus prose still calls MOS3 development, while the dated 2025-10-29 launch announcement establishes operation.", "The current card says 4/3 UPS and 8/7 diesel, while the launch announcement also states 2N at rack level; equipment scopes are not flattened."],
        boundary="The 2,400-rack card is full design capacity. At launch 1,400 racks were functioning and 1,000 were contracted for delivery by January 2026; no later official source reviewed proves the exact July 2026 installed and accepted split.",
    ),
    facility(
        "MOS4", "Moscow_North", "operating_technical_launch_2022",
        {"racks_full_design": 512, "useful_area_sqm": 1861, "published_power_mw": 7, "power_term": "provider_card_unspecified"},
        {"UPS_redundancy": "4_of_3", "diesel_redundancy": "4_of_3"},
        {"redundancy": "N_plus_1", "technology": "LSV_cold_walls", "airflow": "isolated_hot_aisles", "design_PUE_below": 1.3},
        [NORTH], density={"maximum_kw_per_rack": 15},
    ),
    facility(
        "MOS5", "Moscow_South", "operating_final_phase_launched_2025",
        {"racks_full_design": 5002, "useful_area_sqm": 18500, "published_power_mw": 64, "power_term": "facility_power_unspecified", "Telehouse_carrier_hall_racks_subset_not_additive": 140},
        {"distribution_substations_historical_2023": 4, "substation_mw_each": 16, "transformers_historical_2023": 40, "transformer_kVA_each": 2500, "UPS_redundancy": "4_of_3", "diesel_redundancy": "4_of_3"},
        {"redundancy": "N_plus_1", "technology": "cold_wall", "airflow": "isolated_hot_aisles", "average_annual_PUE_below_at_full_load": 1.3},
        [SOUTH, MOS5_POWER, MOS5_TELEHOUSE, CEO_INTERVIEW, CERTIFICATES], density={"maximum_kw_per_rack": 55, "Telehouse_MMR_maximum_kw_per_rack": 10, "Telehouse_adjacent_halls_maximum_kw_per_rack": 25},
        certifications=[{"provider_certificate_page": "MOS5_Tier_III_Design"}],
        conflicts=["The 2023 expansion article stated PUE below 1.4 and a more-than-4,700-rack plan; the current card supersedes these with below 1.3 and 5,002 racks."],
        boundary="The 140 Telehouse racks are a subset inside MOS5 and are not added to the 5,002-rack facility total. Historical equipment counts are not asserted as a complete current as-built BOM.",
    ),
    facility(
        "MOS6", "Moscow_South", "development_not_operating",
        {"racks": "undisclosed", "power_mw": "undisclosed_on_current_facility_page"},
        {"topology_and_equipment": "undisclosed"}, {"technology_and_capacity": "undisclosed"},
        [SOUTH], boundary="MOS6 is part of the South full-build plan; the reviewed current page does not establish an operating launch or facility-level rack and power figures.",
    ),
    facility(
        "MOS7", "Moscow_South", "under_construction_as_of_2025_12_16_no_launch_found_by_2026_07_19",
        {"racks_project": 1720, "published_power_mw_project": 34},
        {"UPS_redundancy_project": "4_of_3", "diesel_redundancy_project": "4_of_3"},
        {"redundancy_project": "N_plus_1", "technology_project": "cold_wall", "airflow_project": "isolated_hot_aisles", "design_PUE_below": 1.3},
        [SOUTH, MOS7_CONSTRUCTION], density={"maximum_kw_per_rack_project": 12},
        boundary="The facility card values are project design metrics. The dated time-capsule announcement describes construction, and no official launch was found by the review date.",
    ),
    facility(
        "MOS8", "Moscow_South", "future_listed_not_operating",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"topology_and_equipment": "undisclosed"}, {"technology_and_capacity": "undisclosed"},
        [SOUTH], boundary="MOS8 appears in the South full-build roster but has no reviewed facility-level numeric card or launch evidence.",
    ),
    facility(
        "MOS11", "Moscow_Veshki", "development_first_phase_scheduled_summer_2026_no_launch_found_by_2026_07_19",
        {"racks_project": 2500, "useful_area_sqm_project": 13037, "published_power_mw_project": 40, "building_strategy": "brownfield_existing_building"},
        {"rack_topology_project": "2N", "grid_inputs": 2, "inputs_from_independent_substations": True, "diesel_and_UPS": True},
        {"redundancy_project": "N_plus_1", "technology_project": "LSV_cold_wall_free_cooling_chillers_with_adiabatic_precooling", "design_PUE_below": 1.33},
        [VESHKI, VESHKI_LAUNCH, CEO_INTERVIEW], density={"standard_maximum_kw_per_rack_project": 12, "HPC_maximum_kw_per_rack_project": 44},
        boundary="The provider scheduled first-phase racks for summer 2026, but no reviewed official launch establishes operation by 2026-07-19; all numeric values remain project scope.",
    ),
    facility(
        "MOS12", "Moscow_Veshki", "future_construction_planned_2027_phases_2029_to_2030",
        {"racks": "undisclosed", "power_mw": "undisclosed"},
        {"topology_and_equipment": "undisclosed"}, {"technology_and_capacity": "undisclosed"},
        [VESHKI, VESHKI_LAUNCH], boundary="The campus plan names MOS12 but does not support deriving its capacity as the residual of the Veshki headline.",
    ),
]


OSM_CROSSWALK = {
    "osm_way_207145308": "ixcellerate_mos1",
    "osm_way_277554026": "ixcellerate_mos2",
    "osm_way_413169015": "ixcellerate_mos3",
    "osm_way_1140704048": "ixcellerate_mos4",
    "osm_relation_8834520": "ixcellerate_mos5",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [{"object_type": "DataCenterFacilityEvidence", "source_order": order, "accessed_on": accessed_on, **row} for order, row in enumerate(FACILITIES, 1)]
    assert len(rows) == 10
    assert len({row["id"] for row in rows}) == 10
    assert sum(row["lifecycle_as_of_2026_07_19"].startswith("operating") for row in rows) == 5
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, facility_ref in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "facility_ref": facility_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "classification": "exact_current_provider_facility_candidate",
            "capacity_counting_rule": "OSM geometry is a crosswalk, not a rack, power, ownership, utilization, revenue or GPU source.",
        })
    assert len(rows) == 5
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sources = list(dict.fromkeys([
        DIRECTORY, NORTH, SOUTH, VESHKI, MOS3_LAUNCH, MOS5_POWER,
        MOS5_TELEHOUSE, MOS7_CONSTRUCTION, VESHKI_LAUNCH, CEO_INTERVIEW,
        HIGH_DENSITY, REQUISITES, CERTIFICATES, UPTIME, UK_COMPANY,
        UK_ACCOUNTS_2024, UK_PSC, UK_CONFIRMATION_2026, BFO_MAIN, BFO_3, BFO_4,
        *[url for row in records for url in row["source_urls"]],
    ]))
    operating = [row for row in records if row["lifecycle_as_of_2026_07_19"].startswith("operating")]
    return {
        "id": "ixcellerate_official_facility_summary_2026_07_19",
        "operator": "IXcellerate",
        "accessed_on": accessed_on,
        "facility_scope": {
            "campuses": 3,
            "operating_facilities_supported": 5,
            "operating_facility_codes": [row["name"] for row in operating],
            "operating_full_design_racks_card_checksum": sum(row["published_metrics"]["racks_full_design"] for row in operating),
            "operating_card_power_mw_checksum": sum(row["published_metrics"]["published_power_mw"] for row in operating),
            "operating_useful_area_sqm_checksum": sum(row["published_metrics"]["useful_area_sqm"] for row in operating),
            "provider_end_2025_North_plus_South_racks": 10329,
            "reconciliation_difference_racks": 1000,
            "reconciliation": "The 11,329 current-card full-design checksum exceeds the provider's end-2025 10,329-rack total by exactly the 1,000 MOS3 racks contracted for delivery by January 2026. The exact July 2026 installed and accepted split remains undisclosed.",
        },
        "campus_full_build_plans": {
            "Moscow_South": {"land_hectares": 14, "facilities": ["MOS5", "MOS6", "MOS7", "MOS8"], "racks_more_than": 19300, "power_mw_more_than": 300, "design_PUE": 1.3, "boundary": "Full-build plan, not operating capacity."},
            "Moscow_Veshki": {"land_hectares": 5.5, "facilities": ["MOS11", "MOS12"], "racks": 7500, "power_mw_more_than": 130, "boundary": "Campus plan; MOS11 lacks a reviewed launch and MOS12 is future."},
            "boundary": "Campus totals overlap facility records and are not added to operating-card checksums.",
        },
        "high_density_and_AI_boundary": {
            "air_cooling_maximum_kw_per_rack": 55,
            "combined_air_liquid_cooling_above_kw_per_rack": 60,
            "dedicated_halls_for_supercomputers_and_AI": True,
            "solution_scale_racks": "1_to_1000_plus",
            "provider_high_density_page_total_power_mw": 380,
            "total_power_denominator": "unclear_mixed_lifecycle_not_operating",
            "physical_GPU_model_count_owner_site_delivery_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "hosted_customer_workloads_not_operator_owned_GPU_proof": True,
            "accelerator_ledger_action": "no_numeric_physical_inventory_row_created",
        },
        "legal_and_ownership_boundary": {
            "UK_parent": "IXcellerate_Limited_company_07265372",
            "UK_accounts_statement": "no_ultimate_controlling_party",
            "active_PSC_register_entry": "The_Goldman_Sachs_Group_Inc_over_25_and_up_to_50_percent_shares_and_votes",
            "PSC_and_accounts_reconciliation": "A major shareholder can satisfy the PSC threshold without controlling the group under the shareholder agreement and board composition.",
            "Russian_entities": {
                "IXcellerate_LLC": {"INN": "7715904744", "OGRN": "1127746106773"},
                "IXcellerate_3_LLC": {"INN": "9715371955", "OGRN": "1197746731808"},
                "IXcellerate_4_LLC": {"INN": "9715390330", "OGRN": "1207700361428"},
            },
            "facility_legal_bridge_from_2024_accounts": {
                "MOS1": "LLC_IXcellerate_operator_or_property_holder",
                "MOS2": "LLC_Olimax_operator_or_property_holder",
                "MOS4": "JSC_SMAK_operator_or_property_holder",
                "MOS5": "LLC_IXcellerate_3_owner_operator",
                "MOS3": "LLC_IXcellerate_4_property_holder_and_technical_operator_with_LLC_IXcellerate_client_operator",
            },
        },
        "financials": {
            "audited_2024_consolidated_USD_million": {
                "revenue": 93.610, "prior_revenue": 71.157, "colocation_revenue": 87.401,
                "gross_profit": 55.979, "operating_profit": 41.376, "EBITDA": 56.772,
                "adjusted_EBITDA": 57.166, "profit_before_tax": 37.337,
                "net_profit": 29.771, "cash": 143.279, "capex": 66.311,
                "long_term_borrowings": 108.357, "short_term_borrowings": 17.010,
                "property_plant_and_equipment": 232.591, "total_assets": 424.373,
                "equity": 254.739, "operating_cash_flow": 46.570,
            },
            "audited_2024_derived": {"revenue_growth_percent": 31.55, "colocation_share_percent": 93, "gross_margin_percent": 60, "operating_margin_percent": 44},
            "installed_grid_power_at_2024_12_31_mw": {"total": 150, "North": 69, "South": 81, "boundary": "Grid capacity at the accounts date, not current card power, IT load or actual draw."},
            "Russian_2025_statutory_thousand_RUB": {
                "IXcellerate_LLC": {"revenue": 7643531, "profit_from_sales_line_2200": 3730035, "profit_before_tax": 985940, "net_profit": 730310},
                "IXcellerate_3_LLC": {"revenue": 7063184, "profit_from_sales_line_2200": 4294089, "profit_before_tax": 3108757, "net_profit": 2327114},
                "IXcellerate_4_LLC": {"revenue": 1839966, "profit_from_sales_line_2200": 849166, "profit_before_tax": -677779, "net_profit": -509588},
            },
            "Russian_statutory_boundary": "The three Russian legal entities contain intercompany transactions and no consolidation eliminations; their revenue and profit lines must not be summed as group performance. Profit from sales is a Russian statutory line, not IFRS group operating profit.",
        },
        "certification_boundary": {
            "independent_Uptime_public_awards_found": ["Moscow_One_Datacentre_Phase_3", "Moscow_Two_Datacentre"],
            "provider_certificate_page_additional_claim": "MOS5_Tier_III_Design",
            "boundary": "General Tier III wording and the provider certificate page are not expanded into constructed-facility awards absent matching independent award entries.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows), "rows": osm_rows,
            "source_file": str(osm_path), "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Five OSM objects map to MOS1-MOS5 but do not establish capacity, lifecycle, ownership or financial scope.",
        },
        "outlook": {
            "positive_signals": ["2024_consolidated_revenue_growth_32_percent_reported", "2024_operating_margin_44_percent", "MOS3_and_final_MOS5_phase_launched_in_2025", "South_and_Veshki_large_development_option", "high_density_air_and_combined_liquid_cooling_design"],
            "risk_signals": ["Russia_only_geographic_concentration", "geopolitical_and_imported_equipment_availability_risk", "large_pipeline_requires_grid_capex_customers_and_delivery", "mixed_lifecycle_380MW_marketing_denominator", "no_physical_GPU_inventory_or_site_economics", "MOS11_launch_not_found_and_MOS7_still_construction_in_reviewed_evidence"],
            "analytical_view": "IXcellerate combines strong audited 2024 growth and margin with five operating Moscow facilities and a large expansion path. The investment case remains private, Russia-concentrated and execution-heavy; pipeline MW, design racks and hosted AI readiness should not be valued as operating load or operator-owned compute.",
        },
        "remaining_material_gaps": [
            "exact_July_2026_MOS3_installed_accepted_and_billed_rack_split",
            "MOS6_MOS7_MOS8_MOS11_MOS12_current_construction_energization_acceptance_and_customer_status",
            "per_site_operating_energized_leased_utilized_billed_and_actual_IT_load",
            "per_site_complete_as_built_grid_transformer_switchgear_UPS_battery_generator_fuel_and_cooling_BOM",
            "per_site_measured_PUE_WUE_absolute_water_energy_and_live_liquid_cooled_MW",
            "physical_GPU_model_count_owner_site_delivery_fabric_power_utilization_revenue_and_margin",
            "site_level_revenue_operating_profit_cash_flow_capex_customer_concentration_and_ROIC",
            "fully_eliminated_2025_consolidated_group_financials_and_current_shareholder_percentages",
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
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "ixcellerate_official_facility_registry.jsonl"
    summary_path = args.output_dir / "ixcellerate_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
