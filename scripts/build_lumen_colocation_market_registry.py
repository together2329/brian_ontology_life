#!/usr/bin/env python3
"""Build Lumen's provider-published colocation-market registry.

Lumen publishes portfolio headlines and a city/state market list, not a current
building/address roster.  This builder therefore keeps provider market rows,
OSM physical objects, divested overseas assets, network reach, power/cooling
features, GPU evidence and company financials in separate scopes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


COLOCATION_PAGE = "https://www.lumen.com/en-us/services/colocation.html"
LOCATION_DATA_SHEET = "https://assets.lumen.com/is/content/Lumen/colocation-location-data-sheet?Creativeid=936d4e33-cf54-4625-b4f2-8a8e224af6eb"
HISTORICAL_2024_OVERVIEW = "https://assets.lumen.com/is/content/Lumen/colocation-overview-data-sheet?Creativeid=1251e94a-b729-42ac-877d-abf98cc7cef5"
NETWORK_MAPBOOK = "https://assets.lumen.com/is/content/Lumen/LumenNetworkMapbook25?Creativeid=91d1e412-8b8a-4608-9f5e-eccd4dc3ae0f.html"
SERVICE_SCHEDULE = "https://assets.lumen.com/is/content/Lumen/data-center-facilities-colo-sch?Creativeid=228ecd41-0f06-498e-bf04-283f8b3e6b30"
NANTERRE_HISTORICAL_SHEET = "https://assets.lumen.com/is/content/Lumen/len-1229-data-centre-colocation-paris-uk-web"
LATAM_DIVESTITURE = "https://ir.lumen.com/news/news-details/2022/Lumen-Technologies-reports-third-quarter-2022-results/default.aspx"
EMEA_DIVESTITURE = "https://ir.lumen.com/news/news-details/2023/Lumen-Completes-Sale-of-EMEA-Business-to-Colt-Technology-Services-for-1-8B/default.aspx"
FY2025_RESULTS = "https://ir.lumen.com/news/news-details/2026/Lumen-Technologies-Reports-Solid-Fourth-Quarter-and-Full-Year-2025-Results-Completes-ATT-Transaction-Strengthening-Balance-Sheet-and-Advancing-Enterprise-Focus/default.aspx"
FY2025_10K = "https://www.sec.gov/Archives/edgar/data/18926/000001892626000014/lumn-20251231.htm"
Q1_2026_RESULTS = "https://ir.lumen.com/news/news-details/2026/Lumen-Technologies-Reports-Solid-First-Quarter-2026-Results/default.aspx"
Q1_2026_10Q = "https://www.sec.gov/Archives/edgar/data/18926/000001892626000046/lumn-20260331.htm"
INVESTOR_DAY_2026 = "https://ir.lumen.com/news/news-details/2026/Lumen-Marks-New-Phase-of-Transformation-at-2026-Investor-Day/default.aspx"
AI_DEALS_2024 = "https://ir.lumen.com/news/news-details/2024/AI-Demand-Drives-5-Billion-in-New-Business-and-Massive-Expansion-of-the-Internet/default.aspx"
MICROSOFT_PCF = "https://ir.lumen.com/news/news-details/2024/Microsoft-and-Lumen-Technologies-partner-to-power-the-future-of-AI-and-enable-digital-transformation-to-benefit-hundreds-of-millions-of-customers/default.aspx"
META_PCF = "https://ir.lumen.com/news/news-details/2024/Lumen-and-Meta-Partner-to-Drive-AI-Network-Expansion/default.aspx"
NETWORK_BUILD_2025 = "https://ir.lumen.com/news/news-details/2025/Lumen-Accelerates-Multi-Billion-Dollar-Network-Expansion-to-Meet-Soaring-AI-Demand/default.aspx"
MULTICLOUD_2026 = "https://ir.lumen.com/news/news-details/2026/Lumen-Targets-AI-Bottlenecks-with-New-Multi-Cloud-Gateway-and-Metro-Expansion/default.aspx"


# Exact four-column transcription of the 2025 provider PDF.  These are market
# rows, not facility identifiers, addresses, campuses or one-to-one buildings.
MARKETS = [
    ("Birmingham", "AL"), ("Wilmington", "DE"), ("St. Louis", "MO"), ("Pittsburgh", "PA"),
    ("Mobile", "AL"), ("Daytona Beach", "FL"), ("Jackson", "MS"), ("Lachine", "QC"),
    ("Phoenix", "AZ"), ("Ft. Lauderdale", "FL"), ("Charlotte", "NC"), ("Providence", "RI"),
    ("Tucson", "AZ"), ("Ft. Myers", "FL"), ("Greensboro", "NC"), ("Columbia", "SC"),
    ("Anaheim", "CA"), ("Jacksonville", "FL"), ("Raleigh", "NC"), ("Spartanburg", "SC"),
    ("Bakersfield", "CA"), ("Melbourne", "FL"), ("W. Bellevue", "NE"), ("Memphis", "TN"),
    ("Emeryville", "CA"), ("Orlando", "FL"), ("Monmouth Junction", "NJ"), ("Nashville", "TN"),
    ("Fresno", "CA"), ("Tallahassee", "FL"), ("Newark", "NJ"), ("Amarillo", "TX"),
    ("Hayward", "CA"), ("Tampa", "FL"), ("Weehawken", "NJ"), ("Austin", "TX"),
    ("Los Angeles", "CA"), ("West Palm Beach", "FL"), ("Albuquerque", "NM"), ("Corpus Christi", "TX"),
    ("Manchester", "CA"), ("Atlanta", "GA"), ("Santa Teresa", "NM"), ("Dallas", "TX"),
    ("Modesto", "CA"), ("Pleasant Hill", "IA"), ("Las Vegas", "NV"), ("El Paso", "TX"),
    ("Riverside", "CA"), ("Boise", "ID"), ("Reno", "NV"), ("Fort Worth", "TX"),
    ("Sacramento", "CA"), ("Broadview", "IL"), ("Albany", "NY"), ("Harlingen", "TX"),
    ("San Bernardino", "CA"), ("Chicago", "IL"), ("Buffalo", "NY"), ("Houston", "TX"),
    ("San Diego", "CA"), ("Indianapolis", "IN"), ("East Syracuse", "NY"), ("Laredo", "TX"),
    ("San Luis Obispo", "CA"), ("South Bend", "IN"), ("New York", "NY"), ("Lubbock", "TX"),
    ("Santa Barbara", "CA"), ("Louisville", "KY"), ("Rochester", "NY"), ("McAllen", "TX"),
    ("Santa Clara", "CA"), ("Baton Rouge", "LA"), ("Akron", "OH"), ("San Antonio", "TX"),
    ("Sunnyvale", "CA"), ("New Orleans", "LA"), ("Cincinnati", "OH"), ("Stratford", "TX"),
    ("Tustin", "CA"), ("Cambridge", "MA"), ("Cleveland", "OH"), ("Waco", "TX"),
    ("Toronto", "CN"), ("Springfield", "MA"), ("Columbus", "OH"), ("Wichita Falls", "TX"),
    ("Aurora", "CO"), ("Worcester", "MA"), ("Dayton", "OH"), ("Ogden", "UT"),
    ("Colorado Springs", "CO"), ("Baltimore", "MD"), ("Oklahoma City", "OK"), ("Salt Lake City", "UT"),
    ("Denver", "CO"), ("Detroit", "MI"), ("Tulsa", "OK"), ("Herndon", "VA"),
    ("Hartford", "CT"), ("Lansing", "MI"), ("Bandon", "OR"), ("McLean", "VA"),
    ("New Haven", "CT"), ("Southfield (Detroit)", "MI"), ("Eugene", "OR"), ("Richmond", "VA"),
    ("Stamford", "CT"), ("Minneapolis", "MN"), ("Portland", "OR"), ("Seattle", "WA"),
    ("Washington", "DC"), ("Columbia", "MO"), ("Lancaster", "PA"), ("Madison", "WI"),
    ("Newark", "DE"), ("Kansas City", "MO"), ("Philadelphia", "PA"), ("Milwaukee", "WI"),
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def market_id(city: str, state: str) -> str:
    return f"lumen_market_{slug(city)}_{slug(state)}"


OSM_TO_MARKET = {
    "osm_way_254756938": market_id("Las Vegas", "NV"),
    "osm_way_151179323": market_id("Phoenix", "AZ"),
    "osm_way_209077298": market_id("Santa Clara", "CA"),
    "osm_node_12682482760": market_id("Albany", "NY"),
    "osm_way_379195054": market_id("Austin", "TX"),
    "osm_node_11168593074": market_id("Baltimore", "MD"),
    "osm_way_465032201": market_id("Dallas", "TX"),
    "osm_way_465032484": market_id("Dallas", "TX"),
    "osm_node_13226718075": market_id("Madison", "WI"),
    "osm_node_9669639033": market_id("McLean", "VA"),
    "osm_way_239147373": market_id("McLean", "VA"),
    "osm_way_343333944": market_id("Minneapolis", "MN"),
    "osm_way_319857331": market_id("San Antonio", "TX"),
    "osm_way_209073635": market_id("Santa Clara", "CA"),
    "osm_way_37877544": market_id("Sunnyvale", "CA"),
}


RESIDUAL_OSM = {
    "osm_way_487510946": {
        "classification": "legacy_Lumen_label_after_Latin_America_divestiture_to_Stonepeak_Cirion_2022_08_01",
        "note": "Mendoza is outside the current North American colocation scope; the OSM operator attribution is not treated as current Lumen ownership or operation.",
        "source": LATAM_DIVESTITURE,
    },
    "osm_node_6289564874": {
        "classification": "legacy_Lumen_label_after_EMEA_divestiture_to_Colt_2023_11_01",
        "note": "The OSM point aligns with the historical Lumen Nanterre/Paris sheet, but current ownership, equipment and service state require Colt evidence.",
        "source": EMEA_DIVESTITURE,
        "historical_pre_divestiture_equipment_snapshot": {
            "maximum_site_power_mva": 4,
            "grid": "20 kV underground ring to dedicated 2 x 2 MVA 10 kV/400 V transformer substation",
            "generators": "2 x 1 MVA diesel generators, 2 MVA total; automatic start under one minute; monthly tests; 24-hour fuel at full load",
            "UPS": "3 x 420 kVA hybrid rotary modules, 840 kVA total N+1, 15-minute battery autonomy",
            "cooling": "750 W/m2 average cooling over gross space; below 26 C; humidity 50% RH +/-20%; positively pressurized technical areas",
            "boundary": "Historical Lumen sheet from the pre-divestiture portfolio; values are not asserted as current Colt equipment or capacity.",
            "source": NANTERRE_HISTORICAL_SHEET,
        },
    },
    "osm_way_140910921": {"classification": "legacy_Lumen_label_after_EMEA_divestiture_to_Colt_2023_11_01", "note": "French OSM object is not treated as current Lumen ownership or operation.", "source": EMEA_DIVESTITURE},
    "osm_way_1131944103": {"classification": "legacy_Lumen_label_after_EMEA_divestiture_to_Colt_2023_11_01", "note": "Middlesbrough OSM object is not treated as current Lumen ownership or operation.", "source": EMEA_DIVESTITURE},
    "osm_way_458775803": {"classification": "legacy_Lumen_label_after_EMEA_divestiture_to_Colt_2023_11_01", "note": "The mapped object is named a cable landing station; it is not automatically a sellable colocation facility and is not treated as current Lumen ownership.", "source": EMEA_DIVESTITURE},
    "osm_way_459600829": {"classification": "legacy_Lumen_label_after_EMEA_divestiture_to_Colt_2023_11_01", "note": "United Kingdom OSM object is not treated as current Lumen ownership or operation.", "source": EMEA_DIVESTITURE},
    "osm_way_300162689": {"classification": "United_States_OSM_object_not_exactly_crosswalked_to_2025_provider_city_row", "note": "Ashburn is not an exact 2025 PDF city row. Nearby Herndon/McLean labels do not prove the same facility or market identity."},
    "osm_way_444683815": {"classification": "United_States_OSM_object_absent_from_2025_provider_city_rows", "note": "Spokane appears in other Lumen product scopes but not the reviewed 2025 colocation city list; product footprints are not merged."},
    "osm_way_835601088": {"classification": "United_States_OSM_object_absent_from_2025_provider_city_rows", "note": "The small St. George-area footprint has building=house in OSM and no provider facility identifier; current colocation identity remains unresolved."},
    "osm_way_366049843": {"classification": "United_States_OSM_object_not_exactly_crosswalked_to_2025_provider_city_row", "note": "Norristown is not an exact PDF row. The Philadelphia market label does not prove facility identity."},
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_lumen_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    related: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        if row.get("operator") == "Lumen Technologies":
            related.append(row)
    return by_id, related


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    assert len(MARKETS) == 120, len(MARKETS)
    assert len({market_id(city, state) for city, state in MARKETS}) == len(MARKETS)
    osm, related = load_lumen_osm(osm_path)
    expected = set(OSM_TO_MARKET) | set(RESIDUAL_OSM)
    actual = {row["id"] for row in related}
    assert len(related) == 25, len(related)
    assert expected == actual, sorted(expected ^ actual)
    current_market_ids = {market_id(city, state) for city, state in MARKETS}
    assert set(OSM_TO_MARKET.values()) <= current_market_ids

    mapped: dict[str, list[dict]] = {}
    for object_id, provider_market_id in OSM_TO_MARKET.items():
        row = osm[object_id]
        note = "Public map point or footprint matched only to an exact provider city/state row; it does not prove facility identity, ownership, lifecycle or building count."
        if object_id in {"osm_node_9669639033", "osm_way_239147373"}:
            note += " The McLean node and footprint appear co-located and must not be counted as two proven facilities."
        mapped.setdefault(provider_market_id, []).append({
            "osm_object_id": object_id,
            "name": row.get("name"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "source_url": row["source_url"],
            "boundary": note,
        })

    records = []
    for order, (city, state) in enumerate(MARKETS, 1):
        record_id = market_id(city, state)
        country = "CA" if state in {"QC", "CN"} else "US"
        anomaly = None
        if state == "CN":
            anomaly = "The source prints Toronto state code CN; this registry preserves CN and normalizes the country to Canada without silently changing the source text."
        records.append({
            "id": record_id,
            "object_type": "ProviderPublishedColocationMarketRow",
            "source_order": order,
            "operator": "Lumen Technologies",
            "provider_city_label": city,
            "provider_state_or_province_code": state,
            "normalized_country_iso2": country,
            "source_anomaly": anomaly,
            "record_granularity": "provider_city_state_market_row_not_facility_identifier_address_campus_or_building",
            "current_facility_count_in_market": "undisclosed",
            "current_operating_lifecycle_by_facility": "undisclosed",
            "current_owned_leased_or_partner_operated_split": "undisclosed",
            "current_site_area_MW_grid_equipment_cooling_PUE_WUE_and_water": "undisclosed_at_market_row_granularity",
            "current_exact_GPU_model_count_owner_delivery_state_utilization_power_and_economics": "undisclosed",
            "osm_market_evidence": mapped.get(record_id, []),
            "source_urls": [LOCATION_DATA_SHEET, COLOCATION_PAGE],
            "accessed_on": accessed_on,
        })
    return records, related


def build_summary(records: list[dict], related: list[dict], osm_path: Path, accessed_on: str) -> dict:
    osm, _ = load_lumen_osm(osm_path)
    residual = [{"osm_object_id": object_id, "osm_name": osm[object_id].get("name"), "country_codes": [item["iso2"] for item in osm[object_id].get("country_candidates", [])], **details} for object_id, details in RESIDUAL_OSM.items()]
    related_country_counts = Counter(item["iso2"] for row in related for item in row.get("country_candidates", []))
    market_osm_counts = Counter(OSM_TO_MARKET.values())
    return {
        "schema_version": 1,
        "registry": "Lumen provider-published North American colocation market-row registry",
        "accessed_on": accessed_on,
        "provider_published_2025_city_state_rows": len(records),
        "provider_published_country_rows": dict(sorted(Counter(row["normalized_country_iso2"] for row in records).items())),
        "current_web_headlines": {
            "locations_in_North_America_more_than": 200,
            "cities_offering_colocation_more_than": 120,
            "colocation_customers_more_than": 2600,
            "compliance_certification_locations_more_than": 50,
            "resell_partners": 7,
            "resell_partner_locations_more_than": 400,
        },
        "2025_data_sheet_headlines": {
            "carrier_neutral_or_on_net_Lumen_data_centers_more_than": 175,
            "North_American_markets_more_than": 60,
            "listed_city_state_rows": len(records),
            "customers_more_than": 2600,
            "global_route_miles_approximate": 340000,
        },
        "historical_2024_snapshot_not_current_roster": {
            "ownership_wording": "owns and operates approximately 200 carrier-neutral data centers throughout North America",
            "on_net_data_centers_more_than": 200,
            "route_miles_approximate": 350000,
            "city_rows_present_then_absent_from_2025_list": ["Irvine, CA", "Honolulu, HI"],
            "boundary": "The 2024 ownership wording and list are retained as a dated snapshot; they do not prove the present ownership or lifecycle of every current web-page location.",
        },
        "scope_reconciliation": "Current web 200+ locations/120+ cities, the 2025 PDF 175+ data centers/60+ markets/124 city rows, the historical 2024 approximately-200 owned-and-operated claim, 400+ reseller locations, 2,200+ on-net third-party data centers, network PoPs and RapidRoutes sites are different dated or commercial scopes and are not silently reconciled or added.",
        "physical_roster_boundary": "No reviewed current official source exposes a building-level address roster for the 175+ or 200+ headline. The 124 JSONL records are market rows, not facilities, and publish no current per-building MW or lifecycle.",
        "current_portfolio_power_and_cooling": {
            "current_web_power_types": ["AC", "DC"],
            "current_web_power_density_per_cabinet_kw": {"minimum": 3, "maximum": 12},
            "2025_data_sheet_power_density_per_cabinet_kw": {"minimum": 3, "maximum": 15},
            "cooling_redundancy_options_vary_by_site": ["N", "2N", "N+1"],
            "generator_redundancy_options_vary_by_site": ["N", "2N", "N+1"],
            "current_service_schedule": {
                "conditioned_power": "Lumen-operated UPS or DC battery backup; 100% monthly power-availability SLA subject to contract conditions",
                "customer_requirement": "primary and redundant A/B sources, each able to support 100% load",
                "over_3kW_environment": "30%-70% RH and 78 F/26 C maximum",
                "under_3kW_environment": "20%-80% RH and 85 F/29.5 C maximum",
            },
            "equipment_boundary": "These are fleet service ranges and contractual environmental limits. They do not disclose per-site utility feeds, substations, transformer/switchgear/UPS/battery/generator/chiller/CDU OEMs, counts, ratings or as-built topology.",
        },
        "network_and_AI_scope": {
            "2026_mapbook": {"global_route_miles_approximate": 340000, "on_net_buildings_approximate": 163000, "on_net_third_party_data_centers_more_than": 2200, "next_gen_400G_route_miles_more_than": 100000, "PoPs_more_than": 400, "North_American_markets": 70, "data_centers_per_market_range": "10-20_network_reach_statement_not_Lumen_owned_facility_count"},
            "PCF_contract_value_usd_billion_nearly_as_of_2026_02_25": 13,
            "named_PCF_or_AI_network_customers": ["Microsoft", "Meta", "Anthropic"],
            "intercity_fiber_miles_2025_year_end_million": 17,
            "intercity_fiber_miles_target_2028_million": 47,
            "intercity_fiber_miles_target_2031_million": 58,
            "2025_added_network_capacity_pbps_more_than": 5.9,
            "2026_metro_data_center_connectivity": "up to 100 Gbps across 16 U.S. markets and up to 400 Gbps at key cloud data centers",
            "boundary": "PCF values are long-term connectivity deal values, not recognized revenue, GPU purchases, colocation MW or data-center capex. Customer GPU fleets are not Lumen-owned inventory.",
        },
        "GPU_and_accelerator_disclosure": {
            "exact_Lumen_owned_or_hosted_GPU_models_counts_sites_owner_delivery_state_utilization_power_revenue_and_margin": "undisclosed",
            "AI_ready_marketing_boundary": "AI-ready colocation, GPUaaS network examples and PCF links to hyperscaler data centers prove connectivity demand, not a Lumen-owned accelerator fleet.",
            "density_caution": "Published 3-12 kW web and 3-15 kW PDF cabinet ranges cannot be generalized to modern high-density GPU racks at every site; custom higher-density capability, if any, requires site-specific evidence.",
        },
        "OSM_reconciliation": {
            "objects_with_operator_label_Lumen_Technologies": len(related),
            "country_counts": dict(sorted(related_country_counts.items())),
            "exact_city_row_crosswalked_objects": len(OSM_TO_MARKET),
            "exact_city_rows_with_OSM_crosswalk": len(market_osm_counts),
            "provider_city_rows_without_OSM_crosswalk": len(records) - len(market_osm_counts),
            "residual_objects": residual,
            "divested_overseas_legacy_label_objects": sum(details["classification"].startswith("legacy_Lumen") for details in RESIDUAL_OSM.values()),
            "United_States_unresolved_or_absent_city_row_objects": sum(details["classification"].startswith("United_States") for details in RESIDUAL_OSM.values()),
            "boundary": "OSM points and footprints are public map evidence, not provider-certified facilities. Duplicate geometries, telecom buildings, a cable landing station and post-divestiture labels prevent object, facility and building count equivalence.",
        },
        "financial_profile_ref": "company_lumen_technologies",
        "portfolio_profile_ref": "dc_lumen_north_america_colocation_network_portfolio",
        "source_urls": [COLOCATION_PAGE, LOCATION_DATA_SHEET, HISTORICAL_2024_OVERVIEW, NETWORK_MAPBOOK, SERVICE_SCHEDULE, NANTERRE_HISTORICAL_SHEET, LATAM_DIVESTITURE, EMEA_DIVESTITURE, FY2025_RESULTS, FY2025_10K, Q1_2026_RESULTS, Q1_2026_10Q, INVESTOR_DAY_2026, AI_DEALS_2024, MICROSOFT_PCF, META_PCF, NETWORK_BUILD_2025, MULTICLOUD_2026],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records, related = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, related, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "lumen_colocation_market_registry.jsonl"
    summary_path = args.output_dir / "lumen_colocation_market_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_related": len(related), "records_sha256": summary["records_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
