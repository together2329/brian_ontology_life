#!/usr/bin/env python3
"""Build a scope-preserving Turkcell / TDC data-center registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


TURKCELL_2025_20F_URL = "https://s.turkcell.com.tr/SiteAssets/Hakkimizda/yatirimci-iliskileri/documents/pdf/20F2025.pdf"
TURKCELL_DATA_CENTER_URL = "https://www.turkcell.com.tr/kurumsal/dijital-is-servisleri/veri-merkezi-data-center"
TURKCELL_WHOLESALE_URL = "https://www.turkcell.com.tr/en-en/about-us/wholesale/fixed-data-services/hosting-data-center-services-and-local-network-access/detail"
TURKCELL_FACILITIES_GUIDE_URL = "https://kariyerim.turkcell.com.tr/Documents/Veri_Merkezi_Departman_Tanitim_Klavuzu.pdf"
TURKCELL_ANKARA_URL = "https://medya.turkcell.com.tr/en/bulletins/turkcell-opens-turkeys-first-solar-powered-data-center-in-ankara/"
TURKCELL_TDC_FINANCING_URL = "https://medya.turkcell.com.tr/en/bulletins/turkcell-secures-e100-million-investment-to-boost-data-center-business-expansion/"
TURKCELL_GOOGLE_URL = "https://medya.turkcell.com.tr/en/bulletins/turkcell-announces-strategic-partnership-with-google-cloud-with-plans-to-establish-a-google-cloud-region-in-turkiye/"
TURKCELL_2025_RESULTS_URL = "https://medya.turkcell.com.tr/bulletins/turkcell-2026da-gelirinin-yuzde-25ini-yatirima-ayiracak-hizini-katlayacak/"
TURKCELL_Q1_2026_URL = "https://medya.turkcell.com.tr/bulletins/turkcellden-5g-cagina-guclu-baslangic/"


SITES = [
    {
        "code": "GEBZE",
        "provider_site_name": "Kocaeli Gebze Data Center",
        "locality": "Gebze, Kocaeli",
        "opened_year": 2016,
        "gross_site_area_m2": 33_000,
        "design_white_space_m2": 10_000,
        "total_IT_energy_capacity_MW": 17.0,
        "OSM_refs": ["osm_way_422730372"],
    },
    {
        "code": "IZMIR",
        "provider_site_name": "Izmir Data Center",
        "locality": "Menderes, Izmir",
        "opened_year": 2018,
        "gross_site_area_m2": 14_500,
        "design_white_space_m2": 2_350,
        "total_IT_energy_capacity_MW": 3.4,
        "OSM_refs": [],
    },
    {
        "code": "ANKARA_TEMELLI",
        "provider_site_name": "Ankara Temelli Data Center",
        "locality": "Temelli, Ankara",
        "opened_year": 2019,
        "gross_site_area_m2": 46_200,
        "design_white_space_m2": 12_000,
        "total_IT_energy_capacity_MW": 20.9,
        "OSM_refs": ["osm_way_742363207"],
        "renewable_and_water": "parking_lot_solar_panels_and_rainwater_recovery_disclosed_without_current_site_load_or_WUE",
    },
    {
        "code": "EUROPE_CORLU",
        "provider_site_name": "Tekirdag European Data Center",
        "locality": "Corlu, Tekirdag",
        "opened_year": 2021,
        "gross_site_area_m2": 37_272,
        "design_white_space_m2": 7_200,
        "total_IT_energy_capacity_MW": 12.5,
        "OSM_refs": ["osm_way_808990471"],
    },
]


OSM_CROSSWALK = {
    "osm_way_422730372": ("GEBZE", "exact_current_new_generation_site_name_city_and_operator_family_match"),
    "osm_way_742363207": ("ANKARA_TEMELLI", "exact_current_new_generation_site_name_locality_and_operator_match"),
    "osm_way_808990471": ("EUROPE_CORLU", "exact_current_new_generation_Europe_Tekirdag_Corlu_site_match"),
    "osm_way_657222646": (None, "Kartal_legacy_site_phased_out_in_2025_with_IT_relocation_to_Sogutozu_targeted_for_2026"),
    "osm_way_532115060": (None, "Edirne_legacy_or_network_data_center_not_reconciled_to_the_four_new_generation_third_party_sites_or_a_complete_current_roster"),
    "osm_node_4673303646": (None, "Yenibosna_named_Turkcell_Superonline_data_center_point_not_reconciled_to_the_four_new_generation_sites_or_a_complete_current_roster"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


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
    for source in SITES:
        row = dict(source)
        row.update({
            "id": f"turkcell_tdc_provider_site_{source['code'].lower()}",
            "object_type": "CurrentNewGenerationThirdPartyDataCenter",
            "country": "Turkiye",
            "asset_holder": "TDC_Veri_Hizmetleri_AS_after_2025_02_20_partial_demerger",
            "parent": "Turkcell_Iletisim_Hizmetleri_AS_100_percent_effective_ownership_at_2025_year_end",
            "service_interfaces": ["Turkcell", "Turkcell_Superonline", "Turkcell_Digital_Business_Services"],
            "lifecycle": "operating_new_generation_data_center_available_for_third_party_sales_at_2025_year_end",
            "certifications": ["Uptime_Tier_III_Design", "Uptime_Tier_III_Facility", "Uptime_Tier_III_Operations", "LEED_Gold", "PCI_DSS", "ISO_and_TSE_50600_portfolio_certifications"],
            "architecture": ["modular", "hot_and_cold_aisle_management", "redundant_cooling", "UPS", "generators", "redundant_fiber_and_radiolink"],
            "capacity_boundary": "Provider site figures are design white space and total IT energy capacity, not current live, sold, occupied, billed or customer-accepted load.",
            "equipment_boundary": "No site-level grid voltage, transformer, switchgear, busway, PDU, UPS, battery, generator, fuel, chiller, CRAH, CRAC, CDU, pump, heat exchanger or cooling-tower OEM, model, count, rating, loading, test state, age or remaining life was established.",
            "accessed_on": accessed_on,
        })
        records.append(row)

    for osm_id, source in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"turkcell_tdc_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityLocationEvidence",
            "country": "Turkiye",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_start_date": source.get("tags", {}).get("start_date"),
            "source_url": source["source_url"],
            "count_boundary": "An OSM point or geometry is location evidence, not proof of the provider's current site count, lifecycle, title, gross floor or white-space area, IT load, equipment, GPU inventory or financial contribution.",
            "accessed_on": accessed_on,
        })

    assert len(records) == 10
    assert sum(row["object_type"] == "CurrentNewGenerationThirdPartyDataCenter" for row in records) == 4
    assert sum(row["object_type"] == "OSMFacilityLocationEvidence" for row in records) == 6
    assert sum(row.get("matched_provider_code") is not None for row in records if row["object_type"] == "OSMFacilityLocationEvidence") == 3
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sites = [row for row in records if row["object_type"] == "CurrentNewGenerationThirdPartyDataCenter"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityLocationEvidence"]
    matched_osm = [row for row in osm if row["matched_provider_code"]]
    site_IT_sum = round(sum(row["total_IT_energy_capacity_MW"] for row in sites), 1)
    site_white_space_sum = sum(row["design_white_space_m2"] for row in sites)
    site_area_sum = sum(row["gross_site_area_m2"] for row in sites)
    assert site_IT_sum == 53.8
    assert site_white_space_sum == 31_550
    assert site_area_sum == 130_972
    assert round(sum(row["OSM_footprint_area_m2"] or 0 for row in matched_osm), 3) == 42_635.634
    assert round(sum(row["OSM_footprint_area_m2"] or 0 for row in osm), 3) == 46_629.398

    return {
        "id": "turkcell_tdc_data_center_summary_2026_07_19",
        "operator_boundary": "Turkcell_group_data_center_and_cloud_business_with_assets_transferred_from_Turkcell_Superonline_to_wholly_owned_TDC_on_2025_02_20",
        "accessed_on": accessed_on,
        "ownership_and_reporting_scope": {
            "TDC_incorporated": "2024_07_11",
            "asset_transfer": "Turkcell_Superonline_data_center_assets_transferred_to_TDC_by_partial_demerger_on_2025_02_20",
            "TDC_effective_ownership_at_2025_year_end_percent": 100,
            "listed_parent": "Turkcell_Iletisim_Hizmetleri_AS_NYSE_TKC_and_BIST_TCELL",
            "ultimate_parent": "Turkiye_Wealth_Fund",
            "boundary": "TDC is the legal data-center and cloud subsidiary after the demerger; Turkcell and Superonline remain commercial and network interfaces. Group, Turkcell Turkiye, Digital Business Services, data-center, cloud and TDC results are different reporting scopes.",
        },
        "site_count_reconciliation": {
            "managed_data_centers_2025_20F": 32,
            "new_generation_sites_available_for_third_party_sales": 4,
            "current_corporate_product_page_sites": 8,
            "2024_company_statement_sites": 33,
            "current_four_site_roster": [row["code"] for row in sites],
            "complete_current_other_managed_or_eight_product_page_site_roster": "undisclosed",
            "boundary": "The thirty-two managed locations include a wider network or internal scope; eight is a commercial product-page count; four is the precisely named new-generation third-party portfolio. The dated thirty-three-site statement is not treated as current after the 2025 Kartal phase-out.",
        },
        "scale_and_power": {
            "four_new_generation_provider_headline": {"design_white_space_m2": 31_550, "potential_IT_power_capacity_MW": 54, "commissioned_active_capacity_MW": 50},
            "four_site_numeric_checksum": {"gross_site_area_m2": site_area_sum, "design_white_space_m2": site_white_space_sum, "site_IT_energy_capacity_MW": site_IT_sum},
            "current_product_page_dated_or_conflicting_closed_area_m2": 122_000,
            "site_rows": [{key: row[key] for key in ["code", "provider_site_name", "opened_year", "gross_site_area_m2", "design_white_space_m2", "total_IT_energy_capacity_MW"]} for row in sites],
            "boundary": "The 54MW headline is the rounded provider total of four site figures summing to 53.8MW. The 50MW active-capacity headline is not allocated by site and does not equal live, sold, occupied, billed or customer-accepted load. The product-page 122,000 square metres conflicts with the current 20-F site sum and is retained as a dated or differently scoped value.",
        },
        "power_cooling_and_equipment": {
            "portfolio_features": ["modular_architecture", "hot_and_cold_aisle_management", "redundant_cooling", "UPS", "generators", "redundant_fiber", "radiolink", "four_location_geographic_redundancy"],
            "certification_scope": ["Tier_III_Design_Facility_and_Operations", "LEED_Gold", "PCI_DSS", "ISO_9001_27001_27017_20000_22301_10002_50001_45001_14001", "ISAE_3402", "TSE_50600"],
            "Ankara": "parking_lot_solar_panels_and_rainwater_recovery; historical_generation_statement_300000_kWh_per_year",
            "complete_per_site_grid_substation_transformer_switchgear_busway_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_acceptance_age_and_remaining_life": "undisclosed_or_incomplete",
            "current_measured_site_PUE_WUE_energy_water_emissions_and_live_liquid_cooled_MW": "undisclosed",
            "boundary": "Portfolio capabilities and certifications do not provide an as-built bill of materials, redundancy path rating, current loading, measured efficiency or site-level energy and water balance.",
        },
        "AI_GPU_and_cloud": {
            "internal_GPU_evidence": "2025_20F_says_on_premise_LLMs_run_exclusively_on_internal_GPU_infrastructure",
            "Google_Cloud_region": "planned_new_Turkiye_region_with_three_or_more_availability_zones_expected_in_or_around_2028_to_2029",
            "Turkcell_investment_target_USD_b_to_2032": 1,
            "joint_investment_public_statement_USD_b": 3,
            "capacity_target": "more_than_double_data_center_capacity_by_end_2032",
            "revenue_target": "sixfold_data_center_reach_and_cloud_revenue_in_USD_terms_by_end_2032",
            "exact_current_Turkcell_TDC_Google_customer_or_partner_physical_GPU_accelerator_model_count_owner_site_delivery_acceptance_server_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "Internal GPU infrastructure proves accelerator use but not model, count or data-center placement. Google Cloud capabilities, future AI demand and partnership investment are not a current Turkcell-owned GPU inventory.",
        },
        "financial_and_investability": {
            "data_center_and_cloud_2025_TRY_m": {"data_center_revenue": 3148.5, "cloud_service_revenue": 1945.8, "combined_checksum": 5094.3, "company_rounded_combined_public_statement": 5100, "2024_combined_public_statement": 3500, "real_growth_percent": 45.0},
            "Digital_Business_Services_2025_TRY_m": {"revenue": 22759.1, "recurring_services_revenue": 16477.9, "hardware_revenue": 6281.2},
            "Turkcell_Group_2025_TRY_m_IAS29": {"revenue": 241470.8, "operating_profit": 38313.6, "adjusted_EBITDA": 104017.0, "profit_for_year": 17604.0},
            "TDC": {"standalone_revenue_operating_profit_EBITDA_cash_flow_capex_assets_debt_customer_concentration_utilization_and_ROIC": "not_separately_disclosed", "five_year_murabaha_financing_EUR_m": 100, "facility_fully_utilized_on": "2025_05_26"},
            "Q1_2026_current_signal_TRY_b": {"group_revenue": 68.4, "group_adjusted_EBITDA": 28.3, "net_profit": 4.6, "data_center_and_cloud_year_on_year_growth_percent": 21, "Digital_Business_Services_year_on_year_growth_percent": 64},
            "direct_public_equity_security": "Turkcell_parent_listed_on_NYSE_and_BIST_not_a_data_center_pure_play",
            "boundary": "Data-center and cloud revenues are disclosed separately and add to the rounded public combined statement, but their operating profit, cash flow and capital returns are not. Group and Digital Business Services margins cannot be attributed to TDC.",
        },
        "outlook": {
            "2026_group_guidance": {"revenue_growth_percent": "5_to_7", "adjusted_EBITDA_margin_percent": "40_to_42", "operational_capex_to_revenue_percent": "approximately_25"},
            "2032_data_center_and_cloud": {"Turkcell_investment_USD_b": 1, "capacity": "more_than_double", "USD_revenue_and_reach": "sixfold", "Google_region_expected": "2028_to_2029"},
            "positive_signals": ["four_named_Tier_III_new_generation_sites", "50MW_active_capacity", "2025_combined_data_center_and_cloud_revenue_5_0943_billion_TRY", "Q1_2026_data_center_and_cloud_growth_21_percent", "Google_Cloud_region_partnership", "100_million_EUR_TDC_financing", "internal_GPU_infrastructure"],
            "conversion_tests": ["publish_complete_managed_and_commercial_site_rosters", "bridge_54MW_potential_and_50MW_active_to_live_and_billed_load", "identify_GPU_model_count_owner_and_site", "disclose_TDC_operating_profit_cash_flow_and_ROIC", "deliver_Google_region_and_capacity_expansion", "publish_current_site_PUE_WUE_and_equipment_inventory"],
            "risks": ["capital_intensity", "power_supply_and_energy_cost", "hyperinflation_and_currency", "Google_execution_and_partner_dependency", "no_GPU_inventory", "no_site_utilization", "no_TDC_profitability", "mixed_network_and_commercial_site_counts"],
            "analytical_view": "Turkcell is unusually useful listed-parent exposure because it discloses named site power and data-center plus cloud revenue. It remains a diversified telecom, and the investment proof requires TDC profitability, live billed load, GPU ownership and delivery of the Google-linked expansion rather than headline capacity alone.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "current_new_generation_matches": len(matched_osm),
            "unreconciled_or_legacy_objects": [row["OSM_ref"] for row in osm if not row["matched_provider_code"]],
            "matched_footprint_area_m2_sum_not_floor_area": round(sum(row["OSM_footprint_area_m2"] or 0 for row in matched_osm), 3),
            "all_related_footprint_area_m2_sum_not_floor_area": round(sum(row["OSM_footprint_area_m2"] or 0 for row in osm), 3),
            "operator_labeled_objects_routed_by_coverage_audit": 5,
            "named_but_operator_untagged_Yenibosna_point": 1,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Three geometries reconcile to named current new-generation sites. Kartal is a phased-out legacy site, while Edirne and Yenibosna are not assigned to a complete current wider roster. Footprints are not provider floor area or capacity.",
        },
        "records": records,
        "sources": [TURKCELL_2025_20F_URL, TURKCELL_DATA_CENTER_URL, TURKCELL_WHOLESALE_URL, TURKCELL_FACILITIES_GUIDE_URL, TURKCELL_ANKARA_URL, TURKCELL_TDC_FINANCING_URL, TURKCELL_GOOGLE_URL, TURKCELL_2025_RESULTS_URL, TURKCELL_Q1_2026_URL],
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
    registry_path = args.output_dir / "turkcell_tdc_data_center_registry.jsonl"
    summary_path = args.output_dir / "turkcell_tdc_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "current_new_generation_sites": 4,
        "OSM_objects": 6,
        "OSM_current_new_generation_matches": 3,
        "site_IT_capacity_checksum_MW": 53.8,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
