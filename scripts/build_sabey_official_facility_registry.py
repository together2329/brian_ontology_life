#!/usr/bin/env python3
"""Build Sabey's current U.S. campus registry and OSM crosswalk.

Sabey's public location sitemap exposes seven campus pages, while current
corporate reporting says six campuses were energized at 31 March 2026 and the
2024 sustainability report separately identifies Umatilla and North Texas as
developments.  The builder preserves those different dates and granularities.
It also keeps customer-owned Horizon accelerators, campus design power, built
powered shell, availability, operating capacity and actual load separate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME_URL = "https://sabeydatacenters.com/"
SITEMAP_URL = "https://sabeydatacenters.com/sitemaps-1-section-locations-2-sitemap.xml"
ARES_URL = "https://sabey.com/news/sabey-data-center-properties-welcomes-strategic-investment-from-ares-strengthening-platform-for-continued-growth"
SUSTAINABILITY_URL = "https://39943764.fs1.hubspotusercontent-na1.net/hubfs/39943764/SDC%20Downloadables/Sustainability/2024%20Sustainability%20Report%20External%201.pdf"
SUSTAINABILITY_RELEASE_URL = "https://sabeydatacenters.com/news/sabey-achieves-over-25-carbon-emissions-cut-pioneers-advanced-nuclear-partnership"
HORIZON_NEWS_URL = "https://tacc.utexas.edu/news/latest-news/2026/07/07/opening-the-future-of-science/"
HORIZON_SYSTEM_URL = "https://tacc.utexas.edu/systems/horizon/"
HORIZON_CONSTRUCTION_URL = "https://lccf.tacc.utexas.edu/construction-updates/2026/new-lccf-datacenter-nears-completion/"
JETCOOL_URL = "https://sabeydatacenters.com/news/sabey-expands-partnership-with-jetcool-technologies-to-accelerate-sustainable-high-density-compute"
OPTICOOL_URL = "https://sabeydatacenters.com/news/sabey-announces-strategic-partnership-with-opticool-technologies"
TERRAPOWER_URL = "https://sabeydatacenters.com/news/terrapower-and-sabey-data-centers-developing-strategic-collaboration-agreement-for-wide-scale-deployment-of-natrium-plants"
UMATILLA_ANNOUNCEMENT_URL = "https://sabeydatacenters.com/news/sabey-data-centers-to-build-new-data-center-campus-in-umatilla-oregon"
UMATILLA_CUTSHEET_URL = "https://info.sabeydatacenters.com/hubfs/SDC%20Downloadables/SDC%20Cutsheets/SDC%20Umatilla%2009242024.pdf"
ASHBURN_EXPANSION_URL = "https://sabeydatacenters.com/news/sabey-breaks-ground-on-final-phase-of-ashburn-campus-expansion"
MANHATTAN_AI_URL = "https://sabeydatacenters.com/news/sdc-manhattan-the-ideal-hub-for-ai-inference-deployments"


def campus(
    campus_id: str,
    name: str,
    market: str,
    state: str,
    lifecycle: str,
    location_url: str | None,
    **extra: object,
) -> dict:
    return {
        "campus_id": campus_id,
        "campus_name": name,
        "market": market,
        "state": state,
        "country_code": "US",
        "lifecycle_as_of_2026_07_19": lifecycle,
        "location_url": location_url,
        **extra,
    }


CAMPUS_RECORDS = [
    campus(
        "seattle",
        "SDC Seattle",
        "Seattle / Tukwila",
        "WA",
        "operating",
        "https://sabeydatacenters.com/locations/seattle-data-center",
        address="3355 35th Ave S, Tukwila, WA 98168",
        scale={"current_page_area_sqft_more_than": 1000000, "current_cutsheet_area_sqft": 1200000, "headline_capacity_mw": 54},
        equipment={"aggregate_utility_MVA_more_than": 90, "utility_feeds": "redundant feeds; third feed available", "critical_power_per_suite_kW_up_to": 1500, "electrical_backup": "N+1", "generator_unit_rating_mw": 2.5, "generator_peak_runtime_hours": 72, "fuel": "on-site with emergency supply contracts", "cooling": ["evaporative", "economizer", "hot_and_cold_aisle", "mobile_commissioning_units"], "free_cooling_percent_of_year_approximately": 90, "installed_HVAC_tons": 9500},
        environment={"current_page_average_annualized_PUE_approximately": 1.5, "older_cutsheet_PUE": 1.25, "carbon_free_power_claim_percent": 100, "boundary": "Page and cutsheet PUE values use different publication snapshots and are not silently reconciled."},
    ),
    campus(
        "columbia",
        "SDC Columbia",
        "East Wenatchee",
        "WA",
        "operating_with_building_under_construction",
        "https://sabeydatacenters.com/locations/east-wenatchee-data-center",
        address="4405 Grant Rd, East Wenatchee, WA 98802",
        scale={"current_buildings": 3, "fourth_building": "under_construction", "utility_or_campus_capacity_mw": 70},
        equipment={"substation": "on-site", "electrical_backup": "N+1", "generator_unit_rating_mw": 2.75, "generator_peak_runtime_hours": 72, "fuel": "on-site", "cooling": ["evaporative", "economizer", "hot_and_cold_aisle", "mobile_commissioning_units"], "water_reclamation": "cooling wastewater reused for landscaping"},
        environment={"average_annualized_PUE": 1.2, "published_power_price_usd_per_kWh": 0.05, "ENERGY_STAR_score_2024": 99},
        availability_boundary="Dated leasing releases used 4.5-5.5 MW near-term and an 18-MW later expansion with changing schedules; none is relabeled as operating or utilized load.",
    ),
    campus(
        "quincy",
        "SDC Quincy",
        "Quincy",
        "WA",
        "operating",
        "https://sabeydatacenters.com/locations/quincy-data-center",
        address="2200 M St NE, Quincy, WA",
        scale={"area_sqft": 530000, "purpose_built_buildings": 5, "headline_capacity_mw": 123, "aggregate_power_delivered_mw_range": [50, 60]},
        equipment={"substation": "on-site", "electrical_backup": "N+1", "generator_unit_rating_mw": 2, "generator_peak_runtime_hours": 72, "cooling": ["evaporative", "economizer", "rooftop_air_handling_units", "Building_B_chilled_water_and_CRAH", "hot_and_cold_aisle"]},
        environment={"average_annualized_PUE": 1.2, "published_power_price_usd_per_kWh": 0.038},
        capacity_boundary="The 123-MW page headline and 50-60 MW aggregate delivered statement use different capacity scopes; neither is actual customer load.",
    ),
    campus(
        "manhattan",
        "SDC Manhattan",
        "New York / Manhattan",
        "NY",
        "operating",
        "https://sabeydatacenters.com/locations/new-york-data-center",
        address="375 Pearl Street, New York, NY",
        scale={"utility_power_across_two_powered_shell_spaces_mw": 7, "dated_turnkey_capacity_kW": 912},
        equipment={"retail_rack_power_kW_up_to": 20, "standard": "Tier_III", "cooling": "liquid-cooling-capable hybrid"},
        AI_context={"marketing_use_case": "GPU inference", "installed_GPU_models_counts_owner_and_utilization": "undisclosed", "source_url": MANHATTAN_AI_URL},
        availability_boundary="The 755-kW, nearly-one-MW and 912-kW disclosures are point-in-time availability statements, not a stable operating-load series.",
    ),
    campus(
        "austin",
        "SDC Austin",
        "Austin / Round Rock",
        "TX",
        "operating_with_building_under_construction",
        "https://sabeydatacenters.com/locations/austin-data-center",
        address="1300 Louis Henna Blvd, Round Rock, TX 78664",
        scale={"buildings": 2, "area_sqft": 603300, "campus_critical_IT_or_design_capacity_mw": 84, "cabinet_power_kW_up_to": 200, "Building_B_total_design_mw": 54, "Building_B_halls": 6, "Building_B_hall_area_sqft": 30000},
        equipment={"aggregate_power_mw": 84, "critical_power_per_module_mw_up_to": 6, "substation": "on-site", "electrical": "N+1 distributed redundant", "generator_unit_rating_Buildings_A_and_B_mw": 2.25, "generator_peak_runtime_hours": 48, "standard": "Tier_3_equivalent", "cooling": ["evaporative", "economizer", "rooftop_air_handling_units", "chilled_water_and_CRAH", "liquid_optimized"]},
        building_status={"Building_A": "operating_and_reported_fully_leased_Q1_2026", "Building_B": "under_construction; first 18 MW scheduled in two 9-MW stages across Q4 2027 and Q1 2028 in a later availability snapshot"},
        AI_context={"named_customer_system": "TACC Horizon", "customer_owned_or_funded_operational_NVIDIA_Blackwell_GPUs": 4000, "customer_nodes": 2000, "node_configuration": "one 72-core Grace CPU and two Blackwell GPUs", "customer_Grace_GB200_CPUs": 2000, "fabric": "800_GBps_InfiniBand", "storage_PB": 400, "host_facility_initial_power_mw": 15, "host_facility_expandable_power_mw": 20, "rack_power_kW_up_to": 250, "cooling": "underfloor liquid-cooling hookups", "ownership_boundary": "TACC/NSF customer hardware hosted at Sabey; not Sabey-owned GPU inventory", "sources": [HORIZON_NEWS_URL, HORIZON_SYSTEM_URL, HORIZON_CONSTRUCTION_URL]},
        liquid_cooling_boundary="A reported 86% of current Austin Building A deployments using liquid cooling is a deployment-share statement, not fleet liquid-cooled MW.",
    ),
    campus(
        "ashburn",
        "SDC Ashburn",
        "Ashburn",
        "VA",
        "operating_with_building_under_construction",
        "https://sabeydatacenters.com/locations/ashburn-data-center",
        address="21741 Red Rum Dr, Ashburn, VA 20147",
        scale={"campus_acres": 38, "planned_buildings": 3, "current_buildings": 2, "current_buildings_capacity_mw_more_than": 36, "full_build_capacity_mw": 85, "full_build_area_sqft": 645000, "rack_power_kW_more_than": 100},
        equipment={"aggregate_power_delivered_mw_more_than": 70, "critical_power_per_module_mw_up_to": 2.85, "substation": "on-site", "electrical": "N+1", "Building_B_generator_unit_mw": 2.25, "Building_B_peak_runtime_hours": 48, "Building_C_generator_unit_mw": 2, "Building_C_peak_runtime_hours": 72, "cooling": ["evaporative", "economizer", "liquid_enabled", "rooftop_air_handling_units", "Building_B_chilled_water_and_CRAH"]},
        environment={"current_buildings_PUE": 1.35},
        expansion={"final_Building_A_total_mw": 54, "first_phase_mw": 18, "future_mw": 36, "expected_initial_delivery": 2026, "stories": 3, "cooling_modes": ["air", "liquid", "hybrid"], "source_url": ASHBURN_EXPANSION_URL},
        availability_boundary="A dated 14-MW prelease tranche is not the same measure as the 54-MW building design or campus full-build capacity.",
    ),
    campus(
        "umatilla",
        "SDC Umatilla",
        "Umatilla",
        "OR",
        "development_not_energized_at_2026_03_31",
        "https://sabeydatacenters.com/locations/sdc-umatilla",
        address="precise_public_street_address_undisclosed",
        scale={"site_acres": 60, "planned_buildings": 2, "planned_area_sqft": 714540, "headline_design_capacity_mw_more_than": 150, "aggregate_power_coming_mw_more_than": 120},
        equipment={"substation": "to_be_built_on_site", "electrical": "redundant_systems", "power_sources": ["hydroelectric", "McNary", "other_renewables"], "cooling": ["liquid_cooling_options", "high_density_ready"], "rack_density_design_kW_more_than": 1000},
        environment={"estimated_PUE_approximately": 1.3, "separately_projected_PUE": 1.25},
        schedule={"ground_work": 2024, "core_and_shell": 2026, "first_hall": "2027", "later_halls_and_Building_2": "2028_to_2029_plus"},
        schedule_boundary="Official snapshots alternately describe 9-MW and 12-MW first delivery tranches; development configuration and dates may have changed and are not operating capacity.",
        source_urls=[UMATILLA_ANNOUNCEMENT_URL, UMATILLA_CUTSHEET_URL],
    ),
    campus(
        "north_texas",
        "SDC North Texas",
        "North Texas exact market undisclosed",
        "TX",
        "development_pipeline",
        None,
        address="undisclosed",
        scale={"current_cutsheet_roster_construction_or_planned_mw": 200},
        disclosure_boundary="Named as under development in Sabey's 2024 sustainability report and shown on a current cutsheet roster, but absent from the reviewed current location sitemap; city, address, buildings, equipment, power lifecycle and delivery milestones remain undisclosed.",
        source_urls=[SUSTAINABILITY_URL, UMATILLA_CUTSHEET_URL],
    ),
]


OSM_TO_CAMPUS = {
    "osm_way_205724885": "seattle",
    "osm_way_293211686": "seattle",
    "osm_way_293211683": "seattle",
    "osm_way_337126742": "seattle",
    "osm_way_337126741": "seattle",
    "osm_way_337126739": "seattle",
    "osm_way_460167187": "columbia",
    "osm_way_460167186": "columbia",
    "osm_way_1071774674": "columbia",
    "osm_way_283051472": "quincy",
    "osm_way_793888427": "ashburn",
}


PORTFOLIO_CONTEXT = {
    "energized_campuses_as_of_2026_03_31": 6,
    "operating_capacity_mw_as_of_2026_03_31_approximately": 251,
    "built_powered_shell_included_in_operating_capacity_mw": 76,
    "output_growth_opportunity_by_2036_on_existing_land": "up_to_three_times",
    "2024_owned_or_operated_campuses": 6,
    "2024_buildings": 21,
    "2024_developments_named": ["SDC_Umatilla", "SDC_North_Texas"],
    "current_homepage": "six campuses across the country and three more in development",
    "roster_boundary": "Seven current location-sitemap pages plus a separately sourced North Texas pipeline record do not resolve the homepage's third-development wording or form a complete physical-building roster.",
    "AI_and_accelerators": {
        "Sabey_owned_GPU_inventory_by_model_site_and_utilization": "undisclosed",
        "publicly_confirmed_named_customer_GPUs_at_Austin": 4000,
        "customer_system": "TACC_Horizon_NVIDIA_Blackwell",
        "ownership_boundary": "The confirmed 4,000 GPUs are TACC/NSF customer hardware, not Sabey assets and not a fleet total.",
    },
    "liquid_cooling": {
        "JetCool": "direct-to-chip portfolio partnership; 2023 comparison reported 13.5% server-power savings versus air",
        "OptiCool": "future two-phase refrigerant customer deployments",
        "live_liquid_cooled_fleet_mw": "undisclosed",
        "boundary": "Partnerships, customer deployment shares and design capability do not establish commissioned fleet MW or equipment share.",
    },
    "environment": {
        "Scope_1_and_2_reduction_2024_from_2018_percent": 25.2,
        "net_zero_Scope_1_and_2_target_year": 2029,
        "SBT_reduction_target_2030_from_2018_percent": 50,
        "renewable_procurement_strategy_portfolio_percent": 100,
        "renewable_instrument_boundary": "current primary strategy includes RECs while PPAs and on-site options are explored; not proof of hourly carbon-free matching",
        "ENERGY_STAR_buildings_above_90": 9,
        "ENERGY_STAR_buildings_scoring_99": 5,
        "Scope_3_share_of_2024_net_emissions_percent_approximately": 96,
        "fleet_PUE_WUE_absolute_water_energy_and_emissions": "not_completely_disclosed",
    },
    "nuclear": {
        "status": "TerraPower_exploratory_MOU_not_contract_or_operating_generation",
        "Natrium_reactor_mw": 345,
        "storage_boost_mw_up_to": 500,
        "first_project_expected": 2030,
    },
    "ownership_and_finance": {
        "platform": "Sabey Data Center Properties LLC",
        "joint_owners_and_governance": ["Sabey", "National_Real_Estate_Advisors"],
        "minority_investor_from_2026_07_08": "Ares_Secondaries_funds",
        "Ares_investment_amount_stake_percent_valuation_and_transaction_economics": "undisclosed",
        "current_revenue_operating_income_EBITDA_capex_debt_cash_flow_customer_concentration_and_site_economics": "undisclosed",
        "customer_characterization": "predominantly_investment_grade_enterprise_and_hyperscale_mix",
    },
}


COMMON_SOURCES = [
    HOME_URL, SITEMAP_URL, ARES_URL, SUSTAINABILITY_URL,
    SUSTAINABILITY_RELEASE_URL, HORIZON_NEWS_URL, HORIZON_SYSTEM_URL,
    HORIZON_CONSTRUCTION_URL, JETCOOL_URL, OPTICOOL_URL, TERRAPOWER_URL,
]


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
        if "sabey" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(CAMPUS_RECORDS) == 8
    assert len({row["campus_id"] for row in CAMPUS_RECORDS}) == 8
    assert len(candidates) == 11, [row["id"] for row in candidates]
    assert set(OSM_TO_CAMPUS) == {row["id"] for row in candidates}

    mapped: dict[str, list[dict]] = {}
    for object_id, campus_id in OSM_TO_CAMPUS.items():
        source = osm[object_id]
        mapped.setdefault(campus_id, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": "OSM geometry is map evidence, not provider-certified ownership, lifecycle, capacity, tenancy or financial data; the Quincy polygon is a campus boundary rather than a building footprint.",
        })

    records = []
    for position, source in enumerate(CAMPUS_RECORDS, start=1):
        extra_sources = source.get("source_urls", [])
        records.append({
            "id": f"sabey_{source['campus_id']}",
            "object_type": "ProviderPublishedDataCenterCampusOrPipelineLabel",
            "source_order": position,
            "operator": "Sabey Data Centers / Sabey Data Center Properties",
            "record_granularity": "campus_or_pipeline_label_not_necessarily_one_physical_building",
            **source,
            "osm_map_evidence": sorted(mapped.get(source["campus_id"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source.get("location_url"), *extra_sources, *COMMON_SOURCES])) if source.get("location_url") else list(dict.fromkeys([*extra_sources, *COMMON_SOURCES])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    assert sum(len(row["osm_map_evidence"]) for row in records) == 11
    return {
        "registry": "Sabey current official location sitemap plus North Texas pipeline and OSM crosswalk",
        "current_location_sitemap_pages": 7,
        "separately_sourced_pipeline_labels": 1,
        "registry_records": len(records),
        "lifecycle_counts": dict(sorted(Counter(row["lifecycle_as_of_2026_07_19"] for row in records).items())),
        "state_counts": dict(sorted(Counter(row["state"] for row in records).items())),
        "related_OSM_objects": len(candidates),
        "mapped_OSM_objects": sum(len(row["osm_map_evidence"]) for row in records),
        "campus_labels_with_OSM_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "unmatched_related_OSM_objects": [],
        "portfolio_context": PORTFOLIO_CONTEXT,
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum campus headline capacity, delivered power, full-build design, powered shell, availability tranches, operating capacity, customer hardware or OSM geometry into one live-load, GPU, building or revenue total.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/sabey_official_facility_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/sabey_official_facility_summary.json"))
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
