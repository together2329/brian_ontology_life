#!/usr/bin/env python3
"""Build a lifecycle-safe Stellanor and legacy Redcentric facility registry.

Stellanor operates eleven UK data centers after acquiring two former Colt
Technology Services sites, eight former Redcentric sites and one former
Imagination Technologies site.  Six OSM objects still carry Redcentric as the
operator.  This builder retains that history while routing the physical assets
to their current operator and keeping grid, site-maximum, UPS, generator,
cooling and financial reporting scopes separate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://www.stellanordatacenters.com/"
DIRECTORY = "https://www.stellanordatacenters.com/our-data-centers/"
REDCENTRIC_LEGACY = "https://redcentricdatacentres.co.uk/"
REDCENTRIC_ACQUISITION = "https://www.stellanordatacenters.com/stellanor-completes-acquisition-of-eight-data-centers-from-redcentric/"
COLT_TS_ACQUISITION = "https://www.stellanordatacenters.com/stellanor-datacenters-now-online-and-already-growing/"
IMAGINATION_ACQUISITION = "https://www.stellanordatacenters.com/stellanor-expands-to-11-facilities-with-acquisition-of-ai-ready-data-center-from-imagination-technologies/"
SUSTAINABILITY = "https://www.stellanordatacenters.com/about-us/sustainable-data-centers/"
REDCENTRIC_FY25 = "https://www.redcentricplc.com/wp-content/uploads/Redcentric-report-and-accounts-FY25.pdf"
REDCENTRIC_FY25_PRESENTATION = "https://www.redcentricplc.com/wp-content/uploads/Redcentric-FY25-Results-Presentation-24-Sep-25.pdf"
REDCENTRIC_H1_FY26 = "https://www.redcentricplc.com/wp-content/uploads/Redcentric-H1-FY26-Results-Presentation-10-Dec-25.pdf"
DISPOSAL_ANNOUNCEMENT = "https://www.lse.co.uk/rns/disposal-of-redcentric-data-centres-limited-490cr8ywa9gvtxj.html"
DISPOSAL_COMPLETION = "https://www.lse.co.uk/rns/completion-of-sale-of-redcentric-data-centres-ltd-d9mjg1do6k24a25.html"
STELLANOR_UK_COMPANY = "https://find-and-update.company-information.service.gov.uk/company/16344352"
STELLANOR_GROUP_COMPANY = "https://find-and-update.company-information.service.gov.uk/company/16534947"
STELLANOR_GROUP_PSC = "https://find-and-update.company-information.service.gov.uk/company/16534947/persons-with-significant-control"


def site(slug: str) -> str:
    return f"https://www.stellanordatacenters.com/our-data-centers/{slug}/"


def facility(
    code: str,
    slug: str,
    address: str,
    acquisition_lineage: str,
    published_metrics: dict,
    electrical: dict,
    cooling: dict,
    ai_and_density: dict | None = None,
    additional_sources: list[str] | None = None,
    publication_conflicts: list[str] | None = None,
) -> dict:
    return {
        "id": f"stellanor_{slug.replace('-', '_')}",
        "facility_code": code,
        "country_code": "GB",
        "address": address,
        "lifecycle_as_of_2026_07_19": "operating",
        "current_operator": "Stellanor_Datacenters",
        "acquisition_lineage": acquisition_lineage,
        "published_metrics": published_metrics,
        "electrical_and_backup_power_evidence": electrical,
        "cooling_evidence": cooling,
        "AI_and_high_density_evidence": ai_and_density or {},
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "capability_or_customer_workload_is_not_operator_GPU_inventory": True,
        "publication_conflicts": publication_conflicts or [],
        "source_urls": list(dict.fromkeys([site(slug), *(additional_sources or [])])),
    }


FACILITIES = [
    facility(
        "London_City",
        "london-city",
        "Lifeline House, 80 Clifton Street, London EC2A 4HB",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 2400, "fitted_colocation_area_sqm": 1500, "maximum_site_power_mva": 2},
        {
            "incoming_power_published_verbatim": "dual_redundant_2_MVA_incoming_feeds",
            "UPS_topology": "N_plus_N",
            "UPS_capacity_kw": 500,
            "diesel_generators": 1,
            "generator_capacity_mva": 1.1,
            "generator_start": "automatic_100_percent",
            "fuel_runtime_hours_at_100_percent": 48,
        },
        {"technology": ["DX", "in_row", "CRAC"], "redundancy": "N_plus_1"},
        additional_sources=[REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "London_East",
        "london-east",
        "6 Braham Street, London E1 8EE",
        "former_Colt_Technology_Services_facility_acquired_by_Stellanor_2025_09_01",
        {"operating_since": 1999, "total_area_sqm": 8046, "fitted_colocation_area_sqm": 2940, "maximum_site_power_mva": 4},
        {
            "incoming_power_published_verbatim": "dual_redundant_3_MVA_incoming_feeds",
            "UPS_topology": "N_plus_1",
            "UPS_capacity_kw": 1500,
            "diesel_generators": 2,
            "generator_total_capacity_mva": 4,
            "automatic_start_within_minutes": 1,
            "fuel_runtime_hours": 24,
            "local_fuel_supplier": True,
        },
        {"technology": "chilled_water", "cooling_capacity_mw": 3, "redundancy": "N_plus_1"},
        additional_sources=[COLT_TS_ACQUISITION],
    ),
    facility(
        "London_North",
        "london-north",
        "260-266 Goswell Road, London EC1V 7EB",
        "former_Colt_Technology_Services_facility_acquired_by_Stellanor_2025_09_01",
        {"operating_since": 2000, "total_area_sqm": 25143, "fitted_colocation_area_sqm": 12212, "maximum_site_power_mva": 20},
        {
            "incoming_power_published_verbatim": "dual_redundant_10_MVA_7300_kW_dedicated_underground_cable_feeds_to_dedicated_dual_redundant_4_MVA_transformer_station",
            "UPS_systems": ["3x500_kVA", "4x625_kVA", "3x625_kVA_undergoing_upgrade", "3x500_kVA", "3x550_kVA"],
            "UPS_total_facility_capacity_kva": 9500,
            "UPS_topology": "N_plus_1_hybrid_rotary_and_static",
            "battery_autonomy_minutes_per_module": 15,
            "distribution": "A_and_B_underfloor_power_track",
            "generator_published_verbatim": "4_x_4.3_MVA_giving_4_MVA",
            "automatic_start_within_minutes": 1,
            "fuel_runtime_hours": 24,
        },
        {"published_average_density_w_per_sqm": 750},
        additional_sources=[
            COLT_TS_ACQUISITION,
            "https://www.stellanordatacenters.com/wp-content/uploads/2025/07/Stellanor-London-North-Datasheet.pdf",
        ],
        publication_conflicts=[
            "The provider page mixes 10 MVA, 7,300 kW and a 4 MVA transformer-station description; values are retained verbatim rather than normalized.",
            "The provider generator line says four 4.3-MVA units while also saying 'giving 4 MVA'; the conflict is retained.",
        ],
    ),
    facility(
        "London_West",
        "london-west",
        "Unit B, Heathrow Corporate Park, Hounslow TW4 6ER",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 18116, "fitted_colocation_area_sqm": 12077, "maximum_site_power_mva": 22},
        {
            "incoming_power_published_verbatim": "dual_redundant_22_MVA_total_incoming_power",
            "UPS_topology": "2N_plus_1",
            "UPS_capacity_kw": 3000,
            "generator_total_capacity_mva": 25,
            "fuel_runtime_hours": 72,
        },
        {"technology": "chilled_water", "chillers": 8, "cooling_capacity_mw": 8.5, "CCU_redundancy": "N_plus_1"},
        {"supported_rack_density_kw_up_to": 100, "provider_use_case": "AI_and_HPC_ready"},
        [REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "Byfleet",
        "byfleet",
        "122 Oyster Lane, Byfleet KT14 7JU",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 1400, "fitted_colocation_area_sqm": 600, "maximum_site_power_mva": 1},
        {"incoming_power_mva": 1, "UPS_topology": "N_plus_1", "UPS_capacity_kw": 600, "diesel_generators": 1, "generator_capacity_mva": 2, "fuel_runtime_hours": 72},
        {"technology": "direct_evaporative", "cooling_capacity_mw": 0.78, "redundancy": "N_plus_1"},
        additional_sources=[REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "Cambridge",
        "cambridge",
        "Newton House, Cowley Road, Cambridge CB4 0WZ",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": "undisclosed", "fitted_colocation_area_sqm": "undisclosed", "maximum_site_power_mva": "undisclosed", "supported_cabinet_density_kw": 3},
        {"online_double_conversion_three_phase_UPS_units": 3, "UPS_capacity_kva_each": 100, "standby_diesel_voltage_v": 400, "standby_diesel_phases": 3, "generator_start": "automatic_100_percent", "fuel_runtime_hours": "undisclosed"},
        {"technology": ["downflow_air", "traditional_multi_unit_air_conditioning"]},
        additional_sources=[REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "Gatwick",
        "gatwick",
        "17-19 Kelvin Lane, Crawley RH10 9EY",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 1400, "fitted_colocation_area_sqm": 818, "maximum_site_power_mva": 1},
        {"incoming_power_mva": 1, "UPS_topology": "2N", "UPS_capacity_kw": 400, "diesel_generators": 1, "generator_capacity_mva": 1, "fuel_runtime_hours": 72},
        {"technology": "chilled_water", "cooling_towers": 2, "cooling_capacity_mw": 1, "redundancy": "N_plus_1", "high_density_options": ["CCU", "rear_door_heat_exchanger", "immersion_cooling"]},
        {"liquid_cooling_options": ["rear_door_heat_exchanger", "immersion_cooling"], "live_liquid_cooled_capacity_mw": "undisclosed"},
        [REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "Hemel_Hempstead",
        "hemel-hempstead",
        "Unit 2, Hemel Park, Boundary Way, Hemel Hempstead HP2 7YU",
        "former_Imagination_Technologies_facility_acquired_by_Stellanor_2026_04_08_sale_and_service_back",
        {"total_area_sqm": 2534, "fitted_colocation_area_sqm": "undisclosed", "maximum_site_power_mva": 3},
        {"incoming_feeds": 1, "incoming_power_mva": 3, "UPS_topology": "N_plus_1", "UPS_capacity_mw": 2, "generator_topology": "N_plus_1", "generator_total_capacity_mva": 4.5, "UPS_bridge_minutes": 7, "fuel_runtime_hours": 72},
        {"technology": "chilled_water", "chillers": 3, "dry_coolers": 1, "cooling_capacity_mw": 8.5, "redundancy": "N_plus_1", "high_density_options": ["liquid_cooling", "CCU"]},
        {"customer_workload": "Imagination_Technologies_GPU_and_AI_chip_design", "customer_remains_fully_managed_client": True, "operator_owned_or_customer_GPU_count_and_model": "undisclosed"},
        [IMAGINATION_ACQUISITION],
    ),
    facility(
        "Reading",
        "reading",
        "3-5 Worton Drive, Reading RG2 0TG",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 1477, "fitted_colocation_area_sqm": 1340, "maximum_site_power_mva": 2},
        {"incoming_power_published_verbatim": "dual_redundant_2_MVA_feeds", "UPS_topology": "N_plus_1", "UPS_capacity_mw": 1.6, "diesel_generators": 1, "generator_capacity_mva": 2.4, "fuel_runtime_hours": 72},
        {"technology": ["free_air", "DX"], "cooling_capacity_mw": 1.2, "plant_redundancy": "N_plus_2", "CCU_redundancy_per_floor": "N_plus_1"},
        additional_sources=[REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "West_Yorkshire",
        "west-yorkshire",
        "Unit J1, Lowfields Business Park, Elland HX5 9DA",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 8305, "fitted_colocation_area_sqm": 3437, "maximum_site_power_mva": 9},
        {"incoming_power_published_verbatim": "dual_redundant_9_MVA_total_incoming_power", "UPS_topology": "N_plus_1", "UPS_capacity_mw": 1, "diesel_generators": 2, "generator_total_capacity_mva": 4, "fuel_runtime_hours": 72},
        {"technology": "DX", "chillers": 16, "cooling_capacity_mw": 1.4, "CCU_redundancy": "N_plus_1"},
        {"supported_rack_density_kw_up_to": 30},
        [REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
    ),
    facility(
        "Woking",
        "woking",
        "Kestrel Way, Woking GU21 3DW",
        "former_Redcentric_facility_acquired_by_Stellanor_2026_04_30",
        {"total_area_sqm": 1477, "fitted_colocation_area_sqm": 1340, "maximum_site_power_mva": 4.5},
        {"incoming_power_published_verbatim": "dual_redundant_4.5_MVA_total_feed", "UPS_topology": "N_plus_1", "UPS_capacity_mw": 1, "diesel_generators": 2, "generator_total_capacity_mva": 4, "fuel_runtime_hours": 72},
        {"technology": "chilled_water_DFU", "chillers": 4, "cooling_capacity_published_verbatim": "4_MW_at_N", "CCU_redundancy": "N_plus_1"},
        additional_sources=[REDCENTRIC_ACQUISITION, REDCENTRIC_LEGACY],
        publication_conflicts=["The page describes cooling as 4 MW at N and separately states N+1 CCU redundancy; both scopes are retained."],
    ),
]


OSM_CROSSWALK = {
    "osm_way_55873731": "stellanor_byfleet",
    "osm_node_7829977772": "stellanor_cambridge",
    "osm_way_202085268": "stellanor_west_yorkshire",
    "osm_way_164527297": "stellanor_london_city",
    "osm_way_254132701": "stellanor_london_west",
    "osm_way_93845197": "stellanor_reading",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [{"object_type": "DataCenterFacilityEvidence", "source_order": order, "accessed_on": accessed_on, **item} for order, item in enumerate(FACILITIES, 1)]
    assert len(rows) == 11
    assert len({row["facility_code"] for row in rows}) == 11
    assert Counter(row["acquisition_lineage"].split("_facility")[0] for row in rows) == Counter({"former_Redcentric": 8, "former_Colt_Technology_Services": 2, "former_Imagination_Technologies": 1})
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, facility_ref in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert source.get("operator") == "Redcentric"
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "facility_ref": facility_ref,
            "current_operator": "Stellanor_Datacenters",
            "classification": "current_Stellanor_facility_with_legacy_Redcentric_OSM_operator_label",
            "capacity_counting_rule": "An OSM object supports an address crosswalk only; it does not establish current ownership, installed MW, utilization or GPU inventory.",
        })
    assert len(rows) == 6
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    max_power = [row["published_metrics"]["maximum_site_power_mva"] for row in records if isinstance(row["published_metrics"].get("maximum_site_power_mva"), (int, float))]
    total_area = [row["published_metrics"]["total_area_sqm"] for row in records if isinstance(row["published_metrics"].get("total_area_sqm"), (int, float))]
    colo_area = [row["published_metrics"]["fitted_colocation_area_sqm"] for row in records if isinstance(row["published_metrics"].get("fitted_colocation_area_sqm"), (int, float))]
    return {
        "id": "stellanor_official_facility_summary_2026_07_19",
        "operator": "Stellanor_Datacenters",
        "accessed_on": accessed_on,
        "current_portfolio": {
            "operating_data_centers": 11,
            "acquisition_lineage_counts": {"former_Redcentric": 8, "former_Colt_Technology_Services": 2, "former_Imagination_Technologies": 1},
            "current_provider_secured_grid_capacity_mva": 39,
            "site_page_maximum_power_checksum_mva_excluding_Cambridge": sum(max_power),
            "published_total_area_checksum_sqm_excluding_Cambridge": sum(total_area),
            "published_fitted_colocation_area_checksum_sqm_excluding_Cambridge_and_Hemel": sum(colo_area),
            "boundary": "The 39-MVA secured-grid headline and 68.5-MVA sum of ten site-page maximum values have different definitions. Dual feeds, site maxima, UPS, generator and cooling ratings are not added or normalized into current IT load.",
        },
        "former_Redcentric_transaction_scope": {
            "facilities": 8,
            "customers_approximately": 450,
            "pre_sale_racks_more_than": 4000,
            "pre_sale_electrical_feed_build_capacity_mw": 41.3,
            "completion_date": "2026-04-30",
            "completion_announced": "2026-05-01",
            "estimated_completion_settlement_GBP_million": 122.85,
            "share_consideration_GBP_million": 83.74,
            "intercompany_debt_settlement_GBP_million": 39.11,
            "forecast_enterprise_value_GBP_million": 122.3,
            "initial_cash_received_GBP_million": 115.4,
            "retained_pending_adjustments_GBP_million": 7.45,
            "planned_debt_repayment_GBP_million_approximately": 21,
            "transaction_costs_GBP_million_approximately": 5,
            "initial_net_cash_inflow_GBP_million_approximately": 90,
            "boundary": "The 41.3-MW, 4,000-plus-rack and customer values are the former eight-site Redcentric transaction perimeter, not Stellanor's current eleven-site operating or utilized totals. Transaction consideration is not Stellanor equity value or market capitalization.",
        },
        "historical_former_owner_financial_proxy": {
            "reporting_entity_and_scope": "Redcentric_plc_discontinued_data_center_operations",
            "period": "FY_ended_2025_03_31",
            "unit": "GBP_thousand",
            "audited_values": {
                "revenue": 44571,
                "cost_of_sales": 18415,
                "gross_profit": 26156,
                "operating_expenditure": 23091,
                "adjusted_EBITDA": 16633,
                "property_plant_and_equipment_depreciation": 3617,
                "intangible_amortization": 832,
                "right_of_use_asset_depreciation": 8308,
                "exceptional_costs": 779,
                "share_based_payments": 32,
                "operating_profit": 3065,
                "finance_costs": 1461,
                "profit_before_tax": 1604,
                "tax": 809,
                "net_profit": 795,
            },
            "derived_percent": {"revenue_growth": -5.96, "gross_margin": 58.69, "adjusted_EBITDA_growth": 51.81, "adjusted_EBITDA_margin": 37.32, "operating_margin": 6.88, "net_margin": 1.78},
            "held_for_sale_assets_GBP_thousand": 82169,
            "held_for_sale_liabilities_GBP_thousand": 40320,
            "H1_FY2026_GBP_million": {"revenue": 21.5, "gross_profit": 13.1, "adjusted_EBITDA": 8.3},
            "official_transaction_multiple_after_property_lease_payments": "15.1x_adjusted_EBITDA",
            "boundary": "These are former-owner discontinued-operation or interim segment results before disposal, not current Stellanor standalone revenue, profit, cash flow, debt or valuation.",
        },
        "current_operator_financial_boundary": {
            "backing": "fund_managed_by_DWS_Group",
            "UK_company": "Stellanor_Datacenters_UK_Limited_16344352_SIC_64209_holding_company",
            "group_company": "Stellanor_Datacenters_Group_Limited_16534947",
            "group_PSC": "Stellanor_Datacenters_Group_Holdings_Limited_more_than_75_percent",
            "first_accounts_period_end": "2025-12-31",
            "first_accounts_due": "2026-09-30",
            "standalone_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_and_ROIC": "undisclosed_as_of_evidence_snapshot",
            "boundary": "A fund managed by DWS is the disclosed backing relationship; it is not rewritten as direct DWS Group corporate ownership. Stellanor Datacenters UK Limited reports holding-company SIC 64209, so the reviewed record does not prove which legal entity contains each site's operations. Newly incorporated UK entities had no first accounts available at the evidence date.",
        },
        "accelerator_and_AI_boundary": {
            "operator_owned_or_customer_GPU_model_count_site_delivery_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "London_West_supported_rack_density_kw_up_to": 100,
            "West_Yorkshire_supported_rack_density_kw_up_to": 30,
            "Hemel_customer_workload": "Imagination_GPU_and_AI_chip_design",
            "liquid_cooling_options": ["Gatwick_RDHx_and_immersion", "Hemel_liquid_cooling", "London_West_high_density_cooling"],
            "accelerator_ledger_action": "no_numeric_row_created",
            "boundary": "High-density or liquid-cooling support and a customer's GPU-oriented workload establish hosting capability, not an installed GPU model or count owned by Stellanor or its customers.",
        },
        "sustainability_boundary": {
            "provider_claim_renewable_or_green_energy_share_percent": 100,
            "provider_target_CO2_neutral_year": 2030,
            "green_hydrogen_emergency_power_claim": "provider_says_used_and_aims_to_expand_but_exact_current_site_count_and_capacity_undisclosed",
            "site_page_backup_fuel": "diesel",
            "current_measured_portfolio_PUE_WUE_absolute_water_hourly_energy_matching_and_waste_heat_delivery": "undisclosed",
            "boundary": "Portfolio-level marketing claims do not establish hourly matching, site-specific emissions or replacement of the diesel generators listed on current facility pages.",
        },
        "OSM_crosswalk": {
            "current_portfolio_sites": 11,
            "related_legacy_Redcentric_operator_objects": len(osm_rows),
            "current_sites_without_reviewed_OSM_operator_crosswalk": 5,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "All six mapped objects still say Redcentric, but the eight-site disposal completed and the current portfolio is Stellanor. OSM is neither a complete site census nor current corporate ownership evidence.",
        },
        "sources": [
            HOME, DIRECTORY, REDCENTRIC_LEGACY, REDCENTRIC_ACQUISITION, COLT_TS_ACQUISITION,
            IMAGINATION_ACQUISITION, SUSTAINABILITY, REDCENTRIC_FY25,
            REDCENTRIC_FY25_PRESENTATION, REDCENTRIC_H1_FY26, DISPOSAL_ANNOUNCEMENT,
            DISPOSAL_COMPLETION, STELLANOR_UK_COMPANY, STELLANOR_GROUP_COMPANY,
            STELLANOR_GROUP_PSC, *[url for row in records for url in row["source_urls"]],
        ],
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
    registry = args.output_dir / "stellanor_official_facility_registry.jsonl"
    summary_path = args.output_dir / "stellanor_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
