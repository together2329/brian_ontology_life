#!/usr/bin/env python3
"""Build a scope-preserving Cirion facility, OSM, engineering and finance registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


DIRECTORY_URL = "https://www.ciriontechnologies.com/en/data-center/our-data-centers/"
PLATFORM_URL = "https://www.ciriontechnologies.com/en/data-center/"
COMPUTE_URL = "https://www.ciriontechnologies.com/en/data-center/compute/"
SOC2_URL = "https://lp.ciriontechnologies.com/hubfs/Other%20Files/Cirion%20Documentation/Certifications/Data-center/ISAE/REG%20-%20ISAE3402-SOC%202-Tipo%20II%20-%202023%20%20-%20Resumen.pdf"
ESG2024_URL = "https://lp.ciriontechnologies.com/hubfs/Other%20Files/Downloadable%20Assets/Reports/cirion-reporte-esg-2024-eng.pdf"
HANDBOOK_URL = "https://www.ciriontechnologies.com/pt-br/customer-handbook-datacenter/"
REGULATORY_URL = "https://www.ciriontechnologies.com/en/resources/legal/regulatory/"
MAY2026_URL = "https://press.ciriontechnologies.com/en/2026/05/19/launches-network-as-a-service-latin-america-own-fiber/"
SAN2_CERT_URL = "https://press.ciriontechnologies.com/en/2026/04/29/cirion-technologies-achieves-tier-iii-design-certification-for-its-san2-data-center-in-chile/"
LIM2_CERT_URL = "https://press.ciriontechnologies.com/en/2025/07/10/tier-iii-certification-uptime-lim2-data-center-peru/"
RIO2_URL = "https://www.ciriontechnologies.com/en/data-center/our-data-centers/rio-de-janeiro-2/"
RIO2_ANNOUNCEMENT_URL = "https://press.ciriontechnologies.com/en/2024/08/01/cirion-ampliara-data-center-rio-de-janeiro/"
BUE1_EXPANSION_URL = "https://press.ciriontechnologies.com/en/2025/08/21/data-center-buenos-aires-digital-transformation-argentina/"
UPTIME_CLIENT_URL = "https://uptimeinstitute.com/uptime-institute-awards/client/cirion-technologies/1091"
S_AND_P_URL = "https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3517660"
LUMEN_SALE_URL = "https://ir.lumen.com/news/news-details/2022/Lumen-Closes-Sale-of-its-Latin-American-Business-to-Stonepeak/default.aspx"
TRANSACTION_URL = "https://press.ciriontechnologies.com/en/2022/01/08/2022-08-01-cirion-announces-its-transaction-close/"


LEGACY_18 = [
    ("BUE1", "Buenos_Aires", "Argentina"),
    ("MEN1", "Mendoza", "Argentina"),
    ("COR1", "Cordoba", "Argentina"),
    ("ROS1", "Rosario", "Argentina"),
    ("SAO1", "Sao_Paulo", "Brazil"),
    ("CUR1", "Curitiba", "Brazil"),
    ("RIO1", "Rio_de_Janeiro", "Brazil"),
    ("SAN1", "Santiago", "Chile"),
    ("BOG1", "Bogota", "Colombia"),
    ("BOG2", "Bogota", "Colombia"),
    ("CAL1", "Cali", "Colombia"),
    ("GUA1", "Guayaquil", "Ecuador"),
    ("QUI1", "Quito", "Ecuador"),
    ("QUI2", "Quito", "Ecuador"),
    ("LIM1", "Lima", "Peru"),
    ("CAR1", "Caracas", "Venezuela"),
    ("MEX1", "Mexico_City", "Mexico"),
    ("PAN1", "Panama_City", "Panama"),
]


SPEC_SHEETS = {
    "BOG2": {"slug": "bog2", "rack_FP": 713, "total_area_m2": 7745, "floor_area_m2": 4478, "power_label_MW": 7, "renewable_percent": 100, "colocation_m2": 2073, "cabinet_density_kW": 4.9, "utility_feeders": 5, "UPS": "distributed_N_plus_N_2N", "standby": "DC1_3x350kW_DC2_4x700kW_DC3_2x1100kW_DC4_2x1100kW_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1"},
    "BUE1": {"slug": "bue1", "rack_FP": 815, "total_area_m2": 5198, "floor_area_m2": 9788, "power_label_MW": 7, "renewable_percent": 25, "colocation_m2": 2541, "cabinet_density_kW": 7.6, "utility_feeders": 3, "UPS": "distributed_N_plus_N_2N", "standby": "1x1250kVA_3x1100kVA_4x650kVA_2x1875kVA_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1", "provider_area_anomaly": "floor_area_9788m2_exceeds_total_area_5198m2"},
    "CAR1": {"slug": "car1", "rack_FP": 300, "total_area_m2": 2159, "floor_area_m2": 8067, "power_label_MW": 2, "colocation_m2": 719, "cabinet_density_kW": 2.1, "utility_feeders": 1, "UPS": "distributed_N_plus_N_2N", "standby": "1x1850kVA_2x963kVA_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1", "provider_area_anomaly": "floor_area_8067m2_exceeds_total_area_2159m2"},
    "CUR1": {"slug": "cur1", "rack_FP": 119, "total_area_m2": 9111, "floor_area_m2": 2995, "power_label_MW": 1, "renewable_percent": 100, "colocation_m2": 662, "cabinet_density_kW": 6.0, "utility_feeders": 1, "UPS": "distributed_N_plus_1", "standby": "2x450kVA_diesel", "standby_redundancy": "N_plus_1", "cooling": "CRAC_N_plus_1"},
    "LIM1": {"slug": "lim1", "rack_FP": 609, "rack_FP_expansion_plan": 68, "total_area_m2": 2569, "floor_area_m2": 9606, "power_label_MW": 4, "renewable_percent": 100, "colocation_m2": 2218, "cabinet_density_kW": 4.9, "utility_feeders": 1, "UPS": "distributed_N_plus_N_2N", "standby": "2x1135kW_2x1007kW_1x945kW_3x910kW_1x900kW_1x835kW_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1", "provider_area_anomaly": "floor_area_9606m2_exceeds_total_area_2569m2"},
    "LIM2": {"slug": "lim2", "rack_FP": 1200, "total_area_m2": 25000, "floor_area_m2": 12000, "power_label_MW": 20, "renewable_percent": 100, "colocation_m2": 2844, "cabinet_density_kW": 9.8, "utility_feeders": 9, "UPS": "distributed_N_plus_N_2N_plus_2C", "standby": "6x2_1MW_DCC", "standby_redundancy": "N_plus_N_2N_plus_2C", "cooling": "spec_sheet_CRAC_N_plus_1_provider_page_says_liquid_cooling_capability", "rack_count_conflict": "spec_sheet_1200_FP_versus_2025_press_approximately_1440_racks"},
    "QUI2": {"slug": "qui2", "rack_FP": 100, "total_area_m2": 1225, "floor_area_m2": 1812, "power_label_MW": 1, "renewable_percent": 35, "colocation_m2": 265, "cabinet_density_kW": 4.0, "utility_feeders": 2, "UPS": "distributed_N_plus_1", "standby": "2x1500kVA_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1", "provider_area_anomaly": "floor_area_1812m2_exceeds_total_area_1225m2"},
    "RIO1": {"slug": "rio1", "rack_FP": 483, "total_area_m2": 7097, "floor_area_m2": 5112, "power_label_MW": 12, "renewable_percent": 100, "colocation_m2": 1787, "cabinet_density_kW": 8.0, "utility_feeders": 3, "UPS": "distributed_N_plus_1", "standby": "13x450kVA_diesel_plus_3x1500kW_DRUPS", "standby_redundancy": "N_plus_1", "cooling": "CRAC_N_plus_1"},
    "RIO2": {"slug": "rio2", "rack_FP": 880, "provider_IT_capacity_label": "81MW_plus_880_racks", "total_area_m2": 15055, "floor_area_m2": 6683, "power_label_MW": 60, "renewable_percent": 100, "colocation_m2": 3310, "cabinet_density_kW": 90, "current_page_rack_density_range_kW": "30_to_126", "platform_high_density_headline_kW_up_to": 140, "utility_feeders": 2, "UPS": "distributed_N_plus_N_2N_plus_2C", "standby": "six_units_rating_and_OEM_undisclosed", "standby_redundancy": "N_plus_N_2N_plus_2C", "cooling": "CRAC_plus_liquid_cooling_N_plus_1", "provider_capacity_anomaly": "IT_capacity_label_81MW_exceeds_separate_power_label_60MW_and_press_up_to_60MW"},
    "SAN1": {"slug": "san1", "rack_FP": 513, "total_area_m2": 9597, "floor_area_m2": 1491, "power_label_MW": 4, "renewable_percent": 100, "colocation_m2": 2037, "cabinet_density_kW": 3.2, "utility_feeders": 3, "UPS": "distributed_N_plus_1", "standby": "2x800kW_3x1250kW_2x1600kW_diesel", "standby_redundancy": "N_plus_1", "cooling": "CRAC_plus_chillers_N_plus_1"},
    "SAN2": {"slug": "san2", "rack_FP": 1200, "total_area_m2": 25000, "floor_area_m2": 9104, "power_label_MW": 20, "renewable_percent": 100, "colocation_m2": 2844, "cabinet_density_kW": 9.8, "utility_feeders": 9, "UPS": "distributed_N_plus_N_2N_plus_2C", "standby": "six_units_rating_and_OEM_undisclosed", "standby_redundancy": "N_plus_N_2N_plus_2C", "cooling": "spec_sheet_CRAC_N_plus_1_provider_page_says_liquid_cooling_installation_capability"},
    "SAO1": {"slug": "sao1", "rack_FP": 1154, "rack_FP_expansion_plan": 308, "total_area_m2": 19777, "floor_area_m2": 9826, "power_label_MW": 20, "renewable_percent": 100, "colocation_m2": 3663, "cabinet_density_kW": 4.6, "utility_feeders": "one_20MW", "UPS": "distributed_N_plus_N_2N", "standby": "2x1915kW_2x1400kW_7x1200kW_1x1136kW_2x360kW_5x280kW_diesel", "standby_redundancy": "N_plus_N_2N", "cooling": "CRAC_N_plus_1"},
}


CURRENT_CARD_CODES = ["BOG2", "BUE1", "CAR1", "CUR1", "LIM1", "LIM2", "QUI2", "RIO1", "RIO2", "SAN1", "SAN2", "SAO1"]
CURRENT_OPERATING_CARD_CODES = [code for code in CURRENT_CARD_CODES if code != "RIO2"]


OSM_CLASSIFICATION = {
    "osm_way_187344929": ("ROS1", "current_data_center_exact_address_and_city_match"),
    "osm_way_204971297": ("BUE1", "current_data_center_exact_address_and_city_match"),
    "osm_way_1472876782": ("Las_Toninas_cable_landing_station", "exclude_subsea_landing_station_from_data_center_facility_count"),
    "osm_way_1109152125": ("SAN1", "current_data_center_exact_address_and_city_match_name_only_OSM_row"),
    "osm_way_1413526741": ("LIM2", "current_data_center_exact_name_and_location_match_name_only_OSM_row"),
    "osm_node_13615091772": ("LIM1", "current_data_center_exact_name_and_location_match"),
}


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CLASSIFICATION:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CLASSIFICATION)
    return rows


def spec_url(code: str) -> str:
    slug = SPEC_SHEETS[code]["slug"]
    return f"https://lp.ciriontechnologies.com/hubfs/Other%20Files/Downloadable%20Assets/data-sheet-web/cirion-technologies-data-center-spec-sheet-{slug}-eng.pdf"


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for code, city, country in LEGACY_18:
        row = {
            "id": f"cirion_facility_{code.lower()}",
            "object_type": "ProviderDataCenterFacilityDisclosure",
            "operator": "Cirion_Technologies",
            "facility_code": code,
            "city": city,
            "country": country,
            "lifecycle": "operating_during_SOC2_period_2024_11_01_to_2025_10_31",
            "roster_source": SOC2_URL,
            "current_status_boundary": "The audited service description establishes a facility during its stated period. It is not a current ownership-title, capacity, utilization or site-economics statement.",
            "accessed_on": accessed_on,
        }
        if code in SPEC_SHEETS:
            row["current_provider_specification"] = SPEC_SHEETS[code]
            row["specification_source"] = spec_url(code)
        records.append(row)
    for code, city, country in [("LIM2", "Lima", "Peru"), ("SAN2", "Santiago", "Chile")]:
        records.append({
            "id": f"cirion_facility_{code.lower()}",
            "object_type": "ProviderDataCenterFacilityDisclosure",
            "operator": "Cirion_Technologies",
            "facility_code": code,
            "city": city,
            "country": country,
            "lifecycle": "recent_activation_reported_by_provider_May_2026",
            "current_provider_specification": SPEC_SHEETS[code],
            "specification_source": spec_url(code),
            "activation_source": MAY2026_URL,
            "boundary": "Activation wording supports a current facility label, but the published power and rack fields are design or capacity labels rather than live utilized load.",
            "accessed_on": accessed_on,
        })
    records.append({
        "id": "cirion_development_rio2",
        "object_type": "ProviderDataCenterDevelopmentDisclosure",
        "operator": "Cirion_Technologies",
        "facility_code": "RIO2",
        "city": "Rio_de_Janeiro",
        "country": "Brazil",
        "lifecycle": "planned_for_construction_or_presale_with_2026_launch_not_confirmed_operational",
        "current_provider_specification": SPEC_SHEETS["RIO2"],
        "specification_source": spec_url("RIO2"),
        "sources": [RIO2_URL, RIO2_ANNOUNCEMENT_URL, MAY2026_URL],
        "boundary": "The May 2026 provider release still calls RIO2 planned for construction and the current page says opening in 2026. No commissioning, acceptance or ready-for-service evidence was found, so RIO2 is excluded from current operating counts and capacity sums.",
        "accessed_on": accessed_on,
    })
    for osm_id, source in osm_rows.items():
        facility, classification = OSM_CLASSIFICATION[osm_id]
        records.append({
            "id": f"cirion_evidence_{osm_id}",
            "object_type": "OSMFacilityOrNetworkEvidence",
            "operator": "Cirion_Technologies",
            "OSM_ref": osm_id,
            "matched_facility_or_network_asset": facility,
            "classification": classification,
            "raw_operator": source.get("operator"),
            "raw_name": source.get("name"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "count_boundary": "OSM is location evidence, not proof of ownership, operating status, gross floor area, IT load or financial contribution. The Las Toninas landing station is excluded from compute-facility counts despite its telecom=data_center tag.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 27
    assert sum(r["object_type"] == "ProviderDataCenterFacilityDisclosure" for r in records) == 20
    assert sum(r["object_type"] == "ProviderDataCenterDevelopmentDisclosure" for r in records) == 1
    assert sum(r["object_type"] == "OSMFacilityOrNetworkEvidence" for r in records) == 6
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    specs = [SPEC_SHEETS[code] for code in CURRENT_OPERATING_CARD_CODES]
    return {
        "id": "cirion_data_center_summary_2026_07_19",
        "operator": "Cirion Technologies",
        "shareholders": ["Stonepeak_managed_funds", "AustralianSuper"],
        "accessed_on": accessed_on,
        "portfolio_scope_reconciliation": {
            "SOC2_period_end_2025_10_31_facility_roster": 18,
            "provider_2026_recent_activations": ["LIM2", "SAN2"],
            "identified_current_facility_label_floor": 20,
            "current_provider_featured_directory_cards": 12,
            "current_featured_operating_cards": 11,
            "current_featured_development_cards": ["RIO2"],
            "provider_2024_ESG": {"carrier_neutral_data_centers": 18, "under_construction": 3},
            "provider_August_2025": {"main_carrier_neutral_data_centers": 12, "under_construction": 3, "edge_data_centers": 10},
            "boundary": "The 18-row SOC2 roster plus two explicitly new activations yields a 20-label current evidence floor, not a claim that Cirion's current total is exactly 20. Featured main sites, edge sites, service-audit facilities, developments and construction counts use different scopes and are not added.",
        },
        "featured_operating_card_arithmetic_checksums_not_portfolio_totals": {
            "sites": CURRENT_OPERATING_CARD_CODES,
            "rack_FP": sum(s["rack_FP"] for s in specs),
            "total_area_m2": sum(s["total_area_m2"] for s in specs),
            "floor_area_m2": sum(s["floor_area_m2"] for s in specs),
            "power_label_MW": sum(s["power_label_MW"] for s in specs),
            "cards_where_floor_area_exceeds_total_area": ["BUE1", "CAR1", "LIM1", "QUI2"],
            "boundary": "These are source-integrity checks across eleven selected operating cards, not fleet totals, live IT load, usable floor area, sold capacity or additive valuation metrics. The four provider area inversions are preserved rather than silently corrected.",
        },
        "development_RIO2": {
            "land_m2_2024_announcement": 15000,
            "provider_spec_total_area_m2": 15055,
            "provider_spec_floor_area_m2": 6683,
            "provider_spec_power_label_MW": 60,
            "provider_spec_IT_capacity_label": "81MW_plus_880_racks",
            "provider_current_page_electrical_infrastructure_support_up_to_MW": 100,
            "modular_blocks_MW": 2,
            "rack_density": {"spec_sheet_kW": 90, "current_page_range_kW": "30_to_126", "platform_headline_up_to_kW": 140},
            "cooling": "CRAC_plus_liquid_cooling_N_plus_1_with_UPS_backed_CDUs_and_pumps",
            "lifecycle": "development_or_presale_not_confirmed_operational",
            "boundary": "The 60MW power, 81MW IT-capacity label and 100MW infrastructure-support statement conflict or use different denominators. They are not combined, and no live liquid-cooled MW or customer load is inferred.",
        },
        "OSM_crosswalk": {
            "operator_tagged_objects": 4,
            "additional_name_only_related_objects": 2,
            "matched_data_center_facilities": ["ROS1", "BUE1", "SAN1", "LIM2", "LIM1"],
            "excluded_network_asset": "Las_Toninas_subsea_cable_landing_station",
            "matched_facility_count": 5,
            "OSM_footprint_area_m2_checksum_where_available": round(sum(r.get("OSM_footprint_area_m2") or 0 for r in records if r["object_type"] == "OSMFacilityOrNetworkEvidence"), 3),
            "boundary": "Five objects match provider facility names, addresses or cities. The landing station remains a network asset, and none of the OSM areas is treated as provider floor area.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "power_cooling_and_equipment_boundary": {
            "site_specifications": {code: SPEC_SHEETS[code] for code in CURRENT_CARD_CODES},
            "common_architecture": "distributed_UPS_and_diesel_standby_with_N_plus_1_or_N_plus_N_site_specific_redundancy_and_CRAC_or_chiller_cooling",
            "current_complete_BOM_and_operating_state": "not_disclosed",
            "undisclosed": ["per_site_grid_voltage_contract_capacity_and_current_draw", "substation_transformer_switchgear_busbar_PDU_OEM_model_serial_count_rating", "UPS_battery_generator_fuel_OEM_loading_test_age_and_remaining_life", "cooling_OEM_model_count_rating_CDU_and_water_loop_details", "energized_available_allocated_sold_occupied_billed_peak_and_actual_IT_load", "measured_per_site_PUE_WUE_and_live_liquid_cooled_MW"],
            "boundary": "Provider sheets contain unusually useful equipment counts and topologies, but nameplate and design data are not an as-built asset register or utilization record.",
        },
        "energy_and_environment_2024": {
            "data_center_electricity_kWh": 175426663,
            "data_center_renewable_electricity_kWh": 140504026,
            "renewable_share_percent": 80,
            "data_center_fuel_liters": 442515,
            "data_center_refrigerants_kg": 1573,
            "data_center_scope1_tCO2e": 4472,
            "data_center_scope2_market_based_tCO2e": 7034,
            "PUE_management": "AI_enabled_infrastructure_management_and_room_containment_reported_30_percent_energy_efficiency_improvement",
            "measured_portfolio_or_site_PUE_WUE": "not_disclosed",
            "boundary": "Renewable electricity includes certificates and contracts; it is not proof of hourly physical matching. The reported 30% improvement is not converted into a PUE value.",
        },
        "certification_boundary": {
            "current_Uptime_project_rows": ["BOG2_DC3_and_DC4_design_and_constructed", "LIM1_DC3_and_DC4_design", "SAN1_phase1_design", "QUI2_Carcelen_design_and_constructed", "SAO1_Cotia_design_and_constructed", "RIO1_DC5_to_DC8_design_and_constructed", "LIM2_DH1_to_DH6_design", "SAN2_DH1_to_DH6_design"],
            "boundary": "Uptime project modules and provider site codes are not always one-to-one. Design certification is not silently upgraded to constructed-facility or operational-sustainability certification.",
        },
        "AI_GPU_and_high_density_boundary": {
            "platform": "bare_metal_private_cloud_with_GPU_support_and_AI_ready_colocation",
            "high_density_claims": {"RIO2_current_page_kW_per_rack": "30_to_126", "platform_up_to_kW_per_rack": 140},
            "liquid_cooling": {"RIO2": "designed_CRAC_plus_liquid", "LIM2_SAN2": "installation_capability_claimed_but_specs_show_CRAC"},
            "current_Cirion_owned_or_customer_GPU_model_count_owner_site_delivery_rack_fabric_power_utilization_revenue_and_margin": "not_disclosed_or_established",
            "boundary": "AI-ready design, GPU support and DCIM using AI do not establish physical accelerator inventory. RIO2 is not confirmed operational, and no live liquid-cooled capacity is inferred.",
        },
        "ownership_and_financial_boundary_USD_million": {
            "acquisition": {"date": "2022-08-01", "seller": "Lumen_Technologies", "buyer": "Stonepeak_managed_fund_and_partners", "cash_transaction_value": 2700, "AustralianSuper_included_as_partner": True, "current_exact_shareholder_percentages": "undisclosed"},
            "S_and_P_2024_actual": {"revenue": 799, "reported_EBITDA": 244, "adjusted_EBITDA": 267, "EBIT_operating_profit": 55, "CFO": -35, "capex": 241, "FOCF": -276, "adjusted_debt": 1341},
            "S_and_P_2025_estimate": {"revenue": 720, "reported_EBITDA": 185, "adjusted_EBITDA": 214, "EBIT_operating_profit": 13, "capex": 277, "FOCF": -225, "adjusted_debt": 1430, "debt_to_EBITDA_x": 6.7},
            "TTM_2025_09_30": {"revenue": 726, "adjusted_EBITDA": 219, "adjusted_EBITDA_margin_percent": 30.2},
            "S_and_P_2026_forecast": {"revenue": 753, "reported_EBITDA": 234, "adjusted_EBITDA": 253, "EBIT_operating_profit": 47, "capex": 230, "FOCF": -89, "adjusted_debt": 1430},
            "rating": "B_minus_negative_outlook_February_2026",
            "data_center_only_revenue_operating_profit_cash_flow_capex_debt_and_ROIC": "not_disclosed",
            "boundary": "S&P figures are rating-adjusted actuals, estimates or forecasts as labelled, not audited Cirion statements. Cirion includes networks, connectivity, cloud and communications as well as data centers. The acquisition value is not current enterprise value.",
        },
        "outlook": {
            "positive_signals": ["two_recent_20MW_class_activations", "three_long_term_US_hyperscaler_contracts", "new_Chile_and_Peru_customers", "regional_interconnection_density", "2026_revenue_and_margin_recovery_forecast", "Stonepeak_equity_support", "renewable_and_high_density_design"],
            "risk_signals": ["2025_revenue_and_margin_contraction", "B_minus_negative_outlook", "adjusted_leverage_6_7x_estimate", "negative_FOCF_forecast_for_multiple_years", "capital_intensity_and_refinancing_risk", "legacy_service_wind_down_and_churn", "portfolio_count_scope_conflicts", "no_exact_GPU_inventory_or_data_center_segment_economics", "RIO2_status_and_capacity_label_conflicts"],
            "analytical_view": "Cirion is one of Latin America's most important private integrated data-center and fiber platforms, but its expansion opportunity is paired with a stressed capital structure. The strongest near-term evidence is physical demand and contracted hyperscaler interest; the weakest is free cash flow, leverage, current denominator consistency and separable data-center profitability.",
        },
        "records": records,
        "sources": [DIRECTORY_URL, PLATFORM_URL, COMPUTE_URL, SOC2_URL, ESG2024_URL, HANDBOOK_URL, REGULATORY_URL, MAY2026_URL, SAN2_CERT_URL, LIM2_CERT_URL, RIO2_URL, RIO2_ANNOUNCEMENT_URL, BUE1_EXPANSION_URL, UPTIME_CLIENT_URL, S_AND_P_URL, LUMEN_SALE_URL, TRANSACTION_URL] + [spec_url(code) for code in CURRENT_CARD_CODES],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records = build_records(load_osm(args.osm), args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    summary["records_sha256"] = canonical_hash(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "cirion_data_center_registry.jsonl"
    summary_path = args.output_dir / "cirion_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}))


if __name__ == "__main__":
    main()
