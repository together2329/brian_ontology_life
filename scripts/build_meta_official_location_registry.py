#!/usr/bin/env python3
"""Build a reproducible Meta data-center location registry.

Meta's current public directory mixes long-running campuses and newly announced
projects without a lifecycle field.  The 2025 Environmental Data Index provides
a separate calendar-2024 boundary: owned, online data centers are reported by
site, while leased facilities remain aggregated.  This builder preserves both
denominators and never treats a directory card, campus, or investment statement
as one operating physical building or as current energized IT load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


DIRECTORY_URL = "https://datacenters.atmeta.com/all-locations/"
ENVIRONMENTAL_INDEX_URL = (
    "https://sustainability.atmeta.com/wp-content/uploads/2025/10/"
    "Meta_2025-Environmental-Data-Index.pdf"
)
STURGEON_ANNOUNCEMENT_URL = (
    "https://about.fb.com/news/2026/07/"
    "breaking-ground-on-metas-first-data-center-in-canada/"
)
TULSA_ANNOUNCEMENT_URL = (
    "https://about.fb.com/news/2026/04/"
    "breaking-ground-new-ai-optimized-data-center-tulsa-oklahoma/"
)

ENVIRONMENTAL_SITE_LABELS = {
    "Altoona": "Altoona (IA)",
    "Clonee": "Clonee (Ireland)",
    "DeKalb": "DeKalb (IL)",
    "Eagle Mountain": "Eagle Mountain (UT)",
    "Forest City": "Forest City (NC)",
    "Fort Worth": "Fort Worth (TX)",
    "Gallatin": "Gallatin (TN)",
    "Henrico": "Henrico (VA)",
    "Huntsville": "Huntsville (AL)",
    "Kansas City": "Kansas City (MO)",
    "Los Lunas": "Los Lunas (NM)",
    "Luleå": "Luleå (Sweden)",
    "Mesa": "Mesa (AZ)",
    "New Albany": "New Albany (OH)",
    "Odense": "Odense (Denmark)",
    "Prineville": "Prineville (OR)",
    "Sarpy": "Sarpy (NE)",
    "Stanton Springs": "Stanton Springs (GA)",
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


def canonical_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", normalize_text(value))
    value = "".join(
        character for character in value if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def slugify(value: str) -> str:
    return canonical_name(value).replace(" ", "_")


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def class_names(attrs) -> set[str]:
    return set(dict(attrs).get("class", "").split())


class MetaDirectoryParser(HTMLParser):
    """Capture Meta's region headings and data-center cards."""

    def __init__(self) -> None:
        super().__init__()
        self.current_group: str | None = None
        self.group_buffer: list[str] | None = None
        self.card: dict | None = None
        self.field: str | None = None
        self.field_tag: str | None = None
        self.field_buffer: list[str] = []
        self.cards: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        classes = class_names(attrs)
        if tag == "h2" and "data-center-location-header" in classes:
            self.group_buffer = []
            return

        if tag == "article" and "wp-block-fbdc-card" in classes:
            if self.card is not None:
                raise RuntimeError("Nested Meta directory card")
            if not self.current_group:
                raise RuntimeError("Meta directory card appeared before a region heading")
            self.card = {
                "region_group": self.current_group,
                "eyebrow_raw": None,
                "location_name": None,
                "excerpt_raw": None,
                "detail_url": None,
                "facebook_url": None,
                "image_url": None,
                "image_alt": None,
            }
            return

        if self.card is None:
            return

        field = None
        if tag == "p" and "card__eyebrow-text" in classes:
            field = "eyebrow_raw"
        elif tag == "h3" and "card__title" in classes:
            field = "location_name"
        elif tag == "p" and "card__excerpt" in classes:
            field = "excerpt_raw"
        if field:
            self.field = field
            self.field_tag = tag
            self.field_buffer = []
        elif tag == "br" and self.field:
            self.field_buffer.append("\n")

        if tag == "a" and attrs_dict.get("href"):
            if "card__primary-cta" in classes:
                self.card["detail_url"] = attrs_dict["href"]
            elif "card__follow-us-cta" in classes:
                self.card["facebook_url"] = attrs_dict["href"]
        elif tag == "img" and "card__thumbnail-image" in classes:
            self.card["image_url"] = attrs_dict.get("src")
            self.card["image_alt"] = normalize_text(attrs_dict.get("alt")) or None

    def handle_endtag(self, tag: str) -> None:
        if self.group_buffer is not None and tag == "h2":
            self.current_group = normalize_text("".join(self.group_buffer))
            self.group_buffer = None
            return

        if self.card is not None and self.field and tag == self.field_tag:
            if self.field == "excerpt_raw":
                lines = [
                    normalize_text(line)
                    for line in "".join(self.field_buffer).splitlines()
                    if normalize_text(line)
                ]
                self.card[self.field] = "\n".join(lines)
            else:
                self.card[self.field] = normalize_text("".join(self.field_buffer))
            self.field = None
            self.field_tag = None
            self.field_buffer = []

        if tag == "article" and self.card is not None:
            required = ["location_name", "eyebrow_raw", "excerpt_raw"]
            missing = [field for field in required if not self.card[field]]
            if missing:
                raise RuntimeError(
                    f"Incomplete Meta directory card {self.card!r}; missing {missing}"
                )
            self.cards.append(self.card)
            self.card = None

    def handle_data(self, data: str) -> None:
        if self.group_buffer is not None:
            self.group_buffer.append(data)
        if self.field:
            self.field_buffer.append(data)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.skip_depth:
            self.skip_depth += 1
        elif tag in {"script", "style", "svg"}:
            self.skip_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.buffer.append(data)

    def text(self) -> str:
        return normalize_text(" ".join(self.buffer))


def parse_directory(html_bytes: bytes) -> list[dict]:
    parser = MetaDirectoryParser()
    parser.feed(html_bytes.decode("utf-8"))
    if not parser.cards:
        raise RuntimeError("Meta directory contained no location cards")
    return parser.cards


def parse_published_number(value: str) -> dict:
    value = normalize_text(value)
    number_match = re.search(r"\d[\d,]*", value)
    return {
        "raw": value,
        "numeric_value": int(number_match.group(0).replace(",", ""))
        if number_match
        else None,
        "is_lower_bound": "+" in value,
        "is_approximate": "~" in value or "approximately" in value.lower(),
        "non_numeric_descriptor": value if not number_match else None,
    }


def parse_card_facts(card: dict) -> dict:
    excerpt = normalize_text(card["excerpt_raw"])
    investment_match = re.search(r"^(.+?)\s+investment\b", excerpt, re.IGNORECASE)
    year_match = re.search(r"\b(\d{4})\s+break ground\b", excerpt, re.IGNORECASE)
    workers_match = re.search(
        r"break ground\s+(.+?)\s+(?:skilled\s+)?trade workers on site at peak construction",
        excerpt,
        re.IGNORECASE,
    )
    jobs_match = re.search(
        r"peak construction\s+(.+?)\s+operational jobs supported once completed",
        excerpt,
        re.IGNORECASE,
    )
    if not all([investment_match, year_match, workers_match, jobs_match]):
        raise RuntimeError(
            f"Could not parse Meta directory facts for {card['location_name']}: {excerpt!r}"
        )

    investment_raw = normalize_text(investment_match.group(1))
    amount_match = re.search(
        r"(\d+(?:\.\d+)?)\s+(billion|million)", investment_raw, re.IGNORECASE
    )
    if not amount_match:
        raise RuntimeError(f"Could not parse Meta investment amount: {investment_raw!r}")
    currency = None
    for marker, code in [
        ("CA$", "CAD"),
        ("S$", "SGD"),
        ("€", "EUR"),
        ("DKK", "DKK"),
        ("SEK", "SEK"),
        ("$", "USD"),
    ]:
        if marker in investment_raw:
            currency = code
            break
    if not currency:
        raise RuntimeError(f"Could not parse Meta investment currency: {investment_raw!r}")
    amount = float(amount_match.group(1))
    unit = amount_match.group(2).lower()
    amount_billion = amount if unit == "billion" else amount / 1000

    return {
        "investment": {
            "raw": investment_raw,
            "currency": currency,
            "amount_billion": amount_billion,
            "is_lower_bound": "+" in investment_raw,
            "boundary": "Published project investment is not incurred capex, book value, revenue, or operating capacity.",
        },
        "break_ground_year": int(year_match.group(1)),
        "peak_construction_workers": parse_published_number(workers_match.group(1)),
        "operational_jobs_once_completed": parse_published_number(jobs_match.group(1)),
    }


def pdf_bytes_to_text(pdf_bytes: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="meta-environmental-index-") as directory:
        pdf_path = Path(directory) / "source.pdf"
        text_path = Path(directory) / "source.txt"
        pdf_path.write_bytes(pdf_bytes)
        try:
            subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(text_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                "pdftotext is required unless --environmental-text is supplied"
            ) from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"pdftotext failed: {error.stderr}") from error
        return text_path.read_text(encoding="utf-8")


def parse_last_numeric_column(section: str, label: str) -> int:
    match = re.search(
        rf"^[ \t]*{re.escape(label)}[ \t]+([^\n]+)$",
        section,
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError(f"Environmental table row not found: {label!r}")
    values = re.findall(r"(?:<|>)?\d[\d,]*|-", match.group(1))
    if len(values) < 5 or values[-1] == "-":
        raise RuntimeError(f"Unexpected environmental table values for {label!r}: {values}")
    return int(values[-1].lstrip("<>").replace(",", ""))


def parse_environmental_index(text: str) -> dict:
    electricity_start = text.find("Electricity Consumption by Facility")
    water_start = text.find("Total water withdrawal", electricity_start)
    water_end = text.find("Not included in our 2024 water withdrawal", water_start)
    if min(electricity_start, water_start, water_end) < 0:
        raise RuntimeError("Could not locate Meta environmental facility tables")
    electricity_section = text[electricity_start:water_start]
    water_section = text[water_start:water_end]

    rows = {}
    for location_name, report_label in ENVIRONMENTAL_SITE_LABELS.items():
        rows[location_name] = {
            "report_label": report_label,
            "electricity_consumption_mwh": parse_last_numeric_column(
                electricity_section, report_label
            ),
            "water_withdrawal_megaliters": parse_last_numeric_column(
                water_section, report_label
            ),
        }

    totals = {}
    for output_name, report_label in [
        ("data_centers_total", "Data centers total"),
        ("leased_data_center_facilities", "Leased data center facilities"),
        ("other_data_center_related_facilities", "Other data center-related facilities"),
    ]:
        totals[output_name] = {
            "electricity_consumption_mwh": parse_last_numeric_column(
                electricity_section, report_label
            ),
            "water_withdrawal_megaliters": parse_last_numeric_column(
                water_section, report_label
            ),
        }

    footnote = re.search(
        r"Owned, online data centers are always reported by site, even if they were below this threshold\.",
        normalize_text(text),
    )
    if not footnote:
        raise RuntimeError("Could not locate Meta owned-online reporting footnote")
    return {"site_rows": rows, "totals": totals}


def parse_announcement_counts(
    sturgeon_html: bytes,
    tulsa_html: bytes,
) -> dict:
    sturgeon_parser = VisibleTextParser()
    sturgeon_parser.feed(sturgeon_html.decode("utf-8"))
    tulsa_parser = VisibleTextParser()
    tulsa_parser.feed(tulsa_html.decode("utf-8"))
    sturgeon_match = re.search(
        r"first data center in Canada and (\d+)rd in our global fleet",
        sturgeon_parser.text(),
        re.IGNORECASE,
    )
    tulsa_match = re.search(
        r"(\d+)th in the US, and (\d+)nd in our global fleet",
        tulsa_parser.text(),
        re.IGNORECASE,
    )
    if not sturgeon_match or not tulsa_match:
        raise RuntimeError("Could not parse Meta fleet-position announcements")
    return {
        "2026-04-21_tulsa": {
            "US_fleet_position": int(tulsa_match.group(1)),
            "global_fleet_position": int(tulsa_match.group(2)),
        },
        "2026-07-08_sturgeon_county": {
            "global_fleet_position": int(sturgeon_match.group(1)),
            "first_in_canada": True,
        },
    }


def country_and_region(card: dict) -> tuple[str, str | None]:
    group = card["region_group"]
    eyebrow = normalize_text(card["eyebrow_raw"])
    if group == "United States":
        return "United States", eyebrow.title()
    if group == "Canada":
        return "Canada", None
    return eyebrow.title(), None


def build_registry(
    cards: list[dict],
    environmental: dict,
    accessed_on: str,
) -> list[dict]:
    records = []
    for card in cards:
        facts = parse_card_facts(card)
        country, subnational_region = country_and_region(card)
        environmental_row = environmental["site_rows"].get(card["location_name"])
        records.append(
            {
                "id": f"meta_data_center_location_{slugify(card['location_name'])}",
                "operator": "Meta",
                "directory_region_group": card["region_group"],
                "location_name": card["location_name"],
                "country_or_territory": country,
                "subnational_region_from_directory": subnational_region,
                "published_facts": facts,
                "lifecycle_reconciliation": {
                    "owned_online_site_reported_in_calendar_2024": bool(
                        environmental_row
                    ),
                    "current_directory_lifecycle_label": None,
                    "interpretation": (
                        "Confirmed as an owned online site in calendar 2024 by the "
                        "site-level environmental table."
                        if environmental_row
                        else "Not separately reported as an owned online site in the calendar-2024 environmental table; this does not prove the location is not operating in 2026."
                    ),
                },
                "environmental_reporting_calendar_2024": environmental_row,
                "directory_assets": {
                    "detail_url": card["detail_url"],
                    "facebook_url": card["facebook_url"],
                    "image_url": card["image_url"],
                    "image_alt": card["image_alt"],
                },
                "granularity_boundary": (
                    "A directory location can represent a multi-building campus at a mixed lifecycle stage. It is not one operating building or a disclosure of energized IT load."
                ),
                "undisclosed_or_unreconciled": [
                    "current operating, construction, commissioning, customer-acceptance, and revenue-start status",
                    "exact campus, building, street address, parcel, ownership, lease, and colocation roster",
                    "operating, energized, leased, utilized, and billed critical IT load",
                    "GPU, MTIA, and accelerator model, count, rack, fabric, ownership, and utilization by site",
                    "utility feeds, substations, transformers, switchgear, UPS, batteries, generators, cooling, and equipment OEMs",
                    "current site PUE, WUE, water, liquid-cooled MW, and hourly energy matching",
                ],
                "sources": {
                    "current_directory": DIRECTORY_URL,
                    "calendar_2024_environmental_index": ENVIRONMENTAL_INDEX_URL,
                },
                "accessed_on": accessed_on,
            }
        )

    record_ids = [record["id"] for record in records]
    if len(record_ids) != len(set(record_ids)):
        raise RuntimeError("Duplicate generated Meta registry IDs")
    return sorted(records, key=lambda row: row["id"])


def build_summary(
    records: list[dict],
    cards: list[dict],
    environmental: dict,
    announcement_counts: dict,
    accessed_on: str,
) -> dict:
    group_counts = Counter(record["directory_region_group"] for record in records)
    owned_online = sorted(
        record["location_name"]
        for record in records
        if record["lifecycle_reconciliation"][
            "owned_online_site_reported_in_calendar_2024"
        ]
    )
    not_separately_reported = sorted(
        record["location_name"]
        for record in records
        if not record["lifecycle_reconciliation"][
            "owned_online_site_reported_in_calendar_2024"
        ]
    )
    investment_by_currency = Counter()
    for record in records:
        investment = record["published_facts"]["investment"]
        investment_by_currency[investment["currency"]] += investment[
            "amount_billion"
        ]

    totals = environmental["totals"]
    site_electricity = sum(
        row["electricity_consumption_mwh"]
        for row in environmental["site_rows"].values()
    )
    site_water = sum(
        row["water_withdrawal_megaliters"]
        for row in environmental["site_rows"].values()
    )
    electricity_line_sum = (
        site_electricity
        + totals["leased_data_center_facilities"]["electricity_consumption_mwh"]
        + totals["other_data_center_related_facilities"][
            "electricity_consumption_mwh"
        ]
    )
    water_line_sum = (
        site_water
        + totals["leased_data_center_facilities"]["water_withdrawal_megaliters"]
        + totals["other_data_center_related_facilities"][
            "water_withdrawal_megaliters"
        ]
    )

    directory_evidence = [
        {
            "region_group": card["region_group"],
            "eyebrow_raw": card["eyebrow_raw"],
            "location_name": card["location_name"],
            "excerpt_raw": card["excerpt_raw"],
            "detail_url": card["detail_url"],
        }
        for card in cards
    ]
    environmental_evidence = {
        "site_rows": environmental["site_rows"],
        "totals": totals,
    }
    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "current_location_directory": DIRECTORY_URL,
            "calendar_2024_environmental_index": ENVIRONMENTAL_INDEX_URL,
            "sturgeon_county_fleet_position_announcement": STURGEON_ANNOUNCEMENT_URL,
            "tulsa_fleet_position_announcement": TULSA_ANNOUNCEMENT_URL,
            "retrieved_evidence_sha256": {
                "current_directory_cards": canonical_hash(directory_evidence),
                "calendar_2024_environmental_tables": canonical_hash(
                    environmental_evidence
                ),
                "fleet_position_counts": canonical_hash(announcement_counts),
            },
            "hash_boundary": "Hashes cover extracted stable evidence rather than full HTML or PDF bytes, whose delivery metadata can vary.",
        },
        "coverage": {
            "current_directory_location_rows": len(records),
            "directory_region_group_counts": dict(sorted(group_counts.items())),
            "directory_rows_with_detail_url": sum(
                bool(record["directory_assets"]["detail_url"]) for record in records
            ),
            "directory_rows_with_investment_year_and_job_facts": len(records),
            "calendar_2024_owned_online_site_rows": len(owned_online),
            "calendar_2024_owned_online_sites": owned_online,
            "current_directory_rows_not_separately_reported_as_owned_online_in_2024": len(
                not_separately_reported
            ),
            "current_directory_labels_not_separately_reported_as_owned_online_in_2024": not_separately_reported,
        },
        "fleet_position_reconciliation": {
            **announcement_counts,
            "current_directory_rows": len(records),
            "interpretation": "The current 33 directory rows agree with Sturgeon County's announcement as the 33rd global location; Tulsa's earlier 32nd-global/28th-US statement reconciles to the added first Canadian row.",
        },
        "investment_reconciliation": {
            "published_amount_billion_by_currency_without_fx_conversion": dict(
                sorted(investment_by_currency.items())
            ),
            "US_directory_28_location_published_investment_floor_usd_billion": investment_by_currency[
                "USD"
            ],
            "boundary": "Amounts are project announcement values at mixed lifecycle stages. Currencies are not combined, and amounts are not treated as incurred capex, current asset value, revenue, or operating capacity.",
        },
        "calendar_2024_environmental_reconciliation": {
            "owned_online_site_rows": len(owned_online),
            "owned_online_site_electricity_sum_mwh": site_electricity,
            "owned_online_site_water_withdrawal_sum_megaliters": site_water,
            "leased_facilities_aggregated": totals["leased_data_center_facilities"],
            "other_data_center_related_facilities_aggregated": totals[
                "other_data_center_related_facilities"
            ],
            "reported_data_centers_total": totals["data_centers_total"],
            "electricity_line_item_sum_mwh": electricity_line_sum,
            "reported_electricity_minus_line_item_sum_mwh": totals[
                "data_centers_total"
            ]["electricity_consumption_mwh"]
            - electricity_line_sum,
            "water_line_item_sum_megaliters": water_line_sum,
            "reported_water_minus_line_item_sum_megaliters": totals[
                "data_centers_total"
            ]["water_withdrawal_megaliters"]
            - water_line_sum,
            "rounding_boundary": "Meta states that line items are rounded and therefore may not sum exactly to reported totals.",
        },
        "lifecycle_boundary": (
            "The current directory has no operating/construction status field. "
            "The environmental report confirms 18 owned online sites in calendar "
            "2024 and aggregates leased facilities without a count. The other 15 "
            "current labels are not classified as offline; they require current "
            "site-level opening, commissioning, or operating evidence."
        ),
        "remaining_gaps": [
            "Current operating, construction, commissioning, customer-acceptance, and revenue-start status for all 33 directory labels",
            "Complete owned, leased, colocation, campus, building, address, parcel, and meter-boundary crosswalk",
            "Physical building count behind each directory location and leased-facility aggregate",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Current GPU, MTIA, accelerator, server, rack, fabric, ownership, and utilization inventory by site",
            "Per-site utility, substation, transformer, switchgear, UPS, battery, generator, cooling, and equipment OEM bill of materials",
            "Per-site current PUE, WUE, water, liquid-cooled MW, and hourly carbon-free energy matching",
            "Project investment incurred-capex, depreciation, operating-cost, and workload-return reconciliation",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official Meta registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--directory-html")
    parser.add_argument("--environmental-pdf")
    parser.add_argument("--environmental-text")
    parser.add_argument("--sturgeon-html")
    parser.add_argument("--tulsa-html")
    args = parser.parse_args()

    directory_bytes = read_or_fetch(args.directory_html, DIRECTORY_URL)
    if args.environmental_text:
        environmental_text = Path(args.environmental_text).read_text(encoding="utf-8")
    else:
        environmental_pdf = read_or_fetch(
            args.environmental_pdf, ENVIRONMENTAL_INDEX_URL
        )
        environmental_text = pdf_bytes_to_text(environmental_pdf)
    sturgeon_html = read_or_fetch(
        args.sturgeon_html, STURGEON_ANNOUNCEMENT_URL
    )
    tulsa_html = read_or_fetch(args.tulsa_html, TULSA_ANNOUNCEMENT_URL)

    cards = parse_directory(directory_bytes)
    environmental = parse_environmental_index(environmental_text)
    announcement_counts = parse_announcement_counts(sturgeon_html, tulsa_html)
    records = build_registry(cards, environmental, args.accessed_on)
    summary = build_summary(
        records,
        cards,
        environmental,
        announcement_counts,
        args.accessed_on,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "meta_official_location_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    summary_path = output_dir / "meta_official_location_summary.json"
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
                "investment_reconciliation": summary["investment_reconciliation"],
                "calendar_2024_environmental_reconciliation": summary[
                    "calendar_2024_environmental_reconciliation"
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
