#!/usr/bin/env python3
"""Build a reproducible Apple data-center location registry.

Apple does not publish a live location directory. Its environmental reports use
three different boundaries that must stay separate: eight Apple-owned data-center
sites, aggregated U.S. and international colocation electricity, and undisclosed
third-party computing. The 2026 PCC expansion adds another boundary: selected
Private Cloud Compute workloads can run on Google Cloud NVIDIA infrastructure,
but Apple does not disclose the physical sites, GPU count, or contracted load.

This builder joins Apple's 2025 named owned-site roster to the fiscal-2025 energy
table in the 2026 report and validates the current expansion and PCC statements.
It does not turn a site label, an energy total, or a cloud architecture statement
into a physical-building, IT-MW, or accelerator-count claim.
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
from html.parser import HTMLParser
from pathlib import Path


REPORT_2025_URL = (
    "https://www.apple.com/environment/pdf/"
    "Apple_Environmental_Progress_Report_2025.pdf"
)
REPORT_2026_URL = (
    "https://www.apple.com/environment/pdf/"
    "Apple_Environmental_Progress_Report_2026.pdf"
)
US_EXPANSION_URL = (
    "https://www.apple.com/newsroom/2025/08/"
    "apple-increases-us-commitment-to-600-billion-usd-announces-ambitious-program/"
)
PCC_ORIGINAL_URL = "https://security.apple.com/blog/private-cloud-compute/"
PCC_EXPANSION_URL = "https://security.apple.com/blog/expanding-pcc/"


OWNED_SITE_ROSTER = [
    {
        "site_name": "Maiden",
        "country": "United States",
        "subnational_region": "North Carolina",
        "report_2026_energy_label": "Maiden, NC",
        "opening": "2010-06",
    },
    {
        "site_name": "Mesa",
        "country": "United States",
        "subnational_region": "Arizona",
        "report_2026_energy_label": "Mesa, AZ",
        "opening": "2017-03",
        "opening_boundary": "Apple says the global command data center came online in 2016 and reports 100 percent renewable since opening in March 2017.",
    },
    {
        "site_name": "Prineville",
        "country": "United States",
        "subnational_region": "Oregon",
        "report_2026_energy_label": "Prineville, OR",
        "opening": "2012-05",
    },
    {
        "site_name": "Reno",
        "country": "United States",
        "subnational_region": "Nevada",
        "report_2026_energy_label": "Reno, NV",
        "opening": "2012-12",
    },
    {
        "site_name": "Viborg",
        "country": "Denmark",
        "subnational_region": "Central Jutland",
        "report_2026_energy_label": "Viborg, Denmark",
        "opening": "2020",
    },
    {
        "site_name": "Waukee",
        "country": "United States",
        "subnational_region": "Iowa",
        "report_2026_energy_label": "Waukee, Iowa",
        "opening": "2024-10",
    },
    {
        "site_name": "Ulanqab",
        "country": "China",
        "subnational_region": "Inner Mongolia",
        "report_2026_energy_label": None,
        "opening": "2021",
    },
    {
        "site_name": "Gui'an",
        "country": "China",
        "subnational_region": "Guizhou",
        "report_2026_energy_label": None,
        "opening": "2021",
    },
]


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


def slugify(value: str) -> str:
    value = value.replace("'", "")
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def html_visible_text(data: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(data.decode("utf-8"))
    return parser.text()


def pdf_bytes_to_text(pdf_bytes: bytes, prefix: str) -> str:
    with tempfile.TemporaryDirectory(prefix=prefix) as directory:
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
                "pdftotext is required unless report text inputs are supplied"
            ) from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"pdftotext failed: {error.stderr}") from error
        return text_path.read_text(encoding="utf-8")


def require_pattern(text: str, pattern: str, label: str) -> re.Match:
    match = re.search(pattern, normalize_text(text), re.IGNORECASE)
    if not match:
        raise RuntimeError(f"Could not validate Apple evidence: {label}")
    return match


def parse_integer(value: str) -> int:
    return int(value.replace(",", ""))


def parse_energy_row(report_text: str, label: str) -> dict:
    match = re.search(
        rf"^[ \t]*{re.escape(label)}[ \t]+([^\n]+)$",
        report_text,
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError(f"Apple fiscal-2025 energy row not found: {label}")
    tokens = re.findall(r"\d[\d,]*|N/A|–|-", match.group(1))
    if len(tokens) < 6:
        raise RuntimeError(f"Unexpected Apple energy row for {label}: {tokens}")
    electricity_values = [parse_integer(value) for value in tokens if value[0].isdigit()]
    if len(electricity_values) < 3:
        raise RuntimeError(f"Missing electricity values for {label}: {tokens}")
    # Electricity and renewable electricity are the third- and second-last numeric
    # columns in every owned-site row; the final numeric column is avoided emissions.
    return {
        "electricity_use_million_kwh": electricity_values[-3],
        "renewable_electricity_million_kwh": electricity_values[-2],
        "location_based_scope_2_emissions_metric_tons_co2e": electricity_values[-1],
    }


def parse_reports(report_2025_text: str, report_2026_text: str) -> dict:
    report_2025_normalized = normalize_text(report_2025_text)
    # The layout-preserving PDF extraction interleaves the page's three text
    # columns, so validate the roster clause in stable fragments rather than
    # pretending it remains one contiguous sentence in extracted text.
    require_pattern(
        report_2025_normalized,
        r"certified seven of the eight data centers",
        "named-roster eight-site denominator",
    )
    roster_fragments = [
        "Prineville, Oregon",
        "Reno, Nevada",
        "Maiden, North Carolina",
        "Mesa, Arizona",
        "Viborg, Denmark",
        "Ulanqab",
        "Gui’an in China",
    ]
    for fragment in roster_fragments:
        require_pattern(
            report_2025_normalized,
            re.escape(fragment),
            f"named-roster fragment {fragment}",
        )
    count_match = require_pattern(
        report_2026_text,
        r"We now own (eight) data centers",
        "current owned-site count",
    )
    require_pattern(
        report_2026_text,
        r"As of 2025, we[’']ve certified all eight Apple-",
        "eight-site AWS certification count",
    )
    require_pattern(
        report_2026_text,
        r"owned data centers to the Alliance for",
        "AWS certification ownership scope",
    )
    require_pattern(
        report_2026_text,
        r"Water Stewardship \(AWS\) Standard",
        "AWS certification standard",
    )
    require_pattern(
        report_2026_text,
        r"Starting with fiscal year 2023, we no longer include the Newark, CA, data center as it was sold in fiscal year 2022",
        "Newark sold boundary",
    )
    require_pattern(
        report_2026_text,
        r"In October 2024, we opened our Waukee data center in Iowa, bringing our total Apple-owned data center count to eight",
        "Waukee opening boundary",
    )

    data_center_row_match = re.search(
        r"^[ \t]*Data center[ \t]+\d", report_2026_text, re.MULTILINE
    )
    retail_row_match = re.search(
        r"^[ \t]*Retail stores[ \t]+\d",
        report_2026_text[data_center_row_match.start() :] if data_center_row_match else "",
        re.MULTILINE,
    )
    if not data_center_row_match or not retail_row_match:
        raise RuntimeError("Could not isolate Apple's fiscal-2025 data-center table")
    data_center_table_start = data_center_row_match.start()
    data_center_table_end = data_center_table_start + retail_row_match.start()
    data_center_table = report_2026_text[
        data_center_table_start:data_center_table_end
    ]

    energy_rows = {}
    for row in OWNED_SITE_ROSTER:
        if row["report_2026_energy_label"]:
            energy_rows[row["site_name"]] = parse_energy_row(
                report_2026_text, row["report_2026_energy_label"]
            )
    energy_rows["China_two_site_aggregate"] = parse_energy_row(
        data_center_table, "China"
    )
    energy_rows["Data_center_total"] = parse_energy_row(
        report_2026_text, "Data center"
    )
    energy_rows["Colocation_US"] = parse_energy_row(
        report_2026_text, "Colocation facilities (U.S.)"
    )
    energy_rows["Colocation_international"] = parse_energy_row(
        report_2026_text, "Colocation facilities (international)"
    )

    colocation_exact_match = require_pattern(
        report_2026_text,
        r"FY 2025\s+(543,594,587)\s+543,594,587\s+190,356\s+0\s+100",
        "fiscal-2025 exact colocation electricity",
    )
    return {
        "owned_site_count": 8 if count_match.group(1).lower() == "eight" else None,
        "named_roster_evidence": {
            "owned_site_count": 8,
            "site_names": [row["site_name"] for row in OWNED_SITE_ROSTER],
            "validated_fragments": roster_fragments,
        },
        "energy_rows": energy_rows,
        "colocation_exact_electricity_kwh": parse_integer(
            colocation_exact_match.group(1)
        ),
    }


def parse_expansion_and_pcc(
    expansion_text: str,
    pcc_original_text: str,
    pcc_expansion_text: str,
) -> dict:
    expansion_sites = []
    for site, pattern in [
        ("Maiden", r"Construction is also underway in Maiden, North Carolina"),
        ("Waukee", r"construction underway in Iowa, Nevada, and Oregon"),
        ("Reno", r"construction underway in Iowa, Nevada, and Oregon"),
        ("Prineville", r"construction underway in Iowa, Nevada, and Oregon"),
    ]:
        require_pattern(expansion_text, pattern, f"{site} expansion")
        expansion_sites.append(site)

    require_pattern(
        pcc_original_text,
        r"custom Apple silicon and a hardened operating system designed for privacy",
        "original PCC Apple silicon architecture",
    )
    require_pattern(
        pcc_original_text,
        r"Large Language Model \(LLM\) inference workloads",
        "PCC inference workload",
    )
    require_pattern(
        pcc_expansion_text,
        r"expanding Private Cloud Compute \(PCC\) beyond Apple[’']s data centers",
        "PCC third-party expansion",
    )
    require_pattern(
        pcc_expansion_text,
        r"collaborating with Google and NVIDIA to run new Apple Intelligence workloads on Google Cloud",
        "Google and NVIDIA PCC relationship",
    )
    require_pattern(
        pcc_expansion_text,
        r"NVIDIA Confidential Computing with NVIDIA GPUs, Intel CPUs with TDX, and Google[’']s Titan chip",
        "third-party PCC hardware stack",
    )
    require_pattern(
        pcc_expansion_text,
        r"third-party data centers for the first time",
        "first third-party PCC data-center deployment",
    )
    return {
        "construction_underway_as_of_2025_08": sorted(expansion_sites),
        "pcc_original": {
            "operator_boundary": "Apple_data_centers",
            "compute": "custom_Apple_silicon_servers",
            "workload": "large_language_model_inference",
        },
        "pcc_expansion_as_of_2026_06_08": {
            "physical_operator": "Google_Cloud",
            "partners": ["Apple", "Google", "NVIDIA"],
            "compute": ["NVIDIA_GPUs", "Intel_CPUs_with_TDX", "Google_Titan_chip"],
            "significance": "first_PCC_use_of_third_party_data_centers",
            "physical_sites_GPU_models_counts_power_and_contract_value": "undisclosed",
        },
    }


def site_energy_evidence(site_name: str, parsed: dict) -> dict:
    if site_name in {"Ulanqab", "Gui'an"}:
        return {
            "reporting_scope": "China_two_owned_sites_aggregate",
            "energy_group_id": "apple_owned_china_two_site_group_fy2025",
            "group_members": ["Ulanqab", "Gui'an"],
            **parsed["energy_rows"]["China_two_site_aggregate"],
            "per_site_allocation": "undisclosed_do_not_divide_or_double_count",
        }
    return {
        "reporting_scope": "site_specific",
        **parsed["energy_rows"][site_name],
    }


def build_registry(parsed: dict, pcc: dict, accessed_on: str) -> list[dict]:
    expansion_sites = set(pcc["construction_underway_as_of_2025_08"])
    records = []
    for row in OWNED_SITE_ROSTER:
        records.append(
            {
                "id": f"apple_owned_data_center_{slugify(row['site_name'])}",
                "operator": "Apple",
                "ownership_scope": "Apple_owned_data_center",
                "site_name": row["site_name"],
                "country": row["country"],
                "subnational_region": row["subnational_region"],
                "lifecycle": {
                    "status": "operating",
                    "opening": row["opening"],
                    "opening_boundary": row.get("opening_boundary"),
                    "construction_expansion_underway_as_of_2025_08": row[
                        "site_name"
                    ]
                    in expansion_sites,
                },
                "fiscal_2025_energy": site_energy_evidence(
                    row["site_name"], parsed
                ),
                "water_stewardship": {
                    "Alliance_for_Water_Stewardship_certified_as_of_2025": True,
                    "portfolio_count_certified": 8,
                },
                "private_cloud_compute_site_allocation": "undisclosed",
                "granularity_boundary": (
                    "Apple's owned data-center label is a site or campus boundary, "
                    "not one physical building. Apple explicitly refers to multiple "
                    "buildings at Maiden and does not publish a fleet building count."
                ),
                "undisclosed_or_unreconciled": [
                    "exact street address, parcel, campus area, and physical building count",
                    "operating, energized, leased, utilized, and billed critical IT load",
                    "server, Apple-silicon, GPU, accelerator, node, chassis, rack, and utilization inventory",
                    "utility service, substation, transformer, switchgear, UPS, battery, generator, and equipment OEM bill of materials",
                    "site PUE, WUE, peak demand, cooling capacity, and current liquid-cooled IT load",
                    "site revenue, operating profit, capex, depreciation, and return on invested capital",
                ],
                "sources": {
                    "named_roster": REPORT_2025_URL,
                    "current_energy_and_owned_count": REPORT_2026_URL,
                    "US_expansion": US_EXPANSION_URL,
                    "PCC_original_architecture": PCC_ORIGINAL_URL,
                    "PCC_third_party_expansion": PCC_EXPANSION_URL,
                },
                "accessed_on": accessed_on,
            }
        )
    return records


def build_summary(
    records: list[dict],
    parsed: dict,
    pcc: dict,
    accessed_on: str,
) -> dict:
    site_specific_energy = sum(
        record["fiscal_2025_energy"]["electricity_use_million_kwh"]
        for record in records
        if record["fiscal_2025_energy"]["reporting_scope"] == "site_specific"
    )
    china_group_energy = parsed["energy_rows"]["China_two_site_aggregate"][
        "electricity_use_million_kwh"
    ]
    owned_energy = site_specific_energy + china_group_energy
    colocation_exact_kwh = parsed["colocation_exact_electricity_kwh"]
    total_exact_equivalent_million_kwh = owned_energy + colocation_exact_kwh / 1_000_000
    reported_total = parsed["energy_rows"]["Data_center_total"][
        "electricity_use_million_kwh"
    ]
    energy_evidence = {
        "site_specific": {
            record["site_name"]: record["fiscal_2025_energy"]
            for record in records
            if record["fiscal_2025_energy"]["reporting_scope"] == "site_specific"
        },
        "China_two_site_aggregate": parsed["energy_rows"][
            "China_two_site_aggregate"
        ],
        "colocation_exact_electricity_kwh": colocation_exact_kwh,
        "reported_data_center_total_million_kwh": reported_total,
    }
    return {
        "schema_version": 1,
        "generated_on": accessed_on,
        "sources": {
            "named_owned_site_roster": REPORT_2025_URL,
            "current_owned_count_fiscal_2025_energy_and_facility_design": REPORT_2026_URL,
            "US_expansion": US_EXPANSION_URL,
            "PCC_original_architecture": PCC_ORIGINAL_URL,
            "PCC_third_party_expansion": PCC_EXPANSION_URL,
            "retrieved_evidence_sha256": {
                "named_roster": canonical_hash(parsed["named_roster_evidence"]),
                "energy": canonical_hash(energy_evidence),
                "expansion_and_PCC": canonical_hash(pcc),
            },
            "hash_boundary": "Hashes cover extracted stable evidence rather than full HTML or PDF bytes, whose delivery metadata can vary.",
        },
        "coverage": {
            "Apple_owned_data_center_labels": len(records),
            "countries": sorted({record["country"] for record in records}),
            "country_count": len({record["country"] for record in records}),
            "site_specific_fiscal_2025_electricity_rows": 6,
            "China_owned_sites_in_one_aggregate_energy_row": 2,
            "colocation_physical_facility_count": None,
            "third_party_compute_physical_facility_count": None,
            "PCC_on_Google_Cloud_physical_site_count": None,
        },
        "ownership_and_location_boundary": {
            "owned_site_labels": [record["site_name"] for record in records],
            "sold_site_excluded": "Newark_CA_sold_in_fiscal_2022",
            "colocation": "Apple reports U.S. and international electricity aggregates but no facility names, operators, addresses, contracts, or counts.",
            "other_third_party_compute": "Apple reports use of on-demand cloud computing and storage but no vendor, location, capacity, or facility roster.",
            "PCC_2026_expansion": pcc["pcc_expansion_as_of_2026_06_08"],
        },
        "fiscal_2025_energy_reconciliation": {
            "six_site_specific_rows_sum_million_kwh": site_specific_energy,
            "China_two_owned_sites_aggregate_million_kwh": china_group_energy,
            "owned_sites_deduplicated_sum_million_kwh": owned_energy,
            "colocation_exact_electricity_kwh": colocation_exact_kwh,
            "colocation_exact_equivalent_million_kwh": round(
                colocation_exact_kwh / 1_000_000, 6
            ),
            "owned_plus_colocation_exact_equivalent_million_kwh": round(
                total_exact_equivalent_million_kwh, 6
            ),
            "reported_data_center_and_colocation_total_million_kwh": reported_total,
            "rounding_difference_million_kwh": round(
                reported_total - total_exact_equivalent_million_kwh, 6
            ),
            "owned_derived_average_facility_draw_mw": round(
                owned_energy * 1000 / 8760, 3
            ),
            "colocation_derived_average_Apple_metered_draw_mw": round(
                colocation_exact_kwh / 1000 / 8760, 3
            ),
            "combined_derived_average_draw_mw": round(
                total_exact_equivalent_million_kwh * 1000 / 8760, 3
            ),
            "boundary": (
                "Annual electricity divided by 8,760 hours is a derived average "
                "metered draw, not utility capacity, contracted IT MW, peak demand, "
                "or current 2026 load. Apple excludes colocation cooling and building "
                "operations from its operational boundary, so owned and colocation "
                "electricity are not identical facility scopes."
            ),
        },
        "expansion": {
            "construction_underway_as_of_2025_08": pcc[
                "construction_underway_as_of_2025_08"
            ],
            "added_buildings_MW_budget_and_completion_schedule": "undisclosed",
        },
        "accelerator_and_PCC_boundary": {
            "original_PCC": pcc["pcc_original"],
            "third_party_PCC": pcc["pcc_expansion_as_of_2026_06_08"],
            "interpretation": (
                "The Apple-owned fleet's exact Apple-silicon inventory remains "
                "undisclosed. The 2026 Google Cloud relationship establishes NVIDIA "
                "GPU use for new PCC workloads, but not GPU model, quantity, ownership, "
                "physical site, power, utilization, or contract economics."
            ),
        },
        "remaining_gaps": [
            "Complete Apple-owned campus, building, street-address, parcel, and meter-boundary crosswalk",
            "Complete colocation, third-party cloud, and Google Cloud PCC physical-site and operator roster",
            "Per-site operating, energized, leased, utilized, and billed critical IT load",
            "Apple-silicon and third-party GPU model, count, ownership, delivery, rack, fabric, site allocation, and utilization",
            "Per-site utility, substation, transformer, switchgear, UPS, battery, generator, cooling, and equipment OEM bill of materials",
            "Per-site current PUE, WUE, peak demand, cooling capacity, liquid-cooled MW, and hourly energy matching",
            "Data-center and PCC revenue, operating profit, capex, depreciation, contract, and return reconciliation",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="life/imports/global_data_centers_20260717",
        help="Directory for the official Apple registry and summary",
    )
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--report-2025-pdf")
    parser.add_argument("--report-2025-text")
    parser.add_argument("--report-2026-pdf")
    parser.add_argument("--report-2026-text")
    parser.add_argument("--US-expansion-html")
    parser.add_argument("--PCC-original-html")
    parser.add_argument("--PCC-expansion-html")
    args = parser.parse_args()

    if args.report_2025_text:
        report_2025_text = Path(args.report_2025_text).read_text(encoding="utf-8")
    else:
        report_2025_text = pdf_bytes_to_text(
            read_or_fetch(args.report_2025_pdf, REPORT_2025_URL),
            "apple-report-2025-",
        )
    if args.report_2026_text:
        report_2026_text = Path(args.report_2026_text).read_text(encoding="utf-8")
    else:
        report_2026_text = pdf_bytes_to_text(
            read_or_fetch(args.report_2026_pdf, REPORT_2026_URL),
            "apple-report-2026-",
        )

    parsed = parse_reports(report_2025_text, report_2026_text)
    expansion_text = html_visible_text(
        read_or_fetch(args.US_expansion_html, US_EXPANSION_URL)
    )
    pcc_original_text = html_visible_text(
        read_or_fetch(args.PCC_original_html, PCC_ORIGINAL_URL)
    )
    pcc_expansion_text = html_visible_text(
        read_or_fetch(args.PCC_expansion_html, PCC_EXPANSION_URL)
    )
    pcc = parse_expansion_and_pcc(
        expansion_text, pcc_original_text, pcc_expansion_text
    )
    records = build_registry(parsed, pcc, args.accessed_on)
    summary = build_summary(records, parsed, pcc, args.accessed_on)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = output_dir / "apple_official_location_registry.jsonl"
    with registry_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    summary_path = output_dir / "apple_official_location_summary.json"
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
                "energy_reconciliation": summary[
                    "fiscal_2025_energy_reconciliation"
                ],
                "PCC_boundary": summary["accelerator_and_PCC_boundary"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
