#!/usr/bin/env python3
"""Build Verizon's current, partner, regulatory, sale and OSM evidence registry.

Verizon publishes several incompatible data-center scopes: service coverage,
U.S. technology facilities, city-level available-capacity locations, external
on-net partner facilities, one exact French regulatory facility and a 2017
divestiture.  This builder preserves those denominators and prevents any of
them from becoming a false current Verizon-owned physical-building census.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


GLOBAL_COLOCATION = "https://www.verizon.com/business/r3s0u4c3s/vps/global-colo-and-dc-solutions.pdf"
ON_NET_COLOCATION = "https://www.verizon.com/business/r3s0u4c3s/vps/prod-mgt/colocation-services.pdf"
AI_CONNECT = "https://www.verizon.com/business/solutions/ai-connect/"
AI_CONNECT_RELEASE = "https://www.verizon.com/about/news/verizon-unveils-ai-strategy-power-next-gen-ai-demands"
AI_CONNECT_Q4_2024_TRANSCRIPT = "https://www.verizon.com/about/sites/default/files/2025-01/VZ_4Q2024_Business_Update_Transcript_012425F.pdf"
AI_CONNECT_Q2_2025_TRANSCRIPT = "https://www.verizon.com/about/sites/default/files/2025-07/vz2q25_earnings_transcript_072125.pdf"
FRANCE_2025_DISCLOSURE = "https://www.verizon.com/business/resources/terms/verizon-fr-data-center-environmental-performance-public-disclosure-june2026.pdf"
FRANCE_2025_WORKBOOK = "https://www.verizon.com/business/r3s0u4c3s/terms/verizon-fr-data-center-environmental-performance-public-disclosure-june2026.xlsx"
VERIZON_2016_ANNUAL = "https://www.verizon.com/about/sites/default/files/Verizon-AnnualReport2016.pdf"
EQUINIX_2017_COMPLETION = "https://newsroom.equinix.com/2017-05-01-Equinix-Completes-Acquisition-of-29-Data-Centers-from-Verizon"
EQUINIX_2017_CARVEOUT = "https://investor.equinix.com/sec-filings/all-sec-filings/content/0001193125-17-073265/0001193125-17-073265.pdf"
VERIZON_2025_10K = "https://www.sec.gov/Archives/edgar/data/732712/000073271226000007/vz-20251231.htm"
VERIZON_Q1_2026 = "https://www.verizon.com/about/news/verizons-transformation-actions-deliver-growth-profitability-1q26-company-raises-adjusted-eps"


AVAILABLE_CAPACITY_CITIES = [
    ("Alpharetta", "GA"),
    ("Annapolis JCT", "MD"),
    ("Aurora", "CO"),
    ("Branchburg", "NJ"),
    ("Orlando", "FL"),
    ("Richardson", "TX"),
    ("Sunnyvale", "CA"),
    ("Richmond", "VA"),
    ("Syracuse", "NY"),
]


ON_NET_PARTNER_FACILITIES = [
    ("1 Switch Way", "Lithia Springs", "GA", "Switch", "dual", "dual", "ready_now"),
    ("2800 S. Ashland Ave.", "Chicago", "IL", "QTS", "single", "single", "projected_unspecified"),
    ("4951 NE Huffman St.", "Hillsboro", "OR", "QTS", "single", "single", "projected_unspecified"),
    ("807 E. 16th St.", "Chattanooga", "TN", "DC Blox", "single", "single", "projected_unspecified"),
    ("4800 Spring Park Rd.", "Jacksonville", "FL", "Cologix", "single", "single", "projected_unspecified"),
    ("22291 Shellhorn Rd.", "Ashburn", "VA", "QTS", "single", "single", "projected_unspecified"),
    ("1 Superloop Circle", "Sparks", "NV", "Switch", "single", "single", "projected_unspecified"),
    ("2335 South Ellis St.", "Chandler", "AZ", "CyrusOne", "single", "single", "projected_unspecified"),
    ("5660 W. Badura Ave.", "Las Vegas", "NV", "Switch", "dual", "dual", "projected_unspecified"),
    ("433 6th Street South", "Birmingham", "AL", "DC Blox", "single", "single", "projected_unspecified"),
    ("9301 Freedom Center Blvd.", "Manassas", "VA", "QTS", "dual", "dual", "projected_unspecified"),
    ("33 Global Dr.", "Greenville", "SC", "DC Blox", "single", "single", "anticipated_Q2_2025_in_source_not_reverified_live"),
]


EQUINIX_2017_BUILDING_CROSSWALK = [
    ("Atlanta", "ATL1", "AT4"),
    ("Atlanta", "ATL2 (Norcross)", "AT5"),
    ("Boston", "BOS1 (Billerica)", "BO2"),
    ("Chicago", "ORD1 (Westmont)", "CH7"),
    ("Culpeper", "IAD3 (Culpeper)", "CU1"),
    ("Culpeper", "IAD3 (Culpeper)", "CU2"),
    ("Culpeper", "IAD3 (Culpeper)", "CU3"),
    ("Culpeper", "IAD3 (Culpeper)", "CU4"),
    ("Dallas", "DFW1 (Irving)", "DA9"),
    ("Dallas", "DFW2 (Richardson Alma)", "DA10"),
    ("Denver", "DEN1 (Englewood)", "DE2"),
    ("Houston", "IAH1 (Houston)", "HO1"),
    ("Los Angeles", "LAX1 (Torrance)", "LA7"),
    ("Miami", "MIA1 (Miami NOTA)", "MI1"),
    ("Miami", "MIA2 (Doral)", "MI6"),
    ("New York", "EWR1 (Carteret)", "NY11"),
    ("New York", "EWR2 (Piscataway)", "NY12"),
    ("New York", "LGA1 (Elmsford)", "NY13"),
    ("Seattle", "SEA1 (Kent)", "SE4"),
    ("Silicon Valley", "SJC2 (San Jose)", "SV13"),
    ("Silicon Valley", "SJC3 (Santa Clara)", "SV14"),
    ("Silicon Valley", "SJC3 (Santa Clara)", "SV15"),
    ("Silicon Valley", "SJC3 (Santa Clara)", "SV16"),
    ("Silicon Valley", "SJC3 (Santa Clara)", "SV17"),
    ("Washington D.C.", "IAD1 (Ashburn)", "DC13"),
    ("Washington D.C.", "IAD4 (Manassas)", "DC14"),
    ("Washington D.C.", "IAD2 (Herndon)", "DC97"),
    ("Sao Paulo", "GRU1 (Sao Paulo NAP)", "SP4"),
    ("Bogota", "BOG1 (Bogota NAP)", "BG1"),
]


PORTFOLIO_CONTEXT = {
    "current_service_and_facility_scopes": {
        "global_colocation_service_locations": "200_plus_including_MVNO_system_integrator_carrier_and_cable_landing_station_locations",
        "US_tech_facilities": "350_plus",
        "US_available_power_MW": "200_plus",
        "narrative_US_locations_with_expanding_power_and_space": "over_300_plus",
        "named_available_capacity_cities": 9,
        "on_net_external_partner_facilities": 12,
        "boundary": "Service locations, technology facilities, city labels and external partner sites are different denominators and do not establish 200, 300 or 350 Verizon-owned data centers.",
    },
    "current_exact_regulatory_site": {
        "name": "Saint Denis",
        "address": "14 Rue de la Montjoie, 93210 Saint Denis, France",
        "property_owner": "SAS Parc de la Plaine",
        "operator": "Verizon France SAS",
        "installed_IT_power_demand_kW": 763.81,
        "customer_IT_power_kW": 505.54,
        "Verizon_IT_power_kW": 258.27,
        "boundary": "Eight local location codes in the workbook are reporting identifiers inside one disclosed structure, not eight physical data centers.",
    },
    "historical_divestiture": {
        "agreement_scope": "24_sites_containing_29_data_center_buildings_in_15_North_and_Latin_American_metros",
        "completion_date": "2017-05-01",
        "cash_consideration_USD_billion": 3.6,
        "buyer": "Equinix",
        "boundary": "The acquired facilities became Equinix assets; later Verizon resale, network presence or tenancy does not restore Verizon ownership.",
    },
    "GPU_and_AI": {
        "direct_Verizon_owned_GPU_inventory_by_model_count_site_power_and_utilization": "undisclosed",
        "evidence": ["Vultr_GPUaaS_partnership", "NVIDIA_private_5G_edge_platform_collaboration", "Google_Cloud_and_Meta_network_capacity", "AWS_fiber_connectivity", "AI_ready_colocation_marketing"],
        "boundary": "GPUaaS, partner deployment and GPU-ready facility language do not prove Verizon ownership of accelerators or a fleet total.",
    },
    "comparison_boundary": "Do not add 200-plus service locations, 300-plus narrative U.S. locations, 350-plus U.S. technology facilities, nine city labels, 12 partner facilities, one French regulatory facility, 29 sold buildings or 13 OSM objects.",
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_").replace("__", "_")


def build_records(accessed_on: str) -> list[dict]:
    records: list[dict] = []
    for order, (city, state) in enumerate(AVAILABLE_CAPACITY_CITIES, start=1):
        records.append({
            "id": f"verizon_available_capacity_{slug(city)}_{state.lower()}",
            "object_type": "ProviderNamedAvailableCapacityCityRecord",
            "source_order": order,
            "city": city,
            "state": state,
            "country_code": "US",
            "published_status": "data_center_site_with_available_capacity",
            "exact_address": "undisclosed",
            "physical_building_count": "undisclosed",
            "property_owner_and_operator": "undisclosed_at_city_label_level",
            "power_allocation_MW": "undisclosed_at_city_label_level",
            "boundary": "A current provider city label is not an exact building, ownership, operating-load or utilization record.",
            "source_urls": [GLOBAL_COLOCATION],
            "accessed_on": accessed_on,
        })
    for order, (street, city, state, operator, entrances, routes, status) in enumerate(ON_NET_PARTNER_FACILITIES, start=1):
        records.append({
            "id": f"verizon_on_net_partner_{slug(operator)}_{slug(city)}_{state.lower()}",
            "object_type": "ExternalPartnerOnNetDataCenterRecord",
            "source_order": order,
            "address": f"{street}, {city}, {state}, US",
            "city": city,
            "state": state,
            "country_code": "US",
            "physical_data_center_operator": operator,
            "Verizon_role": "planned_or_current_direct_transport_connectivity_to_Verizon_IP_core_and_long_haul_network",
            "data_center_entrances": entrances,
            "fiber_routes": routes,
            "source_status": status,
            "current_live_status": "not_reverified_beyond_source_wording",
            "boundary": "On-net connectivity does not make Verizon the property owner or physical data-center operator.",
            "source_urls": [ON_NET_COLOCATION],
            "accessed_on": accessed_on,
        })
    records.append({
        "id": "verizon_france_saint_denis_2025",
        "object_type": "RegulatoryExactDataCenterPerformanceRecord",
        "name": "Saint Denis",
        "address": "14 Rue de la Montjoie, 93210 Saint Denis, France",
        "country_code": "FR",
        "local_administrative_unit_code": "93066",
        "reporting_period": "2025-01-01/2025-12-31",
        "operation_start": "2017-07",
        "type": "colocation_data_center_structure",
        "property_owner": "SAS Parc de la Plaine",
        "operator": "Verizon France SAS",
        "local_reporting_codes": [f"FRA278C{index}" for index in range(1, 9)],
        "electrical_redundancy": {"high_voltage": "N+1", "low_voltage_lineup": "N+1", "rack": "N+1"},
        "cooling_redundancy": {"room": "N+1", "rack": "N"},
        "installed_IT_power_demand_kW": 763.81,
        "installed_IT_power_demand_rounded_PDF_kW": 764,
        "installed_IT_power_split_kW": {"customer": 505.54, "Verizon": 258.27},
        "total_floor_area_m2": 7426,
        "computer_room_floor_area_m2": 1430,
        "total_energy_excluding_backup_generators_kWh": 10943936,
        "backup_generator_energy_kWh": 72650,
        "backup_generator_fuel_liters": 7265,
        "total_IT_energy_kWh": 6690976,
        "PUE_reported": 1.64,
        "PUE_derived_unrounded": 1.635626,
        "water_input_m3": 237,
        "potable_water_input_m3": 237,
        "WUE_reported_rounded": 0.00,
        "WUE_derived_L_per_kWh": 0.035421,
        "renewable_energy_factor_reported": 1.00,
        "renewable_energy_Guarantees_of_Origin_kWh": 10943936,
        "renewable_energy_PPA_kWh": 0,
        "renewable_energy_onsite_kWh": 0,
        "waste_heat_reused_kWh": "not_available",
        "average_waste_heat_temperature_C": 15,
        "IT_intake_air_setpoint_C": 26,
        "refrigerants": ["R134A", "R1234ZE", "R290"],
        "server_capacity_SERT": "not_available",
        "storage_capacity_PB": "not_available",
        "boundary": "This is one leased/operator-separated French structure. Local reporting codes are not physical buildings, installed demand is not measured utilization, and the site is not a complete Verizon portfolio roster.",
        "source_urls": [FRANCE_2025_DISCLOSURE, FRANCE_2025_WORKBOOK],
        "accessed_on": accessed_on,
    })
    records.append({
        "id": "verizon_equinix_divestiture_2017",
        "object_type": "HistoricalDataCenterPortfolioDivestitureRecord",
        "agreement_site_count": 24,
        "completed_data_center_building_count": 29,
        "metros": 15,
        "regions": ["United States", "Brazil", "Colombia"],
        "cash_consideration_USD_billion": 3.6,
        "completion_date": "2017-05-01",
        "buyer": "Equinix",
        "seller": "Verizon",
        "customer_count_at_completion_more_than": 1000,
        "gross_floor_area_at_completion_million_ft2_approximate": 3.0,
        "transferred_employees_approximate": 250,
        "building_crosswalk": [
            {"metro": metro, "Verizon_site_name": old, "new_Equinix_IBX_code": new}
            for metro, old, new in EQUINIX_2017_BUILDING_CROSSWALK
        ],
        "FY2016_selected_sites_USD_million": {
            "net_revenue": 451.962,
            "cost_of_services": 135.764,
            "selling_general_and_administrative": 40.755,
            "depreciation": 71.713,
            "total_direct_expenses": 248.232,
            "net_revenue_less_direct_expenses": 203.730,
            "boundary": "Abbreviated carve-out statement excludes corporate overhead, interest, income taxes and cash-flow statements; net revenue less direct expenses is not standalone operating profit.",
        },
        "historical_2016_global_portfolio_disclosures": {
            "owned_and_leased_customer_facing_data_centers": 54,
            "US": 23,
            "Canada": 2,
            "EMEA": 18,
            "Asia_Pacific": 9,
            "South_America": 2,
            "separate_Verizon_annual_report_retained_international_site_statement": 27,
            "boundary": "The 54-center regional table, 24-site/29-building sale and 27 retained international-site statement use different site/building and reporting scopes and are not arithmetically reconciled.",
        },
        "current_boundary": "The 29 acquired buildings are Equinix facilities after closing. Verizon remained a larger customer, partner and reseller, which is not property ownership.",
        "source_urls": [VERIZON_2016_ANNUAL, EQUINIX_2017_COMPLETION, EQUINIX_2017_CARVEOUT],
        "accessed_on": accessed_on,
    })
    records.append({
        "id": "verizon_ai_connect_infrastructure_scope_2025",
        "object_type": "AIInfrastructureServiceAndAssetScopeRecord",
        "US_available_power_MW": "200_plus_across_350_plus_technology_facilities",
        "provider_transcript_site_power_range_MW": "2_to_10_plus_at_many_sites",
        "distributed_telco_facilities": "thousands_with_some_power_space_and_cooling_available",
        "undeveloped_land_acres": "100_to_200",
        "near_net_enterprise_locations": "over_16000",
        "sales_funnel_USD_billion": {"2025_01_more_than": 1, "2025_07_nearly": 2},
        "early_network_capacity_customers": ["Google Cloud", "Meta"],
        "partners": {"GPUaaS": "Vultr", "private_5G_edge_GPU_platform": "NVIDIA", "cloud_fiber": "AWS"},
        "power_boundary": "Available or retrofit-capable power is not energized, leased, utilized, customer-accepted or billed IT load and is not allocated to named sites.",
        "GPU_boundary": "Vultr initially planned to deploy its GPUaaS infrastructure in one Verizon data center; no reviewed source gives model, count, ownership transfer, exact host site, delivery, utilization or economics.",
        "financial_boundary": "Pipeline is not signed backlog or revenue. Verizon does not publish AI Connect or data-center-only revenue, operating profit, capex or cash flow.",
        "source_urls": [GLOBAL_COLOCATION, AI_CONNECT, AI_CONNECT_RELEASE, AI_CONNECT_Q4_2024_TRANSCRIPT, AI_CONNECT_Q2_2025_TRANSCRIPT],
        "accessed_on": accessed_on,
    })
    assert len(records) == 24
    assert len(EQUINIX_2017_BUILDING_CROSSWALK) == 29
    assert len({row["id"] for row in records}) == len(records)
    return records


def load_osm_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("operator") == "Verizon":
            rows.append(row)
    rows.sort(key=lambda row: row["id"])
    assert len(rows) == 13, [row["id"] for row in rows]
    return rows


def build_osm_reviews(rows: list[dict]) -> list[dict]:
    reviews = []
    for row in rows:
        country = row["country_candidates"][0]["iso2"]
        international = country != "US"
        reviews.append({
            "osm_object_id": row["id"],
            "country_code": country,
            "osm_name": row.get("name"),
            "osm_address": row.get("address"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "footprint_area_m2": row.get("footprint_area_m2"),
            "source_url": row["source_url"],
            "classification": "historical_2016_international_portfolio_candidate_current_status_unresolved" if international else "current_or_legacy_US_network_facility_unresolved",
            "exact_current_provider_crosswalk": None,
            "Saint_Denis_match": False,
            "boundary": "An OSM operator tag and footprint do not prove current property ownership, colocation operation, portfolio inclusion, capacity, equipment, GPU inventory or economics.",
        })
    return reviews


def build_summary(records: list[dict], osm_reviews: list[dict], accessed_on: str) -> dict:
    current_types = Counter(row["object_type"] for row in records)
    return {
        "registry": "Verizon data-center current-service, partner, regulatory, sale and OSM evidence registry",
        "accessed_on": accessed_on,
        "records": len(records),
        "record_type_counts": dict(sorted(current_types.items())),
        "current_provider_named_available_capacity_city_records": len(AVAILABLE_CAPACITY_CITIES),
        "current_external_on_net_partner_facility_records": len(ON_NET_PARTNER_FACILITIES),
        "current_exact_regulatory_facility_records": 1,
        "historical_sold_buildings": len(EQUINIX_2017_BUILDING_CROSSWALK),
        "related_operator_tagged_OSM_objects": len(osm_reviews),
        "OSM_country_counts": dict(sorted(Counter(row["country_code"] for row in osm_reviews).items())),
        "OSM_international_historical_candidates": sum(row["country_code"] != "US" for row in osm_reviews),
        "OSM_US_unresolved_network_or_legacy_objects": sum(row["country_code"] == "US" for row in osm_reviews),
        "OSM_exact_current_provider_crosswalks": 0,
        "osm_reviews": osm_reviews,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "FY2025_Verizon_USD_million": {
            "consolidated_revenue": 138191,
            "consolidated_operating_income": 29259,
            "net_income": 17608,
            "net_income_attributable_to_Verizon": 17174,
            "Business_revenue": 29069,
            "Business_segment_operating_income": 2532,
            "Business_segment_EBITDA_derived": 6644,
            "Business_segment_depreciation_and_amortization": 4112,
            "capital_expenditures": 17011,
            "cash_from_operations": 37137,
            "free_cash_flow_non_GAAP": 20126,
            "total_debt": 158150,
            "boundary": "Consolidated and Business-segment results are not data-center-only or AI Connect economics. Business EBITDA is operating income plus segment D&A and differs from consolidated adjusted EBITDA.",
        },
        "Q1_2026_Verizon_USD_billion": {
            "revenue": 34.4,
            "net_income": 5.1,
            "adjusted_EBITDA_non_GAAP": 13.4,
            "cash_from_operations": 8.0,
            "capital_expenditures": 4.2,
            "free_cash_flow_non_GAAP": 3.8,
            "total_unsecured_debt": 142.5,
            "net_unsecured_debt_non_GAAP": 130.1,
            "boundary": "Frontier is included from 2026-01-20. Unsecured debt is not comparable to FY2025 total debt, and results are not data-center-only.",
        },
        "FY2026_guidance_USD_billion": {
            "mobility_and_broadband_service_revenue_approximate": 93,
            "cash_from_operations": "37.5_to_38.0",
            "capital_expenditures": "16.0_to_16.5",
            "free_cash_flow_non_GAAP_at_least": 21.5,
            "adjusted_EPS_USD": "4.95_to_4.99",
        },
        "official_sources": [
            GLOBAL_COLOCATION, ON_NET_COLOCATION, AI_CONNECT, AI_CONNECT_RELEASE,
            AI_CONNECT_Q4_2024_TRANSCRIPT, AI_CONNECT_Q2_2025_TRANSCRIPT,
            FRANCE_2025_DISCLOSURE, FRANCE_2025_WORKBOOK, VERIZON_2016_ANNUAL,
            EQUINIX_2017_COMPLETION, EQUINIX_2017_CARVEOUT, VERIZON_2025_10K,
            VERIZON_Q1_2026,
        ],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/verizon_data_center_evidence_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/verizon_data_center_evidence_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records = build_records(args.accessed_on)
    osm_reviews = build_osm_reviews(load_osm_rows(args.osm))
    summary = build_summary(records, osm_reviews, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "osm_reviews": len(osm_reviews), "registry": str(args.registry), "summary": str(args.summary)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
