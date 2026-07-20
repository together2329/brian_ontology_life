#!/usr/bin/env python3
"""Build a reproducible Microsoft Azure region registry from official sources.

Microsoft publishes overlapping region views with different scopes.  The
Datacenters Globe API includes public, sovereign, available, and coming-soon
records, while the Azure reliability table covers the public Azure cloud and
also includes restricted regions.  This builder preserves both views, joins
them by displayed region name, and records the gaps without turning a region,
availability zone, or map point into a physical datacenter building.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


GLOBE_BASE_URL = "https://datacenters.microsoft.com/wp-json/globe"
REGIONS_URL = f"{GLOBE_BASE_URL}/regions"
GEOGRAPHIES_URL = f"{GLOBE_BASE_URL}/geographies"
LEARN_REGIONS_URL = "https://learn.microsoft.com/en-us/azure/reliability/regions-list"


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def normalize_text(value: str) -> str:
    return " ".join(html.unescape(value).replace("\xa0", " ").split())


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value).casefold())


class LearnRegionTableParser(HTMLParser):
    """Extract the first, all-regions table from the Microsoft Learn page."""

    def __init__(self) -> None:
        super().__init__()
        self.updated_at: str | None = None
        self.in_all_section = False
        self.in_table = False
        self.table_complete = False
        self.in_row = False
        self.in_cell = False
        self.cell_tag = ""
        self.current_cell_parts: list[str] = []
        self.current_cell_alts: list[str] = []
        self.current_row: list[dict] = []
        self.headers: list[str] = []
        self.rows: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if tag == "meta" and attributes.get("name") == "updated_at":
            self.updated_at = attributes.get("content")
        if tag == "section" and attributes.get("id") == "tabpanel_1_all":
            self.in_all_section = True
        elif self.in_all_section and tag == "table" and not self.table_complete:
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.current_row = []
        elif self.in_row and tag in {"th", "td"}:
            self.in_cell = True
            self.cell_tag = tag
            self.current_cell_parts = []
            self.current_cell_alts = []
        elif self.in_cell and tag == "img":
            alternate = attributes.get("alt")
            if alternate:
                self.current_cell_alts.append(normalize_text(alternate))

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag == self.cell_tag:
            self.current_row.append(
                {
                    "text": normalize_text(" ".join(self.current_cell_parts)),
                    "image_alt": self.current_cell_alts,
                    "cell_tag": self.cell_tag,
                }
            )
            self.in_cell = False
        elif self.in_row and tag == "tr":
            self.in_row = False
            if self.current_row and all(
                cell["cell_tag"] == "th" for cell in self.current_row
            ):
                self.headers = [cell["text"] for cell in self.current_row]
            elif self.current_row and self.headers:
                values = {
                    header: self.current_row[index]
                    for index, header in enumerate(self.headers)
                    if index < len(self.current_row)
                }
                if values.get("Programmatic name", {}).get("text"):
                    self.rows.append(self._normalize_row(values))
        elif self.in_table and tag == "table":
            self.in_table = False
            self.table_complete = True
        elif self.in_all_section and tag == "section":
            self.in_all_section = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            text = normalize_text(data)
            if text:
                self.current_cell_parts.append(text)

    @staticmethod
    def _normalize_row(values: dict[str, dict]) -> dict:
        region = values["Region"]
        paired = values["Paired region"]
        zone = values["Availability zone support"]
        all_alts = region["image_alt"] + paired["image_alt"] + zone["image_alt"]
        return {
            "display_name": region["text"],
            "programmatic_name": values["Programmatic name"]["text"],
            "physical_location_label": values["Physical location"]["text"],
            "geography_label": values["Geography"]["text"],
            "paired_region_label": paired["text"],
            "availability_zone_support": any(alt == "Yes" for alt in zone["image_alt"]),
            "coming_soon": any("coming soon" in alt.casefold() for alt in region["image_alt"]),
            "restricted_access": any("restricted" in alt.casefold() for alt in region["image_alt"]),
            "source_image_alt_evidence": all_alts,
        }


def parse_learn_regions(page: bytes) -> tuple[list[dict], str | None]:
    parser = LearnRegionTableParser()
    parser.feed(page.decode("utf-8"))
    if not parser.rows:
        raise RuntimeError("No rows found in the Microsoft Learn all-regions table")
    return parser.rows, parser.updated_at


def maybe_float(value: str | None) -> float | None:
    try:
        return float(value) if value not in {None, ""} else None
    except ValueError:
        return None


def globe_view(row: dict) -> dict:
    return {
        "wordpress_post_id": row.get("ID"),
        "region_id": row.get("id"),
        "post_name": row.get("post_name"),
        "display_name": normalize_text(row.get("displayName", "")),
        "physical_location_label": normalize_text(row.get("location", "")),
        "geography_id": row.get("geographyId"),
        "continent_raw": row.get("continent"),
        "map_point": {
            "latitude": maybe_float(row.get("latitude")),
            "longitude": maybe_float(row.get("longitude")),
            "interpretation": "provider_visual_region_anchor_not_a_building_or_street_address",
        },
        "lifecycle": {
            "is_open": row.get("isOpen"),
            "year_open_raw": normalize_text(str(row.get("yearOpen", ""))),
            "wordpress_published": row.get("post_date_gmt"),
            "wordpress_modified": row.get("post_modified_gmt"),
        },
        "region_type_id": row.get("typeId"),
        "availability_zones_id": row.get("availabilityZonesId"),
        "availability_zones_nearest_region_ids": row.get(
            "availabilityZonesNearestRegionIds", []
        ),
        "data_residency": normalize_text(row.get("dataResidency", "")),
        "available_to": normalize_text(row.get("availableTo", "")),
        "announcement_url": row.get("announcementLink") or None,
        "products_by_region_url": row.get("productsByRegionLink") or None,
        "products_by_region_nonregional_url": row.get(
            "productsByRegionLinkNonRegional"
        )
        or None,
        "has_ground_station": row.get("hasGroundStation"),
        "disaster_recovery_crossregion_ids": row.get(
            "disasterRecoveryCrossregionIds", []
        ),
        "disaster_recovery_inregion_ids": row.get(
            "disasterRecoveryInregionIds", []
        ),
        "sustainability_ids": row.get("sustainabilityIds", []),
        "compliance_ids": row.get("complianceIds", []),
    }


def build_registry(
    globe_rows: list[dict], learn_rows: list[dict], accessed_on: str
) -> list[dict]:
    globe_by_name = {
        normalized_name(row["displayName"]): row for row in globe_rows
    }
    learn_by_name = {
        normalized_name(row["display_name"]): row for row in learn_rows
    }
    duplicate_globe_names = len(globe_by_name) != len(globe_rows)
    duplicate_learn_names = len(learn_by_name) != len(learn_rows)
    if duplicate_globe_names or duplicate_learn_names:
        raise RuntimeError("Region display names are not unique within an official source")

    records = []
    for key in sorted(set(globe_by_name) | set(learn_by_name)):
        globe = globe_by_name.get(key)
        learn = learn_by_name.get(key)
        display_name = normalize_text(
            (globe or {}).get("displayName") or (learn or {})["display_name"]
        )
        if globe and learn:
            source_presence = "both"
        elif globe:
            source_presence = "datacenters_globe_only"
        else:
            source_presence = "azure_learn_public_table_only"
        records.append(
            {
                "schema_version": 1,
                "object_type": "ProviderOfficialRegionRecord",
                "provider": "Microsoft_Azure",
                "accessed_on": accessed_on,
                "display_name": display_name,
                "source_presence": source_presence,
                "datacenters_globe": globe_view(globe) if globe else None,
                "azure_learn_public_cloud_table": learn,
                "disclosure_boundary": {
                    "region": "one_or_more_datacenters_plus_networking_in_a_metro_area_not_one_building",
                    "availability_zone": "one_or_more_physically_separate_datacenters_not_one_building",
                    "map_point": "provider_region_visualization_anchor_not_exact_building_coordinates",
                    "ownership": "owned_leased_controlled_and_third_party_site_mapping_undisclosed",
                    "power": "live_energized_leased_utilized_and_billed_IT_MW_undisclosed_by_region",
                    "accelerators": "GPU_and_other_accelerator_inventory_racks_utilization_and_site_allocation_undisclosed",
                    "equipment": "substation_transformer_switchgear_UPS_battery_generator_cooling_and_CDU_BOM_undisclosed_by_region",
                },
            }
        )
    return records


def build_summary(
    records: list[dict],
    globe_rows: list[dict],
    learn_rows: list[dict],
    geographies: list[dict],
    accessed_on: str,
    learn_updated_at: str | None,
    source_hashes: dict[str, str],
) -> dict:
    source_presence = Counter(row["source_presence"] for row in records)
    lifecycle = Counter(
        "open" if row.get("isOpen") else "coming_or_not_open"
        for row in globe_rows
    )
    continent = Counter(str(row.get("continent") or "unresolved") for row in globe_rows)
    region_types = Counter(str(row.get("typeId") or "unresolved") for row in globe_rows)
    zone_status = Counter(
        str(row.get("availabilityZonesId") or "unresolved") for row in globe_rows
    )

    globe_only = [
        row["display_name"]
        for row in records
        if row["source_presence"] == "datacenters_globe_only"
    ]
    learn_only = [
        row["display_name"]
        for row in records
        if row["source_presence"] == "azure_learn_public_table_only"
    ]
    anomalies = []
    for row in globe_rows:
        if row.get("geographyId") == "austria" and row.get("continent") != "europe":
            anomalies.append(
                {
                    "region": row.get("displayName"),
                    "field": "continent",
                    "raw_value": row.get("continent"),
                    "expected_from_geography": "europe",
                    "handling": "raw_value_preserved_not_silently_corrected",
                }
            )

    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "datacenters_globe_regions": REGIONS_URL,
            "datacenters_globe_geographies": GEOGRAPHIES_URL,
            "azure_learn_public_cloud_regions": LEARN_REGIONS_URL,
            "azure_learn_updated_at": learn_updated_at,
            "retrieved_content_sha256": source_hashes,
        },
        "coverage": {
            "datacenters_globe_region_records": len(globe_rows),
            "datacenters_globe_lifecycle_counts": dict(sorted(lifecycle.items())),
            "datacenters_globe_region_type_counts": dict(sorted(region_types.items())),
            "datacenters_globe_availability_zone_status_counts": dict(
                sorted(zone_status.items())
            ),
            "datacenters_globe_continent_counts_raw": dict(sorted(continent.items())),
            "datacenters_globe_geography_records": len(geographies),
            "azure_learn_public_cloud_region_rows": len(learn_rows),
            "azure_learn_restricted_region_rows": sum(
                row["restricted_access"] for row in learn_rows
            ),
            "azure_learn_coming_soon_rows": sum(
                row["coming_soon"] for row in learn_rows
            ),
            "union_region_labels": len(records),
            "source_presence_counts": dict(sorted(source_presence.items())),
            "datacenters_globe_only_region_labels": globe_only,
            "azure_learn_only_region_labels": learn_only,
        },
        "source_anomalies": anomalies,
        "interpretation": {
            "why_counts_differ": "The Globe mixes public, sovereign, open, and coming-soon map records; Microsoft Learn documents the public Azure cloud and includes restricted regions.",
            "physical_building_count": "No exact building roster follows from either list. A region and an availability zone each can contain one or more datacenters.",
            "coordinates": "Globe latitude and longitude values are map anchors for regions, not disclosed building coordinates.",
            "company_headline_boundary": "The separate 500-plus datacenter and 80-plus announced-region headlines use broader company scopes and cannot be reconciled one-for-one to this registry.",
        },
        "remaining_gaps": [
            "Complete physical campus and building addresses behind each region and availability zone",
            "Owned versus leased, controlled, colocation, and partner-operated facility mapping",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Per-site GPU, accelerator, rack, network-fabric, and utilization inventory",
            "Per-site utility feed, substation, transformer, switchgear, UPS, battery, generator, chiller, and CDU bill of materials",
            "Construction, commissioning, customer-acceptance, and revenue-start dates for each building",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official Microsoft registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    regions_bytes = fetch_bytes(REGIONS_URL)
    geographies_bytes = fetch_bytes(GEOGRAPHIES_URL)
    learn_bytes = fetch_bytes(LEARN_REGIONS_URL)
    globe_rows = json.loads(regions_bytes.decode("utf-8"))
    geographies = json.loads(geographies_bytes.decode("utf-8"))
    learn_rows, learn_updated_at = parse_learn_regions(learn_bytes)
    records = build_registry(globe_rows, learn_rows, args.accessed_on)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "microsoft_official_region_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_summary(
        records=records,
        globe_rows=globe_rows,
        learn_rows=learn_rows,
        geographies=geographies,
        accessed_on=args.accessed_on,
        learn_updated_at=learn_updated_at,
        source_hashes={
            "datacenters_globe_regions": hashlib.sha256(regions_bytes).hexdigest(),
            "datacenters_globe_geographies": hashlib.sha256(
                geographies_bytes
            ).hexdigest(),
            "azure_learn_public_cloud_regions": hashlib.sha256(
                learn_bytes
            ).hexdigest(),
        },
    )
    summary_path = output_dir / "microsoft_official_region_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "registry": str(registry_path),
                "summary": str(summary_path),
                **summary["coverage"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
