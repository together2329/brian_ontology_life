#!/usr/bin/env python3
"""Build a reproducible AWS Region and Availability Zone registry.

The AWS Global Infrastructure marketing page covers all AWS partitions and
announced Regions, while the Regions and Availability Zones documentation table
is scoped to a standard AWS account.  This builder joins those official views,
preserves marketing-map IDs separately from programmatic Region codes, and
never treats a Region, AZ, or map point as a single physical building.
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


GLOBAL_PAGE_URL = "https://aws.amazon.com/about-aws/global-infrastructure/regions_az/"
REGIONS_MARKDOWN_URL = (
    "https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.md"
)
AZ_MARKDOWN_URL = (
    "https://docs.aws.amazon.com/global-infrastructure/latest/regions/"
    "aws-availability-zones.md"
)
GOVCLOUD_CODES_URL = (
    "https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/using-govcloud.md"
)
CHINA_CODES_URL = "https://docs.amazonaws.cn/en_us/aws/latest/userguide/ARNs.md"
EC2_REGION_CODES_URL = (
    "https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.md"
)

# These codes come from the three supplemental official documentation sources
# above.  The marketing map's `id` is retained separately and is not assumed to
# be a programmatic Region code.
SUPPLEMENTAL_PROGRAMMATIC_CODES = {
    "AWS GovCloud (US-East)": {
        "code": "us-gov-east-1",
        "partition": "aws-us-gov",
        "source": GOVCLOUD_CODES_URL,
    },
    "AWS GovCloud (US-West)": {
        "code": "us-gov-west-1",
        "partition": "aws-us-gov",
        "source": GOVCLOUD_CODES_URL,
    },
    "Mainland China (Beijing)": {
        "code": "cn-north-1",
        "partition": "aws-cn",
        "source": CHINA_CODES_URL,
    },
    "Mainland China (Ningxia)": {
        "code": "cn-northwest-1",
        "partition": "aws-cn",
        "source": CHINA_CODES_URL,
    },
    "AWS European Sovereign Cloud (Germany)": {
        "code": "eusc-de-east-1",
        "partition": "aws-eusc",
        "source": EC2_REGION_CODES_URL,
    },
}

# Three current public Regions have marketing-map IDs that are not their
# documented Region codes.  Matching by displayed name makes the discrepancy
# explicit while the standard-account documentation remains canonical for code.
PUBLIC_DOC_CODE_BY_MARKETING_NAME = {
    "Asia Pacific (Taipei)": "ap-east-2",
    "Asia Pacific (Thailand)": "ap-southeast-7",
    "Asia Pacific (New Zealand)": "ap-southeast-6",
}


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BrianOntologyDataCenterResearch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


class JsonScriptParser(HTMLParser):
    """Collect application/json script payloads from the AWS marketing page."""

    def __init__(self) -> None:
        super().__init__()
        self.in_json_script = False
        self.buffer: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "script" and dict(attrs).get("type") == "application/json":
            self.in_json_script = True
            self.buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.in_json_script:
            self.scripts.append("".join(self.buffer))
            self.in_json_script = False

    def handle_data(self, data: str) -> None:
        if self.in_json_script:
            self.buffer.append(data)


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def extract_global_page(html_bytes: bytes) -> tuple[dict, list[dict]]:
    parser = JsonScriptParser()
    parser.feed(html_bytes.decode("utf-8"))
    matches = []
    for script in parser.scripts:
        try:
            payload = json.loads(script)
        except json.JSONDecodeError:
            continue
        for item in walk_json(payload):
            if "continents" in item and "description" in item:
                try:
                    continents = json.loads(item["continents"])
                except (json.JSONDecodeError, TypeError):
                    continue
                matches.append((item, continents))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one AWS global-infrastructure payload, found {len(matches)}"
        )
    return matches[0]


def markdown_cells(line: str) -> list[str]:
    return [normalize_text(cell) for cell in line.strip().strip("|").split("|")]


def clean_code(value: str) -> str:
    value = value.replace("`", "")
    value = re.sub(r"\s*†.*$", "", value)
    return normalize_text(value)


def parse_region_table(markdown_bytes: bytes) -> list[dict]:
    rows = []
    in_table = False
    for line in markdown_bytes.decode("utf-8").splitlines():
        if line.startswith("| Code | Name | AZs | Geography | Opt-in status |"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|") or line.startswith("| ---"):
            continue
        cells = markdown_cells(line)
        if len(cells) != 5 or not re.fullmatch(r"[a-z]{2}(?:-[a-z0-9]+)+", cells[0]):
            continue
        az_match = re.search(r"\d+", cells[2])
        if not az_match:
            raise RuntimeError(f"Missing AZ count in Region table row: {line}")
        rows.append(
            {
                "programmatic_code": cells[0],
                "name": cells[1],
                "availability_zone_count": int(az_match.group()),
                "geography": cells[3],
                "opt_in_status": cells[4],
            }
        )
    if not rows:
        raise RuntimeError("No AWS Region rows parsed from official markdown")
    return rows


def parse_az_table(markdown_bytes: bytes) -> tuple[list[dict], list[dict]]:
    current_section = None
    in_scope = False
    current_rows = []
    announced_rows = []
    valid_sections = {
        "North America",
        "Africa",
        "Asia Pacific",
        "Europe",
        "Middle East",
        "South America",
    }
    for line in markdown_bytes.decode("utf-8").splitlines():
        if line.startswith("## "):
            current_section = normalize_text(line[3:])
            in_scope = current_section in valid_sections
            if current_section == "Constrained Availability Zones":
                break
            continue
        if not in_scope or not line.startswith("|") or line.startswith("| ---"):
            continue
        cells = markdown_cells(line)
        if len(cells) != 3 or cells[0] == "AZ ID":
            continue
        az_id = clean_code(cells[0])
        region_code = clean_code(cells[1])
        record = {
            "az_id": az_id if re.fullmatch(r"[a-z0-9]+-az\d+", az_id) else None,
            "status_label": None if re.fullmatch(r"[a-z0-9]+-az\d+", az_id) else az_id,
            "region_code": region_code,
            "geography": cells[2],
            "continent_section": current_section,
        }
        if record["az_id"]:
            current_rows.append(record)
        else:
            announced_rows.append(record)
    if not current_rows:
        raise RuntimeError("No AWS AZ rows parsed from official markdown")
    return current_rows, announced_rows


def canonical_name(value: str) -> str:
    return normalize_text(value).rstrip()


def resolve_public_doc_code(marketing_row: dict, docs_by_code: dict[str, dict]) -> str | None:
    name = canonical_name(marketing_row["name"])
    explicit = PUBLIC_DOC_CODE_BY_MARKETING_NAME.get(name)
    if explicit:
        return explicit
    raw_id = normalize_text(marketing_row.get("id"))
    return raw_id if raw_id in docs_by_code else None


def build_registry(
    continents: list[dict],
    region_docs: list[dict],
    az_rows: list[dict],
    accessed_on: str,
) -> list[dict]:
    docs_by_code = {row["programmatic_code"]: row for row in region_docs}
    azs_by_region: dict[str, list[dict]] = defaultdict(list)
    for row in az_rows:
        azs_by_region[row["region_code"]].append(row)

    records = []
    for continent in continents:
        for raw in continent.get("regions", []):
            name = canonical_name(raw["name"])
            public_code = resolve_public_doc_code(raw, docs_by_code)
            supplemental = SUPPLEMENTAL_PROGRAMMATIC_CODES.get(name)
            programmatic_code = public_code or (
                supplemental["code"] if supplemental else None
            )
            if public_code:
                code_source = REGIONS_MARKDOWN_URL
                partition = "aws"
            elif supplemental:
                code_source = supplemental["source"]
                partition = supplemental["partition"]
            else:
                code_source = None
                partition = "announced_not_yet_in_current_region_code_registry"

            docs_row = docs_by_code.get(public_code) if public_code else None
            az_id_rows = sorted(
                azs_by_region.get(public_code or "", []),
                key=lambda row: row["az_id"],
            )
            records.append(
                {
                    "schema_version": 1,
                    "object_type": "ProviderOfficialRegionRecord",
                    "provider": "Amazon_Web_Services",
                    "accessed_on": accessed_on,
                    "name": name,
                    "continent_group": normalize_text(continent.get("name")),
                    "lifecycle": "available" if raw.get("available") else "announced",
                    "launch_year_raw": raw.get("launched"),
                    "marketing_global_map": {
                        "id_raw": normalize_text(raw.get("id")),
                        "availability_zone_count": raw.get("availabilityZones"),
                        "map_point": {
                            "latitude": raw.get("lat"),
                            "longitude": raw.get("lng"),
                            "interpretation": "provider_region_visual_anchor_not_a_building_or_street_address",
                        },
                    },
                    "programmatic_region": {
                        "code": programmatic_code,
                        "partition": partition,
                        "source_url": code_source,
                        "marketing_map_id_matches_programmatic_code": (
                            normalize_text(raw.get("id")) == programmatic_code
                            if programmatic_code
                            else None
                        ),
                    },
                    "standard_account_region_documentation": docs_row,
                    "official_current_availability_zone_ids": az_id_rows,
                    "reconciliation": {
                        "documented_AZ_ID_count": len(az_id_rows),
                        "marketing_AZ_count": raw.get("availabilityZones"),
                        "counts_match_where_standard_docs_apply": (
                            len(az_id_rows) == raw.get("availabilityZones")
                            if docs_row
                            else None
                        ),
                    },
                    "disclosure_boundary": {
                        "region": "physical_geographic_area_containing_multiple_AZs_not_one_building",
                        "availability_zone": "one_or_more_discrete_data_centers_not_one_building",
                        "map_point": "provider_region_visualization_anchor_not_exact_building_coordinates",
                        "ownership": "owned_leased_controlled_colocation_and_partner_site_mapping_undisclosed",
                        "power": "operating_energized_leased_utilized_and_billed_IT_MW_undisclosed_by_region_and_AZ",
                        "accelerators": "GPU_Trainium_Inferentia_rack_and_utilization_inventory_undisclosed_by_region_and_AZ",
                        "equipment": "substation_transformer_switchgear_UPS_battery_generator_cooling_and_CDU_BOM_undisclosed_by_region_and_AZ",
                    },
                }
            )
    records.sort(key=lambda row: (row["lifecycle"], row["name"]))
    return records


def build_summary(
    records: list[dict],
    fields: dict,
    region_docs: list[dict],
    az_rows: list[dict],
    announced_az_rows: list[dict],
    accessed_on: str,
    source_hashes: dict[str, str],
) -> dict:
    available = [row for row in records if row["lifecycle"] == "available"]
    announced = [row for row in records if row["lifecycle"] == "announced"]
    partitions = Counter(
        row["programmatic_region"]["partition"] for row in available
    )
    map_id_mismatches = [
        {
            "region": row["name"],
            "marketing_map_id_raw": row["marketing_global_map"]["id_raw"],
            "programmatic_region_code": row["programmatic_region"]["code"],
            "handling": "both_values_preserved_marketing_map_id_not_used_as_programmatic_code",
        }
        for row in available
        if row["programmatic_region"]["marketing_map_id_matches_programmatic_code"]
        is False
    ]
    docs_missing = [
        row["name"]
        for row in available
        if row["standard_account_region_documentation"] is None
    ]
    announced_marketing_az = sum(
        row["marketing_global_map"]["availability_zone_count"] or 0
        for row in announced
    )
    current_az_count = sum(
        row["marketing_global_map"]["availability_zone_count"] or 0
        for row in available
    )
    headline_planned_az_match = re.search(
        r"announced plans for (\d+) more Availability Zones", fields["description"]
    )
    headline_planned_az = int(headline_planned_az_match.group(1))
    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "global_infrastructure_page": GLOBAL_PAGE_URL,
            "standard_account_region_table": REGIONS_MARKDOWN_URL,
            "standard_account_AZ_ID_table": AZ_MARKDOWN_URL,
            "GovCloud_region_codes": GOVCLOUD_CODES_URL,
            "China_region_codes": CHINA_CODES_URL,
            "European_Sovereign_region_code": EC2_REGION_CODES_URL,
            "source_evidence_sha256": source_hashes,
        },
        "official_headline": fields["description"],
        "coverage": {
            "global_marketing_region_records_total": len(records),
            "available_regions": len(available),
            "announced_regions": len(announced),
            "available_AZs_marketing_sum": current_az_count,
            "standard_account_region_rows": len(region_docs),
            "standard_account_current_AZ_ID_rows": len(az_rows),
            "standard_account_announced_AZ_rows": len(announced_az_rows),
            "available_regions_by_partition": dict(sorted(partitions.items())),
            "available_regions_absent_from_standard_account_table": docs_missing,
            "announced_region_labels": [row["name"] for row in announced],
        },
        "physical_lower_bound": {
            "operating_AZs": current_az_count,
            "physical_data_center_buildings_at_least": current_az_count,
            "derivation": "AWS defines each AZ as one or more discrete data centers.",
            "boundary": "This is a logical lower bound, not a disclosed building roster or ownership count.",
        },
        "planned_AZ_reconciliation": {
            "headline_more_AZs": headline_planned_az,
            "structured_announced_region_AZ_sum": announced_marketing_az,
            "separately_listed_announced_AZ_rows": len(announced_az_rows),
            "unallocated_residual_derived": headline_planned_az
            - announced_marketing_az
            - len(announced_az_rows),
            "boundary": "The current map assigns three planned AZs to Saudi Arabia and zero to Chile; the documentation separately lists one coming Maryland AZ. The remaining three are a headline residual consistent with the minimum-three-AZ Region model, not a site-level assignment.",
        },
        "marketing_map_id_anomalies": map_id_mismatches,
        "remaining_gaps": [
            "Complete physical campus and building addresses behind all 123 current AZs",
            "Owned versus leased, controlled, colocation, and partner-operated facility mapping",
            "Exact building count above the 123-building logical lower bound",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Per-site GPU, Trainium, Inferentia, rack, network-fabric, and utilization inventory",
            "Per-site utility feed, substation, transformer, switchgear, UPS, battery, generator, chiller, and CDU bill of materials",
            "Construction, commissioning, customer-acceptance, and revenue-start dates for each building",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official AWS registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    source_urls = {
        "global_infrastructure_page": GLOBAL_PAGE_URL,
        "standard_account_region_table": REGIONS_MARKDOWN_URL,
        "standard_account_AZ_ID_table": AZ_MARKDOWN_URL,
        "GovCloud_region_codes": GOVCLOUD_CODES_URL,
        "China_region_codes": CHINA_CODES_URL,
        "European_Sovereign_region_code": EC2_REGION_CODES_URL,
    }
    source_bytes = {key: fetch_bytes(url) for key, url in source_urls.items()}
    fields, continents = extract_global_page(
        source_bytes["global_infrastructure_page"]
    )
    region_docs = parse_region_table(source_bytes["standard_account_region_table"])
    az_rows, announced_az_rows = parse_az_table(
        source_bytes["standard_account_AZ_ID_table"]
    )
    records = build_registry(continents, region_docs, az_rows, args.accessed_on)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "aws_official_region_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = build_summary(
        records=records,
        fields=fields,
        region_docs=region_docs,
        az_rows=az_rows,
        announced_az_rows=announced_az_rows,
        accessed_on=args.accessed_on,
        source_hashes={
            **{
                key: hashlib.sha256(value).hexdigest()
                for key, value in source_bytes.items()
                if key != "global_infrastructure_page"
            },
            "global_infrastructure_page": hashlib.sha256(
                json.dumps(
                    {
                        "description": fields["description"],
                        "continents": continents,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        },
    )
    summary_path = output_dir / "aws_official_region_summary.json"
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
