#!/usr/bin/env python3
"""Build a reproducible Tencent Cloud Region and availability-zone registry.

The Tencent Cloud CVM guide publishes Region/AZ identifiers and marks zones with
different sales availability. Tencent's 2025 ESG report publishes portfolio-wide
owned/leased efficiency and electricity evidence, plus one leased Zhongwei data-
center statement. This builder keeps those scopes separate: an AZ record is not a
street-address building, an ownership record, a capacity disclosure, or a GPU
inventory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


REGIONS_URL = "https://intl.cloud.tencent.com/document/product/213/6091"
ESG_REPORT_URL = (
    "https://static.www.tencent.com/uploads/2026/04/09/"
    "34cdfa7393ee49cd5677b28f38c68d74.pdf"
)


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def read_or_fetch(path: str | None, url: str) -> bytes:
    return Path(path).read_bytes() if path else fetch_bytes(url)


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").replace("\ufeff", " ").replace("\xa0", " ").split())


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


class NextDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "script" and dict(attrs).get("id") == "__NEXT_DATA__":
            self.capture = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self.current_table: list[list[str]] | None = None
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self.current_table = []
            self.tables.append(self.current_table)
        elif tag == "tr" and self.current_table is not None:
            self.current_row = []
            self.current_table.append(self.current_row)
        elif tag in {"td", "th"} and self.current_row is not None:
            self.current_cell = []
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
            self.current_cell.append(data)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.buffer: list[str] = []

    def handle_data(self, data: str) -> None:
        self.buffer.append(data)


def parse_document(data: bytes) -> dict:
    parser = NextDataParser()
    parser.feed(data.decode("utf-8"))
    if not parser.buffer:
        raise RuntimeError("Tencent __NEXT_DATA__ payload not found")
    payload = json.loads("".join(parser.buffer))
    detail = payload["props"]["pageProps"]["detailContent"]
    return {
        "title": detail["title"],
        "recent_release_time": detail["recentReleaseTime"],
        "html": detail["html"],
        "source_url": detail["sourceUrl"],
    }


def split_region_context(raw_name: str) -> tuple[str, str | None]:
    for marker in ("Available only", "Coverage:"):
        if marker in raw_name:
            name, rest = raw_name.split(marker, 1)
            return normalize_text(name), normalize_text(marker + rest)
    return normalize_text(raw_name), None


def service_partition(region_id: str) -> str:
    if region_id.endswith("-fsi"):
        return "finance_cloud"
    if region_id.endswith("-adc"):
        return "self_driving_cloud"
    if region_id.startswith(("ap-beijing", "ap-shanghai", "ap-nanjing", "ap-guangzhou", "ap-chengdu", "ap-chongqing", "ap-zhongwei")):
        return "public_cloud_china_mainland"
    if region_id == "ap-hongkong":
        return "public_cloud_greater_china"
    return "public_cloud_international"


def parse_regions(document: dict) -> tuple[list[dict], str]:
    tables = TableParser()
    tables.feed(document["html"])
    visible = VisibleTextParser()
    visible.feed(document["html"])
    visible_text = normalize_text("".join(visible.buffer))
    required_phrases = [
        "Regions refer to the geographic areas where physical data centers of Tencent Cloud are located",
        "Availability zones (AZs) refer to physical data centers within the same region, but with separate power supplies and networks",
        "Availability Zones marked with an asterisk (*) have different sales availability compared to standard zones",
    ]
    for phrase in required_phrases:
        if phrase not in visible_text:
            raise RuntimeError(f"Tencent source definition changed or missing: {phrase}")

    records: list[dict] = []
    target_number = 0
    for table in tables.tables:
        rows = [
            [normalize_text("".join(cell)) for cell in row]
            for row in table
        ]
        if not rows or rows[0] != ["Region", "Region ID", "Number of AZs", "AZ", "AZ ID"]:
            continue
        target_number += 1
        table_scope = "china" if target_number == 1 else "outside_china"
        current: dict | None = None
        for row in rows[1:]:
            if not any(row):
                continue
            if len(row) != 5:
                raise RuntimeError(f"Unexpected Tencent Region table row: {row}")
            raw_region, region_id, count, raw_zone, zone_id = row
            if raw_region:
                region_name, context = split_region_context(raw_region)
                current = {
                    "table_scope": table_scope,
                    "service_partition": service_partition(region_id),
                    "region_name": region_name,
                    "region_context": context,
                    "region_id": region_id,
                    "published_zone_count": int(count),
                    "zones": [],
                }
                records.append(current)
            if not raw_zone and not zone_id:
                continue
            if current is None:
                raise RuntimeError(f"Tencent continuation row without Region: {row}")
            restricted = raw_zone.endswith("*")
            current["zones"].append(
                {
                    "zone_name": raw_zone.removesuffix("*"),
                    "zone_id": zone_id,
                    "different_sales_availability": restricted,
                    "sales_boundary": (
                        "Contact Tencent Cloud sales or online support to purchase resources."
                        if restricted
                        else None
                    ),
                }
            )

    if target_number != 2:
        raise RuntimeError(f"Expected two Tencent Region tables, got {target_number}")
    for record in records:
        if len(record["zones"]) != record["published_zone_count"]:
            raise RuntimeError(
                f"Tencent zone-row mismatch for {record['region_id']}: "
                f"{len(record['zones'])} != {record['published_zone_count']}"
            )
    return records, visible_text


def pdf_bytes_to_text(pdf_bytes: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="tencent_esg_") as directory:
        pdf_path = Path(directory) / "report.pdf"
        text_path = Path(directory) / "report.txt"
        pdf_path.write_bytes(pdf_bytes)
        try:
            subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(text_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as error:
            raise RuntimeError("pdftotext is required unless --esg-text is supplied") from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"pdftotext failed: {error.stderr}") from error
        return text_path.read_text(encoding="utf-8")


def require_match(text: str, pattern: str, label: str) -> re.Match:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise RuntimeError(f"Tencent ESG evidence not found: {label}")
    return match


def parse_esg(text: str) -> dict:
    normalized = normalize_text(text)
    pue = require_match(
        normalized,
        r"performance of owned data centres from ([0-9]+(?:\.[0-9]+)?) to ([0-9]+(?:\.[0-9]+)?)",
        "owned data-center PUE",
    )
    savings = require_match(
        normalized,
        r"saving\s+approximately\s+([0-9,]+(?:\.[0-9]+)?) MWh of electricity and reducing\s+emissions by ([0-9,]+(?:\.[0-9]+)?) tCO2e",
        "electricity and emissions savings",
    )
    renewable_capacity = require_match(
        normalized,
        r"installed capacity of renewable energy facilities.*?owned data centres has reached ([0-9.]+) MW",
        "owned data-center renewable capacity",
    )
    green_shares = require_match(
        normalized,
        r"from ([0-9.]+)% to ([0-9.]+)% in owned data centres and from.*?([0-9.]+)% to ([0-9.]+)% in leased data centres",
        "owned and leased green-electricity shares",
    )
    require_match(
        normalized,
        r"data centre we leased in Zhongwei.*?City was selected",
        "leased Zhongwei data center",
    )
    require_match(normalized, r"By 2026, use 100% green electricity for owned data centres", "2026 target")
    require_match(normalized, r"By 2030, achieve 100% green electricity consumption", "2030 target")
    require_match(
        normalized,
        r"By 2030, improve water usage effectiveness of owned data centres by 20% from 2025 base year",
        "2030 WUE target",
    )
    return {
        "reporting_year": 2025,
        "owned_data_center_average_PUE": float(pue.group(2)),
        "owned_data_center_prior_year_average_PUE": float(pue.group(1)),
        "PUE_scope": "All owned data centers operating for more than 12 months, per report footnote.",
        "electricity_savings_MWh": float(savings.group(1).replace(",", "")),
        "emissions_reduction_tCO2e": float(savings.group(2).replace(",", "")),
        "owned_data_center_onsite_renewable_capacity_MW": float(renewable_capacity.group(1)),
        "owned_data_center_green_electricity_share_percent": float(green_shares.group(2)),
        "owned_data_center_prior_year_green_electricity_share_percent": float(green_shares.group(1)),
        "leased_data_center_green_electricity_share_percent": float(green_shares.group(4)),
        "leased_data_center_prior_year_green_electricity_share_percent": float(green_shares.group(3)),
        "leased_Zhongwei_data_center": True,
        "targets": {
            "owned_data_center_green_electricity_percent_by_2026": 100,
            "total_green_electricity_consumption_percent_by_2030": 100,
            "owned_data_center_WUE_improvement_percent_by_2030_from_2025": 20,
            "owned_data_center_average_PUE_not_to_exceed": 1.25,
        },
        "allocation_boundary": (
            "Portfolio metrics are not assigned to a Region or AZ. The report names a leased data center in Zhongwei City, "
            "but does not map it to the CVM Region/AZ IDs or disclose its capacity."
        ),
    }


def build_records(source_records: list[dict], accessed_on: str) -> list[dict]:
    records = []
    for position, source in enumerate(source_records, start=1):
        geographic_cross_reference = None
        if source["region_id"] == "ap-zhongwei":
            geographic_cross_reference = {
                "evidence": "Tencent's 2025 ESG report names a data center leased in Zhongwei City.",
                "boundary": "Geographic cross-reference only; the report does not map the leased asset to this Region or its AZ ID.",
            }
        records.append(
            {
                "id": f"tencent_cloud_region_{source['region_id'].replace('-', '_')}",
                "provider": "Tencent Cloud",
                "source_order": position,
                **source,
                "lifecycle": "current_CVM_documentation_listed",
                "geographic_cross_reference": geographic_cross_reference,
                "granularity_boundary": (
                    "Tencent calls an AZ a physical data center with separate power and network. The table still does not prove "
                    "one street-address building, campus boundary, owned asset, energized load, or revenue-producing facility per AZ."
                ),
                "undisclosed_or_unreconciled": [
                    "exact campus, building, street address, parcel, ownership, lease, and colocation mapping",
                    "operating, construction, commissioning, customer-acceptance, and revenue-start status below service listing",
                    "utility, IT, energized, leased, utilized, and billed power capacity",
                    "GPU and accelerator models, counts, racks, fabrics, ownership, and utilization",
                    "grid feeds, substations, transformers, switchgear, UPS, batteries, generators, cooling, and equipment OEMs",
                    "per-site PUE, WUE, water, renewable matching, capex, revenue, and operating margin",
                ],
                "sources": {
                    "CVM_regions_and_AZs": REGIONS_URL,
                    "portfolio_ESG_context": ESG_REPORT_URL,
                },
                "accessed_on": accessed_on,
            }
        )
    return records


def build_summary(
    records: list[dict],
    source_records: list[dict],
    document: dict,
    esg: dict,
    accessed_on: str,
) -> dict:
    partition_regions = Counter(row["service_partition"] for row in records)
    partition_zones = Counter()
    restricted = 0
    for row in records:
        partition_zones[row["service_partition"]] += row["published_zone_count"]
        restricted += sum(zone["different_sales_availability"] for zone in row["zones"])
    china_rows = [row for row in records if row["table_scope"] == "china"]
    international_rows = [row for row in records if row["table_scope"] == "outside_china"]
    summary = {
        "registry": "Tencent Cloud official Region and availability-zone registry",
        "accessed_on": accessed_on,
        "technical_document_recent_release_time": document["recent_release_time"],
        "record_count": len(records),
        "published_AZ_record_count": sum(row["published_zone_count"] for row in records),
        "table_scopes": {
            "china": {
                "region_rows": len(china_rows),
                "AZ_rows": sum(row["published_zone_count"] for row in china_rows),
            },
            "outside_china": {
                "region_rows": len(international_rows),
                "AZ_rows": sum(row["published_zone_count"] for row in international_rows),
            },
        },
        "partition_region_counts": dict(sorted(partition_regions.items())),
        "partition_AZ_counts": dict(sorted(partition_zones.items())),
        "AZs_with_different_sales_availability": restricted,
        "portfolio_ESG_2025": esg,
        "anomalies_and_boundaries": {
            "Sao_Paulo_blank_continuation_row": "Ignored after validating its published one-AZ count.",
            "Hong_Kong_region_label": "Provider label references Hong Kong, Macao, and Taiwan while all three published AZ names/IDs are Hong Kong labels; preserved without inferring separate Macao or Taiwan facilities.",
            "finance_regions": "Three finance Regions are application-only service partitions, not proof of three separately owned campuses.",
            "asterisk": "Different sales availability, not closure or non-operation.",
            "AZ_physical_definition": "Provider calls an AZ a physical data center, but exact building, address, ownership, capacity, and lifecycle below the service listing remain undisclosed.",
        },
        "source_snapshots": {
            "CVM_regions_and_AZs": {
                "url": REGIONS_URL,
                "parsed_evidence_sha256": canonical_hash(source_records),
                "hash_scope": "Parsed Region, Region ID, AZ count, AZ name, AZ ID, and sales-availability marker rows.",
            },
            "ESG_report_2025": {
                "url": ESG_REPORT_URL,
                "parsed_evidence_sha256": canonical_hash(esg),
                "hash_scope": "Parsed portfolio PUE, green-electricity, savings, renewable-capacity, Zhongwei lease, and target evidence.",
            },
        },
    }
    summary["canonical_record_sha256"] = canonical_hash(records)
    return summary


def validate_expected_counts(summary: dict) -> None:
    assert summary["record_count"] == 22
    assert summary["published_AZ_record_count"] == 62
    assert summary["table_scopes"] == {
        "china": {"region_rows": 12, "AZ_rows": 40},
        "outside_china": {"region_rows": 10, "AZ_rows": 22},
    }
    assert summary["partition_region_counts"] == {
        "finance_cloud": 3,
        "public_cloud_china_mainland": 7,
        "public_cloud_greater_china": 1,
        "public_cloud_international": 10,
        "self_driving_cloud": 1,
    }
    assert summary["partition_AZ_counts"] == {
        "finance_cloud": 9,
        "public_cloud_china_mainland": 24,
        "public_cloud_greater_china": 3,
        "public_cloud_international": 22,
        "self_driving_cloud": 4,
    }


def write_outputs(output_dir: Path, records: list[dict], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "tencent_official_region_registry.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )
    (output_dir / "tencent_official_region_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regions-html")
    esg_group = parser.add_mutually_exclusive_group()
    esg_group.add_argument("--esg-pdf")
    esg_group.add_argument("--esg-text")
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--output-dir", default="life/imports/global_data_centers_20260717")
    args = parser.parse_args()

    document = parse_document(read_or_fetch(args.regions_html, REGIONS_URL))
    source_records, _visible_text = parse_regions(document)
    if args.esg_text:
        esg_text = Path(args.esg_text).read_text(encoding="utf-8")
    else:
        esg_text = pdf_bytes_to_text(read_or_fetch(args.esg_pdf, ESG_REPORT_URL))
    esg = parse_esg(esg_text)
    records = build_records(source_records, args.accessed_on)
    summary = build_summary(records, source_records, document, esg, args.accessed_on)
    validate_expected_counts(summary)
    write_outputs(Path(args.output_dir), records, summary)
    print(
        json.dumps(
            {
                "records": len(records),
                "AZs": summary["published_AZ_record_count"],
                "restricted_sales_AZs": summary["AZs_with_different_sales_availability"],
                "canonical_record_sha256": summary["canonical_record_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
