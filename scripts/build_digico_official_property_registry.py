#!/usr/bin/env python3
"""Build a scope-preserving DigiCo Infrastructure REIT property registry.

DigiCo's legal property count, current website directory, operating facilities,
development land, contracted sales and portfolio MW use different scopes.  This
builder preserves those scopes, joins the seven local OSM objects, and keeps
provider or customer AI-readiness statements separate from installed GPUs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


PDS = "https://announcements.asx.com.au/asxpdf/20241212/pdf/06ckxj5xhzpb18.pdf"
DIRECTORY = "https://www.digi-co.com.au/data-centres/"
HY26_PRESENTATION = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/financial-reports-presentations/hy26-results-presentation/"
HY26_REPORT = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/financial-reports-presentations/appendix-4d-and-hy26-financial-report/"
FY25_ANNUAL = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/financial-reports-presentations/dgt-annual-report-2025/"
FY25_RESULTS = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/financial-reports-presentations/dgt-fy25-results-presentation/"
IPO = "https://www.hmccapital.com.au/insights/hmc-capital-today-announces-the-establishment-of-a-new-asx-listed-digital-infrastructure-reit-asxdgt-digico-reit/"
GSA_ACQUISITION = "https://www.hmccapital.com.au/insights/hmc-capital-announces-strategic-acquisition-to-seed-global-digico-platform-and-300m-equity-raise/"
CHI1_SALE = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/sale-of-chi1-and-strengthened-balance-sheet/"
LAX_SALE = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/digico-contracts-lax-sale/"
LAX1_WITHDRAWAL = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/digico-withdraws-lax1-development-application/"
H2_DISTRIBUTION = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/h2-fy26-distribution-and-capital-management/"
CEO_UPDATE = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/ceo-update/"
FY26_NOTICE = "https://www.hmccapital.com.au/investment-strategies/digital-infrastructure/digico-infrastructure-reit/asx-announcements/advance-notice-2026-full-year-financial-results/"
SYD1_PLANNING = "https://www.planningportal.nsw.gov.au/major-projects/projects/digico-syd1-data-centre-expansion?page=0"
SYD1_DECISION = "https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=SSD-69637456%2120251223T231353.358+GMT"
SYD1_EQUIPMENT = "https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=SSD-69637456%2120250410T071257.407+GMT"
SHARONAI_10K = "https://www.sec.gov/Archives/edgar/data/2068385/000149315226014068/form10-k.htm"
SHARONAI_424B3 = "https://www.sec.gov/Archives/edgar/data/2068385/000149315226030362/form424b3.htm"
SHARONAI_8K = "https://www.sec.gov/Archives/edgar/data/2068385/000149315226014475/form8-k.htm"


LOCATION_PAGES = {
    "SYD1": "https://www.digi-co.com.au/location/sydney-syd1/",
    "ADL1": "https://www.digi-co.com.au/location/adelaide-adl1/",
    "ADL2": "https://www.digi-co.com.au/location/adelaide-adl2/",
    "BNE": "https://www.digi-co.com.au/location/brisbane-bne/",
    "BNE1": "https://www.digi-co.com.au/location/brisbane-bne1/",
    "BNE2": "https://www.digi-co.com.au/location/brisbane-bne2/",
    "BNE3": "https://www.digi-co.com.au/location/brisbane-bne3/",
    "TSV1": "https://www.digi-co.com.au/location/townsville-tsv1/",
    "CHI1": "https://www.digi-co.com.au/location/chicago-chi1/",
    "DAL1": "https://www.digi-co.com.au/location/dallas-dal1/",
    "KCM1": "https://www.digi-co.com.au/location/kansas-kcm1/",
}


def property_record(
    code: str,
    country: str,
    market: str,
    locality: str,
    lifecycle: str,
    pds: dict,
    technical: dict | None = None,
    current_updates: dict | None = None,
    source_urls: list[str] | None = None,
    publication_conflicts: list[str] | None = None,
) -> dict:
    pages = [PDS]
    if code in LOCATION_PAGES:
        pages.extend([DIRECTORY, LOCATION_PAGES[code]])
    pages.extend(source_urls or [])
    return {
        "id": f"digico_{code.lower()}",
        "property_code": code,
        "country_code": country,
        "market": market,
        "locality": locality,
        "current_provider_directory_page": code in LOCATION_PAGES,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "legal_ownership_as_of_2026_07_19": "retained_pending_sale_completion" if code in {"CHI1", "LAX1", "LAX2"} else "held",
        "PDS_metrics": pds,
        "technical_evidence": technical or {},
        "current_updates": current_updates or {},
        "publication_conflicts": publication_conflicts or [],
        "physical_GPU_or_accelerator_inventory_at_site": "undisclosed",
        "AI_or_liquid_cooling_readiness_is_not_GPU_inventory": True,
        "source_urls": list(dict.fromkeys(pages)),
    }


PROPERTIES = [
    property_record(
        "DAL1", "US", "Dallas", "Richardson_Texas", "operating_enterprise_facility",
        {"opened": 2015, "tier": "III", "NLA_sqm_table": 11915, "white_space_sqm": 3716, "installed_IT_mw": 4.5, "contracted_IT_mw": 4.5, "planned_IT_mw": 4.5, "contracted_utilization_percent": 100, "lease_type": "absolute_net"},
        publication_conflicts=["PDS_table_NLA_11915sqm_vs_narrative_11015sqm"],
    ),
    property_record(
        "KCM1", "US", "Kansas_City", "Olathe_Kansas", "operating_enterprise_facility",
        {"opened": 2016, "tier": "III", "NLA_sqm_table": 18018, "white_space_sqm": 6582, "installed_IT_mw": 7.5, "contracted_IT_mw": 7.5, "planned_IT_mw": 7.5, "contracted_utilization_percent": 100, "lease_type": "absolute_net"},
        publication_conflicts=["PDS_table_NLA_18018sqm_vs_narrative_approximately_18000sqm"],
    ),
    property_record(
        "CHI1", "US", "Chicago", "Elk_Grove_Village_Illinois", "phased_turnkey_delivery_partly_billing_sale_contract_signed_pending_close",
        {"tier": "III", "NLA_sqm_table": 16185, "installed_IT_mw": "not_stated_in_PDS", "contracted_IT_mw": 32, "planned_IT_mw": 32, "lease_type": "triple_net", "lease_years": 15, "annual_escalation_percent": 3.5},
        current_updates={"first_tranche_mw_delivered_and_billing_by_2025_12_31_derived_from_portfolio_bridge": 20, "remaining_contracted_mw_scheduled": 12, "binding_sale_price_USD_million": 750, "sale_price_premium_to_book_value_percent_approximate": 5, "passing_yield_percent": 5.8, "expected_close": "Q1_FY2027", "sale_completion_confirmed_in_reviewed_sources": False},
        source_urls=[HY26_PRESENTATION, CHI1_SALE],
        publication_conflicts=["PDS_table_NLA_16185sqm_vs_narrative_approximately_16000sqm", "20MW_is_a_derived_residual_from_32MW_North_America_billing_less_DAL1_and_KCM1_not_a_site_meter_reading"],
    ),
    property_record(
        "LAX1", "US", "Los_Angeles", "Monterey_Park_California", "vacant_office_land_data_center_application_withdrawn_conditional_sale_pending",
        {"land_sqm": 54673, "installed_IT_mw": 0, "contracted_IT_mw": 0, "PDS_planned_IT_mw": 36},
        technical={"withdrawn_design": {"data_halls": 7, "data_hall_area_sqm": 10216, "support_area_sqm": 8547, "proposed_emergency_generators": 12, "proposed_generator_rating_mw_each": 4}, "installed_equipment_from_withdrawn_design": False},
        current_updates={"development_application_withdrawn": "2026-04-07", "withdrawal_reason": "planning_outcome_uncertainty", "combined_LAX1_LAX2_book_value_USD_million_at_2025_12_31": 71, "conditional_sale_signed": "2026-06-12", "expected_close": "1H_FY2027", "sale_completion_confirmed_in_reviewed_sources": False},
        source_urls=[LAX1_WITHDRAWAL, LAX_SALE],
        publication_conflicts=["PDS_36MW_design_vs_post_withdrawal_portfolio_bridge_implying_33MW_per_LAX_site"],
    ),
    property_record(
        "LAX2", "US", "Los_Angeles", "Monterey_Park_California", "vacant_office_land_no_live_data_center_conditional_sale_pending",
        {"land_sqm": 78528, "installed_IT_mw": 0, "contracted_IT_mw": 0, "PDS_planned_IT_mw": 36},
        current_updates={"combined_LAX1_LAX2_book_value_USD_million_at_2025_12_31": 71, "combined_land_acres": 33, "conditional_sale_signed": "2026-06-12", "expected_close": "1H_FY2027", "sale_completion_confirmed_in_reviewed_sources": False},
        source_urls=[LAX1_WITHDRAWAL, LAX_SALE],
        publication_conflicts=["PDS_36MW_design_vs_post_withdrawal_portfolio_bridge_implying_33MW_per_LAX_site"],
    ),
    property_record(
        "BNE1", "AU", "Brisbane", "Brisbane_Airport", "operating_colocation_facility",
        {"opened": 2010, "tier": "III", "NLA_sqm": 900, "land_sqm": 3567, "installed_IT_mw": 1.8, "contracted_IT_mw": 1.2, "planned_IT_mw": 1.8, "contracted_utilization_percent": 64},
        technical={"electrical_and_mechanical_topology": "concurrently_maintainable"},
    ),
    property_record(
        "BNE2", "AU", "Brisbane", "Brisbane_Airport", "operating_colocation_facility",
        {"opened": 2020, "tier": "IV", "NLA_sqm": 1232, "land_sqm": 6195, "installed_IT_mw": 1.7, "contracted_IT_mw": 0.6, "planned_IT_mw": 1.7, "contracted_utilization_percent": 37},
        technical={"liquid_cooling_trial": True, "GPU_model_or_count": "undisclosed"},
    ),
    property_record(
        "BNE", "AU", "Brisbane", "Woolloongabba", "operating_colocation_facility",
        {"PDS_code": "BNE3", "opened": 2006, "tier": "II", "NLA_sqm": 243, "land_sqm": 2345, "installed_IT_mw": 0.3, "contracted_IT_mw": 0.2, "planned_IT_mw": 0.3, "contracted_utilization_percent": 67},
        technical={"fiber_ring_to_BNE1_and_BNE2_km": 60, "core_and_shell_lease_expiry": 2035},
        publication_conflicts=["PDS_BNE3_was_renamed_current_BNE"],
    ),
    property_record(
        "TSV1", "AU", "Townsville", "Townsville_Queensland", "operating_colocation_facility",
        {"opened": 2019, "tier": "III", "NLA_sqm": 285, "land_sqm": 2550, "installed_IT_mw": 0.5, "contracted_IT_mw": 0.2, "planned_IT_mw": 0.5, "contracted_utilization_percent": 34},
        technical={"cyclone_resistance": "Category_5", "core_and_shell_lease_expiry": 2049},
    ),
    property_record(
        "ADL1", "AU", "Adelaide", "Edinburgh_Parks", "operating_colocation_facility_with_expansion_option",
        {"opened": 2016, "tier": "III", "NLA_sqm": 2280, "land_sqm": 22920, "installed_IT_mw": 1.2, "contracted_IT_mw": 0.6, "PDS_future_expansion_IT_mw": 8, "PDS_planned_IT_mw": 9.2, "contracted_utilization_percent": 52},
        current_updates={"potential_expansion_upsized_from_mw": 8, "potential_expansion_upsized_to_mw": 15, "cornerstone_customer_condition": True},
        source_urls=[HY26_PRESENTATION],
        publication_conflicts=["PDS_table_mislabels_2280sqm_NLA_as_land_area_while_narrative_land_is_22920sqm"],
    ),
    property_record(
        "ADL2", "AU", "Adelaide", "Hawthorn", "operating_colocation_facility",
        {"opened": 2015, "tier": "II", "NLA_sqm": 580, "land_sqm": 1506, "installed_IT_mw": 0.6, "contracted_IT_mw": 0.4, "planned_IT_mw": 0.6, "contracted_utilization_percent": 67},
    ),
    property_record(
        "BNE3", "AU", "Brisbane", "Brisbane_Airport", "greenfield_development_not_operating",
        {"PDS_code": "BNE4", "land_sqm": 9786, "installed_IT_mw": 0, "contracted_IT_mw": 0, "planned_IT_mw": 19.6, "projected_racks_approximate": 2496, "design_target": "Tier_IV", "projected_completion": "CY2027"},
        publication_conflicts=["PDS_BNE4_was_renamed_current_BNE3"],
    ),
    property_record(
        "SYD1", "AU", "Sydney", "Ultimo", "operating_two_building_campus_with_approved_expansion",
        {"land_sqm": 11035, "NLA_sqm": 37835, "west_building_levels": 7, "west_building_NLA_sqm": 25180, "east_building_levels": 5, "east_building_NLA_sqm": 12655, "PDS_installed_IT_mw": 26.2, "PDS_contracted_IT_mw": 20, "PDS_future_expansion_IT_mw": 61.8, "PDS_planned_IT_mw": 88, "PDS_contracted_utilization_percent": 76, "design_PUE_range": [1.3, 1.5], "secured_power_MVA": 120},
        technical={"approved_expansion": {"old_total_IT_mw": 42.5, "approved_total_IT_mw": 88, "power_consumption_increase_mw": 47.5, "additional_emergency_generators": 24, "total_emergency_generators_after_expansion": 66}, "high_density_and_liquid_cooling_ready": True, "flexible_deployment_blocks_mw": "5_to_10_plus", "acquired_equipment_categories": ["power_distribution_units", "automatic_static_transfer_switches", "triple_filters", "cooling_generators_and_related_assets_as_worded_in_acquisition_note"], "equipment_OEM_models_and_complete_as_built_BOM": "undisclosed_or_commercial_in_confidence"},
        current_updates={"current_capacity_contracted_percent": 100, "first_15MW_expansion_practical_completion_confirmed": "2026-05-06", "remaining_5MW_target": "before_2026-06-30", "remaining_5MW_completion_confirmed_in_reviewed_sources": False, "full_88MW_SSD_approval": "2025-12-23", "next_10MW_target": "Q2_2027", "full_expansion_target": "FY2029", "target_yield_on_cost_percent": 15, "target_NAV_uplift_AUD_per_security_approximate": 1.50},
        source_urls=[HY26_PRESENTATION, CHI1_SALE, SYD1_PLANNING, SYD1_DECISION, SYD1_EQUIPMENT],
        publication_conflicts=["target_yield_and_NAV_uplift_are_management_targets_not_realized_returns", "remaining_5MW_target_is_not_a_completion_confirmation"],
    ),
]


OSM_CROSSWALK = {
    "osm_way_544451114": "digico_adl1",
    "osm_way_812989671": "digico_adl2",
    "osm_relation_19402810": "digico_bne1",
    "osm_relation_19402811": "digico_bne2",
    "osm_way_100109132": "digico_syd1",
    "osm_way_474805153": "digico_syd1",
    "osm_way_1262899342": "digico_tsv1",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(PROPERTIES, start=1):
        records.append({
            "object_type": "DataCenterPropertyEvidence",
            "source_order": order,
            "operator": "DigiCo_Infrastructure_REIT",
            "accessed_on": accessed_on,
            **source,
        })
    assert len(records) == 13
    assert len({row["property_code"] for row in records}) == 13
    assert Counter(row["country_code"] for row in records) == {"AU": 8, "US": 5}
    assert sum(row["current_provider_directory_page"] for row in records) == 11
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, property_ref in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert source.get("operator") == "DigiCo"
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "property_ref": property_ref,
            "crosswalk_status": "exact_current_provider_code_candidate",
            "source_url": source["source_url"],
            "boundary": "OSM geometry is not provider-certified title, current lifecycle, floor area, IT load, utilization or GPU inventory.",
        })
    assert len(rows) == 7
    assert Counter(row["property_ref"] for row in rows)["digico_syd1"] == 2
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    pds_planned = {
        row["property_code"]: row["PDS_metrics"].get("planned_IT_mw", row["PDS_metrics"].get("PDS_planned_IT_mw"))
        for row in records
    }
    pds_sum = round(sum(value for value in pds_planned.values() if isinstance(value, (int, float))), 1)
    assert pds_sum == 237.7
    operating_codes = ["DAL1", "KCM1", "BNE1", "BNE2", "BNE", "TSV1", "ADL1", "ADL2", "SYD1"]
    return {
        "id": "digico_official_property_summary_2026_07_19",
        "object_type": "DigiCoPortfolioReconciliation",
        "accessed_on": accessed_on,
        "legal_property_ledger": {
            "properties": len(records),
            "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
            "current_provider_directory_labels": sum(row["current_provider_directory_page"] for row in records),
            "source_established_operating_property_labels": len(operating_codes),
            "operating_property_codes": operating_codes,
            "phased_delivery_sale_pending": ["CHI1"],
            "greenfield_development_not_operating": ["BNE3"],
            "vacant_land_or_withdrawn_development_sale_pending": ["LAX1", "LAX2"],
            "boundary": "Thirteen legally held properties are not thirteen operating data centers. CHI1 and both LAX properties remain in the legal ledger until reviewed sale-completion evidence is published.",
        },
        "capacity_reconciliation": {
            "PDS_property_planned_IT_mw_checksum": pds_sum,
            "PDS_by_property_mw": pds_planned,
            "FY2025": {"billing_IT_mw": 53, "contracted_IT_mw": 65, "installed_IT_mw": 76, "future_expansion_IT_mw": 156, "planned_IT_mw": 232},
            "HY2026": {"billing_IT_mw": 51, "contracted_IT_mw": 85, "planned_IT_mw": 238, "North_America_planned_IT_mw": 110, "Australia_planned_IT_mw": 128},
            "post_LAX1_withdrawal_announced_planned_IT_mw": 172,
            "boundary": "PDS design, installed, contracted, billing, expansion and post-withdrawal portfolio values use different dates and denominators. None is current instantaneous load or a GPU-power measure.",
        },
        "sale_and_capital_management_boundary": {
            "CHI1": {"binding_sale_USD_million": 750, "expected_close": "Q1_FY2027", "completion_confirmed": False},
            "LAX1_and_LAX2": {"conditional_sale_signed": "2026-06-12", "expected_close": "1H_FY2027", "completion_confirmed": False},
            "pro_forma_after_CHI1_sale": {"net_debt_AUD_billion_approximate": 0.5, "gearing_percent": 17, "available_liquidity_AUD_billion_approximate": 0.9},
            "available_liquidity_after_CHI1_and_LAX_sale_agreements_AUD_billion_approximate": 1.0,
            "boundary": "Pro-forma debt, gearing and liquidity are transaction scenarios, not period-end statutory balances; signed sales are not treated as closed.",
        },
        "AI_and_GPU_boundary": {
            "SharonAI_10K_names_hosting_partners": ["NEXTDC", "GreenSquare", "DigiCo"],
            "named_capabilities": ["NVIDIA_B200", "NVIDIA_B300", "NVIDIA_GB300"],
            "DigiCo_site_model_or_count_allocation": "undisclosed",
            "Australia_wide_72MW_and_up_to_40000_GB300_collaboration_assignable_to_DigiCo": False,
            "Australia_8200_B300_deployment_assignable_to_DigiCo": False,
            "provider_owned_GPU_count": "undisclosed",
            "accelerator_ledger_action": "no_numeric_row_created",
            "boundary": "SharonAI names DigiCo among multiple Australian hosts but does not allocate a site, model or unit count to DigiCo. Countrywide or unnamed-site deployments are not assigned to this portfolio.",
        },
        "public_map_crosswalk": {
            "DigiCo_operator_tagged_OSM_objects": len(osm_rows),
            "matched_property_codes": sorted({row["property_ref"].removeprefix("digico_").upper() for row in osm_rows}),
            "objects": osm_rows,
            "boundary": "Seven OSM objects cover six property codes because SYD1 has two mapped buildings; the objects are not a complete legal or operating estate census.",
        },
        "unresolved_gaps": [
            "13_legal_properties_to_exact_current_title_lease_buildings_and_sale_completion",
            "CHI1_remaining_12MW_delivery_customer_acceptance_billing_and_sale_close",
            "SYD1_remaining_5MW_completion_and_next_10MW_grid_fitout_customer_acceptance_and_billing",
            "BNE3_ADL1_and_SYD1_expansion_permits_grid_energization_construction_customer_commitments_and_returns",
            "per_site_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CDU_models_counts_ratings_OEMs_and_as_built_topology",
            "per_site_measured_PUE_WUE_water_energy_hourly_renewable_matching_live_liquid_cooled_MW_and_actual_load",
            "DigiCo_hosted_GPU_model_count_owner_site_power_utilization_revenue_and_margin",
            "site_level_revenue_operating_profit_NOI_capex_debt_customer_concentration_utilization_and_ROIC",
        ],
        "sources": sorted({url for row in records for url in row["source_urls"]} | {HY26_REPORT, FY25_ANNUAL, FY25_RESULTS, IPO, GSA_ACQUISITION, H2_DISTRIBUTION, CEO_UPDATE, FY26_NOTICE, SHARONAI_10K, SHARONAI_424B3, SHARONAI_8K}),
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
    registry = args.output_dir / "digico_official_property_registry.jsonl"
    summary_path = args.output_dir / "digico_official_property_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
