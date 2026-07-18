#!/usr/bin/env python3
"""Build CDC Data Centres' official ANZ facility-code registry.

CDC publishes building codes on a dated investor map, campus-level capacity on
location pages, and portfolio-level operating/construction/pipeline metrics in
Infratil reporting.  Those scopes are deliberately kept separate here.  The
builder also crosswalks public OSM objects without treating a footprint, tenant
label, campus, or provider building code as interchangeable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


INVESTOR_DAY_URL = "https://infratil.com/news/cdc-investor-presentation-and-guidance-update/cdc-infratil-investor-day-presentation/"
FY26_METRICS_URL = "https://infratil.com/news/infratil-full-year-results-for-the-year-ended-31-march-2026/detailed-financial-information-operating-metrics-march-2026/"
SUSTAINABILITY_URL = "https://www.cdc.com.au/media/dugnsyfr/cdc-2026-sustainability-report_aasb-s2.pdf"
CONTRACT_URL = "https://www.cdc.com.au/resources/news/cdc-signs-555mw-data-centre-contract-with-us-customer/"
WATER_URL = "https://www.cdc.com.au/resources/insights-and-reports/saving-water-on-an-epic-scale/"
SCHNEIDER_URL = "https://www.cdc.com.au/resources/insights-and-reports/data-centres-part-of-the-energy-solution-says-schneider-electric/"
DGX_URL = "https://www.cdc.com.au/resources/news/cdc-achieves-nvidia-dgx-ready-data-center-certification-across-australia-and-new-zealand/"

LOCATION_URLS = {
    "Canberra": "https://www.cdc.com.au/locations/canberra/",
    "Sydney": "https://www.cdc.com.au/locations/sydney/",
    "Melbourne": "https://www.cdc.com.au/locations/melbourne/",
    "Auckland": "https://www.cdc.com.au/locations/auckland/",
    "Perth": "https://www.cdc.com.au/locations/perth/",
}


def facility(
    site_id: str,
    region: str,
    campus: str,
    country_code: str,
    state_or_region: str,
    dated_lifecycle: str,
    **extra: object,
) -> dict:
    return {
        "site_id": site_id,
        "region": region,
        "campus": campus,
        "country_code": country_code,
        "state_or_region": state_or_region,
        "dated_investor_day_lifecycle_as_of_2026_03_26": dated_lifecycle,
        "location_page_url": LOCATION_URLS[region],
        **extra,
    }


FACILITIES = [
    facility("HU1", "Canberra", "Hume One", "AU", "ACT", "operational"),
    facility("HU2", "Canberra", "Hume One", "AU", "ACT", "operational"),
    facility("HU3", "Canberra", "Hume One", "AU", "ACT", "operational"),
    facility("HU4", "Canberra", "Hume Two", "AU", "ACT", "operational"),
    facility("HU5", "Canberra", "Hume Two", "AU", "ACT", "operational"),
    facility("HU6", "Canberra", "Hume", "AU", "ACT", "under_construction"),
    facility("FY1", "Canberra", "Fyshwick", "AU", "ACT", "operational"),
    facility("FY2", "Canberra", "Fyshwick", "AU", "ACT", "operational"),
    facility("BE1", "Canberra", "Beard", "AU", "ACT", "operational", status_note="Dated investor material says work was completed; the current location page still calls Beard under construction."),
    facility("EC1", "Sydney", "Eastern Creek", "AU", "NSW", "operational"),
    facility("EC2", "Sydney", "Eastern Creek", "AU", "NSW", "operational"),
    facility("EC3", "Sydney", "Eastern Creek", "AU", "NSW", "operational"),
    facility("EC4", "Sydney", "Eastern Creek", "AU", "NSW", "operational"),
    facility("EC5", "Sydney", "Eastern Creek", "AU", "NSW", "under_construction"),
    facility("EC6", "Sydney", "Eastern Creek", "AU", "NSW", "under_construction"),
    facility("MP1", "Sydney", "Marsden Park", "AU", "NSW", "operational", status_note="Dated investor material says the first of six buildings was complete; the current location page describes the campus as in early construction."),
    facility("MP2", "Sydney", "Marsden Park", "AU", "NSW", "future_development_land_secured"),
    facility("MP3", "Sydney", "Marsden Park", "AU", "NSW", "future_development_land_secured"),
    facility("MP4", "Sydney", "Marsden Park", "AU", "NSW", "future_development_land_secured"),
    facility("MP5", "Sydney", "Marsden Park", "AU", "NSW", "future_development_land_secured"),
    facility("MP6", "Sydney", "Marsden Park", "AU", "NSW", "future_development_land_secured"),
    facility("BK1", "Melbourne", "Brooklyn", "AU", "VIC", "operational"),
    facility("BK2", "Melbourne", "Brooklyn", "AU", "VIC", "operational", status_note="Dated investor material says work was completed; the current location page says only BK1 is operational."),
    facility("LV1", "Melbourne", "Laverton", "AU", "VIC", "under_construction"),
    facility("LV2", "Melbourne", "Laverton", "AU", "VIC", "future_development_land_secured"),
    facility("SD1", "Auckland", "Silverdale", "NZ", "Auckland", "operational"),
    facility("SD2", "Auckland", "Silverdale", "NZ", "Auckland", "future_development_land_secured"),
    facility("HV1", "Auckland", "Hobsonville One", "NZ", "Auckland", "operational"),
    facility("HV2", "Auckland", "Hobsonville Two", "NZ", "Auckland", "operational"),
    facility("MA1", "Perth", "Maddington", "AU", "WA", "under_construction", status_note="Dated investor material says construction was underway; the current location page uses future-oriented language."),
]


CAMPUS_CAPACITY_CONTEXT = {
    "Hume One": {"published_mw": 21, "qualifier": "current_operating_capacity"},
    "Hume Two": {"published_mw": 51, "qualifier": "current_operating_capacity"},
    "Fyshwick": {"published_mw": 45, "qualifier": "current_operating_capacity"},
    "Beard": {"published_mw": 39, "qualifier": "location_page_total_capacity_with_status_conflict"},
    "Eastern Creek": {"published_mw_more_than": 200, "qualifier": "campus_capacity_not_current_operating_load"},
    "Marsden Park": {"published_planned_mw_more_than": 504, "scalability_toward_mw": 1000, "qualifier": "planned_and_scalability_not_current_load"},
    "Brooklyn": {"published_completion_mw_more_than": 350, "qualifier": "upon_completion_not_current_load"},
    "Laverton": {"published_completion_mw_more_than": 400, "qualifier": "upon_completion_not_current_load"},
    "Silverdale": {"published_operating_mw": 22, "published_growth_mw_more_than": 60, "qualifier": "operating_and_future_values_kept_separate"},
    "Hobsonville One": {"published_operating_mw": 22, "qualifier": "current_operating_capacity"},
    "Hobsonville Two": {"published_operating_mw": 54, "qualifier": "current_operating_capacity"},
    "Maddington": {"published_completion_mw_more_than": 200, "qualifier": "future_high_density_capacity_not_current_load"},
}


REGION_CAPACITY_CONTEXT = {
    "Canberra": {"location_page_capacity_mw_more_than": 250},
    "Sydney": {"location_page_capacity_mw_more_than": 1000},
    "Melbourne": {"location_page_capacity_mw_more_than": 780},
    "Auckland": {"location_page_capacity_mw_more_than": 220},
    "Perth": {"location_page_future_capacity_mw_more_than": 200},
}


OSM_TO_SITE = {
    "osm_way_1010500714": "HU1",
    "osm_way_59807473": "HU2",
    "osm_way_1010500713": "HU3",
    "osm_way_1010496550": "HU4",
    "osm_way_1060498365": "HU5",
    "osm_way_971044866": "FY1",
    "osm_way_971044867": "FY2",
    "osm_way_803869403": "EC1",
    "osm_way_977470049": "EC2",
    "osm_way_966897260": "EC3",
    "osm_way_977470047": "EC4",
    "osm_way_977470046": "EC5",
    "osm_way_1479628967": "EC6",
    "osm_way_1087109147": "HV1",
    "osm_way_1358308781": "HV1",
    "osm_way_1002516540": "SD1",
}


OSM_NOTES = {
    "osm_way_1358308781": "OSM calls this HV1A; CDC's reviewed investor map publishes HV1, not a separate HV1A building code.",
    "osm_way_1002516540": "OSM names Microsoft as operator and CDC as owner; the Silverdale location supports an SD1 crosswalk but does not prove Microsoft tenancy status, building scope, or current contract terms.",
}


PORTFOLIO_INFRASTRUCTURE = {
    "electrical_and_generation": {
        "standby_generation_fuel": "diesel",
        "standby_generator_use": "emergency_response_testing_and_maintenance",
        "sustainable_fuel_ready_generator_infrastructure": True,
        "confirmed_supplier": "Schneider Electric",
        "confirmed_supplier_scope": [
            "equipment powering CDC closed-loop system",
            "in-row cooling integrated with CDC closed-loop chilled water",
            "energy management and automation portfolio",
        ],
        "undisclosed": "utility feeds, substations, transformers, switchgear, UPS, batteries, generator models, quantities, ratings, redundancy and site allocation",
    },
    "cooling_and_water": {
        "architecture": "closed-loop cooling across CDC-built facilities with liquid-cooling support",
        "primary_cooling_water_use": "initial fill followed by continuous recirculation",
        "portfolio_PUE_FY2026": 1.38,
        "portfolio_WUE_liters_per_kwh_FY2026_less_than": 0.02,
        "metric_scope": "operational sites at or above 50 percent utilization",
        "undisclosed": "site-level chiller, CDU, heat-rejection equipment, live liquid-cooled MW, PUE, WUE and absolute water",
    },
    "gpu_inventory": {
        "physical_model_count_owner_delivery_state_site_allocation_utilization_power_draw_revenue_and_margin": "undisclosed",
        "hosting_context": ["NVIDIA DGX-Ready certification", "high-density air and liquid cooling", "customer-deployed ICT equipment"],
        "boundary": "Certification, rack-density illustrations and linked customer AI projects do not prove that CDC owns GPUs or establish a live per-site accelerator inventory.",
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
        if row.get("operator") in {"CDC", "Canberra Data Centres"} or row.get("owner") == "CDC":
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(candidates) == 17, len(candidates)
    assert set(OSM_TO_SITE).issubset(osm), sorted(set(OSM_TO_SITE) - set(osm))
    site_ids = {row["site_id"] for row in FACILITIES}
    assert len(FACILITIES) == 30
    assert len(site_ids) == 30
    assert set(OSM_TO_SITE.values()).issubset(site_ids)

    site_osm: dict[str, list[dict]] = {}
    for object_id, site_id in OSM_TO_SITE.items():
        source = osm[object_id]
        site_osm.setdefault(site_id, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "osm_owner": source.get("owner"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "identity_note": OSM_NOTES.get(object_id),
            "boundary": "Public map object or footprint, not provider-certified address, ownership, lifecycle, operating status, MW, tenant or legal asset count.",
        })

    common_sources = [INVESTOR_DAY_URL, FY26_METRICS_URL, SUSTAINABILITY_URL, CONTRACT_URL, WATER_URL, SCHNEIDER_URL, DGX_URL]
    records = []
    for position, source in enumerate(FACILITIES, start=1):
        records.append({
            "id": f"cdc_{source['site_id'].lower()}",
            "object_type": "ProviderPublishedDataCenterFacilityCode",
            "source_order": position,
            "operator": "CDC_Data_Centres",
            **source,
            "record_granularity": "provider_building_code_from_dated_investor_map",
            "campus_capacity_context": CAMPUS_CAPACITY_CONTEXT.get(source["campus"]),
            "region_capacity_context": REGION_CAPACITY_CONTEXT[source["region"]],
            "capacity_boundary": "Campus and region MW are repeated context, not allocated to this building code; never sum registry rows. Portfolio operating, construction and future-build MW use a separate reporting boundary.",
            "portfolio_infrastructure_context": PORTFOLIO_INFRASTRUCTURE,
            "osm_map_evidence": site_osm.get(source["site_id"], []),
            "source_urls": list(dict.fromkeys([source["location_page_url"], *common_sources])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    lifecycles = Counter(row["dated_investor_day_lifecycle_as_of_2026_03_26"] for row in records)
    mapped_ids = set(OSM_TO_SITE)
    unresolved = [row for row in candidates if row["id"] not in mapped_ids]
    assert [row["id"] for row in unresolved] == ["osm_way_263915226"]
    assert unresolved[0].get("name") == "CDC Laverton"
    assert lifecycles == Counter({"operational": 18, "future_development_land_secured": 7, "under_construction": 5})
    return {
        "registry": "CDC Data Centres official ANZ facility-code registry",
        "accessed_on": accessed_on,
        "facility_code_records": len(records),
        "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "region_counts": dict(sorted(Counter(row["region"] for row in records).items())),
        "campus_label_count_in_registry": len({(row["region"], row["campus"]) for row in records}),
        "current_location_page_marketed_campus_cards": 12,
        "campus_count_boundary": "HU6 is shown under Hume on the dated map but is not allocated to Hume One or Hume Two; the registry therefore has 13 campus labels while current location pages market 12 campus cards. Neither is a physical-building count.",
        "dated_investor_day_lifecycle_counts": dict(sorted(lifecycles.items())),
        "dated_status_boundary": "The 18 operating, 5 construction and 7 future facility-code reconstruction follows the 26 March 2026 map, its legend, and completion notes; it is not a current provider status table.",
        "FY2026_portfolio_metrics_as_of_2026_03_31": {
            "operating_data_centers": 19,
            "under_construction_data_centers": 6,
            "operating_capacity_mw": 671,
            "under_construction_capacity_mw": 572,
            "development_pipeline_mw": 1663,
            "total_capacity_pipeline_mw": 2906,
            "contracted_ICT_capacity_mw": 220,
            "rack_utilization_percent": 62,
            "boundary": "The reporting table does not allocate the one additional operating and one additional construction data center versus the dated map to facility codes, so this registry does not guess the identities.",
        },
        "later_contract_update": {
            "new_contract_mw": 555,
            "total_contracted_capacity_mw_more_than": 1000,
            "delivery_window": "FY2028_to_FY2029",
            "boundary": "Contracted capacity is not current operating, energized, utilized or billed load and is not allocated to named campuses in the release.",
        },
        "osm_candidate_objects": len(candidates),
        "osm_operator_labeled_objects": sum(row.get("operator") in {"CDC", "Canberra Data Centres"} for row in candidates),
        "osm_owner_only_or_other_operator_objects": sum(row.get("operator") not in {"CDC", "Canberra Data Centres"} for row in candidates),
        "osm_objects_crosswalked_to_facility_codes": len(mapped_ids),
        "osm_objects_crosswalked_to_unique_facility_codes": len(set(OSM_TO_SITE.values())),
        "osm_campus_only_unallocated_objects": [{
            "osm_object_id": unresolved[0]["id"],
            "osm_name": unresolved[0].get("name"),
            "campus": "Laverton",
            "reason": "The footprint is campus-labeled and cannot be assigned to LV1 or LV2 without inventing a building identity.",
            "source_url": unresolved[0]["source_url"],
        }],
        "current_page_conflicts_preserved": [
            "Canberra page calls BE1 under construction while dated investor material says work was completed.",
            "Sydney page calls Marsden Park early construction while dated investor material says the first of six buildings was complete.",
            "Melbourne page calls only BK1 operational while dated investor material says work at BK2 was completed.",
            "Perth page uses future-oriented language while dated investor material says MA1 construction was underway.",
        ],
        "installed_GPU_inventory": "undisclosed",
        "site_level_power_and_cooling_bill_of_materials": "undisclosed",
        "no_row_capacity_sum": True,
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
    registry_path = args.output_dir / "cdc_official_facility_registry.jsonl"
    summary_path = args.output_dir / "cdc_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
