#!/usr/bin/env python3
"""Build CloudHQ's current campus-page registry and OSM crosswalk.

CloudHQ currently exposes 20 WordPress campus records while its portfolio page
reports 23 global campuses.  The page cards contain mixed operating, contracted,
under-construction and future capacity, and several card values conflict with
their own narrative.  This builder retains those disclosures as checksums and
does not relabel them as live or utilized IT load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME_URL = "https://cloudhq.com/"
CAMPUSES_URL = "https://cloudhq.com/campuses/"
ABOUT_URL = "https://cloudhq.com/about/"
SUSTAINABILITY_URL = "https://cloudhq.com/sustainability/"
WATER_URL = "https://cloudhq.com/water-is-precious/"
PARIS_RENEWABLE_URL = "https://cloudhq.com/first-steps-to-carbon-neutral-in-paris/"
MILAN_CIRCULAR_URL = "https://cloudhq.com/a-new-life-in-milan/"
SP_PRESALE_URL = "https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3542678"
FITCH_URL = "https://www.fitchratings.com/topics/data-center-and-digital-infrastructure"
SEC_AUP_URL = "https://www.sec.gov/Archives/edgar/data/2122128/000110465926040349/tm2610102d1_ex99-1.htm"
MEXICO_GOV_URL = "https://www.gob.mx/presidencia/prensa/plan-mexico-avanza-se-anuncia-inversion-de-4-mil-800-mdd-de-cloudhq-para-la-construccion-de-6-centros-de-datos-en-queretaro?idiom=es-MX"


def campus(
    code: str,
    slug: str,
    city: str,
    region: str,
    country_code: str,
    latitude: float,
    longitude: float,
    area_raw: str | None,
    available_mw: float,
    total_mw: float,
    rfs_text: str,
    overview: str,
    lifecycle: str = "current_marketed_mixed_lifecycle_status_not_fully_verified",
    **extra: object,
) -> dict:
    return {
        "campus_code": code,
        "city": city,
        "region": region,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "campus_url": f"https://cloudhq.com/campus/{slug}/",
        "current_page_area_raw": area_raw,
        "current_page_available_critical_load_mw": available_mw,
        "current_page_total_critical_it_load_mw": total_mw,
        "current_page_rfs_text": rfs_text,
        "current_page_overview": overview,
        "lifecycle_as_of_2026_07_19": lifecycle,
        **extra,
    }


CAMPUSES = [
    campus("AMS", "ams-campus", "Amsterdam / Schiphol-Rijk", "North Holland", "NL", 52.28208, 4.74543,
           "533,890 SF | 49,600 SM", 84, 84, "RFS Within 22 Months",
           "One planned multi-story data center with up to 84 MW critical IT load; power is contracted from the new A4 Zone substation in a diverse configuration.",
           buildings_context={"planned_data_centers": 1}, power_context={"source": "A4 Zone substation", "delivery": "contracted", "configuration": "diverse"}),
    campus("BKK", "bkk-campus", "Bangkok", "Chonburi vicinity", "TH", 13.01023, 101.08196,
           "726,000 SF | 67,448 SM", 108, 108, "RFS within 22 months",
           "Planned 108-MW critical-IT-load data center outside Bangkok with an on-site substation and access to multiple high-density fiber carriers.",
           buildings_context={"planned_data_centers": 1}, power_context={"substation": "on_site"}),
    campus("CDG", "cdg-campus", "Lisses / Paris", "Île-de-France", "FR", 48.59768, 2.40782,
           "900,00 SF | 83,613 SM", 74, 150, "RFS Within 22 Months",
           "Two fully permitted 74.4-MW IT-load buildings powered by a new 225-kV on-site substation.",
           buildings_context={"buildings": 2, "it_load_mw_each": 74.4, "narrative_sum_mw": 148.8}, power_context={"substation_kv": 225, "substation": "on_site"},
           environment_context={"planned_renewable_power_percent": 100},
           source_conflict="The card says 74 MW available and 150 MW total; two times 74.4 MW equals 148.8 MW. The raw card and narrative are retained separately."),
    campus("CLP", "clp-campus", "Culpeper", "VA", "US", 38.4620783, -77.9776797,
           "954,190 SF | 88,646 SM", 215, 215, "RFS in 2027",
           "Development campus near Culpeper; the narrative says three data centers will provide up to 142 MW from an on-site substation.",
           lifecycle="development_coordination_and_current_scale_conflict", buildings_context={"planned_data_centers": 3}, power_context={"substation": "on_site"},
           source_conflict="The current card says 215 MW while its narrative says 142 MW upon completion; neither is relabeled as operating capacity."),
    campus("FRA_HOCHST", "fra-campus-hochst", "Frankfurt-Höchst", "Hesse", "DE", 50.07940, 8.54088,
           "2,330,000 SF | 216,743 SM", 90, 224, "RFS Within 22 Months",
           "Second Frankfurt-area campus; the narrative says a 300-MW on-site utility connection enables 276 MW of critical IT load.",
           power_context={"onsite_utility_connection_mw": 300, "narrative_critical_it_load_mw": 276},
           source_conflict="The current card says 90 MW available and 224 MW total, versus 276 MW enabled by a 300-MW connection in the narrative."),
    campus("FRA_OFFENBACH", "fra-campus-offenbach", "Offenbach", "Hesse", "DE", 50.10932, 8.80648,
           "1,166,500 SF | 108,371 SM", 0, 112, "RFS Entered Service 2023",
           "Two fully permitted 56-MW critical-IT-load buildings powered by a new 110-kV on-site substation.",
           lifecycle="operating_entered_service_2023_with_zero_available_card_capacity", buildings_context={"buildings": 2, "it_load_mw_each": 56}, power_context={"substation_kv": 110, "substation": "on_site"}),
    campus("FRA7_OFFENBACH", "fra7-campus-offenbach", "Offenbach", "Hesse", "DE", 50.10779, 8.78910,
           None, 90, 90, "RFS Within 22 Months",
           "A planned 90-MW three-story data center near FRA1-2, scheduled to begin development in 2027 and enter service in 2029 with LEED Gold, about 1,950 square metres of solar panels and 50 MW of waste heat for EVO.",
           lifecycle="planned_development_2027_target_service_2029", buildings_context={"planned_data_centers": 1, "stories": 3}, environment_context={"LEED_target": "Gold", "solar_panel_area_sqm_approximately": 1950, "waste_heat_to_EVO_mw": 50}),
    campus("GIG", "gig-campus", "São João de Meriti / Rio de Janeiro", "RJ", "BR", -22.79426, -43.35038,
           "483,922 SF | 49,958 SM", 36, 36, "RFS Within 22 Months",
           "One data center providing 36 MW of critical IT load with access to multiple fiber providers.", buildings_context={"data_centers": 1}),
    campus("GRU", "gru-campus", "Paulínia / Campinas", "SP", "BR", -22.77089, -47.10425,
           "1,657,340 SF | 153,972 SM", 288, 288, "RFS Within 22 Months",
           "Two phases of three 48-MW data centers each, powered by an on-site substation and authorized to connect to the Brazilian National Grid.",
           buildings_context={"phases": 2, "data_centers_per_phase": 3, "it_load_mw_per_data_center": 48}, power_context={"substation": "on_site", "grid": "Brazilian_National_Grid_authorization"}),
    campus("KIX", "kix-campus", "Osaka / Nanko Kita", "Osaka", "JP", 34.63940, 135.42107,
           "1,345,489 SF | 125,000 SM", 96.4, 96.4, "RFS Planned for June 2025",
           "Cosmosquare 96-MW hyperscale campus planned in three phases named KIX1, KIX2 and KIX3.",
           lifecycle="current_page_contains_elapsed_RFS_target_without_reviewed_operating_confirmation", buildings_context={"phases": ["KIX1", "KIX2", "KIX3"]},
           schedule_boundary="The June 2025 RFS wording is still present after the date passed; this registry does not infer delivery or operation."),
    campus("LC", "lc-campus", "Ashburn", "VA", "US", 39.01015, -77.46270,
           "8,500,00 SF | 789.676 SM", 756, 1256, "RFS Within 20 Months",
           "Ashburn campus planned for more than 1.7 GW of customer critical IT load across fourteen data centers; LC3 and LC4 are described as under construction.",
           lifecycle="mixed_two_operating_ABS_assets_active_construction_and_long_term_plan", buildings_context={"planned_data_centers": 14, "under_construction": ["LC3", "LC4"], "operating_ABS_assets": ["LC1A", "LC2"]},
           power_context={"narrative_planned_customer_critical_it_load_gw_more_than": 1.7},
           source_conflict="The card says 756 MW available and 1,256 MW total, while narrative says more than 1.7 GW planned. Area punctuation is malformed and is retained raw."),
    campus("LHR", "lhr-campus-2", "Didcot", "Oxfordshire", "GB", 51.62773, -1.27040,
           "2,250,000 SF | 209,032 SM", 101, 101, "RFS Within 22 Months",
           "37.5-acre fully permitted and powered campus offering over 100 MW IT load with capacity to expand to 300 MW, adjacent to a 400-kV National Grid substation.",
           power_context={"current_offer_mw_more_than": 100, "expansion_capacity_mw": 300, "adjacent_grid_substation_kv": 400}),
    campus("MCC", "mcc-campus", "Manassas", "VA", "US", 38.71955, -77.49819,
           "2,232,875 SF | 207,441 SM", 96, 382, "RFS Within 20 Months",
           "Inaugural Manassas campus with more than 375 MW across seven data centers; MCC5 is site-plan approved and MCC7 was slated for construction in mid-2025 with Q3 2026 RFS.",
           lifecycle="mixed_operating_leased_and_future_buildings_with_elapsed_schedule_points", buildings_context={"data_centers": 7, "MCC5": "site_plan_approved", "MCC7": "dated_mid_2025_construction_and_Q3_2026_RFS_target"}, power_context={"narrative_critical_it_load_mw_more_than": 375}),
    campus("MDC", "mdc-campus", "Manassas", "VA", "US", 38.73088, -77.50829,
           "1,000,000 SF | 92,903 SM", 300, 300, "RFS Within 20 Months",
           "Manassas campus with two planned on-site substations providing up to 300 MW; MDC1 marketed as serviceable within 22 months of commitment.",
           buildings_context={"first_data_center": "MDC1"}, power_context={"onsite_substations": 2}),
    campus("MSP", "msp-campus", "Chaska", "MN", "US", 44.81068, -93.63557,
           "1,100,000 SF | 102,193 SM", 200, 200, "RFS Within 20 Months",
           "Up to 200 MW of critical IT load in one or two customizable data centers served by an on-site substation.",
           buildings_context={"planned_data_centers": "one_or_two"}, power_context={"substation": "on_site"}),
    campus("MXP", "mxp-campus", "Milan", "Lombardy", "IT", 45.46866, 8.87342,
           "2,200,000 SF | 204,387 SM", 240, 240, "RFS Within 2026",
           "54-acre campus with four 48-MW IT-load buildings; page says permitting is in progress, first phase was expected in 2024 and 240 MW was secured from the transmission-grid operator.",
           lifecycle="development_with_stale_first_phase_target_and_2026_RFS_wording", buildings_context={"buildings": 4, "it_load_mw_each": 48, "narrative_building_sum_mw": 192}, power_context={"secured_grid_mw": 240},
           environment_context={"brownfield_reuse_percent": 99.9, "waste_diverted_tons_approximately": 300000, "water": "non_potable_groundwater_and_irrigation_channel_discharge"},
           source_conflict="Four times 48 MW equals 192 MW, while the card and secured-grid statements say 240 MW. The 2024 first-phase expectation has elapsed without reviewed operating confirmation."),
    campus("ORD", "ord-campus", "Mount Prospect / Chicago", "IL", "US", 42.03501, -87.95370,
           "1,700,000 SF | 157,935 SM", 252, 252, "RFS Within 20 Months",
           "Redevelopment of the former United Airlines headquarters; narrative says up to 300 MW critical IT load via an on-site substation.",
           power_context={"substation": "on_site", "narrative_critical_it_load_mw_up_to": 300},
           source_conflict="The card says 252 MW available and total, while narrative says up to 300 MW."),
    campus("QRO", "qro-campus", "Querétaro", "Querétaro", "MX", 20.61983, -100.14740,
           "2,738,340 SF | 254,400 SM", 360, 360, "RFS Within 2027",
           "Campus designed for six 48-MW IT-load buildings powered by an on-site substation via 400-kV transmission.",
           lifecycle="development_with_2027_RFS_target", buildings_context={"planned_data_centers": 6, "it_load_mw_each": 48, "narrative_building_sum_mw": 288}, power_context={"substation": "on_site", "transmission_kv": 400},
           investment_context={"government_announced_investment_USD_billion": 4.8, "site_hectares": 52, "government_announced_electrical_capacity_mw": 900, "construction_jobs": 7200, "permanent_jobs": 900},
           environment_context={"government_description": "waterless_cooling_and_LEED_Gold_and_Silver"},
           source_conflict="The card says 360 MW total IT, six times 48 MW equals 288 MW, and the Mexican government announcement says 900 MW electrical capacity; these denominators are not interchangeable."),
    campus("SAT", "sat-campus", "San Antonio", "TX", "US", 29.41681, -98.79809,
           "3,023,300 SF | 280,595 SM", 600, 600, "RFS Within 2027",
           "Five planned customizable data centers providing up to 600 MW critical IT load, eventually served by multiple on-site substations.",
           lifecycle="planned_development_with_2027_RFS_target", buildings_context={"planned_data_centers": 5}, power_context={"substations": "multiple_on_site_planned"}),
    campus("SJC", "sjc-campus", "Santa Clara", "CA", "US", 37.35936, -121.94266,
           "300,00 SF | 27,871 SM", 42, 42, "RFS Within 2030",
           "Planned multi-story SJC1 with flexible room densities, exterior-mounted backup generators, rooftop air-cooled chillers and an on-site medium-voltage substation.",
           lifecycle="planned_development_with_2030_RFS_target", buildings_context={"planned_data_centers": 1, "facility": "SJC1"},
           equipment_context={"backup": "exterior_mounted_generators", "cooling": "rooftop_air_cooled_chillers", "substation": "on_site_medium_voltage"}),
]


OSM_TO_CAMPUS = {
    "osm_way_1125276312": "FRA_OFFENBACH",
    "osm_way_1409758368": "CDG",
    "osm_way_1343774537": "LC",
    "osm_way_1381994242": "LC",
    "osm_way_794147654": "LC",
    "osm_way_794147655": "LC",
    "osm_way_1443187163": "LC",
    "osm_way_882977350": "MCC",
    "osm_way_996899489": "MCC",
    "osm_way_1227614670": "MCC",
}


PORTFOLIO_CONTEXT = {
    "current_WordPress_campus_pages": 20,
    "company_headline_global_campuses": 23,
    "global_data_center_inventory_gw_more_than": 5.2,
    "data_center_space_delivered_sqft_more_than": 9200000,
    "critical_IT_load_contracted_mw_more_than": 1380,
    "land_acquired_acres_more_than": 1000,
    "current_20_card_total_critical_IT_load_checksum_mw": 5136.4,
    "current_20_card_available_critical_load_checksum_mw": 4028.4,
    "checksum_boundary": "The page sums combine operating, zero-available, available, contracted, under-construction and future RFS capacity. They are not current energized, leased, utilized or billed load and do not explain the 23-campus/20-page gap.",
    "ABS_pool_2026_presale": {
        "assets": ["LC1A", "LC2"],
        "completed_operating_data_centers": 2,
        "gross_area_sqft": 1054211,
        "leased_and_ramped_critical_load_mw": 160,
        "tenants": 2,
        "lease_type": "100_percent_turnkey_and_triple_net",
        "annualized_adjusted_base_rent_USD_million": 110.7,
        "appraised_value_USD_million": 2002,
        "SP_value_USD_million": 1101,
        "weighted_average_remaining_lease_years": 14.2,
        "closing_DSCR": 1.65,
        "largest_tenant_AABR_percent": 52.3,
        "second_tenant_AABR_percent": 47.7,
        "proposed_notes_USD_million": 1400,
        "manager_fee_percent_of_base_rent": 1.45,
        "maintenance_capex_USD_per_kW_per_month": 0.25,
        "maintenance_capex_annual_escalator_percent": 2,
        "boundary": "A securitized two-asset pool is not CloudHQ consolidated revenue, operating profit, EBITDA, debt, capex, cash flow, valuation or portfolio customer concentration.",
    },
    "accelerators": {
        "CloudHQ_owned_GPU_inventory_by_model_site_and_utilization": "undisclosed",
        "ABS_turnkey_boundary": "CloudHQ or the landlord owns critical mechanical and electrical infrastructure and supplies space, power, cooling and security; the tenants are responsible for servers, racks, networking and other computing infrastructure.",
    },
    "ownership_and_finance": {
        "founded": 2016,
        "founder": "Hossein Fateh",
        "group": "Fateh Family Office",
        "affiliates": ["CloudCapital", "WindHQ", "Dalian_Development"],
        "SP_reported_hyperscale_data_centers_leased": 16,
        "SP_reported_leased_capacity_mw": 1380,
        "SP_reported_assets_sold_to_related_CloudCapital": 5,
        "current_exact_cap_table_enterprise_value_revenue_operating_income_EBITDA_capex_debt_cash_flow_and_site_returns": "undisclosed",
    },
    "environment": {
        "net_zero_target_year": 2040,
        "CDG_planned_renewable_power_percent": 100,
        "water_policy": "minimize_water_and_use_evaporative_heat_rejection_only_when_land_and_energy_tradeoff_supports_it",
        "Ashburn_water": "greywater_where_evaporative_heat_rejection_is_required",
        "Milan_water": "non_potable_groundwater_with_excess_to_irrigation_channels",
        "fleet_PUE_WUE_energy_water_emissions_and_renewable_share": "undisclosed",
    },
}


COMMON_SOURCES = [HOME_URL, CAMPUSES_URL, ABOUT_URL, SUSTAINABILITY_URL, WATER_URL,
                  PARIS_RENEWABLE_URL, MILAN_CIRCULAR_URL, SP_PRESALE_URL,
                  FITCH_URL, SEC_AUP_URL, MEXICO_GOV_URL]


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
        if "cloudhq" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(CAMPUSES) == 20
    assert len({row["campus_code"] for row in CAMPUSES}) == 20
    assert round(sum(row["current_page_total_critical_it_load_mw"] for row in CAMPUSES), 1) == 5136.4
    assert round(sum(row["current_page_available_critical_load_mw"] for row in CAMPUSES), 1) == 4028.4
    assert len(candidates) == 10, [row["id"] for row in candidates]
    assert set(OSM_TO_CAMPUS) == {row["id"] for row in candidates}

    mapped: dict[str, list[dict]] = {}
    for object_id, code in OSM_TO_CAMPUS.items():
        source = osm[object_id]
        mapped.setdefault(code, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": "OSM geometry is public map evidence, not provider-certified ownership, lifecycle, physical-building granularity, load, tenant or finance evidence.",
        })

    records = []
    for position, source in enumerate(CAMPUSES, start=1):
        records.append({
            "id": f"cloudhq_{source['campus_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterCampusPage",
            "source_order": position,
            "operator": "CloudHQ",
            "record_granularity": "provider_campus_page_not_necessarily_one_building_or_operating_asset",
            **source,
            "osm_map_evidence": sorted(mapped.get(source["campus_code"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source["campus_url"], *COMMON_SOURCES])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    mapped_count = sum(len(row["osm_map_evidence"]) for row in records)
    assert mapped_count == 10
    return {
        "registry": "CloudHQ current official campus pages and OSM crosswalk",
        "current_official_campus_pages": len(records),
        "company_headline_global_campuses": 23,
        "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "lifecycle_counts": dict(sorted(Counter(row["lifecycle_as_of_2026_07_19"] for row in records).items())),
        "current_card_total_critical_IT_load_checksum_mw": round(sum(row["current_page_total_critical_it_load_mw"] for row in records), 1),
        "current_card_available_critical_load_checksum_mw": round(sum(row["current_page_available_critical_load_mw"] for row in records), 1),
        "related_OSM_objects": len(candidates),
        "raw_operator_tagged_OSM_objects": sum((row.get("operator") or "").casefold() == "cloudhq" for row in candidates),
        "mapped_OSM_objects": mapped_count,
        "campus_pages_with_OSM_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "unmatched_related_OSM_objects": [],
        "portfolio_context": PORTFOLIO_CONTEXT,
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum or equate campus cards, narrative MW, 23-campus headline, ABS assets, future RFS, tenant computing equipment, investment plans or OSM objects as one operating-building, live-load, GPU, revenue, debt or valuation total.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/cloudhq_official_campus_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/cloudhq_official_campus_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, candidates = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
