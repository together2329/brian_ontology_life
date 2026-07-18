#!/usr/bin/env python3
"""Build a crosswalk for major physical data-center operators.

The detailed evidence already lives in the landscape and financial ledgers.  This
builder validates and joins those records without flattening facility, campus,
market, design-capacity, operating-capacity and financial reporting scopes into a
false league table.  URLs and hashes are copied from the reviewed local evidence,
so the output is a reproducible index rather than a second hand-maintained ledger.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


def spec(
    company: str,
    financial_ref: str,
    portfolio_refs: list[str],
    geography: str,
    disclosure_class: str,
    scale_headline: str,
    scale_boundary: str,
    page_registry_refs: list[str] | None = None,
) -> dict:
    return {
        "company": company,
        "financial_profile_ref": financial_ref,
        "portfolio_profile_refs": portfolio_refs,
        "geography": geography,
        "financial_disclosure_class": disclosure_class,
        "scale_headline": scale_headline,
        "scale_boundary": scale_boundary,
        "page_registry_refs": page_registry_refs or [],
    }


SPECS = [
    spec("Aligned_Data_Centers", "company_aligned_data_centers", ["dc_aligned_north_america_public_directory", "dc_odata_aligned_latam_portfolio"], "Americas", "private_or_unlisted", "39 visible North/Latin America identifiers versus an 87 data-centers-under-management-and-future-development headline", "The 48-unit gap may include managed, private-customer or future assets; neither count is an operating-building total."),
    spec("Africa_Data_Centres", "company_africa_data_centres", ["dc_africa_data_centres_current_core_portfolio"], "Africa", "private_or_unlisted", "five current marketed facility cards in South Africa, Kenya and Nigeria", "The 92.15 MW card checksum mixes upon-completion, available and critical-IT measures and is not current live load."),
    spec("Khazna_Data_Centers", "company_khazna_data_centers", ["dc_khazna_global_portfolio"], "UAE_plus_international_pipeline", "private_or_unlisted", "30 live UAE facility markers and a separate 673 MW portfolio headline", "Visible marker design values sum to 298.51 MW, leaving a 374.49 MW scope difference that is not allocated to projects."),
    spec("Gulf_Data_Hub", "company_gulf_data_hub", ["dc_gulf_data_hub_gcc_portfolio"], "GCC_and_MENA", "private_or_unlisted", "six visible operating markers, four construction markers and 55 pipeline markers versus a seven-owned-facility transaction scope", "Ownership, website visibility and lifecycle are different scopes; pipeline pins are not permits or operating sites."),
    spec("Ascenty", "company_ascenty", ["dc_ascenty_latam_portfolio"], "Latin_America", "public_parent_with_segment_or_platform_boundary", "27 operating and 13 under-development facilities in the reviewed portfolio snapshot", "Parent and regional portfolio disclosures do not provide per-building active load, utilization or returns."),
    spec("Scala_Data_Centers", "company_scala_data_centers", ["dc_scala_latam_portfolio"], "Latin_America", "private_or_unlisted", "operating portfolio plus a large future power-and-land pipeline", "Campus and future-power announcements are not current energized, leased, utilized or billed IT load."),
    spec("DATA4", "company_data4", ["dc_data4_european_portfolio"], "Europe", "private_or_unlisted", "more than 1.5 GW marketed portfolio context with 1,252 MW of reviewed city headlines", "Pages use total power, available energy, electrical reserve and IT power language that cannot be ranked as one capacity metric."),
    spec("CoreSite", "company_american_tower", ["dc_coresite_american_tower_us_portfolio", "dc_coresite_ch2_chicago"], "United_States", "public_parent_with_segment_or_platform_boundary", "30 operating facilities in 11 markets in the latest SEC ledger", "SEC NRSF, market gross-area headlines and visible-card area have different denominators; CoreSite segment profit is company-defined."),
    spec("Iron_Mountain_Data_Centers", "company_iron_mountain", ["dc_iron_mountain_global_data_centers_portfolio"], "Global", "public_parent_with_segment_or_platform_boundary", "approximately 1.4 GW developable-capacity marketing context", "Developable and potential capacity plus a 400 MW pipeline are not operating capacity or current revenue."),
    spec("NTT_Global_Data_Centers", "company_ntt_data_group", ["dc_ntt_global_data_centers_portfolio", "dc_ntt_india_portfolio"], "Global", "public_parent_with_segment_or_platform_boundary", "more than 2,000 MW of current marketing critical-IT-load scope and a greater-than-3 GW FY2030 target", "The current headline, dated 1,630 MW management measure and target are different timing and lifecycle scopes."),
    spec("CyrusOne", "company_cyrusone", ["dc_cyrusone_global_portfolio"], "North_America_Europe_and_Japan", "private_or_unlisted", "66 published facility identifiers across 46 unique official location pages and more than 1 GW companywide critical-load claim", "Shared pages and mixed lifecycle prevent identifier count or marketed capacity from becoming an operating-building or utilized-load total.", ["life/imports/global_data_centers_20260717/cyrusone_official_location_pages.jsonl", "life/imports/global_data_centers_20260717/cyrusone_official_location_summary.json"]),
    spec("Equinix", "company_equinix", ["dc_equinix_global_ibx_xscale_portfolio"], "Global", "public_standalone_or_listed_operator", "global IBX retail portfolio plus xScale, with 52 major development projects at 2025 year-end", "Retail cabinets, xScale MW, land-supported capacity and development projects are distinct measures."),
    spec("Digital_Realty", "company_digital_realty", ["dc_digital_realty_global_portfolio"], "Global", "public_standalone_or_listed_operator", "approximately 2.9 GW in-place IT capacity, 769 MW under development and more than 5 GW future-development capacity", "In-place, under-construction and future land or space capacity cannot be added as current operating load."),
    spec("QTS", "company_qts", ["dc_qts_global_data_centers_portfolio"], "North_America_and_Europe", "private_or_unlisted", "49 canonical current official location candidates and more than 3 GW critical power under customer contract in the dated 2024 scope", "Contracted power, public-card capacity, commissioned facilities and concept-stage gross capacity are not interchangeable.", ["life/imports/global_data_centers_20260717/qts_official_location_pages.jsonl", "life/imports/global_data_centers_20260717/qts_official_location_summary.json"]),
    spec("Vantage_Data_Centers", "company_vantage_data_centers", ["dc_vantage_global_data_centers_portfolio"], "Global", "private_or_unlisted", "approximately 5.9 GW summed from current regional or campus design and full-buildout pages", "The sum mixes operating sites and development projects and is not operating, energized, leased or utilized load."),
    spec("AirTrunk", "company_airtrunk", ["dc_airtrunk_apac_portfolio"], "Asia_Pacific", "private_or_unlisted", "22 disclosed campuses with a derived design-capacity lower bound above 3.153 GW", "Campus design capacity is not current operating load; the separate dated 800 MW customer-commitment measure is not added."),
    spec("NEXTDC", "company_nextdc", ["dc_nextdc_apac_portfolio"], "Australia_and_Asia_Pacific", "public_standalone_or_listed_operator", "29 current provider facility labels across Australia, Japan, Malaysia and New Zealand", "Twenty-eight published card values sum to a 1.82055-GW mixed-lifecycle lower bound; this is not operating, energized, leased, utilized or billed load.", ["life/imports/global_data_centers_20260717/nextdc_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/nextdc_official_facility_summary.json"]),
    spec("Flexential", "company_flexential", ["dc_flexential_us_portfolio"], "United_States", "private_or_unlisted", "41 current provider cards and more than 360 MW online or under development", "The card checksum is 372.17 MW across mixed lifecycle, one card can cover multiple buildings, and the 28-asset KBRA pool uses a separate 199-MW financial boundary.", ["life/imports/global_data_centers_20260717/flexential_official_facility_registry.jsonl", "life/imports/global_data_centers_20260717/flexential_official_facility_summary.json"]),
    spec("DayOne_Data_Centers", "company_dayone", ["dc_firmus_dayone_batam_dsx"], "Asia_Pacific", "private_or_unlisted", "Batam 360 MW Firmus partnership plus the wider DayOne expansion platform", "The Batam capacity and up-to-170,000 accelerator ceiling are announced through 2027-2028, not live infrastructure."),
    spec("STACK_Infrastructure", "company_stack_infrastructure", ["dc_stack_global_data_center_portfolio"], "Global", "private_or_unlisted", "more than 8.5 GW built or under development plus more than 8.5 GW planned and potential in current marketing", "Regional headlines and market cards conflict; built, development, planned and potential scopes are never summed into operating load."),
    spec("GDS_Holdings", "company_gds_holdings", ["dc_gds_china_portfolio"], "Mainland_China", "public_standalone_or_listed_operator", "1,538 MW in service and 77.3% utilized area at Q1 2026, with 3.7 GW powered land and reservations", "Area utilization is not power utilization; powered land and reservations are future resources."),
    spec("VNET_Group", "company_vnet_group", ["dc_vnet_china_portfolio"], "Mainland_China", "public_standalone_or_listed_operator", "907 wholesale MW in service with 75.7% utilized MW plus a separate 50,170-cabinet retail fleet at Q1 2026", "Wholesale MW utilization and retail cabinet counts use different denominators and are not combined."),
    spec("Chindata_China", "company_chindata_china", ["dc_chindata_china_portfolio"], "Mainland_China", "private_or_unlisted", "dated Q2 2024 operating-plus-construction IT capacity of 1.64 GW and 1,355 MVA operating-substation nameplate", "The snapshot predates ownership changes; MVA, IT MW, construction and operating load are different measures."),
    spec("EdgeConneX", "company_edgeconnex", ["dc_edgeconnex_global_portfolio"], "Global", "private_or_unlisted", "40 kW to 500 MW-plus solution range with more than 80% of deployed MW described as build-to-suit", "Design range and build-to-suit share do not disclose current fleet MW, utilization or per-site capacity."),
    spec("STT_GDC_India", "company_stt_gdc_india", ["dc_stt_gdc_india_portfolio"], "India", "private_or_unlisted", "operating and under-development marketed portfolio with a separate 550 MW plan", "Dated operating, investment and planned-capacity snapshots are kept separate."),
    spec("CtrlS_Datacenters", "company_ctrls_datacenters", ["dc_ctrls_india_portfolio"], "India", "private_or_unlisted", "company headline of 19 live facilities and more than 370 MW versus ICRA's 17 operating facilities and 150 MW", "The 220-plus-MW difference may reflect marketed versus analytical or revenue-generating scope; it remains unresolved."),
    spec("Yotta_Data_Services", "company_nidar_yotta", ["dc_yotta_india_portfolio"], "India", "private_or_unlisted", "six reviewed operating or operated facility labels plus future campus programs", "Owned, government-operated, marketed-live and future facilities are distinct asset and lifecycle classes."),
    spec("Sify_Infinit_Spaces", "company_sify_technologies", ["dc_sify_india_portfolio"], "India", "public_standalone_or_listed_operator", "14 operating data centers and a 188.05 MW site-card sum reconciling to the rounded 188 MW headline", "Only 129 MW was cumulatively sold at FY2026 year-end; marketed live, installed, sold and revenue-generating MW differ."),
    spec("DataBank", "company_databank_holdings", ["dc_databank_north_america_uk_portfolio"], "United_States_and_United_Kingdom", "private_or_unlisted", "76 current marketing cards summing to 1.023179 GW of mixed-lifecycle critical IT load", "Eleven cards are explicitly development or future; the full checksum is not operating, energized, leased, utilized or billed load."),
]


COMMON_GAPS = [
    "exact current physical building roster with ownership, lease and lifecycle",
    "operating, energized, leased, utilized, billed and customer-accepted IT load by site",
    "site-level customer concentration, revenue, operating profit and return on invested capital",
    "GPU model, count, owner, delivery state, site allocation and utilization",
    "grid feeds, substations, transformers, switchgear, UPS, batteries and backup generation",
    "cooling equipment, live liquid-cooled MW, measured PUE, WUE and absolute water",
]


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def collect_urls(value: object) -> list[str]:
    found: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, str) and item.startswith(("https://", "http://")):
            found.append(item)
        elif isinstance(item, dict):
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return list(dict.fromkeys(found))


def load_index(path: Path, key: str) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = document[key]
    return {row["id"]: row for row in rows}


def build_records(finance_path: Path, landscape_path: Path, accessed_on: str) -> list[dict]:
    finance = load_index(finance_path, "financial_profiles")
    landscape = load_index(landscape_path, "campus_profiles")
    assert len(SPECS) == 29
    assert len({row["company"] for row in SPECS}) == len(SPECS)
    records = []
    for position, source in enumerate(SPECS, start=1):
        financial = finance[source["financial_profile_ref"]]
        portfolios = [landscape[ref] for ref in source["portfolio_profile_refs"]]
        for file_ref in source["page_registry_refs"]:
            assert Path(file_ref).exists(), file_ref
        urls = collect_urls(financial.get("sources", []))
        for portfolio in portfolios:
            urls.extend(collect_urls(portfolio.get("sources", [])))
        urls = list(dict.fromkeys(urls))
        records.append({
            "id": f"physical_operator_{source['company'].lower()}",
            "object_type": "PhysicalOperatorDisclosureCrosswalk",
            "source_order": position,
            **source,
            "official_evidence_urls": urls,
            "official_evidence_url_count": len(urls),
            "financial_profile_sha256": canonical_hash(financial),
            "portfolio_profile_sha256": canonical_hash(portfolios),
            "comparison_contract": {
                "location": "facility, building, campus, market, Region and service AZ remain separate granularities",
                "power": "utility, apparent-power, gross facility, critical IT, contracted, live and utilized values remain separate",
                "lifecycle": "operating, construction, announced, planned and potential values remain separate",
                "economics": "funding, valuation, capex plans, bookings and contract values are not revenue or operating profit",
            },
            "common_unresolved_gaps": COMMON_GAPS,
            "accessed_on": accessed_on,
        })
    return records


def build_summary(records: list[dict], accessed_on: str) -> dict:
    classes = Counter(row["financial_disclosure_class"] for row in records)
    return {
        "registry": "Major physical data-center operator disclosure crosswalk",
        "accessed_on": accessed_on,
        "operator_records": len(records),
        "financial_disclosure_class_counts": dict(sorted(classes.items())),
        "operators_with_machine_generated_page_registries": [row["company"] for row in records if row["page_registry_refs"]],
        "operators_with_reviewed_portfolio_profiles": len(records),
        "no_cross_operator_capacity_sum": True,
        "no_facility_or_building_count_ranking": True,
        "comparison_gate": [
            "Choose one physical granularity.",
            "Choose one lifecycle date and state.",
            "Choose one power denominator.",
            "Choose one financial reporting boundary.",
            "Only then compare growth, utilization, margin or returns.",
        ],
        "record_ids": [row["id"] for row in records],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--finance", type=Path, default=Path("life/finance/ai_data_center_supply_chain_financials_202607.yaml"))
    parser.add_argument("--landscape", type=Path, default=Path("life/knowledge/global_ai_data_center_landscape_202607.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.finance, args.landscape, args.accessed_on)
    summary = build_summary(records, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "physical_operator_disclosure_registry.jsonl"
    summary_path = args.output_dir / "physical_operator_disclosure_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
