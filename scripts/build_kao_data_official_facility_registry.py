#!/usr/bin/env python3
"""Build a scope-safe Kao Data facility and evidence registry.

Kao's current site publishes seven facility codes across four UK locations and
separately announced a Park Royal project.  The company, investor and statutory
sources use several different capacity, financial and environmental perimeters.
This builder retains those perimeters, dates and lifecycle states instead of
turning a mixed 160-MW-plus headline, a 106-MW build pipeline, customer GPUs or
an ultimate Harlow expansion envelope into current operating IT load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


HOME = "https://kaodata.com/"
ABOUT = "https://kaodata.com/about/"
INVESTORS = "https://kaodata.com/about/investors/"
PARTNERS = "https://kaodata.com/about/partners/"
SUSTAINABILITY = "https://kaodata.com/about/sustainability-esg/"
HARLOW = "https://kaodata.com/locations/harlow/"
NORTHOLT = "https://kaodata.com/locations/northolt/"
SLOUGH = "https://kaodata.com/locations/slough/"
MANCHESTER = "https://kaodata.com/locations/manchester/"
PARK_ROYAL = "https://kaodata.com/discover/news/kao-data-acquires-new-industrial-site-in-park-royal-west-london/"
KLON03 = "https://kaodata.com/discover/news/kao-data-announces-construction-of-a-new-17-6mw-liquid-cooled-ai-data-centre-in-harlow-2/"
KLON02_OPEN = "https://kaodata.com/discover/news/kao-data-announces-its-second-10mw-harlow-data-centre-is-now-live-and-operational"
KLON02_BUILD = "https://kaodata.com/discover/news/kao-data-expands-harlow-campus-with-construction-of-second-high-performance-10mw-data-centre/"
HARLOW_POWER = "https://kaodata.com/uploads/KDL1-Data-Sheet-Data-Centre-Power-Resiliency.pdf"
HARLOW_CELL = "https://kaodata.com/uploads/Data-Sheet-KDL1-Technology-Cell.pdf"
HARLOW_CFD = "https://kaodata.com/using-cfd-analysis-to-design-and-build-the-uk-innovation-corridors-home-for-hpc-and-ai/"
SLOUGH_2022 = "https://kaodata.com/discover/news/kao-data-expands-uk-data-centre-footprint-with-16mw-facility-in-slough/"
SLOUGH_ENGINEERING = "https://kaodata.com/discover/news/kao-data-appoints-gratte-brothers-ltd-to-support-high-performance-data-centre-expansion/"
COMMISSIONING = "https://kaodata.com/the-unseen-heroes-behind-every-successful-ai-deployment/"
MANCHESTER_WHITEPAPER = "https://kaodata.com/wp-content/uploads/2026/03/Kao-Data-Why-Manchester-Whitepaper-v1.pdf"
MANCHESTER_RESPONSE = "https://kaodata.com/discover/news/response-to-youtube-video/"
MANCHESTER_APPROVAL = "https://kaodata.com/discover/news/kao-data-announces-planning-approved-for-new-350m-greater-manchester-data-centre-2/"
NEBIUS = "https://kaodata.com/discover/news/nebius-chooses-kao-datas-harlow-campus-for-major-ai-infrastructure-deployment/"
ORI = "https://kaodata.com/discover/news/ori-selects-kao-data-for-its-first-uk-ai-cloud-region/"
NVIDIA_CAMBRIDGE = "https://nvidianews.nvidia.com/news/nvidia-calls-uk-ai-strategy-important-step-will-open-cambridge-1-supercomputer-to-uk-healthcare-startups"
NVIDIA_DGX_A100 = "https://docs.nvidia.com/dgx/dgxa100-user-guide/introduction-to-dgxa100.html"
ESG_REPORT = "https://kaodata.com/uploads/Kao-Data-ESG-Report-2024-FINAL-compressed.pdf"
SHELL_RENEWAL = "https://kaodata.com/discover/news/shell-energy-renews-deal-with-kao-data-helping-to-power-the-uks-ai-ambitions-with-renewable-electricity/"
CBRE = "https://kaodata.com/discover/news/kao-data-names-cbre-as-its-new-data-centre-facilities-management-partner/"
DEBT_RAISE = "https://kaodata.com/discover/news/kao-data-completes-206m-debt-raise-with-deutsche-bank-to-accelerate-data-centre-platform-expansion/"
ACCOUNTS_FY2025 = "https://find-and-update.company-information.service.gov.uk/company/11756346/filing-history/MzQ5NTEzNjI1OGFkaXF6a2N4/document?download=1&format=pdf"
INFRATIL_AR2026 = "https://infratil.com/for-investors/annual-reports/annual-report-2026/"
INFRATIL_VALUATION = "https://infratil.com/for-investors/results/annual-results-for-the-year-ended-31-march-2026/infratil-31-march-2026-valuation-update/"


def record(
    code: str,
    location: str,
    address: str,
    lifecycle: str,
    card_it_mw: float | None,
    *,
    sources: list[str],
    area: dict | None = None,
    engineering: dict | None = None,
    conflicts: list[str] | None = None,
    commercial: str = "undisclosed",
) -> dict:
    return {
        "id": f"kao_{code.lower().replace('-', '_').replace(' ', '_')}",
        "object_type": "DataCenterFacilityEvidence",
        "name": code,
        "location": location,
        "country_code": "GB",
        "address_as_published": address,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "commercial_status_as_published": commercial,
        "current_provider_card_IT_load_mw": card_it_mw if card_it_mw is not None else "undisclosed",
        "published_area_context": area or {},
        "power_and_cooling_evidence": engineering or {},
        "physical_GPU_or_accelerator_inventory": "no_Kao_owned_inventory_established",
        "publication_conflicts": conflicts or [],
        "boundary": "Published IT load is design or marketed capacity, not proof of energization, customer acceptance, lease, utilization, billing or actual draw. AI-ready, DGX-Ready and liquid-cooling capability do not establish Kao-owned GPUs.",
        "source_urls": list(dict.fromkeys(sources)),
    }


HARLOW_CAMPUS = {
    "campus_acres": 15,
    "investment_gbp_million_more_than": 230,
    "current_four_code_card_IT_mw_checksum": 71.2,
    "current_page_rounded_IT_mw": 71,
    "campus_area_sqm": 61_000,
    "technical_area_sqm": 14_000,
    "technology_suites": 16,
    "technology_suite_sqm_each": 850,
    "future_site_accommodation_mw_up_to": 150,
    "PUE_SLA_as_low_as": 1.2,
    "renewable_matching_claim_percent": 100,
    "certification_and_design": ["NVIDIA_DGX_Ready", "OCP_Ready"],
    "boundary": "The 150MW value is an ultimate future site-accommodation envelope. It is not added to the four current code cards or treated as operating capacity.",
}


FACILITIES = [
    record(
        "KLON-01", "Harlow", "Kao Data Campus, London Road, Harlow, CM17 9NA",
        "operational", 8.8, sources=[HARLOW, HARLOW_POWER, HARLOW_CELL, HARLOW_CFD, NVIDIA_CAMBRIDGE],
        area={"campus_context": HARLOW_CAMPUS},
        engineering={
            "facility_cooling": "indirect_evaporative_refrigerant_free_with_water_evaporation_on_hot_days",
            "rack_density_evidence_kw": "25_to_40_and_beyond_historical_CFD_article",
            "campus_power_sheet_scope": "historical_or_partial_Harlow_scope_not_allocated_per_facility",
        },
    ),
    record(
        "KLON-02", "Harlow", "Kao Data Campus, London Road, Harlow, CM17 9NA",
        "operational", 8.8, sources=[HARLOW, KLON02_OPEN, KLON02_BUILD, HARLOW_POWER, HARLOW_CELL],
        area={"campus_context": HARLOW_CAMPUS, "historical_technical_area_sqm": 3_400, "historical_technology_suites": 4, "historical_racks_almost": 1_800},
        engineering={"historical_PUE_target_below": 1.2, "backup_fuel": "HVO"},
        conflicts=["The current Harlow card says 8.8MW; 2022 and 2023 construction/opening releases describe KLON-02 as 10MW."],
    ),
    record(
        "KLON-03", "Harlow", "Kao Data Campus, London Road, Harlow, CM17 9NA",
        "under_development", 17.6, sources=[HARLOW, KLON03, NEBIUS, INFRATIL_AR2026],
        area={"campus_context": HARLOW_CAMPUS},
        engineering={"cooling": ["hybrid_air", "direct_to_chip_liquid"], "Nebius_22MW_contract": "Harlow_campus_scope_not_assigned_exclusively_to_this_code"},
        conflicts=["The current card retains 17.6MW under development; Infratil rounds the Harlow work to 18MW under construction."],
    ),
    record(
        "KLON-04", "Harlow", "Kao Data Campus, London Road, Harlow, CM17 9NA",
        "planned", 36.0, sources=[HARLOW, INFRATIL_AR2026],
        area={"campus_context": HARLOW_CAMPUS},
        engineering={"exact_power_cooling_design_and_equipment_BOM": "undisclosed"},
    ),
    record(
        "KLON-05", "Northolt", "Rowdell Road, Northolt, London, UB5 5QR",
        "operational", 4.0, sources=[NORTHOLT, ESG_REPORT, CBRE],
        area={"site_sqm": 4_000, "technology_suites": 4},
        engineering={"resilience": "Tier_3_equivalent_concurrently_maintainable_provider_wording", "PUE": 1.25, "renewable_matching_claim_percent": 100, "backup_fuel": "HVO"},
        conflicts=["The current page publishes postcode UB5 5QR; some Kao policy documents publish UB5 6AG."],
        commercial="fully_occupied",
    ),
    record(
        "KLON-06", "Slough", "672 Galvin Road, Slough, SL1 4AN",
        "operational", 20.0, sources=[SLOUGH, SLOUGH_2022, SLOUGH_ENGINEERING, COMMISSIONING, ESG_REPORT, CBRE],
        area={"site_sqm": 30_000, "technology_suites": 8},
        engineering={
            "resilience": "Tier_3_equivalent_concurrently_maintainable_provider_wording",
            "current_page_PUE": 1.25,
            "renewable_matching_claim_percent": 100,
            "backup_fuel": "HVO",
            "UPS": "lithium_ion",
            "cooling": "ultra_efficient_provider_wording",
            "commissioning": "tested_at_25_50_75_percent_load_with_15_second_backup_power_target_and_chiller_recovery_scenarios",
        },
        conflicts=["The current page says 20MW and PUE 1.25; the 2022 release and FY2024-25 ESG report describe 16MW, and the release targeted PUE below 1.2."],
    ),
    record(
        "KMAN-01", "Manchester", "Kenwood Point, Kenwood Road, Reddish, Stockport, SK5 6PH",
        "under_development", 33.0, sources=[MANCHESTER, MANCHESTER_WHITEPAPER, MANCHESTER_RESPONSE, MANCHESTER_APPROVAL, ACCOUNTS_FY2025],
        area={"site_sqm": 40_000, "technical_area_sqm": 11_000, "racks_more_than": 4_000, "project_investment_gbp_million": 350},
        engineering={"cooling": ["air", "liquid", "closed_loop"], "PUE_target": 1.2, "renewable_matching_claim_percent": 100, "backup_fuel": "HVO", "designed_DGX_Ready": True},
        conflicts=["The current card says 33MW and Q3 2027 operational, while a 2026 whitepaper says 40MW and Kao's 2026-07-01 response says power is expected late 2027, buildings are built during 2027 and operation begins in 2028."],
    ),
    record(
        "Park Royal code undisclosed", "Park Royal, West London", "Former Frogmore Industrial Estate, exact street address undisclosed",
        "site_acquired_redevelopment_planned", None, sources=[PARK_ROYAL, INFRATIL_AR2026, INFRATIL_VALUATION],
        area={"site_acres": 4.7, "site_sqft": 107_000, "target_ready_for_service": 2029},
        engineering={"exact_grid_power_IT_load_design_and_equipment_BOM": "undisclosed", "investor_valuation_assumption": "30MW_plus_West_London_greenfield_site_ready_early_2029_not_explicitly_allocated_by_Kao_provider_release"},
        conflicts=["Kao calls the parcel a former industrial estate; Infratil's valuation update describes a new West London greenfield site. The apparent project crosswalk is not a legal parcel bridge."],
    ),
]


OSM_CROSSWALK = {
    "osm_way_699790674": ("kao_klon_01", "exact_named_facility_building"),
    "osm_way_1305758728": ("kao_klon_02", "exact_named_facility_building"),
    "osm_way_222789497": ("kao_klon_05", "exact_named_facility_building"),
    "osm_way_447245009": ("kao_klon_06", "exact_named_facility_building"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [{"source_order": order, "accessed_on": accessed_on, **item} for order, item in enumerate(FACILITIES, 1)]
    assert len(rows) == 8
    assert len({row["id"] for row in rows}) == 8
    assert Counter(row["lifecycle_as_of_2026_07_19"] for row in rows) == {
        "operational": 4,
        "under_development": 2,
        "planned": 1,
        "site_acquired_redevelopment_planned": 1,
    }
    numeric = [row["current_provider_card_IT_load_mw"] for row in rows if isinstance(row["current_provider_card_IT_load_mw"], (int, float))]
    assert round(sum(numeric), 1) == 128.2
    operational = [row["current_provider_card_IT_load_mw"] for row in rows if row["lifecycle_as_of_2026_07_19"] == "operational"]
    assert round(sum(operational), 1) == 41.6
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
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "capacity_counting_rule": "OSM geometry is a crosswalk only and contributes no additional facility or capacity count.",
        })
    assert len(rows) == 4
    assert {row["raw_operator"] for row in rows} == {"Kao Data"}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    source_urls = list(dict.fromkeys([
        HOME, ABOUT, INVESTORS, PARTNERS, SUSTAINABILITY, HARLOW, NORTHOLT, SLOUGH, MANCHESTER,
        PARK_ROYAL, KLON03, KLON02_OPEN, KLON02_BUILD, HARLOW_POWER, HARLOW_CELL, HARLOW_CFD,
        SLOUGH_2022, SLOUGH_ENGINEERING, COMMISSIONING, MANCHESTER_WHITEPAPER, MANCHESTER_RESPONSE,
        MANCHESTER_APPROVAL, NEBIUS, ORI, NVIDIA_CAMBRIDGE, NVIDIA_DGX_A100, ESG_REPORT, SHELL_RENEWAL,
        CBRE, DEBT_RAISE, ACCOUNTS_FY2025, INFRATIL_AR2026, INFRATIL_VALUATION,
    ]))
    return {
        "id": "kao_data_official_facility_summary_2026_07_19",
        "operator": "Kao Data",
        "legal_entity_boundary": "Kao_Data_Limited_group_Harlow_Operations_Limited_trading_site_and_project_subsidiaries",
        "accessed_on": accessed_on,
        "current_provider_roster": {
            "location_pages": 4,
            "named_current_facility_codes": 7,
            "separate_Park_Royal_plan_records": 1,
            "registry_records": len(records),
            "lifecycle_counts": dict(sorted(Counter(row["lifecycle_as_of_2026_07_19"] for row in records).items())),
            "numeric_current_card_IT_mw_checksum": 128.2,
            "operational_current_card_IT_mw_checksum": 41.6,
            "mixed_lifecycle_company_headline_IT_mw_more_than": 160,
            "headline_minus_current_card_checksum_mw_at_least": 31.8,
            "FY2026_investor_operating_capacity_mw": 37,
            "FY2026_investor_Harlow_under_construction_mw": 18,
            "FY2026_investor_future_build_pipeline_mw": 106,
            "boundary": "The 128.2MW card checksum, 41.6MW operational-card checksum, 37MW investor operating measure, 18MW construction round number, 106MW future pipeline, 150MW Harlow accommodation envelope and 160MW-plus mixed-lifecycle company headline are separate scopes and are not added.",
        },
        "Harlow_power_and_cooling_reconciliation": {
            "current_four_code_IT_mw_checksum": 71.2,
            "current_page_rounded_mw": 71,
            "future_site_accommodation_mw_up_to": 150,
            "historical_power_sheet_ITE_load_mw": 40,
            "grid_connection": "43.5MVA_UKPN_from_Harlow_West_Grid_over_approximately_5km",
            "on_site_substation_MVA": 43.5,
            "transformers": "3x_33kV_to_11kV_30MVA_at_N_plus_1",
            "building_feeds": "dual_feeds_each_capable_of_supporting_whole_building_provider_sheet",
            "generators": "7x_2.2MW_11kV_at_N_plus_1_with_six_rated_for_full_ITE_load",
            "generator_start_to_full_load_seconds": "18_to_33",
            "generator_fuel_hours_each": 48,
            "refuel_SLA_hours": 8,
            "UPS": "N_plus_1_with_A_B_C_feeds_and_N_plus_2_distribution_to_rack",
            "rack_density_kw_up_to": 80,
            "cooling": ["indirect_evaporative_for_KLON_01", "hybrid_air_and_direct_to_chip_for_KLON_03"],
            "boundary": "The power and technology-cell sheets are older Harlow/KDL1 material and their 40MW ITE scope does not reconcile to today's 71.2MW four-code card sum. Equipment is not allocated to every current building without a one-line and as-built acceptance bridge.",
        },
        "AI_and_accelerator_boundary": {
            "Cambridge_1_at_launch": {
                "site": "Kao_operated_Harlow_facility_exact_code_not_stated_in_NVIDIA_source",
                "owner_and_compute_operator": "NVIDIA",
                "DGX_A100_systems": 80,
                "A100_GPUs_per_DGX_system": 8,
                "derived_A100_GPU_count": 640,
                "derivation": "80_DGX_A100_systems_times_8_A100_GPUs_per_official_DGX_A100_specification",
                "hardware": ["A100_GPU", "BlueField_2_DPU", "HDR_InfiniBand"],
                "boundary": "The 640 count is a launch-configuration inference from two NVIDIA sources, not a July 2026 inventory audit and not Kao-owned hardware.",
            },
            "Ori": {"site": "Harlow", "hardware": ["H200_first_tranche", "GB200_planned_from_April_2025"], "counts_and_current_delivery_state": "undisclosed", "owner": "customer_or_compute_provider_not_Kao"},
            "Nebius": {"site": "Harlow_campus", "contract_mw": 22, "term_years": 10, "specific_facility_code_GPU_model_count_delivery_acceptance_price_revenue_and_margin": "undisclosed", "boundary": "Contract MW is not added to campus capacity and does not prove the whole deployment is live."},
            "Kao_owned_physical_GPU_inventory": "not_established",
        },
        "sustainability_reconciliation": {
            "FY2025_statutory_SECR": {
                "grid_energy_GWh": 121.79,
                "generator_energy_GWh": 0.17,
                "total_energy_GWh": 121.96,
                "PUE": 1.52,
                "WUE": 0.18,
                "scope_1_tCO2e": 628,
                "scope_2_location_tCO2e": 8_646,
                "scope_3_tCO2e": 18_811,
                "total_tCO2e": 28_085,
                "energy_intensity_MWh_per_GBP_revenue": 0.001911,
            },
            "FY2024_25_ESG_report": {
                "estate_PUE": 1.53,
                "estate_WUE": 0.26,
                "energy_MWh": 122_101.95,
                "potable_water_litres": 15_669_000,
                "scope_1_tCO2e": 477.55,
                "scope_2_location_tCO2e": 8_646.16,
                "scope_3_tCO2e": 18_811.64,
                "REF_percent": 100,
                "market_based_CUE": 0,
                "site_PUE": {"KLON_01": 1.27, "KLON_02": 1.63, "KLON_05": 1.49, "KLON_06": 1.74},
                "site_WUE": {"KLON_01": 0.57, "KLON_02": 0.33, "KLON_05": 0.07, "KLON_06": 0.07},
            },
            "2026_Shell_contract": {"annual_supply_GWh_around": 140, "renewable_matching": "UK_assets_with_initial_Dogger_Bank_output_from_2025", "HVO_lifecycle_emission_reduction_percent_up_to_provider_claim": 90},
            "boundary": "The audited SECR and ESG report publish slightly different PUE, WUE, energy and Scope 1 values for apparently similar periods. Their methodologies and reporting perimeters are not silently normalized. Renewable certificates and market-based CUE zero do not mean zero location-based emissions or hourly carbon-free power.",
        },
        "legal_ownership_and_financial_reconciliation": {
            "parent": {"name": "Kao Data Limited", "company_number": "11756346", "status": "private_holding_company"},
            "trading_site_entity": {"name": "Harlow Operations Limited", "company_number": "09227383", "site_footer_trading_role": "current_Kao_Data_website"},
            "FY2025_subsidiaries": ["KD MidCo Limited", "KD OpCo Limited", "Harlow Operations Limited", "Harlow Properties Limited", "KD 1 Limited", "KD 2 Limited", "KD 5 Limited", "KD 6 Limited", "KD 8 Limited", "KD ServCo Limited"],
            "known_project_entity_link": "KD_5_Limited_entered_2025_08_13_Manchester_loan",
            "unresolved_site_entity_bridge": "Northolt_Slough_Park_Royal_and_each_Harlow_building_to_KD1_KD2_KD6_or_acquired_SPVs",
            "ownership_at_2026_03_31_percent": {"Infratil": 54.7, "Legal_and_General_Group": 33.4, "Goldacre": 11.7, "rounding_difference": 0.2},
            "governance": "Infratil_reports_significant_influence_but_no_unilateral_control_or_joint_control_and_accounts_for_Kao_as_an_associate",
            "FY2025_audited_GBP_thousand": {
                "revenue": 63_814, "recurring_revenue": 31_227, "power_revenue": 26_229, "ancillary_revenue": 6_358,
                "gross_profit": 17_095, "operating_profit": 4_177, "adjusted_EBITDA": 4_916, "internal_adjusted_EBITDA": 4_943,
                "net_loss": -22_647, "operating_cash_flow": 2_432, "investment_property_expenditure": 80_142,
                "ending_cash": 28_185, "restricted_cash": 5_244, "assets": 544_466, "liabilities": 188_340,
                "net_assets": 356_126, "secured_loan_carrying_value": 132_393, "net_debt": 104_208,
                "remaining_performance_obligations": 365_045, "contracted_capex_not_provided": 42_256,
            },
            "FY2025_derived_percent": {"revenue_growth": 12.905, "gross_margin": 26.789, "operating_margin": 6.546, "adjusted_EBITDA_margin": 7.704, "net_loss_margin": -35.489},
            "FY2026_IFRS_associate_summary_GBP_million_100_percent_Kao": {"revenue": 73.7, "net_loss_after_tax": -26.8, "assets": 788.1, "liabilities": 422.6, "net_assets": 365.5},
            "FY2026_investor_management_GBP_million": {"revenue": 48, "EBITDAF": 5, "EBITDAF_margin_percent": 10, "capital_expenditure": 202, "net_debt": 252},
            "independent_equity_valuation_at_2026_03_31_GBP_million": {"midpoint": 686.5, "range_low": 622.7, "range_high": 755.6, "Infratil_54_7_percent_share_value": 375.2},
            "financing": {"2024_facility_GBP_million": 206, "accordion_GBP_million": 356, "drawn_at_2025_03_31_GBP_million": 137.6, "Manchester_2025_08_13_loan_GBP_million": 28.4},
            "boundary": "FY2026's IFRS associate revenue of GBP73.7m and investor-management revenue of GBP48m are not reconciled; the latter likely uses an adjusted perimeter but no bridge is published. FY2025 operating profit is not a FY2026 operating-profit estimate. RPO, debt capacity, valuation, capex and customer contract MW are not revenue.",
        },
        "OSM_crosswalk": {
            "operator_tagged_objects": len(osm_rows),
            "distinct_current_facilities": 4,
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Four OSM ways crosswalk to KLON-01, KLON-02, KLON-05 and KLON-06 only; they do not establish a complete eight-record portfolio, ownership, capacity or lifecycle.",
        },
        "outlook": {
            "positive_signals": ["22MW_ten_year_Nebius_contract", "FY2026_revenue_growth_and_positive_management_EBITDAF", "Harlow_liquid_cooled_expansion", "106MW_future_build_pipeline", "30MW_plus_West_London_valuation_assumption", "current_institutional_equity_support", "renewable_matching_and_40MW_private_wire_solar_agreement"],
            "risk_signals": ["FY2026_net_loss_and_high_capex", "net_debt_growth", "long_grid_and_construction_schedule", "capacity_denominator_conflicts", "private_company_and_no_direct_public_security", "management_and_IFRS_revenue_perimeters_unbridged", "customer_concentration_contract_economics_and_live_load_undisclosed", "no_Kao_owned_GPU_inventory_or_complete_as_built_BOM"],
            "analytical_view": "Kao has strong specialist positioning for UK AI colocation, a credible anchor contract and measurable revenue growth, but remains in a capital-intensive expansion phase with accounting losses, rapidly rising debt and material delivery risk. The public investable look-through is principally Infratil, where Kao is only one associate; the independent equity valuation already embeds West London delivery and a lower discount rate, so future returns depend on converting grid, construction and contracted MW into accepted, billed capacity rather than merely expanding headline pipeline.",
        },
        "remaining_material_gaps": [
            "seven_current_codes_Park_Royal_and_160MW_plus_headline_to_exact_legal_building_title_lease_and_lifecycle_bridge",
            "128_2MW_cards_41_6MW_operational_cards_37MW_investor_operating_18MW_construction_106MW_pipeline_150MW_Harlow_and_160MW_plus_scope_reconciliation",
            "per_site_operating_energized_customer_accepted_leased_utilized_billed_and_actual_IT_load",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_acceptance_loading_and_remaining_life",
            "per_site_live_liquid_cooled_MW_measured_PUE_WUE_energy_water_hourly_matching_and_emissions",
            "Cambridge_1_Ori_Nebius_physical_GPU_model_count_current_delivery_owner_site_code_rack_fabric_power_utilization_revenue_and_margin",
            "FY2026_IFRS_73_7m_to_management_48m_revenue_bridge_and_accounting_operating_profit_cash_flow_detail",
            "customer_concentration_contract_pricing_acceptance_RPO_conversion_site_economics_ROIC_and_covenant_headroom",
            "current_legal_subsidiary_to_each_site_and_project_asset_bridge_and_exact_current_shareholder_rights",
            "Manchester_and_Park_Royal_permits_grid_substation_construction_customer_contract_acceptance_and_live_load",
        ],
        "sources": source_urls,
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
    registry = args.output_dir / "kao_data_official_facility_registry.jsonl"
    summary_path = args.output_dir / "kao_data_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "codes": 7, "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
