#!/usr/bin/env python3
"""Build a scope-safe Leading Edge Data Centres facility registry.

The current provider network exposes six operating New South Wales facility
cards.  Older releases describe a much larger regional rollout and standard
30- or 75-rack modules, while newer Australian business-name registrations
signal an AI-oriented brand direction.  This builder keeps those scopes apart:
current card capacity is not rack inventory, historical rollout plans are not
operating sites, AI readiness is not physical GPU ownership, and investor or
parent-portfolio figures are not LEDC standalone financials.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


NETWORK = "https://leadingedgedc.com/network-map/"
NEWCASTLE = "https://leadingedgedc.com/dc_location/newcastle/"
TAMWORTH = "https://leadingedgedc.com/dc_location/tamworth/"
DUBBO = "https://leadingedgedc.com/dc_location/dubbo/"
ALBURY = "https://leadingedgedc.com/dc_location/albury/"
COFFS = "https://leadingedgedc.com/dc_location/coffs-harbour/"
WAGGA = "https://leadingedgedc.com/dc_location/wagga-wagga/"
NEWCASTLE_OPEN = "https://leadingedgedc.com/news_post/eading-edge-data-centre-opens-doors-in-newcastle-nsw/"
TAMWORTH_OPEN = "https://leadingedgedc.com/news_post/tamworth-data-centre-grand-opening/"
DUBBO_OPEN = "https://leadingedgedc.com/news_post/ledc-opens-dubbo-press-release/"
ALBURY_LEASE = "https://leadingedgedc.com/news_post/lease-signed-for-albury-wodonga-edge-data-centre/"
COFFS_DA = "https://leadingedgedc.com/news_post/da-lodged-for-a-1m-data-centre-at-coffs-harbour-airport-enterprise-parkl5tsbvakqa1qttmpbjt1nk81ceo52b/"
COFFS_BUILD = "https://leadingedgedc.com/news_post/leading-edge-dc-breaks-ground-in-coffs-harbour/"
WAGGA_HISTORY = "https://leadingedgedc.com/news_post/prime7-news-in-wagga-wagga/"
SCHNEIDER_CASE = "https://www.se.com/au/en/work/campaign/customer-stories/leading-edge/"
SCHNEIDER_PROGRAM = "https://leadingedgedc.com/news_post/ecosystm-schneider-electric-partners-with-australias-leading-edge-data-centres/"
CISCO = "https://leadingedgedc.com/news_post/leading-edge-data-centres-cisco-deal/"
DCI = "https://leadingedgedc.com/data-centre-interconnect/"
SUSTAINABILITY = "https://leadingedgedc.com/sustainability/"
TIER_READY = "https://leadingedgedc.com/blog_post/tier-ready-a-new-way-to-deliver-data-centres/"
ABOUT = "https://leadingedgedc.com/about/"
TERMS = "https://leadingedgedc.com/terms-and-conditions/"
ABN = "https://abr.business.gov.au/ABN/View/55632303827"
WHSP_FUNDING = "https://leadingedgedc.com/news_post/welcome-aboard-jarrett-appleby-as-senior-advisor/"
DIGITALBRIDGE_FUNDING = "https://www.datacenterdynamics.com/en/news/australias-leading-edge-data-centres-raises-au30-million-from-digitalbridge/"
WHSP_FY2025 = "https://www.datocms-assets.com/104850/1759808456-whsp-holdings-limited-fy25-annual-report.pdf"
IAAS_BROCHURE = "https://leadingedgedc.com/wp-content/uploads/2022/12/LEDC_IaaS_Final_Dec22.pdf"


COMMON_POWER = {
    "supply_redundancy": "N_plus_1",
    "rack_power_topology": "2N_A_and_B",
    "backup_generation": "redundant_1000_kVA_diesel_generators",
    "UPS": "present",
    "distribution": "isolated_parallel_bus",
}

COMMON_COOLING = {
    "technology": "in_row_direct_expansion",
    "redundancy": "N_plus_1_independent_cooling",
    "airflow": "hot_aisle_containment",
    "controls": ["temperature_and_humidity_monitoring", "dehumidification", "filtration"],
}


def facility(
    code: str,
    city: str,
    card_url: str,
    capacity_kw: int,
    available_m2: int,
    module_it_kw: int,
    cameras: str,
    history_urls: list[str],
    *,
    lifecycle_detail: str,
    network_note: str | None = None,
    conflicts: list[str] | None = None,
) -> dict:
    return {
        "id": f"leading_edge_{code.lower()}",
        "name": code,
        "city": city,
        "state": "NSW",
        "country_code": "AU",
        "lifecycle_as_of_2026_07_19": "operating_current_provider_card",
        "lifecycle_detail": lifecycle_detail,
        "published_card_metrics": {
            "total_site_capacity_kw": capacity_kw,
            "total_m2_available": available_m2,
            "IT_load_per_module_kw": module_it_kw,
            "rack_count_current_card": "undisclosed",
            "power_term": "total_site_capacity_provider_wording",
        },
        "electrical_and_backup_power_evidence": dict(COMMON_POWER),
        "cooling_evidence": dict(COMMON_COOLING),
        "network_evidence": {
            "redundancy": "N_plus_1",
            "provider_network_availability_SLA_percent": 99.95,
            "layer_2_service_range": "100_Mbps_to_100_Gbps",
            "internet_or_transit_up_to_Gbps": 100,
            "note": network_note or f"Provider card says dark fibre connects to the {city} NBN POI.",
        },
        "security_evidence": {
            "camera_wording": cameras,
            "design": "SCEC_Zone_2",
            "framework": "Australian_Government_PSPF",
        },
        "certification_evidence": {
            "facility_card_wording": "Tier_Design_Tier_III",
            "portfolio_sustainability_page_wording": "each_DC_completed_ISO27001_and_Tier_III_certified",
            "independent_facility_specific_award_captured_in_review": False,
        },
        "physical_GPU_or_accelerator_inventory": "undisclosed",
        "publication_conflicts": conflicts or [],
        "boundary": "The provider's total-site-capacity and module-IT-load fields are retained as published. They do not establish installed rack count, energized or utilized IT load, customer acceptance, revenue, site economics or physical GPU inventory.",
        "source_urls": list(dict.fromkeys([card_url, *history_urls, SCHNEIDER_CASE, DCI, SUSTAINABILITY])),
    }


FACILITIES = [
    facility(
        "NTL1", "Newcastle", NEWCASTLE, 1500, 1160, 375, "30_plus",
        [NEWCASTLE_OPEN],
        lifecycle_detail="Current card is marketed as operating; provider opening material describes the first LEDC facility and a historical 75-rack design.",
    ),
    facility(
        "TMW1", "Tamworth", TAMWORTH, 375, 290, 375, "30_plus",
        [TAMWORTH_OPEN],
        lifecycle_detail="Current card is marketed as operating; the provider records a 5 November 2021 grand opening.",
    ),
    facility(
        "DBO1", "Dubbo", DUBBO, 750, 580, 375, "30_plus",
        [DUBBO_OPEN],
        lifecycle_detail="Current card is marketed as operating; the provider says the third regional facility opened on 10 December 2021 and was announced on 13 December 2021.",
    ),
    facility(
        "ABX1", "Albury", ALBURY, 750, 580, 375, "30_plus",
        [ALBURY_LEASE],
        lifecycle_detail="Current card is marketed as operating. The reviewed first-party historical page establishes the earlier lease but does not provide a current rack count.",
    ),
    facility(
        "CFS1", "Coffs_Harbour", COFFS, 300, 212, 150, "9_plus",
        [COFFS_DA, COFFS_BUILD],
        lifecycle_detail="Current card is marketed as operating. Historical provider pages cover the Airport Enterprise Park development and construction, not current utilization.",
    ),
    facility(
        "WGA1", "Wagga_Wagga", WAGGA, 300, 212, 150, "9_plus",
        [WAGGA_HISTORY],
        lifecycle_detail="Current card is marketed as operating; the reviewed historical provider page was a plan-stage report.",
        network_note="The Wagga Wagga card says dark fibre connects to the Coffs Harbour NBN POI; this appears to be provider copy carry-over and is not silently corrected.",
        conflicts=["The Wagga Wagga facility page names the Coffs Harbour NBN POI rather than a Wagga Wagga POI."],
    ),
]


OSM_CROSSWALK = {
    "osm_way_1441548716": "leading_edge_ntl1",
    "osm_way_1248945224": "leading_edge_tmw1",
    "osm_way_1441548719": "leading_edge_dbo1",
    "osm_way_1441547266": "leading_edge_abx1",
    "osm_way_1441548723": "leading_edge_cfs1",
    "osm_way_1150357328": "leading_edge_wga1",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    rows = [{"object_type": "DataCenterFacilityEvidence", "source_order": order, "accessed_on": accessed_on, **row} for order, row in enumerate(FACILITIES, 1)]
    assert len(rows) == 6
    assert len({row["id"] for row in rows}) == 6
    assert sum(row["published_card_metrics"]["total_site_capacity_kw"] for row in rows) == 3975
    assert sum(row["published_card_metrics"]["total_m2_available"] for row in rows) == 3034
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, facility_ref in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "facility_ref": facility_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "classification": "exact_current_provider_facility_candidate",
            "capacity_counting_rule": "OSM geometry is a crosswalk, not a capacity, ownership, lifecycle, utilization, revenue or GPU source.",
        })
    assert len(rows) == 6
    assert {row["raw_operator"] for row in rows} == {"Leading Edge Data Centres", "Leading Edge Data Centre"}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sources = list(dict.fromkeys([
        NETWORK, NEWCASTLE, TAMWORTH, DUBBO, ALBURY, COFFS, WAGGA,
        NEWCASTLE_OPEN, TAMWORTH_OPEN, DUBBO_OPEN, ALBURY_LEASE, COFFS_DA,
        COFFS_BUILD, WAGGA_HISTORY, SCHNEIDER_CASE, SCHNEIDER_PROGRAM, CISCO,
        DCI, SUSTAINABILITY, TIER_READY, ABOUT, TERMS, ABN, WHSP_FUNDING,
        DIGITALBRIDGE_FUNDING, WHSP_FY2025, IAAS_BROCHURE,
    ]))
    return {
        "id": "leading_edge_official_facility_summary_2026_07_19",
        "operator": "Leading Edge Data Centres",
        "legal_entity": "Edge Data Centres Pty Ltd",
        "accessed_on": accessed_on,
        "current_facility_scope": {
            "operating_provider_cards": 6,
            "facility_codes": [row["name"] for row in records],
            "state": "New_South_Wales",
            "total_site_capacity_card_checksum_mw": 3.975,
            "total_available_area_card_checksum_sqm": 3034,
            "derived_module_capacity_equivalent": 13,
            "derived_module_boundary": "Capacity divided by each card's 375-kW or 150-kW module field; this is an arithmetic check, not an installed physical-module count.",
            "current_card_rack_count": "undisclosed",
        },
        "historical_rollout_boundary": {
            "first_six_program_investment_with_Schneider_AUD_million": 30,
            "historical_racks_per_first_six_site": 75,
            "historical_power_density_kw_per_rack": 5,
            "historical_first_six_rack_plan_checksum": 450,
            "older_regional_plan_headlines": ["more_than_20", "26", "more_than_30"],
            "current_Victoria_and_Queensland_status_on_network_page": "coming_soon_without_current_facility_cards",
            "boundary": "The first-six rack design and older 20/26/30-plus rollout statements are historical program or service-network scopes. They do not prove current installed racks or operating facilities beyond the six NSW cards.",
        },
        "power_cooling_network_and_supplier_evidence": {
            "site_card_common_power": COMMON_POWER,
            "site_card_common_cooling": COMMON_COOLING,
            "Schneider_program_products": ["EcoStruxure_IT_Expert", "EcoStruxure_Asset_Advisor", "Power_Monitoring_Expert", "InRow_DX", "Galaxy_UPS", "APC_NetShelter_SX", "APC_metered_PDUs", "EcoAisle_containment"],
            "Cisco": "core_network_backbone_historical_program",
            "current_DCI": "redundant_wavelength_backbone_between_regional_data_centres",
            "boundary": "Named suppliers and product families establish program participation, not a current per-site as-built quantity, model, acceptance or remaining-life ledger.",
        },
        "sustainability_and_certification_boundary": {
            "solar_shield_provider_claimed_PUE_improvement": 0.3,
            "roof_mounted_on_site_solar": True,
            "net_zero_target": "before_2040_or_better",
            "transition_stage": 1,
            "provider_wording": "each_DC_completed_ISO27001_and_Tier_III_certified",
            "facility_cards": "Tier_Design_Tier_III",
            "Tier_Ready_model": True,
            "independent_facility_specific_Uptime_award_captured_in_review": False,
            "measured_fleet_or_site_PUE_WUE_water_energy_renewable_share_and_hourly_matching": "undisclosed",
            "boundary": "The sustainability page's certification wording and the Tier-Ready modular design are retained as provider evidence. No facility-specific independent award identifier was captured in the reviewed public sources, and absence from this review is not proof that no award exists.",
        },
        "AI_and_accelerator_boundary": {
            "new_business_names_registered_from_2026_03_11": ["AI_DATA_CENTRES", "AI_DC", "LEDC_AI"],
            "brand_direction_signal": "AI_oriented_business_names_without_a_reviewed_current_product_or_hardware_ledger",
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin": "undisclosed",
            "accelerator_ledger_action": "no_numeric_physical_inventory_row_created",
        },
        "legal_ownership_and_financial_boundary": {
            "ABN": "55_632_303_827",
            "ACN": "632_303_827",
            "legal_entity_status": "active_Australian_private_company",
            "current_named_investors": ["WHSP", "DigitalBridge"],
            "exact_current_investor_stakes_and_valuation": "undisclosed",
            "historical_funding_AUD_million": {"WHSP_2020": 20, "DigitalBridge_2022_equity_secondary_source": 30},
            "WHSP_FY2025_controlled_vehicle": "WHSP_Leading_Edge_Pty_Limited_100_percent_controlled_by_WHSP",
            "vehicle_boundary": "WHSP's control of its own investment vehicle does not establish 100% ownership of Edge Data Centres Pty Ltd, whose current site also names DigitalBridge as an investor.",
            "LEDC_standalone_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_and_ROIC": "undisclosed",
            "WHSP_FY2025_private_equity_portfolio_AUD_million": {"regular_net_loss_after_tax": -21.1, "statutory_net_loss_after_tax": -35.9, "contracted_investment_commitments": 158.4},
            "parent_portfolio_boundary": "WHSP Private Equity contains multiple holdings and is not allocated to LEDC revenue, profit, debt, capex or value.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm_rows),
            "raw_operator_labels": sorted({row["raw_operator"] for row in osm_rows}),
            "rows": osm_rows,
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Six OSM ways map to all six current provider cards. Operator-label spelling differs at Tamworth, and object footprints are not a rack, load or ownership census.",
        },
        "outlook": {
            "positive_signals": ["six_current_regional_NSW_facility_cards", "3_975_MW_card_capacity_checksum", "redundant_interconnected_edge_network", "Schneider_and_Cisco_supplier_history", "2026_AI_business_name_registrations"],
            "risk_signals": ["small_current_card_scale", "current_cards_concentrated_in_NSW", "Victoria_and_Queensland_still_coming_soon", "older_rollout_targets_not_delivered_as_current_cards", "no_physical_GPU_inventory", "no_standalone_financials_or_current_cap_table", "no_measured_site_efficiency_or_utilization"],
            "analytical_view": "LEDC is a real six-site regional edge platform with a modest published capacity base and an AI-oriented naming signal. Its investability cannot be ranked from public evidence because standalone earnings, current ownership percentages, utilization, expansion funding and physical accelerator deployment remain undisclosed.",
        },
        "remaining_material_gaps": [
            "current_non_overlapping_legal_building_title_lease_and_lifecycle_roster_beyond_six_cards",
            "current_installed_racks_modules_energized_leased_utilized_billed_and_actual_IT_load_by_site",
            "per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_and_cooling_BOM",
            "per_site_measured_PUE_WUE_water_energy_renewable_matching_and_live_liquid_cooled_MW",
            "facility_specific_current_Uptime_and_ISO_award_identifiers_scope_and_expiry",
            "physical_GPU_model_count_owner_host_site_delivery_fabric_power_utilization_revenue_and_margin",
            "standalone_revenue_operating_profit_EBITDA_cash_flow_capex_debt_customer_concentration_and_ROIC",
            "current_investor_stakes_valuation_governance_and_post_2026_AI_brand_strategy",
            "Victoria_Queensland_and_historical_NSW_pipeline_land_permit_grid_financing_construction_customer_and_launch_status",
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
    registry = args.output_dir / "leading_edge_official_facility_registry.jsonl"
    summary_path = args.output_dir / "leading_edge_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
