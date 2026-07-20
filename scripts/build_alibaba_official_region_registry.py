#!/usr/bin/env python3
"""Build a reproducible Alibaba Cloud Region and zone registry.

Alibaba Cloud publishes two useful but differently scoped official sources. The
technical guide lists public-cloud, Finance Cloud, and Gov Cloud Region and zone
IDs. The global-locations page lists only the public-cloud marketing portfolio,
with release years and a stronger physical definition of a zone. This builder
joins those sources without treating a Region, zone, or map point as one data-
center building, an owned asset, or an energized-capacity disclosure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


REGIONS_URL = (
    "https://www.alibabacloud.com/help/en/cloud-migration-guide-for-beginners/"
    "latest/regions-and-zones"
)
GLOBAL_LOCATIONS_URL = (
    "https://www.alibabacloud.com/en/about/global-locations?_p_lc=1"
)


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def read_or_fetch(path: str | None, url: str) -> bytes:
    return Path(path).read_bytes() if path else fetch_bytes(url)


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


def canonical_name(value: str) -> str:
    value = normalize_text(value).lower()
    value = value.replace(" - closing down", " closing down")
    value = value.replace("mexico (querétaro)", "mexico")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


class TableParser(HTMLParser):
    """Capture tables and their cell text/rowspan metadata."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[dict] = []
        self.current_table: dict | None = None
        self.current_row: list[dict] | None = None
        self.current_cell: dict | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if tag == "table":
            self.current_table = {"attrs": attrs_dict, "rows": []}
            self.tables.append(self.current_table)
        elif tag == "tr" and self.current_table is not None:
            self.current_row = []
            self.current_table["rows"].append(self.current_row)
        elif tag in {"td", "th"} and self.current_row is not None:
            self.current_cell = {
                "text": [],
                "rowspan": int(attrs_dict.get("rowspan", "1")),
            }
            self.current_row.append(self.current_cell)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self.current_cell = None
        elif tag == "tr":
            self.current_row = None
        elif tag == "table":
            self.current_table = None

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell["text"].append(data)


def table_rows(data: bytes) -> list[dict]:
    parser = TableParser()
    parser.feed(data.decode("utf-8"))
    tables = []
    for table in parser.tables:
        rows = []
        for row in table["rows"]:
            rows.append(
                [
                    {
                        "text": normalize_text("".join(cell["text"])),
                        "rowspan": cell["rowspan"],
                    }
                    for cell in row
                ]
            )
        tables.append({"attrs": table["attrs"], "rows": rows})
    return tables


def parse_region_tables(data: bytes) -> list[dict]:
    public_table_number = 0
    records: list[dict] = []
    for table in table_rows(data):
        if not table["rows"]:
            continue
        headers = [cell["text"] for cell in table["rows"][0]]
        if headers == [
            "Region name",
            "Region ID",
            "Number of zones",
            "Zone name",
            "Zone ID",
        ]:
            public_table_number += 1
            partition = (
                "public_cloud_china"
                if public_table_number == 1
                else "public_cloud_international"
            )
            expected_columns = 5
        elif headers == [
            "Region name",
            "Region ID",
            "Region",
            "Number of zones",
            "Zone name",
            "Zone ID",
        ]:
            expected_columns = 6
            flattened = " ".join(
                cell["text"] for row in table["rows"][1:] for cell in row
            )
            partition = (
                "finance_cloud" if "finance" in flattened.lower() else "government_cloud"
            )
        else:
            continue

        current: dict | None = None
        for row in table["rows"][1:]:
            cells = [cell["text"] for cell in row]
            if len(cells) == expected_columns:
                if expected_columns == 5:
                    region_name, region_id, zone_count, zone_name, zone_id = cells
                    reference_region = None
                else:
                    (
                        region_name,
                        region_id,
                        reference_region,
                        zone_count,
                        zone_name,
                        zone_id,
                    ) = cells
                current = {
                    "service_partition": partition,
                    "region_name": region_name,
                    "region_id": region_id,
                    "reference_physical_region": reference_region,
                    "published_zone_count": int(zone_count),
                    "zones": [],
                }
                records.append(current)
            elif len(cells) == 2 and current is not None:
                zone_name, zone_id = cells
            else:
                raise RuntimeError(
                    f"Unexpected Alibaba table row for {partition}: {cells}"
                )
            current["zones"].append({"zone_name": zone_name, "zone_id": zone_id})

    if public_table_number != 2:
        raise RuntimeError(f"Expected two Alibaba public-cloud tables, got {public_table_number}")
    return records


def parse_marketing_arrays(data: bytes) -> list[dict]:
    text = data.decode("utf-8")
    records = []
    for array_name, group in (
        ("intlRegions", "international"),
        ("domesticRegions", "china"),
    ):
        match = re.search(
            rf"window\.{array_name}\s*=\s*(\[.*?\]);",
            text,
            re.DOTALL,
        )
        if not match:
            raise RuntimeError(f"Alibaba marketing array not found: {array_name}")
        for item in json.loads(match.group(1)):
            records.append(
                {
                    "marketing_group": group,
                    "marketing_name": normalize_text(item["name"]),
                    "published_zone_count": int(item["number"]),
                    "release_year": int(item["time"]),
                    "map_anchor": {
                        "x": int(item["x"]) if item.get("x") else None,
                        "y": int(item["y"]) if item.get("y") else None,
                        "boundary": "Provider infographic anchor, not latitude/longitude or a building coordinate.",
                    },
                }
            )
    return records


def validate_definitions(regions_data: bytes, marketing_data: bytes) -> None:
    regions_text = normalize_text(regions_data.decode("utf-8"))
    marketing_text = normalize_text(marketing_data.decode("utf-8"))
    required = [
        (
            regions_text,
            "A region is a geographic area that contains Alibaba Cloud data centers",
        ),
        (
            regions_text,
            "A zone is a physical area within a region with independent power and networking",
        ),
        (
            marketing_text,
            "A zone is composed of one or multiple scattered data centers",
        ),
        (
            marketing_text,
            "redundant power supplies, networks, and connections",
        ),
    ]
    for haystack, needle in required:
        if needle not in haystack:
            raise RuntimeError(f"Alibaba source definition changed or missing: {needle}")


def join_sources(regions: list[dict], marketing: list[dict], accessed_on: str) -> list[dict]:
    marketing_by_name = {canonical_name(row["marketing_name"]): row for row in marketing}
    joined = []
    for position, source in enumerate(regions, start=1):
        lifecycle = "current_listed"
        if "Closing Down" in source["region_name"]:
            lifecycle = "closing_down"
        elif "Preview" in source["region_name"]:
            lifecycle = "preview"

        marketing_match = None
        if source["service_partition"].startswith("public_cloud"):
            marketing_match = marketing_by_name.get(canonical_name(source["region_name"]))
            if marketing_match is None:
                raise RuntimeError(
                    f"No Alibaba marketing crosswalk for {source['region_name']}"
                )
            if marketing_match["published_zone_count"] != source["published_zone_count"]:
                raise RuntimeError(
                    f"Alibaba zone-count mismatch for {source['region_name']}"
                )

        if len(source["zones"]) != source["published_zone_count"]:
            raise RuntimeError(
                f"Alibaba zone-row mismatch for {source['region_name']}: "
                f"{len(source['zones'])} != {source['published_zone_count']}"
            )

        partner_region = "Partner Region" in source["region_name"]
        joined.append(
            {
                "id": f"alibaba_cloud_region_{source['region_id'].replace('-', '_')}",
                "provider": "Alibaba Cloud",
                "source_order": position,
                "service_partition": source["service_partition"],
                "region_name": source["region_name"],
                "region_id": source["region_id"],
                "reference_physical_region": source["reference_physical_region"],
                "lifecycle": lifecycle,
                "partner_region": partner_region,
                "published_zone_count": source["published_zone_count"],
                "zones": source["zones"],
                "public_marketing_crosswalk": marketing_match,
                "granularity_boundary": (
                    "A Region is a provider geography. A zone is a physical area made of one or "
                    "multiple data centers with independent supporting facilities; neither is one "
                    "proven building, street address, owned asset, or energized IT-load record."
                ),
                "ownership_boundary": (
                    "The source does not identify owned, leased, colocation, partner-owned, or "
                    "joint-venture capacity. Riyadh is explicitly labeled a Partner Region."
                ),
                "undisclosed_or_unreconciled": [
                    "exact campus, building, street address, parcel, owner, lease, and colocation roster",
                    "operating, construction, commissioning, customer-acceptance, and revenue-start status below Region lifecycle",
                    "utility, IT, energized, leased, utilized, and billed power capacity",
                    "GPU and proprietary accelerator models, counts, racks, fabrics, ownership, and utilization",
                    "grid feeds, substations, transformers, switchgear, UPS, batteries, generators, cooling, and equipment OEMs",
                    "site PUE, WUE, water, liquid-cooled MW, renewable matching, revenue, capex, and operating margin",
                ],
                "sources": {
                    "technical_region_and_zone_guide": REGIONS_URL,
                    "public_cloud_global_locations": (
                        GLOBAL_LOCATIONS_URL if marketing_match is not None else None
                    ),
                },
                "accessed_on": accessed_on,
            }
        )
    return joined


def build_summary(
    records: list[dict],
    marketing: list[dict],
    source_records: list[dict],
    accessed_on: str,
) -> dict:
    partition_region_counts = Counter(row["service_partition"] for row in records)
    partition_zone_counts = Counter()
    for row in records:
        partition_zone_counts[row["service_partition"]] += row["published_zone_count"]
    lifecycle_region_counts = Counter(row["lifecycle"] for row in records)
    lifecycle_zone_counts = Counter()
    for row in records:
        lifecycle_zone_counts[row["lifecycle"]] += row["published_zone_count"]

    public = [row for row in records if row["service_partition"].startswith("public_cloud")]
    current_public = [row for row in public if row["lifecycle"] == "current_listed"]
    stable_current = [row for row in records if row["lifecycle"] == "current_listed"]
    no_map_anchor = [
        row["region_name"]
        for row in public
        if row["public_marketing_crosswalk"]["map_anchor"]["x"] is None
    ]
    summary = {
        "registry": "Alibaba Cloud official Region and zone registry",
        "accessed_on": accessed_on,
        "record_count": len(records),
        "published_zone_record_count": sum(row["published_zone_count"] for row in records),
        "partition_region_counts": dict(sorted(partition_region_counts.items())),
        "partition_zone_counts": dict(sorted(partition_zone_counts.items())),
        "lifecycle_region_counts": dict(sorted(lifecycle_region_counts.items())),
        "lifecycle_zone_counts": dict(sorted(lifecycle_zone_counts.items())),
        "public_cloud_scope": {
            "region_rows": len(public),
            "zone_rows_including_closing_down": sum(row["published_zone_count"] for row in public),
            "current_listed_region_rows_excluding_closing_down": len(current_public),
            "current_listed_zone_rows_excluding_closing_down": sum(
                row["published_zone_count"] for row in current_public
            ),
            "marketing_crosswalk_rows": len(marketing),
        },
        "all_partitions_current_listed_excluding_closing_and_preview": {
            "region_rows": len(stable_current),
            "zone_rows": sum(row["published_zone_count"] for row in stable_current),
        },
        "notable_rows": {
            "closing_down": [
                row["region_name"] for row in records if row["lifecycle"] == "closing_down"
            ],
            "preview": [
                row["region_name"] for row in records if row["lifecycle"] == "preview"
            ],
            "partner_region": [row["region_name"] for row in records if row["partner_region"]],
            "public_marketing_rows_without_map_anchor": no_map_anchor,
            "marketing_alias_reconciliation": {"technical_guide": "Mexico", "marketing": "Mexico (Querétaro)"},
        },
        "interpretation": {
            "region": "Provider geography containing Alibaba Cloud data centers.",
            "zone": "Physical area within a Region with independent power/networking; the marketing page says one zone contains one or multiple scattered data centers.",
            "building_count": "Undisclosed. The 130 zone records must not be called 130 buildings or facilities.",
            "capacity": "No current utility MW, IT MW, energized MW, live load, GPU inventory, or ownership roster is disclosed by these sources.",
        },
        "source_snapshots": {
            "technical_region_and_zone_guide": {
                "url": REGIONS_URL,
                "parsed_evidence_sha256": canonical_hash(source_records),
                "hash_scope": "Parsed Region, Region ID, zone count, zone name, and zone ID rows; excludes dynamic page shell.",
            },
            "public_cloud_global_locations": {
                "url": GLOBAL_LOCATIONS_URL,
                "parsed_evidence_sha256": canonical_hash(marketing),
                "hash_scope": "Parsed public marketing name, zone count, release year, and map-anchor rows; excludes dynamic page shell.",
            },
        },
    }
    summary["canonical_record_sha256"] = canonical_hash(records)
    return summary


def validate_expected_counts(records: list[dict], marketing: list[dict], summary: dict) -> None:
    expected_regions = {
        "public_cloud_china": 16,
        "public_cloud_international": 16,
        "finance_cloud": 4,
        "government_cloud": 1,
    }
    expected_zones = {
        "public_cloud_china": 65,
        "public_cloud_international": 40,
        "finance_cloud": 20,
        "government_cloud": 5,
    }
    assert summary["record_count"] == 37
    assert summary["published_zone_record_count"] == 130
    assert summary["partition_region_counts"] == expected_regions
    assert summary["partition_zone_counts"] == expected_zones
    assert len(marketing) == 32
    assert summary["public_cloud_scope"]["current_listed_region_rows_excluding_closing_down"] == 30
    assert summary["public_cloud_scope"]["current_listed_zone_rows_excluding_closing_down"] == 103
    assert summary["all_partitions_current_listed_excluding_closing_and_preview"] == {
        "region_rows": 34,
        "zone_rows": 125,
    }
    assert {row["region_id"] for row in records} == {
        row["region_id"] for row in records
    }
    assert len({row["region_id"] for row in records}) == 37


def write_outputs(output_dir: Path, records: list[dict], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "alibaba_official_region_registry.jsonl"
    summary_path = output_dir / "alibaba_official_region_summary.json"
    registry_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regions-html")
    parser.add_argument("--global-html")
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
    )
    args = parser.parse_args()

    inputs = {
        "regions": read_or_fetch(args.regions_html, REGIONS_URL),
        "marketing": read_or_fetch(args.global_html, GLOBAL_LOCATIONS_URL),
    }
    validate_definitions(inputs["regions"], inputs["marketing"])
    source_records = parse_region_tables(inputs["regions"])
    marketing = parse_marketing_arrays(inputs["marketing"])
    records = join_sources(source_records, marketing, args.accessed_on)
    summary = build_summary(records, marketing, source_records, args.accessed_on)
    validate_expected_counts(records, marketing, summary)
    write_outputs(Path(args.output_dir), records, summary)
    print(
        json.dumps(
            {
                "records": len(records),
                "zones": summary["published_zone_record_count"],
                "canonical_record_sha256": summary["canonical_record_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
