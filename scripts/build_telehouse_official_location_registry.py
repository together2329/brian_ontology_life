#!/usr/bin/env python3
"""Build Telehouse's current official location-label registry and OSM crosswalk.

The July 2025 global brochure lists 31 country/city/campus labels but reports
more than 45 data-center sites.  Tokyo, Frankfurt and other rows aggregate
multiple buildings, while some current regional pages add detail omitted from
the global page.  This builder preserves that granularity rather than calling
31 labels or OSM objects a complete physical-building total.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


BROCHURE_URL = "https://www.telehouse.com/wp-content/uploads/2025/09/Telehouse-Global-Brochure-2025.pdf"
GLOBAL_URL = "https://www.telehouse.com/global-data-centers/"
LONDON_URL = "https://www.telehouse.net/data-centre-services/uk/london/"
PARIS_URL = "https://www.telehouse.net/data-centre-services/france/paris/"
FRANKFURT_URL = "https://www.telehouse.net/data-centre-services/germany/frankfurt/telehouse-frankfurt/"
TOKYO_URL = "https://www.telehouse.com/global-data-centers/asia/tokyo-data-centers/"
TAMA3_URL = "https://www.telehouse.com/global-data-centers/asia/tokyo-data-centers/tama-3/"
LIQUID_LAB_URL = "https://www.telehouse.net/news/telehouse-launches-pioneering-liquid-cooling-lab/"
SHIBUYA_URL = "https://newsroom.kddi.com/english/news/detail/kddi_nr-454_3732.html"
RENEWABLE_URL = "https://news.kddi.com/kddi/corporate/csr-topic/2026/04/30/7739.html"
KDDI_REPORT_URL = "https://www.kddi.com/extlib/files/english/corporate/ir/ir-library/sustainability-integrated-report/pdf/kddi_sir2025_e_p_OB5ud7.pdf"
KDDI_FINANCE_URL = "https://www.kddi.com/english/corporate/ir/finance/result-forecast/"


def location(code: str, label: str, country_code: str, market: str, location_url: str, **extra: object) -> dict:
    return {
        "location_code": code,
        "location_label": label,
        "country_code": country_code,
        "market": market,
        "lifecycle_as_of_2026_07_19": "operating_or_current_market_group",
        "location_url": location_url,
        **extra,
    }


LOCATIONS = [
    location("CA_TORONTO_151", "Toronto 151 Front Street West", "CA", "Toronto", "https://www.telehouse.ca/data-centres/", address="151 Front Street West, Toronto, Ontario"),
    location("CA_TORONTO_250", "Toronto 250 Front Street West", "CA", "Toronto", "https://www.telehouse.ca/data-centres/", address="250 Front Street West, Toronto, Ontario"),
    location("CA_TORONTO_905", "Toronto 905 King Street West", "CA", "Toronto", "https://www.telehouse.ca/data-centres/", address="905 King Street West, Toronto, Ontario"),
    location("US_NY_TELEPORT", "New York Teleport", "US", "New York / Staten Island", "https://www.telehouse.com/global-data-centers/america/new-york-datacenters/telehouse-new-york-teleport-data-center/", address="7 Teleport Drive, Staten Island, NY 10311", equipment_context={"high_density_rack_kW_up_to": 20, "power": "redundant commercial feeds, N+1 UPS and multiple backup generators", "cooling": "redundant air cooling with hot/cold aisle containment"}),
    location("US_NY_CHELSEA", "New York Chelsea", "US", "New York / Manhattan", "https://www.telehouse.com/global-data-centers/america/new-york-datacenters/telehouse-new-york-chelsea/", address="85 10th Avenue, New York, NY"),
    location("US_LA", "Los Angeles", "US", "Los Angeles", "https://www.telehouse.com/global-data-centers/america/los-angeles-data-centers/", address="626 Wilshire Boulevard, Los Angeles, CA"),
    location("FR_VOLTAIRE", "Paris Voltaire", "FR", "Paris", "https://www.telehouse.net/data-centre-services/france/paris/telehouse-paris-voltaire/", address="137 Boulevard Voltaire, 75011 Paris", area_context={"colocation_sqm": 7000}, equipment_context={"utility": "2 x 10 MW public-company feeds and two dedicated cables", "generators": "6 x 2 MVA MTU, N+1", "fuel": "3 tanks, 50 m3 total and 72 hours at full load", "UPS": "Siemens 150-400 kVA, N+1 to N+N with STS and 30-minute battery", "cooling": "7 Carrier screw units, 5,600 kW total N+1; 70 kW Aircé cabinets N+1 to N+N"}),
    location("FR_JEUNEURS", "Paris Jeûneurs", "FR", "Paris", "https://www.telehouse.net/data-centre-services/france/paris/", address="38 Rue des Jeûneurs, 75002 Paris"),
    location("FR_MAGNY", "Paris Magny", "FR", "Paris / Magny-les-Hameaux", "https://www.telehouse.net/data-centre-services/france/paris/telehouse-magny-les-hameaux/", address="1 Rue Pablo Picasso, 78114 Magny-les-Hameaux"),
    location("FR_MAGNY_2", "Paris Magny 2", "FR", "Paris / Magny-les-Hameaux", "https://www.telehouse.net/data-centre-services/france/paris/telehouse-paris-magny-2/", address="Magny-les-Hameaux campus, France", granularity_boundary="Provider label on a multi-building campus; not necessarily one physical building."),
    location("GB_LONDON_NORTH", "London North", "GB", "London Docklands", "https://www.telehouse.net/data-centre-services/uk/london/telehouse-north/", address="Coriander Avenue, London E14 2AA", equipment_context={"generators": "6, N+1", "UPS": "N+1 or 2N", "rack_power_kW": "0.5 to 2", "cooling": "closed-control air, N+1; redundant A/B pipe routes and N+1 pumps"}),
    location("GB_LONDON_NORTH_TWO", "London North Two", "GB", "London Docklands", "https://www.telehouse.net/data-centre-services/uk/london/telehouse-north-two/", address="Coriander Avenue, London E14 2AA", equipment_context={"generators": "8, N+1", "UPS": "2(N+1)", "rack_power_kW": "3 and upwards", "cooling": "indirect adiabatic and evaporative"}, environmental_context={"design_PUE": 1.16}),
    location("GB_LONDON_EAST", "London East", "GB", "London Docklands", "https://www.telehouse.net/data-centre-services/uk/london/telehouse-east/", address="Coriander Avenue, London E14 2AA", equipment_context={"generators": "5, N+1", "UPS": "N+1 or 2N", "rack_power_kW": "0.5 to 2"}),
    location("GB_LONDON_WEST", "London West", "GB", "London Docklands", "https://www.telehouse.net/data-centre-services/uk/london/telehouse-west/", address="Coriander Avenue, London E14 2AA", equipment_context={"generators": "8, N+1", "UPS": "2(N+1)", "rack_power_kW": "2 to 4"}),
    location("GB_LONDON_SOUTH", "London South", "GB", "London Docklands / Blackwall Yard", "https://www.telehouse.net/data-centre-services/uk/london/telehouse-south/", address="1 Paul Julius Close, London E14 2EH", capacity_context={"existing_IT_mw_in_2025_factsheet": 7.4, "full_build_IT_mw": 18, "peak_IT_load_current_homepage_mw": 5.4}, area_context={"gross_sqm": 31000, "rack_footprints_per_floor": 688}, equipment_context={"incoming_feeds": "dual redundant diverse routes", "generators": "N+1 with 24-hour fuel storage", "UPS": "2N distributed redundancy", "cooling": "free-cooling air-cooled chillers N+1 and N+20% floor CRAH"}, environmental_context={"design_PUE_below": 1.3, "design_WUE_below": 0.01, "renewable_power": True}, source_conflict="The current homepage markets 5.4 MW peak IT load while the 2025 factsheet says 7.4 MW existing and 18 MW full-build; the measures/dates are retained separately."),
    location("DE_FRANKFURT", "Frankfurt", "DE", "Frankfurt", FRANKFURT_URL, address="Kleyerstrasse 79-89, 60326 Frankfurt am Main", facility_group_context={"campus_buildings_reported_in_2024_KDDI_report": 5, "older_current_page_text_data_centers": 3}, area_context={"site_sqm": 67000, "fitted_colocation_sqm": 25000}, equipment_context={"utility": "two independent feeds from two substations", "rack_power_kW_up_to": 8, "UPS": "N+1 with battery backup", "emergency_power_MVA_up_to": 21, "diesel_runtime_days": 3, "cooling": "redundant N+1"}, source_conflict="KDDI said the fifth building opened in October 2023, while one current Telehouse page still describes three data centers; the Frankfurt brochure row remains a campus label."),
    location("TR_ISTANBUL", "Istanbul", "TR", "Istanbul / Kozyatağı", "https://www.telehouse.net/data-centre-services/turkey/istanbul/", partnership_context="Operated to Telehouse standards with local partner Teknotel Telekomünikasyon"),
    location("CN_BEIJING_BDA", "Beijing BDA", "CN", "Beijing", "https://www.telehouse.com/global-data-centers/asia/china-data-centers/"),
    location("CN_BEIJING_BEZ", "Beijing BEZ", "CN", "Beijing", "https://www.telehouse.com/global-data-centers/asia/china-data-centers/"),
    location("CN_SHANGHAI_ZHANGJIANG", "Shanghai Zhangjiang", "CN", "Shanghai", "https://www.telehouse.com/global-data-centers/asia/china-data-centers/"),
    location("CN_SHANGHAI_JINQIAO", "Shanghai Jinqiao", "CN", "Shanghai", "https://www.telehouse.com/global-data-centers/asia/china-data-centers/"),
    location("JP_SENDAI", "Sendai", "JP", "Sendai", "https://www.telehouse.com/global-data-centers/asia/japan-data-centers/"),
    location("JP_OYAMA", "Oyama", "JP", "Oyama", "https://www.telehouse.com/global-data-centers/asia/japan-data-centers/"),
    location("JP_TOKYO", "Tokyo", "JP", "Tokyo", TOKYO_URL, facility_group_context={"carrier_neutral_data_center_facilities_in_Tokyo": 11, "named_examples": ["Otemachi", "Tama 3", "Tama 5", "Shibuya"]}, granularity_boundary="One brochure city label aggregates eleven Tokyo facilities and cannot be treated as one building."),
    location("JP_NAGOYA", "Nagoya", "JP", "Nagoya", "https://www.telehouse.com/global-data-centers/asia/japan-data-centers/", facility_group_context={"historically_marketed_facilities": 2}),
    location("JP_OSAKA", "Osaka", "JP", "Osaka", "https://www.telehouse.com/global-data-centers/asia/japan-data-centers/", facility_group_context={"historically_marketed_facilities": 2, "current_named_example": "Osaka 2"}),
    location("JP_FUKUOKA", "Fukuoka", "JP", "Fukuoka", "https://www.telehouse.com/global-data-centers/asia/japan-data-centers/"),
    location("HK_CCC", "Hong Kong CCC", "HK", "Hong Kong", "https://www.telehouse.com/global-data-centers/asia/hong-kong-data-centers/"),
    location("SG_SINGAPORE", "Singapore", "SG", "Singapore", "https://www.telehouse.com/global-data-centers/asia/singapore-data-centers/"),
    location("TH_BANGKOK", "Bangkok", "TH", "Bangkok", "https://www.telehouse.com/global-data-centers/asia/bangkok-data-center/telehouse-bangkok/"),
    location("VN_HANOI", "Hanoi", "VN", "Hanoi", "https://www.telehouse.com/global-data-centers/asia/hanoi-data-centers/"),
]


OSM_TO_LOCATION = {
    "osm_way_1185768205": "DE_FRANKFURT", "osm_way_1423647898": "DE_FRANKFURT",
    "osm_way_35603471": "DE_FRANKFURT", "osm_way_35604586": "DE_FRANKFURT",
    "osm_way_616337075": "DE_FRANKFURT", "osm_node_6102483146": "FR_JEUNEURS",
    "osm_node_6015635281": "FR_VOLTAIRE", "osm_way_700526670": "FR_MAGNY",
    "osm_way_206625804": "GB_LONDON_EAST", "osm_way_206625800": "GB_LONDON_NORTH",
    "osm_way_497956675": "GB_LONDON_NORTH_TWO", "osm_way_193806160": "GB_LONDON_SOUTH",
    "osm_way_34160179": "GB_LONDON_WEST", "osm_way_1457990503": "TH_BANGKOK",
    "osm_way_247428943": "US_NY_TELEPORT",
}
UNMATCHED_RELATED_OSM_IDS = ["osm_node_12150464472"]


PORTFOLIO_CONTEXT = {
    "official_global_brochure_location_labels": 31,
    "operator_reported_data_center_sites_more_than": 45,
    "countries_more_than": 10,
    "global_space_sqm_more_than": 560000,
    "average_MVA_per_data_center": 20,
    "customers_worldwide": 3000,
    "connectivity_partners_more_than": 1000,
    "scope_boundary": "The 31 brochure labels aggregate cities, campuses and multiple facilities; the more-than-45 headline is not a disclosed physical-building roster or live power total.",
    "London_campus": {"data_centers": 5, "private_substation_MVA": 50, "grid_feeds": "two 132 kV lines", "substation_redundancy": "N+N"},
    "accelerators": {
        "Telehouse_or_KDDI_owned_GPU_inventory": "undisclosed",
        "London_South_liquid_cooling_lab": {"technologies": ["Accelsius NeuCool two-phase direct-to-chip", "JetCool SmartPlate", "Legrand ColdLogik", "EkkoSense optimization"], "test_hardware": "thermal simulation and cooling demonstration; no installed production GPU count disclosed"},
        "Tokyo_Shibuya_verification": {"maximum_power_source_kVA": 300, "maximum_cooling_kW": 300, "design_test_context": "NVIDIA GB200 NVL72 at 100 kW-plus per rack", "actual_GPU_count": "undisclosed"},
        "boundary": "Cooling labs, heat-load tests and platform compatibility do not establish a production GPU fleet, model split, ownership, utilization or site economics.",
    },
    "environment": {
        "KDDI_group_data_centers_renewable_electricity_percent": 100,
        "achievement_announcement": "2026-04-30",
        "instrument_boundary": "includes renewable-energy programs and environmental certificates; not necessarily hourly additional renewable matching",
        "current_fleet_PUE_WUE_water_energy_and_emissions": "undisclosed",
    },
    "financial_boundary": {
        "parent": "KDDI Corporation",
        "FY2025_3_KDDI_data_center_operating_revenue_jpy_billion": 130,
        "FY2024_3_comparable_jpy_billion": 121,
        "FY2031_3_target_jpy_billion": 200,
        "Telehouse_standalone_revenue_and_operating_profit": "undisclosed",
        "boundary": "KDDI's data-center revenue includes the parent data-center business and is not a Telehouse-legal-entity or per-site result.",
    },
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        combined = f"{row.get('name') or ''} {row.get('operator') or ''}".casefold()
        if "telehouse" in combined and "transact" not in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(LOCATIONS) == 31
    assert len({row["location_code"] for row in LOCATIONS}) == 31
    assert len(candidates) == 16, [row["id"] for row in candidates]
    assert set(OSM_TO_LOCATION) | set(UNMATCHED_RELATED_OSM_IDS) == {row["id"] for row in candidates}
    mapped: dict[str, list[dict]] = {}
    for object_id, code in OSM_TO_LOCATION.items():
        source = osm[object_id]
        mapped.setdefault(code, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"], "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"), "source_url": source["source_url"],
            "boundary": "OSM point or footprint; not provider-certified lifecycle, ownership, capacity, tenancy or financial evidence.",
        })
    common_sources = [BROCHURE_URL, GLOBAL_URL, LONDON_URL, PARIS_URL, FRANKFURT_URL, TOKYO_URL, TAMA3_URL, LIQUID_LAB_URL, SHIBUYA_URL, RENEWABLE_URL, KDDI_REPORT_URL, KDDI_FINANCE_URL]
    records = []
    for position, source in enumerate(LOCATIONS, start=1):
        records.append({
            "id": f"telehouse_{source['location_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterLocationLabel",
            "source_order": position,
            "operator": "Telehouse / KDDI",
            "record_granularity": "provider_brochure_location_label_not_physical_building",
            **source,
            "osm_map_evidence": sorted(mapped.get(source["location_code"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source["location_url"], *common_sources])),
            "accessed_on": accessed_on,
        })
    unmatched = [{"osm_object_id": object_id, "osm_name": osm[object_id].get("name"), "osm_operator": osm[object_id].get("operator"), "source_url": osm[object_id]["source_url"], "reason": "Marseille THM1 appears in OSM and older Telehouse material but is absent from the July 2025 global brochure and current France city directory; current operator/lifecycle not inferred."} for object_id in UNMATCHED_RELATED_OSM_IDS]
    return records, candidates, unmatched


def build_summary(records: list[dict], candidates: list[dict], unmatched: list[dict], accessed_on: str) -> dict:
    assert sum(len(row["osm_map_evidence"]) for row in records) == 15
    return {
        "registry": "Telehouse July-2025 official global location-label and OSM crosswalk",
        "official_brochure_location_labels": len(records),
        "operator_reported_data_center_sites_more_than": 45,
        "country_counts_for_labels": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "market_counts_for_labels": dict(sorted(Counter(row["market"] for row in records).items())),
        "related_OSM_objects_excluding_TransACT_Telehouse": len(candidates),
        "mapped_OSM_objects": 15,
        "unmatched_or_legacy_OSM_objects": unmatched,
        "location_labels_with_OSM_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "portfolio_context": PORTFOLIO_CONTEXT,
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum location labels, city groups, campus buildings, historical site counts, OSM objects, MVA averages, design power, current IT load, test labs or customer hardware into one operating fleet measure.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/telehouse_official_location_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/telehouse_official_location_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, candidates, unmatched = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, unmatched, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
