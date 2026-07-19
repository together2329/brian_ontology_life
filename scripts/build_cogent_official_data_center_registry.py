#!/usr/bin/env python3
"""Build a scope-safe Cogent data-center evidence registry.

Cogent publishes a current classic-data-center total, a separate edge total,
market labels that do not expose every building, and a FY2025 statutory count
that is larger than the current marketing total.  This builder preserves those
denominators instead of inventing one row per hidden building or treating
carrier-neutral service locations as Cogent-owned facilities.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


DIRECTORY = "https://www.cogentco.com/en/network/cogent-data-centers"
NORTH_AMERICA = "https://www.cogentco.com/en/network/cogent-data-centers/169-cdc-locations/1156-na-data-centers"
EUROPE = "https://cogentco.com/en/network/cogent-data-centers/169-cdc-locations/1165-eu-data-centers"
FRANCE_LOCATOR = "https://www.cogentco.com/en/?action=search&country=France&id=40&option=com_content&site_type=CDC&view=article"
FRANCE_PAGE = "https://www2.cogentco.com/en/cogent-france"
COLOCATION = "https://cogentco.com/en/products-and-services/colocation/cogent-data-centers"
COLOCATION_BROCHURE = "https://www.cogentco.com/files/docs/network/colocation/brochure_colocation.pdf"
UTILITY_COMPUTING = "https://www.cogentco.com/en/products-and-services/colocation/utility-computing"
UTILITY_BROCHURE = "https://www.cogentco.com/files/docs/network/colocation/brochure_utility_computing.pdf"
SEC_2025_10K = "https://www.sec.gov/Archives/edgar/data/1158324/000110465926017968/ccoi-20251231x10k.htm"


NORTH_AMERICAN_MARKETS = [
    ("Northeast", "Akron", "OH", "US", False),
    ("Northeast", "Albany", "NY", "US", False),
    ("Northeast", "Boston", "MA", "US", True),
    ("Northeast", "Buffalo", "NY", "US", False),
    ("Northeast", "Cleveland", "OH", "US", False),
    ("Northeast", "Columbus", "OH", "US", False),
    ("Northeast", "Franklin", "NJ", "US", False),
    ("Northeast", "Hackensack", "NJ", "US", True),
    ("Northeast", "Mississauga", "ON", "CA", False),
    ("Northeast", "New York", "NY", "US", True),
    ("Northeast", "Pennsauken", "NJ", "US", False),
    ("Northeast", "Pittsburgh", "PA", "US", False),
    ("Northeast", "Richmond", "VA", "US", False),
    ("Northeast", "Sparta", "NJ", "US", False),
    ("Northeast", "Springfield", "MA", "US", False),
    ("Northeast", "Syracuse", "NY", "US", False),
    ("Northeast", "Toronto", "ON", "CA", True),
    ("Northeast", "Vienna", "VA", "US", False),
    ("Northeast", "Washington", "DC", "US", True),
    ("Northeast", "Worcester", "MA", "US", False),
    ("Southeast", "Atlanta", "GA", "US", True),
    ("Southeast", "Boca Raton", "FL", "US", True),
    ("Southeast", "Charlotte", "NC", "US", True),
    ("Southeast", "Fairfax", "SC", "US", False),
    ("Southeast", "Hollywood", "FL", "US", False),
    ("Southeast", "Miami", "FL", "US", False),
    ("Southeast", "New Orleans", "LA", "US", True),
    ("Southeast", "Orlando", "FL", "US", False),
    ("Southeast", "Raleigh", "NC", "US", False),
    ("Southeast", "Tampa", "FL", "US", False),
    ("Midwest", "Austin", "TX", "US", False),
    ("Midwest", "Chicago", "IL", "US", True),
    ("Midwest", "Dallas", "TX", "US", False),
    ("Midwest", "Detroit", "MI", "US", False),
    ("Midwest", "El Paso", "TX", "US", False),
    ("Midwest", "Fort Worth", "TX", "US", False),
    ("Midwest", "Houston", "TX", "US", False),
    ("Midwest", "Indianapolis", "IN", "US", False),
    ("Midwest", "Irving", "TX", "US", True),
    ("Midwest", "Louisville", "KY", "US", False),
    ("Midwest", "Milwaukee", "WI", "US", False),
    ("Midwest", "Minneapolis", "MN", "US", True),
    ("Midwest", "Oklahoma City", "OK", "US", False),
    ("Midwest", "Omaha", "NE", "US", False),
    ("Midwest", "St. Louis", "MO", "US", False),
    ("West", "Anaheim", "CA", "US", False),
    ("West", "Billings", "MT", "US", False),
    ("West", "Cheyenne", "WY", "US", False),
    ("West", "Denver", "CO", "US", False),
    ("West", "La Mirada", "CA", "US", False),
    ("West", "Livermore", "CA", "US", False),
    ("West", "Los Angeles", "CA", "US", False),
    ("West", "Oroville", "CA", "US", False),
    ("West", "Palm Springs", "CA", "US", False),
    ("West", "Pasadena", "CA", "US", True),
    ("West", "Phoenix", "AZ", "US", True),
    ("West", "Portland", "OR", "US", False),
    ("West", "Rialto", "CA", "US", False),
    ("West", "San Diego", "CA", "US", False),
    ("West", "San Jose", "CA", "US", False),
    ("West", "Spokane", "WA", "US", False),
    ("West", "Tacoma", "WA", "US", True),
]


EUROPEAN_FACILITIES = [
    ("fr_antibes", "Antibes / Sophia-Antipolis", "FR", "PÔLE ENTREPRISES EURO 95 165 ROUTE DES CISTES BÂ, 06600 Antibes, France", False),
    ("fr_bordeaux", "Bordeaux", "FR", "BÂT G2 - BASSIN À FLOTS, 33300 Bordeaux, France", False),
    ("fr_dijon", "Dijon", "FR", "41 QUAI GAUTHEY, 21000 Dijon, France", False),
    ("fr_grenoble", "Grenoble", "FR", "33 RUE JOSEPH CHANRION, 38000 Grenoble, France", False),
    ("fr_paris_la_garenne", "Paris / La Garenne-Colombes", "FR", "77 BOULEVARD DE LA RÉPUBLIQUE, 92250 La Garenne-Colombes, France", None),
    ("fr_lille", "Lille", "FR", "72 RUE JENNER, 59000 Lille, France", False),
    ("fr_montpellier", "Montpellier", "FR", "189 PL DU 56E RGMT D ARTILLERIE, 34000 Montpellier, France", False),
    ("fr_nantes", "Nantes", "FR", "32 BOULEVARD VICTOR HUGO, 44000 Nantes, France", False),
    ("fr_nice", "Nice", "FR", "16 AVENUE THIERS, 06000 Nice, France", False),
    ("fr_poitiers", "Poitiers", "FR", "18/22 RUE JEANNE DARC, 86000 Poitiers, France", False),
    ("fr_rennes", "Rennes", "FR", "AV CHARDONNET - LORANS 30F, 35000 Rennes, France", False),
    ("fr_rouen", "Rouen", "FR", "20 RUE ALEXANDRE BARRABÉ, 76100 Rouen, France", False),
    ("fr_strasbourg", "Strasbourg / Schiltigheim", "FR", "46 ROUTE DE BISCHWILLER, 67300 Schiltigheim, France", False),
    ("fr_toulouse", "Toulouse", "FR", "125 BIS CH DU SANG DE SERP, 31000 Toulouse, France", False),
    ("fr_tours", "Tours", "FR", "171 RUE DES DOUETS, 37100 Tours, France", False),
    ("fr_paris_velizy", "Paris / Vélizy-Villacoublay", "FR", "16 RUE GRANGE DAME ROSE, 78140 Vélizy-Villacoublay, France", None),
    ("de_frankfurt", "Frankfurt", "DE", "Exact current street address not established in reviewed official directory", True),
    ("nl_halfweg", "Halfweg", "NL", "Exact current street address not established in reviewed official directory", True),
    ("es_madrid", "Madrid", "ES", "Exact current street address not established in reviewed official directory", True),
]


OSM_CROSSWALK = {
    "osm_node_4975162489": ("cogent_fr_rennes", "city_and_operator_candidate_without_building_geometry"),
    "osm_way_126029978": ("cogent_fr_dijon", "named_building_footprint_candidate"),
    "osm_way_84942310": ("cogent_fr_lille", "named_building_footprint_candidate"),
    "osm_way_75759038": ("cogent_fr_montpellier", "named_building_footprint_candidate"),
    "osm_way_65043676": ("cogent_fr_rouen", "named_building_footprint_candidate"),
    "osm_way_76296417": ("cogent_fr_toulouse", "named_building_footprint_candidate"),
    "osm_way_843118512": ("cogent_fr_tours", "named_building_footprint_candidate"),
    "osm_way_43013791": ("cogent_fr_strasbourg", "geographic_candidate_not_exact_name_or_address_match"),
    "osm_node_7522025783": ("cogent_fr_grenoble", "named_point_candidate"),
    "osm_way_290307022": ("cogent_na_phoenix_az", "market_candidate_without_official_street_address_bridge"),
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows: list[dict] = []
    for region, city, subdivision, country, utility in NORTH_AMERICAN_MARKETS:
        rows.append({
            "id": f"cogent_na_{slug(city)}_{subdivision.lower()}",
            "object_type": "DataCenterMarketEvidence",
            "operator": "Cogent Communications",
            "geography": "North America",
            "subregion": region,
            "country_code": country,
            "market_or_city": city,
            "administrative_subdivision": subdivision,
            "address_as_published": "Current directory publishes a city label; exact building address and multiplicity are not exposed on the reviewed page.",
            "record_granularity": "market_label_not_a_proven_single_building",
            "lifecycle_as_of_2026_07_19": "currently_marketed_classic_data_center_market",
            "utility_computing_marker": utility,
            "published_capacity": {},
            "power_and_cooling_evidence": "Portfolio-level features only; no site-specific equipment schedule is attributed to this market row.",
            "physical_GPU_or_accelerator_inventory": "No Cogent-owned GPU inventory is disclosed.",
            "source_urls": [DIRECTORY, NORTH_AMERICA, COLOCATION],
            "accessed_on": accessed_on,
        })
    for code, location, country, address, utility in EUROPEAN_FACILITIES:
        source_urls = [DIRECTORY, EUROPE]
        if country == "FR":
            source_urls.extend([FRANCE_LOCATOR, FRANCE_PAGE])
        rows.append({
            "id": f"cogent_{code}",
            "object_type": "DataCenterFacilityEvidence",
            "operator": "Cogent Communications",
            "geography": "Europe",
            "country_code": country,
            "market_or_city": location,
            "address_as_published": address,
            "record_granularity": "facility_address" if country == "FR" else "market_label_with_exact_address_undisclosed",
            "lifecycle_as_of_2026_07_19": "currently_marketed_classic_data_center",
            "utility_computing_marker": utility if utility is not None else "Paris_market_marked_but_exact_building_allocation_undisclosed",
            "published_capacity": {},
            "power_and_cooling_evidence": {
                "scope": "France portfolio-level" if country == "FR" else "portfolio-level",
                "space": "42U cabinets and private cages" if country == "FR" else "undisclosed_by_this_location_record",
                "power": "multiple options, UPS and backup generator" if country == "FR" else "undisclosed_by_this_location_record",
                "environment": "HVAC plus fire suppression and detection" if country == "FR" else "undisclosed_by_this_location_record",
                "security": "24x7x365 access control and camera surveillance" if country == "FR" else "undisclosed_by_this_location_record",
                "boundary": "General provider features are not a per-site as-built OEM, model, count, rating, loading or remaining-life ledger.",
            },
            "physical_GPU_or_accelerator_inventory": "No Cogent-owned GPU inventory is disclosed.",
            "source_urls": list(dict.fromkeys(source_urls)),
            "accessed_on": accessed_on,
        })
    assert len(NORTH_AMERICAN_MARKETS) == 62
    assert len(EUROPEAN_FACILITIES) == 19
    assert len(rows) == 81
    assert len({row["id"] for row in rows}) == 81
    assert Counter(row["country_code"] for row in rows)["FR"] == 16
    return [{"source_order": position, **row} for position, row in enumerate(rows, 1)]


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (profile_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "profile_ref": profile_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "counting_rule": "OSM geometry is a crosswalk only and contributes no additional facility or capacity count.",
        })
    assert len(rows) == 10
    assert Counter(row["raw_operator"] for row in rows) == {"Cogent": 8, "Cogent Communications, Inc.": 2}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sources = [
        DIRECTORY, NORTH_AMERICA, EUROPE, FRANCE_LOCATOR, FRANCE_PAGE,
        COLOCATION, COLOCATION_BROCHURE, UTILITY_COMPUTING, UTILITY_BROCHURE,
        SEC_2025_10K,
    ]
    return {
        "id": "cogent_official_data_center_summary_2026_07_19",
        "operator": "Cogent Communications Holdings, Inc.",
        "ticker": "NASDAQ_CCOI",
        "accessed_on": accessed_on,
        "current_marketing_scope": {
            "classic_data_centers": 87,
            "North_America_classic_data_centers": 68,
            "Europe_classic_data_centers": 19,
            "North_America_edge_data_centers": 86,
            "total_current_marketed_classic_plus_edge": 173,
            "visible_North_America_market_labels": 62,
            "North_America_buildings_not_individually_allocated_across_market_labels": 6,
            "visible_Europe_facility_records": 19,
            "registry_records": len(records),
            "registry_boundary": "The registry has 62 North American market labels and 19 European facility records. It does not invent six hidden North American building rows or 86 edge-site rows without a complete current address roster.",
        },
        "FY2025_statutory_scope_at_2025_12_31": {
            "total_Cogent_data_center_buildings": 187,
            "classic_data_centers": 100,
            "edge_data_centers": 87,
            "floor_space_million_sqft": 2.1,
            "available_or_published_power_mw": 213,
            "edge_floor_space_thousand_sqft": 174,
            "edge_available_power_mw": 31,
            "legacy_Cogent_portfolio_after_seven_reductions": 48,
            "major_Sprint_data_centers_added": 52,
            "smaller_edge_data_centers_added": 87,
            "boundary": "The 213MW term is not disclosed as live IT load, utilized draw, leased load or customer-accepted capacity. The 187-building year-end scope is dated and not silently substituted for the current 173-site marketing scope.",
        },
        "current_to_FY2025_reconciliation": {
            "FY2025_total_buildings": 187,
            "current_marketed_classic_plus_edge": 173,
            "net_reduction": 14,
            "classic_reduction": 13,
            "edge_reduction": 1,
            "complete_site_by_site_sale_decommission_or_reclassification_bridge": "not_disclosed_in_reviewed_sources",
            "conflicting_current_publications": "The live directory and network pages show 87 classic facilities, while May 2026 brochures and search-index copies can still state 99. The live-page denominator is primary and the publication conflict is retained rather than averaged.",
        },
        "separate_network_service_scope": {
            "FY2025_carrier_neutral_data_centers": 1715,
            "FY2025_carrier_neutral_buildings": 1511,
            "current_marketing_carrier_neutral_data_centers_more_than": 1744,
            "boundary": "Carrier-neutral locations are Cogent-lit service locations, not Cogent-owned facilities, and are excluded from the 173/187 physical-portfolio counts.",
        },
        "power_cooling_and_conversion_evidence": {
            "current_general_features": [
                "redundant_power",
                "UPS",
                "backup_generators",
                "HVAC_or_air_conditioning",
                "fire_detection_and_suppression",
                "access_control_and_camera_surveillance",
                "temperature_and_humidity_control",
            ],
            "Cogent_Fiber_conversion_work": [
                "obsolete_equipment_and_rack_removal",
                "many_DC_to_AC_power_conversions",
                "HVAC_upgrade_or_installation",
                "UPS_upgrade_or_installation",
                "backup_generator_upgrade_or_installation",
                "fire_suppression_upgrade_or_installation",
                "structural_work",
            ],
            "per_site_complete_as_built_BOM": "undisclosed",
            "missing_fields": "grid feeds, substations, transformers, switchgear, PDUs, UPS/battery/generator/chiller/CRAH/CRAC/CDU OEMs, models, counts, ratings, loading, acceptance and remaining life",
        },
        "GPU_and_utility_computing_boundary": {
            "product": "Cogent Utility Computing",
            "scope": "managed servers plus Tier 1 IP at selected classic data centers",
            "published_server_attributes": ["CPU", "RAM", "disk_or_controller", "network_options", "Linux_or_bare_metal", "100Mbps_to_10Gbps"],
            "Cogent_owned_GPU_model_count_and_site_allocation": "not_disclosed_or_established",
            "server_model_count_delivery_state_utilization_and_economics": "undisclosed",
            "boundary": "Availability of a managed-server product is not evidence of an accelerator fleet or a current physical GPU inventory.",
        },
        "FY2025_audited_company_financials_USD_thousand": {
            "service_revenue": 975766,
            "FY2024_service_revenue": 1036104,
            "derived_revenue_growth_percent": -5.823,
            "network_operations_expense": 534962,
            "selling_general_and_administrative": 274436,
            "depreciation_and_amortization": 270181,
            "gain_on_lease_terminations_and_other": 2740,
            "total_operating_expenses": 1079579,
            "operating_loss": -101073,
            "derived_operating_margin_percent": -10.358,
            "FY2024_operating_loss": -197606,
            "interest_expense_including_swap_valuation": 161362,
            "loss_before_income_taxes": -244965,
            "income_tax_benefit": 62791,
            "net_loss": -182174,
            "derived_net_margin_percent": -18.670,
            "operating_cash_flow": -10579,
            "cash_purchases_of_property_and_equipment": 187600,
            "derived_operating_cash_flow_less_cash_PPandE": -198179,
            "ending_cash_and_restricted_cash": 205112,
            "cash_interest_paid": 154748,
            "property_and_equipment_net": 1721074,
            "boundary": "Companywide results cover connectivity, wavelength, colocation and non-core operations. Cogent does not disclose data-center-only revenue, operating profit, cash flow or capex.",
        },
        "FY2025_revenue_mix_percent": {
            "on_net": 54.5,
            "off_net": 40.7,
            "wavelength": 3.9,
            "non_core": 0.9,
            "data_center_only_split": "undisclosed",
        },
        "debt_and_asset_optionalities": {
            "note_principal_USD_million_derived": 1730.4,
            "components_USD_million": {"2032_notes": 600, "2027_mirror_notes": 300, "2027_notes": 450, "existing_IPv4_notes": 206, "new_IPv4_notes": 174.4},
            "facilities_actively_marketed_for_sale_or_lease_at_FY2025": 24,
            "terminated_nonbinding_LOI_for_two_facilities_USD_million": 144,
            "boundary": "The derived principal sum excludes lease liabilities and unamortized accounting adjustments and is not labeled the GAAP debt carrying value. A terminated LOI is not realized sale proceeds.",
        },
        "OSM_crosswalk": {
            "rows": osm_rows,
            "all_related_objects": len(osm_rows),
            "raw_operator_counts": dict(sorted(Counter(row["raw_operator"] for row in osm_rows).items())),
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "The ten OSM objects are partial geometry or city candidates. They neither prove a complete current portfolio nor add capacity.",
        },
        "outlook": {
            "positive_signals": [
                "scarce_owned_classic_and_edge_real_estate_power_and_network_interconnection",
                "213MW_and_2_1m_sqft_FY2025_physical_platform",
                "converted_Sprint_properties_create_colocation_sale_or_lease_optionality",
                "FY2025_operating_loss_improved_by_96_5m_year_over_year",
                "direct_optical_network_supports_connectivity_and_colocation_cross_sell",
            ],
            "risk_signals": [
                "FY2025_revenue_declined_5_8_percent",
                "operating_loss_net_loss_and_negative_operating_cash_flow",
                "derived_1_7304bn_note_principal_and_high_interest_burden",
                "current_site_count_is_14_below_FY2025_without_complete_bridge",
                "failed_two_facility_LOI_highlights_real_estate_execution_and_valuation_risk",
                "213MW_is_not_live_IT_load_or_utilization",
                "no_data_center_only_profit_occupancy_utilization_or_site_economics",
                "no_owned_GPU_inventory_or_complete_per_site_power_and_cooling_BOM",
            ],
            "analytical_view": "Cogent has a large, network-integrated real-estate and power platform, but the current portfolio is shrinking relative to FY2025 and the company remains loss-making with negative operating cash flow and a heavy interest burden. Treat property monetization and AI/colocation upside as optionality, not proven earnings, until Cogent publishes a site bridge, utilization, signed demand, data-center-only economics and delivery evidence.",
        },
        "remaining_material_gaps": [
            "exact_current_87_classic_and_86_edge_non_overlapping_building_address_title_lease_and_lifecycle_roster",
            "187_FY2025_to_173_current_site_by_site_sale_decommission_reclassification_and_date_bridge",
            "six_North_American_buildings_hidden_inside_62_current_market_labels_and_complete_86_edge_addresses",
            "per_site_operating_energized_leased_customer_accepted_utilized_billed_and_actual_IT_load",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life",
            "per_site_measured_PUE_WUE_energy_water_emissions_and_live_liquid_cooled_MW",
            "Cogent_owned_or_customer_GPU_model_count_owner_site_delivery_rack_fabric_power_utilization_revenue_and_margin",
            "data_center_only_revenue_operating_profit_cash_flow_capex_ROIC_customer_concentration_occupancy_pricing_and_contract_term",
            "24_marketed_facilities_exact_roster_asking_price_status_and_realized_proceeds",
            "current_share_price_enterprise_value_and_valuation_require_same_date_market_data",
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
    registry = args.output_dir / "cogent_official_data_center_registry.jsonl"
    summary_path = args.output_dir / "cogent_official_data_center_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
