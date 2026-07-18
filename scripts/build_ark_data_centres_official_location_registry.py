#!/usr/bin/env python3
"""Build Ark Data Centres' location, operating-company and OSM registry.

Ark's current headline, location cards, statutory operating-company accounts and
development announcements use different scopes.  This builder keeps the eight
published location pages, the separately announced Barcelona development, the
ten related OSM footprints, the accounts' 108.42-MW built-capacity reconstruction
and the mixed-lifecycle location-card values separate.  It does not convert any
of them into a false current live-load, building or Ark-owned GPU census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


LOCATIONS_URL = "https://www.ark-d-c.com/locations"
ABOUT_URL = "https://www.ark-d-c.com/about-us"
ARK_2026_OUTLOOK = "https://www.ark-d-c.com/insights/ai-infrastructure-and-uncertainty-a-view-into-2026"
ARK_NEBIUS = "https://www.ark-d-c.com/insights/ark-data-centres-collaborates-with-nebius"
NEBIUS_LAUNCH = "https://assets.nebius.com/assets/2e98580f-8c50-40b5-b1f1-c45be76a15a5/20251106%20Nebius%20AI%20Cloud%20arrives%20in%20UK%20with%20one%20of%20the%20country%E2%80%99s%20first%20advanced%20NVIDIA%20AI%20infrastructure%20deployments.pdf"
NEBIUS_2026 = "https://assets.nebius.com/assets/938e0a84-7432-4a12-85f2-9732689045ed/08062026%C2%A0Nebius%20expands%20in%20UK%20with%20more%20NVIDIA-powered%20infrastructure%2C%20more%20customers%2C%20and%20more%20cloud%20capabilities%20for%20agentic%20and%20enterprise%20AI.pdf"
COMPANIES_HOUSE = "https://find-and-update.company-information.service.gov.uk/company/05656968"
FILING_HISTORY = "https://find-and-update.company-information.service.gov.uk/company/05656968/filing-history"
FY2025_IXBRL = "https://find-and-update.company-information.service.gov.uk/company/05656968/filing-history/MzQ5NTAxNDIxN2FkaXF6a2N4/document?format=xhtml&download=1"
CROWN_HOSTING = "https://www.gov.uk/guidance/the-crown-hosting-data-centres-framework-on-the-digital-marketplace"
UNION_PERMIT = "https://assets.publishing.service.gov.uk/media/68e64d858c1db6022d0ca226/Application_Bespoke_A001_Permit_-_03102025.pdf"
UNION_BAT = "https://consult.environment-agency.gov.uk/psc/ub3-4dg-ark-data-centres-limited-epr-zp3527ss-a001/supporting_documents/Application%20Bespoke%20A001%20%20BAT%20assessment%20%2015112024.pdf"
UNION_PLANNING = "https://planning.hillingdon.gov.uk/OcellaWeb/viewDocument?file=dv_pl_files%5C75111_APP_2025_739%5CChapter+1+Introduction.pdf&module=pl"
LONGCROSS_NOISE = "https://consult.environment-agency.gov.uk/psc/kt16-0ee-ark-data-centres-limited/supporting_documents/Application%20Bespoke%20Noise%20Assessment%20A001%2022052024.pdf"
LONGCROSS_JCA = "https://jca.co.uk/jca-and-ark-data-centres-unveil-longcross-park-a-groundbreaking-ai-ready-campus-in-surrey/"
MERIDIAN_GRATTE = "https://www.gratte.com/portfolio/dc-infrastructure-fit"
SPRING_FINNING = "https://www.finning.com/en_GB/company/news-events/product-customer-stories/ark-data-centres.html"
CODY_DATANET = "https://www.datanet.co.uk/racks-co-location/"
CODY_COOLING = "https://www.datanet.co.uk/news/smarter-cooling/"
BARCELONA_TRANSACTION = "https://www.dlapiper.com/en/news/2026/05/dla-piper-advises-ark-data-centres-on-its-more-than-eur600-million"
DIRECT_AIR = "https://www.ark-d-c.com/technologies/direct-air-cooling"
INDIRECT_AIR = "https://www.ark-d-c.com/technologies/indirect-air-cooling"
CONSTRUCTION = "https://www.ark-d-c.com/technologies/construction"
HIGH_POWER_COMPUTE = "https://www.ark-d-c.com/solutions/high-power-compute"
BUILT_TO_SUIT = "https://www.ark-d-c.com/solutions/built-to-suit-infrastructure"


def page(slug: str) -> str:
    return f"https://www.ark-d-c.com/locations/{slug}"


LOCATIONS = [
    {
        "id": "ark_cody_park",
        "provider_label": "Cody Park",
        "country_code": "GB",
        "locality": "Farnborough",
        "postcode": "GU14 0LH",
        "official_page": page("cody-park"),
        "provider_coordinates": {"latitude": 51.2758, "longitude": -0.7643},
        "page_total_compute_capacity_mw": 51,
        "page_data_center_count": 6,
        "page_operational_since": "2011",
        "lifecycle_class": "operating_and_expanding",
        "page_scale_context": {"campus_acres": 36, "tier": "Tier_3", "PUE_claim_less_than": 1.3},
        "capabilities": ["AI_ready", "direct_air", "indirect_air", "liquid_cooled_capability", "modular_steel"],
        "OSM_refs": ["osm_way_838655597", "osm_way_838655598", "osm_way_838655599", "osm_way_838655600", "osm_way_838655601"],
        "equipment_evidence": {
            "scope": "Datanet-accessible_Cody_configuration_not_all_campus_buildings",
            "UPS": "eight_400kVA_modules_configured_2_times_N_plus_1",
            "distribution": ["A_and_B_busbars", "independent_switchgear", "independent_11kV_to_415V_transformer"],
            "cooling": "BladeRoom_Air_Optimizers_N_plus_N_free_air_and_evaporative",
        },
        "additional_sources": [CODY_DATANET, CODY_COOLING],
    },
    {
        "id": "ark_spring_park",
        "provider_label": "Spring Park",
        "country_code": "GB",
        "locality": "Corsham",
        "postcode": "SN13 9GB",
        "official_page": page("spring-park"),
        "provider_coordinates": {"latitude": 51.4313, "longitude": -2.2212},
        "page_total_compute_capacity_mw": 55,
        "page_data_center_count": 6,
        "page_operational_since": "2010",
        "lifecycle_class": "operating_and_expanding",
        "capabilities": ["AI_ready", "direct_air", "indirect_air", "liquid_cooled_capability", "modular_steel"],
        "OSM_refs": ["osm_way_574135457", "osm_way_574135468", "osm_way_574135471"],
        "equipment_evidence": {
            "scope": "P1_phase_2_only_not_campus_wide",
            "generators": "two_Cat_C18_700kVA_standby_sets_in_N_plus_1",
            "fuel": "each_enclosure_on_bunded_slab_tank_with_combined_72_hours_at_full_load",
            "cooling": "fresh_air_cooling",
        },
        "additional_sources": [SPRING_FINNING],
    },
    {
        "id": "ark_meridian_park",
        "provider_label": "Meridian Park",
        "country_code": "GB",
        "locality": "Edmonton / London",
        "postcode": "N9 0BD",
        "official_page": page("meridian-park"),
        "provider_coordinates": {"latitude": 51.6224, "longitude": -0.0413},
        "page_total_compute_capacity_mw": 16,
        "page_data_center_count": 1,
        "page_operational_since": "2020",
        "lifecycle_class": "operating",
        "capabilities": ["onsite_solar", "backup_generators", "indirect_air"],
        "OSM_refs": ["osm_way_131474700"],
        "equipment_evidence": {
            "contractor_scope": "16MW_white_space_seven_data_halls_two_floors_completed_May_2021",
            "electrical": ["multi_voltage_infrastructure", "MV_generators", "LV_transformers_and_switchgear", "UPS", "busbar"],
            "controls_and_safety": ["BMS", "gas_suppression"],
            "cooling": "indirect_evaporative_cooling_units_on_external_gantries",
            "energy": "direct_wire_from_adjacent_London_Energy_energy_from_waste_plant",
        },
        "additional_sources": [MERIDIAN_GRATTE],
    },
    {
        "id": "ark_union_park",
        "provider_label": "Union Park",
        "country_code": "GB",
        "locality": "Hayes / London",
        "postcode": "UB3 4DG",
        "official_page": page("union-park"),
        "provider_coordinates": {"latitude": 51.5122, "longitude": -0.4308},
        "page_total_compute_capacity_mw": 99,
        "page_data_center_count": 4,
        "page_operational_since": "2024",
        "lifecycle_class": "part_operating_and_part_construction_or_development",
        "page_scale_context": {"campus_area_sqm": 56000},
        "capabilities": ["onsite_solar", "advanced_air_cooling", "rainwater_harvesting", "living_roofs_and_walls", "renewable_grid_claim", "HVO_backup"],
        "OSM_refs": [],
        "equipment_evidence": {
            "Ark_operated_scope": "EC3_UP3_only",
            "generators": "twelve_Rolls_Royce_MTU_DS4000_each_3_2MWe_output_and_8_01MWth_input",
            "aggregate_thermal_input_mw": 96.12,
            "emissions_control": "SCR_each_set_NOx_target_95mg_per_Nm3_at_5_percent_O2_EPA_Tier_II",
            "grid": "National_Grid_North_Hyde_66kV_to_Ark_owned_66_11kV_primary_substation_two_routes_2N",
            "fuel_storage_litres": 629000,
            "permit_operation_boundary": "less_than_500_hours_per_year_emergency_and_testing_class",
            "other_operator_boundary": "EC1_and_EC2_are_under_Amazon_Data_Services_UK_environmental_permit_not_Ark_operation",
        },
        "additional_sources": [UNION_PERMIT, UNION_BAT, UNION_PLANNING],
    },
    {
        "id": "ark_longcross_park",
        "provider_label": "Longcross Park",
        "country_code": "GB",
        "locality": "Chertsey / Surrey",
        "postcode": "KT16 0EE",
        "official_page": page("longcross-park"),
        "provider_coordinates": {"latitude": 51.3837, "longitude": -0.5798},
        "page_total_compute_capacity_mw": 54,
        "page_data_center_count": 2,
        "page_operational_since": "2025",
        "lifecycle_class": "operating_and_expanding",
        "capabilities": ["AI_ready", "direct_air", "liquid_ready_or_capable", "rainwater_harvesting", "HVO_backup"],
        "OSM_refs": ["osm_way_1481166632"],
        "equipment_evidence": {
            "LP1": "completed_100_percent_direct_air_cooled_hyperscale_halls_with_BladeRoom_and_zero_data_hall_mechanical_cooling",
            "UPS": "25MVA_turnkey_medium_voltage_architecture_reported_by_project_partners",
            "ABB_components_vendor_reported": ["HiPerGuard_solid_state_MV_UPS", "UniGear_switchgear", "Zenon_ZEE600_controls"],
            "UPS_efficiency_claim_percent_at_heavy_load": 98,
            "permit_stage_generators": "28_emergency_sets_assessed_with_24_continuous_during_72_hour_outage_and_4_redundant",
            "generator_OEM_boundary": "not_selected_in_reviewed_permit_stage_noise_assessment",
        },
        "additional_sources": [LONGCROSS_NOISE, LONGCROSS_JCA, ARK_NEBIUS, NEBIUS_LAUNCH],
    },
    {
        "id": "ark_alliance_park",
        "provider_label": "Alliance Park",
        "country_code": "GB",
        "locality": "Park Royal / London",
        "postcode": "W3 0RZ",
        "official_page": page("alliance-park"),
        "provider_coordinates": {"latitude": 51.5179, "longitude": -0.2661},
        "page_total_compute_capacity_mw": 50,
        "page_data_center_count": 2,
        "page_operational_since": "Under construction",
        "lifecycle_class": "under_construction",
        "page_scale_context": {"tier_target": "Tier_3", "PUE_target_less_than": 1.3},
        "capabilities": ["AI_ready", "direct_air", "indirect_air", "liquid_cooled_capability", "modular_steel"],
        "OSM_refs": [],
        "equipment_evidence": {},
        "additional_sources": [],
    },
    {
        "id": "ark_brussels",
        "provider_label": "Brussels",
        "country_code": "BE",
        "locality": "Brussels",
        "postcode": None,
        "official_page": page("brussels"),
        "provider_coordinates": None,
        "page_total_compute_capacity_mw": 24,
        "page_data_center_count": 2,
        "page_operational_since": "Under construction",
        "lifecycle_class": "planning_permitting_or_under_construction",
        "page_scale_context": {"secured_power_MVA": 40, "power_status": "secured"},
        "capabilities": ["Tier_3_resilience_target", "direct_air", "indirect_air", "modular_steel"],
        "OSM_refs": [],
        "equipment_evidence": {},
        "additional_sources": [],
    },
    {
        "id": "ark_hilfield_park",
        "provider_label": "Former Mercure Hotel / Hilfield Park",
        "country_code": "GB",
        "locality": "Elstree / Borehamwood",
        "postcode": None,
        "official_page": page("elstree"),
        "provider_coordinates": None,
        "page_total_compute_capacity_mw": 200,
        "page_total_compute_capacity_qualifier": "approximately",
        "page_data_center_count": 6,
        "page_data_center_count_qualifier": "at_least_or_more_than",
        "page_operational_since": "2029",
        "lifecycle_class": "development",
        "page_scale_context": {"utility_delivery_MVA": 250, "utility_delivery_start": 2028},
        "capabilities": ["modular_steel", "direct_air", "indirect_air", "liquid_cooled_capability"],
        "OSM_refs": [],
        "equipment_evidence": {},
        "additional_sources": [],
    },
    {
        "id": "ark_barcelona",
        "provider_label": "Barcelona / La Maquinista",
        "country_code": "ES",
        "locality": "Barcelona",
        "postcode": None,
        "official_page": None,
        "provider_coordinates": None,
        "page_total_compute_capacity_mw": None,
        "page_data_center_count": None,
        "page_operational_since": None,
        "lifecycle_class": "land_acquired_development",
        "development_context": {
            "industrial_land_sqm": 30000,
            "investment_EUR_million_more_than": 600,
            "IT_capacity_mw_up_to": 45,
            "exact_schedule": "undisclosed",
        },
        "capabilities": [],
        "OSM_refs": [],
        "equipment_evidence": {},
        "additional_sources": [ARK_2026_OUTLOOK, BARCELONA_TRANSACTION],
    },
]


OSM_CROSSWALK = {
    "osm_way_838655597": ("ark_cody_park", "operator_cluster_match_not_facility_code_specific"),
    "osm_way_838655598": ("ark_cody_park", "operator_cluster_match_not_facility_code_specific"),
    "osm_way_838655599": ("ark_cody_park", "operator_cluster_match_not_facility_code_specific"),
    "osm_way_838655600": ("ark_cody_park", "operator_cluster_match_not_facility_code_specific"),
    "osm_way_838655601": ("ark_cody_park", "operator_cluster_match_not_facility_code_specific"),
    "osm_way_574135457": ("ark_spring_park", "operator_cluster_match_not_complete_building_roster"),
    "osm_way_574135468": ("ark_spring_park", "operator_cluster_match_not_complete_building_roster"),
    "osm_way_574135471": ("ark_spring_park", "operator_cluster_match_not_complete_building_roster"),
    "osm_way_131474700": ("ark_meridian_park", "named_site_match"),
    "osm_way_1481166632": ("ark_longcross_park", "named_site_match"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(LOCATIONS, start=1):
        row = dict(source)
        urls = [LOCATIONS_URL, ABOUT_URL, DIRECT_AIR, INDIRECT_AIR, CONSTRUCTION]
        if source["official_page"]:
            urls.append(source["official_page"])
        urls.extend(source["additional_sources"])
        row.update({
            "object_type": "ArkDataCentresOfficialLocationRecord",
            "source_order": order,
            "physical_granularity_boundary": "A provider location card may cover a campus, multiple data centers, phased buildings or a development; page counts are not a verified current physical-building roster.",
            "power_boundary": "Page compute-capacity MW, statutory built MW, utility MVA, generator MWe or MWth, contracted runway and utilized customer load remain separate.",
            "GPU_boundary": "AI-ready capability does not establish Ark-owned GPUs; the disclosed Longcross hardware is a Nebius customer deployment.",
            "source_urls": sorted(set(urls)),
            "accessed_on": accessed_on,
        })
        records.append(row)

    assert len(records) == 9
    assert len({row["id"] for row in records}) == 9
    pages = [row for row in records if row["official_page"]]
    assert len(pages) == 8
    assert sum(row["page_data_center_count"] for row in pages) == 29
    assert sum(row["page_total_compute_capacity_mw"] for row in pages) == 549
    assert Counter(row["country_code"] for row in records) == {"GB": 7, "BE": 1, "ES": 1}
    assert sum(len(row["OSM_refs"]) for row in records) == 10
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_id, (location_ref, status) in OSM_CROSSWALK.items():
        source = osm[osm_id]
        assert source.get("operator") == "Ark Data Centres"
        rows.append({
            "osm_ref": osm_id,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "country_codes": sorted({candidate["iso2"] for candidate in source.get("country_candidates", [])}),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "location_ref": location_ref,
            "crosswalk_status": status,
            "boundary": "OSM geometry is public-map evidence, not provider-verified gross floor area, data-hall area, ownership, lifecycle, capacity, utilization or facility code.",
            "source_url": source["source_url"],
        })
    assert len(rows) == 10
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_crosswalk: list[dict], accessed_on: str) -> dict:
    pages = [row for row in records if row["official_page"]]
    operational_page_rows = [row for row in pages if row["page_operational_since"] not in {"Under construction", "2029"}]
    development_page_rows = [row for row in pages if row not in operational_page_rows]
    return {
        "id": "ark_data_centres_official_location_summary_2026_07_19",
        "object_type": "ArkDataCentresPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator": "Ark Data Centres",
        "reconstructed_location_registry": {
            "records": len(records),
            "published_location_pages": len(pages),
            "separately_announced_development_locations": ["Barcelona / La Maquinista"],
            "countries": sorted({row["country_code"] for row in records}),
            "OSM_objects": len(osm_crosswalk),
        },
        "published_roster_denominators": {
            "locations_page_headline": {"data_centres": 27, "strategic_locations": 9},
            "visible_location_pages": {"pages": 8, "page_data_center_count_lower_bound": 29, "page_capacity_mw_approximate_checksum": 549},
            "Barcelona_separate_development": {"IT_capacity_mw_up_to": 45, "published_location_page": False},
            "development_inclusive_capacity_checksum_mw_approximate": 594,
            "operational_since_page_subset": {
                "location_pages": len(operational_page_rows),
                "page_data_center_count": sum(row["page_data_center_count"] for row in operational_page_rows),
                "page_capacity_mw_checksum": sum(row["page_total_compute_capacity_mw"] for row in operational_page_rows),
                "labels": [row["provider_label"] for row in operational_page_rows],
            },
            "under_construction_or_development_page_subset": {
                "location_pages": len(development_page_rows),
                "page_data_center_count_lower_bound": sum(row["page_data_center_count"] for row in development_page_rows),
                "page_capacity_mw_approximate_checksum": sum(row["page_total_compute_capacity_mw"] for row in development_page_rows),
                "labels": [row["provider_label"] for row in development_page_rows],
            },
            "other_official_outlook_scopes": {
                "about_page_projected_MW_by_2030": 446,
                "UK_contracted_power_runway_MW_more_than": 700,
            },
            "boundary": "The 27/9 headline conflicts with the eight visible pages' 29-plus card count. The approximately 549-MW card checksum mixes operating, phased, construction and development scope. Barcelona, 446 MW by 2030 and UK 700-MW-plus contracted-power runway use other scopes and are never added into current live load.",
        },
        "FY2025_statutory_operating_company": {
            "company": "Ark Data Centres Limited",
            "company_number": "05656968",
            "period_end": "2025-06-30",
            "reporting_boundary": "Operating company accounts, not consolidated Ark Group or every current location-page project.",
            "built_capacity_disclosure": {
                "Cody_Park": {"built_MW": 48.78, "buildings": 5, "under_construction_MW": 0.8},
                "Spring_Park": {"built_MW": 41.68, "buildings": 5, "under_construction_MW": 13.5},
                "A9_building": {"built_MW": 1.6, "site_context": "Cody_Technology_Park_but_separately_disclosed"},
                "Meridian_Park": {"built_MW": 16.36},
                "built_MW_derived": 108.42,
                "under_construction_MW_derived": 14.3,
                "boundary": "The A9 bullet is retained separately because the accounts do not explicitly bridge it to the five-building Cody subtotal. Derived totals are not energized, leased, utilized, billed or customer-accepted load.",
            },
            "income_statement_GBP": {
                "FY2025": {
                    "turnover": 257640619,
                    "cost_of_sales": 221204125,
                    "gross_profit": 36436494,
                    "administrative_expenses": 32334440,
                    "operating_profit": 4102054,
                    "interest_and_investment_income": 1935168,
                    "profit_before_tax_and_net_profit": 6037222,
                },
                "FY2024": {
                    "turnover": 226537929,
                    "cost_of_sales": 203034797,
                    "gross_profit": 23503132,
                    "administrative_expenses": 32754041,
                    "operating_loss": -9250909,
                    "interest_and_investment_income": 1903291,
                    "loss_before_tax_and_net_loss": -7347618,
                },
                "derived_FY2025": {
                    "turnover_growth_percent": 13.73,
                    "gross_profit_growth_percent": 55.03,
                    "gross_margin_percent": 14.14,
                    "operating_margin_percent": 1.59,
                    "net_margin_percent": 2.34,
                    "EBITDA_like_GBP": 8506713,
                    "EBITDA_like_margin_percent": 3.30,
                    "EBITDA_like_boundary": "Operating profit plus disclosed depreciation and amortisation; not a company-reported EBITDA and not adjusted for lease economics.",
                },
            },
            "revenue_breakdown_GBP": {
                "data_centre_income": 133056309,
                "power_income": 66785729,
                "fit_out_fees": 24418526,
                "management_charges_related_entities": 32839483,
                "cost_recharges": 52306,
                "joint_venture_recharges": 488266,
            },
            "balance_sheet_and_cash_flow_GBP": {
                "net_assets": 23946959,
                "cash": 30610707,
                "current_assets": 86608585,
                "current_liabilities": 70645995,
                "net_current_assets": 15962590,
                "operating_cash_flow": 13210643,
                "purchases_intangible_assets": 515532,
                "purchases_tangible_assets": 2016385,
                "net_investing_outflow": 608280,
                "lessee_undiscounted_commitments": 487226395,
                "lessor_contracted_tenant_payments": 685539694,
                "lease_boundary": "Undiscounted commitments and contracted tenant payments are not net debt, backlog, recognized revenue or present value.",
            },
            "average_employees": {"FY2025": 139, "FY2024": 107},
            "growth_commentary": "New long-term contracts in government, financial services, telecom, cloud and IT plus a strong pipeline; management expected further growth and expansion in 2026.",
        },
        "Crown_Hosting_boundary": {
            "Ark_ownership_percent": 74.9,
            "Minister_for_Cabinet_Office_percent": 25.1,
            "governance": "jointly_managed_joint_venture",
            "FY2025_related_party_charges_GBP": {
                "running_costs": 69222392,
                "account_management": 423780,
                "sales_and_marketing": 64486,
                "trade_debtor": 7398742,
            },
            "boundary": "Crown Hosting is a UK public-sector procurement framework and joint venture; its charges are not a standalone customer revenue or margin table.",
        },
        "energy_carbon_and_cooling": {
            "calendar_2024": {
                "total_energy_MWh": 280597,
                "IT_energy_MWh": 203608,
                "PUE_derived": 1.378,
                "Scope_1_tCO2e": 2346,
                "Scope_2_market_based_tCO2e": 12325,
                "selected_Scope_3_tCO2e": 2664,
                "total_tCO2e": 17335,
                "CUE_tCO2e_per_MWh_IT": 0.085,
            },
            "calendar_2023": {"total_energy_MWh": 239803, "IT_energy_MWh": 164622, "PUE_derived": 1.457, "total_tCO2e": 2988, "CUE_tCO2e_per_MWh_IT": 0.018},
            "electricity": "100_percent_certificate_backed_carbon_free_or_renewable_grid_claim",
            "Meridian": "direct_wire_PPA_from_London_Energy_energy_from_waste_since_2021",
            "backup_fuel": "HVO_replaced_gas_oil_stocks_by_April_2022_with_claimed_90_to_95_percent_fossil_GHG_reduction",
            "free_cooling": "direct_air_free_cooling_at_scale_since_2011_with_design_PUE_improvement_from_above_1_65_to_about_1_2",
            "centralized_HV_generation": "used_since_2018_with_31_percent_less_installed_standby_capacity_than_LV_system",
            "emissions_boundary": "The 2024 increase includes a Meridian energy-from-waste factor recalculation and base-year changes. Derived PUE is a calendar-year operating-company ratio, not a measured page-card PUE for every site.",
        },
        "accelerator_deployment": {
            "site": "Longcross Park",
            "customer_owner_and_operator": "Nebius",
            "host": "Ark Data Centres",
            "initial_announced_GPU_count": 4000,
            "model_family": "NVIDIA_Blackwell_Ultra",
            "announcement_date": "2025-06-26",
            "launch_confirmed": "2025-11",
            "fabric": "NVIDIA_Quantum_X800_InfiniBand",
            "infrastructure": ["high_density_power", "air_cooled_design_per_Ark_2026_commentary", "liquid_ready_data_hall", "low_latency_connectivity", "dedicated_onsite_generation"],
            "boundary": "The 4,000-GPU figure is the initial Nebius deployment scope and the later release confirms the Blackwell Ultra cluster launch, but it is not an Ark-owned fleet or a portfolio-wide current inventory. Nebius's additional UK deployment plan is not assigned to Ark without site evidence.",
        },
        "selected_power_and_equipment": {
            "Union_Park_EC3": next(row["equipment_evidence"] for row in records if row["id"] == "ark_union_park"),
            "Longcross_Park": next(row["equipment_evidence"] for row in records if row["id"] == "ark_longcross_park"),
            "Meridian_Park": next(row["equipment_evidence"] for row in records if row["id"] == "ark_meridian_park"),
            "Spring_Park_P1_phase_2": next(row["equipment_evidence"] for row in records if row["id"] == "ark_spring_park"),
            "Cody_Datanet_accessible_scope": next(row["equipment_evidence"] for row in records if row["id"] == "ark_cody_park"),
            "boundary": "These are site-, permit-, contractor- or tenant-scope facts. They are not propagated across the portfolio or treated as a current complete as-built bill of materials.",
        },
        "ownership_and_outlook": {
            "immediate_parent": "Ark Group Limited_Isle_of_Man",
            "ultimate_parent": "Ark Capital Partners I LP Inc_Isle_of_Man",
            "Companies_House_PSC": "Revcap Properties 25 Limited",
            "market_reported_control_context": "Elliott_majority_or_control_with_Revcap_minority_reported_but_not_reconstructed_as_a_statutory_cap_table",
            "UK_expansion_roadmap_GBP_billion": 7.5,
            "projected_capacity_MW_by_2030": 446,
            "contracted_UK_power_runway_MW_more_than": 700,
            "Barcelona": {"land_sqm": 30000, "investment_EUR_million_more_than": 600, "IT_capacity_MW_up_to": 45},
            "risks": [
                "private_group_financial_and_cap_table_opacity",
                "operating_company_accounts_do_not_cover_every_portfolio_project",
                "power_grid_permitting_and_construction_timing",
                "large_lease_commitments_and_power_cost_exposure",
                "customer_and_related_party_concentration",
                "high_capex_expansion_and_acceptance_risk",
                "page_roster_capacity_and_lifecycle_conflicts",
                "potential_sale_reporting_without_confirmed_transaction",
            ],
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_crosswalk),
            "operator_label": "Ark Data Centres",
            "mapped_location_groups": Counter(row["location_ref"] for row in osm_crosswalk),
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_crosswalk), 3),
            "boundary": "The footprint checksum is geometry QA only, not provider gross floor area. Cody and Spring public-map coordinates differ from page coordinates and their polygons are not mapped one-for-one to provider data-center labels.",
            "objects": osm_crosswalk,
        },
        "unresolved_gaps": [
            "exact_current_physical_building_roster_and_27_9_headline_reconciliation",
            "location_page_29_plus_card_count_and_Barcelona_ninth_location_reconciliation",
            "per_site_operating_energized_leased_utilized_billed_and_customer_accepted_IT_load",
            "exact_ownership_lease_tenant_and_environmental_operator_roles_by_building",
            "current_group_consolidated_revenue_operating_profit_capex_debt_cash_flow_and_ROIC",
            "complete_site_level_substation_transformer_switchgear_UPS_battery_generator_and_cooling_BOM",
            "current_physical_GPU_inventory_owner_site_allocation_power_draw_utilization_revenue_and_margin",
            "measured_site_level_PUE_WUE_water_energy_emissions_and_live_liquid_cooled_MW",
        ],
        "sources": sorted({
            LOCATIONS_URL, ABOUT_URL, ARK_2026_OUTLOOK, ARK_NEBIUS, NEBIUS_LAUNCH, NEBIUS_2026,
            COMPANIES_HOUSE, FILING_HISTORY, FY2025_IXBRL, CROWN_HOSTING,
            UNION_PERMIT, UNION_BAT, UNION_PLANNING, LONGCROSS_NOISE, LONGCROSS_JCA,
            MERIDIAN_GRATTE, SPRING_FINNING, CODY_DATANET, CODY_COOLING,
            BARCELONA_TRANSACTION, DIRECT_AIR, INDIRECT_AIR, CONSTRUCTION,
            HIGH_POWER_COMPUTE, BUILT_TO_SUIT,
            *[row["official_page"] for row in records if row["official_page"]],
        }),
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_crosswalk = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_crosswalk, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "ark_data_centres_official_location_registry.jsonl"
    summary_path = args.output_dir / "ark_data_centres_official_location_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_crosswalk), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
