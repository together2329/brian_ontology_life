#!/usr/bin/env python3
"""Build a scope-safe Prime Data Centers facility and evidence registry.

Prime's current directory exposes nine location pages and twenty-eight facility
cards, but its home page, sustainability report and investor material publish
different campus, location and data-center counts.  This builder retains those
denominators, lifecycle states and publication dates rather than treating the
1.09-GW campus headline or 4-GW-plus roadmap as live IT load.  Customer-owned
Lambda GPUs, design cooling capabilities and private-company investor metrics
also remain separate from Prime-owned physical inventory and standalone
financial performance.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://primedatacenters.com/"
DIRECTORY = "https://primedatacenters.com/locations/"
ABOUT = "https://primedatacenters.com/about/"
AI = "https://primedatacenters.com/ai/"
SUSTAINABILITY = "https://primedatacenters.com/sustainability/"
SUSTAINABILITY_REPORT = "https://primedatacenters.com/wp-content/uploads/2025/08/Prime-Data-Centers_2025-Sustainability-Report_FINAL-optimised.pdf"
MACQUARIE_CURRENT = "https://www.macquarie.com/ie/en/insights/supporting-and-investing-in-large-scale-data-storage-in-the-americas.html"
MACQUARIE_2021 = "https://primedatacenters.com/news/prime-data-centers-announces-strategic-partnership-and-equity-investment-with-macquarie-capital/"
SNOWHAWK_NUVEEN = "https://primedatacenters.com/news/snowhawk-and-nuveen-make-strategic-investment-in-prime-data-centers/"
SIEMENS_AR2025 = "https://assets.new.siemens.com/siemens/assets/api/uuid:428ea18a-e7ab-4f93-a160-33908f1c3540/Siemens-Annual-Report-2025.pdf"
ENERGY_STAR = "https://primedatacenters.com/news/prime-data-centers-dallas-and-sacramento-facilities-earn-energy-star-certification-for-superior-energy-performance/"
LAX_OPEN = "https://primedatacenters.com/news/prime-opens-los-angeles-data-center/"
LAX_LAMBDA = "https://primedatacenters.com/news/prime-data-centers-and-lambda-partner-to-power-the-next-era-of-superintelligence-with-ai-optimized-infrastructure-in-southern-california/"
PHOENIX_CURRENT = "https://primedatacenters.com/news/prime-data-centers-breaks-ground-on-three-buildings-at-its-240mw-phoenix-campus-advancing-3billion-dollar-investment-in-avondale/"
PHOENIX_HISTORICAL = "https://primedatacenters.com/news/prime-announces-its-first-phoenix-data-center-campus/"
SACRAMENTO_CURRENT = "https://primedatacenters.com/news/prime-data-centers-breaks-ground-on-second-sacramento-data-center-expanding-regional-campus-footprint/"
SJC03_HISTORICAL = "https://primedatacenters.com/news/prime-launches-construction-at-second-silicon-valley-location/"
SAEBY = "https://primedatacenters.com/news/prime-enters-denmark-with-124-megawatt-data-center-campus-that-delivers-a-net-positive-environmental-impact/"
ESBJERG = "https://primedatacenters.com/news/prime-data-centers-announces-plans-for-major-data-center-development-in-esbjerg-denmark/"


LOCATION_PAGES = {
    "AUS01": "https://primedatacenters.com/locations/austin/",
    "ORD01": "https://primedatacenters.com/locations/chicago/",
    "DFW01": "https://primedatacenters.com/locations/dallas/",
    "LAX01": "https://primedatacenters.com/locations/los-angeles/",
    "PHX01": "https://primedatacenters.com/locations/phoenix/",
    "SMF01": "https://primedatacenters.com/locations/sacramento/",
    "SJC": "https://primedatacenters.com/locations/silicon-valley/",
    "FRA01": "https://primedatacenters.com/locations/frankfurt/",
    "MAD01": "https://primedatacenters.com/locations/madrid/",
}


CAMPUS = {
    "AUS01": {"market": "Austin", "locality": "Lockhart", "region": "Texas", "country_code": "US", "facility_cards": 8, "critical_it_mw": 384, "acres": 205, "size": 2_000_000, "size_unit": "sq_ft", "data_halls": None, "utility": "Blue_Bonnet_Electric_Cooperative", "substation": "on_site", "connectivity": "10_carriers_in_proximity", "compliance": "SOC2_Type_II_and_ISO_27001_projected", "performance": "AI_ready"},
    "ORD01": {"market": "Chicago", "locality": "Elk_Grove_Village", "region": "Illinois", "country_code": "US", "facility_cards": 3, "critical_it_mw": 270, "acres": 29.75, "size": 958_000, "size_unit": "sq_ft", "data_halls": 18, "utility": "ComEd", "substation": "adjacent_to_campus", "connectivity": "17_carriers_in_proximity", "compliance": "SOC2_Type_II_and_ISO_27001_projected", "performance": "AI_ready", "publication_conflict": "Current page headline says 985K square feet while the overview says 958,000 square feet."},
    "DFW01": {"market": "Dallas", "locality": "Dallas", "region": "Texas", "country_code": "US", "facility_cards": 2, "critical_it_mw": 20, "acres": 8.44, "size": 213_000, "size_unit": "sq_ft", "data_halls": 7, "utility": "Oncor", "substation": "in_close_proximity", "connectivity": "multiple_carriers_in_proximity", "compliance": "SOC2_Type_II_and_ISO_27001_projected", "performance": "AI_ready"},
    "LAX01": {"market": "Los_Angeles", "locality": "Vernon", "region": "California", "country_code": "US", "facility_cards": 1, "critical_it_mw": 33, "acres": 1.95, "size": 242_495, "size_unit": "sq_ft", "data_halls": 6, "utility": "Vernon_Power_Utility", "substation": "on_site", "connectivity": "multiple_carriers_in_proximity", "compliance": "SOC2_Type_II_and_ISO_27001_projected", "performance": "AI_ready"},
    "PHX01": {"market": "Phoenix", "locality": "Avondale", "region": "Arizona", "country_code": "US", "facility_cards": 5, "critical_it_mw": 240, "acres": 66.5, "size": 1_300_000, "size_unit": "sq_ft", "data_halls": 20, "utility": "Salt_River_Project", "substation": "on_site", "connectivity": "multiple_carriers_in_proximity", "compliance": "SOC2_Type_II_and_ISO_27001_projected", "performance": "AI_ready"},
    "SMF01": {"market": "Sacramento", "locality": "McClellan_Park", "region": "California", "country_code": "US", "facility_cards": 2, "critical_it_mw": 26, "acres": 8.64, "size": 215_000, "size_unit": "sq_ft", "data_halls": 6, "utility": "SMUD", "substation": "on_site", "connectivity": "10_carriers_in_proximity", "compliance": "SOC2_Type_II_ISO_27001_and_PCI_DSS", "performance": None},
    "SJC": {"market": "Silicon_Valley", "locality": "Hayward_Santa_Clara_and_San_Jose", "region": "California", "country_code": "US", "facility_cards": 5, "critical_it_mw": 57, "acres": 13, "size": 540_000, "size_unit": "sq_ft", "data_halls": 17, "utility": "Silicon_Valley_Power_and_PG&E", "substation": "in_close_proximity", "connectivity": "25_carriers_in_proximity", "compliance": "SOC2_Type_II_ISO_27001_and_PCI_DSS", "performance": None},
    "FRA01": {"market": "Frankfurt", "locality": "Main_Taunus_Kreis", "region": "Hesse", "country_code": "DE", "facility_cards": 1, "critical_it_mw": 20, "acres": 2.8, "size": 15_000, "size_unit": "sqm", "data_halls": 2, "utility": "undisclosed", "substation": "in_close_proximity", "connectivity": "6_carriers_in_proximity", "compliance": "ISO_9001_and_ISO_27001_projected", "performance": "AI_ready"},
    "MAD01": {"market": "Madrid", "locality": "Alcobendas", "region": "Community_of_Madrid", "country_code": "ES", "facility_cards": 1, "critical_it_mw": 40, "acres": 8, "size": 25_810, "size_unit": "sqm", "data_halls": 4, "utility": "Iberdrola", "substation": "on_site", "connectivity": "10_carriers_on_campus", "compliance": "ISO_9001_and_ISO_27001_projected", "performance": "AI_ready"},
}


def facility(code: str, campus: str, address: str, kind: str, use: str, status: str, availability: str, capacity_mw: int | None, size: int, size_unit: str = "sq_ft", *, sources: list[str] | None = None, conflicts: list[str] | None = None) -> dict:
    context = CAMPUS[campus]
    return {
        "id": f"prime_{code.lower().replace('-', '_')}",
        "object_type": "DataCenterFacilityEvidence",
        "name": code,
        "campus_code": campus,
        "market": context["market"],
        "locality": context["locality"],
        "region": context["region"],
        "country_code": context["country_code"],
        "address_as_published": address,
        "lifecycle_as_of_2026_07_19": status.lower().replace(" ", "_"),
        "commercial_availability_as_published": availability.lower(),
        "facility_type": kind,
        "use": use,
        "published_card_metrics": {"critical_it_capacity_mw": capacity_mw if capacity_mw is not None else "undisclosed_on_current_card", "size": size, "size_unit": size_unit},
        "campus_context": {"campus_critical_it_mw": context["critical_it_mw"], "facility_cards": context["facility_cards"], "utility": context["utility"], "substation": context["substation"]},
        "power_and_cooling_evidence": {"M_and_E": "concurrently_maintainable", "cooling": "closed_loop_air_and_liquid", "exact_redundancy_configuration": "not_published_on_current_card", "as_built_equipment_OEM_model_count_rating_acceptance_and_remaining_life": "undisclosed"},
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": conflicts or [],
        "boundary": "Status and availability are separate provider fields. Card or campus critical IT capacity is design or marketed scope and is not proof of energized, customer-accepted, leased, utilized, billed or actual IT load. AI-ready and liquid-cooling capability do not establish Prime-owned GPUs.",
        "source_urls": list(dict.fromkeys([LOCATION_PAGES[campus], *(sources or [])])),
    }


CURRENT_CARDS = [
    *[facility(f"AUS01-{i:02d}", "AUS01", "3300 FM 2720", "hyperscale_with_liquid_cooling", "single_or_multi_tenant", "Development", "Available", 144 if i == 1 else None, 250_000) for i in range(1, 9)],
    facility("ORD01-01", "ORD01", "1650 E Higgins", "hyperscale_with_liquid_cooling", "single_or_multi_tenant", "Operational", "Leased", 72, 384_000),
    facility("ORD01-02", "ORD01", "1600 E Higgins", "hyperscale_with_liquid_cooling_options", "single_or_multi_tenant", "Development", "Leased", 54, 279_000),
    facility("ORD01-03", "ORD01", "1550 E Higgins", "hyperscale_with_liquid_cooling_options", "single_or_multi_tenant", "Development", "Leased", 54, 294_000),
    facility("DFW01-01", "DFW01", "1515 Round Table", "enterprise", "multi_tenant", "Operational", "Leased", 8, 107_000, sources=[ENERGY_STAR]),
    facility("DFW01-02", "DFW01", "1455 Round Table", "enterprise", "multi_tenant", "Construction", "Leased", 12, 96_000),
    facility("LAX01-01", "LAX01", "4701 S Santa Fe", "hyperscale", "multi_tenant", "Operational", "Leased", 33, 242_000, sources=[LAX_OPEN, LAX_LAMBDA]),
    facility("PHX01-01", "PHX01", "3700 S Avondale Blvd", "hyperscale", "single_or_multi_tenant", "Construction", "Leased", 48, 267_000, sources=[PHOENIX_CURRENT, PHOENIX_HISTORICAL]),
    facility("PHX01-02", "PHX01", "3704 S Avondale Blvd", "hyperscale", "single_or_multi_tenant", "Construction", "Leased", 48, 267_000, sources=[PHOENIX_CURRENT, PHOENIX_HISTORICAL]),
    facility("PHX01-03", "PHX01", "3708 S Avondale Blvd", "hyperscale", "single_or_multi_tenant", "Construction", "Leased", 48, 267_000, sources=[PHOENIX_CURRENT, PHOENIX_HISTORICAL]),
    facility("PHX01-04", "PHX01", "3712 S Avondale Blvd", "hyperscale", "single_or_multi_tenant", "Construction", "Available", 48, 267_000, sources=[PHOENIX_CURRENT, PHOENIX_HISTORICAL], conflicts=["The 2026-05-21 groundbreaking release describes the first three buildings as the initial phase; the later/current page classifies PHX01-04 as Construction."]),
    facility("PHX01-05", "PHX01", "3716 S Avondale Blvd", "hyperscale", "single_or_multi_tenant", "Development", "Available", 48, 267_000, sources=[PHOENIX_CURRENT, PHOENIX_HISTORICAL]),
    facility("SMF01-01", "SMF01", "2407 AK Street", "enterprise", "single_tenant", "Operational", "Leased", 8, 65_000, sources=[ENERGY_STAR]),
    facility("SMF01-02", "SMF01", "2408 AK Street", "enterprise", "multi_tenant", "Construction", "Available", 18, 150_000, sources=[SACRAMENTO_CURRENT], conflicts=["The current page calls the second building SMF01-02; the 2026 groundbreaking release calls it SMF02."]),
    facility("SJC01", "SJC", "26415 Corporate Ave", "enterprise", "single_tenant", "Operational", "Leased", 20, 146_000),
    facility("SJC02", "SJC", "1111 Comstock St", "enterprise", "single_tenant", "Powered shell", "Leased", 9, 123_000),
    facility("SJC03", "SJC", "2215 Martin", "enterprise", "single_or_multi_tenant", "Development", "Leased", 9, 79_000, sources=[SJC03_HISTORICAL], conflicts=["The current card says 2215 Martin; the 2022 construction release said 2175 Martin and expected construction completion in H2 2023, while the current page still says Development."]),
    facility("SJC04", "SJC", "1231 Comstock", "enterprise", "single_or_multi_tenant", "Development", "Available", 9, 112_000),
    facility("SJC06", "SJC", "6580 Via del Oro", "enterprise", "single_or_multi_tenant", "Operational", "Available", 10, 80_000),
    facility("FRA01-01", "FRA01", "Main-Taunus-Kreis", "hyperscale", "single_or_multi_tenant", "Development", "Available", 20, 15_000, "sqm"),
    facility("MAD01-01", "MAD01", "C. de la Pedriza", "hyperscale", "single_or_multi_tenant", "Development", "Available", 40, 25_810, "sqm"),
]


PIPELINE_RECORDS = [
    {
        "id": "prime_aal01_saeby_campus_plan",
        "object_type": "DataCenterCampusPlanEvidence",
        "name": "AAL01_Saeby",
        "locality": "Saeby",
        "country_code": "DK",
        "address_as_published": "Energivej",
        "lifecycle_as_of_2026_07_19": "historical_announced_plan_current_status_unconfirmed",
        "published_plan_metrics": {"campus_critical_it_mw": 124, "hyperscale_data_centers": 3, "in_rack_cooling_kw_per_cabinet_up_to": 50},
        "power_and_cooling_evidence": {"renewable_target": "100_percent", "backup_generation": "biofuel_powered_plan", "district_heat_partner": "Saeby_Varmevaerk", "in_rack_cooling_partner": "New_Nordic_Data_Cooling_ApS", "DGNB_Gold": "design_target"},
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "boundary": "The 2023 release announced a three-data-center campus, but the former location page is absent from the current nine-page directory. The reviewed evidence does not establish construction, energization, operation, cancellation or current Prime ownership.",
        "source_urls": [SAEBY],
    },
    {
        "id": "prime_esb01_esbjerg_campus_plan",
        "object_type": "DataCenterCampusPlanEvidence",
        "name": "ESB01_Esbjerg",
        "locality": "Esbjerg",
        "country_code": "DK",
        "address_as_published": "Nordre Tovrupvej",
        "lifecycle_as_of_2026_07_19": "EIA_and_preconstruction_plan",
        "published_plan_metrics": {"site_sqm": 640_000, "first_phase_IT_mw": 160, "full_assessed_IT_mw": 550, "first_phase_investment_eur_billion_approximate": 2, "full_build_investment_eur_billion_expected": 6, "construction_start_anticipated": 2027, "initial_go_live_target": "late_2029"},
        "power_and_cooling_evidence": {"electricity_source": "Danish_national_grid", "renewable_share": "high_share_provider_wording", "waste_heat_recovery": "exploration_not_committed_as_built"},
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "boundary": "Both phases are subject to successful EIA, permits, grid connection, demand and construction. Investment estimates are project plans, not Prime revenue, incurred capex, committed financing or operating value.",
        "source_urls": [ESBJERG],
    },
]


OSM_CROSSWALK = {
    "osm_way_1461896928": ("prime_dfw01_01", "exact_facility_building_component"),
    "osm_way_465032380": ("prime_dfw01_01", "second_building_footprint_component_same_facility_and_address"),
    "osm_way_209073636": ("prime_sjc02", "exact_current_facility"),
    "osm_node_12437277166": ("prime_sjc03", "exact_current_address_point"),
    "osm_way_209073659": ("prime_sjc04", "exact_current_facility"),
    "osm_way_618756435": ("prime_aal01_saeby_campus_plan", "historical_announced_plan_footprint_current_lifecycle_unconfirmed"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = []
    for order, source in enumerate([*CURRENT_CARDS, *PIPELINE_RECORDS], 1):
        rows.append({"source_order": order, "accessed_on": accessed_on, **source})
    assert len(rows) == 30
    assert len({row["id"] for row in rows}) == 30
    cards = [row for row in rows if row["object_type"] == "DataCenterFacilityEvidence"]
    assert len(cards) == 28
    assert Counter(row["lifecycle_as_of_2026_07_19"] for row in cards) == {"development": 15, "construction": 6, "operational": 6, "powered_shell": 1}
    numeric = [row["published_card_metrics"]["critical_it_capacity_mw"] for row in cards if isinstance(row["published_card_metrics"]["critical_it_capacity_mw"], int)]
    assert sum(numeric) == 760
    assert sum(row["critical_it_mw"] for row in CAMPUS.values()) == 1090
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "facility_ref": facility_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "capacity_counting_rule": "OSM geometry is a crosswalk only; duplicate footprints do not create additional facility capacity.",
        })
    assert len(rows) == 6
    assert {row["raw_operator"] for row in rows} == {"Prime", "Prime Data Centers"}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    cards = [row for row in records if row["object_type"] == "DataCenterFacilityEvidence"]
    sources = list(dict.fromkeys([
        HOME, DIRECTORY, *LOCATION_PAGES.values(), ABOUT, AI, SUSTAINABILITY,
        SUSTAINABILITY_REPORT, ENERGY_STAR, LAX_OPEN, LAX_LAMBDA,
        PHOENIX_CURRENT, PHOENIX_HISTORICAL, SACRAMENTO_CURRENT,
        SJC03_HISTORICAL, SAEBY, ESBJERG, SNOWHAWK_NUVEEN, MACQUARIE_2021,
        MACQUARIE_CURRENT, SIEMENS_AR2025,
    ]))
    numeric_by_status = Counter()
    for row in cards:
        value = row["published_card_metrics"]["critical_it_capacity_mw"]
        if isinstance(value, int):
            numeric_by_status[row["lifecycle_as_of_2026_07_19"]] += value
    return {
        "id": "prime_data_centers_official_facility_summary_2026_07_19",
        "operator": "Prime Data Centers",
        "legal_entity": "Prime Data Centers LLC",
        "accessed_on": accessed_on,
        "current_directory_scope": {
            "visible_location_pages": 9,
            "visible_facility_cards": 28,
            "facility_card_lifecycle_counts": dict(sorted(Counter(row["lifecycle_as_of_2026_07_19"] for row in cards).items())),
            "campus_headline_critical_IT_mw_checksum": 1090,
            "facility_card_numeric_critical_IT_mw_checksum": 760,
            "facility_card_numeric_mw_by_lifecycle": dict(sorted(numeric_by_status.items())),
            "campus_minus_numeric_card_mw": 330,
            "unallocated_difference": {"AUS01": 240, "ORD01": 90},
            "operational_card_numeric_mw_checksum": 151,
            "boundary": "The 1.09-GW sum spans current page campus headlines across operating, powered-shell, construction and development states. Only 760 MW is allocated to numeric facility cards, and even the 151-MW operational-card checksum is design or marketed critical IT rather than measured live, utilized or billed load.",
        },
        "publication_scope_reconciliation": {
            "current_home_page": {"campuses": 13, "pipeline_GW_more_than": 4},
            "current_directory": {"location_pages": 9, "facility_cards": 28},
            "Macquarie_as_of_2025_11_03": {"global_campuses": 14, "data_centers": 29, "extension_pipeline_GW_more_than": 4},
            "2025_sustainability_report_2024_basis": {"locations": 22, "roadmap_GW_more_than": 3},
            "current_named_roadmap_markets_from_2025_investment_release": ["Chicago", "Phoenix", "Austin", "Los_Angeles", "Silicon_Valley", "Frankfurt", "Berlin", "Helsinki", "Madrid"],
            "separately_reviewed_Denmark_plans": ["AAL01_Saeby_2023", "ESB01_Esbjerg_2026"],
            "boundary": "Campus, location, data-center, facility-card, market and roadmap counts come from different dates and granularity. The public sources do not provide a current legal-building bridge that reconciles them.",
        },
        "selected_power_and_cooling_evidence": {
            "current_location_pages": {"M_and_E": "concurrently_maintainable", "cooling": "closed_loop_air_and_liquid", "utility_and_substation": {key: {"utility": value["utility"], "substation": value["substation"]} for key, value in CAMPUS.items()}},
            "2025_standard_design": {"high_efficiency_magnetic_bearing_chillers": True, "automated_variable_speed_cooling": True, "CFD_and_hydraulic_analysis": True, "integrated_BMS_and_EPMS": True, "automated_free_cooling_controls": True},
            "LAX01": {"generator_buildings": True, "standard_air_cooling_kw_per_rack_up_to": 40, "combined_liquid_cooling_kw_per_rack_up_to": 120, "HVO_exclusive_in_new_backup_generators_from_2024": True},
            "DFW01": {"HVO_exclusive_in_new_backup_generators_from_2024": True},
            "PHX01": {"substation_phase_1_mw": 250, "phase_1_commissioned_as_of_2026_05_21": True, "closed_loop_zero_process_water_during_operations_provider_claim": True},
            "AAL01_plan": {"biofuel_backup_generators": True, "district_heat": True, "partner": "New_Nordic_Data_Cooling_ApS", "in_rack_kw_per_cabinet_up_to": 50},
            "AI_capability_page": {"rack_density_kw_more_than": 100, "cooling_options": ["air", "direct_to_chip_liquid", "immersion", "hybrid"], "named_supported_hardware": ["NVIDIA_H100", "NVIDIA_A100", "NVIDIA_HGX_B200"], "network_fabrics": ["NVLink", "InfiniBand", "Ethernet"]},
            "as_built_per_site_transformer_switchgear_PDU_UPS_battery_generator_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_acceptance_and_remaining_life": "undisclosed",
            "boundary": "Portfolio design features and capability marketing are not a per-site as-built bill of materials. Named AI hardware is supported-customer equipment, not Prime inventory.",
        },
        "sustainability_and_measured_performance_boundary": {
            "reporting_period": "calendar_2024_with_qualitative_discussion_through_2025_H1",
            "design_PUE": 1.20,
            "design_WUE_site_l_per_kWh": 0.002,
            "design_WUE_source": 4.054,
            "market_based_CUE_kg_CO2e_per_IT_kWh": 0.109,
            "operating_data_center_water_consumption_cubic_meters": 2400,
            "water_restoration_certificate_coverage_percent": 120,
            "renewable_energy_certificate_coverage_of_US_operating_energy_percent": 36,
            "average_renewable_share_from_grid_US_operating_portfolio_percent": 28,
            "electricity_from_grid": "nearly_100_percent_with_less_than_1_percent_from_on_site_emergency_generators",
            "operating_site_water_in_high_or_extremely_high_stress_regions_percent": 0,
            "high_stress_sites_not_operational_during_reporting_period": ["Los_Angeles", "Phoenix"],
            "ENERGY_STAR_2026": ["DFW01-01", "SMF01-01"],
            "all_current_data_centers_provider_wording": "non_evaporative_closed_loop_cooling",
            "boundary": "PUE and WUE are design metrics, not measured facility results. The absolute water, renewable and CUE figures use the 2024 operating/reporting boundary and must not be applied to the 2026 mixed-lifecycle directory.",
        },
        "AI_and_accelerator_boundary": {
            "LAX01_Lambda": {"initial_lease_mw": 21, "hardware_family": "NVIDIA_Blackwell", "customer_and_compute_operator": "Lambda", "Prime_role": "facility_power_cooling_and_delivery", "first_AI_data_halls_provider_says_online": True},
            "physical_GPU_model_variant_count_owner_delivery_state_rack_count_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "Prime_owned_physical_GPU_inventory": "not_established",
            "accelerator_ledger_action": "no_numeric_Prime_owned_physical_inventory_row_created",
        },
        "legal_ownership_and_financial_boundary": {
            "company_status": "private_and_currently_described_as_majority_founder_owned",
            "founder_and_CEO": "Nicholas_Laag",
            "2025_strategic_investors": ["Snowhawk", "Nuveen"],
            "other_named_institutional_investors": ["Macquarie_Capital", "Ares_Management", "Siemens_Financial_Services"],
            "2025_investment_terms": "undisclosed",
            "Macquarie_2025_action": "partially_realised_its_stake_without_public_value_or_remaining_percentage",
            "Siemens_FY2025_disclosures": {"Prime_Data_Centers_LLC_equity_interest_percent": 3, "Prime_Data_Centers_LLC_net_income_and_equity": "not_available", "Prime_Super_Holding_One_LLC_equity_interest_percent": 9, "Prime_Super_Holding_One_LLC_latest_local_GAAP_net_income_EUR_million": -14, "Prime_Super_Holding_One_LLC_latest_local_GAAP_equity_EUR_million": 491},
            "Siemens_boundary": "Direct and holding-entity interests have different legal perimeters and cannot be added into an inferred Siemens economic stake in Prime.",
            "project_investment_headlines": {"PHX01_Prime_investment_USD_billion_more_than": 3, "ESB01_phase_1_EUR_billion_approximate": 2, "ESB01_full_build_EUR_billion_expected": 6, "Macquarie_2021_ten_year_target_USD_billion_more_than": 5},
            "standalone_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_debt_customer_concentration_site_economics_ROIC_and_valuation": "undisclosed",
            "boundary": "Investor stakes, parent financial statements, project investment plans and customer spending are not Prime standalone revenue, profit, cash flow, incurred capex or valuation.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "current_facility_candidates": 4,
            "current_facility_refs": ["prime_dfw01_01", "prime_sjc02", "prime_sjc03", "prime_sjc04"],
            "historical_or_pipeline_candidate_refs": ["prime_aal01_saeby_campus_plan"],
            "raw_operator_labels": sorted({row["raw_operator"] for row in osm_rows}),
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Six OSM objects represent four current facility candidates plus one Saeby plan. DFW01-01 has two building footprints, so objects and facilities are not equal denominators.",
        },
        "outlook": {
            "positive_signals": ["4GW_plus_roadmap", "large_US_and_Europe_development_optionality", "operating_LAX01_Lambda_Blackwell_deployment", "contracted_or_leased_capacity_at_multiple_projects", "institutional_equity_support", "closed_loop_and_liquid_cooling_capability"],
            "risk_signals": ["only_9_current_directory_pages_against_13_or_14_campus_headlines", "mixed_lifecycle_1_09GW_scope", "330MW_unallocated_between_campus_and_card_values", "large_permitting_grid_and_construction_execution_burden", "private_standalone_financials_and_leverage_undisclosed", "customer_concentration_undisclosed", "no_Prime_owned_GPU_inventory", "no_per_site_as_built_BOM_or_measured_PUE_WUE"],
            "analytical_view": "Prime has credible hyperscale and AI delivery evidence, a large development pipeline and deep institutional backing. The public investment case remains non-underwritable as a standalone operator because live load, utilization, contracted economics, customer concentration, leverage, current cap table and project-level returns are not disclosed, while most published capacity is not an operating denominator.",
        },
        "remaining_material_gaps": [
            "current_13_or_14_campus_22_location_29_data_center_and_28_card_counts_to_exact_legal_building_title_lease_and_lifecycle_roster",
            "per_site_operating_energized_customer_accepted_leased_utilized_billed_and_actual_IT_load",
            "per_site_grid_voltage_feeds_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_acceptance_and_remaining_life",
            "per_site_measured_PUE_WUE_CUE_energy_water_renewable_hourly_matching_and_live_liquid_cooled_MW",
            "physical_GPU_model_variant_count_owner_host_site_delivery_rack_fabric_power_utilization_customer_revenue_and_margin",
            "standalone_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_debt_customer_concentration_site_economics_ROIC_and_valuation",
            "current_founder_Snowhawk_Nuveen_Macquarie_Ares_Siemens_stakes_preferences_voting_rights_governance_and_ultimate_economic_ownership",
            "Berlin_Helsinki_Saeby_and_other_hidden_campus_land_permit_grid_financing_construction_customer_launch_or_cancellation_status",
            "ESB01_EIA_permits_grid_connection_financing_customer_contract_final_design_construction_and_go_live",
        ],
        "sources": sources,
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
    registry = args.output_dir / "prime_data_centers_official_facility_registry.jsonl"
    summary_path = args.output_dir / "prime_data_centers_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
