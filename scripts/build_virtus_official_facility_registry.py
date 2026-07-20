#!/usr/bin/env python3
"""Build a scope-preserving VIRTUS Data Centres facility-code registry.

The provider's current pages mix operating UK sites with development projects
in the UK, Germany and Italy.  This builder retains every current facility code,
records provider publication conflicts, and keeps design IT MW separate from
FY2024 live, contracted and billable portfolio measures.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DOWNLOADS = "https://virtusdatacentres.com/media-centre/downloads"
LOCATIONS = "https://virtusdatacentres.com/locations"
UK = "https://virtusdatacentres.com/locations/uk"
GERMANY = "https://virtusdatacentres.com/locations/germany"
STOCKLEY = "https://virtusdatacentres.com/locations/uk/london/stockley-park-campus"
SLOUGH = "https://virtusdatacentres.com/locations/uk/london/slough-campus"
SAUNDERTON = "https://virtusdatacentres.com/locations/uk/london/saunderton-campus"
MARIENPARK = "https://virtusdatacentres.com/locations/germany/berlin-data-centres-marienpark-campus"
WUSTERMARK = "https://virtusdatacentres.com/locations/germany/berlin-data-centres-wustermark-campus"
MILAN = "https://virtusdatacentres.com/locations/eu/italy-data-centres-milan-1"
LONDON19_RELEASE = "https://de.virtusdatacentres.com/presseerklarungen/virtus-announces-expansion-with-the-addition-of-london19"
SAUNDERTON_RELEASE = "https://virtusdatacentres.com/press-releases/virtus-unveils-new-data-centre-development-in-saunderton-buckinghamshire"
WUSTERMARK_TRANSFORMERS = "https://de.virtusdatacentres.com/presseerklarungen/virtus-installs-two-of-europes-largest-super-grid-transformers-at-wustermark-campus-in-brandenburg"
MARIENPARK_RELEASE = "https://virtusdatacentres.com/press-releases/virtus-announces-expansion-into-europe-with-berlin-dc-campus"
MILAN_RELEASE = "https://virtusdatacentres.com/press-releases/virtus-announces-new-facility-in-milan-to-support-european-digital-demand"
AI_CASE_STUDY = "https://virtusdatacentres.com/media/attachments/2025/03/14/virtus_case_study_ai-proven_130325.pdf"
CORPORATE_BROCHURE = "https://virtusdatacentres.com/media/attachments/2025/06/13/virtus-data-centres---corporate-brochure50.pdf"
STOCKLEY_SPEC = "https://virtusdatacentres.com/media/attachments/2025/06/10/virtus_spec_sheet_stockley-park-campus-v3.4.pdf"
SAUNDERTON_SPEC = "https://virtusdatacentres.com/media/attachments/2026/04/15/virtus_spec_sheet_saunderton-campus-v2.pdf"
LONDON19_SPEC = "https://virtusdatacentres.com/media/attachments/2026/07/03/virtus_spec_sheet_london19.pdf"
MARIENPARK_SPEC = "https://virtusdatacentres.com/media/attachments/2025/03/03/virtus_spec_sheet_marienpark.pdf"
WUSTERMARK_SPEC = "https://virtusdatacentres.com/media/attachments/2025/03/06/virtus_spec_sheet_wustermark-v3.1.pdf"
MILAN_SPEC = "https://virtusdatacentres.com/media/attachments/2025/03/11/virtus_spec_sheet_milan1.pdf"
ACCOUNTS = "https://find-and-update.company-information.service.gov.uk/company/07670473/filing-history/MzQ3ODYxNTQzOWFkaXF6a2N4/document?format=pdf&download=1"
MAM_STAKE = "https://virtusdatacentres.com/media-centre/press-releases/macquarie-asset-management-acquires-significant-minority-stake-in-st-telemedia-s-virtus-data-centres"
STT_STAKE = "https://www.sttelemediagdc.com/zh/newsroom/st-telemedia-global-data-centres-closes-transaction-introducing-macquarie-asset-management-as-a-significant-minority-shareholder-in-its-European-subsidiary-VIRTUS-data-centres"
LONDON14_PERMIT = "https://www.gov.uk/government/publications/ub3-1qf-virtus-holdco-limited-environmental-permit-issued-eprup3624swa001"
LONDON14_TESTING = "https://planning.hillingdon.gov.uk/OcellaWeb/viewDocument?file=dv_pl_files%5C18399_APP_2025_1908%5CFormal+Declaration.pdf&module=pl"


def london_spec(number: int) -> str:
    if number == 8:
        return "https://virtusdatacentres.com/media/attachments/2025/06/13/virtus_spec_sheet_london816.pdf"
    if number == 14:
        return "https://virtusdatacentres.com/media/attachments/2025/06/13/virtus_spec_sheet_london1490.pdf"
    return f"https://virtusdatacentres.com/images/022025-sepc-specsheets/virtus_spec_sheet_london{number}.pdf"


STANDARD_UK_TECH = {
    "UPS": "centralized_N_plus_N_online",
    "generation": "N_plus_1_LV_DCC_emergency_generation",
    "generator_fuel_autonomy_hours_at_full_load": 48,
    "cooling": "N_plus_1_chilled_water_with_free_cooling",
}


def uk_site(number: int, locality: str, campus: str, it_mw: float, ntm_sqm: int,
            incoming_mva: float | None, lifecycle: str, **extra: object) -> dict:
    profile = {"design_IT_load_mw": it_mw, "net_technical_area_sqm_more_than_or_equal": ntm_sqm}
    if incoming_mva is not None:
        profile["incoming_utility_capacity_MVA"] = incoming_mva
    profile.update(STANDARD_UK_TECH)
    profile.update(extra.pop("technical_profile", {}))
    return {
        "id": f"virtus_london{number}",
        "facility_code": f"LONDON{number}",
        "country_code": "GB",
        "locality": locality,
        "campus": campus,
        "lifecycle": lifecycle,
        "technical_profile": profile,
        "source_urls": [london_spec(number), UK],
        **extra,
    }


FACILITIES = [
    uk_site(1, "Enfield", "Enfield", 4.3, 2900, 8, "operating_at_2024_year_end",
            technical_profile={"design_PUE_less_than": 1.6}),
    uk_site(2, "Hayes", "Hayes", 12.2, 6000, 20, "operating_at_2024_year_end",
            technical_profile={"cooling": "indirect_adiabatic_plus_air_flooded_room_and_free_cooling", "design_PUE_less_than_front_page": 1.2, "design_PUE_less_than_body": 1.3},
            publication_conflicts=["same_spec_front_page_PUE_below_1_2_vs_body_below_1_3", "current_page_rounds_12_2MW_to_12MW"]),
    uk_site(3, "Slough", "Slough", 7.2, 3000, 10, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3}),
    uk_site(4, "Slough", "Slough", 27, 10600, 40, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3}),
    uk_site(5, "Hayes", "Stockley_Park", 24, 10000, 36, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3, "liquid_cooling_ready": True}, source_urls=[london_spec(5), STOCKLEY_SPEC, STOCKLEY]),
    uk_site(6, "Hayes", "Stockley_Park", 16, 7000, 24, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3, "liquid_cooling_ready": True}, source_urls=[london_spec(6), STOCKLEY_SPEC, STOCKLEY]),
    uk_site(7, "Hayes", "Stockley_Park", 32.5, 13000, 49, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3, "liquid_cooling_ready": True}, source_urls=[london_spec(7), STOCKLEY_SPEC, STOCKLEY]),
    uk_site(8, "Hayes", "Stockley_Park", 18, 6000, 24, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3, "liquid_cooling_ready": True}, source_urls=[london_spec(8), STOCKLEY_SPEC, STOCKLEY], publication_conflicts=["individual_spec_NTM_6000sqm_vs_current_location_and_campus_page_7000sqm"]),
    uk_site(9, "Slough", "Slough", 24, 10000, 40, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3, "liquid_cooling_ready": True}, source_urls=[london_spec(9), SLOUGH]),
    uk_site(10, "Slough", "Slough", 6.6, 3000, 11, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3}, source_urls=[london_spec(10), SLOUGH]),
    uk_site(11, "Slough", "Slough", 13, 5500, 22, "operating_at_2024_year_end", technical_profile={"design_PUE_less_than": 1.3}, source_urls=[london_spec(11), SLOUGH]),
    uk_site(12, "Slough", "Slough", 21, 7800, None, "advanced_development_at_2024_year_end_current_RFS_not_provider_confirmed",
            technical_profile={"design_PUE_less_than": 1.3, "renewable_electricity_marketing_percent": 100, "liquid_cooling_ready": ["direct_to_chip", "immersion", "rear_door_heat_exchanger"], "rack_density_kW_more_than": 80}, source_urls=[london_spec(12), SLOUGH]),
    uk_site(14, "Hayes", "Stockley_Park", 22, 8400, None, "advanced_development_at_2024_year_end_current_RFS_not_provider_confirmed",
            technical_profile={"design_PUE_less_than": 1.3, "renewable_electricity_marketing_percent": 100, "liquid_cooling_ready": ["direct_to_chip", "immersion", "rear_door_heat_exchanger"], "permitted_emergency_generators": 16, "generator_OEM": "Finning_Caterpillar", "permitted_annual_testing_hours_total": 20, "permitted_testing_hours_full_load": 16, "SCR_on_all_generators": True},
            source_urls=[london_spec(14), STOCKLEY_SPEC, STOCKLEY, LONDON14_PERMIT, LONDON14_TESTING]),
    uk_site(19, "Slough", "Slough", 32.5, 8500, None, "development_planning_secured_construction_to_begin_after_design_approval",
            technical_profile={"UPS": "centralized_N_plus_1_online", "design_PUE_less_than": 1.3, "powered_shell_partner": "SEGRO", "liquid_cooling_ready": True, "future_heat_export": True, "BREEAM_target": "Excellent"}, source_urls=[LONDON19_SPEC, LONDON19_RELEASE, SLOUGH]),
]


for number, it_mw in [(15, 9.5), (16, 22.5), (17, 16), (18, 30)]:
    FACILITIES.append(uk_site(
        number, "Saunderton", "Saunderton", it_mw, 0, None,
        "development_under_construction_current_RFS_not_provider_confirmed",
        technical_profile={
            "net_technical_area_sqm_more_than_or_equal": "undisclosed_by_facility_code",
            "UPS": "centralized_N_plus_1_online",
            "design_PUE_less_than": 1.2,
            "liquid_cooling_ready": True,
            "rack_density_kW_more_than": 100,
            "campus_grid_contract_MVA_historical": 120,
        },
        source_urls=[SAUNDERTON_SPEC, SAUNDERTON, SAUNDERTON_RELEASE],
        publication_conflicts=["2024_release_75MW_and_Q2_2026_target_vs_current_spec_78MW_and_no_reviewed_provider_RFS_confirmation"],
    ))


for number in range(1, 5):
    FACILITIES.append({
        "id": f"virtus_berlin{number}",
        "facility_code": f"BERLIN{number}",
        "country_code": "DE",
        "locality": "Berlin",
        "campus": "Marienpark",
        "lifecycle": "development_current_provider_target_2027",
        "technical_profile": {
            "design_IT_load_mw": 14.4,
            "campus_IT_load_mw": 57.6,
            "campus_net_technical_area_sqm": 19200,
            "campus_historical_incoming_capacity_MVA_at_least": 90,
            "UPS": "centralized_N_plus_1_online",
            "generation": "N_plus_1_LV_DCC_emergency_generation_48_hour_fuel",
            "cooling": "N_plus_1_chilled_water_with_free_cooling",
            "design_PUE_less_than": 1.2,
            "waste_heat_reuse_planned": True,
        },
        "publication_conflicts": ["historic_BERLIN1_2026_target_revised_by_current_Germany_page_to_2027"],
        "source_urls": [MARIENPARK_SPEC, MARIENPARK, MARIENPARK_RELEASE, GERMANY],
    })


for number, it_mw in [(5, 24), (6, 24), (7, 24), (8, 24), (9, 24), (10, 24), (11, 24), (12, 24), (13, 12)]:
    FACILITIES.append({
        "id": f"virtus_berlin{number}",
        "facility_code": f"BERLIN{number}",
        "country_code": "DE",
        "locality": "Wustermark",
        "campus": "Wustermark",
        "lifecycle": "development_current_provider_projected_early_2028",
        "technical_profile": {
            "design_IT_load_mw": it_mw,
            "campus_design_IT_load_mw": 204,
            "campus_land_sqm_more_than": 350000,
            "grid_connection_kV": 380,
            "dedicated_substation_mw": 500,
            "initial_grid_capacity_mw": 300,
            "super_grid_transformers": {"count": 2, "rating_MVA_each": 185, "type": "oil_filled"},
            "UPS": "centralized_N_plus_1_online_or_optional_generatorless_customer_design",
            "generation": "N_plus_1_LV_DCC_48_hour_HVO_compatible_available_by_default",
            "cooling": "N_plus_1_closed_loop_chilled_water_air_and_liquid_to_liquid_compatible",
            "design_PUE": 1.2,
        },
        "publication_conflicts": ["historic_300MW_project_headline_vs_current_204MW_IT_facility_code_sum", "initial_300MW_grid_capacity_and_500MW_substation_are_not_IT_load"],
        "source_urls": [WUSTERMARK_SPEC, WUSTERMARK, WUSTERMARK_TRANSFORMERS, GERMANY],
    })


FACILITIES.append({
    "id": "virtus_milan1",
    "facility_code": "MILAN1",
    "country_code": "IT",
    "locality": "Cornaredo_Milan",
    "campus": "Milan",
    "lifecycle": "development_current_provider_RFS_2028",
    "technical_profile": {
        "current_page_design_IT_load_mw": 48,
        "older_spec_design_IT_load_mw": 42,
        "grid_capacity_MVA": 70,
        "brownfield_site_area_sqm": 71000,
        "zoned_facility_area_sqm": 44000,
        "older_spec_net_technical_area_sqm_more_than": 44000,
        "UPS": "N_plus_N_online",
        "generation": "N_plus_1_emergency_generation_48_hour_fuel",
        "cooling": "N_plus_1_chilled_water_with_free_cooling",
        "design_PUE_less_than": 1.3,
    },
    "publication_conflicts": ["2025_spec_42MW_and_RFS_2027_vs_current_page_48MW_and_RFS_2028"],
    "source_urls": [MILAN_SPEC, MILAN, MILAN_RELEASE, LOCATIONS],
})


OSM_CROSSWALK = {
    "osm_way_240952254": ["virtus_london1"],
    "osm_way_712298673": ["virtus_london2"],
    "osm_way_459572486": ["virtus_london3", "virtus_london4"],
    "osm_way_705065014": ["virtus_london3"],
    "osm_way_705085806": ["virtus_london5"],
    "osm_way_705085805": ["virtus_london6"],
    "osm_way_705085807": ["virtus_london7"],
    "osm_way_838801558": ["virtus_london8"],
    "osm_way_787209399": ["virtus_london9"],
    "osm_way_459600800": ["virtus_london10"],
    "osm_way_1313579347": ["virtus_london11"],
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(FACILITIES, start=1):
        records.append({
            "object_type": "DataCenterFacilityEvidence",
            "source_order": order,
            "operator": "VIRTUS_Data_Centres",
            "physical_GPU_or_accelerator_inventory_at_site": "undisclosed",
            "AI_readiness_is_not_GPU_inventory": True,
            "accessed_on": accessed_on,
            **source,
        })
    assert len(records) == 32
    assert len({row["facility_code"] for row in records}) == 32
    assert Counter(row["country_code"] for row in records) == {"GB": 18, "DE": 13, "IT": 1}
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, facility_refs in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert "virtus" in (source.get("name") or "").lower()
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "operator_tagged": source.get("operator") in {"VIRTUS", "Virtus"},
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_refs": facility_refs,
            "crosswalk_status": "exact_name_candidate_shared_object_retained_where_applicable",
            "source_url": source["source_url"],
            "boundary": "OSM geometry is not provider-certified ownership, current lifecycle, floor area, IT load, utilization or GPU inventory.",
        })
    assert len(rows) == 11
    assert sum(row["operator_tagged"] for row in rows) == 8
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    uk_total = round(sum(row["technical_profile"].get("design_IT_load_mw", 0) for row in records if row["country_code"] == "GB"), 1)
    germany_total = round(sum(row["technical_profile"].get("design_IT_load_mw", 0) for row in records if row["country_code"] == "DE"), 1)
    assert uk_total == 338.3
    assert germany_total == 261.6
    return {
        "id": "virtus_official_facility_summary_2026_07_19",
        "object_type": "VIRTUSPortfolioReconciliation",
        "accessed_on": accessed_on,
        "current_provider_code_roster": {
            "facility_codes": len(records),
            "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
            "UK_mixed_lifecycle_code_capacity_mw": uk_total,
            "Germany_exact_code_capacity_mw": germany_total,
            "Germany_current_marketing_capacity_mw": 260,
            "Italy_current_page_capacity_mw": 48,
            "Europe_mixed_lifecycle_headline_checksum_mw": round(uk_total + germany_total + 48, 1),
            "boundary": "The 647.9-MW checksum includes operating, advanced-development, construction and announced facilities and is not current operating, energized, leased, utilized or billed load.",
        },
        "FY2024_statutory_portfolio_boundary": {
            "fully_live_UK_sites": 11,
            "live_sites_contracted_percent": 98,
            "contracted_mw": 181.8,
            "billable_mw": 179.3,
            "UK_total_design_capacity_mw": 302.7,
            "European_projects_design_capacity_mw": 303.6,
            "total_design_capacity_mw": 606.3,
            "advanced_development_sites": ["LONDON12", "LONDON14"],
            "capacity_added_by_LONDON12_and_LONDON14_mw": 43,
            "new_sites_brought_live_during_2024": 0,
            "boundary": "FY2024 audited measures use a dated statutory perimeter and do not reconcile one-for-one to the July 2026 marketing roster or current facility-code design values.",
        },
        "campus_reconciliation": {
            "Slough": {"current_page_facilities": 7, "page_capacity_mw_more_than": 138, "exact_current_code_sum_mw": 131.3, "publication_conflict": "page_header_also_says_six_facilities"},
            "Stockley_Park": {"spec_facilities": 5, "exact_code_sum_mw": 112.5, "net_technical_area_sqm": 45400, "publication_conflict": "current_page_body_says_four_facilities"},
            "Saunderton": {"current_spec_capacity_mw": 78, "historic_release_capacity_mw": 75, "historic_grid_contract_MVA": 120, "current_RFS": "not_provider_confirmed_in_reviewed_sources"},
            "Marienpark": {"facility_codes": 4, "IT_load_mw": 57.6, "current_target": 2027},
            "Wustermark": {"facility_codes": 9, "IT_load_mw": 204, "current_projected_RFS": "early_2028"},
            "Milan": {"current_page_mw": 48, "older_spec_mw": 42, "current_RFS": 2028, "older_target": 2027},
        },
        "AI_and_GPU_boundary": {
            "unnamed_customer_A": {
                "in_operation_since": 2021,
                "workload": "multi_MW_AI",
                "cooling": ["direct_to_chip_single_phase_liquid", "rear_door_heat_exchanger"],
                "multiple_racks_weight_vs_standard_air_cooled_more_than": "3x",
                "test_equipment": ["industrial_boiler", "thermal_store_for_fluctuating_load"],
                "operational_PUE_less_than": 1.1,
            },
            "provider_owned_GPU_count": "undisclosed",
            "GPU_model_count_owner_site_and_utilization": "undisclosed",
            "accelerator_ledger_action": "no_count_row_created",
            "boundary": "A customer case study and rack-density or liquid-cooling readiness do not establish VIRTUS-owned GPU inventory.",
        },
        "public_map_crosswalk": {
            "related_named_OSM_objects": len(osm_rows),
            "operator_tagged_OSM_objects": sum(row["operator_tagged"] for row in osm_rows),
            "objects": osm_rows,
            "boundary": "One Slough polygon names LONDON3 and LONDON4 while another names LONDON3; overlapping map evidence is retained and not converted into a physical-building count.",
        },
        "ownership": {
            "STT_GDC_majority_percent": 60,
            "Macquarie_Asset_Management_MEIF7_percent": 40,
            "immediate_parent": "STT_VIRTUS_Holdco_Limited_Guernsey",
            "ultimate_parent_and_controlling_party": "Temasek_Holdings_Private_Limited",
        },
        "unresolved_gaps": [
            "32_provider_codes_to_exact_non_overlapping_physical_buildings_parcels_title_lease_and_current_lifecycle",
            "LONDON12_LONDON14_Saunderton_current_RFS_energization_customer_acceptance_and_billing",
            "UK_338_3MW_Germany_261_6MW_Italy_48MW_mixed_design_to_current_operating_energized_leased_utilized_and_billed_load",
            "per_site_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CDU_models_counts_ratings_OEMs_and_as_built_topology",
            "per_site_measured_PUE_WUE_water_energy_renewable_hourly_matching_heat_reuse_and_live_liquid_cooled_MW",
            "AI_case_study_customer_site_GPU_model_count_owner_power_utilization_revenue_and_margin",
            "site_level_revenue_operating_profit_capex_debt_customer_concentration_utilization_and_ROIC",
            "Wustermark_Marienpark_Milan_LONDON19_land_grid_permit_financing_construction_customer_and_RFS_progress",
        ],
        "sources": sorted({url for row in records for url in row["source_urls"]} | {DOWNLOADS, LOCATIONS, AI_CASE_STUDY, CORPORATE_BROCHURE, ACCOUNTS, MAM_STAKE, STT_STAKE}),
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
    registry = args.output_dir / "virtus_official_facility_registry.jsonl"
    summary_path = args.output_dir / "virtus_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
