#!/usr/bin/env python3
"""Build atNorth's official Nordic site registry and OSM crosswalk.

The current atNorth navigation exposes thirteen site codes, while the latest
ownership announcement reports eight operating sites and several developments.
Power values on site pages mix operating capacity, first phases and full-build
design.  This builder preserves those scopes and does not sum them into live MW.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY_URL = "https://www.atnorth.com/nordic-data-centers/"
SUSTAINABILITY_URL = "https://www.atnorth.com/wp-content/uploads/2026/06/Sustainability-Report-2025.pdf"
ACQUISITION_URL = "https://www.cppinvestments.com/newsroom/cpp-investments-and-equinix-to-acquire-atnorth-for-us4-billion/"
NORWAY_RELEASE_URL = "https://www.atnorth.com/news/atnorth-expands-to-norway-with-new-mega-site-in-haugaland/"
CRUSOE_URL = "https://www.atnorth.com/news/crusoe-expands-partnership-with-atnorth/"
SWE_AI_URL = "https://www.atnorth.com/case-studies/sovereign-ai-infrastructure-for-swedens-national-ai-cloud/"
OPERA_URL = "https://www.atnorth.com/blog/preparing-for-the-agentic-web-revolution/"


def site(
    code: str,
    name: str,
    country_code: str,
    locality: str,
    site_type: str,
    lifecycle: str,
    location_url: str,
    **extra: object,
) -> dict:
    return {
        "site_code": code,
        "marketed_name": name,
        "country_code": country_code,
        "locality": locality,
        "site_type": site_type,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "location_url": location_url,
        **extra,
    }


SITE_RECORDS = [
    site("ICE01", "Reykjavik metro site", "IS", "Reykjavik / Hafnarfjordur", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/iceland-data-centers/reykjavik-metro-site/", power_context={"site_power_capacity_mw": 3.2}, area_context={"facility_size_sqm": 2700}),
    site("ICE02", "Keflavik mega site", "IS", "Reykjanesbaer / Keflavik", "mega", "operating", "https://www.atnorth.com/nordic-data-centers/iceland-data-centers/keflavik-mega-site/", power_context={"campus_power_capacity_mw": 83}, area_context={"campus_hectares": 9}),
    site("ICE03", "Akureyri mega site", "IS", "Akureyri", "mega", "operating", "https://www.atnorth.com/nordic-data-centers/iceland-data-centers/akureyri-mega-site/", power_context={"campus_power_capacity_mw": 50}, area_context={"campus_hectares": 4.3}),
    site("DEN01", "Copenhagen metro site", "DK", "Ballerup / Greater Copenhagen", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/denmark-data-centers/copenhagen-metro-site/", power_context={"campus_power_capacity_mw": 30}, area_context={"campus_size_sqm": 27728}, timing_context={"first_phase_went_live": "2025_Q4", "report_footnote_operational": "2026_Q1"}),
    site("DEN02", "Varde mega site", "DK", "Varde / Olgod", "mega", "development_or_announced", "https://www.atnorth.com/nordic-data-centers/denmark-data-centers/varde-mega-site/", power_context={"initial_capacity_mw": 250, "full_build_marketed_capacity_mw": 500}, area_context={"campus_hectares": 171}),
    site("SWE01", "Stockholm metro site", "SE", "Kista / Stockholm", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/sweden-data-centers/stockholm-metro-site/", power_context={"site_power_capacity_mw": 12}, area_context={"facility_size_sqm": 6400}),
    site("SWE02", "Stockholm metro site", "SE", "Akalla / Stockholm", "metro", "development_or_announced", "https://www.atnorth.com/nordic-data-centers/sweden-data-centers/stockholm-swe02/", power_context={"site_power_capacity_mw": 30}, area_context={"facility_size_sqm": 15000, "plot_hectares": 1.5}, timing_context={"scheduled_go_live": "2027_Q4", "directory_card_visibility": "navigation_link_but_not_current_main_card_grid"}),
    site("SWE04", "Solleftea mega site", "SE", "Solleftea", "mega", "development_or_announced", "https://www.atnorth.com/nordic-data-centers/sweden-data-centers/solleftea-swe04/", power_context={"site_power_capacity_mw": 300}, area_context={"site_hectares": 50}),
    site("FIN01", "Helsinki metro site", "FI", "Helsinki", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/finland-data-centers/helsinki-metro-site-01/", power_context={"power_capacity_mw": 1.6}, area_context={"white_space_sqm": 450}),
    site("FIN02", "Helsinki metro site", "FI", "Espoo / Helsinki", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/finland-data-centers/helsinki-metro-site-02/", power_context={"campus_power_capacity_mw": 40}, area_context={"campus_size_sqm": 20048}),
    site("FIN03", "Helsinki metro site", "FI", "Espoo / Helsinki", "metro", "operating", "https://www.atnorth.com/nordic-data-centers/finland-data-centers/helsinki-metro-site-03/", power_context={"power_capacity_mw": 1.6}, area_context={"white_space_sqm": 450}),
    site("FIN04", "Myllykoski mega site", "FI", "Myllykoski / Kouvola", "mega", "development_or_announced", "https://www.atnorth.com/nordic-data-centers/finland-data-centers/myllykoski-mega-site/", power_context={"campus_power_capacity_mw": 430, "additional_path_to_power": "several_hundred_MW"}, area_context={"campus_hectares": 45}, timing_context={"page_ready_target": "2026_H1", "current_conflict": "2026_02_and_2026_06_sources_still_describe_as_under_development"}),
    site("NOR01", "Haugaland mega site", "NO", "Haugaland / Tysvaer", "mega", "development_or_announced", "https://www.atnorth.com/nordic-data-centers/norway-data-centers/haugaland-nor01/", power_context={"initial_phase_mw": 120, "planned_ramp_mw": 350, "power_availability_projected": 2028}, area_context={"site_hectares": 36}, grid_context={"planned_substations": ["Statnett", "Fagne"]}),
]


ICE02_OSM_IDS = [
    "osm_way_1223207434", "osm_way_588514774", "osm_way_588514773",
    "osm_way_588514772", "osm_way_802114425", "osm_way_802114424",
    "osm_way_1463708635", "osm_way_802114419", "osm_way_802114420",
    "osm_way_802114421", "osm_way_802114422", "osm_way_802114423",
    "osm_way_1223207435", "osm_way_1463708636", "osm_way_1463708637",
]
OSM_TO_SITE = {object_id: "ICE02" for object_id in ICE02_OSM_IDS} | {
    "osm_node_10062286674": "ICE01"
}


PORTFOLIO_CONTEXT = {
    "current_operating_data_centers": 8,
    "current_official_site_codes": 13,
    "secured_power_gw": 1,
    "scope_boundary": "Eight operating sites, thirteen navigation codes, secured power and site-page design MW are different scopes.",
    "accelerators": {
        "atNorth_owned_GPU_inventory": "undisclosed",
        "ICE02_Crusoe": {"contracted_capacity_mw": 57, "platforms": ["NVIDIA_GB200_NVL72", "NVIDIA_Blackwell", "NVIDIA_Hopper"], "exact_GPU_count": "undisclosed"},
        "ICE02_Opera": {"platform": "NVIDIA_DGX_H100_SuperPOD", "GPU_count": "hundreds_not_exact"},
        "SWE01_6G_AI_Sweden": {"current_GPU_count": 240, "future_allocated_GPU_count": 2500, "initial_IT_load_kw": 500, "models_announced": ["NVIDIA_H200", "NVIDIA_GB200"]},
        "ownership_boundary": "Customer deployments do not establish an atNorth-owned portfolio GPU total.",
    },
    "power_cooling_and_environment_2025": {
        "weighted_average_PUE": 1.21,
        "renewable_energy_share_percent": 99.1,
        "total_energy_MWh_reported_conflict": [256163, 256193],
        "water_consumption_m3": 9600,
        "WUE": "not_meaningfully_reportable_due_to_metering_challenges",
        "all_operational_sites_closed_loop_water_cooling": True,
        "several_buildings_air_only": True,
        "sites_with_adiabatic_supplementary_or_emergency_cooling": 2,
        "direct_liquid_cooling": True,
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        if (row.get("operator") or "").casefold() == "atnorth" or "atnorth" in (row.get("name") or "").casefold():
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(SITE_RECORDS) == 13
    assert len({row["site_code"] for row in SITE_RECORDS}) == 13
    assert len(candidates) == 16, [row["id"] for row in candidates]
    assert set(OSM_TO_SITE) == {row["id"] for row in candidates}

    mapped: dict[str, list[dict]] = {}
    for object_id, site_code in OSM_TO_SITE.items():
        source = osm[object_id]
        mapped.setdefault(site_code, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": "OSM building, campus outline or point; not provider-certified lifecycle, capacity, ownership, tenant or revenue evidence.",
        })

    common_sources = [DIRECTORY_URL, SUSTAINABILITY_URL, ACQUISITION_URL, NORWAY_RELEASE_URL, CRUSOE_URL, SWE_AI_URL, OPERA_URL]
    records = []
    for position, source in enumerate(SITE_RECORDS, start=1):
        records.append({
            "id": f"atnorth_{source['site_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterSite",
            "source_order": position,
            "operator": "atNorth",
            "record_granularity": "provider_site_code_not_physical_building",
            **source,
            "marketed_PUE_up_to": 1.2,
            "osm_map_evidence": sorted(mapped.get(source["site_code"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source["location_url"], *common_sources])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    lifecycles = Counter(row["lifecycle_as_of_2026_07_19"] for row in records)
    countries = Counter(row["country_code"] for row in records)
    osm_counts = Counter()
    for row in records:
        osm_counts[row["site_code"]] = len(row["osm_map_evidence"])
    return {
        "registry": "atNorth official Nordic site-code and OSM crosswalk",
        "official_site_code_records": len(records),
        "lifecycle_counts": dict(sorted(lifecycles.items())),
        "country_counts": dict(sorted(countries.items())),
        "current_owner_announced_operating_data_centers": 8,
        "related_osm_objects": len(candidates),
        "osm_objects_by_site": dict(sorted(osm_counts.items())),
        "site_codes_with_osm_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum operating, planned, first-phase, full-build, secured-power, IT-load, rack-density or OSM-object measures.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/atnorth_official_site_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/atnorth_official_site_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    records, candidates = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
