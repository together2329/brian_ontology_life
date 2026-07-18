#!/usr/bin/env python3
"""Build a reproducible registry from QTS's public WordPress location API.

The API exposes language variants and mixes marketed campuses, projects in
development, and projects still in consideration.  This builder preserves those
boundaries and never treats a page-level MW statement as energized or utilized
load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


BASE_URL = "https://q.com"
POSTS_URL = (
    f"{BASE_URL}/wp-json/wp/v2/data-centers"
    "?per_page=100&orderby=title&order=asc"
)
STATUS_URL = f"{BASE_URL}/wp-json/wp/v2/data-center-status?per_page=100"
LOCATION_URL = f"{BASE_URL}/wp-json/wp/v2/datacenterlocation?per_page=100"

# The public API has no consistently populated language field.  These pairs are
# explicit page-level reconciliations based on titles, slugs, and page content.
ALTERNATE_LANGUAGE_TO_CANONICAL = {
    "calatorao": "calatorao-en",
    "netherlands-eemshaven-nl": "netherlands-eemshaven",
    "netherlands-groningen-nl": "netherlands-groningen",
    "south-dallas-es": "south-dallas",
    "vimercate": "vimercate-en",
}

US_STATE_TERMS = {
    "Alabama",
    "Arizona",
    "California",
    "Colorado",
    "Florida",
    "Georgia",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "New Jersey",
    "Ohio",
    "Oregon",
    "Pennsylvania",
    "South Carolina",
    "Texas",
    "Utah",
    "Virginia",
    "Wisconsin",
}
COUNTRY_BY_LOCATION_TERM = {
    "Finland": "FI",
    "Italy": "IT",
    "Netherlands": "NL",
    "Spain": "ES",
    "United Kingdom": "GB",
}

NUMBER_UNIT_PATTERN = re.compile(
    r"(?<![\w.])(?:\$\s*)?\d[\d,.]*(?:\s*(?:\+|plus|more than|up to))?\s*"
    r"(?:GW|MW|MVA|kV|acres?|sq\.?\s*ft\.?|square feet|square meters?|"
    r"gallons?|million|billion|jobs?)\b",
    flags=re.I,
)
CAPACITY_PATTERN = re.compile(
    r"(?<![\w.])(?P<value>\d[\d,.]*)\s*(?P<plus>\+|plus|more than|up to)?\s*"
    r"(?P<unit>GW|MW|MVA)\b",
    flags=re.I,
)
AREA_PATTERN = re.compile(
    r"(?<![\w.])(?P<value>\d[\d,.]*)\s*(?P<plus>\+|plus|more than|up to)?\s*"
    r"(?P<unit>acres?|sq\.?\s*ft\.?|square feet|square meters?)\b",
    flags=re.I,
)
MONEY_PATTERN = re.compile(
    r"\$\s*(?P<value>\d[\d,.]*)\s*(?P<unit>billion|million)\b",
    flags=re.I,
)
WATER_VOLUME_PATTERN = re.compile(
    r"(?<![\w.])(?P<value>\d[\d,.]*)\s*(?P<unit>million\s+gallons?|gallons?)\b",
    flags=re.I,
)
ADDRESS_PATTERN = re.compile(
    r"\b\d{1,6}\s+[^\n]{2,100}\b(?:Road|Rd\.?|Drive|Dr\.?|Street|St\.?|"
    r"Avenue|Ave\.?|Boulevard|Blvd\.?|Highway|Hwy\.?|Lane|Ln\.?|Way|Parkway|"
    r"Pkwy\.?|Place|Pl\.?|Circle|Court|Ct\.?)\b",
    flags=re.I,
)

EVIDENCE_PATTERNS = {
    "scale_and_capacity": re.compile(
        r"\b(?:GW|MW|MVA|acre|square feet|sq\.?\s*ft|capacity|campus footprint|"
        r"building|data hall)\b",
        flags=re.I,
    ),
    "address_and_location": re.compile(
        r"\b(?:address|located|location|Road|Drive|Street|Avenue|Boulevard|"
        r"Highway|Parkway|County|City)\b",
        flags=re.I,
    ),
    "power_and_resilience": re.compile(
        r"\b(?:power|electric|electricity|utility|substation|transformer|"
        r"switchgear|UPS|generator|battery|redundan|carbon-free|renewable)\b",
        flags=re.I,
    ),
    "cooling_and_water": re.compile(
        r"\b(?:cooling|water|chiller|refrigerant|liquid|closed-loop|PUE|WUE|"
        r"humidification|gallons?)\b",
        flags=re.I,
    ),
    "lifecycle_and_phasing": re.compile(
        r"\b(?:construction|under construction|coming online|operational|"
        r"development|consideration|planning|planned|approved|approval|phase|"
        r"phased|build-out|completion|timeline|break ground)\b",
        flags=re.I,
    ),
    "economics_jobs_and_tax": re.compile(
        r"(?:\$|\b(?:investment|investing|economic|tax|revenue|jobs?|employees?|"
        r"workforce|billion|million)\b)",
        flags=re.I,
    ),
}


def fetch_json(url: str) -> list[dict]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_text(value: str) -> str:
    return " ".join(html.unescape(value).replace("\xa0", " ").split())


def stable_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        value = normalize_text(value)
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


class ContentExtractor(HTMLParser):
    """Collect visible text chunks and links from Elementor post content."""

    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.text_chunks: list[str] = []
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.add(urllib.parse.urljoin(BASE_URL, html.unescape(href)))

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            value = normalize_text(data)
            if value:
                self.text_chunks.append(value)


def content_before_resource_feed(lines: list[str]) -> list[str]:
    for index, value in enumerate(lines):
        if value == "Resources":
            return lines[:index]
    return lines


def context_snippets(text: str, pattern: re.Pattern, radius: int = 100) -> list[str]:
    snippets = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        snippets.append(text[start:end].strip(" ,;:-"))
    return stable_unique(snippets)


def structured_mentions(text: str, pattern: re.Pattern, radius: int = 90) -> list[dict]:
    mentions = []
    seen = set()
    for match in pattern.finditer(text):
        context = text[
            max(0, match.start() - radius) : min(len(text), match.end() + radius)
        ].strip(" ,;:-")
        key = (match.group(0).lower(), context)
        if key in seen:
            continue
        seen.add(key)
        item = {
            "raw": normalize_text(match.group(0)),
            "value": float(match.group("value").replace(",", "")),
            "unit": normalize_text(match.group("unit")).lower(),
            "context": normalize_text(context),
        }
        if "plus" in match.groupdict():
            qualifier = match.group("plus")
            item["qualifier"] = normalize_text(qualifier).lower() if qualifier else None
        mentions.append(item)
    return mentions


def infer_language(post: dict) -> str:
    slug = post["slug"]
    title = normalize_text(post["title"]["rendered"])
    if slug.endswith("-nl") or title.endswith("(NL)"):
        return "nl"
    if slug.endswith("-es") or title.endswith("-ES"):
        return "es"
    if title.endswith("-IT"):
        return "it"
    return "en"


def lifecycle_from_terms(term_ids: list[int], status_terms: dict[int, dict]) -> str:
    slugs = {status_terms[term_id]["slug"] for term_id in term_ids if term_id in status_terms}
    if "in-development" in slugs:
        return "in_development_taxonomy"
    if "in-consideration" in slugs:
        return "in_consideration_taxonomy"
    return "not_status_taxonomy_tagged"


def country_for_location_term(location_term: str | None) -> str | None:
    if location_term in US_STATE_TERMS:
        return "US"
    return COUNTRY_BY_LOCATION_TERM.get(location_term)


def extract_record(
    post: dict,
    alternate_posts: list[dict],
    status_terms: dict[int, dict],
    location_terms: dict[int, dict],
    accessed_on: str,
) -> dict:
    extractor = ContentExtractor()
    rendered = post.get("content", {}).get("rendered", "")
    extractor.feed(rendered)
    all_lines = stable_unique(extractor.text_chunks)
    evidence_lines = content_before_resource_feed(all_lines)
    evidence_text = " ".join(evidence_lines)

    location_names = [
        location_terms[term_id]["name"]
        for term_id in post.get("datacenterlocation", [])
        if term_id in location_terms
    ]
    location_term = location_names[0] if len(location_names) == 1 else None
    taxonomy_ids = post.get("data-center-status", [])
    lifecycle = lifecycle_from_terms(taxonomy_ids, status_terms)

    evidence = {
        category: stable_unique(
            [line for line in evidence_lines if pattern.search(line)]
        )
        for category, pattern in EVIDENCE_PATTERNS.items()
    }
    numeric_context = context_snippets(evidence_text, NUMBER_UNIT_PATTERN)
    address_context = stable_unique(
        [line for line in evidence_lines if ADDRESS_PATTERN.search(line)]
    )
    linked_pdf_urls = sorted(
        url
        for url in extractor.links
        if re.search(r"\.pdf(?:$|\?)", url, flags=re.I)
    )

    return {
        "schema_version": 1,
        "object_type": "OperatorOfficialLocationPage",
        "operator": "QTS",
        "accessed_on": accessed_on,
        "wordpress_post_id": post["id"],
        "slug": post["slug"],
        "title": normalize_text(post["title"]["rendered"]),
        "source_url": post["link"],
        "wordpress_modified": post.get("modified"),
        "language": infer_language(post),
        "alternate_language_pages": [
            {
                "wordpress_post_id": alternate["id"],
                "slug": alternate["slug"],
                "title": normalize_text(alternate["title"]["rendered"]),
                "source_url": alternate["link"],
                "language": infer_language(alternate),
            }
            for alternate in sorted(alternate_posts, key=lambda row: row["slug"])
        ],
        "taxonomy": {
            "lifecycle": lifecycle,
            "status_terms": [
                status_terms[term_id]["name"]
                for term_id in taxonomy_ids
                if term_id in status_terms
            ],
            "location_terms": location_names,
            "country_code_derived_from_location_term": country_for_location_term(location_term),
        },
        "operator_page_description": normalize_text(
            post.get("yoast_head_json", {}).get("og_description", "")
        ),
        "evidence": {
            **evidence,
            "numeric_context": numeric_context,
            "address_mentions": address_context,
        },
        "structured_mentions": {
            "capacity": structured_mentions(evidence_text, CAPACITY_PATTERN),
            "area": structured_mentions(evidence_text, AREA_PATTERN),
            "investment_and_money": structured_mentions(evidence_text, MONEY_PATTERN),
            "water_volume": structured_mentions(evidence_text, WATER_VOLUME_PATTERN),
        },
        "official_linked_pdf_urls": linked_pdf_urls,
        "visible_evidence_text_sha256": hashlib.sha256(
            evidence_text.encode("utf-8")
        ).hexdigest(),
        "disclosure_boundary": {
            "directory_lifecycle": "taxonomy_and_current_marketing_content_not_proof_of_energized_leased_utilized_or_billed_load",
            "capacity": "all_numeric_mentions_retain_page_context_and_are_not_automatically_summed",
            "accelerators": "GPU_models_counts_servers_racks_owners_customers_installation_utilization_and_power_draw_undisclosed_unless_separately_sourced",
            "equipment": "only_items_explicitly_named_in_operator_evidence_are_observed",
        },
    }


def build_summary(records: list[dict], source_post_count: int, accessed_on: str) -> dict:
    lifecycle_counts = Counter(row["taxonomy"]["lifecycle"] for row in records)
    country_counts = Counter(
        row["taxonomy"]["country_code_derived_from_location_term"] or "unresolved"
        for row in records
    )
    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "data_center_posts": POSTS_URL,
            "status_terms": STATUS_URL,
            "location_terms": LOCATION_URL,
        },
        "coverage": {
            "wordpress_published_records": source_post_count,
            "alternate_language_records_removed": len(ALTERNATE_LANGUAGE_TO_CANONICAL),
            "canonical_physical_location_candidates": len(records),
            "lifecycle_taxonomy_counts": dict(sorted(lifecycle_counts.items())),
            "country_counts": dict(sorted(country_counts.items())),
            "records_with_numeric_context": sum(
                bool(row["evidence"]["numeric_context"]) for row in records
            ),
            "records_with_address_mentions": sum(
                bool(row["evidence"]["address_mentions"]) for row in records
            ),
            "official_linked_pdf_urls": len(
                {
                    url
                    for row in records
                    for url in row["official_linked_pdf_urls"]
                }
            ),
        },
        "limits": [
            "The catalog mixes marketed campuses, in-development projects, and in-consideration concepts.",
            "An untagged page is not independent proof that every building is operating or fully energized.",
            "Page-level MW statements can describe current, planned, future, gross, or building-specific capacity and must retain their context.",
            "Campus pages are not a one-for-one reconciliation to QTS's more-than-75 data-center or building claim.",
            "AI or liquid-cooling readiness does not prove installed GPU inventory.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official QTS JSONL registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    posts = fetch_json(POSTS_URL)
    status_terms = {row["id"]: row for row in fetch_json(STATUS_URL)}
    location_terms = {row["id"]: row for row in fetch_json(LOCATION_URL)}
    posts_by_slug = {row["slug"]: row for row in posts}

    unknown_duplicate_targets = sorted(
        {
            slug
            for pair in ALTERNATE_LANGUAGE_TO_CANONICAL.items()
            for slug in pair
            if slug not in posts_by_slug
        }
    )
    if unknown_duplicate_targets:
        raise RuntimeError(
            f"Expected language-variant slugs missing from API: {unknown_duplicate_targets}"
        )

    alternates_by_canonical: dict[str, list[dict]] = {}
    for alternate_slug, canonical_slug in ALTERNATE_LANGUAGE_TO_CANONICAL.items():
        alternates_by_canonical.setdefault(canonical_slug, []).append(
            posts_by_slug[alternate_slug]
        )

    records = [
        extract_record(
            post,
            alternates_by_canonical.get(post["slug"], []),
            status_terms,
            location_terms,
            args.accessed_on,
        )
        for post in posts
        if post["slug"] not in ALTERNATE_LANGUAGE_TO_CANONICAL
    ]
    records.sort(key=lambda row: row["slug"])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "qts_official_location_pages.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_summary(records, len(posts), args.accessed_on)
    summary_path = output_dir / "qts_official_location_summary.json"
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
