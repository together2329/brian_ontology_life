#!/usr/bin/env python3
"""Build a scope-preserving Volcano Engine Region/AZ registry.

Volcano Engine's documentation is a client-rendered application and its Region
tables are product-specific.  The normalized rows below are a reviewed snapshot
of three official pages, not a claimed company-wide facility inventory:

* the general Region/AZ guide (7 Region rows; 24 published AZs),
* the Container Service guide (6 Region rows; 20 explicit AZ IDs), and
* the ECS API-endpoint guide (6 Region rows; endpoint names only).

The builder intentionally preserves disagreements between those scopes.  A
Region, AZ, or endpoint is not converted into a building, ownership, MW, GPU, or
revenue record.  Source-row hashes and count assertions make the curated snapshot
deterministic and reviewable even though the upstream pages do not expose stable
server-rendered tables to a simple fetch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


GENERAL_REGIONS_URL = "https://www.volcengine.com/docs/6534/1131814"
CONTAINER_REGIONS_URL = "https://www.volcengine.com/docs/6460/79643"
ECS_ENDPOINTS_URL = "https://www.volcengine.com/docs/6396/1581668?lang=zh"
SUSTAINABILITY_URL = "https://gongyi.bytedance.com/detail/7161987661010602014"


GENERAL_ROWS = [
    {
        "region_name": "华北2（北京）",
        "region_id": "cn-beijing",
        "published_zone_count": 9,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-beijing-a", "publication_status": "commercial"},
            {"zone_name": "可用区B", "zone_id": "cn-beijing-b", "publication_status": "commercial"},
            {"zone_name": "可用区C", "zone_id": "cn-beijing-c", "publication_status": "commercial"},
            {"zone_name": "可用区D", "zone_id": "cn-beijing-d", "publication_status": "commercial"},
            {"zone_name": "大同本地可用区A", "zone_id": "cn-beijing-datong-a", "publication_status": "invite_test"},
            {"zone_name": "可用区I", "zone_id": "cn-beijing-i", "publication_status": "dedicated_region"},
            {"zone_name": "大同本地可用区B", "zone_id": "cn-beijing-datong-b", "publication_status": "dedicated_region"},
        ],
    },
    {
        "region_name": "华北3（北京）",
        "region_id": "cn-beijing2",
        "published_zone_count": 2,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-beijing2-a", "publication_status": "invite_test"},
            {"zone_name": "可用区B", "zone_id": "cn-beijing2-b", "publication_status": "invite_test"},
        ],
    },
    {
        "region_name": "华北4（大同）",
        "region_id": "cn-datong",
        "published_zone_count": 3,
        "zones": [
            {"zone_name": "可用区I", "zone_id": "cn-datong-i", "publication_status": "dedicated_region"},
        ],
    },
    {
        "region_name": "华北5（乌兰察布）",
        "region_id": "cn-wulanchabu",
        "published_zone_count": 1,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-wulanchabu-a", "publication_status": "invite_test"},
        ],
    },
    {
        "region_name": "华东2（上海）",
        "region_id": "cn-shanghai",
        "published_zone_count": 3,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-shanghai-a", "publication_status": "commercial"},
            {"zone_name": "可用区B", "zone_id": "cn-shanghai-b", "publication_status": "commercial"},
            {"zone_name": "可用区C", "zone_id": "cn-shanghai-c", "publication_status": "commercial"},
        ],
    },
    {
        "region_name": "华南1（广州）",
        "region_id": "cn-guangzhou",
        "published_zone_count": 4,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-guangzhou-a", "publication_status": "commercial"},
            {"zone_name": "可用区B", "zone_id": "cn-guangzhou-b", "publication_status": "commercial"},
            {"zone_name": "可用区C", "zone_id": "cn-guangzhou-c", "publication_status": "commercial"},
        ],
    },
    {
        "region_name": "中国香港",
        "region_id": "cn-hongkong",
        "published_zone_count": 2,
        "zones": [
            {"zone_name": "可用区A", "zone_id": "cn-hongkong-a", "publication_status": "commercial"},
            {"zone_name": "可用区B", "zone_id": "cn-hongkong-b", "publication_status": "commercial"},
        ],
    },
]


CONTAINER_ROWS = [
    ("华北2（北京）", "cn-beijing", ["cn-beijing-a", "cn-beijing-b", "cn-beijing-c", "cn-beijing-d"]),
    ("华南1（广州）", "cn-guangzhou", ["cn-guangzhou-a", "cn-guangzhou-b", "cn-guangzhou-c"]),
    ("华东2（上海）", "cn-shanghai", ["cn-shanghai-a", "cn-shanghai-b", "cn-shanghai-c", "cn-shanghai-d", "cn-shanghai-e"]),
    ("亚太东南（柔佛）", "ap-southeast-1", ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]),
    ("亚太东南（雅加达）", "ap-southeast-3", ["ap-southeast-3a", "ap-southeast-3b", "ap-southeast-3c"]),
    ("中国香港", "cn-hongkong", ["cn-hongkong-a", "cn-hongkong-b"]),
]


ECS_ENDPOINT_ROWS = [
    ("华北2（北京）", "cn-beijing", "ecs.cn-beijing.volcengineapi.com"),
    ("华东2（上海）", "cn-shanghai", "ecs.cn-shanghai.volcengineapi.com"),
    ("华南1（广州）", "cn-guangzhou", "ecs.cn-guangzhou.volcengineapi.com"),
    ("中国香港", "cn-hongkong", "ecs.cn-hongkong.volcengineapi.com"),
    ("亚太东南（柔佛）", "ap-southeast-1", "ecs.ap-southeast-1.volcengineapi.com"),
    ("亚太东南（雅加达）", "ap-southeast-3", "ecs.ap-southeast-3.volcengineapi.com"),
]


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def source_map(rows, key_index: int = 1) -> dict[str, object]:
    return {row[key_index]: row for row in rows}


def validate_source_snapshot() -> None:
    assert len(GENERAL_ROWS) == 7
    assert sum(row["published_zone_count"] for row in GENERAL_ROWS) == 24
    assert sum(len(row["zones"]) for row in GENERAL_ROWS) == 19
    assert len(CONTAINER_ROWS) == 6
    assert sum(len(row[2]) for row in CONTAINER_ROWS) == 20
    assert len(ECS_ENDPOINT_ROWS) == 6
    assert {row[1] for row in CONTAINER_ROWS} == {row[1] for row in ECS_ENDPOINT_ROWS}


def build_records(accessed_on: str) -> list[dict]:
    validate_source_snapshot()
    general = {row["region_id"]: row for row in GENERAL_ROWS}
    container = source_map(CONTAINER_ROWS)
    ecs = source_map(ECS_ENDPOINT_ROWS)
    region_ids = list(general)
    region_ids.extend(region_id for region_id in container if region_id not in general)
    records = []
    for position, region_id in enumerate(region_ids, start=1):
        general_row = general.get(region_id)
        container_row = container.get(region_id)
        ecs_row = ecs.get(region_id)
        names = []
        if general_row:
            names.append(general_row["region_name"])
        if container_row:
            names.append(container_row[0])
        if ecs_row:
            names.append(ecs_row[0])
        record = {
            "id": f"volcengine_service_region_{region_id.replace('-', '_')}",
            "provider": "Volcano Engine",
            "source_order": position,
            "region_id": region_id,
            "region_names_as_published": list(dict.fromkeys(names)),
            "general_guide": None,
            "container_service": None,
            "ECS_API_endpoint": None,
            "scope_union_only": True,
            "lifecycle_boundary": (
                "A current documentation row indicates a documented service scope; it does not establish "
                "construction, commissioning, ownership, customer acceptance, or revenue start for a facility."
            ),
            "physical_granularity_boundary": (
                "Volcano Engine defines a Region as a geographic area containing physical data centers and an AZ as a "
                "physical area with independent power and network. Neither definition establishes one building per row."
            ),
            "undisclosed_or_unreconciled": [
                "company-wide Region and AZ roster across every Volcano Engine and ByteDance service",
                "campus, building, street address, parcel, ownership, lease, and colocation mapping",
                "operating, construction, commissioning, customer-acceptance, and revenue-start status below service documentation",
                "utility, IT, energized, leased, utilized, and billed power capacity",
                "GPU and accelerator models, counts, racks, fabrics, ownership, and utilization",
                "grid feeds, substations, transformers, switchgear, UPS, batteries, generators, cooling, and equipment OEMs",
                "per-site PUE, WUE, water, renewable matching, capex, revenue, and operating margin",
            ],
            "sources": {
                "general_Region_AZ_guide": GENERAL_REGIONS_URL,
                "container_service_Region_AZ_guide": CONTAINER_REGIONS_URL,
                "ECS_API_endpoint_guide": ECS_ENDPOINTS_URL,
                "ByteDance_sustainability_context": SUSTAINABILITY_URL,
            },
            "accessed_on": accessed_on,
        }
        if general_row:
            missing = general_row["published_zone_count"] - len(general_row["zones"])
            record["general_guide"] = {
                "document_updated_on": "2025-03-13",
                "published_zone_count": general_row["published_zone_count"],
                "captured_zone_rows": general_row["zones"],
                "zone_rows_not_exposed_in_reviewed_search_snapshot": missing,
                "boundary": (
                    "Published count is retained even where the reviewed official search snapshot did not render every ZoneID; "
                    "missing identifiers are not inferred."
                ),
            }
        if container_row:
            record["container_service"] = {
                "document_updated_on": "2025-09-30",
                "published_zone_count": len(container_row[2]),
                "zone_ids": container_row[2],
                "publication_status": "commercial",
                "boundary": "Container Service product availability only; not a provider-wide AZ roster.",
            }
        if ecs_row:
            record["ECS_API_endpoint"] = {
                "document_updated_on": "2025-06-30",
                "endpoint": ecs_row[2],
                "boundary": (
                    "The provider states that an API endpoint is an access point and does not necessarily represent "
                    "the geographic location where the product is directly provided."
                ),
            }
        records.append(record)
    return records


def build_summary(records: list[dict], accessed_on: str) -> dict:
    overlap = Counter()
    for row in records:
        scopes = sum(row[key] is not None for key in ("general_guide", "container_service", "ECS_API_endpoint"))
        overlap[f"present_in_{scopes}_source_scopes"] += 1
    general_ids = {row["region_id"] for row in records if row["general_guide"]}
    container_ids = {row["region_id"] for row in records if row["container_service"]}
    summary = {
        "registry": "Volcano Engine scope-preserving official Region and AZ registry",
        "accessed_on": accessed_on,
        "source_union_region_id_count": len(records),
        "source_union_count_boundary": "Nine unique IDs across three reviewed service-document scopes, not nine company-wide physical Regions.",
        "general_guide": {
            "document_updated_on": "2025-03-13",
            "region_rows": len(GENERAL_ROWS),
            "published_AZ_count": sum(row["published_zone_count"] for row in GENERAL_ROWS),
            "captured_AZ_ID_rows": sum(len(row["zones"]) for row in GENERAL_ROWS),
            "unrendered_AZ_ID_residual": sum(row["published_zone_count"] - len(row["zones"]) for row in GENERAL_ROWS),
        },
        "container_service_guide": {
            "document_updated_on": "2025-09-30",
            "region_rows": len(CONTAINER_ROWS),
            "AZ_ID_rows": sum(len(row[2]) for row in CONTAINER_ROWS),
        },
        "ECS_API_endpoint_guide": {
            "document_updated_on": "2025-06-30",
            "region_endpoint_rows": len(ECS_ENDPOINT_ROWS),
        },
        "scope_reconciliation": {
            "general_and_container_common_region_IDs": sorted(general_ids & container_ids),
            "general_only_region_IDs": sorted(general_ids - container_ids),
            "container_and_ECS_only_region_IDs": sorted(container_ids - general_ids),
            "source_presence_counts": dict(sorted(overlap.items())),
            "product_specific_AZ_count_conflicts": {
                "cn_beijing": {"general_guide": 9, "container_service": 4},
                "cn_guangzhou": {"general_guide": 4, "container_service": 3},
                "cn_shanghai": {"general_guide": 3, "container_service": 5},
                "cn_hongkong": {"general_guide": 2, "container_service": 2},
            },
        },
        "portfolio_sustainability_context": {
            "source_date": "2022-04-07",
            "metric_year": 2020,
            "renewable_energy_utilization_at_some_data_centers_percent_up_to": 100,
            "reported_data_center_PUE": 1.14,
            "reported_cooling": "indirect_evaporative_natural_cooling",
            "site_selection_preference": "areas_rich_in_wind_and_solar_resources",
            "allocation_boundary": "The reviewed company page does not map these portfolio statements to a Region, AZ, campus, building, or capacity.",
        },
        "source_snapshots": {
            "general_Region_AZ_guide": {
                "url": GENERAL_REGIONS_URL,
                "normalized_evidence_sha256": canonical_hash(GENERAL_ROWS),
                "access_boundary": "Client-rendered source; reviewed official search snapshot retained as normalized rows.",
            },
            "container_service_Region_AZ_guide": {
                "url": CONTAINER_REGIONS_URL,
                "normalized_evidence_sha256": canonical_hash(CONTAINER_ROWS),
                "access_boundary": "Product-specific official documentation snapshot.",
            },
            "ECS_API_endpoint_guide": {
                "url": ECS_ENDPOINTS_URL,
                "normalized_evidence_sha256": canonical_hash(ECS_ENDPOINT_ROWS),
                "access_boundary": "Endpoint roster only; provider disclaimer preserved.",
            },
            "ByteDance_sustainability_context": {
                "url": SUSTAINABILITY_URL,
                "normalized_evidence_sha256": canonical_hash({
                    "metric_year": 2020,
                    "renewable_up_to_percent": 100,
                    "PUE": 1.14,
                    "cooling": "indirect_evaporative_natural_cooling",
                }),
            },
        },
    }
    summary["canonical_record_sha256"] = canonical_hash(records)
    return summary


def validate_summary(summary: dict) -> None:
    assert summary["source_union_region_id_count"] == 9
    assert summary["general_guide"] == {
        "document_updated_on": "2025-03-13",
        "region_rows": 7,
        "published_AZ_count": 24,
        "captured_AZ_ID_rows": 19,
        "unrendered_AZ_ID_residual": 5,
    }
    assert summary["container_service_guide"]["AZ_ID_rows"] == 20
    assert summary["ECS_API_endpoint_guide"]["region_endpoint_rows"] == 6


def write_outputs(output_dir: Path, records: list[dict], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "volcengine_official_region_registry.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )
    (output_dir / "volcengine_official_region_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--output-dir", default="life/imports/global_data_centers_20260717")
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    validate_summary(summary)
    write_outputs(Path(args.output_dir), records, summary)
    print(json.dumps({
        "source_union_region_ids": len(records),
        "general_published_AZs": summary["general_guide"]["published_AZ_count"],
        "container_AZ_IDs": summary["container_service_guide"]["AZ_ID_rows"],
        "canonical_record_sha256": summary["canonical_record_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
