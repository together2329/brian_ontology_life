#!/usr/bin/env python3
"""Build a lifecycle- and scope-safe Verne facility evidence registry.

Verne's July 2026 footprint is unusually easy to overstate: two Finnish sites
were sold in February, the London facility is under a signed sale agreement,
one Finnish campus is being built, and the France and Norway projects remain
plans.  This builder keeps those lifecycle states, the audited 52.3-MW installed
capacity, site-card envelopes, grid requests, GPUs and financial perimeters
separate instead of adding them into a false operating fleet total.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY = "https://www.verne.co/locations"
ICELAND = "https://www.verne.co/locations/iceland"
ICELAND_DATASHEET = "https://www.verneglobal.com/hubfs/Downloadable_Content/Datasheets%202025/Iceland_Datasheet%20.pdf"
ICELAND_SUBSTATION = "https://www.verne.co/news/news-verne-and-landsnet-launch-high-capacity-substation"
HELSINKI_DATASHEET = "https://www.verneglobal.com/hubfs/Datasheets%202025/Helsinki%20Datasheet-1.pdf"
HELSINKI_EXPANSION = "https://www.verne.co/news/news-verne-expands-helsinki-data-center-campus-with-strategic-site-acquisition"
PORI_DATASHEET = "https://www.verneglobal.com/hubfs/Downloadable_Content/Datasheets%202025/Pori%20Datasheet.pdf"
TAMPERE_DATASHEET = "https://www.verneglobal.com/hubfs/Downloadable_Content/Datasheets%202025/Tampere%20Datasheet.pdf"
FINLAND_SALE = "https://www.verne.co/news/news-glesys-acquires-managed-private-cloud-operations"
ARCUS_NEWS = "https://arcusip.com/news/"
MANTSALA_BUILD = "https://www.verne.co/news/news-verne-begins-construction-of-the-first-70-mw-on-its-data-center-campus-in-m%C3%A4nts%C3%A4l%C3%A4"
FRANCE_PLAN = "https://www.verne.co/news/news-at-choose-france-ardian-and-verne-announce-plans-for-a-digital-infrastructure-campus-in-%C3%AEle-de-france-to-strengthen-europes-industrial-and-ai-capacity?hs_amp=true"
TENSIO_NORWAY = "https://www.tensio.no/no/proff/nyheter-proff/dette-er-de-nye-storforbrukerne-av-strom-i-midt-norge"
STJORDAL_PLANS = "https://www.stjordal.kommune.no/tjenester/plan-miljo-bygg-kart-og-eiendom/reguleringsplaner/medvirkning-og-horing/vedtatte-reguleringsplaner-og-planprogram/"
LAUVASEN_PLAN = "https://www.stjordal.kommune.no/_f/p3/i4007e4c1-27e7-47f2-8f7e-cba9d3cf27c7/5008-planbeskrivelse_13092024.pdf"
NORWAY_CONTEXT = "https://trondelageuropeanoffice.no/2026/04/lauvasen-naeringspark-blir-en-del-av-trondelag-europakontor/"
NSCALE = "https://www.verne.co/news/news-verne-and-nscale"
ACCOUNTS_FY2025 = "https://find-and-update.company-information.service.gov.uk/company/14551205/filing-history/MzUyNzI0ODY2NWFkaXF6a2N4/document?download=1&format=pdf"
ACCOUNTS_INDEX = "https://find-and-update.company-information.service.gov.uk/company/14551205/filing-history"
ARDIAN_ACQUISITION = "https://www.ardian.com/sites/default/files/2024-03/Press%20release%20Verne%2020240315.pdf"
D9_SALE = "https://www.investegate.co.uk/announcement/rns/digital-9-infrastructure-npv--dgi9/verne-global-sale-completion/8089329"


def facility(
    code: str,
    name: str,
    country_code: str,
    location: str,
    address: str,
    lifecycle: str,
    published_capacity: dict,
    *,
    area: dict | None = None,
    engineering: dict | None = None,
    ownership: str,
    conflicts: list[str] | None = None,
    sources: list[str],
) -> dict:
    return {
        "id": f"verne_{code}",
        "object_type": "DataCenterFacilityEvidence",
        "operator_or_project_name": name,
        "country_code": country_code,
        "location": location,
        "address_as_published": address,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "ownership_or_transaction_boundary": ownership,
        "published_capacity": published_capacity,
        "published_area_context": area or {},
        "power_and_cooling_evidence": engineering or {},
        "physical_GPU_or_accelerator_inventory": "No Verne-owned inventory is established; customer deployment evidence is retained at group-summary scope.",
        "publication_conflicts": conflicts or [],
        "capacity_counting_rule": "Published MW may be installed, site-card, substation, grid-request, construction-phase or master-plan capacity. It is never treated as live, leased, utilized, billed or additive without an explicit source bridge.",
        "source_urls": list(dict.fromkeys(sources)),
    }


FACILITIES = [
    facility(
        "iceland_keflavik",
        "Verne Iceland campus",
        "IS",
        "Keflavik / Reykjanesbær",
        "Valhallarbraut 868, 262 Reykjanesbær, Iceland",
        "retained_operating",
        {
            "campus_capacity_mw_more_than": 140,
            "new_substation_initial_operational_mw": 120,
            "new_substation_planned_total_by_end_2026_mw": 240,
            "boundary": "The campus envelope and substation supply scopes are not added and neither is actual IT draw.",
        },
        area={"campus_acres": 40, "campus_hectares": 16, "new_substation_sqm": 1500, "site_history": "former_NATO_base"},
        engineering={
            "rack_height_U": 52,
            "resilience": "Tier_III_equivalent_provider_wording",
            "certification": "NVIDIA_DGX_authorised",
            "electricity": "100_percent_renewable_geothermal_and_hydro_provider_claim",
            "campus_feeds": "dual_33kV_transmission_feeds_on_diverse_routes",
            "generators": "2N",
            "UPS": "2N",
            "cooling": "year_round_free_cooling_N_plus_2_and_direct_liquid_cooling_enabled",
            "fire_protection": ["VESDA", "gas_or_high_pressure_mist"],
            "new_substation": "11kV_switchgear_room_integrated_control_centre_high_voltage_hall_flood_protected_transformer_rooms_cable_basement_sprinkler_and_pump_systems",
        },
        ownership="Retained Verne operating campus; no site sale identified.",
        conflicts=[
            "The substation article index and page metadata disagree between 2026-05-20 and 2025-05-19; both are preserved as a source-date conflict.",
            "The article contains an unresolved 'approximately 1,600 [insert unit]' cable placeholder, so no cable unit is inferred.",
        ],
        sources=[ICELAND, ICELAND_DATASHEET, ICELAND_SUBSTATION, NSCALE, ACCOUNTS_FY2025],
    ),
    facility(
        "helsinki_vantaa",
        "Verne Helsinki campus",
        "FI",
        "Vantaa / Helsinki region",
        "Mittalinja 1, FIN-01260 Vantaa, Finland",
        "retained_operating",
        {"overall_campus_capacity_mw": 70, "FY2025_expansion_under_construction_mw": 11.7, "Q4_2025_hyperscale_contract_mw": 2.6},
        area={"published_campus_sqm": 15000, "new_buildings_planned": 2},
        engineering={
            "rack_height_U": 62,
            "resilience": "Tier_III_equivalent_provider_wording",
            "certification": "NVIDIA_DGX_authorised",
            "electricity": "100_percent_renewable_wind_provider_claim",
            "utility_feeds": "two_separate_20kV_feeds_on_diverse_routes",
            "UPS_and_generators": "cell_based_N_plus_1",
            "cooling": "indirect_free_cooling_with_rotating_heat_exchanger_N_plus_1",
            "liquid_cooling": "enabled_for_new_buildings",
            "heat_reuse": "district_heating",
            "backup_fuel": "HVO",
        },
        ownership="Retained Verne operating campus with disclosed expansion.",
        conflicts=["FY2025 accounts targeted H1 2026 completion for the 11.7MW expansion, but a later reviewed acceptance or live-load confirmation was not found."],
        sources=[HELSINKI_DATASHEET, HELSINKI_EXPANSION, ACCOUNTS_FY2025],
    ),
    facility(
        "pori_the_rock",
        "Pori The Rock",
        "FI",
        "Pori",
        "Exact current street address not established in reviewed sources",
        "divested_2026_02_02",
        {"legacy_site_capacity_mw": 11},
        area={"legacy_site_sqm": 8500, "underground_tunnel_halls": 9, "solar_plant_sqm": 2600, "site_history": "former_Finnish_Defence_Forces"},
        engineering={
            "utility_feeds": "two_20kV_feeds",
            "generators": "2N",
            "UPS": "N_plus_1_or_2N_by_service_scope",
            "cooling": "direct_free_cooling_N_plus_1_and_direct_liquid_cooling_in_operation",
            "electricity": "wind_and_solar_provider_claim",
            "backup_fuel": "HVO_transition",
        },
        ownership="Sold with Tampere and the managed private-cloud operation; FY2025 accounts state completion on 2026-02-02 and a USD17.4m disposal gain.",
        sources=[PORI_DATASHEET, FINLAND_SALE, ACCOUNTS_FY2025],
    ),
    facility(
        "tampere_the_deck",
        "Tampere The Deck",
        "FI",
        "Tampere",
        "Pakkahuoneenaukio 2a, FIN-33100 Tampere, Finland",
        "divested_2026_02_02",
        {"legacy_site_capacity_mw": 0.5},
        area={"legacy_site_sqm": 400, "data_halls": 2},
        engineering={
            "rack_height_U": 42,
            "resilience": "Tier_III_equivalent_provider_wording",
            "electricity": "100_percent_renewable_provider_claim",
            "utility_feeds": "two_separate_20kV_feeds_on_diverse_routes",
            "generators": "backup_generation_configuration_undisclosed",
            "UPS": "N_plus_1",
            "cooling": "indirect_free_cooling_N_plus_1_with_CRAC",
            "fire_protection": ["VESDA", "gas_suppression"],
        },
        ownership="Sold with Pori and the managed private-cloud operation; FY2025 accounts state completion on 2026-02-02.",
        sources=[TAMPERE_DATASHEET, FINLAND_SALE, ACCOUNTS_FY2025],
    ),
    facility(
        "london_volta",
        "London Volta / Great Sutton Street",
        "GB",
        "Central London",
        "Great Sutton Street, London, United Kingdom",
        "definitive_sale_agreement_currently_operated_by_verne_pending_close_confirmation",
        {"facility_capacity_mw": 6},
        area={"carriers_more_than": 40, "cross_connects_more_than": 1200},
        engineering={"carrier_neutral": True, "complete_current_as_built_power_and_cooling_BOM": "undisclosed"},
        ownership="Arcus announced a definitive 100% acquisition agreement on 2026-07-02 and described the site as currently operated by Verne. No reviewed closing confirmation was found by 2026-07-19.",
        conflicts=["Verne's current directory replaces the London facility card with a UK headquarters entry, while Arcus still calls the facility Verne-operated pending transaction completion."],
        sources=[DIRECTORY, ARCUS_NEWS, ACCOUNTS_FY2025],
    ),
    facility(
        "mantsala_kapuli",
        "Verne Mäntsälä campus",
        "FI",
        "Kapuli, Mäntsälä",
        "Kapuli industrial area, exact parcel undisclosed",
        "under_construction",
        {"initial_phase_mw": 70},
        area={"site_hectares": 10},
        engineering={"electricity": "renewable_provider_claim", "heat_reuse": "planned", "power_partner": "Nivos", "complete_equipment_BOM": "undisclosed"},
        ownership="Verne Mantsala Oy project; foundation-stone and construction-start announcement dated 2026-06-17.",
        conflicts=["An older timetable anticipated a mid-2025 start and roughly two-year build; the reviewed construction-start evidence moved to June 2026."],
        sources=[DIRECTORY, MANTSALA_BUILD, ACCOUNTS_FY2025],
    ),
    facility(
        "ile_de_france",
        "Verne Île-de-France campus",
        "FR",
        "Île-de-France",
        "Exact site and parcel undisclosed",
        "planned",
        {"masterplan_mw": 500, "initial_capacity_by_2030_mw_more_than": 200},
        area={"investment_eur_billion_up_to": 5},
        engineering={"grid_and_energy_collaboration": ["RTE", "EDF"], "ecosystem_collaboration": ["Bouygues", "Credit_Agricole"], "complete_design_and_equipment_BOM": "undisclosed"},
        ownership="Ardian and Verne plan; announcement does not establish an operating, permitted, financed or contracted facility.",
        sources=[DIRECTORY, FRANCE_PLAN],
    ),
    facility(
        "norway_stjordal_lauvasen",
        "Verne Norway / Lauvåsen",
        "NO",
        "Stjørdal / Lauvåsen",
        "Lauvåsen Næringspark planning area; exact parcel undisclosed",
        "planned",
        {"grid_connection_request_in_capacity_queue_mw": 180},
        area={"municipal_plan_id": 5008, "municipal_plan_approved": "2026-02-26"},
        engineering={"heat_reuse": "ambition", "planning_concept_only": ["diesel_backup", "external_cooling_machines"], "complete_project_design_and_equipment_BOM": "undisclosed"},
        ownership="Verne Norway AS project described as coming soon; the 180MW value is a queued grid request, not secured, approved, energized or operating capacity.",
        conflicts=["The municipal plan mentions halls up to 160,000sqm and generic equipment concepts, but these are planning possibilities rather than a disclosed Verne build specification."],
        sources=[DIRECTORY, TENSIO_NORWAY, STJORDAL_PLANS, LAUVASEN_PLAN, NORWAY_CONTEXT],
    ),
]


OSM_CROSSWALK = {
    "osm_relation_17995325": ("verne_iceland_keflavik", "campus_container"),
    "osm_way_35973807": ("verne_iceland_keflavik", "building_footprint_with_historical_start_date"),
    "osm_way_35973808": ("verne_iceland_keflavik", "building_footprint_with_historical_start_date"),
    "osm_way_26933574": ("verne_helsinki_vantaa", "named_operating_building_footprint"),
    "osm_way_33503496": ("verne_london_volta", "named_transitional_building_footprint"),
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
        "retained_operating": 2,
        "divested_2026_02_02": 2,
        "definitive_sale_agreement_currently_operated_by_verne_pending_close_confirmation": 1,
        "under_construction": 1,
        "planned": 2,
    }
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
            "capacity_counting_rule": "Geometry is a crosswalk only and contributes no additional site or capacity count.",
        })
    assert len(rows) == 5
    assert sum(row["raw_operator"] == "Verne Global" for row in rows) == 4
    assert sum(row["raw_operator"] is None for row in rows) == 1
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sources = list(dict.fromkeys([
        DIRECTORY, ICELAND, ICELAND_DATASHEET, ICELAND_SUBSTATION, HELSINKI_DATASHEET,
        HELSINKI_EXPANSION, PORI_DATASHEET, TAMPERE_DATASHEET, FINLAND_SALE, ARCUS_NEWS,
        MANTSALA_BUILD, FRANCE_PLAN, TENSIO_NORWAY, STJORDAL_PLANS, LAUVASEN_PLAN,
        NORWAY_CONTEXT, NSCALE, ACCOUNTS_FY2025, ACCOUNTS_INDEX, ARDIAN_ACQUISITION, D9_SALE,
    ]))
    return {
        "id": "verne_official_facility_summary_2026_07_19",
        "operator": "Verne",
        "legal_entity_boundary": "Jules_I_Limited_consolidated_Verne_group_with_discontinued_Finland_cloud_and_site_operation_separated",
        "accessed_on": accessed_on,
        "current_roster_and_lifecycle": {
            "registry_records": len(records),
            "lifecycle_counts": dict(sorted(Counter(row["lifecycle_as_of_2026_07_19"] for row in records).items())),
            "retained_operating_campuses": ["Iceland_Keflavik", "Finland_Helsinki_Vantaa"],
            "completed_divestments": ["Pori_The_Rock", "Tampere_The_Deck"],
            "signed_sale_pending_close_confirmation": "London_Volta",
            "under_construction": "Mantsala_70MW_initial_phase",
            "planned": ["Ile_de_France_500MW_masterplan", "Norway_Stjordal_180MW_grid_request_in_queue"],
        },
        "capacity_scope_reconciliation": {
            "FY2025_installed_operational_capacity_mw": 52.3,
            "FY2024_installed_operational_capacity_mw": 51.0,
            "FY2025_average_occupancy_percent": 94,
            "Iceland_campus_envelope_mw_more_than": 140,
            "Iceland_substation_initial_operational_mw": 120,
            "Iceland_substation_planned_total_by_end_2026_mw": 240,
            "Helsinki_campus_envelope_mw": 70,
            "FY2025_Helsinki_expansion_under_construction_mw": 11.7,
            "Mantsala_initial_construction_mw": 70,
            "France_masterplan_mw": 500,
            "Norway_grid_request_in_queue_mw": 180,
            "boundary": "52.3MW is the audited year-end installed operating denominator across the then Iceland, Finland and UK perimeter. Site-card, substation, build-phase, master-plan and grid-queue values are not added or treated as live load.",
        },
        "retained_site_power_and_cooling": {
            "Iceland": records[0]["power_and_cooling_evidence"],
            "Helsinki": records[1]["power_and_cooling_evidence"],
            "boundary": "Provider topology is design or current-site evidence, not a full as-built OEM, model, count, loading, acceptance and remaining-life ledger.",
        },
        "legacy_divested_site_engineering": {
            "Pori": records[2]["power_and_cooling_evidence"],
            "Tampere": records[3]["power_and_cooling_evidence"],
            "boundary": "These specifications describe legacy Verne scope and are not attributed to the retained July 2026 fleet.",
        },
        "AI_and_accelerator_boundary": {
            "Nscale_agreement_date": "2025-11-20",
            "Iceland_contract_mw": 15,
            "approximate_NVIDIA_Blackwell_Ultra_GPUs_planned_for_deployment_through_2026": 4600,
            "cooling_share_percent": {"liquid_cooled": 85, "air_cooled": 15},
            "related_hardware_wording": "GB300_in_separate_Verene_article_and_peak_120kW_per_rack_context",
            "ownership": "customer_Nscale_deployment; Verne-owned inventory not established",
            "delivery_state_as_of_2026_07_19": "exact_delivered_installed_accepted_and_operating_count_undisclosed",
            "boundary": "Approximately 4,600 is a signed deployment plan over 2026, not a current inventory audit. Contract MW is not added to campus capacity and no GPU revenue or margin is inferred.",
        },
        "FY2025_audited_consolidated_USD_thousand": {
            "reporting_parent": "Jules_I_Limited_company_14551205",
            "period": "year_ended_2025_12_31",
            "comparator_boundary": "FY2024_comparator_covers_2024_03_14_to_2024_12_31_only",
            "total_revenue_including_discontinued": 172900,
            "continuing_revenue": 161454,
            "continuing_operating_loss": -2382,
            "acquisition_and_other_investment_costs": 9657,
            "finance_costs": 51019,
            "continuing_loss_before_tax": -60447,
            "continuing_net_loss": -36549,
            "discontinued_profit": 2409,
            "group_net_loss": -34140,
            "EBITDA_including_continuing_and_discontinued": 105700,
            "continuing_segment_EBITDA": 101291,
            "segment": {
                "Iceland": {"revenue": 135599, "EBITDA": 111062},
                "Finland_continuing": {"revenue": 6014, "EBITDA": -360},
                "UK": {"revenue": 19841, "EBITDA": 6717},
                "rest_of_world": {"EBITDA": -855},
                "central_administration": {"EBITDA": -15273},
            },
            "continuing_revenue_mix": {"colocation": 26703, "power": 17220, "support": 3862, "IaaS": 69765, "lease_income": 43903},
            "operating_cash_flow": 60184,
            "cash_capex_PPE": 117520,
            "accounting_PPE_additions": 133217,
            "contracted_capital_commitments": 47121,
            "assets": 1007783,
            "PPE": 745575,
            "cash": 19861,
            "restricted_cash": 13467,
            "borrowings": 692096,
            "debt_including_leases_and_held_for_sale": 696397,
            "net_debt": 676536,
            "equity": 55490,
            "net_debt_to_equity_times": 12.2,
            "contract_liabilities_total": 181772,
            "boundary": "EBITDA is not accounting operating profit or cash flow. Total revenue includes discontinued operations; continuing and segment measures are retained separately.",
        },
        "financing_and_ownership": {
            "owner": "Ardian_infrastructure_funds_private",
            "direct_public_security": "none",
            "Ardian_committed_expansion_capital_USD_billion_up_to": 1.2,
            "Facility_A_USD_million": {"drawn": 135, "margin": "SOFR_plus_3_percent", "maturity": 2029},
            "Facility_B_EUR_million": {"total": 250, "drawn": 134.3, "margin": "SOFR_or_EURIBOR_plus_3_percent"},
            "Facility_C_EUR_million": {"total": 25, "drawn": 0},
            "Facility_D_EUR_million": {"total": 130, "drawn": 0, "added": "2025-12-19"},
            "Jules_II_parent_loan_USD_thousand": {"carrying_value": 401944, "fixed_rate_percent": 9.42, "maturity": 2039},
            "covenants_at_2025_12_31": "passed",
            "loss_sensitivity_to_100bp_USD_million": 2.6,
            "IFRS_acquisition_consideration_USD_thousand": 399043,
            "IFRS_goodwill_USD_thousand": 80865,
            "D9_sale_max_equity_price_USD_million": 575,
            "D9_price_components_USD_million": {"initial": 415, "deferred": 25, "earnout_up_to": 135},
            "April_2026_early_settlement_GBP_million": 10,
            "boundary": "IFRS purchase consideration, the D9 maximum transaction price and the later GBP10m settlement use different accounting and transaction scopes and are not treated as additive.",
        },
        "sustainability": {
            "FY2025_energy_GWh": {"Iceland": 181.300, "Finland": 21.912, "UK": 28.575, "total": 231.787},
            "FY2025_PUE": {"Iceland": 1.2, "Finland_excluding_heat_reuse": 1.39, "UK": 1.5},
            "FY2025_tCO2e": {"scope_1": 119.59, "scope_2_market_based": 7.82, "scope_1_plus_2_market_based": 127.41, "scope_2_location_based": 7244.46},
            "power_claim_boundary": "Nordic sites claim 100% renewable supply. The broader low-carbon mix can include nuclear in the UK and is not simplified to all-renewable or hourly carbon-free operation.",
            "HVO": "used_in_Finland_and_introduced_in_UK_in_2025_with_reported_94_percent_scope_1_reduction",
            "water_and_WUE": "not_disclosed_in_current_group_accounts",
        },
        "Finland_discontinued_operation_USD_thousand": {
            "perimeter": "managed_private_cloud_platform_plus_Pori_and_Tampere_not_site_only_economics",
            "revenue": 11408,
            "operating_profit": 3035,
            "net_profit": 2409,
            "operating_cash_flow": 4402,
            "held_for_sale_assets": 24034,
            "held_for_sale_liabilities": 3946,
            "disposal_gain": 17400,
            "sale_completed": "2026-02-02",
        },
        "OSM_crosswalk": {
            "rows": osm_rows,
            "all_related_objects": len(osm_rows),
            "raw_operator_tagged_objects": 4,
            "name_only_campus_relation": 1,
            "distinct_facility_records_crosswalked": 3,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "The Iceland campus relation and two building ways are one campus. OSM geometry is partial map evidence, not an eight-record facility census or capacity source.",
        },
        "outlook": {
            "positive_signals": [
                "94_percent_FY2025_average_occupancy_on_52_3MW_installed_capacity",
                "FY2025_total_revenue_172_9m_and_EBITDA_105_7m",
                "15MW_approximately_4600_Blackwell_Ultra_customer_deployment_through_2026",
                "Helsinki_expansion_and_Mantsala_70MW_initial_build",
                "France_500MW_and_Norway_180MW_optional_pipeline",
                "Ardian_up_to_1_2bn_expansion_commitment_and_undrawn_Facilities_C_and_D",
            ],
            "risk_signals": [
                "net_debt_676_5m_and_12_2_times_net_debt_to_equity",
                "finance_costs_51_0m_operating_loss_and_group_net_loss",
                "installed_capacity_much_smaller_than_mixed_pipeline_headlines",
                "Norway_grid_queue_France_site_and_permitting_and_Mantsala_schedule_delivery_risk",
                "Iceland_and_IaaS_revenue_concentration",
                "private_owner_no_direct_public_security_and_opaque_current_valuation",
                "customer_GPU_ownership_delivery_state_and_economics_incomplete",
                "Pori_Tampere_and_London_transactions_change_the_reporting_perimeter",
            ],
            "analytical_view": "Verne has a scarce Nordic low-carbon and high-density platform with high occupancy and credible AI demand. Its expansion option is large, but current installed capacity is modest beside the pipeline and leverage is high. The investable exposure is private through Ardian, so public investors should primarily use Verne as demand evidence for power, grid, cooling and accelerator suppliers rather than as a directly purchasable pure play.",
        },
        "remaining_material_gaps": [
            "exact_current_retained_building_roster_legal_title_lease_and_site_to_subsidiary_bridge",
            "per_site_operating_energized_leased_customer_accepted_utilized_billed_and_actual_IT_load",
            "per_site_as_built_grid_transformer_switchgear_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life",
            "current_Nscale_Blackwell_Ultra_delivered_installed_accepted_operating_count_owner_rack_fabric_power_utilization_revenue_and_margin",
            "Helsinki_11_7MW_expansion_and_2_6MW_contract_acceptance_live_load_and_revenue_start",
            "London_Arcus_transaction_close_price_debt_and_post_close_reporting_perimeter",
            "Mantsala_permits_grid_financing_customer_contract_construction_schedule_and_acceptance",
            "France_exact_site_land_permit_grid_financing_customer_and_phased_delivery",
            "Norway_grid_request_outcome_exact_site_permit_financing_customer_and_design",
            "site_level_revenue_operating_profit_cash_flow_capex_debt_ROIC_customer_concentration_and_contract_pricing",
            "current_enterprise_value_Ardian_fund_economics_and_exit_terms",
            "current_WUE_absolute_water_hourly_matching_and_per_site_emissions",
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
    registry = args.output_dir / "verne_official_facility_registry.jsonl"
    summary_path = args.output_dir / "verne_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
