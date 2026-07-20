#!/usr/bin/env python3
"""Build KDDI's current Japan service-label and AI-campus registry.

The KDDI WVS product page publishes 22 KDDI/Telehouse labels where its
traffic-free feature is available.  That table is a product-availability
roster, not KDDI's complete domestic physical-building census: the broader
data-center page also shows Toyama, and one Tama label can aggregate multiple
facilities.  Osaka Sakai and Tama 5-2nd are therefore retained as separately
sourced AI-campus lifecycle records rather than silently added to the 22-row
table as equivalent service sites.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


WVS_URL = "https://biz.kddi.com/service/kddi-wvs/function/data-center-list/"
DATA_CENTER_URL = "https://biz.kddi.com/english/service/data-center/"
SAKAI_URL = "https://newsroom.kddi.com/english/news/detail/kddi_nr-916_4323.html"
GPU_CLOUD_URL = "https://newsroom.kddi.com/news/detail/kddi_nr-796_4171.html"
SAKAI_2024_URL = "https://newsroom.kddi.com/english/news/detail/kddi_nr_s-9_3387.html"
TAMA_5_2_URL = "https://biz.kddi.com/topics/2025/news/022/"
RENEWABLE_URL = "https://news.kddi.com/kddi/corporate/csr-topic/2026/04/30/7739.html"


def service(code: str, market: str, label: str, brand: str = "Telehouse") -> dict:
    return {
        "record_code": code,
        "market": market,
        "provider_label": label,
        "brand": brand,
        "record_class": "current_KDDI_WVS_traffic_free_product_availability_label",
        "lifecycle_as_of_2026_07_19": "current_product_service_label_operating_status_not_individually_reverified",
        "source_urls": [WVS_URL, DATA_CENTER_URL],
    }


RECORDS = [
    service("SAPPORO", "Sapporo", "TELEHOUSE SAPPORO"),
    service("SENDAI", "Sendai", "TELEHOUSE SENDAI"),
    service("OYAMA", "Oyama", "TELEHOUSE OYAMA"),
    service("TOKYO_SHINJUKU", "Tokyo", "TELEHOUSE TOKYO Shinjuku"),
    service("TOKYO_OTEMACHI", "Tokyo", "TELEHOUSE TOKYO Otemachi"),
    service("TOKYO_ODAIBA", "Tokyo", "TELEHOUSE TOKYO Odaiba"),
    service("TOKYO_SHIBUYA", "Tokyo", "TELEHOUSE TOKYO Shibuya"),
    service("TOKYO_KOTO", "Tokyo", "TELEHOUSE TOKYO Koto"),
    service("TOKYO_FUCHU", "Tokyo", "TELEHOUSE TOKYO Fuchu"),
    service("TOKYO_MEJIROZAKA", "Tokyo", "TELEHOUSE TOKYO Mejirozaka"),
    service("TOKYO_IIDABASHI", "Tokyo", "TELEHOUSE TOKYO Iidabashi"),
    service("TOKYO_TAMA", "Tokyo", "TELEHOUSE TOKYO Tama"),
    service("TOKYO_TENNOZU", "Tokyo", "Tennozu Data Center", "KDDI_non_Telehouse_label"),
    service("NAGOYA_NAGOYA_NAKA", "Nagoya", "TELEHOUSE NAGOYA Nagoya-naka"),
    service("NAGOYA_SAKAE", "Nagoya", "TELEHOUSE NAGOYA Sakae"),
    service("OSAKA_OSAKA_CHUO", "Osaka", "TELEHOUSE OSAKA Osaka-chuo"),
    service("OSAKA_SHINSAIBASHI", "Osaka", "Shinsaibashi Data Center", "KDDI_non_Telehouse_label"),
    service("OSAKA_UMEDA_KITA", "Osaka", "Umeda-kita Data Center", "KDDI_non_Telehouse_label"),
    service("OKAYAMA", "Okayama", "Okayama Data Center", "KDDI_non_Telehouse_label"),
    service("HIROSHIMA", "Hiroshima", "TELEHOUSE HIROSHIMA"),
    service("FUKUOKA", "Fukuoka", "TELEHOUSE FUKUOKA"),
    service("NAHA", "Naha", "TELEHOUSE NAHA"),
    {
        "record_code": "OSAKA_SAKAI_AI",
        "market": "Sakai / Osaka",
        "provider_label": "Osaka Sakai Data Center",
        "brand": "KDDI",
        "record_class": "separately_sourced_operating_AI_data_center_not_in_22_row_WVS_table",
        "lifecycle_as_of_2026_07_19": "operating_since_2026_01_22_with_GPU_Cloud_trial_and_2026_04_01_applications",
        "building": {"stories_above_ground": 4, "cumulative_floor_area_sqm_approximately": 57000},
        "power_and_cooling": {
            "reused_former_Sharp_Sakai_plant_power_and_cooling": True,
            "cooling": ["direct_liquid_cooling", "air_cooling", "turbo_chillers", "cooling_towers"],
            "renewable_electricity_percent": 100,
            "facility_IT_or_grid_capacity_mw": "undisclosed",
        },
        "network": {"internet_speed_gbps_up_to": 100, "closed_network": "KDDI_WVS2", "multicloud_gateway": True},
        "accelerators": {
            "confirmed_platform": "NVIDIA_GB200_NVL72_by_HPE_and_other_systems",
            "GPU_Cloud": "trial_from_2026_01_22_and_applications_from_2026_04_01",
            "service_granularity": "bare_metal_GPU_server_compute_units_from_one_server_to_cluster",
            "current_installed_system_rack_and_physical_GPU_count": "undisclosed",
            "2024_discussion_estimate": "1000_units_of_GB200_NVL72_assumed_to_be_supplied_by_NVIDIA",
            "estimate_boundary": "The 2024 four-party discussion assumption is not a confirmed 2026 delivered, installed, accepted, serviceable or utilized count; later operating releases disclose no quantity.",
        },
        "source_urls": [SAKAI_URL, GPU_CLOUD_URL, SAKAI_2024_URL, RENEWABLE_URL],
    },
    {
        "record_code": "TOKYO_TAMA_5_2ND",
        "market": "Tama / Tokyo",
        "provider_label": "Telehouse TOKYO Tama 5-2nd",
        "brand": "Telehouse / KDDI",
        "record_class": "separately_sourced_AI_ready_construction_project_not_in_22_row_WVS_table_as_distinct_label",
        "lifecycle_as_of_2026_07_19": "under_construction_target_open_autumn_2027",
        "building": {"stories_above_ground": 8, "stories_below_ground": 1, "rack_area_sqm_approximately": 5800, "racks_approximately": 1900},
        "power_and_cooling": {
            "IT_power_capacity_mw": 18,
            "Tama_area_total_receiving_capacity_mw_up_to": 100,
            "cooling": "water_cooling_ready_for_high_power_GPU_servers",
            "planned_renewable_electricity_percent": 100,
        },
        "denominator_boundary": "18 MW is facility IT power; 100 MW is total receiving capacity for the wider Tama area and includes all servers and cooling. They are not additive or current operating load.",
        "source_urls": [TAMA_5_2_URL, DATA_CENTER_URL, RENEWABLE_URL],
    },
]


PORTFOLIO_CONTEXT = {
    "current_WVS_product_availability_labels": 22,
    "WVS_label_brand_counts": {"Telehouse": 18, "KDDI_non_Telehouse_label": 4},
    "WVS_markets": 10,
    "broader_current_domestic_map_areas": ["Hokkaido", "Miyagi", "Tochigi", "Toyama", "Tokyo", "Aichi", "Osaka", "Okayama", "Hiroshima", "Fukuoka", "Okinawa"],
    "scope_gap": "The broader current service page includes Toyama on its Japan map, but the 22-row WVS product table has no Toyama label. The WVS list is therefore not a complete KDDI domestic portfolio census.",
    "Tama_boundary": "The one WVS Tama label can aggregate multiple facilities including Tama 3 and Tama 5; Tama 5-2nd is separately disclosed under construction and is not silently counted as a current WVS label.",
    "Telehouse_global_context": "KDDI separately markets more than 45 Telehouse locations in more than 10 countries; this Japan registry does not replace the global Telehouse registry.",
    "company_financial_ref": "company_kddi",
    "global_portfolio_ref": "dc_telehouse_global_connectivity_portfolio",
}


OSM_DISPOSITIONS = {
    "osm_node_12500429891": {"market": "Tokyo", "disposition": "KDDI_name_only_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12504065376": {"market": "Fukuoka", "disposition": "KDDI_name_only_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12504065377": {"market": "Fukuoka", "disposition": "KDDI_name_only_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12564883385": {"market": "Fukuoka", "disposition": "KDDI_name_only_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12500332318": {"market": "Osaka", "disposition": "KDDI_operator_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12500429890": {"market": "Tokyo", "disposition": "KDDI_operator_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12504065381": {"market": "Osaka", "disposition": "KDDI_operator_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12500429900": {"market": "Nagoya", "disposition": "KDDI_name_and_operator_market_evidence_exact_provider_site_unresolved"},
    "osm_node_12581599889": {"market": "Takamatsu", "disposition": "KDDI_name_and_operator_object_outside_current_22_label_WVS_roster"},
    "osm_way_617551098": {"market": "Chikura", "disposition": "KDDI_submarine_cable_relay_named_telecom_object_outside_current_service_roster"},
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
        combined = f"{row.get('name') or ''} {row.get('operator') or ''}".casefold()
        if "kddi" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    wvs = [row for row in RECORDS if row["record_class"].startswith("current_KDDI_WVS")]
    assert len(RECORDS) == 24
    assert len(wvs) == 22
    assert len({row["record_code"] for row in RECORDS}) == len(RECORDS)
    assert Counter(row["brand"] for row in wvs) == {"Telehouse": 18, "KDDI_non_Telehouse_label": 4}
    assert len({row["market"] for row in wvs}) == 10
    assert len(candidates) == 10, [row["id"] for row in candidates]
    assert set(OSM_DISPOSITIONS) == {row["id"] for row in candidates}
    osm_reviews = []
    for object_id, disposition in OSM_DISPOSITIONS.items():
        source = osm[object_id]
        osm_reviews.append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "source_url": source["source_url"],
            **disposition,
            "boundary": "OSM market evidence is not an official KDDI service-site identity, physical building, operating status, capacity, ownership or financial record.",
        })
    records = [{
        "id": f"kddi_japan_{row['record_code'].lower()}",
        "object_type": "ProviderPublishedDataCenterServiceOrProjectRecord",
        "source_order": position,
        "operator": "KDDI / Telehouse",
        "country_code": "JP",
        "record_granularity": "product_service_label_or_separately_sourced_project_not_physical_building_census",
        **row,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "accessed_on": accessed_on,
    } for position, row in enumerate(RECORDS, 1)]
    return records, osm_reviews


def build_summary(records: list[dict], osm_reviews: list[dict], accessed_on: str) -> dict:
    wvs = [row for row in records if row["record_class"].startswith("current_KDDI_WVS")]
    return {
        "registry": "KDDI Japan current product-service labels and separately sourced AI data-center projects",
        "records": len(records),
        "current_WVS_product_availability_labels": len(wvs),
        "WVS_market_counts": dict(sorted(Counter(row["market"] for row in wvs).items())),
        "WVS_brand_counts": dict(sorted(Counter(row["brand"] for row in wvs).items())),
        "separate_operating_AI_data_centers": 1,
        "separate_under_construction_AI_projects": 1,
        "related_OSM_objects": len(osm_reviews),
        "raw_operator_tagged_OSM_objects": sum(bool(row["osm_operator"]) for row in osm_reviews),
        "raw_name_only_OSM_objects": sum(bool(row["osm_name"]) and not row["osm_operator"] for row in osm_reviews),
        "OSM_market_counts": dict(sorted(Counter(row["market"] for row in osm_reviews).items())),
        "OSM_disposition_counts": dict(sorted(Counter(row["disposition"] for row in osm_reviews).items())),
        "osm_reviews": sorted(osm_reviews, key=lambda row: row["osm_object_id"]),
        "portfolio_context": PORTFOLIO_CONTEXT,
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not equate or sum product labels, market groups, physical buildings, OSM objects, Osaka Sakai operating AI infrastructure, Tama construction, global Telehouse locations, receiving capacity, IT power, investment plans or the 2024 accelerator estimate.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/kddi_japan_data_center_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/kddi_japan_data_center_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, osm_reviews = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
