#!/usr/bin/env python3
"""Build a scope-safe Compass Datacenters market and OSM registry.

Compass publishes current campus markets, development-scale MW, and a separate
"where we have built" section for assets now independently owned and operated.
This builder keeps those lifecycles separate and corrects the raw True North Data
Solutions OSM label at the Thunderball Drive campus using Virginia permits that
identify Compass Datacenters, LLC as the permitted operator.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


MARKETS = "https://www.compassdatacenters.com/data-center-markets/"
HYPERSCALE_DESIGN = "https://www.compassdatacenters.com/design/hyperscale/"
CLOUD_DESIGN = "https://www.compassdatacenters.com/design/cloud/"
CAPABILITIES = "https://www.compassdatacenters.com/capabilities/"
PARTNERS = "https://www.compassdatacenters.com/about/our-partners/"
NORTHERN_VIRGINIA = "https://www.compassdatacenters.com/why-northern-virginia/"
LOUDOUN_2019 = "https://www.compassdatacenters.com/news/compass-datacenters-begins-construction-on-75mw-data-center-campus-in-northern-virginia/"
LOUDOUN_DEQ = "https://www.deq.virginia.gov/home/showpublisheddocument/25859/638628780385130000"
LOUDOUN_COUNTY = "https://www.loudoun.gov/DocumentCenter/View/151069/Issued-Building-Permit-Report-April-1-30-2019?bidId="
RED_OAK = "https://www.compassdatacenters.com/news/compass-datacenters-adds-second-dallas-area-campus/"
PHOENIX = "https://www.compassdatacenters.com/leadership-thoughts/building-for-whats-next-phoenix-data-centers/"
MILAN = "https://www.compassdatacenters.com/news/milan/"
ROOT_ACQUISITION = "https://www.compassdatacenters.com/news/compass-datacenters-acquires-root-data-center-expanding-focus-on-hyperscale-market/"
VERTIV_COOLING = "https://www.compassdatacenters.com/future-ready-cooling-for-ai/"
VERTIV_CASE = "https://www.compassdatacenters.com/wp-content/uploads/2025/05/Case-Study_Vertiv-CoolPhase-Flex.pdf"
SIEMENS = "https://press.siemens.com/global/en/pressrelease/siemens-and-compass-datacenters-sign-multi-year-custom-electrical-solution-agreement"
SCHNEIDER = "https://www.compassdatacenters.com/news/compass-and-schneider-electric-utilize-ai-to-transform-data-center-maintenance/"
OUTCOMES_2025 = "https://www.compassdatacenters.com/wp-content/uploads/2025/10/Compass_Datacenters_Outcomes_Report_10-10-25-compressed-1.pdf"
ACQUISITION = "https://www.compassdatacenters.com/news/brookfield-infrastructure-and-ontario-teachers-to-acquire-compass-datacenters-from-redbird-capital-partners-and-azrieli-group/"
BIP_Q2_2023 = "https://bip.brookfield.com/bip/reports-filings/letters-unitholders/bip-q2-2023-letter-unitholders"
BAM_Q2_2023 = "https://bam.brookfield.com/sites/brookfield-bam-v2/files/brookfield-bam-v2/events-news/2023/2023-q2-bam-earnings-transcript.pdf"
BIP_2025_20F = "https://www.sec.gov/Archives/edgar/data/1406234/000140623426000002/bip-20251231.htm"
BIP_Q4_2025 = "https://bip.brookfield.com/bip/reports-filings/letters-unitholders/bip-q4-2025-letter-unitholders"
KKR_2026 = "https://www.compassdatacenters.com/in-the-news/kkr-permanent-capital-partnership/"


CURRENT_MARKETS = [
    {
        "id": "compass_current_chicago_hoffman_estates",
        "market": "Chicago / Hoffman Estates",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 200,
        "capacity_term": "campus",
        "lifecycle": "current_market_development_campus",
        "evidence": "Current market page describes a 200 MW campus 30 miles west of Chicago; Siemens' first custom skid deployment was projected for the second half of 2025.",
        "sources": [MARKETS, SIEMENS],
    },
    {
        "id": "compass_current_meridian_mississippi",
        "market": "Meridian, Mississippi",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 320,
        "capacity_term": "site",
        "lifecycle": "current_market_development_broke_ground_or_planned_from_2025",
        "evidence": "Current market page states the 320 MW site was breaking ground in 2025.",
        "sources": [MARKETS],
    },
    {
        "id": "compass_current_red_oak",
        "market": "Dallas-Fort Worth / Red Oak",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 360,
        "capacity_term": "development",
        "lifecycle": "current_market_mixed_operating_and_nearing_completion",
        "evidence": "Current market page calls the 360 MW Red Oak development nearing completion; the 2020 announcement used 350+ MW and a first 6 MW building.",
        "sources": [MARKETS, RED_OAK],
    },
    {
        "id": "compass_current_northern_virginia",
        "market": "Northern Virginia / Loudoun County / Leesburg",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 79,
        "capacity_term": "current_site",
        "lifecycle": "current_operating_campus_plus_separately_planned_regional_campuses",
        "evidence": "Current Compass page gives 79 MW at Loudoun. The 2019 first phase was 6 MW within a then-75 MW and 500,000-square-foot campus plan.",
        "sources": [MARKETS, NORTHERN_VIRGINIA, LOUDOUN_2019, LOUDOUN_DEQ, LOUDOUN_COUNTY],
    },
    {
        "id": "compass_current_goodyear",
        "market": "Phoenix / Goodyear",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 212,
        "capacity_term": "campus",
        "lifecycle": "current_market_mixed_operating_and_development",
        "evidence": "Current market page describes a 212 MW Goodyear campus; an earlier engineering page cited 240 MW of substation capacity for the 190-acre campus.",
        "sources": [MARKETS, PHOENIX],
    },
    {
        "id": "compass_current_el_mirage",
        "market": "Phoenix / El Mirage",
        "country": "United States",
        "country_code": "US",
        "published_capacity_mw": 108,
        "capacity_term": "campus",
        "lifecycle": "current_market_development",
        "evidence": "Current market page describes a 108 MW El Mirage campus.",
        "sources": [MARKETS],
    },
    {
        "id": "compass_current_toronto",
        "market": "Greater Toronto Area",
        "country": "Canada",
        "country_code": "CA",
        "published_capacity_mw": None,
        "capacity_term": "undisclosed",
        "lifecycle": "current_marketed_hyperscale_campus",
        "evidence": "Current market page names a Greater Toronto Area hyperscale campus but does not publish its MW or exact street address.",
        "sources": [MARKETS],
    },
    {
        "id": "compass_current_milan_noviglio",
        "market": "Milan / Noviglio",
        "country": "Italy",
        "country_code": "IT",
        "published_capacity_mw": 48,
        "capacity_term": "IT_load_minimum_plan",
        "lifecycle": "current_market_development_with_exact_current_delivery_state_not_reconciled",
        "evidence": "The 2022 Hines joint-venture announcement targeted more than 48 MW of IT load on a 2.3-million-square-foot site; current market page retains Milan without a refreshed MW or delivery schedule.",
        "sources": [MARKETS, MILAN],
    },
]

BUILT_OR_TRANSITION_MARKETS = [
    ("compass_built_boston", "Boston", "United States", "US", "customer_owned_data_center_delivered_by_Compass"),
    ("compass_built_columbus", "Columbus", "United States", "US", "two_customer_owned_data_centers_delivered_by_Compass"),
    ("compass_built_minneapolis_shakopee", "Minneapolis / Shakopee", "United States", "US", "historical_Compass_development_now_independently_owned_and_operated"),
    ("compass_built_montreal", "Montréal", "Canada", "CA", "two_historical_campus_locations_with_current_page_operator_wording_conflict"),
    ("compass_built_nashville_franklin", "Nashville / Franklin", "United States", "US", "historical_14_acre_campus_now_independently_owned_and_operated"),
    ("compass_built_raleigh", "Raleigh", "United States", "US", "historical_fully_leased_campus_now_independently_owned_and_operated"),
    ("compass_built_tel_aviv", "Tel Aviv", "Israel", "IL", "multiple_historical_data_centers_now_independently_owned_and_operated"),
    ("compass_built_tulsa", "Tulsa", "United States", "US", "historical_five_acre_campus_now_independently_owned_and_operated"),
]

RED_OAK_OSM = [f"osm_way_{number}" for number in range(1426525212, 1426525222)] + ["osm_way_850965775"]

OSM_CROSSWALK = {
    "osm_node_8712918739": ("compass_built_montreal", "Montreal_name_only_candidate_in_historical_or_transition_scope"),
    "osm_way_59244466": ("compass_current_toronto", "Compass_operator_candidate_in_Greater_Toronto_without_official_address_bridge"),
    **{osm_ref: ("compass_current_red_oak", "Red_Oak_building_or_campus_component_grouped_under_one_360MW_mixed_lifecycle_development") for osm_ref in RED_OAK_OSM},
    "osm_way_723116259": ("compass_current_goodyear", "named_Goodyear_campus_boundary_candidate"),
    "osm_way_1529510642": ("compass_current_el_mirage", "Phoenix_II_construction_geometry_is_a_geographic_candidate_for_El_Mirage_without_official_address_bridge"),
    "osm_way_1292897243": ("compass_current_northern_virginia", "Thunderball_address_matches_Virginia_DEQ_Compass_permit_raw_True_North_operator_is_not_used"),
    "osm_way_1292897242": ("compass_current_northern_virginia", "Thunderball_address_matches_Virginia_DEQ_Compass_permit_raw_True_North_operator_is_not_used"),
    "osm_way_909455922": ("compass_current_northern_virginia", "Thunderball_address_matches_Virginia_DEQ_Compass_permit_raw_True_North_operator_is_not_used"),
    "osm_way_1292897241": ("compass_current_northern_virginia", "Thunderball_address_matches_Virginia_DEQ_Compass_permit_raw_True_North_operator_is_not_used"),
    "osm_way_1387391201": ("compass_current_northern_virginia", "TikTok_name_and_True_North_operator_are_unverified_tenant_and_operator_claims_inside_the_Compass_campus_candidate"),
    "osm_way_1387391200": ("compass_current_northern_virginia", "OSM_campus_envelope_grouped_with_buildings_and_not_counted_as_an_extra_facility"),
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = []
    for source in CURRENT_MARKETS:
        rows.append({
            **{key: value for key, value in source.items() if key != "sources"},
            "object_type": "DataCenterMarketOrCampusEvidence",
            "operator_or_developer": "Compass Datacenters",
            "record_scope": "current_marketed_market_or_campus_not_a_proven_single_building",
            "published_capacity_boundary": "Published MW is design, development, current-site or IT-load wording as retained in capacity_term and lifecycle; it is not automatically operating, energized, leased, utilized or billed load.",
            "physical_GPU_inventory": "No Compass-owned or customer-owned installed GPU count is disclosed for this row.",
            "source_urls": source["sources"],
            "accessed_on": accessed_on,
        })
    for row_id, market, country, country_code, lifecycle in BUILT_OR_TRANSITION_MARKETS:
        rows.append({
            "id": row_id,
            "object_type": "HistoricalDataCenterDevelopmentMarketEvidence",
            "operator_or_developer": "Compass Datacenters",
            "market": market,
            "country": country,
            "country_code": country_code,
            "published_capacity_mw": None,
            "capacity_term": "undisclosed_on_current_market_page",
            "lifecycle": lifecycle,
            "record_scope": "where_Compass_has_built_not_current_Compass_owned_or_operated_fleet",
            "published_capacity_boundary": "The current page places this market under projects now independently owned and operated. It is excluded from current Compass capacity; Montreal's local sentence saying Compass operates two campuses is retained as a publication conflict.",
            "physical_GPU_inventory": "No installed GPU count or current hardware owner is disclosed for this historical row.",
            "source_urls": [MARKETS] + ([ROOT_ACQUISITION] if market == "Montréal" else []),
            "accessed_on": accessed_on,
        })
    assert len(CURRENT_MARKETS) == 8
    assert len(BUILT_OR_TRANSITION_MARKETS) == 8
    assert len(rows) == 16
    assert sum(row["published_capacity_mw"] or 0 for row in rows) == 1327
    return [{"source_order": position, **row} for position, row in enumerate(rows, 1)]


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (registry_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "registry_ref": registry_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "counting_rule": "OSM geometry is a partial crosswalk. Campus envelopes and buildings are grouped, and no row adds MW, GPUs or a separate facility count.",
        })
    assert len(rows) == 21
    assert Counter(row["raw_operator"] for row in rows) == {None: 14, "True North Data Solutions": 6, "Compass": 1}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "compass_datacenters_market_summary_2026_07_19",
        "operator": "Compass Datacenters, LLC",
        "accessed_on": accessed_on,
        "current_market_reconciliation": {
            "current_market_or_campus_rows": 8,
            "where_we_have_built_transition_rows": 8,
            "registry_rows": len(records),
            "numeric_current_row_checksum_mw": 1327,
            "numeric_checksum_boundary": "The 1,327 MW sum mixes current-site, campus, development and IT-load-plan wording. It excludes unknown Toronto and transition rows and is not operating, energized, leased, utilized or billed capacity.",
            "North_America_marketing_headline": "more_than_2GW_of_capacity",
            "headline_boundary": "The broader North America headline is not reconciled to the 1,327 MW row checksum and may include undisclosed or future campuses. No residual MW is allocated.",
            "transition_boundary": "The current page says the eight where-we-have-built markets are now independently owned and operated; they are excluded from the current Compass fleet.",
            "publication_conflict": "The same transition section says assets are independently owned and operated while the Montreal sentence says Compass operates two campus locations. Current ownership and operator are left unresolved pending a property-level source.",
        },
        "dated_2023_investor_scope": {
            "operating_capacity_mw": 170,
            "operating_contracted_and_reserved_capacity_mw": 735,
            "contracted_capacity_mw": 675,
            "investment_grade_hyperscaler_support_percent": 85,
            "weighted_average_contract_duration_years": 13,
            "triple_net_share_of_contracted_capacity_percent_approx": 60,
            "boundary": "Brookfield's Q2 2023 acquisition snapshot is dated and cannot be substituted for current Compass operating or contracted capacity.",
        },
        "power_and_electrical": {
            "hyperscale_design_ceiling_mw": 360,
            "hyperscale_substation_claim": "450_MDA_as_published_typographical_or_unit_anomaly_not_silently_changed_to_MVA",
            "cloud_design_package_mw_range": [6, 80],
            "Siemens_capacity_agreement": {
                "maximum_units_over_five_years": 1500,
                "unit": "modular_medium_voltage_skid",
                "components": ["Siemens_8DJH_36_gas_insulated_arc_resistant_medium_voltage_switchgear", "transformers"],
                "first_deployment_plan": "Chicago_second_half_2025",
                "boundary": "Maximum contracted delivery capacity is not delivered, accepted, installed or operating equipment count by site.",
            },
            "backup_generation": "Cummins manufacture and maintenance relationship; HVO biodiesel use is supported, but site-level generator model, count, rating, fuel runtime and acceptance are undisclosed.",
            "Schneider_EcoCare": "Factory-integrated sensors and gateways, 24x7 Connected Service Hub and condition-based maintenance; published 40% lower onsite interventions and 20% OPEX reduction are program results, not Compass accounting operating margin.",
            "complete_per_site_as_built_BOM": "undisclosed",
        },
        "cooling_and_water": {
            "legacy_or_general_design": "Vertiv free-air-based equipment and water-free operational design",
            "AI_hybrid_solution": "Vertiv CoolPhase Flex combines air and liquid cooling in one refrigerant-based modular heat-rejection unit and can support direct-to-chip liquid cooling.",
            "white_space": "Schneider EcoStruxure Pod can integrate hot-aisle containment, InRow or rear-door heat exchangers, high-power busway and a technical-water loop.",
            "site_level_live_liquid_cooled_mw_rack_density_PUE_WUE_and_absolute_water": "undisclosed",
            "boundary": "Design capability and partner product availability do not prove deployment, site allocation, live liquid-cooled MW or customer acceptance.",
        },
        "GPU_and_AI_boundary": {
            "hyperscale_design": "marketed_as_high_density_GPU_and_AI_ready",
            "installed_Compass_owned_GPU_count": "not_disclosed_or_established",
            "installed_customer_GPU_model_count_owner_site_and_delivery_state": "not_disclosed",
            "TikTok_OSM_name": "unverified_tenant_label_not_used_as_customer_contract_or_GPU_evidence",
            "boundary": "Compass builds and operates facilities for hyperscale and cloud customers; readiness, customer class and a map label are not physical accelerator inventory.",
        },
        "ownership_finance_and_transaction_boundary": {
            "2023_acquirers": ["Brookfield_Infrastructure", "Ontario_Teachers_Pension_Plan"],
            "2023_Brookfield_co_control_stake_purchase_USD_billion": 1.35,
            "2023_Brookfield_equity_share_USD_million_approx": 375,
            "2023_transaction_enterprise_value_USD_billion_approx": 5.0,
            "standalone_Compass_revenue_operating_profit_cash_flow_capex_debt_and_current_valuation": "undisclosed",
            "2025_Brookfield_data_storage_adjusted_EBITDA_USD_million": 324,
            "2025_Brookfield_data_storage_FFO_USD_million": 184,
            "2025_Brookfield_hyperscale_capacity_commissioned_mw": 220,
            "Brookfield_boundary": "Data-storage results and commissioned MW aggregate Compass, Data4 and other Brookfield platforms at Brookfield's reporting boundary; none is Compass-only revenue, operating profit, cash flow or delivered MW.",
            "2026_KKR_partnership": "Definitive permanent-capital agreement announced March 16, 2026; investment amount, ownership percentage, exact operating/future asset perimeter, consideration and closing status are undisclosed in the reviewed Compass release.",
        },
        "True_North_and_OSM_identity_resolution": {
            "all_related_OSM_objects": len(osm_rows),
            "raw_operator_counts": {str(key): value for key, value in sorted(Counter(row["raw_operator"] for row in osm_rows).items(), key=lambda item: str(item[0]))},
            "Thunderball_objects_with_raw_True_North_operator": 6,
            "Thunderball_addresses_in_Virginia_DEQ_Compass_permit": 4,
            "resolution": "Virginia DEQ and Loudoun permit evidence identifies Compass Datacenters, LLC for the Thunderball Drive facility. The raw True North Data Solutions label is preserved but not used as current operator evidence.",
            "TikTok_and_fifth_building_boundary": "The reviewed permit explicitly covers four addresses. The separate TikTok-named footprint and campus envelope remain group-level Compass campus candidates without primary tenant or building-operator proof.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "outlook": {
            "positive_signals": [
                "current_more_than_2GW_North_America_marketing_headline_and_multiple_large_campus_programs",
                "2023_long_duration_hyperscaler_contract_and_reserved_capacity_snapshot",
                "Brookfield_Ontario_Teachers_and_KKR_long_term_capital_support",
                "standardized_prefabricated_supply_chain_and_equipment_capacity_agreements",
                "hybrid_air_liquid_cooling_and_AI_ready_white_space",
            ],
            "risk_signals": [
                "current_operating_contracted_reserved_and_pipeline_MW_not_reconciled",
                "large_current_market_checksum_is_mixed_lifecycle_and_not_live_load",
                "private_standalone_financials_debt_capex_customer_concentration_and_returns_undisclosed",
                "transition_market_ownership_wording_conflict_and_KKR_asset_perimeter_undisclosed",
                "grid_permit_supply_chain_customer_acceptance_and_construction_execution_for_large_pipeline",
                "no_installed_GPU_inventory_or_site_level_economics",
            ],
            "analytical_view": "Compass is a high-quality private hyperscale developer with unusually useful contract and engineering evidence, but the strongest capacity snapshot is dated 2023 and the live market page mixes current, development and transferred scopes. Public investors gain only indirect, blended exposure through Brookfield Infrastructure, Brookfield Asset Management or KKR; site delivery, current standalone economics and the KKR perimeter remain the key missing facts.",
        },
        "remaining_material_gaps": [
            "exact_current_non_overlapping_campus_building_address_title_lease_operator_and_lifecycle_roster",
            "current_operating_energized_contracted_reserved_customer_accepted_leased_utilized_billed_and_actual_IT_load_by_site",
            "current_more_than_2GW_headline_to_market_row_and_building_reconciliation",
            "transition_market_property_by_property_owner_operator_and_transaction_bridge",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life",
            "per_site_live_liquid_cooled_MW_rack_density_measured_PUE_WUE_energy_water_and_emissions",
            "GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_and_margin",
            "standalone_revenue_operating_profit_cash_flow_capex_debt_ROIC_customer_concentration_and_contract_pricing",
            "KKR_permanent_capital_amount_ownership_asset_perimeter_consideration_closing_and_current_valuation",
        ],
        "sources": [
            MARKETS, HYPERSCALE_DESIGN, CLOUD_DESIGN, CAPABILITIES, PARTNERS, NORTHERN_VIRGINIA,
            LOUDOUN_2019, LOUDOUN_DEQ, LOUDOUN_COUNTY, RED_OAK, PHOENIX, MILAN, ROOT_ACQUISITION,
            VERTIV_COOLING, VERTIV_CASE, SIEMENS, SCHNEIDER, OUTCOMES_2025, ACQUISITION,
            BIP_Q2_2023, BAM_Q2_2023, BIP_2025_20F, BIP_Q4_2025, KKR_2026,
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
    registry = args.output_dir / "compass_datacenters_market_registry.jsonl"
    summary_path = args.output_dir / "compass_datacenters_market_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
