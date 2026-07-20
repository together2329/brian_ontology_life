#!/usr/bin/env python3
"""Build a scope-preserving H5 Data Centers portfolio and OSM registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


DIRECTORY_URL = "https://h5datacenters.com/data-centers.html"
HOME_URL = "https://h5datacenters.com/"
AI_URL = "https://h5datacenters.com/Ai-in-data-centers.html"
HYSCALE_JV_URL = "https://novacapcorp.com/news/novacap-h5-data-centers-joint-venture-advanced-data-center-solutions-north-america/"
HYSCALE_FUND_URL = "https://novacapcorp.com/news/novacap-closes-first-digital-infrastructure-fund/"
HYSCALEIX_URL = "https://novacapcorp.com/news/novacap-and-h5-data-centers-launch-hyscaleix-data-centers/"
HYSCALEIX_PORTFOLIO_URL = "https://novacapcorp.com/company/hyscaleix/"
LOCKPORT_PERMIT_URL = "https://extapps.dec.ny.gov/data/dar/afs/permits/929260015800002_r1.pdf"
ASHBURN_RELEASE_URL = "https://h5datacenters.com/H5-Data-Centers-Breaks-Ground-on-new-ashburn-build.html"
PHOENIX_EXPANSION_URL = "https://h5datacenters.com/phase-two-expanstion-h5-data-center-phoenix.html"
CHARLOTTE_URL = "https://h5datacenters.com/charlotte-data-center.html"
CLEVELAND_URL = "https://h5datacenters.com/cleveland-data-center.html"
CHICAGO_URL = "https://h5datacenters.com/chicago-data-center.html"
QUINCY_URL = "https://h5datacenters.com/quincy-data-center.html"
VIRGINIA_URL = "https://h5datacenters.com/virginia-data-center.html"


def facility(code: str, label: str, address: str, slug: str, **extra: object) -> dict:
    return {
        "code": code,
        "directory_label": label,
        "directory_address": address,
        "url": f"https://h5datacenters.com/{slug}.html",
        **extra,
    }


FACILITIES = [
    facility("ABQ", "Albuquerque, NM", "505 Marquette Ave NW, Albuquerque, NM 87102", "albuquerque-data-center", provider_area_sq_ft=225000, area_denominator="two_facilities_combined"),
    facility("ASH", "Ashburn, VA", "21800 Beaumeade Circle, Ashburn, VA 20147", "ashburn-data-center", provider_area_sq_ft=255000, provider_power_MW=42, power_denominator="ultimate_critical_load_or_Dominion_access_wording_not_current_live_load", provider_power_MVA=60, lifecycle_detail="current_directory_new_build_marketing_page_with_stale_Q3_2024_phase_availability_copy"),
    facility("ATL", "Atlanta, GA", "345 Courtland Street NE, Atlanta, GA 30308", "atlanta-data-center", provider_area_sq_ft=110000),
    facility("BUF1", "Buffalo I, NY", "5319 Enterprise Dr., Lockport, NY 14094", "buffalo-I-data-center", platform="Hyscale_Data_Centers_JV", provider_area_sq_ft=409200, area_denominator="Buffalo_I_and_II_combined_campus_do_not_sum_twice", provider_power_MVA=44, power_denominator="two_on_site_substations_for_BUF1_and_BUF2_combined"),
    facility("BUF2", "Buffalo II, NY", "5319 Enterprise Dr., Lockport, NY 14094", "buffalo-II-data-center", platform="Hyscale_Data_Centers_JV", provider_area_sq_ft=409200, area_denominator="Buffalo_I_and_II_combined_campus_do_not_sum_twice", provider_power_MVA=44, power_denominator="two_on_site_substations_for_BUF1_and_BUF2_combined"),
    facility("BUF3", "Buffalo III, NY", "350 Main Street, Buffalo, NY 14202", "buffalo-III-data-center", platform="HyscaleIX_JV", provider_area_sq_ft=19000),
    facility("CLT", "Charlotte, NC", "10105 David Taylor Drive, Charlotte, NC 28262", "charlotte-data-center", provider_area_sq_ft=207000, area_denominator="mixed_use_existing_campus", future_adjacent_area_sq_ft=200000, future_adjacent_critical_MW=20),
    facility("CHI", "Chicago, IL", "1951 W. Hastings St., Chicago, IL 60608", "chicago-data-center", provider_area_sq_ft=185000, provider_power_MW=36, power_denominator="ultimate_two_phase_total", initial_phase_MW=18, lifecycle_detail="development_target_with_provider_1H_versus_2H_2027_ready_date_conflict"),
    facility("CIN1", "Cincinnati I, OH", "360 Gest Street, Cincinnati, OH 45203", "cincinnati-data-center", provider_area_sq_ft=80000, area_denominator="current_brochure_rounded_from_historical_79825_square_feet"),
    facility("CIN2", "Cincinnati II, OH", "925 Dalton Avenue, Cincinnati, OH 45203", "cincinnati-II-data-center", provider_area_sq_ft=107000),
    facility("CLE", "Cleveland, OH", "1625 Rockwell Avenue, Cleveland, OH 44114", "cleveland-data-center", provider_area_sq_ft=351000, future_expansion_MW="10_plus", future_expansion_target="Q1_2027"),
    facility("DEN", "Denver, CO", "5350 South Valentia Way, Greenwood Village, CO 80111", "denver-data-center", provider_area_sq_ft=300000, area_denominator="two_independent_data_centers_on_one_campus"),
    facility("HER", "Herndon, VA", "470 Springpark Pl, Herndon, VA 20170", "herndon-data-center", current_page_address="470_and_480_Springpark_Place", provider_area_sq_ft=53000, area_denominator="two_building_campus", provider_power_MW=15, power_denominator="critical_capacity_not_live_load"),
    facility("MSP", "Minneapolis, MN", "1125 Energy Park Dr., Suite 100, St. Paul, MN 55108", "minneapolis-data-center", provider_area_sq_ft=17000),
    facility("BNA", "Nashville, TN", "211 Commerce St., Suite 700, Nashville, TN 37201", "nashville-data-center", platform="HyscaleIX_JV", current_page_address="147 Fourth Avenue N., 8th Floor, Nashville, TN 37219", provider_area_sq_ft=19700, address_boundary="directory_and_current_facility_page_conflict_current_page_matches_2026_acquired_carrier_hotel"),
    facility("NJ", "New Jersey", "200B Meadowlands Parkway, Secaucus, NJ 07094", "new-jersey-data-center", provider_area_sq_ft=38000, provider_backup_generation_MW=2.5),
    facility("NYC", "New York, NY", "325 Hudson St., New York, NY 10013", "new-york-data-center", provider_area_sq_ft=240000, area_denominator="host_building_or_data_center_property_not_H5_white_space"),
    facility("OMA", "Omaha, NE", "10917 Harry Watanabe Pkwy, Omaha, NE 68128", "omaha-data-center", platform="Hyscale_Data_Centers_JV", provider_area_sq_ft=234500, area_denominator="current_provider_campus_value_conflicts_with_299488_square_foot_property_transaction_report"),
    facility("PHL", "Philadelphia, PA", "1500 Spring Garden St., Suite 520, Philadelphia, PA 19130", "philadelphia-data-center", provider_area_sq_ft=72000),
    facility("PHX", "Phoenix, AZ", "2600 W Germann Rd, Chandler, AZ 85286", "phoenix-data-center", provider_area_sq_ft=180000, provider_power_MW=26, power_denominator="current_page_capacity_not_live_load", provider_density_source_text="up_to_20_watts_per_cabinet", density_boundary="source_text_is_preserved_and_not_silently_corrected_to_kW", historical_full_buildout_MW=30),
    facility("PIT", "Pittsburgh, PA", "2202 Liberty Ave., Pittsburgh, PA 15222", "pittsburgh-data-center", provider_area_sq_ft=30000),
    facility("PDX", "Portland, OR", "1233 NW 12th Avenue, Suite 201, Portland, OR 97209", "portland-data-center", provider_area_sq_ft=42000, provider_backup_generation_MW=2),
    facility("QCY1", "Quincy, WA", "1711 M Street NE, Quincy, WA 98848", "quincy-data-center", provider_area_sq_ft=240000, provider_power_MW=40, power_denominator="full_buildout_not_live_load"),
    facility("QCY2", "Quincy II, WA", "1305 Intermodal Way NE, Quincy, WA 98848", "quincy-II-data-center", provider_area_sq_ft=452300, area_denominator="Quincy_II_and_III_combined_campus_do_not_sum_twice"),
    facility("QCY3", "Quincy III, WA", "1500 M Street NE, Quincy, WA 98848", "quincy-III-data-center", platform="Hyscale_Data_Centers_JV", provider_area_sq_ft=452300, area_denominator="Quincy_II_and_III_combined_campus_do_not_sum_twice"),
    facility("SAT", "San Antonio, TX", "100 Taylor St., San Antonio, TX 78205", "san-antonio-data-center", provider_area_sq_ft=85000, area_denominator="two_facilities_combined"),
    facility("SLO", "San Luis Obispo, CA", "3610 Sacramento Drive, San Luis Obispo, CA 93401", "san-luis-obispo-data-center", provider_area_sq_ft=44000),
    facility("SEA", "Seattle, WA", "1000 Denny Way, Seattle, WA 98109", "seattle-data-center", provider_area_sq_ft=293000, area_denominator="converted_former_Seattle_Times_building_not_white_space"),
    facility("SJC", "Silicon Valley, CA", "1360 Kifer Rd, Sunnyvale, CA 94086", "silicon-valley-data-center", provider_area_sq_ft=96100),
    facility("STL", "St. Louis, MO", "710 N. Tucker Blvd., Suite 610, St. Louis, MO 63101", "saint-louis-data-center", platform="HyscaleIX_JV", provider_area_sq_ft=36000, area_denominator="H5_space_inside_550000_square_foot_Globe_Building"),
    facility("TPA", "Tampa, FL", "655 North Franklin Street, Tampa, FL 33602", "tampa-data-center", platform="HyscaleIX_JV", current_page_address="655_North_Franklin_Street_Suite_1000_10th_floor", provider_area_sq_ft=27300),
    facility("VA", "Virginia, VA", "4050 Lafayette Center Dr, Chantilly, VA 20151", "virginia-data-center", current_page_address="4030_4040_and_4050_Lafayette_Center_Drive", provider_area_sq_ft=145000, area_denominator="three_building_campus", provider_power_MW=23, power_denominator="critical_capacity_not_live_load"),
]


OSM_CROSSWALK = {
    "osm_way_491914767": ("CLE", "name_and_website_match_without_operator_tag"),
    "osm_way_131874718": ("MSP", "operator_H5_exact_current_match"),
    "osm_way_300959969": ("PHX", "operator_H5_exact_current_match"),
    "osm_node_12471740457": ("NJ", "operator_H5_exact_current_match"),
    "osm_node_13748555787": ("PDX", "operator_H5_Data_Centers_exact_current_match"),
    "osm_way_234722720": ("ASH", "operator_H5_Data_Centers_exact_address_match"),
    "osm_way_102129663": ("SAT", "operator_H5_Data_Centers_exact_current_match"),
    "osm_way_231664575": ("SEA", "operator_H5_Data_Centers_current_conversion_match"),
    "osm_way_283051474": ("QCY1", "current_H5_name_and_website_with_legacy_Intuit_operator_tag"),
}


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


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
    for row in FACILITIES:
        records.append({
            "id": f"h5_provider_directory_{row['code'].lower()}",
            "object_type": "ProviderDirectoryLabelEvidence",
            "operator_or_manager": "H5_Data_Centers",
            "country": "United_States",
            "lifecycle": row.get("lifecycle_detail", "current_provider_directory_operating_or_marketed_label"),
            "platform": row.get("platform", "H5_direct_or_ownership_vehicle_not_established_by_directory"),
            **row,
            "count_boundary": "A directory label is not automatically one owned parcel, building, data hall, operating facility or revenue-producing asset. Shared addresses and multi-building cards are preserved.",
            "capacity_boundary": "Provider area and power fields retain their stated denominator. They are not summed into live, energized, contracted, sold, utilized, billed or actual IT load.",
            "accessed_on": accessed_on,
        })
    for osm_id, row in osm_rows.items():
        code, classification = OSM_CROSSWALK[osm_id]
        records.append({
            "id": f"h5_osm_evidence_{osm_id}",
            "object_type": "OSMFacilityEvidence",
            "operator_or_manager": "H5_Data_Centers",
            "OSM_ref": osm_id,
            "matched_provider_code": code,
            "match_classification": classification,
            "raw_operator": row.get("operator"),
            "raw_name": row.get("name"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "OSM_footprint_area_m2": row.get("footprint_area_m2"),
            "OSM_building_levels": row.get("building_levels"),
            "source_url": row["source_url"],
            "count_boundary": "The OSM object is a location crosswalk, not proof of title, building count, lifecycle, gross floor area, white space, MW, utilization or H5 financial contribution.",
            "accessed_on": accessed_on,
        })
    assert len(records) == 41
    assert sum(row["object_type"] == "ProviderDirectoryLabelEvidence" for row in records) == 32
    assert sum(row["object_type"] == "OSMFacilityEvidence" for row in records) == 9
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    provider = [row for row in records if row["object_type"] == "ProviderDirectoryLabelEvidence"]
    osm = [row for row in records if row["object_type"] == "OSMFacilityEvidence"]
    return {
        "id": "h5_data_centers_portfolio_summary_2026_07_19",
        "operator": "H5 Data Centers",
        "accessed_on": accessed_on,
        "roster_reconciliation": {
            "current_provider_directory_labels": len(provider),
            "distinct_directory_addresses": len({row["directory_address"] for row in provider}),
            "provider_homepage_market_headline": 25,
            "provider_homepage_space_under_management_sq_ft": "4_million_plus",
            "Hyscale_wholesale_facilities_disclosed_by_JV": 4,
            "HyscaleIX_carrier_hotel_facilities_disclosed_by_JV": 4,
            "directory_labels_tagged_to_Hyscale": [row["code"] for row in provider if row["platform"] == "Hyscale_Data_Centers_JV"],
            "directory_labels_tagged_to_HyscaleIX": [row["code"] for row in provider if row["platform"] == "HyscaleIX_JV"],
            "Nashville_address_conflict": "Directory says 211 Commerce Street while the current site page says 147 Fourth Avenue North, matching the acquired carrier-hotel identity; both are retained and the card is not counted as two current facilities.",
            "boundary": "Thirty-two labels, thirty-one directory addresses, twenty-five marketed markets, more than four million square feet under management, eight JV facilities and physical buildings are different scopes. Under management is not synonymous with owned, operating, available or H5-recognized revenue area.",
        },
        "selected_scale_and_lifecycle_not_additive": {
            "Ashburn": {"area_sq_ft": 255000, "ultimate_critical_load_MW": 42, "page_power_MVA": 60, "boundary": "Current marketing retains a Q3 2024 first-phase statement; exact current commissioned, accepted and live MW is not disclosed on the provider page."},
            "Buffalo_I_and_II": {"combined_area_sq_ft": 409200, "substation_capacity_MVA": 44, "emergency_generators_in_legacy_permit": 38, "boundary": "Two data centers at one address; permit narrative retains former Yahoo/Verizon operator language and does not establish current loading or ownership of every unit."},
            "Charlotte": {"existing_mixed_use_area_sq_ft": 207000, "future_adjacent_area_sq_ft": 200000, "future_critical_MW": 20},
            "Chicago": {"area_sq_ft": 185000, "initial_phase_MW": 18, "ultimate_MW": 36, "ready_date_conflict": "provider materials show first_half_and_second_half_2027"},
            "Cleveland": {"area_sq_ft": 351000, "future_expansion_MW": "10_plus", "future_target": "Q1_2027"},
            "Herndon": {"combined_area_sq_ft": 53000, "critical_capacity_MW": 15},
            "Phoenix": {"area_sq_ft": 180000, "current_page_capacity_MW": 26, "historical_full_buildout_MW": 30, "source_density_text": "20_watts_per_cabinet_preserved_without_correction"},
            "Quincy": {"area_sq_ft": 240000, "full_buildout_MW": 40},
            "Virginia_Chantilly": {"three_building_area_sq_ft": 145000, "critical_capacity_MW": 23},
            "boundary": "These are selected site, campus, future, critical, full-buildout, utility-access and MVA labels. They are not summed because their lifecycle and power denominators differ.",
        },
        "OSM_crosswalk": {
            "related_objects": len(osm),
            "raw_H5_or_H5_Data_Centers_operator_tagged_objects": 7,
            "name_or_website_only_current_matches": ["osm_way_491914767", "osm_way_283051474"],
            "legacy_operator_boundary": "The Quincy object retains raw operator Intuit. Intuit is not added as an H5 alias and its other objects are not routed to H5.",
            "matched_provider_codes": [row["matched_provider_code"] for row in osm],
            "footprint_values_available": sum(row["OSM_footprint_area_m2"] is not None for row in osm),
            "boundary": "OSM footprint, provider gross property area, managed space, white space and data-hall area are not interchangeable. The very large Quincy polygon is not treated as floor area.",
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "power_cooling_and_equipment_boundary": {
            "selected_provider_designs": {
                "Ashburn": "Tier_III_or_N_plus_2C_up_to_60_MVA_air_cooled_chillers_concurrently_maintainable_outside_air_economization_and_fan_walls",
                "Buffalo_I_II": "two_substations_44_MVA_N_plus_1_cooling_and_38_legacy_permit_diesel_generators",
                "Cleveland": "2N_UPS_2N_generator_farm_48_hour_runtime_more_than_20_kW_per_rack_and_2N_chillers_or_cooling_towers",
                "Denver": "2N_UPS_N_plus_1_generators_48_hour_runtime_N_plus_1_chillers_and_cooling_towers_N_plus_20_percent_CRAHs_and_460_kW_onsite_solar",
                "New_Jersey": "2N_UPS_multiple_diesel_generators_48_hour_runtime_N_plus_1_chillers_cooling_towers_and_CRACs",
                "Phoenix": "N_plus_1_UPS_48_hour_runtime_N_plus_1_chillers_and_cooling_towers",
                "Quincy": "2N_UPS_2N_backup_generators_N_plus_1_chillers_and_cooling_towers",
                "Virginia": "2N_UPS_48_hour_diesel_runtime_N_plus_1_CRACs_and_high_density_cooling_solutions",
            },
            "undisclosed_or_not_complete_by_site": [
                "utility_service_voltage_contract_capacity_current_draw_and_interconnection_queue",
                "substation_transformer_switchgear_busway_PDU_UPS_battery_generator_fuel_OEM_model_count_rating_loading_test_age_and_remaining_life",
                "chiller_CRAH_CRAC_CDU_pump_heat_exchanger_cooling_tower_OEM_model_count_rating_loading_and_live_liquid_cooled_MW",
                "operating_energized_available_allocated_sold_occupied_billed_peak_and_actual_IT_load",
                "measured_PUE_WUE_absolute_energy_water_emissions_and_hourly_renewable_matching",
            ],
            "boundary": "A redundancy topology, runtime, design capacity or future readiness claim does not establish as-built equipment inventory, current condition, live load or measured efficiency.",
        },
        "AI_GPU_boundary": {
            "provider_AI_claim": "supports_air_cooled_water_cooled_or_liquid_cooled_high_density_clusters",
            "Chicago_brochure_claim": "high_density_and_AI_deployments_with_liquid_cooling",
            "exact_current_H5_JV_customer_or_partner_GPU_accelerator_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_margin_and_remaining_life": "undisclosed_or_unestablished",
            "live_liquid_cooled_MW": "undisclosed_or_unestablished",
            "boundary": "AI and liquid-cooling support language is facility capability marketing, not proof of installed cooling plant, contracted AI load or physical accelerators. No GPU total is inferred.",
        },
        "ownership_financial_and_investability_boundary": {
            "H5_legal_and_equity_state": "privately_owned_operator_with_no_direct_public_equity_security",
            "Hyscale": {"formed": "2025-01-15", "partners": ["Novacap", "H5_Data_Centers"], "facilities": 4, "focus": "wholesale_colocation_development_and_repositioning"},
            "HyscaleIX": {"announced": "2026-02-02", "partners": ["Novacap", "H5_Data_Centers"], "facilities": 4, "focus": "carrier_hotels_and_interconnection", "acquired_from_365": ["Buffalo", "Nashville", "Tampa"], "fourth_market": "St_Louis_per_current_Novacap_portfolio_page"},
            "Novacap_Digital_Infrastructure_Fund_I_USD": "more_than_1_billion_in_primary_commitments_and_co_investments",
            "H5_standalone_audited_revenue_operating_profit_EBITDA_net_income_cash_flow_capex_debt_assets_customer_concentration_and_ROIC": "not_publicly_disclosed_in_reviewed_primary_sources",
            "JV_purchase_prices_financing_ownership_percentages_preferences_voting_rights_guarantees_and_consolidation": "undisclosed",
            "rejected_secondary_estimates": "Third-party revenue estimates range from roughly USD39.6m to USD380m for inconsistent apparent scopes; none is used as audited H5 revenue or profit.",
            "boundary": "The more-than-USD1bn sponsor fund is not capital committed to H5 alone, H5 enterprise value, H5 revenue or H5 assets. Acquired property prices and managed area do not establish company earnings.",
        },
        "outlook": {
            "positive_signals": ["25_market_and_4_million_plus_sq_ft_management_scale", "eight_facility_two_JV_expansion", "carrier_hotel_interconnection_assets", "Ashburn_fully_leased_marketing_signal", "Chicago_and_Cleveland_pipeline", "low_cost_hydropower_Central_Washington", "AI_high_density_and_liquid_cooling_addressable_demand", "Novacap_institutional_capital"],
            "conversion_tests": ["publish_exact_legal_asset_and_current_building_roster", "resolve_Nashville_and_other_directory_page_conflicts", "commission_and_accept_Ashburn_Chicago_and_Cleveland_capacity", "convert_power_to_contracted_billed_load", "publish_live_liquid_cooled_MW_and_measured_efficiency", "disclose_H5_and_JV_financial_returns"],
            "risks": ["private_financial_opacity", "JV_and_managed_asset_scope_complexity", "future_capacity_not_live_load", "power_and_equipment_bottlenecks", "directory_staleness_and_shared_address_double_counting", "legacy_asset_repositioning_capex", "no_GPU_inventory_or_AI_revenue_bridge", "no_site_level_profit_or_ROIC"],
            "analytical_view": "H5 has credible scale in regional carrier hotels, enterprise colocation and selected wholesale campuses, while Novacap provides acquisition and repositioning capital. The investable read-through is indirect: H5 and both JVs are private, and public evidence does not show standalone revenue, operating profit, leverage, utilization or returns. Growth should be tested at commissioning, customer acceptance and billed-load milestones rather than at directory, managed-area or design-MW headlines.",
        },
        "records": records,
        "sources": [
            DIRECTORY_URL,
            HOME_URL,
            AI_URL,
            HYSCALE_JV_URL,
            HYSCALE_FUND_URL,
            HYSCALEIX_URL,
            HYSCALEIX_PORTFOLIO_URL,
            LOCKPORT_PERMIT_URL,
            ASHBURN_RELEASE_URL,
            PHOENIX_EXPANSION_URL,
            CHARLOTTE_URL,
            CLEVELAND_URL,
            CHICAGO_URL,
            QUINCY_URL,
            VIRGINIA_URL,
        ] + [row["url"] for row in FACILITIES],
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
    registry_path = args.output_dir / "h5_data_centers_registry.jsonl"
    summary_path = args.output_dir / "h5_data_centers_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "summary": str(summary_path),
        "records": len(records),
        "provider_labels": 32,
        "OSM_objects": 9,
        "canonical_sha256": canonical_hash(summary),
    }, indent=2))


if __name__ == "__main__":
    main()
