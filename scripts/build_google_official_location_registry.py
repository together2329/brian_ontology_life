#!/usr/bin/env python3
"""Build a reproducible Google data-center location registry.

Google's location page publishes three overlapping scopes: a static active-
location headline, a visible location list, and a hidden structured map payload.
The FAQ and selected detail pages provide additional lifecycle evidence.  This
builder preserves those scopes separately, reconciles explicit conflicts, and
does not treat a location label, detail page, or map coordinate as one physical
building.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


LOCATIONS_URL = "https://www.datacenters.google/locations/"
FAQ_URL = "https://www.datacenters.google/discover-more/faq/"
CANELONES_DETAIL_URL = (
    "https://datacenters.google/intl/es-419_ALL/locations/canelones-uruguay/"
)
WALTHAM_CROSS_DETAIL_URL = (
    "https://www.datacenters.google/locations/waltham-cross/"
)

US_STATE_NAMES = {
    "Alabama",
    "Arizona",
    "Arkansas",
    "Georgia",
    "Indiana",
    "Iowa",
    "Minnesota",
    "Missouri",
    "Nebraska",
    "Nevada",
    "North Carolina",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "South Carolina",
    "Tennessee",
    "Texas",
    "Virginia",
}


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


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def classes(attrs) -> set[str]:
    return set(dict(attrs).get("class", "").split())


class StructuredDataParser(HTMLParser):
    """Capture the JSON object stream in Google's hidden map-data div."""

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.depth:
            self.depth += 1
        elif tag == "div" and dict(attrs).get("id") == "data-centers-data":
            self.depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self.depth:
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.buffer.append(data)

    def rows(self) -> list[dict]:
        payload = "".join(self.buffer).strip().rstrip(",")
        if not payload:
            raise RuntimeError("Google hidden data-center payload was empty")
        rows = json.loads(f"[{payload}]")
        if not isinstance(rows, list) or not rows:
            raise RuntimeError("Google hidden data-center payload had no rows")
        return rows


class VisibleListParser(HTMLParser):
    """Parse the human-visible 'All locations' roster."""

    def __init__(self) -> None:
        super().__init__()
        self.container_depth = 0
        self.current_continent: str | None = None
        self.capture_tag: str | None = None
        self.buffer: list[str] = []
        self.current_href: str | None = None
        self.rows: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if not self.container_depth:
            if tag == "div" and "map-full-list" in classes(attrs):
                self.container_depth = 1
            return

        self.container_depth += 1
        if tag == "h3" and "glue-label" in classes(attrs):
            self.capture_tag = "h3"
            self.buffer = []
        elif tag == "li":
            self.capture_tag = "li"
            self.buffer = []
            self.current_href = None
        elif tag == "a" and self.capture_tag == "li":
            self.current_href = attrs_dict.get("href")

    def handle_endtag(self, tag: str) -> None:
        if not self.container_depth:
            return
        if tag == "h3" and self.capture_tag == "h3":
            self.current_continent = normalize_text("".join(self.buffer))
            self.capture_tag = None
            self.buffer = []
        elif tag == "li" and self.capture_tag == "li":
            text = normalize_text("".join(self.buffer))
            marker = "(in development)"
            location = normalize_text(text.replace(marker, ""))
            self.rows.append(
                {
                    "location": location,
                    "continent": self.current_continent,
                    "status": "in_development" if marker in text else "not_marked_in_development",
                    "detail_page": urljoin(LOCATIONS_URL, self.current_href)
                    if self.current_href
                    else None,
                }
            )
            self.capture_tag = None
            self.buffer = []
            self.current_href = None
        self.container_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.capture_tag:
            self.buffer.append(data)


class SidebarStatsParser(HTMLParser):
    """Capture the static headline counters beside Google's map."""

    def __init__(self) -> None:
        super().__init__()
        self.container_depth = 0
        self.capture_tag: str | None = None
        self.buffer: list[str] = []
        self.values: list[tuple[str, str]] = []
        self.pending_number: str | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if not self.container_depth:
            if tag == "div" and "map-sidebar__stats" in classes(attrs):
                self.container_depth = 1
            return
        self.container_depth += 1
        if tag in {"h2", "p"}:
            self.capture_tag = tag
            self.buffer = []

    def handle_endtag(self, tag: str) -> None:
        if not self.container_depth:
            return
        if tag == self.capture_tag:
            text = normalize_text("".join(self.buffer))
            if tag == "h2":
                self.pending_number = text
            elif tag == "p" and self.pending_number is not None:
                self.values.append((text, self.pending_number))
                self.pending_number = None
            self.capture_tag = None
            self.buffer = []
        self.container_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.capture_tag:
            self.buffer.append(data)


class ParagraphParser(HTMLParser):
    """Collect normalized paragraph text while excluding script and SVG noise."""

    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.in_paragraph = False
        self.buffer: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.skip_depth:
            self.skip_depth += 1
            return
        if tag in {"script", "style", "svg"}:
            self.skip_depth = 1
        elif tag == "p":
            self.in_paragraph = True
            self.buffer = []

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "p" and self.in_paragraph:
            text = normalize_text("".join(self.buffer))
            if text:
                self.paragraphs.append(text)
            self.buffer = []
            self.in_paragraph = False

    def handle_data(self, data: str) -> None:
        if self.in_paragraph and not self.skip_depth:
            self.buffer.append(data)


def parse_locations_page(html_bytes: bytes) -> tuple[list[dict], list[dict], dict]:
    html_text = html_bytes.decode("utf-8")

    structured_parser = StructuredDataParser()
    structured_parser.feed(html_text)
    structured_rows = structured_parser.rows()

    visible_parser = VisibleListParser()
    visible_parser.feed(html_text)
    visible_rows = visible_parser.rows

    stats_parser = SidebarStatsParser()
    stats_parser.feed(html_text)
    stats = {}
    for label, number in stats_parser.values:
        if number.isdigit():
            stats[label] = int(number)

    return structured_rows, visible_rows, stats


def parse_paragraphs(html_bytes: bytes) -> list[str]:
    parser = ParagraphParser()
    parser.feed(html_bytes.decode("utf-8"))
    return parser.paragraphs


def country_from_label(location: str) -> str:
    if location == "Singapore":
        return "Singapore"
    if location in {"Central Ohio", "Indiana", "Northern Virginia"}:
        return "United States"
    suffix = location.rsplit(",", 1)[-1].strip()
    if suffix in US_STATE_NAMES:
        return "United States"
    if "," in location:
        return suffix
    raise RuntimeError(f"Could not derive country from Google label: {location}")


def status_from_faq(location: str, faq_paragraphs: list[str]) -> str:
    matches = [
        paragraph
        for paragraph in faq_paragraphs
        if paragraph == location or paragraph == f"{location} (in development)"
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one exact FAQ lifecycle row for {location!r}, found {matches!r}"
        )
    return (
        "in_development"
        if matches[0].endswith("(in development)")
        else "not_marked_in_development"
    )


def build_registry(
    structured_rows: list[dict],
    visible_rows: list[dict],
    faq_paragraphs: list[str],
    canelones_paragraphs: list[str],
    waltham_paragraphs: list[str],
    accessed_on: str,
) -> list[dict]:
    structured_by_name = {row["location"]: row for row in structured_rows}
    visible_by_name = {row["location"]: row for row in visible_rows}
    if len(structured_by_name) != len(structured_rows):
        raise RuntimeError("Duplicate Google labels in hidden structured payload")
    if len(visible_by_name) != len(visible_rows):
        raise RuntimeError("Duplicate Google labels in visible location list")
    if set(structured_by_name) != set(visible_by_name):
        raise RuntimeError(
            "Google hidden and visible location rosters differ: "
            f"hidden_only={sorted(set(structured_by_name) - set(visible_by_name))}, "
            f"visible_only={sorted(set(visible_by_name) - set(structured_by_name))}"
        )

    canelones_detail_text = " ".join(canelones_paragraphs)
    if "En desarrollo" not in canelones_detail_text and not any(
        "próximo centro de datos" in paragraph for paragraph in canelones_paragraphs
    ):
        raise RuntimeError("Canelones detail page no longer contains development evidence")
    waltham_detail_text = " ".join(waltham_paragraphs)
    if "Google opens the Waltham Cross, UK data centre." not in waltham_detail_text:
        raise RuntimeError("Waltham Cross detail page no longer contains opening evidence")

    records = []
    for location in sorted(structured_by_name):
        raw = structured_by_name[location]
        visible = visible_by_name[location]
        structured_status = (
            "in_development" if raw["inDevelopment"] else "not_marked_in_development"
        )
        faq_status = status_from_faq(location, faq_paragraphs)
        status_sources = {
            "locations_hidden_map_payload": structured_status,
            "locations_visible_list": visible["status"],
            "faq_location_roster": faq_status,
        }

        detail_override = None
        if location == "Canelones, Uruguay":
            detail_override = "in_development"
            reconciled_status = "in_development"
            reconciliation_basis = (
                "FAQ and Canelones detail page explicitly say in development; "
                "the locations-page hidden flag and visible row omit that marker."
            )
        elif location == "Waltham Cross, United Kingdom":
            detail_override = "operating_opened_2025"
            reconciled_status = "operating_or_active"
            reconciliation_basis = (
                "The detail page explicitly says Google opened the site in 2025."
            )
        elif len(set(status_sources.values())) == 1:
            reconciled_status = (
                "in_development"
                if structured_status == "in_development"
                else "operating_or_active"
            )
            reconciliation_basis = "All three official roster views agree."
        else:
            reconciled_status = "unresolved_conflict"
            reconciliation_basis = "Official roster views conflict and no detail-page override was reviewed."

        detail_page = raw.get("detailPage") or visible.get("detail_page")
        detail_page = urljoin(LOCATIONS_URL, detail_page) if detail_page else None
        raw_detail = visible.get("detail_page")
        if raw_detail and detail_page and raw_detail.rstrip("/") != detail_page.rstrip("/"):
            raise RuntimeError(
                f"Hidden and visible detail URLs differ for {location}: "
                f"{detail_page!r} vs {raw_detail!r}"
            )

        latitude = raw.get("latitude")
        longitude = raw.get("longitude")
        record = {
            "id": f"google_dc_location_{slugify(location)}",
            "operator": "Google",
            "location_label": location,
            "continent": raw.get("continent"),
            "country_or_territory_derived_from_label": country_from_label(location),
            "lifecycle": {
                "reconciled_status": reconciled_status,
                "source_statuses": status_sources,
                "selected_detail_page_evidence": detail_override,
                "has_official_source_conflict": len(set(status_sources.values())) > 1,
                "reconciliation_basis": reconciliation_basis,
            },
            "provider_map_anchor": {
                "latitude": latitude,
                "longitude": longitude,
                "present": latitude is not None and longitude is not None,
                "boundary": "Provider map coordinate; not assumed to be a parcel, building, utility interconnect, or street-address point.",
            },
            "detail_page": detail_page,
            "page_metadata": {
                "short_description": normalize_text(raw.get("shortDescription")),
                "topics": raw.get("topics") or [],
                "callout_blocks": raw.get("calloutBlocks") or [],
                "featured_image": raw.get("featuredImage") or {},
            },
            "granularity_boundary": (
                "One public location label can cover more than one data-center site; "
                "it is not an exact campus or physical-building record."
            ),
            "undisclosed_or_unreconciled": [
                "exact physical campus and building count",
                "street address, parcel, and building coordinates",
                "owned versus leased or partner-operated building mapping",
                "operating, energized, leased, utilized, and billed IT MW",
                "site GPU, TPU, rack, fabric, and utilization inventory",
                "utility feeds, substations, transformers, switchgear, UPS, batteries, generators, chillers, CDUs, and OEM bill of materials",
                "construction, commissioning, acceptance, and revenue-start dates",
            ],
            "source": LOCATIONS_URL,
            "accessed_on": accessed_on,
        }
        records.append(record)
    return records


def build_summary(
    records: list[dict],
    structured_rows: list[dict],
    visible_rows: list[dict],
    sidebar_stats: dict,
    faq_paragraphs: list[str],
    canelones_paragraphs: list[str],
    waltham_paragraphs: list[str],
    accessed_on: str,
) -> dict:
    structured_status = Counter(
        "in_development" if row["inDevelopment"] else "not_marked_in_development"
        for row in structured_rows
    )
    visible_status = Counter(row["status"] for row in visible_rows)
    reconciled_status = Counter(
        row["lifecycle"]["reconciled_status"] for row in records
    )
    continent_all = Counter(row["continent"] for row in records)
    continent_reconciled_active = Counter(
        row["continent"]
        for row in records
        if row["lifecycle"]["reconciled_status"] == "operating_or_active"
    )
    active_records = [
        row
        for row in records
        if row["lifecycle"]["reconciled_status"] == "operating_or_active"
    ]
    active_countries = sorted(
        {row["country_or_territory_derived_from_label"] for row in active_records}
    )
    pre_waltham_active = [
        row
        for row in active_records
        if row["location_label"] != "Waltham Cross, United Kingdom"
    ]
    pre_waltham_countries = sorted(
        {row["country_or_territory_derived_from_label"] for row in pre_waltham_active}
    )

    detail_groups: dict[str, list[str]] = defaultdict(list)
    for row in records:
        if row["detail_page"]:
            detail_groups[row["detail_page"]].append(row["location_label"])
    shared_detail_pages = {
        url: sorted(labels)
        for url, labels in sorted(detail_groups.items())
        if len(labels) > 1
    }
    conflicts = [
        {
            "location": row["location_label"],
            "source_statuses": row["lifecycle"]["source_statuses"],
            "reconciled_status": row["lifecycle"]["reconciled_status"],
            "basis": row["lifecycle"]["reconciliation_basis"],
        }
        for row in records
        if row["lifecycle"]["has_official_source_conflict"]
    ]

    structured_evidence = [
        {
            key: row.get(key)
            for key in [
                "location",
                "latitude",
                "longitude",
                "inDevelopment",
                "detailPage",
                "continent",
                "shortDescription",
                "topics",
                "calloutBlocks",
            ]
        }
        for row in structured_rows
    ]
    canelones_evidence = sorted(
        paragraph
        for paragraph in canelones_paragraphs
        if "En desarrollo" in paragraph or "próximo centro de datos" in paragraph
    )
    waltham_evidence = sorted(
        paragraph
        for paragraph in waltham_paragraphs
        if "Google opens the Waltham Cross" in paragraph
        or "announced the opening of our data centre in Waltham Cross" in paragraph
    )

    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "locations_page": LOCATIONS_URL,
            "faq_page": FAQ_URL,
            "canelones_detail_page": CANELONES_DETAIL_URL,
            "waltham_cross_detail_page": WALTHAM_CROSS_DETAIL_URL,
            "retrieved_evidence_sha256": {
                "locations_hidden_structured_payload": canonical_hash(structured_evidence),
                "locations_visible_list": canonical_hash(visible_rows),
                "locations_sidebar_stats": canonical_hash(sidebar_stats),
                "faq_exact_location_rows": canonical_hash(
                    sorted(
                        paragraph
                        for paragraph in faq_paragraphs
                        if any(
                            paragraph == row["location"]
                            or paragraph == f'{row["location"]} (in development)'
                            for row in structured_rows
                        )
                    )
                ),
                "canelones_lifecycle_evidence": canonical_hash(canelones_evidence),
                "waltham_cross_lifecycle_evidence": canonical_hash(waltham_evidence),
            },
            "hash_boundary": "Hashes cover extracted stable evidence rather than full HTML, whose runtime nonce and presentation payload can vary per request.",
        },
        "coverage": {
            "location_labels_total": len(records),
            "hidden_payload_status_counts": dict(sorted(structured_status.items())),
            "visible_list_status_counts": dict(sorted(visible_status.items())),
            "reconciled_status_counts": dict(sorted(reconciled_status.items())),
            "continent_counts_all": dict(sorted(continent_all.items())),
            "continent_counts_reconciled_active": dict(
                sorted(continent_reconciled_active.items())
            ),
            "reconciled_active_country_or_territory_count": len(active_countries),
            "reconciled_active_countries_or_territories": active_countries,
            "provider_coordinates_present": sum(
                row["provider_map_anchor"]["present"] for row in records
            ),
            "provider_coordinates_present_reconciled_active": sum(
                row["provider_map_anchor"]["present"] for row in active_records
            ),
            "detail_page_rows": sum(bool(row["detail_page"]) for row in records),
            "unique_detail_pages": len(detail_groups),
            "shared_detail_pages": shared_detail_pages,
            "rows_with_callout_blocks": sum(
                bool(row["page_metadata"]["callout_blocks"]) for row in records
            ),
        },
        "headline_reconciliation": {
            "published_sidebar_stats": sidebar_stats,
            "hidden_and_visible_locations_page_raw_result": {
                "not_marked_in_development_location_labels": structured_status[
                    "not_marked_in_development"
                ],
                "countries_or_territories_derived": len(
                    {
                        row["country_or_territory_derived_from_label"]
                        for row in records
                        if row["lifecycle"]["source_statuses"][
                            "locations_hidden_map_payload"
                        ]
                        == "not_marked_in_development"
                    }
                ),
            },
            "after_canelones_detail_and_faq_correction": {
                "operating_or_active_location_labels": len(active_records),
                "countries_or_territories": len(active_countries),
            },
            "after_also_excluding_waltham_cross_opened_in_2025": {
                "operating_or_active_location_labels": len(pre_waltham_active),
                "countries_or_territories": len(pre_waltham_countries),
            },
            "inference": (
                "The static 30-location/11-country sidebar exactly matches the "
                "reconciled roster after removing Waltham Cross, which Google says "
                "opened in 2025. This strongly suggests the counters predate that "
                "opening, but Google does not publish a counter timestamp, so the "
                "staleness explanation remains an inference rather than a stated fact."
            ),
        },
        "official_source_conflicts": conflicts,
        "interpretation": {
            "canelones": "Treat as in development because the FAQ and detail page explicitly say so; preserve the contrary locations-page hidden flag and missing visible marker as upstream inconsistencies.",
            "waltham_cross": "Treat as operating or active because its official detail page says Google opened it in 2025.",
            "physical_building_count": "The 59 labels, 31 reconciled active labels, 28 in-development labels, and 29 unique detail pages are not physical-building counts. Google explicitly says a listed region may contain more than one data-center site.",
            "coordinates": "Only provider map anchors are preserved; none is promoted to parcel, building, street-address, or utility-interconnect precision.",
            "country_count": "Country or territory is derived from the public label solely to reconcile Google's headline; it is not a new site-level disclosure.",
        },
        "remaining_gaps": [
            "Exact physical campus and building roster behind each public label and shared detail page",
            "Street addresses, parcels, building coordinates, and land-control status",
            "Owned, leased, colocation, and partner-operated building mapping",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Per-site live GPU, TPU, rack, network-fabric, and utilization inventory",
            "Per-site utility feed, substation, transformer, switchgear, UPS, battery, generator, chiller, CDU, and OEM bill of materials",
            "Construction, commissioning, customer-acceptance, and revenue-start dates",
            "Timestamped correction or update of Google's static active-location and active-country counters",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official Google registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--locations-html")
    parser.add_argument("--faq-html")
    parser.add_argument("--canelones-html")
    parser.add_argument("--waltham-html")
    args = parser.parse_args()

    locations_bytes = read_or_fetch(args.locations_html, LOCATIONS_URL)
    faq_bytes = read_or_fetch(args.faq_html, FAQ_URL)
    canelones_bytes = read_or_fetch(args.canelones_html, CANELONES_DETAIL_URL)
    waltham_bytes = read_or_fetch(args.waltham_html, WALTHAM_CROSS_DETAIL_URL)

    structured_rows, visible_rows, sidebar_stats = parse_locations_page(
        locations_bytes
    )
    faq_paragraphs = parse_paragraphs(faq_bytes)
    canelones_paragraphs = parse_paragraphs(canelones_bytes)
    waltham_paragraphs = parse_paragraphs(waltham_bytes)
    records = build_registry(
        structured_rows,
        visible_rows,
        faq_paragraphs,
        canelones_paragraphs,
        waltham_paragraphs,
        args.accessed_on,
    )
    summary = build_summary(
        records,
        structured_rows,
        visible_rows,
        sidebar_stats,
        faq_paragraphs,
        canelones_paragraphs,
        waltham_paragraphs,
        args.accessed_on,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "google_official_location_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            )

    summary_path = output_dir / "google_official_location_summary.json"
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
                "headline_reconciliation": summary["headline_reconciliation"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
