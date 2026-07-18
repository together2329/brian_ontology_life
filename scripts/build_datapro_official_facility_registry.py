#!/usr/bin/env python3
"""Build a scope-preserving DataPro facility, finance and OSM registry.

DataPro's current directory shows four operating sites and a 6,550-rack
headline, while still-addressable pages expose two future buildings and a
25,000-plus-rack potential.  Several page cards disagree with their own detail
text, and launch years on the future pages are stale.  This builder retains
those conflicts instead of turning them into false live capacity.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://en.datapro.ru/"
DIRECTORY = "https://en.datapro.ru/data-centers"
BFO_ORGANIZATION = "https://bo.nalog.gov.ru/nbo/organizations/7668900"
BFO_REPORTS = "https://bo.nalog.gov.ru/nbo/organizations/7668900/bfo/"
RBC_COMPANY = "https://companies.rbc.ru/id/1137746000435-ooo-datapro/"
CNEWS_2024 = "https://corp.cnews.ru/reviews/tsentry_obrabotki_dannyh_2025/review_table/d2e45cfc70be7f70daf246462bb86f960ae21244"
CNEWS_2025 = "https://corp.cnews.ru/reviews/tsentry_obrabotki_dannyh_2025/articles/ot_defitsita_stojko-mest_v_rossii"
COMNEWS_2024 = "https://www.comnews.ru/content/234517/2024-08-02/2024-w31/1180/reyting-krupneyshie-operatory-kommercheskikh-data-centrov-rossii-stoykam-vvedennym-ekspluataciyu"
UPTIME_RUSSIA = "https://uptimeinstitute.com/uptime-institute-awards/country/id/RU"
TVER_HISTORY = "https://www.tadviser.ru/index.php/%D0%9F%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%3A%D0%A6%D0%9E%D0%94_DataPro_%D0%A2%D0%B2%D0%B5%D1%80%D1%8C"


def page(number: str) -> str:
    return f"https://en.datapro.ru/data-centers/datapro-moscow-{number.lower()}"


def facility(
    code: str,
    address: str,
    lifecycle: str,
    source_urls: list[str],
    published_metrics: dict,
    engineering: dict | None = None,
    conflicts: list[str] | None = None,
    roster_role: str = "current_provider_directory",
) -> dict:
    return {
        "id": f"datapro_{code.lower()}",
        "facility_code": f"DataPro_{code}",
        "country_code": "RU",
        "market": "Moscow_region" if code != "Tver" else "Tver",
        "address": address,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "roster_role": roster_role,
        "published_metrics": published_metrics,
        "engineering_and_equipment_evidence": engineering or {},
        "publication_conflicts": conflicts or [],
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "high_density_or_cloud_capability_is_not_GPU_inventory": True,
        "source_urls": list(dict.fromkeys(source_urls)),
    }


COMMON_ENGINEERING = {
    "cooling_redundancy": "N+1_each_system_independent",
    "modular_cooling_unit_published_rating_kw": 125,
    "utility_inlets": 2,
    "IT_power_reservation_topology": "4/3N",
    "cooling_power_redundancy": "2N",
    "dynamic_UPS_published_rating_kw_each": 1520,
    "switchgear_published_value_verbatim": "10 kWatts",
    "dry_air_cooled_transformer_published_rating_kw_each": 1600,
    "unit_warning": "Provider English pages use mWatts and kWatts where MW, kV or kVA may have been intended; values are retained as published and are not silently normalized.",
}


FACILITIES = [
    facility(
        "I",
        "Moscow, Aviamotornaya Street 69",
        "operating",
        [page("i"), "https://en.datapro.ru/public/documents/pdf1_en.pdf?v=4", UPTIME_RUSSIA],
        {
            "current_racks": 2000,
            "projected_racks": 4000,
            "projected_area_sqm": 20000,
            "projected_gross_facility_power_mw_more_than": 20,
            "provider_resiliency_label": "Tier_III",
        },
        {
            "cooling": ["Schneider_Electric_EcoBreeze_modular", "precision_air_conditioning"],
            "utility_inlets": 2,
            "IT_power_reservation_topology": "4/3N",
            "dynamic_UPS": "KINOLT_and_Hitec_Power_Protection_1670_published_kWatts_each",
            "distribution_substations": ["Siemens", "Eaton"],
            "dry_air_cooled_transformer_published_rating_kw_each": 1600,
            "Uptime_current_public_registry": ["Tier_III_Design_Documents", "Tier_III_Constructed_Facility_stage_1"],
        },
    ),
    facility(
        "II",
        "Khimki, 74 km MKAD, possession 3",
        "operating",
        [page("ii"), "https://en.datapro.ru/public/documents/pdf2_en.pdf?v=4", UPTIME_RUSSIA],
        {
            "card_current_or_capacity_usage_racks": 1500,
            "detail_current_racks": 1600,
            "card_projected_racks": 1500,
            "projected_area_sqm": 6000,
            "gross_facility_power_mw": 11,
            "provider_resiliency_label": "Tier_IV",
        },
        {
            **COMMON_ENGINEERING,
            "static_UPS": "Vertiv_Emerson_1200_published_kWatts",
            "provider_page_certificate_claim": ["Uptime_Tier_IV_Design", "Uptime_Tier_IV_Facility"],
            "Uptime_current_public_registry_exact_site_match": "not_found_in_reviewed_Russia_list",
        },
        ["Current page card says 1,500 racks while detail text says 1,600; neither is overwritten."],
    ),
    facility(
        "III",
        "Moscow, Ryabinovaya Street 53 building 3",
        "operating_launched_Q1_2022",
        [page("iii"), "https://en.datapro.ru/public/documents/pdf3_en.pdf?v=4", UPTIME_RUSSIA],
        {
            "launch": "Q1_2022",
            "card_projected_racks": 4200,
            "detail_projected_racks": 4000,
            "current_racks_site_page": "undisclosed",
            "projected_area_sqm": 20000,
            "gross_facility_power_mw": 30,
            "provider_resiliency_label": "Tier_IV",
        },
        {
            **COMMON_ENGINEERING,
            "static_UPS": "Vertiv_Emerson_2x800_published_kWatts",
            "provider_page_certificate_claim": ["Uptime_Tier_IV_Design", "Uptime_Tier_IV_Facility"],
            "Uptime_current_public_registry_exact_site_match": "not_found_in_reviewed_Russia_list",
        },
        ["Current page card says 4,200 projected racks while detail text and PDF say 4,000."],
    ),
    facility(
        "IV",
        "Moscow, Ryabinovaya Street 53 building 4",
        "operating",
        [page("iv"), "https://en.datapro.ru/public/documents/pdf4_en.pdf?v=4", UPTIME_RUSSIA],
        {
            "card_current_racks": 1100,
            "detail_current_racks": 200,
            "card_projected_racks": 1100,
            "detail_projected_racks": 1000,
            "projected_area_sqm": 4000,
            "gross_facility_power_mw": 9,
            "provider_resiliency_label": "Tier_IV",
        },
        {
            **COMMON_ENGINEERING,
            "static_UPS": "Vertiv_Emerson_2x800_published_kWatts",
            "provider_page_certificate_claim": ["Uptime_Tier_IV_Design", "Uptime_Tier_IV_Facility"],
            "Uptime_current_public_registry_exact_site_match": "not_found_in_reviewed_Russia_list",
        },
        ["Current card and detail body disagree on both current and projected racks; all four values are retained."],
    ),
    facility(
        "V",
        "Moscow, Ryabinovaya Street 53 building 5",
        "delayed_or_deferred_development_exact_current_construction_state_unconfirmed",
        [page("v"), "https://en.datapro.ru/public/documents/pdf5_en.pdf?v=4", CNEWS_2025, COMNEWS_2024],
        {
            "official_page_launch_year_stale": 2023,
            "projected_racks": 7000,
            "projected_area_sqm": 35000,
            "gross_facility_power_mw": 50,
            "provider_resiliency_label": "Tier_IV",
        },
        {
            **COMMON_ENGINEERING,
            "static_UPS": "Vertiv_Emerson_2x800_published_kWatts",
            "provider_page_certificate_claim": ["Uptime_Tier_IV_Design", "Uptime_Tier_IV_Facility"],
        },
        [
            "Provider page still says launch 2023 but the site is absent from the current four-site directory.",
            "CNews reports DataPro added zero racks in 2025 and remained at 6,553 racks, so the planned 2025 opening is not treated as operating.",
        ],
        "addressable_legacy_project_page_not_current_directory",
    ),
    facility(
        "VI",
        "Moscow, Ryabinovaya Street 53 building 2",
        "planned_or_deferred_exact_current_construction_state_unconfirmed",
        [page("vi"), CNEWS_2025, COMNEWS_2024],
        {
            "official_page_launch_year_stale": 2025,
            "secondary_2024_schedule_year": 2027,
            "projected_racks": 8000,
            "gross_facility_power_mw": "undisclosed",
            "provider_resiliency_label": "Tier_IV",
        },
        {},
        [
            "Provider page says 2025 while a 2024 industry roster moved launch to 2027.",
            "CNews reports zero new DataPro racks in 2025; neither date proves current construction or operation as of the evidence snapshot.",
        ],
        "addressable_legacy_project_page_not_current_directory",
    ),
    facility(
        "Tver",
        "Tver, Dmitry Donskoy Street",
        "former_DataPro_asset_sold_to_RT_Invest_Transport_Systems_in_2015",
        [TVER_HISTORY, UPTIME_RUSSIA],
        {
            "commercial_launch_year": 2013,
            "racks": 400,
            "gross_facility_power_mw": 4.5,
            "gross_area_sqm": 2650,
        },
        {
            "historical_reservation_topology": "3/2N",
            "historical_high_density_rack_power_kw_up_to": 20,
            "Uptime_current_public_registry": ["Tier_III_Design_Documents"],
        },
        ["Former asset is retained for operator history and is excluded from the current DataPro roster and capacity."],
        "former_asset_outside_current_provider_directory",
    ),
]


OSM_CROSSWALK = {
    "osm_way_166679654": ("datapro_i", "current_operating_building", "coordinate_and_Aviamotornaya_site_match"),
    "osm_relation_16532317": ("datapro_ii", "current_operating_site_relation", "name_and_Khimki_coordinate_match"),
    "osm_way_37176485": ("datapro_iii", "current_operating_building", "exact_name_building_number_and_coordinate_match"),
    "osm_way_37176483": ("datapro_iv", "current_operating_building", "exact_name_building_number_and_coordinate_match"),
    "osm_way_37176481": ("datapro_v", "future_or_deferred_project_building_not_current_operating_capacity", "exact_name_building_number_and_coordinate_match"),
    "osm_way_37176486": ("datapro_vi", "future_or_deferred_project_building_not_current_operating_capacity", "exact_name_and_Ryabinovaya_cluster_match"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = [
        {
            "object_type": "DataCenterFacilityEvidence",
            "source_order": order,
            "operator_or_historical_operator": "DataPro",
            "accessed_on": accessed_on,
            **item,
        }
        for order, item in enumerate(FACILITIES, 1)
    ]
    assert len(records) == 7
    assert sum(row["lifecycle_as_of_2026_07_19"].startswith("operating") for row in records) == 4
    assert len({row["facility_code"] for row in records}) == 7
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, classification, basis) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "facility_ref": facility_ref,
            "current_classification": classification,
            "match_basis": basis,
            "capacity_counting_rule": "Only current operating classifications may contribute to a current-site count; an OSM building does not prove racks are installed or energized.",
        })
    assert len(rows) == 6
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    lifecycle_counts = Counter(row["roster_role"] for row in records)
    finance_2025_rub_thousand = {
        "revenue": 5534902,
        "cost_of_sales": 2608088,
        "gross_profit": 2926814,
        "commercial_and_administrative_expenses": 214017,
        "operating_profit": 2712797,
        "interest_income": 40377,
        "interest_expense": 228463,
        "profit_before_tax": 2506466,
        "net_profit": 1872414,
        "operating_cash_flow": 2502408,
        "purchases_of_noncurrent_assets_cash_outflow": 458108,
        "dividends_cash_outflow": 1880000,
        "cash": 236774,
        "fixed_assets_net": 9952907,
        "total_assets": 11215219,
        "equity": 8597003,
        "long_term_liabilities": 2273694,
        "short_term_liabilities": 344522,
        "interest_bearing_borrowings_balance_sheet_lines_1410_and_1510": 0,
    }
    return {
        "id": "datapro_official_facility_summary_2026_07_19",
        "operator": "DataPro",
        "accessed_on": accessed_on,
        "facility_scope": {
            "current_provider_directory_sites": 4,
            "addressable_future_project_pages_outside_current_directory": 2,
            "former_operator_asset_records": 1,
            "roster_role_counts": dict(sorted(lifecycle_counts.items())),
        },
        "rack_reconciliation": {
            "provider_current_headline_racks": 6550,
            "CNews_end_2025_racks": 6553,
            "CNews_new_racks_in_2025": 0,
            "current_directory_card_projected_rack_checksum": 10800,
            "future_V_and_VI_projected_rack_checksum": 15000,
            "six_page_projected_rack_checksum": 25800,
            "provider_development_potential_headline_racks_more_than": 25000,
            "boundary": "Current racks, card or detail projected racks, and future potential are different denominators. Internal page conflicts prevent a defensible per-site allocation of the 6,550/6,553 current portfolio total.",
        },
        "power_reconciliation": {
            "four_current_page_gross_facility_power_checksum_mw_more_than": 70,
            "DataPro_V_gross_facility_power_mw": 50,
            "DataPro_VI_power": "undisclosed",
            "boundary": "Provider general-capacity values are gross facility or input measures, not current critical IT, utilized, billed or instantaneous load; they are not summed with rack power.",
        },
        "certification_reconciliation": {
            "provider_claims": "DataPro I Tier III and DataPro II-IV Tier IV Design/Facility",
            "current_Uptime_Russia_public_registry_exact_DataPro_matches": ["DataPro_Moscow_1_Tier_III_Design_and_Constructed_Facility", "DataPro_Tver_Tier_III_Design"],
            "DataPro_II_III_IV_exact_public_registry_matches": "not_found",
            "boundary": "Provider claims and the current Uptime public award roster are retained as separate evidence; absence from the reviewed roster is not rewritten as proof that an award never existed.",
        },
        "financial_boundary": {
            "legal_entity": "ООО ДАТАПРО",
            "INN": "7704825145",
            "OGRN": "1137746000435",
            "reporting_period": "2025",
            "unit": "RUB_thousand",
            "accounting_basis": "Russian_statutory_BFO_unconsolidated_legal_entity",
            "official_BFO_values": finance_2025_rub_thousand,
            "derived_metrics_percent": {
                "revenue_growth": 9.23,
                "operating_profit_growth": 9.55,
                "net_profit_growth": 4.20,
                "operating_margin": 49.01,
                "net_margin": 33.83,
                "operating_cash_flow_margin": 45.21,
                "noncurrent_asset_purchase_intensity": 8.28,
            },
            "derived_free_cash_flow_proxy_RUB_thousand": 2044300,
            "prior_year_comparatives_RUB_thousand": {"revenue": 5067329, "operating_profit": 2476403, "net_profit": 1796963},
            "ownership_from_EGRUL_secondary_display": {"Evgeny_Bogdanchikov_percent": 51.33, "Tatyana_Bogdanchikova_percent": 48.67},
            "boundary": "The BFO values cover the Russian legal entity, not site-level economics. Free cash flow is only operating cash flow less cash purchases of noncurrent assets, not a company-defined KPI. Zero borrowings in lines 1410/1510 does not eliminate lease, supplier, other-liability or off-balance-sheet obligations.",
        },
        "accelerator_and_AI_boundary": {
            "portfolio_owned_GPU_model_count_site_delivery_fabric_power_and_utilization": "undisclosed",
            "public_high_density_context_kw_per_rack_up_to": 20,
            "owned_or_customer_hardware_split": "undisclosed",
            "accelerator_ledger_action": "no_numeric_row_created",
            "boundary": "A colocation site that can host a 20-kW rack does not establish any GPU model or unit count, and is below modern liquid-cooled AI-rack designs without further retrofit evidence.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "current_operating_objects": sum(row["current_classification"].startswith("current_operating") for row in osm_rows),
            "future_or_deferred_project_objects": sum("future_or_deferred" in row["current_classification"] for row in osm_rows),
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [
            DIRECTORY, page("i"), page("ii"), page("iii"), page("iv"), page("v"), page("vi"),
            BFO_ORGANIZATION, BFO_REPORTS, RBC_COMPANY, CNEWS_2024, CNEWS_2025, COMNEWS_2024,
            UPTIME_RUSSIA, TVER_HISTORY,
        ],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_rows = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "datapro_official_facility_registry.jsonl"
    summary_path = args.output_dir / "datapro_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
