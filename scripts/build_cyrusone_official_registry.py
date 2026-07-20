#!/usr/bin/env python3
"""Build a reproducible registry from CyrusOne's official location pages.

The directory currently groups multiple facility identifiers onto some campus
pages.  Page-level space and IT-capacity figures are therefore kept as shared
campus values and are never divided among identifiers.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


BASE_URL = "https://www.cyrusone.com"
DIRECTORY_URL = f"{BASE_URL}/data-centers"
LOCATION_PATTERN = re.compile(
    r'(/data-centers/(?:north-america|emea|apac)/[^"?#]+)'
)
RANGE_PATTERN = re.compile(r"^([A-Z]+)(\d+)-([A-Z]+)?(\d+)$")
EXTRA_OFFICIAL_DATA_SHEETS = {
    # These valid CyrusOne-hosted PDFs are not linked in the current page HTML.
    "MIL1": "https://www.cyrusone.com/hubfs/CyrusOne/C1_MIL1_DataSheet_SD.pdf?hsLang=en",
    "MIL2": "https://www.cyrusone.com/hubfs/C1_MIL2_DataSheet_DD%20%2811%29.pdf?hsLang=en",
}


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def plain_text(raw: str) -> str:
    return " ".join(
        re.sub(r"<[^>]+>", " ", html.unescape(raw), flags=re.S).split()
    )


class VisibleElementParser(HTMLParser):
    """Collect the rendered text of selected elements without dependencies."""

    TARGETS = {"h1", "h2", "h3", "h4", "h5", "p", "li"}

    def __init__(self) -> None:
        super().__init__()
        self.active: list[dict] = []
        self.items: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        for item in self.active:
            item["depth"] += 1
        if tag in self.TARGETS:
            self.active.append({"tag": tag, "depth": 0, "parts": []})

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            for item in self.active:
                item["parts"].append(value)

    def handle_endtag(self, tag: str) -> None:
        finished = []
        for item in self.active:
            if item["tag"] == tag and item["depth"] == 0:
                text = " ".join(item["parts"])
                if text:
                    self.items.append((tag, text))
                finished.append(item)
            else:
                item["depth"] = max(0, item["depth"] - 1)
        for item in finished:
            self.active.remove(item)


def extract_first(pattern: str, source: str) -> str | None:
    match = re.search(pattern, source, flags=re.I | re.S)
    return plain_text(match.group(1)) if match else None


def expand_identifiers(label: str) -> list[str]:
    label = label.strip()
    match = RANGE_PATTERN.fullmatch(label)
    if not match:
        return [label]
    start_prefix, start_raw, end_prefix, end_raw = match.groups()
    end_prefix = end_prefix or start_prefix
    if end_prefix != start_prefix:
        return [label]
    start = int(start_raw)
    end = int(end_raw)
    if end < start or end - start > 100:
        return [label]
    return [f"{start_prefix}{number}" for number in range(start, end + 1)]


def parse_number(raw: str | None) -> float | None:
    if not raw:
        return None
    match = re.search(r"[\d,.]+", raw)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def section_items(
    items: list[tuple[str, str]],
    start_label: str,
    end_labels: set[str],
    after_label: str | None = None,
) -> list[str]:
    after_index = -1
    if after_label:
        after_index = next(
            (
                index
                for index, (_, text) in enumerate(items)
                if text == after_label
            ),
            -1,
        )
    starts = [
        index for index, (_, text) in enumerate(items) if text == start_label
        and index > after_index
    ]
    if not starts:
        return []
    # HubSpot repeats labels in navigation and the footer.  For Sustainability,
    # the first exact heading after Technical Specifications is the content one.
    start = starts[0] if after_label else starts[-1]
    values = []
    for tag, text in items[start + 1 :]:
        if text in end_labels:
            break
        if tag == "li":
            values.append(text)
    return values


def parse_location_page(path: str, accessed_on: str) -> dict:
    canonical_url = urllib.parse.urljoin(BASE_URL, path)
    html_text = fetch_text(f"{canonical_url}?hsLang=en")
    left = re.search(
        r'<div class="left-content">(.*?)<div class="cta-wrapper">',
        html_text,
        flags=re.I | re.S,
    )
    left_html = left.group(1) if left else ""
    identifier_label = extract_first(r"<h3[^>]*>(.*?)</h3>", left_html) or ""
    identifiers = expand_identifiers(identifier_label)

    stat_pairs = [
        (plain_text(value), plain_text(label))
        for value, label in re.findall(
            r'<div class="item-text">\s*<h3[^>]*>(.*?)</h3>\s*'
            r"<p[^>]*>(.*?)</p>",
            html_text,
            flags=re.I | re.S,
        )
    ]
    technical_space_raw = next(
        (value for value, label in stat_pairs if "Technical IT Space" in label), None
    )
    it_capacity_raw = next(
        (value for value, label in stat_pairs if "IT Capacity" in label), None
    )

    parser = VisibleElementParser()
    parser.feed(html_text)
    features = section_items(
        parser.items, "Technical Specifications", {"Sustainability", "Contact Us"}
    )
    sustainability = section_items(
        parser.items,
        "Sustainability",
        {"Contact Us", "Global Headquarters"},
        after_label="Technical Specifications",
    )
    data_sheet_urls = sorted(
        {
            urllib.parse.urljoin(BASE_URL, html.unescape(url))
            for url in re.findall(
                r'href="([^"]+\.pdf(?:\?[^"]*)?)"', html_text, flags=re.I
            )
            if "ccpa-notice" not in url.lower()
        }
    )
    if identifier_label in EXTRA_OFFICIAL_DATA_SHEETS:
        data_sheet_urls.append(EXTRA_OFFICIAL_DATA_SHEETS[identifier_label])
        data_sheet_urls = sorted(set(data_sheet_urls))

    region = path.split("/")[2]
    space_unit = (
        "square_feet"
        if technical_space_raw and "ft" in technical_space_raw.lower()
        else "square_meters"
        if technical_space_raw and "m" in technical_space_raw.lower()
        else None
    )
    shared_page = len(identifiers) > 1
    return {
        "schema_version": 1,
        "object_type": "OperatorOfficialLocationPage",
        "operator": "CyrusOne",
        "accessed_on": accessed_on,
        "region": region,
        "metro_title": extract_first(r"<h1[^>]*>(.*?)</h1>", left_html),
        "published_identifier_label": identifier_label,
        "facility_identifiers": identifiers,
        "operator_published_address": extract_first(r"<p[^>]*>(.*?)</p>", left_html),
        "marketed_scale": {
            "technical_it_space_raw": technical_space_raw,
            "technical_it_space_value": parse_number(technical_space_raw),
            "technical_it_space_unit": space_unit,
            "total_it_capacity_raw": it_capacity_raw,
            "total_it_capacity_mw": parse_number(it_capacity_raw),
            "scope": (
                "shared_page_total_not_per_identifier"
                if shared_page
                else "single_identifier_page_marketed_total"
            ),
            "capacity_sum_eligible_once_per_page": True,
        },
        "technical_specifications": features,
        "sustainability": sustainability,
        "official_data_sheet_urls": data_sheet_urls,
        "source_url": canonical_url,
        "disclosure_boundary": {
            "lifecycle": "current_marketing_page_not_proof_of_energized_leased_utilized_or_billed_load",
            "accelerators": "GPU_models_counts_servers_racks_owners_installation_utilization_and_power_draw_undisclosed_unless_separately_sourced",
            "equipment": "only_items_explicitly_named_on_the_page_are_observed",
        },
    }


def build_summary(records: list[dict], accessed_on: str) -> dict:
    identifier_count = sum(len(row["facility_identifiers"]) for row in records)
    capacity_by_region: dict[str, float] = {}
    space_by_unit: dict[str, float] = {}
    for row in records:
        region = row["region"]
        capacity = row["marketed_scale"]["total_it_capacity_mw"] or 0
        capacity_by_region[region] = round(capacity_by_region.get(region, 0) + capacity, 3)
        unit = row["marketed_scale"]["technical_it_space_unit"]
        space = row["marketed_scale"]["technical_it_space_value"]
        if unit and space is not None:
            space_by_unit[unit] = round(space_by_unit.get(unit, 0) + space, 3)
    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "source": DIRECTORY_URL,
        "coverage": {
            "official_location_pages": len(records),
            "facility_identifiers": identifier_count,
            "multi_identifier_pages": sum(
                len(row["facility_identifiers"]) > 1 for row in records
            ),
            "marketed_it_capacity_mw_by_region": capacity_by_region,
            "marketed_it_capacity_mw_global_page_sum": round(
                sum(capacity_by_region.values()), 3
            ),
            "technical_it_space_by_published_unit": space_by_unit,
        },
        "limits": [
            "The directory mixes operating, development, and future identifiers.",
            "Marketed IT capacity is not energized, leased, utilized, or billed load.",
            "Multi-identifier page totals must be counted once and never allocated without a separate source.",
            "Rack-density or AI-readiness claims do not prove installed GPU inventory.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official CyrusOne JSONL registry and summary",
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    directory_html = fetch_text(DIRECTORY_URL)
    paths = sorted(set(LOCATION_PATTERN.findall(directory_html)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(
            pool.map(lambda path: parse_location_page(path, args.accessed_on), paths)
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "cyrusone_official_location_pages.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_summary(records, args.accessed_on)
    summary_path = output_dir / "cyrusone_official_location_summary.json"
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
