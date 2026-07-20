#!/usr/bin/env python3
"""Build a scope-safe IBM Cloud and Kyndryl facility-boundary registry.

IBM publishes cloud service-location codes and accelerator product availability,
not a complete legal building, ownership, MW or installed-GPU ledger.  Kyndryl
publishes selected certification sites after its 2021 separation from IBM, not a
complete global fleet.  This builder retains both scopes and crosswalks legacy
IBM/Kyndryl OpenStreetMap labels without treating them as interchangeable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


IBM_LOCATIONS = "https://cloud.ibm.com/docs/overview?topic=overview-locations"
IBM_CLOSURES = "https://cloud.ibm.com/docs/account?topic=account-dc-closure"
IBM_FACILITIES = "https://www.ibm.com/solutions/cloud-data-centers"
IBM_VPC_PROFILES = "https://cloud.ibm.com/docs/vpc?interface=cli&topic=vpc-profiles"
IBM_ACCEL_GEN3 = "https://cloud.ibm.com/docs/vpc?interface=ui&topic=vpc-accelerated-profile-family"
IBM_ACCEL_GEN4 = "https://cloud.ibm.com/docs/vpc?topic=vpc-accelerated-profile-family-gen4"
IBM_VELA_PAPER = "https://research.ibm.com/publications/vela-a-virtualized-llm-training-system-with-gpu-direct-and-roce"
IBM_VELA_LAUNCH = "https://research.ibm.com/blog/AI-supercomputer-Vela-GPU-cluster"
IBM_VELA_UPDATE = "https://research.ibm.com/blog/vela-ai-supercomputer-updates"
IBM_BLUE_VELA = "https://research.ibm.com/blog/ibm-storage-scale-mlperf"
IBM_2025_10K = "https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/ibm-20251231_d2.htm"
IBM_2025_LETTER = "https://www.ibm.com/downloads/documents/us-en/15db1aa422b5a2d8"

KYNDRYL_CERTIFICATIONS = "https://www.kyndryl.com/us/en/compliance/certifications"
KYNDRYL_FR_ISO22301 = "https://www.kyndryl.com/content/dam/kyndrylprogram/certifications/iso22301/kyndryl_france_iso_22301_2019_01_feb_2029.pdf"
KYNDRYL_FR_HDS = "https://www.kyndryl.com/content/dam/kyndrylprogram/certifications/hds/kyndryl_france_hds_30_jul_25.pdf"
KYNDRYL_DE_ISO27001 = "https://www.kyndryl.com/content/dam/kyndrylprogram/certifications/iso27001/kyndryl_germany_iso_27001_31_oct_2025.pdf"
KYNDRYL_STRATEGY = "https://www.kyndryl.com/ie/en/about-us/news/2026/05/hybrid-it-modern-data-center-strategy"
KYNDRYL_2026_10K = "https://www.sec.gov/Archives/edgar/data/1867072/000110465926067881/kd-20260331x10k.htm"
KYNDRYL_FY2026_RESULTS = "https://investors.kyndryl.com/news-releases/news-release-details/kyndryl-reports-fourth-quarter-and-full-year-2026-results"
IBM_KYNDRYL_SEPARATION = "https://newsroom.ibm.com/2021-11-03-IBM-Completes-the-Separation-of-Kyndryl"


CLASSIC_CODES = [
    "DAL08", "DAL09", "DAL10", "DAL12", "DAL13", "DAL14", "MON01", "SJC03", "SJC04",
    "SAO01", "SAO04", "SAO05", "TOR01", "TOR04", "TOR05", "WDC03", "WDC04", "WDC06", "WDC07",
    "AMS03", "FRA02", "FRA04", "FRA05", "LON02", "LON04", "LON05", "LON06", "MAD02", "MAD04",
    "MAD05", "PAR01", "CHE01", "OSA21", "OSA22", "OSA23", "SNG01", "SYD01", "SYD04", "SYD05",
    "TOK02", "TOK04", "TOK05",
]

REGION_CODES = {
    "us-south_Dallas": ("normal_multizone_region", ["DAL10", "DAL12", "DAL13", "DAL14"]),
    "br-sao_Sao_Paulo": ("normal_multizone_region", ["SAO01", "SAO04", "SAO05"]),
    "ca-tor_Toronto": ("normal_multizone_region", ["TOR01", "TOR04", "TOR05"]),
    "us-east_Washington_DC": ("normal_multizone_region", ["WDC04", "WDC06", "WDC07"]),
    "eu-de_Frankfurt": ("normal_multizone_region", ["FRA02", "FRA04", "FRA05"]),
    "eu-gb_London": ("normal_multizone_region", ["LON04", "LON05", "LON06"]),
    "eu-es_Madrid": ("normal_multizone_region", ["MAD02", "MAD04", "MAD05"]),
    "au-syd_Sydney": ("normal_multizone_region", ["SYD01", "SYD04", "SYD05"]),
    "jp-tok_Tokyo": ("normal_multizone_region", ["TOK02", "TOK04", "TOK05"]),
    "in-che_Chennai": ("single_campus_multizone_region", ["CHE02"]),
    "ca-mon_Montreal": ("single_campus_multizone_region", ["MON04"]),
    "in-mum_Mumbai": ("single_campus_multizone_region", ["MUM02", "MUM03", "MUM05"]),
    "jp-osa_Osaka": ("single_campus_multizone_region", ["OSA21", "OSA22", "OSA23"]),
}

PREFIX_GEOGRAPHY = {
    "DAL": ("United States", "Dallas", "US"),
    "MON": ("Canada", "Montreal", "CA"),
    "SJC": ("United States", "San Jose", "US"),
    "SAO": ("Brazil", "Sao Paulo", "BR"),
    "TOR": ("Canada", "Toronto", "CA"),
    "WDC": ("United States", "Washington DC area", "US"),
    "AMS": ("Netherlands", "Amsterdam", "NL"),
    "FRA": ("Germany", "Frankfurt", "DE"),
    "LON": ("United Kingdom", "London", "GB"),
    "MAD": ("Spain", "Madrid", "ES"),
    "PAR": ("France", "Paris", "FR"),
    "CHE": ("India", "Chennai", "IN"),
    "MUM": ("India", "Mumbai", "IN"),
    "OSA": ("Japan", "Osaka", "JP"),
    "SNG": ("Singapore", "Singapore", "SG"),
    "SYD": ("Australia", "Sydney", "AU"),
    "TOK": ("Japan", "Tokyo", "JP"),
}

EXACT_ACCELERATOR_CODES = {
    "Gaudi3": {"DAL12", "WDC06", "WDC07", "FRA02"},
    "H100": {"DAL10", "WDC06", "WDC07", "TOR05", "SAO01", "FRA04", "LON05", "MAD05", "SYD04", "TOK05"},
    "H200": {"WDC06", "WDC07", "TOR05", "FRA04", "LON05", "SYD05", "CHE02"},
    "B300": {"WDC07"},
}

KYNDRYL_CERTIFIED_SITE_GROUPS = [
    {
        "id": "kyndryl_fr_montpellier_grabels",
        "country": "France",
        "country_code": "FR",
        "site_group": "Montpellier & Grabels",
        "named_components": ["Montpellier", "Grabels"],
        "address_as_published": "Certificate site-group label; exact full addresses are not transcribed in this registry.",
        "certification": "France ISO 22301 certificate; Grabels also appears in the reviewed HDS certificate.",
        "sources": [KYNDRYL_FR_ISO22301, KYNDRYL_FR_HDS],
    },
    {
        "id": "kyndryl_fr_clermont_i_ii",
        "country": "France",
        "country_code": "FR",
        "site_group": "Clermont I & II",
        "named_components": ["Clermont I", "Clermont II"],
        "address_as_published": "Certificate site-group label; exact full addresses are not transcribed in this registry.",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_fr_collegien_i_ii",
        "country": "France",
        "country_code": "FR",
        "site_group": "Collégien I & II",
        "named_components": ["Collégien I", "Collégien II"],
        "address_as_published": "35 Allée du Clos des Charmes, Collégien, France",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_fr_clichy_i_ii",
        "country": "France",
        "country_code": "FR",
        "site_group": "Clichy I & II",
        "named_components": ["Clichy I", "Clichy II"],
        "address_as_published": "7-9 rue Petit, Clichy, France",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_fr_seclin",
        "country": "France",
        "country_code": "FR",
        "site_group": "Seclin",
        "named_components": ["Seclin"],
        "address_as_published": "14 rue de Lorival, Seclin, France",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_fr_venissieux",
        "country": "France",
        "country_code": "FR",
        "site_group": "Vénissieux",
        "named_components": ["Vénissieux"],
        "address_as_published": "Rue Marrane, Vénissieux, France",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_fr_marcoussis",
        "country": "France",
        "country_code": "FR",
        "site_group": "Marcoussis",
        "named_components": ["Marcoussis"],
        "address_as_published": "3 route de Marcoussis, Nozay, France",
        "certification": "France ISO 22301 certificate",
        "sources": [KYNDRYL_FR_ISO22301],
    },
    {
        "id": "kyndryl_de_kelsterbach",
        "country": "Germany",
        "country_code": "DE",
        "site_group": "DC Kelsterbach",
        "named_components": ["DC Kelsterbach"],
        "address_as_published": "Am Weiher 24, Kelsterbach, Germany",
        "certification": "Germany ISO 27001 certificate",
        "sources": [KYNDRYL_DE_ISO27001],
    },
    {
        "id": "kyndryl_de_schwalbach_eschborn",
        "country": "Germany",
        "country_code": "DE",
        "site_group": "DC Schwalbach",
        "named_components": ["DC Schwalbach"],
        "address_as_published": "Bismarckstr. 2, Eschborn, Germany",
        "certification": "Germany ISO 27001 certificate",
        "sources": [KYNDRYL_DE_ISO27001],
    },
    {
        "id": "kyndryl_de_oberursel",
        "country": "Germany",
        "country_code": "DE",
        "site_group": "DC Oberursel",
        "named_components": ["DC Oberursel"],
        "address_as_published": "Gablonzer Str. 34, Oberursel, Germany",
        "certification": "Germany ISO 27001 certificate",
        "sources": [KYNDRYL_DE_ISO27001],
    },
    {
        "id": "kyndryl_de_ruesselsheim",
        "country": "Germany",
        "country_code": "DE",
        "site_group": "DC Rüsselsheim",
        "named_components": ["DC Rüsselsheim"],
        "address_as_published": "Karl-Landsteiner-Ring 4, Rüsselsheim, Germany",
        "certification": "Germany ISO 27001 certificate",
        "sources": [KYNDRYL_DE_ISO27001],
    },
]

OSM_CROSSWALK = {
    "osm_relation_1604367": ("kyndryl_fr_collegien_i_ii", "legacy_IBM_label_matches_current_Kyndryl_certified_site_group_but_not_one_to_one_building_allocation"),
    "osm_way_113167016": ("kyndryl_fr_collegien_i_ii", "legacy_IBM_label_matches_current_Kyndryl_certified_site_group_but_not_one_to_one_building_allocation"),
    "osm_way_125557451": ("kyndryl_fr_seclin", "legacy_IBM_label_and_city_match_current_Kyndryl_certified_site_group"),
    "osm_way_66911687": ("kyndryl_fr_clermont_i_ii", "legacy_IBM_label_matches_current_Kyndryl_certified_site_group_but_three_OSM_objects_cannot_map_one_to_one_to_I_and_II"),
    "osm_way_91286607": ("kyndryl_fr_clermont_i_ii", "legacy_IBM_label_matches_current_Kyndryl_certified_site_group_but_three_OSM_objects_cannot_map_one_to_one_to_I_and_II"),
    "osm_way_91288538": ("kyndryl_fr_clermont_i_ii", "legacy_IBM_label_matches_current_Kyndryl_certified_site_group_but_three_OSM_objects_cannot_map_one_to_one_to_I_and_II"),
    "osm_way_82894448": ("kyndryl_fr_montpellier_grabels", "legacy_IBM_Grabels_label_matches_current_Kyndryl_certified_site_group"),
    "osm_way_26225758": ("kyndryl_de_schwalbach_eschborn", "current_Kyndryl_operator_and_city_match_certified_DC_Schwalbach_address_in_Eschborn"),
    "osm_way_38754141": ("kyndryl_de_oberursel", "current_Kyndryl_operator_and_city_match_certified_DC_Oberursel"),
    "osm_way_128487593": (None, "legacy_IBM_Horsham_label_with_RSA_owner_current_facility_operator_and_lifecycle_unconfirmed"),
    "osm_way_1295392065": (None, "Chile_IBM_name_only_candidate_without_current_IBM_Cloud_or_Kyndryl_official_bridge"),
    "osm_way_368613614": (None, "Spain_IBM_name_only_candidate_without_current_IBM_Cloud_or_Kyndryl_official_bridge"),
    "osm_way_218905097": (None, "Kyndryl_UK_name_only_candidate_not_present_in_selected_France_or_Germany_certificate_scope"),
    "osm_way_205832460": (None, "New_Zealand_IBM_name_only_candidate_without_current_official_bridge"),
    "osm_way_258519934": (None, "IBM_owner_tag_near_Washington_service_market_without_code_to_building_bridge"),
    "osm_way_258519959": (None, "IBM_owner_tag_near_Washington_service_market_without_code_to_building_bridge"),
    "osm_way_69827429": (None, "Albany_commercial_IBM_Building_with_telecom_tag_not_proven_as_current_data_center"),
    "osm_way_195803647": (None, "IBM_Quantum_Data_Center_is_a_separate_quantum_facility_not_a_public_IBM_Cloud_code_bridge"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_ibm_records(accessed_on: str) -> list[dict]:
    region_membership: dict[str, list[dict]] = {}
    for region, (region_type, codes) in REGION_CODES.items():
        for code in codes:
            region_membership.setdefault(code, []).append({"region": region, "region_type": region_type})
    all_codes = sorted(set(CLASSIC_CODES) | set(region_membership))
    rows = []
    for code in all_codes:
        country, market, country_code = PREFIX_GEOGRAPHY[re.match(r"[A-Z]+", code).group(0)]
        accelerators = sorted(model for model, codes in EXACT_ACCELERATOR_CODES.items() if code in codes)
        rows.append({
            "id": f"ibm_cloud_physical_code_{code.lower()}",
            "object_type": "CloudPhysicalDataCenterCodeEvidence",
            "provider": "IBM Cloud",
            "physical_data_center_code": code,
            "country": country,
            "country_code": country_code,
            "market_or_city": market,
            "classic_infrastructure_table": code in CLASSIC_CODES,
            "cloud_region_memberships": region_membership.get(code, []),
            "record_granularity": "provider_published_physical_data_center_code_not_a_proven_single_building_or_legal_property",
            "lifecycle_as_of_2026_07_19": "currently_listed_but_exact_closure_flag_unknown",
            "closure_boundary": "IBM says the classic table can include data centers set to close soon, but the reviewed closure page does not identify the affected code roster.",
            "street_address_legal_title_lease_and_physical_operator": "undisclosed_by_code",
            "published_power_mw_area_PUE_WUE_and_equipment_BOM": "undisclosed_by_code",
            "exact_code_accelerator_product_availability": accelerators,
            "accelerator_boundary": "A product profile can be ordered at this code; it is not an installed fleet count, owner ledger, utilization measure or proof that inventory is continuously available.",
            "source_urls": [IBM_LOCATIONS] + ([IBM_ACCEL_GEN3] if set(accelerators) & {"Gaudi3", "H100", "H200"} else []) + ([IBM_ACCEL_GEN4] if "B300" in accelerators else []),
            "accessed_on": accessed_on,
        })
    assert len(CLASSIC_CODES) == 42
    assert len(REGION_CODES) == 13
    assert sum(1 for kind, _ in REGION_CODES.values() if kind == "normal_multizone_region") == 9
    assert sum(1 for kind, _ in REGION_CODES.values() if kind == "single_campus_multizone_region") == 4
    assert len({code for kind, codes in REGION_CODES.values() if kind == "normal_multizone_region" for code in codes}) == 28
    assert len({code for kind, codes in REGION_CODES.values() if kind == "single_campus_multizone_region" for code in codes}) == 8
    assert len(rows) == 47
    assert len({row["physical_data_center_code"] for row in rows}) == 47
    return rows


def build_kyndryl_records(accessed_on: str) -> list[dict]:
    rows = []
    for source in KYNDRYL_CERTIFIED_SITE_GROUPS:
        rows.append({
            **{key: value for key, value in source.items() if key != "sources"},
            "object_type": "CertifiedDataCenterSiteGroupEvidence",
            "operator": "Kyndryl",
            "record_granularity": "certification_site_group_not_a_complete_global_fleet_or_legal_property_ledger",
            "lifecycle_as_of_2026_07_19": "present_in_current_reviewed_certification_scope",
            "published_capacity": {},
            "power_cooling_GPU_and_site_economics": "not_disclosed_by_this_certificate_record",
            "ownership_boundary": "The certificate proves a Kyndryl operational or certification scope at the named site; it does not by itself prove title, lease, building count, MW or exclusive operation.",
            "source_urls": source["sources"],
            "accessed_on": accessed_on,
        })
    assert len(rows) == 11
    assert Counter(row["country_code"] for row in rows) == {"FR": 7, "DE": 4}
    assert sum(len(row["named_components"]) for row in rows) == 15
    return rows


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (registry_ref, classification) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        rows.append({
            "osm_ref": osm_ref,
            "registry_ref": registry_ref,
            "classification": classification,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "raw_owner": source.get("owner"),
            "address": source.get("address"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "counting_rule": "OSM is a location crosswalk only. This object contributes no extra facility, MW or GPU count.",
        })
    assert len(rows) == 18
    assert Counter(row["raw_operator"] for row in rows) == {None: 8, "IBM": 8, "Kyndryl Deutschland GmbH": 2}
    return rows


def build_summary(records: list[dict], osm_rows: list[dict], osm_path: Path, accessed_on: str) -> dict:
    ibm_rows = [row for row in records if row["object_type"] == "CloudPhysicalDataCenterCodeEvidence"]
    kyndryl_rows = [row for row in records if row["object_type"] == "CertifiedDataCenterSiteGroupEvidence"]
    return {
        "id": "ibm_cloud_kyndryl_boundary_summary_2026_07_19",
        "accessed_on": accessed_on,
        "registry_scope": {
            "total_records": len(records),
            "IBM_Cloud_physical_code_records": len(ibm_rows),
            "Kyndryl_selected_certification_site_group_records": len(kyndryl_rows),
            "boundary": "IBM Cloud codes and Kyndryl certification sites are different sources, legal entities and granularities. They are not added into a single fleet count.",
        },
        "IBM_Cloud_location_reconciliation": {
            "current_classic_table_codes": 42,
            "normal_multizone_regions": 9,
            "normal_multizone_physical_codes": 28,
            "single_campus_multizone_regions": 4,
            "single_campus_multizone_physical_codes": 8,
            "all_regions": 13,
            "union_unique_physical_codes": 47,
            "physical_building_lower_bound": "not_inferred_because_a_code_can_represent_a_building_or_campus_scope_and_SC_MZR_dependencies_can_overlap",
            "closure_state": "IBM says some classic codes are set to close soon but the reviewed page does not publish the affected code list.",
            "excluded_scope": "network points of presence are not counted as physical data-center codes",
        },
        "IBM_Cloud_power_cooling_and_facility_design": {
            "portfolio_level_features": [
                "N_plus_1_power_and_cooling",
                "backup_generators_for_classic_POD_architecture",
                "racks_servers_network_and_storage_in_classic_PODs",
                "24x7_onsite_security",
                "restricted_server_room_access",
            ],
            "normal_MZR_definition": "At least three data centers with independent power, cooling and network; minimum one mile separation, under 2ms latency and more than 1000Gbps between zones.",
            "SC_MZR_definition": "Three zones in one building or campus with potentially overlapping dependencies and concurrent maintainability.",
            "per_code_grid_feeds_substations_transformers_switchgear_PDU_UPS_battery_generator_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life": "undisclosed",
            "per_code_MW_area_measured_PUE_WUE_energy_water_and_emissions": "undisclosed",
        },
        "IBM_accelerator_product_and_physical_inventory_boundary": {
            "published_profile_models": {
                "V100": "one_or_two_16GB_GPUs_per_profile",
                "L4": "one_two_or_four_24GB_GPUs_per_profile",
                "L40S": "one_or_two_48GB_GPUs_per_profile",
                "A100": "one_or_two_80GB_GPUs_per_profile",
                "H100": "eight_80GB_GPUs_per_profile",
                "H200": "eight_141GB_GPUs_per_profile",
                "Gaudi3": "eight_128GB_accelerators_per_profile",
                "MI300X": "eight_accelerators_per_profile",
                "B300": "eight_288GB_GPUs_per_profile",
            },
            "exact_physical_code_product_availability": {model: sorted(codes) for model, codes in EXACT_ACCELERATOR_CODES.items()},
            "H100_cluster_network": "WDC06, WDC07 and FRA04; up to 3.2Tbps through eight 400Gbps NVIDIA ConnectX-7 links.",
            "H200_source_conflict": "The product-specific physical-code page includes CHE02 while the generic logical-zone page reviewed did not; CHE02 is retained with the product-page citation rather than silently harmonized.",
            "H200_network_table_conflict": "The profile row and regional availability table use inconsistent dedicated-cluster-network markers; no site-level installed network is inferred from the conflict.",
            "product_profile_boundary": "GPUs per orderable instance are not a fleet count. Exact installed, accepted, available, utilized, customer-owned and IBM-owned units by site are undisclosed.",
            "Vela": {
                "online_since": "2022-05",
                "site_scope": "one_undisclosed_IBM_Cloud_data_center",
                "node_configuration": "eight_NVIDIA_A100_80GB_GPUs_two_Cascade_Lake_CPUs_1_5TB_DRAM_four_3_2TB_NVMe_and_multiple_100G_links",
                "research_evaluation_scale": "approximately_1500_GPUs_not_a_current_installed_fleet_count",
                "throughput_result": "approximately_80_percent_of_ideal_on_a_50B_parameter_model_and_approximately_70_percent_per_GPU_FLOPS",
                "December_2023_update": "around_twice_as_many_GPUs_after_upgrade_without_exact_baseline_or_current_count",
            },
            "Blue_Vela": "H100-based Dell/NVIDIA/IBM Storage Scale platform conceived in spring 2024; reviewed source does not disclose site or fleet count.",
        },
        "IBM_FY2025_financials_USD_million": {
            "revenue": 67535,
            "gross_profit": 39297,
            "derived_pre_interest_pre_other_operating_like_result": 11822,
            "derived_operating_like_margin_percent": 17.505,
            "reported_GAAP_operating_income_line": "not_presented",
            "pretax_income_from_continuing_operations": 10328,
            "net_income": 10593,
            "operating_cash_flow": 13193,
            "net_capex_approx": 1600,
            "company_defined_free_cash_flow_non_GAAP": 14700,
            "cash_restricted_cash_and_marketable_securities": 14471,
            "short_and_long_term_debt": 61260,
            "property_plant_and_equipment_gross": 17874,
            "property_plant_and_equipment_net": 5899,
            "boundary": "Companywide IBM results; the derived result equals gross profit less SG&A and R&D plus IP/custom-development income and is not reported GAAP operating income. IBM Cloud data-center-only revenue, profit, cash flow and capex are undisclosed.",
        },
        "IBM_Infrastructure_segment_FY2025_USD_million": {
            "revenue": 15718,
            "reported_growth_percent": 12.1,
            "constant_currency_growth_percent": 10.4,
            "hybrid_infrastructure_revenue": 10618,
            "infrastructure_support_revenue": 5100,
            "gross_profit": 9216,
            "gross_margin_percent": 58.6,
            "segment_profit": 3458,
            "segment_profit_margin_percent": 22.0,
            "boundary": "The segment includes IBM Z, Power, Storage, support and IaaS; it is not a data-center-only segment, and z17 product-cycle strength should not be read as IBM Cloud facility economics.",
        },
        "Kyndryl_separation_and_current_facility_boundary": {
            "IBM_separation_completed": "2021-11-03",
            "selected_France_certificate_site_groups": 7,
            "selected_France_named_components_if_labels_are_split": 11,
            "selected_Germany_explicit_DC_rows": 4,
            "combined_registry_rows": 11,
            "current_strategy": "Kyndryl says it hosts workloads in its own facilities and colocation partners, with bespoke co-creation at select Kyndryl-owned data centers.",
            "boundary": "Certificates are a partial compliance scope, not a complete global roster or proof of property title. IBM's historical label, the separation, and an OSM coordinate do not alone prove which property transferred or who operates it today.",
        },
        "Kyndryl_FY2026_financials_USD_million": {
            "period_ended": "2026-03-31",
            "revenue": 15092,
            "derived_pre_interest_pre_other_operating_like_result": 534,
            "derived_operating_like_margin_percent": 3.538,
            "reported_GAAP_operating_income_line": "not_presented",
            "pretax_income": 414,
            "net_income": 198,
            "operating_cash_flow": 948,
            "net_capex": 543,
            "company_defined_free_cash_flow_non_GAAP": 406,
            "cash_approx": 2600,
            "current_plus_long_term_debt_including_revolver": 4089,
            "owned_or_leased_real_estate_million_sqft": 9.0,
            "real_estate_boundary": "Substantially all of the 9.0 million square feet is data-center and office space, but the filing does not split the categories or disclose an exact data-center count, MW or GPU inventory.",
            "internal_control_risk": "The FY2026 auditor report identifies material weaknesses in internal control over financial reporting as of 2026-03-31.",
            "boundary": "Companywide Kyndryl results. The derived result equals revenue less cost of services, SG&A, workforce rebalancing and transaction-related costs; it is not reported GAAP operating income or data-center-only profit.",
        },
        "Kyndryl_FY2027_company_outlook_USD_million": {
            "adjusted_pretax_income_range": [600, 700],
            "free_cash_flow_range": [400, 500],
            "constant_currency_revenue_growth_range_percent": [-2, 0],
            "FY2026_hyperscaler_related_revenue": 1900,
            "FY2026_hyperscaler_related_revenue_growth_percent": 59,
            "FY2026_consult_revenue": 3500,
            "FY2026_consult_revenue_growth_percent": 18,
            "FY2026_signings": 13500,
            "boundary": "Outlook and growth measures are companywide and largely non-GAAP or operational; none is data-center-only revenue, margin or booked capacity.",
        },
        "OSM_crosswalk": {
            "rows": osm_rows,
            "all_related_objects": len(osm_rows),
            "raw_operator_counts": {str(key): value for key, value in sorted(Counter(row["raw_operator"] for row in osm_rows).items(), key=lambda item: str(item[0]))},
            "current_Kyndryl_certificate_group_candidates": sum(row["registry_ref"] is not None for row in osm_rows),
            "unresolved_or_separate_scope_objects": sum(row["registry_ref"] is None for row in osm_rows),
            "source_file": str(osm_path),
            "source_file_sha256": hashlib.sha256(osm_path.read_bytes()).hexdigest(),
            "boundary": "The OSM objects are partial geometry and identity candidates. They do not add facilities, area, power or GPU capacity to either provider scope.",
        },
        "outlook": {
            "IBM_positive_signals": [
                "broad_47_code_cloud_service_footprint",
                "B300_H200_H100_Gaudi3_and_other_accelerator_product_breadth",
                "strong_FY2025_Infrastructure_growth_and_cash_generation",
                "Vela_and_Blue_Vela_demonstrate_large_scale_AI_system_engineering",
            ],
            "IBM_risk_signals": [
                "exact_site_ownership_MW_GPU_counts_and_cloud_data_center_economics_undisclosed",
                "some_classic_codes_set_to_close_without_public_code_list",
                "Infrastructure_growth_heavily_influenced_by_z17_cycle_not_pure_cloud_facility_demand",
                "high_consolidated_debt_and_cross_segment_capital_allocation",
            ],
            "Kyndryl_positive_signals": [
                "FY2026_hyperscaler_related_revenue_growth_of_59_percent",
                "positive_operating_cash_flow_and_FY2027_profit_improvement_outlook",
                "own_plus_colocation_hybrid_infrastructure_position",
            ],
            "Kyndryl_risk_signals": [
                "FY2027_constant_currency_revenue_outlook_flat_to_down_2_percent",
                "no_complete_current_facility_count_MW_GPU_or_data_center_only_economics",
                "debt_refinancing_and_internal_control_material_weaknesses",
                "certificate_and_legacy_IBM_labels_do_not_prove_title_or_current_operator_by_building",
            ],
            "analytical_view": "IBM is the more investable broad technology and cash-generation exposure, but its data-center economics cannot be isolated and its accelerator tables prove product availability rather than fleet size. Kyndryl benefits from hybrid and hyperscaler integration growth, yet remains a lower-margin services transformation with incomplete facility disclosure, revenue pressure and control risk. Neither should be valued as a pure-play owned AI data-center fleet from these disclosures.",
        },
        "remaining_material_gaps": [
            "IBM_Cloud_exact_current_code_closure_roster_and_code_to_street_address_building_campus_title_lease_operator_bridge",
            "IBM_Cloud_per_site_operating_energized_leased_utilized_billed_and_actual_IT_load",
            "IBM_Cloud_per_site_grid_substation_transformer_switchgear_PDU_UPS_battery_generator_fuel_chiller_CRAH_CRAC_CDU_OEM_model_count_rating_loading_acceptance_and_remaining_life",
            "IBM_Cloud_per_site_measured_PUE_WUE_energy_water_emissions_and_live_liquid_cooled_MW",
            "IBM_and_customer_GPU_model_count_owner_site_delivery_acceptance_rack_fabric_power_utilization_revenue_and_margin",
            "IBM_Cloud_data_center_only_revenue_operating_profit_cash_flow_capex_ROIC_customer_concentration_and_contract_terms",
            "Kyndryl_complete_current_global_owned_leased_and_colocation_facility_building_address_lifecycle_title_and_operator_roster",
            "Kyndryl_legacy_IBM_property_by_property_separation_and_current_operator_bridge",
            "Kyndryl_per_site_MW_equipment_PUE_WUE_GPU_inventory_utilization_and_economics",
            "current_share_prices_enterprise_values_and_valuation_require_same_date_market_data",
        ],
        "sources": [
            IBM_LOCATIONS, IBM_CLOSURES, IBM_FACILITIES, IBM_VPC_PROFILES, IBM_ACCEL_GEN3, IBM_ACCEL_GEN4,
            IBM_VELA_PAPER, IBM_VELA_LAUNCH, IBM_VELA_UPDATE, IBM_BLUE_VELA, IBM_2025_10K, IBM_2025_LETTER,
            KYNDRYL_CERTIFICATIONS, KYNDRYL_FR_ISO22301, KYNDRYL_FR_HDS, KYNDRYL_DE_ISO27001,
            KYNDRYL_STRATEGY, KYNDRYL_2026_10K, KYNDRYL_FY2026_RESULTS, IBM_KYNDRYL_SEPARATION,
        ],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    ibm_records = build_ibm_records(args.accessed_on)
    kyndryl_records = build_kyndryl_records(args.accessed_on)
    records = [{"source_order": position, **row} for position, row in enumerate(ibm_records + kyndryl_records, 1)]
    osm_rows = build_osm_crosswalk(load_osm(args.osm))
    summary = build_summary(records, osm_rows, args.osm, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "ibm_cloud_kyndryl_boundary_registry.jsonl"
    summary_path = args.output_dir / "ibm_cloud_kyndryl_boundary_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "IBM_Cloud_codes": len(ibm_records), "Kyndryl_certificate_groups": len(kyndryl_records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
