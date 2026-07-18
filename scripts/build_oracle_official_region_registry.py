#!/usr/bin/env python3
"""Build a reproducible Oracle public-cloud Region registry.

Oracle's marketing table covers commercial, sovereign, and government realms,
while the OCI technical documentation provides exact identifiers, realm keys,
and Availability Domain counts for live commercial Regions.  This builder joins
those official scopes, preserves upstream code discrepancies, and never treats a
Region or Availability Domain as one physical data-center building.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path


MARKETING_URL = "https://www.oracle.com/cloud/public-cloud-regions/"
REGION_DOCS_URL = (
    "https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm"
)
PHYSICAL_COUNT_URL = (
    "https://www.oracle.com/news/announcement/blog/"
    "oracle-advances-american-ai-innovation-in-new-mexico-2026-01-23/"
)

REALMS = {"Commercial", "Sovereign", "Government"}
DOC_NAME_OVERRIDES = {
    "Malaysia West (Kulai)": "Malaysia West 2 (Kulai)",
    "Spain Central 2 (Madrid)": "Spain Central (Madrid 3)",
}
PLANNED_COUNTRY_BY_MARKETING_NAME = {
    "Kenya": "Kenya",
    "Morocco 2": "Morocco",
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
    value = "".join(character for character in value if not unicodedata.combining(character))
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


class OracleMarketingParser(HTMLParser):
    """Capture Oracle realm headings and their Region tables."""

    def __init__(self) -> None:
        super().__init__()
        self.header_depth = 0
        self.capture_realm_heading = False
        self.heading_buffer: list[str] = []
        self.current_realm: str | None = None
        self.current_table: dict | None = None
        self.current_row: list[dict] | None = None
        self.current_cell: dict | None = None
        self.tables: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if self.header_depth:
            self.header_depth += 1
            if tag == "h2":
                self.capture_realm_heading = True
                self.heading_buffer = []
        elif tag == "div" and "rc116header" in class_names(attrs):
            self.header_depth = 1

        if (
            tag == "table"
            and self.current_realm in REALMS
            and "OCI Regions" in attrs_dict.get("aria-label", "")
        ):
            self.current_table = {
                "realm": self.current_realm,
                "attrs": attrs_dict,
                "rows": [],
            }
            self.tables.append(self.current_table)
        elif self.current_table is not None and tag == "tr":
            self.current_row = []
            self.current_table["rows"].append(self.current_row)
        elif self.current_row is not None and tag in {"td", "th"}:
            self.current_cell = {
                "tag": tag,
                "attrs": attrs_dict,
                "buffer": [],
            }
            self.current_row.append(self.current_cell)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.capture_realm_heading:
            heading = normalize_text("".join(self.heading_buffer))
            self.current_realm = heading
            self.capture_realm_heading = False
            self.heading_buffer = []
        if self.header_depth:
            self.header_depth -= 1

        if tag in {"td", "th"}:
            self.current_cell = None
        elif tag == "tr":
            self.current_row = None
        elif tag == "table" and self.current_table is not None:
            self.current_table = None

    def handle_data(self, data: str) -> None:
        if self.capture_realm_heading:
            self.heading_buffer.append(data)
        if self.current_cell is not None:
            self.current_cell["buffer"].append(data)


class GenericTableParser(HTMLParser):
    """Capture all simple HTML tables, retaining cell attributes."""

    def __init__(self) -> None:
        super().__init__()
        self.current_table: dict | None = None
        self.current_row: list[dict] | None = None
        self.current_cell: dict | None = None
        self.tables: list[dict] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self.current_table = {"attrs": dict(attrs), "rows": []}
            self.tables.append(self.current_table)
        elif self.current_table is not None and tag == "tr":
            self.current_row = []
            self.current_table["rows"].append(self.current_row)
        elif self.current_row is not None and tag in {"td", "th"}:
            self.current_cell = {
                "tag": tag,
                "attrs": dict(attrs),
                "buffer": [],
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
            self.current_cell["buffer"].append(data)


class VisibleTextParser(HTMLParser):
    """Collect page text while excluding executable and SVG payloads."""

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


def cell_text(cell: dict) -> str:
    return normalize_text("".join(cell["buffer"]))


def parse_marketing_page(html_bytes: bytes) -> tuple[list[dict], dict]:
    html_text = html_bytes.decode("utf-8")
    parser = OracleMarketingParser()
    parser.feed(html_text)
    rows = []
    for table in parser.tables:
        table_rows = table["rows"]
        if not table_rows:
            continue
        headers = [cell_text(cell) for cell in table_rows[0]]
        if "Status" not in headers:
            continue
        status_index = headers.index("Status")
        azure_index = (
            headers.index("Oracle Interconnect for Azure")
            if "Oracle Interconnect for Azure" in headers
            else None
        )
        google_index = (
            headers.index("Oracle Interconnect for Google Cloud")
            if "Oracle Interconnect for Google Cloud" in headers
            else None
        )
        geography = headers[0]
        for html_row in table_rows[1:]:
            values = [cell_text(cell) for cell in html_row]
            if not values or not values[0] or len(values) <= status_index:
                continue
            first_cell = html_row[0]
            rows.append(
                {
                    "realm_scope": table["realm"].lower(),
                    "geography_section": geography,
                    "marketing_name": values[0],
                    "marketing_region_code_raw": normalize_text(
                        first_cell["attrs"].get("geo-data")
                    )
                    or None,
                    "status": values[status_index].lower().replace(" ", "_"),
                    "oracle_interconnect_for_azure": values[azure_index].lower()
                    if azure_index is not None and len(values) > azure_index
                    else None,
                    "oracle_interconnect_for_google_cloud": values[google_index].lower()
                    if google_index is not None and len(values) > google_index
                    else None,
                }
            )

    visible_parser = VisibleTextParser()
    visible_parser.feed(html_text)
    visible_text = visible_parser.text()
    headline_match = re.search(
        r"services from (50\+) public cloud regions across (\d+) countries",
        visible_text,
        re.IGNORECASE,
    )
    legacy_match = re.search(
        r"(41) cloud regions (26) countries",
        visible_text,
        re.IGNORECASE,
    )
    if not headline_match or not legacy_match:
        raise RuntimeError("Could not parse both Oracle current and legacy headlines")
    headlines = {
        "current_public_region_claim": headline_match.group(1),
        "current_country_claim": int(headline_match.group(2)),
        "legacy_region_claim_same_page": int(legacy_match.group(1)),
        "legacy_country_claim_same_page": int(legacy_match.group(2)),
    }
    return rows, headlines


def parse_region_docs(html_bytes: bytes) -> list[dict]:
    parser = GenericTableParser()
    parser.feed(html_bytes.decode("utf-8"))
    expected_headers = [
        "Region Name",
        "Region Identifier",
        "Region Location",
        "Region Key",
        "Realm Key",
        "Availability Domains",
    ]
    matches = []
    for table in parser.tables:
        if not table["rows"]:
            continue
        headers = [cell_text(cell) for cell in table["rows"][0]]
        if headers == expected_headers:
            matches.append(table)
    if len(matches) != 1:
        raise RuntimeError(f"Expected one OCI commercial Region table, found {len(matches)}")

    rows = []
    for html_row in matches[0]["rows"][1:]:
        values = [cell_text(cell) for cell in html_row]
        if len(values) != 6:
            raise RuntimeError(f"Unexpected OCI Region documentation row: {values!r}")
        try:
            availability_domains = int(values[5])
        except ValueError as error:
            raise RuntimeError(f"Invalid Availability Domain count: {values!r}") from error
        rows.append(
            {
                "region_name": values[0],
                "region_identifier": values[1],
                "region_location": values[2],
                "region_key": values[3],
                "realm_key": values[4],
                "availability_domain_count": availability_domains,
            }
        )
    if not rows:
        raise RuntimeError("OCI technical Region table contained no rows")
    return rows


def parse_physical_count_claim(html_bytes: bytes) -> dict:
    parser = VisibleTextParser()
    parser.feed(html_bytes.decode("utf-8"))
    match = re.search(
        r"With (\d+) active data centers around the world, and (\d+) more on the way",
        parser.text(),
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Could not parse Oracle physical data-center count claim")
    return {
        "active_data_centers": int(match.group(1)),
        "data_centers_on_the_way": int(match.group(2)),
        "claim_date": "2026-01-23",
    }


def country_from_doc_location(region_name: str, location: str) -> str:
    if region_name.startswith("US "):
        return "United States"
    suffix = normalize_text(location.rsplit(",", 1)[-1])
    return {"UAE": "United Arab Emirates"}.get(suffix, suffix)


def build_registry(
    marketing_rows: list[dict],
    docs_rows: list[dict],
    accessed_on: str,
) -> list[dict]:
    docs_by_name = {canonical_name(row["region_name"]): row for row in docs_rows}
    if len(docs_by_name) != len(docs_rows):
        raise RuntimeError("Duplicate names in OCI technical Region table")

    matched_doc_names = set()
    records = []
    for marketing in marketing_rows:
        docs = None
        if marketing["realm_scope"] == "commercial" and marketing["status"] == "live":
            docs_name = DOC_NAME_OVERRIDES.get(
                marketing["marketing_name"], marketing["marketing_name"]
            )
            docs = docs_by_name.get(canonical_name(docs_name))
            if not docs:
                raise RuntimeError(
                    f"No OCI technical Region match for {marketing['marketing_name']!r}"
                )
            matched_doc_names.add(docs["region_name"])

        raw_code = marketing["marketing_region_code_raw"]
        documented_code = docs["region_identifier"] if docs else None
        if documented_code and raw_code == documented_code:
            code_status = "marketing_matches_technical_docs"
        elif documented_code and raw_code:
            code_status = "marketing_conflicts_with_technical_docs"
        elif documented_code:
            code_status = "marketing_missing_code_technical_docs_supplies_it"
        elif raw_code:
            code_status = "marketing_only_code_not_joined_to_commercial_docs"
        else:
            code_status = "programmatic_code_not_publicly_resolved_in_reviewed_sources"

        identifier_basis = documented_code or raw_code or marketing["marketing_name"]
        country = (
            country_from_doc_location(docs["region_name"], docs["region_location"])
            if docs
            else PLANNED_COUNTRY_BY_MARKETING_NAME.get(marketing["marketing_name"])
        )
        record = {
            "id": (
                f"oracle_oci_region_{marketing['realm_scope']}_"
                f"{slugify(identifier_basis)}"
            ),
            "operator": "Oracle",
            "realm_scope": marketing["realm_scope"],
            "geography_section": marketing["geography_section"],
            "marketing_name": marketing["marketing_name"],
            "marketing_status": marketing["status"],
            "programmatic_metadata": {
                "marketing_region_code_raw": raw_code,
                "documented_region_name": docs["region_name"] if docs else None,
                "documented_region_identifier": documented_code,
                "documented_region_location": docs["region_location"] if docs else None,
                "documented_region_key": docs["region_key"] if docs else None,
                "documented_realm_key": docs["realm_key"] if docs else None,
                "availability_domain_count": docs["availability_domain_count"]
                if docs
                else None,
                "code_reconciliation_status": code_status,
            },
            "country_or_territory": country,
            "country_or_territory_basis": (
                "technical_documentation_location"
                if docs
                else (
                    "explicit_marketing_name"
                    if marketing["marketing_name"] in PLANNED_COUNTRY_BY_MARKETING_NAME
                    else None
                )
            ),
            "multicloud_interconnect": {
                "oracle_interconnect_for_azure": marketing[
                    "oracle_interconnect_for_azure"
                ],
                "oracle_interconnect_for_google_cloud": marketing[
                    "oracle_interconnect_for_google_cloud"
                ],
            },
            "granularity_boundary": (
                "A Region is a provider geography. An Availability Domain is one "
                "or more data centers, so neither field is one physical building."
            ),
            "undisclosed_or_unreconciled": [
                "physical campus and building roster behind Region and Availability Domain",
                "street address, parcel, ownership, lease, and colocation mapping",
                "operating, energized, leased, utilized, and billed IT MW",
                "GPU and accelerator model, count, rack, fabric, and utilization by site",
                "utility feeds, substations, transformers, switchgear, UPS, batteries, generators, cooling, and equipment OEMs",
                "commissioning, customer-acceptance, and revenue-start dates",
            ],
            "sources": {
                "marketing": MARKETING_URL,
                "technical_docs": REGION_DOCS_URL if docs else None,
            },
            "accessed_on": accessed_on,
        }
        records.append(record)

    if matched_doc_names != {row["region_name"] for row in docs_rows}:
        raise RuntimeError(
            "Unmatched OCI technical Region rows: "
            f"{sorted({row['region_name'] for row in docs_rows} - matched_doc_names)}"
        )
    record_ids = [record["id"] for record in records]
    if len(record_ids) != len(set(record_ids)):
        duplicates = [name for name, count in Counter(record_ids).items() if count > 1]
        raise RuntimeError(f"Duplicate generated Oracle registry IDs: {duplicates}")
    return sorted(records, key=lambda row: row["id"])


def build_summary(
    records: list[dict],
    marketing_rows: list[dict],
    docs_rows: list[dict],
    headlines: dict,
    physical_claim: dict,
    accessed_on: str,
) -> dict:
    realm_status = Counter(
        f"{row['realm_scope']}:{row['marketing_status']}" for row in records
    )
    doc_code_status = Counter(
        row["programmatic_metadata"]["code_reconciliation_status"]
        for row in records
        if row["realm_scope"] == "commercial" and row["marketing_status"] == "live"
    )
    availability_domains = Counter(
        row["availability_domain_count"] for row in docs_rows
    )
    country_values = sorted(
        {
            country_from_doc_location(row["region_name"], row["region_location"])
            for row in docs_rows
        }
    )
    live_and_planned_commercial_country_values = sorted(
        {
            record["country_or_territory"]
            for record in records
            if record["realm_scope"] == "commercial"
            and record["country_or_territory"]
        }
    )
    anomalies = []
    for record in records:
        metadata = record["programmatic_metadata"]
        if metadata["code_reconciliation_status"] in {
            "marketing_conflicts_with_technical_docs",
            "marketing_missing_code_technical_docs_supplies_it",
        }:
            anomalies.append(
                {
                    "marketing_name": record["marketing_name"],
                    "marketing_region_code_raw": metadata[
                        "marketing_region_code_raw"
                    ],
                    "documented_region_name": metadata["documented_region_name"],
                    "documented_region_identifier": metadata[
                        "documented_region_identifier"
                    ],
                    "handling": "technical_documentation_identifier_selected_marketing_value_preserved",
                }
            )

    raw_code_groups: dict[str, list[str]] = defaultdict(list)
    for record in records:
        raw_code = record["programmatic_metadata"]["marketing_region_code_raw"]
        if raw_code:
            raw_code_groups[raw_code].append(
                f"{record['realm_scope']}:{record['marketing_name']}"
            )
    collisions = {
        code: sorted(labels)
        for code, labels in sorted(raw_code_groups.items())
        if len(labels) > 1
    }
    interconnect_counts = {
        provider: dict(
            sorted(
                Counter(
                    record["multicloud_interconnect"][provider] or "blank_or_not_applicable"
                    for record in records
                    if record["realm_scope"] == "commercial"
                    and record["marketing_status"] == "live"
                ).items()
            )
        )
        for provider in [
            "oracle_interconnect_for_azure",
            "oracle_interconnect_for_google_cloud",
        ]
    }

    marketing_evidence = [
        {
            key: row[key]
            for key in [
                "realm_scope",
                "geography_section",
                "marketing_name",
                "marketing_region_code_raw",
                "status",
                "oracle_interconnect_for_azure",
                "oracle_interconnect_for_google_cloud",
            ]
        }
        for row in marketing_rows
    ]
    docs_evidence = sorted(docs_rows, key=lambda row: row["region_identifier"])

    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "public_cloud_region_marketing_table": MARKETING_URL,
            "commercial_region_technical_documentation": REGION_DOCS_URL,
            "physical_data_center_count_claim": PHYSICAL_COUNT_URL,
            "retrieved_evidence_sha256": {
                "marketing_region_tables": canonical_hash(marketing_evidence),
                "marketing_headlines": canonical_hash(headlines),
                "commercial_region_technical_table": canonical_hash(docs_evidence),
                "physical_data_center_count_claim": canonical_hash(physical_claim),
            },
            "hash_boundary": "Hashes cover extracted stable evidence rather than full HTML, whose runtime scripts and delivery metadata can vary.",
        },
        "coverage": {
            "marketing_region_rows_total": len(records),
            "realm_and_status_counts": dict(sorted(realm_status.items())),
            "live_region_rows_all_reviewed_realms": sum(
                record["marketing_status"] == "live" for record in records
            ),
            "planned_region_rows": sum(
                record["marketing_status"] != "live" for record in records
            ),
            "commercial_live_rows_joined_to_technical_docs": len(docs_rows),
            "commercial_country_or_territory_count_from_docs": len(country_values),
            "commercial_countries_or_territories_from_docs": country_values,
            "commercial_live_and_planned_country_or_territory_count": len(
                live_and_planned_commercial_country_values
            ),
            "commercial_live_and_planned_countries_or_territories": (
                live_and_planned_commercial_country_values
            ),
            "commercial_availability_domain_total": sum(
                row["availability_domain_count"] for row in docs_rows
            ),
            "commercial_region_count_by_availability_domains": {
                str(count): regions for count, regions in sorted(availability_domains.items())
            },
            "commercial_regions_with_three_availability_domains": sorted(
                row["region_name"]
                for row in docs_rows
                if row["availability_domain_count"] == 3
            ),
            "commercial_realm_key_counts": dict(
                sorted(Counter(row["realm_key"] for row in docs_rows).items())
            ),
            "commercial_code_reconciliation_counts": dict(sorted(doc_code_status.items())),
            "commercial_interconnect_markers": interconnect_counts,
        },
        "marketing_headline_reconciliation": {
            **headlines,
            "current_live_rows_across_commercial_sovereign_and_government_tables": sum(
                record["marketing_status"] == "live" for record in records
            ),
            "live_commercial_country_or_territory_count": len(country_values),
            "live_and_planned_commercial_country_or_territory_count": len(
                live_and_planned_commercial_country_values
            ),
            "country_scope_reconciliation": (
                "The 45 live commercial Regions cover 27 countries or territories. "
                "Adding the two coming-soon rows adds Kenya but no new country for "
                "Morocco 2, producing the marketed 28-country reach."
            ),
            "interpretation": (
                "The 50-plus claim is compatible with the 55 live rows across the "
                "reviewed commercial, sovereign, and government tables. The "
                "28-country claim matches the live-plus-planned commercial scope, "
                "not the 27-country live commercial scope. The 41/26 statement is "
                "stale content retained on the same page."
            ),
        },
        "physical_scope_reconciliation": {
            **physical_claim,
            "commercial_availability_domains_documented": sum(
                row["availability_domain_count"] for row in docs_rows
            ),
            "commercial_physical_data_center_lower_bound": sum(
                row["availability_domain_count"] for row in docs_rows
            ),
            "boundary": (
                "Each Availability Domain contains one or more data centers, so "
                "55 is only a commercial-realm physical lower bound. The 147-active "
                "company claim can include multiple buildings per Availability Domain "
                "and other public, dedicated, government, partner, or distributed-cloud "
                "scopes; no residual building count is inferred."
            ),
        },
        "marketing_code_anomalies": anomalies,
        "marketing_raw_code_collisions": collisions,
        "interpretation": {
            "hyderabad_and_batam": "The marketing geo-data values are swapped; the technical documentation identifiers ap-hyderabad-1 and ap-batam-1 are selected for their named Regions.",
            "madrid_second_row": "The marketing table says Spain Central 2 and reuses eu-madrid-1, while technical documentation says Spain Central (Madrid 3) with eu-madrid-3. Both labels are preserved and the technical identifier is selected.",
            "region_and_building_boundary": "Marketing rows, programmatic Regions, Availability Domains, and physical data centers are different denominators and are not ranked as equivalent fleet counts.",
        },
        "remaining_gaps": [
            "Complete mapping of 147 active and 64 planned physical data centers to public, sovereign, government, dedicated, multicloud, and partner realms",
            "Physical campus, building, address, parcel, ownership, lease, and colocation mapping behind each Region and Availability Domain",
            "Programmatic identifiers and Availability Domain counts for sovereign and government rows",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Per-site live GPU and accelerator model, count, rack, fabric, and utilization inventory",
            "Per-site utility, substation, transformer, switchgear, UPS, battery, generator, cooling, and equipment OEM bill of materials",
            "Construction, commissioning, customer-acceptance, and revenue-start dates",
            "Removal or timestamping of the stale 41-region/26-country statement and correction of marketing geo-data anomalies",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official Oracle registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--marketing-html")
    parser.add_argument("--region-docs-html")
    parser.add_argument("--physical-count-html")
    args = parser.parse_args()

    marketing_bytes = read_or_fetch(args.marketing_html, MARKETING_URL)
    docs_bytes = read_or_fetch(args.region_docs_html, REGION_DOCS_URL)
    physical_bytes = read_or_fetch(args.physical_count_html, PHYSICAL_COUNT_URL)

    marketing_rows, headlines = parse_marketing_page(marketing_bytes)
    docs_rows = parse_region_docs(docs_bytes)
    physical_claim = parse_physical_count_claim(physical_bytes)
    records = build_registry(marketing_rows, docs_rows, args.accessed_on)
    summary = build_summary(
        records,
        marketing_rows,
        docs_rows,
        headlines,
        physical_claim,
        args.accessed_on,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "oracle_official_region_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            )

    summary_path = output_dir / "oracle_official_region_summary.json"
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
                "physical_scope_reconciliation": summary[
                    "physical_scope_reconciliation"
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
