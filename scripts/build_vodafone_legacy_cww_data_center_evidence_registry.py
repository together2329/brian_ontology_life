#!/usr/bin/env python3
"""Reconcile Vodafone and legacy Cable & Wireless OSM evidence.

The raw map sample mixes owned or managed data centres, historical CWW labels,
submarine-cable landing stations, duplicate site geometries and businesses that
only license the Vodafone or Cable & Wireless brand.  This builder preserves
those boundaries and keeps dated facility rosters separate from current
country-level marketing and current exact-site certification evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


VODAFONE_COLOCATION = "https://www.vodafone.com/business/products/cloud-and-edge/cloud-services/colocation"
VODAFONE_ESG_2025_DC = "https://reports.investors.vodafone.com/view/997622618/28/"
VODAFONE_ESG_2025_ENERGY = "https://reports.investors.vodafone.com/view/997622618/29/"
VODAFONE_FY26_REPORT = "https://reports.investors.vodafone.com/view/500231330/"
VODAFONE_FY26_RESULTS = "https://www.vodafone.com/~/media/Files/V/vodafone/corp/results-and-presentations/vodafone-fy26-preliminary-results.pdf"
VODAFONE_FY26_RESILIENCE = "https://reports.investors.vodafone.com/view/500231330/59/"
VODAFONE_CWW_ACQUISITION = "https://www.vodafone.com/news/newsroom/corporate-and-financial/cww"
VODAFONE_CWW_INTEGRATION = "https://www.vodafone.com/news/newsroom/services/enterprise-update"
VODAFONE_2013_REPORT = "https://investors.vodafone.com/~/media/files/v/vodafone-ir/documents/performance/financial-results/2013/vodafone-annual-report-2013.pdf"
VODAFONE_2015_REPORT = "https://www.vodafone.com/~/media/Files/V/vodafone/corp/documents/performance/financial-results/2015/full-annual-report-2015.pdf"
VODAFONE_2014_SUSTAINABILITY = "https://www.vodafone.com/content/dam/vodcom/sustainability/pdfs/vodafone_full_report_2014.pdf"
VODAFONE_2010_SUSTAINABILITY = "https://www.vodafone.com/content/dam/vodcom/sustainability/pdfs/vodafone_sustainability_report.pdf"
UK_DC_CCA_2020 = "https://s3.amazonaws.com/thegovernmentsays-files/attachments/177/1777179-1-Umbrella_climate_change_agreement_for_the_data_centre_sector.pdf"
JRC_DC_PARTICIPANTS = "https://e3p.jrc.ec.europa.eu/en/groups/data-centres-code-conduct/participants?order=field_adhesion_date&page=2&partner_search=&sort=desc"
VODAFONE_TURKEY_DC = "https://www.vodafone.com.tr/whosale-services/products-and-solutions/datacenter-solutions"
VODAFONE_TURKEY_TIA = "https://tiaonline.org/wp-content/uploads/2025/08/Turkey_Vodafone-Data-Centre_DCCC_TIA942TR250328001-TIA942-Certificate-Signed.pdf"
VODAFONE_TURKEY_ESG = "https://cms.vodafone.com.tr/static/files/25-02/28/vodafone-turkiye-2024-csy-raporu.pdf"
VODAFONE_BUDE = "https://www.vodafone.com/news/newsroom/technology/vodafone-connects-uk-to-the-world-s-largest-subsea-cable-system"
VODAFONE_SUBSEA = "https://www.vodafone.com/business/solutions/by-business-type/carrier-and-infrastructure-provider/submarine-and-terrestrial-cable"
ONE_NZ_STANDARD_COLOCATION = "https://one.nz/_document/20230321155847/?id=00000187-05bd-d0f2-adc7-dffd91520000"
ONE_NZ_PREMIUM_COLOCATION = "https://one.nz/_document/20230321151004/?id=00000187-0593-d1fd-a597-ed97163c0000"
ONE_NZ_CHRISTCHURCH_SOLAR = "https://media.one.nz/renewable-energy-powers-one-nz-stadium-connectivity"
INFRATIL_ONE_NZ_ACQUISITION = "https://infratil.com/news/completion-of-the-one-new-zealand-acquisition/"
VODAFONE_PNG_ABOUT = "https://vodafone.com.pg/about"
LLA_CW_PANAMA = "https://www.lla.com/blog/cable-wireless-panama-completes-acquisition-of-america-movil-panama-operations"
LIBERTY_CWC_ACQUISITION = "https://www.libertyglobal.com/pdf/press-release/05-16-Closing-CWC-Acquisition-FINAL.pdf"


UK_CCA_2020_SITES = [
    {"name": "Swindon Data Centre", "address": "Windmill Hill Business Park, Whitehill Way, Swindon, SN5 6LA", "agreement_ref": "DATC/F00023"},
    {"name": "Brentford Data Centre", "address": "Great West Plaza, Riverbank Way, London, TW8 9DS", "agreement_ref": "DATC/F00024"},
    {"name": "Gotts Road Data Centre", "address": "Wellington Bridge Industrial Estate, Gotts Road, Leeds, LS12 1AD", "agreement_ref": "DATC/F00025"},
    {"name": "Melbourne Street Data Centre", "address": "The White House, Sheepscar, Leeds, LS2 7PS", "agreement_ref": "DATC/F00026"},
    {"name": "Watford Data Centre Unit 5&6", "address": "Unit 5, Imperial Way, Watford, WD24 4PD", "agreement_ref": "DATC/F00027"},
    {"name": "Uxbridge Data Centre", "address": "Prologis Park, Stockley Park, West Drayton, Uxbridge, UB7 9BN", "agreement_ref": "DATC/F00028"},
    {"name": "Park Royal", "address": "Unit 5-9 Matrix Industrial Park, 900 Coronation Road, London, NW10 7PQ", "agreement_ref": "DATC/F00029"},
]


OSM_DISPOSITIONS = {
    "osm_way_1106581591": {
        "lineage": "Vodafone_Group",
        "site_group": "Berlin_unverified",
        "physical_role": "data_center_candidate",
        "classification": "current_OSM_Vodafone_operator_candidate_without_exact_provider_or_certifier_match",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_166184193": {
        "lineage": "Vodafone_Group_legacy_CWW",
        "site_group": "Swindon",
        "physical_role": "data_center_building_candidate",
        "classification": "OSM_building_exactly_matches_dated_2020_UK_CCA_Vodafone_site",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_117662106": {
        "lineage": "legacy_Cable_Wireless_Worldwide_probable_Vodafone_network",
        "site_group": "Brean_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_444197674": {
        "lineage": "legacy_Cable_Wireless_label_current_title_unverified",
        "site_group": "Porthcurno_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_with_misleading_CWC_website_tag_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_190297843": {
        "lineage": "legacy_Cable_Wireless_Worldwide_probable_Vodafone",
        "site_group": "London_Docklands_legacy_unverified",
        "physical_role": "legacy_data_center_building_candidate",
        "classification": "legacy_CWW_label_current_operation_title_lease_and_service_state_unverified",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_303243253": {
        "lineage": "legacy_Cable_Wireless_Worldwide_probable_Vodafone_network",
        "site_group": "Lanis_1_Blackpool_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_117581892": {
        "lineage": "legacy_Cable_Wireless_Worldwide_probable_Vodafone_network",
        "site_group": "Reynoldston_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_458775807": {
        "lineage": "Vodafone_Group",
        "site_group": "Bude_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "current_provider_confirmed_2Africa_landing_station_not_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_184071840": {
        "lineage": "Vodafone_Group_network_label_current_title_unverified",
        "site_group": "Winterton_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_697464724": {
        "lineage": "Vodafone_Group",
        "site_group": "Dublin",
        "physical_role": "site_or_industrial_area_geometry",
        "classification": "OSM_site_geometry_containing_Vodafone_data_center_building_not_a_second_facility",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_68337079": {
        "lineage": "Vodafone_Group",
        "site_group": "Dublin",
        "physical_role": "data_center_building_candidate",
        "classification": "current_OSM_candidate_supported_by_country_level_owned_managed_hosting_and_historical_Dublin_evidence",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_328914458": {
        "lineage": "One_New_Zealand_not_current_Vodafone_Group",
        "site_group": "Manukau_legacy",
        "physical_role": "legacy_Vodafone_NZ_data_center_candidate",
        "classification": "legacy_brand_label_absent_from_two_reviewed_2023_One_NZ_service_rosters_current_status_unverified",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_1278659480": {
        "lineage": "Cable_Wireless_Panama_Liberty_Latin_America_boundary",
        "site_group": "Panama_unverified",
        "physical_role": "telecom_or_data_center_candidate",
        "classification": "CWC_lineage_not_CWW_or_Vodafone_Group_current_facility",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_1372715027": {
        "lineage": "Vodafone_PNG_ATH_Digitec_licensee_not_Vodafone_Group",
        "site_group": "Papua_New_Guinea_unverified",
        "physical_role": "data_center_candidate",
        "classification": "separate_ATH_and_Austel_owned_operator_not_Vodafone_Group_facility",
        "current_vodafone_group_exact_site_inclusion": False,
    },
    "osm_way_1241724628": {
        "lineage": "Vodafone_Group_Turkiye",
        "site_group": "Esenyurt",
        "physical_role": "current_certified_data_center",
        "classification": "current_TIA_942_Rated_3_exact_site_match",
        "current_vodafone_group_exact_site_inclusion": True,
    },
    "osm_way_459188725": {
        "lineage": "legacy_Cable_Wireless_label_current_title_unverified",
        "site_group": "Shirley_New_York_cable_landing",
        "physical_role": "submarine_cable_landing_station",
        "classification": "network_landing_station_not_counted_as_compute_data_center",
        "current_vodafone_group_exact_site_inclusion": False,
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {
        row["id"]: row
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
        for row in [json.loads(line)]
    }


def build_records(osm: dict[str, dict], accessed_on: str) -> list[dict]:
    records = []
    for source_order, (osm_ref, disposition) in enumerate(OSM_DISPOSITIONS.items(), 1):
        source = osm[osm_ref]
        country = source.get("country_candidates", [{}])[0]
        row = {
            "id": f"vodafone_legacy_cww_{osm_ref}",
            "object_type": "DataCenterOrTelecomGeometryEvidence",
            "source_order": source_order,
            "OSM_ref": osm_ref,
            "OSM_name": source.get("name"),
            "OSM_operator": source.get("operator"),
            "OSM_owner": source.get("owner"),
            "OSM_website": source.get("website"),
            "country_code": country.get("iso2"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "OSM_footprint_area_m2": source.get("footprint_area_m2"),
            "OSM_source_url": source["source_url"],
            **disposition,
            "accessed_on": accessed_on,
        }
        if disposition["physical_role"] == "submarine_cable_landing_station":
            row["counting_boundary"] = "A cable landing station can contain telecom and power equipment but is not counted as a compute, hosting or colocation data center without separate provider evidence."
        elif disposition["site_group"] == "Dublin":
            row["counting_boundary"] = "The industrial/site polygon and nested building are one candidate Dublin site group, not two facilities; OSM footprint is not gross floor, whitespace or IT area."
        elif disposition["site_group"] == "Esenyurt":
            row["current_exact_site_evidence"] = "TIA certificate valid 2025-03-28 through 2028-03-27, initially certified 2022-03-28, rates architecture, telecom, electrical and mechanical scope Rated-3."
            row["counting_boundary"] = "One exact current certified facility. The OSM footprint is not certified whitespace, gross floor area, IT load or operating power."
        elif disposition["site_group"] == "Manukau_legacy":
            row["current_operator_boundary"] = "Vodafone New Zealand was renamed One New Zealand and is 99.9% owned by Infratil; the reviewed One NZ documents name other service sites and do not establish Manukau's current status."
        elif disposition["site_group"] == "Panama_unverified":
            row["current_operator_boundary"] = "Cable & Wireless Panama is a 49%-owned Liberty Latin America subsidiary and is unrelated to Vodafone's acquisition of Cable & Wireless Worldwide for current counting."
        elif disposition["site_group"] == "Papua_New_Guinea_unverified":
            row["current_operator_boundary"] = "Vodafone PNG says it is Digitec Communications, a subsidiary of ATH and Austel, managed through Vodafone Fiji; the brand does not prove Vodafone Group ownership."
        else:
            row["counting_boundary"] = "OSM identity and footprint do not establish current legal title, lease, operation, service availability, live IT load or financial contribution."
        records.append(row)

    assert len(records) == 16
    assert sum(row["physical_role"] == "submarine_cable_landing_station" for row in records) == 7
    assert sum(row["current_vodafone_group_exact_site_inclusion"] for row in records) == 1
    assert sum(row["site_group"] == "Dublin" for row in records) == 2
    return records


def build_summary(records: list[dict], osm_path: Path, accessed_on: str) -> dict:
    return {
        "id": "vodafone_legacy_cww_data_center_evidence_summary_2026_07_19",
        "operator": "Vodafone Group with legacy Cable & Wireless Worldwide boundary",
        "accessed_on": accessed_on,
        "portfolio_reconciliation": {
            "related_OSM_objects": len(records),
            "raw_Vodafone_operator_rows": 5,
            "raw_Cable_Wireless_operator_rows": 5,
            "raw_Vodafone_Turkiye_operator_rows": 1,
            "additional_name_only_related_rows": 5,
            "cable_landing_station_rows_excluded_from_compute_facility_counts": 7,
            "Dublin_geometries_grouped_to_one_candidate_site": 2,
            "current_exact_provider_or_certifier_listed_Vodafone_Group_site_floor": 2,
            "current_exact_site_floor_names": ["Rehhecke_Ratingen", "Esenyurt_Istanbul"],
            "OSM_objects_in_current_exact_site_floor": 1,
            "current_owned_or_managed_hosting_country_evidence": ["United_Kingdom", "Germany", "Ireland"],
            "complete_current_direct_global_facility_or_building_count": "undisclosed",
            "boundary": "Two is an exact-site evidence floor, not Vodafone's global fleet count. The seven-site UK roster is dated 2020, the 18-site disclosure is dated FY2015, country-level hosting does not disclose buildings, and partner data centers are not Vodafone physical inventory.",
        },
        "current_and_dated_facility_evidence": {
            "current_exact_site_floor": {
                "Ratingen": {
                    "current_list_name": "Vodafone Group Service GmbH - Rehhecke, Ratingen",
                    "address": "Rehhecke 50, 40885 Ratingen, Germany",
                    "evidence": "Current European Commission JRC participant page; adhesion year 2012",
                    "OSM_match_in_reviewed_rows": False,
                    "current_operating_IT_MW_racks_servers_and_complete_BOM": "undisclosed",
                },
                "Esenyurt": {
                    "address_scope": "Esenyurt 34510, Istanbul, Turkey",
                    "TIA_942_certificate": "TIA942TR250328001",
                    "rating": "Rated_3_architecture_telecom_electrical_mechanical",
                    "initial_certification": "2022-03-28",
                    "certificate_valid_from": "2025-03-28",
                    "certificate_valid_until": "2028-03-27",
                    "OSM_ref": "osm_way_1241724628",
                    "OSM_footprint_area_m2": 3875.595,
                    "current_operating_IT_MW_racks_servers_and_complete_BOM": "undisclosed",
                },
            },
            "current_country_level_owned_or_managed_hosting": {
                "countries": ["United_Kingdom", "Germany", "Ireland"],
                "evidence": "FY2025 ESG methodology says Vodafone provides shared centralized hosting through data centres it owns and manages and gives country-level Vodafone data-centre factors for the UK, Germany and Ireland.",
                "exact_current_site_roster_and_count": "not_disclosed",
            },
            "UK_2020_climate_change_agreement": {
                "agreement_date": "2020-12-18",
                "facility_rows": UK_CCA_2020_SITES,
                "facility_count": len(UK_CCA_2020_SITES),
                "current_revalidation_status": "not_established",
                "OSM_exact_match": "Swindon_only",
                "boundary": "The seven rows are a dated regulatory-agreement roster and are not asserted as the current 2026 UK fleet.",
            },
            "historical_FY2015": {
                "data_centers": 18,
                "customers_more_than": 1200,
                "geographies": ["United_Kingdom", "Ireland", "Germany", "Africa"],
                "partner_network_also_used": True,
                "boundary": "Historical portfolio statement only; it is not a 2026 building, ownership or operating count.",
            },
            "current_marketing_scope": {
                "global_data_center_space_m2_more_than": 800000,
                "Equinix_and_Digital_Realty_partner_data_centers_more_than": 165,
                "availability_percent_more_than": 99.982,
                "can_run_without_electricity_up_to_days": 30,
                "direct_current_Vodafone_site_count": "not_disclosed",
                "boundary": "The page does not allocate the 800,000-square-metre headline between Vodafone-owned, managed, leased, customer, partner or other space. The 165-plus partner centers are explicitly Equinix/Digital Realty access, not Vodafone physical facilities.",
            },
        },
        "corporate_lineage": {
            "Cable_Wireless_Worldwide": {
                "Vodafone_acquisition_effective": "2012-07-27",
                "integration": "CWW Technology integrated with Group Technology and hosting/cloud became a worldwide enterprise unit",
                "acquired_network_context": {"UK_fiber_km": 20500, "international_cable_network_km": 425000},
                "boundary": "Legacy UK CWW map labels route to Vodafone for research, but acquisition does not prove that each mapped building remains owned, leased, operated or used as a data center in 2026.",
            },
            "Cable_Wireless_Communications": {
                "separated_from_CWW": "2010_demerger",
                "Liberty_Global_acquisition_completed": "2016-05-16",
                "current_regional_parent_boundary": "Liberty_Latin_America_for_CW_Panama_and_regional_CW_businesses",
                "boundary": "CWC, C&W Panama and cwc.com are not evidence of Vodafone Group ownership.",
            },
            "One_New_Zealand": {
                "former_brand": "Vodafone_New_Zealand",
                "current_parent": "Infratil",
                "Infratil_ownership_percent": 99.9,
                "current_service_documents": {
                    "standard_sites": ["Albany", "Hamilton", "Avalon_Lower_Hutt"],
                    "premium_sites": ["Orbit_Auckland", "Kapua_Hamilton", "Abel_Wellington", "Gloucester_Christchurch"],
                    "overlap_and_product_boundary": "The two 2023 service descriptions use separate product and site naming scopes; they are not summed into a seven-site current fleet without a provider bridge.",
                },
                "Manukau_OSM_status": "legacy_brand_candidate_absent_from_reviewed_current_service_rosters",
            },
            "Vodafone_PNG": {
                "legal_operator": "Digitec_Communications_Limited",
                "ownership": "ATH_and_Austel_Investment",
                "management": "assigned_to_Vodafone_Fiji",
                "boundary": "Brand affiliation is not Vodafone Group physical ownership or consolidated-site evidence.",
            },
        },
        "power_cooling_and_environment": {
            "current_group_energy_FY2026": {
                "total_energy_GWh": 5966.56,
                "mobile_fixed_access_network_and_technology_centres_GWh": 5648,
                "purchased_electricity_from_renewable_sources_percent": 100,
                "boundary": "Network and technology-centre energy combines radio, fixed network and other technology infrastructure; it is not a data-center-only denominator. Renewable matching is not onsite generation or hourly carbon-free supply.",
            },
            "historical_efficiency": {
                "FY2010_Ratingen_PUE": 1.47,
                "FY2010_Dublin_PUE": 1.61,
                "FY2014_global_and_regional_average_PUE": 1.49,
                "boundary": "Historical PUE values are not current site PUE and cannot be applied to the 2026 estate.",
            },
            "Esenyurt_and_Turkiye_2023_24": {
                "TIA_resilience": "Rated_3_architecture_telecom_electrical_mechanical",
                "rooftop_solar_investment_TRY_million": 3.2,
                "reported_installed_solar_value": 475,
                "reported_installed_solar_unit": "kWh_as_printed_unit_inconsistent_with_power_capacity",
                "solar_generation_2022_23_MWh": 517,
                "solar_generation_2023_24_MWh": 489,
                "solar_avoided_2023_24_tCO2e": 234,
                "four_data_center_VFD_annual_energy_savings_MWh": 1100,
                "four_data_center_VFD_avoided_tCO2": 525,
                "AI_thermal_management_reported_PUE_improvement_percent": 10,
                "AI_thermal_management_reported_cooling_energy_savings_up_to_percent": 30,
                "Turkey_total_electricity_matched_renewable_MWh": 637785,
                "boundary": "The solar figure preserves the report's inconsistent kWh capacity unit. Portfolio VFD, AI thermal and renewable-electricity measures are not all Esenyurt-only, do not disclose baseline PUE, and are not current IT load.",
            },
            "One_NZ_service_engineering_separate_group": {
                "standard_product": {"A_and_B_feeds": True, "emergency_diesel_generator": True, "battery_runtime_minutes": 20, "full_rack_load_W": 2000, "full_rack_monthly_allocation_kWh": 1488},
                "premium_product": {"full_rack_average_limit_kW": 6.2, "single_rack_limit_without_approval_kW": 12, "Orbit_power_availability_percent": 99.995, "Kapua_power_availability_percent": 99.995, "Abel_power_availability_percent": 99.982, "Gloucester_power_availability_percent": 99.95},
                "Christchurch_solar_2026": {"panel_count": 142, "panel_unit_W": 580, "derived_module_nameplate_kW": 82.36, "three_phase_inverter_kW": 110, "stated_peak_output_up_to_kW": 90},
                "boundary": "These are One NZ service and Christchurch values, not Vodafone Group capacity and not evidence for Manukau's current state.",
            },
            "complete_current_site_power_chain": "grid_feeds_substations_transformers_switchgear_PDU_UPS_batteries_generators_fuel_chillers_CRAH_CRAC_CDU_OEM_model_counts_ratings_loading_acceptance_age_and_remaining_life_undisclosed",
        },
        "accelerators_and_AI": {
            "current_Vodafone_owned_or_leased_GPU_model_count_by_site": "not_publicly_disclosed_or_established",
            "current_customer_or_partner_GPU_inventory_on_Vodafone_colocation": "not_publicly_disclosed_or_established",
            "AI_evidence": ["Turkey_AI_supported_digital_thermal_management", "Vodafone_operational_and_customer_service_AI", "cloud_and_hyperscaler_partnerships"],
            "boundary": "AI services, thermal-control algorithms, hyperscaler consolidation, partner data-center access and support for neocloud customers do not establish physical GPU model, count, owner, delivery, site allocation or utilization.",
        },
        "ownership_and_financials": {
            "listing": "London_Stock_Exchange_VOD",
            "ownership": "public_listed_group",
            "FY2026_EUR_million": {
                "revenue": 40461,
                "service_revenue": 33480,
                "operating_profit": 2844,
                "profit_for_financial_year_continuing_operations": 59,
                "adjusted_EBITDAaL": 11351,
                "cash_inflow_from_operating_activities": 14291,
                "adjusted_free_cash_flow": 2621,
                "capital_additions": 7291,
                "net_debt": 25411,
            },
            "FY2025_comparative_EUR_million": {
                "revenue": 37448,
                "operating_loss": 411,
                "loss_for_financial_year_continuing_operations": 3724,
                "adjusted_EBITDAaL": 10932,
                "cash_inflow_from_operating_activities": 15373,
                "adjusted_free_cash_flow": 2548,
                "capital_additions": 6862,
                "net_debt": 22397,
            },
            "derived_FY2026": {
                "operating_margin_percent": 7.029,
                "adjusted_EBITDAaL_margin_percent": 28.054,
                "capital_additions_to_revenue_percent": 18.019,
            },
            "data_center_segment_and_site_revenue_operating_profit_cash_flow_capex_ROIC_and_customer_economics": "undisclosed",
            "boundary": "Vodafone is a diversified telecom group. Company revenue, profit, cash flow, capex and debt cannot be allocated to data centers, cable landing stations, partner facilities or individual countries without a segment and cost bridge.",
        },
        "outlook": {
            "FY2027_guidance": {"adjusted_EBITDAaL_EUR_billion": "11.9_to_12.2", "adjusted_free_cash_flow_EUR_billion": "2.6_to_2.9", "Europe_adjusted_EBITDAaL_EUR_billion": "7.6_to_7.9", "restructuring_and_integration_costs_EUR_billion_approx": 0.7},
            "medium_term": {"organic_adjusted_free_cash_flow_growth": "double_digit", "EU_opex_reduction_FY2027_to_FY2030_EUR_billion": 1, "UK_annual_cost_and_capex_synergies_by_FY2030_GBP_million": 700},
            "positive_signals": ["current_owned_managed_hosting_in_three_named_European_countries", "current_Ratingen_and_Esenyurt_exact_site_evidence", "large_global_fiber_subsea_and_partner_reach", "FY2026_revenue_EBITDAaL_and_operating_profit_improvement", "FY2027_profit_and_cash_flow_growth_guidance", "renewable_matching_and_site_efficiency_programs"],
            "risk_signals": ["strategic_data_center_consolidation_to_hyperscalers", "complete_current_direct_site_count_and_MW_undisclosed", "legacy_and_brand_license_map_labels", "partner_versus_direct_portfolio_ambiguity", "GPU_inventory_and_site_economics_undisclosed", "integration_restructuring_competition_regulatory_cyber_and_network_resilience_risk", "higher_net_debt_after_VodafoneThree_consolidation"],
            "analytical_view": "Vodafone offers listed connectivity, enterprise hosting and subsea-network exposure rather than a data-center pure play. Current exact-site evidence is thin relative to broad marketing, and consolidation toward hyperscalers makes partner reach and direct owned capacity especially important to keep separate.",
        },
        "OSM_crosswalk": {
            "records": [{key: row.get(key) for key in ["OSM_ref", "OSM_name", "OSM_operator", "country_code", "site_group", "physical_role", "classification", "OSM_footprint_area_m2", "current_vodafone_group_exact_site_inclusion"]} for row in records],
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
        },
        "sources": [
            VODAFONE_COLOCATION, VODAFONE_ESG_2025_DC, VODAFONE_ESG_2025_ENERGY,
            VODAFONE_FY26_REPORT, VODAFONE_FY26_RESULTS, VODAFONE_FY26_RESILIENCE,
            VODAFONE_CWW_ACQUISITION, VODAFONE_CWW_INTEGRATION, VODAFONE_2013_REPORT,
            VODAFONE_2015_REPORT, VODAFONE_2014_SUSTAINABILITY, VODAFONE_2010_SUSTAINABILITY,
            UK_DC_CCA_2020, JRC_DC_PARTICIPANTS, VODAFONE_TURKEY_DC, VODAFONE_TURKEY_TIA,
            VODAFONE_TURKEY_ESG, VODAFONE_BUDE, VODAFONE_SUBSEA,
            ONE_NZ_STANDARD_COLOCATION, ONE_NZ_PREMIUM_COLOCATION, ONE_NZ_CHRISTCHURCH_SOLAR,
            INFRATIL_ONE_NZ_ACQUISITION, VODAFONE_PNG_ABOUT, LLA_CW_PANAMA,
            LIBERTY_CWC_ACQUISITION,
        ],
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
    registry_path = args.output_dir / "vodafone_legacy_cww_data_center_evidence_registry.jsonl"
    summary_path = args.output_dir / "vodafone_legacy_cww_data_center_evidence_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
