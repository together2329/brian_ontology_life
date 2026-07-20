#!/usr/bin/env python3
"""Build a scope-preserving TIM Enterprise / Noovle data-center registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


NOOVLE_DATA_CENTER_URL = "https://www.noovle.com/en/datacenter/"
NOOVLE_CERTIFICATIONS_URL = "https://www.noovle.com/it/datacenter/una-rete-di-data-center-certificati/"
TIM_ISO27001_URL = "https://www.gruppotim.it/content/dam/gt/sostenibilit%C3%A0/doc-varie/2025/ISO%2027001%20-%20Gruppo%20TIM.pdf"
TIM_2024_REPORT_URL = "https://www.gruppotim.it/content/dam/gt/investitori/doc---report-finanziari/2024/Annual%20report%202024.pdf"
TIM_2025_REPORT_URL = "https://www.gruppotim.it/content/dam/gt/investitori/doc---report-finanziari/2025/Annual%20report%202025.pdf"
TIM_2025_RESULTS_URL = "https://www.gruppotim.it/en/press-archive/corporate/2026/PR-BoD-24-February-2026.html"
TIM_2025_ACCOUNTS_URL = "https://www.gruppotim.it/en/press-archive/corporate/2026/PR-BoD-11-March-2026.html"
TIM_2025_ENTERPRISE_URL = "https://www.gruppotim.it/en/press-archive/corporate/2025/PR-Unboxing-TIM-Enterprise-ENG-02-10-25.html"
TIM_NEW_ROME_URL = "https://www.gruppotim.it/en/press-archive/corporate/2024/PR-TIM-Data-Center-ENG-21-11-24.html"
TIM_NOOVLE_ISLAND_URL = "https://www.gruppotim.it/it/newsroom/notiziario-tecnico-tim/2022/n2-2022/Noovle-Island-Google-Cloud-Region.html"
TIM_GREEN_DATA_CENTER_URL = "https://www.gruppotim.it/it/newsroom/notiziario-tecnico-tim/Anno-2023/n2-2023/Green_Data_Center.html"
NOOVLE_ROZZANO_HEAT_URL = "https://www.noovle.com/it/news/calore-data-center-rozzano-teleriscaldamento/"


def site(code: str, name: str, category: str, address: str, **extra: object) -> dict:
    return {
        "code": code,
        "provider_site_name": name,
        "provider_category": category,
        "current_certified_scope_address": address,
        **extra,
    }


SITES = [
    site("CESANO", "Cesano Maderno", "core", "Via Fulvio Bracco 39, 20811 Cesano Maderno (MB)"),
    site("TORINO_CENTRO", "Torino Centro", "core", "Via Issiglio 90, 10141 Torino (TO)", current_certificate_label_boundary="ISO27001_address_is_current_while_older_environmental_certificate_called_it_Centro_Servizi_Torino"),
    site("PADOVA", "Padova", "core", "Via Settima Strada 22, 35129 Padova (PD)", cogeneration_units_kW=[2019]),
    site("BOLOGNA", "Bologna", "core", "Via della Centralinista 3, 40138 Bologna (BO)", cogeneration_units_kW=[2019, 860], OSM_refs=["osm_node_12886503841"]),
    site("ROMA_POMEZIA", "Roma Sud / Pomezia", "core", "Via Pontina km 29.100, 00071 Pomezia (RM)", cogeneration_units_kW=[1800, 1800]),
    site("ROMA_ACILIA", "Roma Ovest / Acilia", "core", "Via di Macchia Palocco 223/243, 00125 Roma (RM)", cogeneration_units_kW=[1560], current_certification="Uptime_Tier_IV_facility", OSM_refs=["osm_relation_7129758"]),
    site("ROMA_ORIOLO", "Roma Nord / Oriolo Romano", "core", "Via Oriolo Romano 257, 00189 Roma (RM)"),
    site("MILANO_EST", "Milano Est / Cassina de' Pecchi", "public_cloud", "Via Strada Antica di Cassano 4, 20051 Cassina de' Pecchi (MI)"),
    site("MILANO_OVEST", "Milano Ovest / Santo Stefano Ticino", "public_cloud", "Via Ticino 66, 20010 Santo Stefano Ticino (MI)"),
    site("MILANO_SUD", "Milano Sud / Rozzano", "public_cloud", "Viale Toscana 3/5, 20089 Rozzano (MI)", cogeneration_units_kW=[2019, 2300, 1000], current_certification="Uptime_Tier_IV_facility", heat_recovery="district_heating_for_more_than_5000_homes_with_estimated_3500_tCO2_annual_reduction"),
    site("TORINO_EST", "Torino Est / Cebrosa", "public_cloud", "Via Leini at Via Reisera, 10036 Cebrosa-Settimo Torinese (TO)", OSM_refs=["osm_way_1433345058"]),
    site("TORINO_SUD", "Torino Sud / Moncalieri", "public_cloud", "Via Alessandro Cruto 2, 10024 Moncalieri (TO)", OSM_refs=["osm_relation_14662947"]),
    site("TORINO_OVEST", "Torino Ovest / Rivoli", "public_cloud", "Via Ferrero 10-16, 10098 Rivoli (TO)", OSM_refs=["osm_way_1419931331"]),
    site("FIRENZE", "Centro Servizi Firenze", "service_center", "Viuzzo dei Bruni 6, 50133 Firenze (FI)"),
    site("NAPOLI", "Centro Servizi Napoli", "service_center", "Centro Direzionale Isola F6, 80143 Napoli (NA)"),
    site("PALERMO", "Centro Servizi Palermo", "service_center", "Via Ugo La Malfa 159, 90147 Palermo (PA)", equipment_modernization="existing_UPS_replaced_with_high_efficiency_UPS_units_in_2025_without_OEM_count_or_rating_disclosure"),
]


OSM_CROSSWALK = {
    "osm_way_1419931331": ("TORINO_OVEST", "exact_current_Noovle_name_city_address_and_operator_family_match"),
    "osm_way_1433345058": ("TORINO_EST", "exact_current_Noovle_name_city_address_and_operator_family_match"),
    "osm_node_12886503841": ("BOLOGNA", "current_Noovle_name_and_Bologna_certified_site_location_match"),
    "osm_relation_7129758": ("ROMA_ACILIA", "current_Rome_Acilia_postcode_and_Tier_IV_facility_match"),
    "osm_relation_14662947": ("TORINO_SUD", "TIM_Google_name_start_date_and_Moncalieri_location_match"),
    "osm_node_10316973933": (None, "TIM_tagged_point_not_reconciled_to_current_sixteen_site_Noovle_roster"),
    "osm_way_53189075": (None, "TIM_Trento_Nord_telecom_exchange_not_present_in_current_sixteen_site_Noovle_roster"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] in OSM_CROSSWALK:
            rows[row["id"]] = row
    assert set(rows) == set(OSM_CROSSWALK)
    return rows


def build_records(osm_rows: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for source in SITES:
        row = dict(source)
        row.update({
            "id": f"tim_noovle_provider_site_{source['code'].lower()}",
            "object_type": "CurrentCertifiedDataCenterServiceSite",
            "country": "Italy",
            "owner": "TIM_SpA",
            "operator": "Noovle_SpA_Societa_Benefit",
            "lifecycle": "active_service_scope_per_current_2025_ISO27001_certificate_and_April_2026_company_statement_of_sixteen_active_data_centers",
            "site_count_boundary": "The certificate establishes a current Noovle operational service location. It does not establish building count, title parcel, data-hall count, customer tenancy, live IT load or site revenue.",
            "power_boundary": "The portfolio POD, historical IT and target installed-power metrics are not allocated to this site without a provider site-level disclosure.",
            "accessed_on": accessed_on,
        })
        records.append(row)

    records.append({
        "id": "tim_noovle_provider_project_new_rome_25mw",
        "object_type": "PlannedDataCenterProject",
        "country": "Italy",
        "market": "near_Rome_exact_site_undisclosed",
        "owner": "TIM_SpA",
        "operator": "Noovle_SpA_expected",
        "lifecycle": "announced_for_operation_by_end_2026_not_counted_among_sixteen_active_sites",
        "project_capacity_MW": 25,
        "power_denominator": "provider_project_capacity_or_installed_capacity_not_live_IT_load",
        "investment_EUR": 130_000_000,
        "reliability_target": "Rating_4",
        "AI_GPU_statement": "intended_to_host_high_performance_GPU_hardware_for_AI_without_vendor_model_count_owner_delivery_or_acceptance_disclosure",
        "water_and_waste": "rainwater_recovery_no_city_water_impact_goal_and_88_percent_construction_waste_recycling_target",
        "source_url": TIM_NEW_ROME_URL,
        "count_boundary": "This announced project is retained separately from the sixteen active sites and from existing Rome campus expansions.",
        "accessed_on": accessed_on,
    })

    for osm_id, source in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"tim_noovle_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityOrTelecomLocationEvidence",
            "country": "Italy",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_start_date": source.get("tags", {}).get("start_date"),
            "source_url": source["source_url"],
            "count_boundary": "An OSM geometry or point is location evidence, not proof of current provider roster status, title, building count, gross floor area, live load, equipment, GPU inventory or financial contribution.",
            "accessed_on": accessed_on,
        })

    assert len(records) == 24
    assert sum(row["object_type"] == "CurrentCertifiedDataCenterServiceSite" for row in records) == 16
    assert sum(row["object_type"] == "PlannedDataCenterProject" for row in records) == 1
    assert sum(row["object_type"] == "OSMFacilityOrTelecomLocationEvidence" for row in records) == 7
    assert sum(row.get("matched_provider_code") is not None for row in records if row["object_type"] == "OSMFacilityOrTelecomLocationEvidence") == 5
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    sites = [row for row in records if row["object_type"] == "CurrentCertifiedDataCenterServiceSite"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityOrTelecomLocationEvidence"]
    matched_osm = [row for row in osm if row["matched_provider_code"]]
    cogeneration = {
        row["code"]: row["cogeneration_units_kW"]
        for row in sites
        if row.get("cogeneration_units_kW")
    }
    return {
        "id": "tim_noovle_data_center_summary_2026_07_19",
        "operator_boundary": "TIM_owned_data_centers_managed_by_wholly_owned_Noovle_with_TIM_Enterprise_customer_and_financial_scope",
        "accessed_on": accessed_on,
        "current_roster_reconciliation": {
            "active_data_centers": 16,
            "current_provider_category_counts": {"public_cloud": 6, "core": 7, "service_centers": 3},
            "current_2025_ISO27001_data_center_or_service_site_rows": len(sites),
            "planned_new_Rome_project": 1,
            "future_network_target": 17,
            "future_latest_generation_Tier_or_Rating_IV_target": 8,
            "boundary": "The sixteen active certificate-backed service sites, the planned twenty-fifth-megawatt Rome project, and the future seventeen-site/eight-latest-generation target are different lifecycle scopes. Offices in the same certificate are excluded.",
        },
        "scale_and_power_denominator_reconciliation": {
            "2022_disclosure": {"sites": 16, "system_room_area_m2": 40_000, "servers": 60_000, "total_IT_electrical_power_MW": 40},
            "2024_reporting_disclosure": {"sites": 16, "system_room_area_m2": 50_000, "power_available_at_electrical_cabinet_points_of_delivery_MW": 100.8},
            "2026_end_target": {"sites": 17, "installed_capacity_MW": 125, "increment_MW": 25, "new_Rome_project_investment_EUR": 130_000_000},
            "site_level_allocation": "not_publicly_disclosed_except_new_Rome_project_25MW_and_named_cogeneration_units",
            "current_live_IT_load_sold_load_occupied_load_utilization_and_billed_load": "undisclosed",
            "boundary": "Historical IT power, current or dated POD availability, installed-capacity targets, redundant paths, cogeneration ratings and live customer IT load are not interchangeable or additive.",
        },
        "power_cooling_and_equipment": {
            "named_2025_natural_gas_high_efficiency_cogeneration_units_kW": cogeneration,
            "named_cogeneration_total_kW": sum(sum(values) for values in cogeneration.values()),
            "modernization_categories": ["UPS", "refrigeration_units", "batteries", "generators", "auxiliary_systems"],
            "Palermo": "high_efficiency_UPS_replacement_disclosed_without_OEM_model_count_rating_or_topology",
            "new_generation_architecture": "fully_redundant_electrical_and_cooling_design_with_99_995_percent_service_availability_statement",
            "provider_design_PUE": "less_than_1_3_for_state_of_the_art_sites_not_a_measured_fleet_average",
            "2022_mature_fleet_PUE": "1_54_excluding_new_2022_sites_dated_not_current",
            "2025_water": {"monitored_sites": 11, "average_WUE_l_per_kWh": 0.097, "2024_comparator_WUE_l_per_kWh": 0.291, "rainwater_reuse_sites": 3, "rainwater_reused_m3": 480},
            "2025_energy_and_certification": {"Italy_certified_renewable_electricity_procurement_percent": 100, "EU_Code_of_Conduct_data_centers": 11, "data_centers_with_WUE_at_or_below_0_19": 9},
            "Rozzano_heat_recovery": {"homes": "more_than_5000", "estimated_annual_CO2_reduction_tonnes": 3500, "technology": "heat_exchangers_and_heat_pumps_to_third_party_district_heating"},
            "complete_per_site_grid_voltage_contract_transformer_switchgear_busbar_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_test_age_and_remaining_life": "undisclosed_or_incomplete",
            "boundary": "Cogeneration ratings are generation equipment capacity, not data-center IT load. Provider design PUE, certified renewable procurement and monitored WUE do not establish per-site actual load, hourly carbon matching, water use or a complete as-built bill of materials.",
        },
        "AI_GPU_and_cloud_boundary": {
            "Google_Cloud": "Google_installed_its_public_cloud_solution_in_two_three-zone_Italian_regions_hosted_across_six_TIM_Noovle_sites",
            "ownership_boundary": "Google_platform_and_customer_hardware_are_not_inferred_as_TIM_or_Noovle_owned_GPUs",
            "TIM_accelerated_cloud": "2025_annual_report_says_GPU_accelerated_AI_infrastructure_is_in_release_during_2026",
            "new_Rome_project": "intended_to_host_high_performance_GPU_hardware",
            "exact_current_TIM_Noovle_Google_customer_or_partner_physical_GPU_accelerator_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "boundary": "Cloud and AI services, public-cloud tenancy and future GPU readiness do not disclose a physical accelerator inventory. No GPU total is inferred.",
        },
        "financial_and_investability_boundary": {
            "Noovle": {"ownership": "100_percent_TIM_SpA", "standalone_audited_revenue": "not_separately_disclosed_in_reviewed_public_group_reporting", "standalone_operating_profit_EBITDA_cash_flow_capex_assets_debt_and_ROIC": "not_separately_disclosed"},
            "TIM_Enterprise_2025_EUR_m": {"revenue": 3520, "service_revenue": 3276, "order_book": "more_than_4000", "cloud_service_revenue_growth_percent": 24, "ICT_share_of_service_revenue_percent": 68, "EBITDA_after_lease": "not_disclosed_for_2025_in_reviewed_results", "operating_profit": "not_disclosed"},
            "TIM_Enterprise_2024_EUR_m": {"revenue": 3291, "gross_margin": 1200, "EBITDA_after_lease": 700, "cloud_revenue": "more_than_1000"},
            "TIM_Group_2025": {"revenue_EUR_b": 13.7, "EBITDA_EUR_b": 4.4, "EBITDA_after_lease_EUR_b": 3.7, "EBIT_EUR_m": 549, "net_profit_EUR_m": 519, "capex_EUR_b": 1.9, "adjusted_net_debt_after_lease_EUR_b": 6.854},
            "data_center_only_revenue_operating_profit_EBITDA_capex_energy_cost_assets_utilization_customer_concentration_and_ROIC": "undisclosed",
            "direct_public_equity_security": "Telecom_Italia_SpA_listed_parent_not_a_data_center_pure_play",
            "boundary": "TIM Enterprise combines connectivity, cloud, IT, cybersecurity and IoT and includes Noovle, Olivetti, Telsy and Trust Technologies. Group results also include Consumer and Brazil. Neither perimeter isolates Noovle or data-center operating profit.",
        },
        "outlook": {
            "TIM_2026_guidance": {"group_revenue_growth_percent": "2_to_3", "group_EBITDA_after_lease_growth_percent": "5_to_6", "domestic_revenue_growth_percent": "1_to_2", "domestic_EBITDA_after_lease_growth_percent": "approximately_4", "group_capex_percent_of_revenue": "below_14", "net_debt_after_lease_to_EBITDA_after_lease": "below_1_7x"},
            "positive_signals": ["sixteen_active_national_sites", "cloud_service_revenue_growth_24_percent", "more_than_4_billion_EUR_order_book", "new_25MW_Rome_AI_ready_project", "two_Google_Cloud_regions", "measured_water_efficiency", "TIM_enterprise_distribution_and_network"],
            "conversion_tests": ["commission_new_Rome_site_by_end_2026", "bridge_100_8MW_POD_and_125MW_target_to_live_IT_and_billed_load", "publish_site_level_capacity_and_utilization", "identify_GPU_model_count_owner_and_AI_revenue", "separate_Noovle_and_data_center_financials", "publish_complete_equipment_inventory_and_vendor_awards"],
            "risks": ["mixed_telecom_and_ICT_financial_scope", "capital_intensity_and_execution", "hyperscaler_dependency", "no_GPU_inventory", "no_site_utilization_or_ROIC", "POD_IT_and_installed_capacity_denominator_conflict", "legacy_facility_modernization"],
            "analytical_view": "TIM offers listed exposure to a real national data-center platform with fast-growing cloud demand, but it is not a data-center pure play. The investable proof point is conversion of the Rome expansion and enterprise order book into disclosed utilization, cash return and margin without losing economics to hyperscaler ownership or group-level cost opacity.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "current_roster_matches": len(matched_osm),
            "unreconciled_or_excluded_objects": [row["OSM_ref"] for row in osm if not row["matched_provider_code"]],
            "matched_footprint_area_m2_sum_not_floor_area": round(sum(row["OSM_footprint_area_m2"] or 0 for row in matched_osm), 3),
            "all_related_footprint_area_m2_sum_not_floor_area": round(sum(row["OSM_footprint_area_m2"] or 0 for row in osm), 3),
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "Five OSM objects reconcile to current certificate-backed sites. The unnamed TIM point and Trento telecom exchange remain outside the current sixteen-site roster. Footprints are not floor area, data-hall area or revenue-producing capacity.",
        },
        "records": records,
        "sources": [NOOVLE_DATA_CENTER_URL, NOOVLE_CERTIFICATIONS_URL, TIM_ISO27001_URL, TIM_2024_REPORT_URL, TIM_2025_REPORT_URL, TIM_2025_RESULTS_URL, TIM_2025_ACCOUNTS_URL, TIM_2025_ENTERPRISE_URL, TIM_NEW_ROME_URL, TIM_NOOVLE_ISLAND_URL, TIM_GREEN_DATA_CENTER_URL, NOOVLE_ROZZANO_HEAT_URL],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()

    osm_rows = load_osm(args.osm)
    records = build_records(osm_rows, args.accessed_on)
    summary = build_summary(records, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "tim_noovle_data_center_registry.jsonl"
    summary_path = args.output_dir / "tim_noovle_data_center_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "current_certified_sites": 16,
        "planned_projects": 1,
        "OSM_objects": 7,
        "OSM_current_roster_matches": 5,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
