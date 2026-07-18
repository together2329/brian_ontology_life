#!/usr/bin/env python3
"""Build Global Switch's current facility-label, expansion and OSM registry.

Global Switch publishes several valid but non-equivalent portfolio views.  The
current directory exposes 16 named labels with an undefined ``MW`` field plus
two coming-soon markets.  The 2025 annual report instead reports eight data
centres/campuses, 12 completed legal investment-property labels, four
development properties, 488 MVA of utility supply and 252 MW of saleable
capacity.  This builder preserves those denominators rather than converting
them into a single fleet-capacity number.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY_URL = "https://www.globalswitch.com/data-centres/"
ANNUAL_2025_URL = "https://gswitch-cdn.com/wp-content/uploads/2026/03/16131953/Global-Switch-Holdings-Limited-31-December-2025_-FINAL-Euronext.pdf"
ESG_2025_URL = "https://gswitch-cdn.com/wp-content/uploads/2026/04/24102809/2025-ESG-Report.pdf"
LIQUID_URL = "https://www.globalswitch.com/our-offer/liquid-cooling/"
LONDON_URL = "https://www.globalswitch.com/locations/london-data-centres/"
LONDON_SOUTH_URL = "https://www.globalswitch.com/about-us/news/21-02-24-global-switch-receives-full-planning-approval-for-its-third-london-data-centre/"
FRANKFURT_URL = "https://www.globalswitch.com/locations/frankfurt-data-centres/"
MADRID_URL = "https://www.globalswitch.com/locations/madrid-data-centre/"
SINGAPORE_URL = "https://www.globalswitch.com/locations/singapore-data-centres/"
HONG_KONG_URL = "https://www.globalswitch.com/locations/hong-kong-data-centre/"
AMSTERDAM_EAST_SPEC_URL = "https://www.globalswitch.com/media/zq0jnz4w/global-switch-technical-specification-amsterdam-east.pdf"
PARIS_EAST_SPEC_URL = "https://www.globalswitch.com/media/25bjuswe/global-switch-technical-specification-paris-east.pdf"
PARIS_WEST_SPEC_URL = "https://www.globalswitch.com/media/sbtjgkzc/global-switch-technical-specification-paris-west.pdf"
JOHOR_URL = "https://www.globalswitch.com/data-centres/johor/"


def label(
    code: str,
    market: str,
    name: str,
    country_code: str,
    directory_mw: float,
    address: str,
    lifecycle: str,
    annual_property_status: str,
    details: dict | None = None,
    source_urls: list[str] | None = None,
) -> dict:
    row = {
        "record_code": code,
        "market": market,
        "provider_label": name,
        "country_code": country_code,
        "address": address,
        "record_class": "current_provider_directory_facility_label",
        "lifecycle_as_of_2026_07_19": lifecycle,
        "directory_card_mw": directory_mw,
        "directory_card_mw_definition": "not_defined_as_grid_utility_IT_saleable_installed_operating_leased_or_utilized_on_current_directory",
        "annual_report_investment_property_status": annual_property_status,
        "source_urls": [DIRECTORY_URL, ANNUAL_2025_URL],
    }
    if details:
        row["selected_facility_engineering"] = details
    if source_urls:
        row["source_urls"].extend(source_urls)
    return row


RECORDS = [
    label(
        "AMS_WEST", "Amsterdam", "Amsterdam West", "NL", 42,
        "Johan Huizingalaan 759, 1066 VH Amsterdam, Netherlands",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_50_year_leasehold_expiring_2045",
    ),
    label(
        "AMS_EAST", "Amsterdam", "Amsterdam East", "NL", 32,
        "Johan Huizingalaan 759, 1066 VH Amsterdam, Netherlands",
        "current_directory_label_phase_1_completed_in_2025_and_completed_legal_investment_property",
        "completed_50_year_leasehold_expiring_2045",
        {
            "gross_space_sqm_all_stages": 32000,
            "utility_supply": "50kV; 40MVA planned/all-stages technical specification",
            "UPS": "static UPS N+1",
            "backup_generation": "standby generators N+1; 24-hour on-site fuel at full load",
            "cooling": "35MW provision; N+2; chiller-assist free cooling; fan-wall units",
            "standard_power_density_w_per_sqm": 2000,
            "2025_phase_1_contracted_capacity_added_mw": 8,
            "boundary": "All-stages technical specification is not current live load; the current directory's 32MW field and 40MVA planned utility figure use different undefined/apparent-power denominators.",
        },
        [AMSTERDAM_EAST_SPEC_URL],
    ),
    label(
        "FRA_NORTH", "Frankfurt", "Frankfurt North", "DE", 12,
        "Eschborner Landstrasse 110, 60489 Frankfurt am Main, Germany",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 11862,
            "utility_supply": "10kV N+N; 14MVA current",
            "UPS": "static UPS N+1",
            "backup_generation": "standby generators N+1; 24-hour on-site fuel at full load",
            "cooling": "19MW installed; N+2; chiller-assist free cooling; chilled-water system",
            "standard_power_density_w_per_sqm": 2000,
            "performance_validated_PUE_at_full_load": 1.1,
        },
        [FRANKFURT_URL],
    ),
    label(
        "FRA_SOUTH", "Frankfurt", "Frankfurt South", "DE", 10,
        "Eschborner Landstrasse 110, 60489 Frankfurt am Main, Germany",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 17686,
            "utility_supply": "10kV N+N; 14MVA current",
            "UPS": "diesel rotary UPS N+2",
            "backup_generation": "2 x 1.6MW standby generators N+N; 24-hour on-site fuel at full load",
            "cooling": "11.8MW installed; N+1; chilled-water system with free cooling",
            "standard_power_density_w_per_sqm": 1000,
        },
        [FRANKFURT_URL],
    ),
    label(
        "LON_EAST", "London", "London East", "GB", 87,
        "Global Switch House, 3 Nutmeg Lane, London E14 2AX, United Kingdom",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 65542,
            "utility_supply": "132kV N+N; 60MVA current",
            "UPS": "diesel rotary UPS N+2 for IT and mechanical systems",
            "backup_fuel": "48 hours at full load with continuous delivery",
            "cooling": "41.57MW installed; N+2; CRAH and chilled-water; in-rack cooling capability",
            "standard_power_density_w_per_sqm": 2000,
        },
        [LONDON_URL],
    ),
    label(
        "LON_NORTH", "London", "London North", "GB", 18,
        "East India Dock House, 240 East India Dock Road, London E14 9YY, United Kingdom",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 23439,
            "utility_supply": "11kV N+1; 26MVA current and planned",
            "UPS": "static N+1 in Area 1; diesel rotary UPS N+1 in Areas 2 and 3",
            "backup_generation": "Area 1 standby generators N+1; 48-hour on-site fuel at full load",
            "cooling": "16.1MW; N+1; CRAH and chilled-water; in-rack cooling capability",
            "standard_power_density_w_per_sqm": 2000,
            "Area_3_annualized_PUE_below": 1.3,
        },
        [LONDON_URL],
    ),
    label(
        "LON_SOUTH", "London", "London South", "GB", 35,
        "Nutmeg Lane, London E14 2AX, United Kingdom",
        "under_development_after_planning_approval",
        "development_freehold",
        {
            "gross_space_sqm_up_to": 27000,
            "utility_supply_capacity_MVA": 40,
            "2024_announcement_IT_power_capacity_mw": 40,
            "current_directory_card_mw": 35,
            "standard_power_density_w_per_sqm": 3000,
            "higher_density_w_per_sqm_more_than": 5000,
            "cooling": "planned air and liquid cooling optionality",
            "boundary": "The current 35MW directory card, 40MVA utility statement and 40MW IT announcement conflict or use different denominators; no value is treated as operating load.",
        },
        [LONDON_URL, LONDON_SOUTH_URL],
    ),
    label(
        "MAD_1", "Madrid", "Madrid 1", "ES", 14,
        "Calle Yecora 4, 28022 Madrid, Spain",
        "current_directory_label_corresponding_to_completed_Madrid_property_at_shared_address",
        "completed_freehold_property_reported_as_Madrid_without_number",
        {
            "gross_space_sqm": 21922,
            "utility_supply": "15kV N+N; 2 x 18MVA current",
            "UPS": "2N static UPS",
            "backup_generation": "standby generators N+1; 24-hour on-site fuel at full load",
            "cooling": "24MW installed; N+1; CRAC; condenser-water system; three water tanks totalling 600 cubic metres",
            "standard_power_density_w_per_sqm": 1000,
        },
        [MADRID_URL],
    ),
    label(
        "MAD_2", "Madrid", "Madrid 2", "ES", 56,
        "Calle Yecora 4, 28022 Madrid, Spain",
        "current_directory_label_but_annual_report_classifies_Madrid_2_as_development",
        "development_freehold",
    ),
    label(
        "PAR_EAST", "Paris", "Paris East", "FR", 22,
        "7-9 rue Petit, 92582 Clichy Cedex, France",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 34915,
            "utility_supply": "15kV N+1; 34MVA current and planned",
            "UPS": "2N static UPS",
            "backup_generation": "standby generators N+1; 48-hour on-site fuel at full load",
            "cooling": "22.8MW installed; N+1; CRAC and condenser-water system",
            "standard_power_density_w_per_sqm": 800,
        },
        [PARIS_EAST_SPEC_URL],
    ),
    label(
        "PAR_WEST", "Paris", "Paris West", "FR", 17,
        "7-9 rue Petit, 92582 Clichy Cedex, France",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_freehold",
        {
            "gross_space_sqm": 16703,
            "utility_supply": "20kV N+1; 25MVA current",
            "UPS": "diesel rotary UPS N+2 for IT and mechanical systems",
            "backup_fuel": "48 hours at full load with continuous delivery",
            "cooling": "18MW installed and planned; N+1; CRAH; chilled-water with free cooling",
            "standard_power_density_w_per_sqm": 1500,
        },
        [PARIS_WEST_SPEC_URL],
    ),
    label(
        "PAR_NORTH", "Paris", "Paris North", "FR", 24,
        "7-9 rue Petit, 92582 Clichy Cedex, France",
        "current_directory_label_at_shared_campus_address",
        "not_separately_enumerated_in_2025_legal_property_schedule",
    ),
    label(
        "PAR_SOUTH", "Paris", "Paris South", "FR", 18,
        "7-9 rue Petit, 92582 Clichy Cedex, France",
        "current_directory_label_at_shared_campus_address",
        "not_separately_enumerated_in_2025_legal_property_schedule",
    ),
    label(
        "HKG", "Hong Kong", "Hong Kong", "HK", 71,
        "18 Chun Yat Street, Tseung Kwan O Industrial Estate, New Territories, Hong Kong",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_35_year_leasehold_expiring_2047",
        {
            "gross_floor_area_sqm": 70545,
            "buildings": 5,
            "utility_supply": "132kV N+1; 100MVA current",
            "UPS": "diesel rotary UPS N+2 for Buildings 1-3; static UPS N+1 for Buildings 4-5",
            "backup_generation": "Buildings 4-5 standby generators N+1; 24-hour on-site fuel at full load",
            "cooling": "82MW installed and planned; N+1; CRAH and chilled-water",
            "annualized_design_PUE_below": 1.3,
            "liquid_cooled_capacity_available_mw_2024_announcement": 30,
            "liquid_partners": ["LiquidStack", "X-Fusion", "Supermicro"],
            "boundary": "The 30MW statement is available liquid-cooled capacity, not confirmed utilized customer load or GPU inventory.",
        },
        [HONG_KONG_URL, LIQUID_URL],
    ),
    label(
        "SG_TAI_SENG", "Singapore", "Singapore Tai Seng", "SG", 17,
        "2 Tai Seng Avenue, Singapore 534408",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_30_year_leasehold_expiring_2053",
        {
            "gross_space_sqm": 26743,
            "utility_supply": "22kV N+N; 30MVA current and planned",
            "UPS": "2N static UPS in Main Building; diesel rotary UPS N+1 distributed in Extension Wing",
            "backup_generation": "Main Building mechanical standby generators N+1; 24-hour on-site fuel at full load",
            "cooling": "30MW installed; N+1; CRAC; condenser-water and chilled-water systems",
            "standard_power_density_w_per_sqm": 1000,
        },
        [SINGAPORE_URL],
    ),
    label(
        "SG_WOODLANDS", "Singapore", "Singapore Woodlands", "SG", 22,
        "7 Woodlands Height, Singapore 737858",
        "current_directory_label_and_completed_legal_investment_property",
        "completed_30_year_leasehold_expiring_2039",
        {
            "gross_floor_area_sqm_2025_ESG": 23946,
            "utility_supply": "22kV N+N; 30MVA current",
            "UPS": "diesel rotary UPS N+2 for IT and N+1 for mechanical systems",
            "backup_fuel": "24 hours at full load with continuous delivery",
            "cooling": "28.8MW installed; N+1",
            "standard_power_density_w_per_sqm": 1500,
        },
        [SINGAPORE_URL, ESG_2025_URL],
    ),
    {
        "record_code": "JOHOR",
        "market": "Kulai / Johor",
        "provider_label": "Johor - Coming Soon",
        "country_code": "MY",
        "address": "Kulai, Johor, Malaysia; exact street address undisclosed",
        "record_class": "provider_announced_coming_soon_market",
        "lifecycle_as_of_2026_07_19": "development_capacity_targeted_available_in_2028",
        "annual_report_investment_property_status": "development_freehold",
        "directory_card_mw": "undisclosed",
        "power_cooling_GPU_and_exact_site": "undisclosed",
        "source_urls": [DIRECTORY_URL, JOHOR_URL, ANNUAL_2025_URL],
    },
    {
        "record_code": "BANGKOK",
        "market": "Bangkok / Thailand",
        "provider_label": "Bangkok - Coming Soon",
        "country_code": "TH",
        "address": "undisclosed",
        "record_class": "provider_announced_coming_soon_market",
        "lifecycle_as_of_2026_07_19": "coming_soon_marketing_label_without_disclosed_capacity_or_availability_date",
        "annual_report_investment_property_status": "not_listed_in_2025_investment_property_schedule",
        "directory_card_mw": "undisclosed",
        "power_cooling_GPU_and_exact_site": "undisclosed",
        "source_urls": [DIRECTORY_URL, ANNUAL_2025_URL],
    },
]


OSM_DISPOSITIONS = {
    "osm_way_759989363": {"market": "Frankfurt", "disposition": "shared_campus_evidence_exact_North_or_South_building_unresolved"},
    "osm_way_74475616": {"market": "Paris", "disposition": "shared_campus_evidence_exact_East_West_North_or_South_label_unresolved"},
    "osm_way_157178049": {"market": "London", "provider_record_code": "LON_EAST", "disposition": "exact_provider_label_match"},
    "osm_way_196783604": {"market": "London", "provider_record_code": "LON_NORTH", "disposition": "exact_provider_label_match"},
    "osm_node_2808423607": {"market": "Amsterdam", "disposition": "shared_campus_evidence_exact_West_or_East_building_unresolved"},
    "osm_node_8208598778": {"market": "Singapore", "provider_record_code": "SG_WOODLANDS", "disposition": "exact_provider_label_match_by_postcode"},
    "osm_node_8208598779": {"market": "Singapore", "provider_record_code": "SG_TAI_SENG", "disposition": "exact_provider_label_match_by_postcode"},
}


PORTFOLIO_CONTEXT = {
    "current_directory_named_facility_labels_with_numeric_MW": 16,
    "directory_card_MW_checksum": 497,
    "coming_soon_market_labels_without_numeric_MW": 2,
    "2025_ESG_data_centres_or_campuses": 8,
    "2025_ESG_tier_1_cities": 7,
    "2025_ESG_gross_floor_area_sqm_existing_and_in_progress": 410499,
    "2025_annual_completed_legal_investment_property_labels": 12,
    "2025_annual_development_property_labels": ["Frankfurt 3", "London South", "Madrid 2", "Johor"],
    "2025_annual_utility_power_supply_MVA": 488,
    "2025_annual_saleable_capacity_MW": 252,
    "capacity_boundary": "The 497MW directory checksum, 488MVA utility supply, 252MW saleable capacity, site engineering values, 38.8MW new signings and customer load use different definitions and are not additive.",
    "accelerator_boundary": "Global Switch supplies colocation space, power, cooling and connectivity. It is NVIDIA DGX-Ready and supports customer AI/HPC equipment, but does not disclose a Global Switch-owned or hosted GPU inventory by model, site, count, delivery state, power draw or utilization.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        combined = f"{row.get('name') or ''} {row.get('operator') or ''}".casefold()
        if "global switch" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    numeric = [row for row in RECORDS if isinstance(row.get("directory_card_mw"), (int, float))]
    assert len(RECORDS) == 18
    assert len(numeric) == 16
    assert sum(row["directory_card_mw"] for row in numeric) == 497
    assert len({row["record_code"] for row in RECORDS}) == len(RECORDS)
    assert len(candidates) == 7, [row["id"] for row in candidates]
    assert set(OSM_DISPOSITIONS) == {row["id"] for row in candidates}
    reviews = []
    for object_id, disposition in OSM_DISPOSITIONS.items():
        source = osm[object_id]
        reviews.append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            **disposition,
            "boundary": "OSM object identity and footprint do not prove official lifecycle, ownership, capacity, utility configuration, customer load or facility economics.",
        })
    records = [{
        "id": f"global_switch_{row['record_code'].lower()}",
        "object_type": "ProviderPublishedDataCenterFacilityOrExpansionRecord",
        "source_order": position,
        "operator": "Global Switch",
        "record_granularity": "provider_facility_label_or_coming_soon_market_not_uniform_physical_building_or_legal_property",
        **row,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "accessed_on": accessed_on,
    } for position, row in enumerate(RECORDS, 1)]
    return records, reviews


def build_summary(records: list[dict], osm_reviews: list[dict], accessed_on: str) -> dict:
    numeric = [row for row in records if isinstance(row.get("directory_card_mw"), (int, float))]
    return {
        "registry": "Global Switch current facility labels and coming-soon market expansions",
        "records": len(records),
        "current_directory_labels_with_numeric_MW": len(numeric),
        "coming_soon_market_labels_without_numeric_MW": len(records) - len(numeric),
        "directory_card_MW_checksum": sum(row["directory_card_mw"] for row in numeric),
        "directory_label_market_counts": dict(sorted(Counter(row["market"] for row in numeric).items())),
        "directory_label_country_counts": dict(sorted(Counter(row["country_code"] for row in numeric).items())),
        "related_OSM_objects": len(osm_reviews),
        "raw_operator_tagged_OSM_objects": sum(bool(row["osm_operator"]) for row in osm_reviews),
        "raw_name_only_OSM_objects": sum(bool(row["osm_name"]) and not row["osm_operator"] for row in osm_reviews),
        "exact_provider_label_OSM_matches": sum(row["disposition"].startswith("exact_provider") for row in osm_reviews),
        "shared_campus_OSM_objects_unresolved_to_exact_label": sum(row["disposition"].startswith("shared_campus") for row in osm_reviews),
        "osm_reviews": sorted(osm_reviews, key=lambda row: row["osm_object_id"]),
        "portfolio_context": PORTFOLIO_CONTEXT,
        "GPU_inventory": "undisclosed; readiness, DGX-Ready status, liquid cooling and hosted customer equipment do not establish Global Switch-owned GPUs",
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not equate or sum directory labels, campuses, legal properties, OSM objects, utility MVA, undefined card MW, saleable MW, signed MW, cooling MW, liquid-ready MW, live IT load or GPU inventory.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/global_switch_official_facility_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/global_switch_official_facility_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, osm_reviews = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
