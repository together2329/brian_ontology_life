#!/usr/bin/env python3
"""Build Switch's official U.S. campus registry and OSM crosswalk.

Switch publishes current campus pages, a current owner publishes an aggregate
operating-data-center count, and selected releases/spec sheets disclose named
building or expansion facts.  Those are different granularities.  This builder
therefore keeps campus, operating-asset, named-facility, OSM-footprint and future
full-build claims separate rather than inventing a complete building roster.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


IFM_PORTFOLIO_URL = "https://www.ifminvestors.com/capabilities/infrastructure/our-portfolio/switch-inc/"
IFM_CASE_STUDY_URL = "https://www.ifminvestors.com/en-gb/capabilities/infrastructure/hub/switch-inc-a-case-study/"
SWITCH_LOCATIONS_URL = "https://www.switch.com/locations/"
AI_FACTORY_URL = "https://www.switch.com/ai-factories/"
POWER_URL = "https://www.switch.com/sustainable-data-centers/power/"
SCHNEIDER_URL = "https://www.switch.com/schneider-electric-and-switch-expand-partnership-with-1-9-billion-supply-capacity-agreement-to-power-ai-factories/"
COREWEAVE_URL = "https://www.switch.com/coreweave-deploys-industry-first-nvidia-gb300-nvl72-in-switchs-ai-factory-solution/"
FINANCING_URL = "https://www.switch.com/switch-expands-corporate-revolving-credit-and-letter-of-credit-facilities-to-nearly-10-billion/"
TAKE_PRIVATE_URL = "https://ir.digitalbridge.com/news-releases/news-release-details/digitalbridge-and-ifm-investors-complete-11-billion-take-private/"
SEC_2021_URL = "https://www.sec.gov/Archives/edgar/data/1710583/000171058322000009/swch-20211231.htm"


def campus(
    campus_id: str,
    marketed_name: str,
    prime_name: str,
    city: str,
    state: str,
    lifecycle: str,
    location_url: str,
    **extra: object,
) -> dict:
    return {
        "campus_id": campus_id,
        "marketed_name": marketed_name,
        "prime_name": prime_name,
        "city": city,
        "state": state,
        "country_code": "US",
        "lifecycle_as_of_2026_07_19": lifecycle,
        "location_url": location_url,
        **extra,
    }


CAMPUS_RECORDS = [
    campus(
        "core_las_vegas",
        "Switch Las Vegas",
        "The Core Campus",
        "Las Vegas",
        "NV",
        "operating_with_active_expansion",
        "https://www.switch.com/las-vegas/",
        capacity_context={
            "full_completion_power_mw_up_to": 495,
            "metric_boundary": "Current campus-page full-build design value, not current energized, leased, utilized or billed IT load.",
        },
        named_facility_evidence={
            "Las_Vegas_10": {"area_sqft_nearly": 350000, "power_mw_up_to": 40, "opened_release_url": "https://www.switch.com/switch-core-campus-opens-las-vegas-10-data-center/"},
            "current_about_page_image_labels": ["Las_Vegas_7", "Las_Vegas_8", "Las_Vegas_9"],
            "IFM_case_study_image_label": "Las_Vegas_12",
            "boundary": "Examples do not constitute a complete current building roster.",
        },
    ),
    campus(
        "citadel_tahoe_reno",
        "Switch Tahoe Reno",
        "The Citadel Campus",
        "McCarran / Tahoe Reno",
        "NV",
        "operating_with_active_expansion",
        "https://www.switch.com/tahoe-reno/",
        capacity_context={
            "current_page": "multi_gigawatt_upon_completion",
            "dated_Tahoe_Reno_02_sheet_full_completion_power_mw_up_to": 2000,
            "dated_Tahoe_Reno_02_sheet_full_completion_area_sqft_more_than": 12000000,
            "metric_boundary": "Full-build projection is not current operating capacity or load.",
        },
        named_facility_evidence={
            "Tahoe_Reno_01": {"area_sqft_up_to": 1300000, "power_mw_up_to": 130, "source_url": "https://www.switch.com/switch-tahoe-reno-data-center-now-open/"},
            "Tahoe_Reno_02": {"area_sqft_more_than": 522000, "power_mw_up_to": 55, "published_opening": "2024-05", "source_url": "https://switchdotcom.s3-sites.data.switch.com/media/one-sheets/COLO/Tahoe-Reno-2.pdf"},
            "boundary": "Later OSM labels Tahoe Reno 3-5 are campus map evidence, not provider-published lifecycle or capacity records.",
        },
    ),
    campus(
        "pyramid_grand_rapids",
        "Switch Grand Rapids",
        "The Pyramid Campus",
        "Grand Rapids",
        "MI",
        "operating_with_active_expansion",
        "https://www.switch.com/grand-rapids/",
        capacity_context={
            "current_full_completion_power_mw_up_to": 237,
            "historical_2017_full_completion_power_mw_up_to": 320,
            "historical_2017_full_completion_area_sqft_up_to": 1800000,
            "conflict_boundary": "The current page supersedes the older marketing power headline for present research; neither value is current live load.",
        },
        named_facility_evidence={
            "Grand_Rapids_01": {"published_area_sqft": 471248, "source_url": "https://www.switch.com/switch-grand-rapids-now-open-largest-advanced-data-center-campus-eastern-u-s/"},
            "boundary": "The reviewed official pages do not publish a complete current facility-code roster.",
        },
    ),
    campus(
        "keep_atlanta",
        "Switch Atlanta",
        "The Keep Campus",
        "Lithia Springs / Atlanta",
        "GA",
        "operating_with_active_expansion",
        "https://www.switch.com/atlanta/",
        capacity_context={
            "original_campus_full_completion_power_mw_up_to": 150,
            "expansion_campus_acres_more_than": 2000,
            "expansion_power": "multi_gigawatt_upon_completion",
            "metric_boundary": "Original-campus and expansion full-build claims are not current energized, leased, utilized or billed load.",
        },
        named_facility_evidence={
            "current_page_labels": ["Atlanta_01", "Keep_2.0_expansion"],
            "boundary": "Video labels do not disclose a complete building roster or commissioning table.",
        },
    ),
    campus(
        "rock_texas",
        "Switch Austin / Houston",
        "The Rock Campus and legacy Data Foundry locations",
        "Round Rock / Austin / Houston",
        "TX",
        "operating_with_active_expansion",
        "https://www.switch.com/austin/",
        capacity_context={
            "dated_2021_ecosystem_full_completion_power_mw_up_to": 185,
            "dated_2021_ecosystem_full_completion_area_sqft_more_than": 2000000,
            "legacy_Data_Foundry_four_operating_facilities_acquisition_scope": True,
            "legacy_facilities_available_power_as_of_2021_mw_up_to": 22,
            "metric_boundary": "Dated acquisition and full-build scopes are not a current campus capacity or utilization table.",
        },
        named_facility_evidence={
            "legacy_Data_Foundry_spec_sheets": ["Austin_1", "Texas_1", "Texas_2", "Houston_2"],
            "source_urls": [
                "https://switchdotcom.s3-sites.data.switch.com/df/media/austin-1.pdf",
                "https://switchdotcom.s3-sites.data.switch.com/df/media/texas-1.pdf",
                "https://switchdotcom.s3-sites.data.switch.com/df/media/texas-2.pdf",
                "https://switchdotcom.s3-sites.data.switch.com/df/media/houston-2.pdf",
            ],
            "boundary": "Legacy sheets are detailed equipment snapshots, not proof of unchanged 2026 configuration, lifecycle or ownership boundary.",
        },
    ),
    campus(
        "beaver_county_pennsylvania",
        "Switch Beaver County",
        "Greater Pittsburgh planned campus",
        "Big Beaver Borough",
        "PA",
        "announced_planned",
        "https://www.switch.com/switch-announces-new-data-center-campus-in-beaver-county-pennsylvania/",
        capacity_context={
            "site_acres": 382,
            "power_mw": "undisclosed",
            "area_sqft": "undisclosed",
            "metric_boundary": "Announced land is not an operating facility, powered shell, contracted MW or construction completion.",
        },
    ),
]


OSM_TO_CAMPUS = {
    "osm_way_1263819877": "core_las_vegas",
    "osm_way_617194689": "core_las_vegas",
    "osm_way_1421212901": "core_las_vegas",
    "osm_way_1017460713": "core_las_vegas",
    "osm_way_1017460715": "core_las_vegas",
    "osm_way_172739953": "core_las_vegas",
    "osm_way_585998677": "core_las_vegas",
    "osm_way_585998678": "core_las_vegas",
    "osm_way_172739950": "core_las_vegas",
    "osm_way_1017048670": "core_las_vegas",
    "osm_way_984796364": "core_las_vegas",
    "osm_way_1314355599": "core_las_vegas",
    "osm_way_1116775094": "citadel_tahoe_reno",
    "osm_way_1116775095": "citadel_tahoe_reno",
    "osm_way_1320683840": "citadel_tahoe_reno",
    "osm_way_1494498031": "citadel_tahoe_reno",
    "osm_way_1494498032": "citadel_tahoe_reno",
    "osm_way_975064004": "keep_atlanta",
    "osm_way_1493169641": "rock_texas",
}


PORTFOLIO_INFRASTRUCTURE = {
    "current_owner_published_operating_data_centers": 20,
    "operating_count_scope": "IFM case-study aggregate; not allocated to current facility codes or street addresses.",
    "AI_and_GPU": {
        "confirmed_hosted_milestones": ["CoreWeave_NVIDIA_GB200_NVL72", "CoreWeave_NVIDIA_GB300_NVL72"],
        "hardware_owner_and_integrator": ["CoreWeave", "Dell_Technologies", "NVIDIA"],
        "exact_system_count_GPU_count_models_by_site_owner_utilization_power_draw_revenue_and_margin": "undisclosed",
        "boundary": "A named NVL72 platform and an industry-first bring-up establish hosted architecture, not a Switch-owned fleet total or a complete customer inventory.",
    },
    "power_and_cooling": {
        "EVO_density_kW_per_rack_from_to": [20, 2000],
        "fluidic_pathways": 5,
        "cooling_modes": ["liquid_to_air", "liquid_to_chip", "hybrid_air_and_liquid"],
        "current_marketed_PUE": 1.18,
        "renewable_energy_claim": "100_percent_since_2016",
        "confirmed_2025_supplier": "Schneider_Electric",
        "confirmed_2025_supply_capacity_agreement_usd_billion": 1.9,
        "confirmed_2025_equipment": ["prefabricated_power_modules", "Uniflair_oil_free_variable_speed_centrifugal_chillers", "integrated_free_cooling"],
        "site_level_utility_feeds_substations_transformers_switchgear_UPS_batteries_generators_fuel_chillers_CDU_counts_ratings_and_as_built_topology": "mostly_undisclosed_outside_legacy_Data_Foundry_sheets",
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def is_us(row: dict) -> bool:
    return any(country.get("iso2") == "US" for country in row.get("country_candidates", []))


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        name = row.get("name", "")
        if is_us(row) and (row.get("operator") == "Switch" or name.startswith("Switch ")):
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(candidates) == 19, [row["id"] for row in candidates]
    assert set(OSM_TO_CAMPUS) == {row["id"] for row in candidates}
    assert len(CAMPUS_RECORDS) == 6
    assert len({row["campus_id"] for row in CAMPUS_RECORDS}) == 6

    mapped: dict[str, list[dict]] = {}
    for object_id, campus_id in OSM_TO_CAMPUS.items():
        source = osm[object_id]
        mapped.setdefault(campus_id, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": "OSM building or point evidence; not a provider-certified address, lifecycle, operating-asset count, MW value, tenant or legal ownership record.",
        })

    common_sources = [
        SWITCH_LOCATIONS_URL,
        IFM_PORTFOLIO_URL,
        IFM_CASE_STUDY_URL,
        AI_FACTORY_URL,
        POWER_URL,
        SCHNEIDER_URL,
        COREWEAVE_URL,
        FINANCING_URL,
        TAKE_PRIVATE_URL,
        SEC_2021_URL,
    ]
    records = []
    for position, source in enumerate(CAMPUS_RECORDS, start=1):
        records.append({
            "id": f"switch_{source['campus_id']}",
            "object_type": "ProviderPublishedDataCenterCampus",
            "source_order": position,
            "operator": "Switch_US",
            **source,
            "record_granularity": "provider_campus_or_announced_campus_not_physical_building",
            "portfolio_infrastructure_context": PORTFOLIO_INFRASTRUCTURE,
            "osm_map_evidence": mapped.get(source["campus_id"], []),
            "source_urls": list(dict.fromkeys([source["location_url"], *common_sources])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    lifecycle_counts = Counter(row["lifecycle_as_of_2026_07_19"] for row in records)
    operator_tagged = [row for row in candidates if row.get("operator") == "Switch"]
    name_only = [row for row in candidates if row.get("operator") != "Switch"]
    mapped_counts = Counter(OSM_TO_CAMPUS.values())
    assert len(operator_tagged) == 16
    assert len(name_only) == 3
    assert lifecycle_counts == Counter({"operating_with_active_expansion": 5, "announced_planned": 1})
    return {
        "registry": "Switch official U.S. campus registry",
        "accessed_on": accessed_on,
        "campus_records": len(records),
        "current_operating_and_expanding_campuses": 5,
        "announced_planned_campuses": 1,
        "lifecycle_counts": dict(sorted(lifecycle_counts.items())),
        "current_owner_published_operating_data_centers": 20,
        "operating_count_boundary": "IFM's current aggregate is not allocated to the five campuses or a complete public building-code roster.",
        "related_US_OSM_objects": len(candidates),
        "OSM_operator_tagged_objects": len(operator_tagged),
        "OSM_name_only_objects": len(name_only),
        "OSM_objects_by_campus": dict(sorted(mapped_counts.items())),
        "OSM_missing_current_markets": ["Grand_Rapids"],
        "OSM_scope_boundary": "Nineteen related OSM objects cannot be compared as nineteen of twenty operating data centers: OSM is a footprint/point map, omits Grand Rapids and legacy Texas facilities, and can contain multiple objects for one provider facility or campus.",
        "named_facility_roster_status": "partial_only",
        "capacity_checksum_prohibited": True,
        "capacity_boundary": "Current, dated, campus, named-building and full-completion values are retained separately and are never summed as current live load.",
        "exact_Switch_owned_or_customer_GPU_inventory": "undisclosed",
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records, candidates = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "switch_official_campus_registry.jsonl"
    summary_path = args.output_dir / "switch_official_campus_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
