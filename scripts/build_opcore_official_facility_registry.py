#!/usr/bin/env python3
"""Build OPCORE's France, Poland and development-location evidence registry.

The July 2026 OPCORE site exposes seven current French facility pages.  Play
markets five Polish addresses whose passive assets sit in Op Core Poland, and
public planning material separately describes DC6 and the Montereau program.
This builder keeps provider labels, addresses, physical buildings, legal
establishments, OSM objects, operating sites and development projects separate.
It also preserves contradictory source values instead of silently selecting a
preferred PUE, area, room count, fuel, battery or refrigerant denominator.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


OPCORE_HOME = "https://www.opcore.com/"
OPCORE_DIRECTORY = "https://www.opcore.com/datacenters"
OPCORE_AI_DESIGN = "https://www.opcore.com/application/data-centers-designed-around-your-needs"
OPCORE_AI_READINESS = "https://www.opcore.com/application/not-all-data-centers-are-created-equal"
OPCORE_EXPERTISE = "https://www.opcore.com/application/whatever-your-expertise-were-built-you"
OPCORE_SOVEREIGNTY = "https://www.opcore.com/100-sovereign-data-centers"
PLAY_DIRECTORY = "https://www.play.pl/duze-firmy/chmura-i-centra-danych/centra-danych"
DC5_MRAE = "https://www.mrae.developpement-durable.gouv.fr/IMG/pdf/2026-01-21_st-ouen-l_aumone_extension_datacenterdc5_delegue.pdf"
DC6_REGISTER = "https://www.registre-numerique.fr/datacenter-dc6-soa"
DC6_REPORT = "https://www.registre-numerique.fr/datacenter-dc6-soa/telechargement?rapport=2387"
DC6_RESPONSE = "https://www.registre-numerique.fr/datacenter-dc6-soa/telechargement?rapport=2389"
EDF_MONTEREAU = "https://www.edf.fr/en/the-edf-group/dedicated-sections/journalists/all-press-releases/edf-and-opcore-to-develop-a-high-power-data-center-on-site-of-former-thermal-power-plant-in-montereau-vallee-de-la-seine-wider-paris-metropolitan-region"
INFRAVIA_PARTNERSHIP = "https://infraviacapital.com/infravia-enters-into-exclusive-negotiations-with-iliad-to-form-a-partnership-with-opcore/"
INFRAVIA_CLOSE = "https://infraviacapital.com/infravia-completes-the-acquisition-of-a-50-stake-in-opcore/"
ILIAD_2025_URD = "https://www.iliad.fr/media/ILIAD_URD_30042026_ENG_834039a832.pdf"
P4_2025_REPORT = "https://ir.play.pl/upload/reports/Sprawozdanie%20z%20dzia%C5%82alno%C5%9Bci%20P4%20za%202025%20rok.pdf"
RUBYPAYEUR = "https://rubypayeur.com/societe/op-core-891405227"
LEGAL_DIRECTORY = "https://annuaire-entreprises.data.gouv.fr/entreprise/op-core-891405227"


def page(code: str) -> str:
    return f"https://www.opcore.com/datacenters/{code.lower()}"


FRANCE = [
    {
        "id": "opcore_par1_bezons",
        "code": "PAR1",
        "locality": "Bezons",
        "address": "80 Rue du Quai Voltaire, 95870 Bezons, France",
        "technical_profile": {
            "published_surface_sqm": 5980,
            "published_PUE_TTM": 1.48,
            "utility_feeds": "two_5_2MW_feeds",
            "power_topology": "N_plus_1_power_UPS_and_generation_with_dual_feed",
            "generation": "standby_low_voltage_diesel",
            "published_fuel_autonomy_hours": 94,
            "cooling": "chilled_water_N_plus_1_loop_with_cold_aisle",
            "published_cooling_value_verbatim": "4,778 MWf",
            "fire_systems": ["FOGTEC", "Siemens_DFHS"],
        },
        "publication_conflicts": ["cooling_value_4_778_MWf_is_dimensionally_ambiguous_and_is_not_normalized"],
        "OSM_refs": ["osm_way_76727775"],
    },
    {
        "id": "opcore_mrs1_marseille",
        "code": "MRS1",
        "locality": "Marseille",
        "address": "70 Chemin du Passet, 13016 Marseille, France",
        "technical_profile": {
            "published_surface_sqm": 8000,
            "published_PUE": 1.45,
            "utility_feeds": "two_12MW_feeds",
            "electrical_lineups": "three_TriCore",
            "UPS": "2N_dual",
            "generation": "2N_low_voltage_diesel",
            "published_fuel_autonomy_hours": 72,
            "published_cooling_mwf": 3.6,
            "cooling": "chilled_water_N_plus_1_loop_with_cold_corridor",
        },
        "publication_conflicts": [],
        "OSM_refs": [],
    },
    {
        "id": "opcore_lyo1_lyon",
        "code": "LYO1",
        "locality": "Lyon",
        "address": "60 Avenue Rockefeller, 69008 Lyon, France",
        "technical_profile": {
            "published_surface_sqm": 3708,
            "published_PUE": 1.37,
            "utility_feed_capacity": "undisclosed",
            "electrical_lineups": 4,
            "UPS": "2N",
            "generation": "2N",
            "published_fuel_autonomy_hours": 72,
            "published_cooling_mwf": 2.4,
            "cooling": "chilled_water_N_plus_1_loop_with_cold_aisle",
        },
        "publication_conflicts": [],
        "OSM_refs": [],
    },
    {
        "id": "opcore_par2_vitry_sur_seine",
        "code": "PAR2",
        "locality": "Vitry-sur-Seine",
        "address": "29 Rue Edith Cavell, 94400 Vitry-sur-Seine, France",
        "technical_profile": {
            "published_surface_sqm": 5500,
            "facility_page_PUE": 1.47,
            "dashboard_PUE_category": 1.5,
            "dashboard_recent_TTM_approximate": "1_43",
            "dashboard_commission_year": 1991,
            "dashboard_total_capacity_mw_undefined_denominator": 3.8,
            "utility_feeds": "two_12MW_feeds",
            "electrical_lineups": "four_N_plus_1_or_2N",
            "UPS_published_verbatim": "N+1 & N",
            "generation": "N_plus_1_catcher",
            "published_fuel_autonomy_hours": 50,
            "published_cooling_mwf": 5,
        },
        "publication_conflicts": ["facility_page_PUE_1_47_versus_dashboard_category_1_5_and_dynamic_TTM_around_1_43"],
        "extra_source_urls": ["https://pue.dc2.opcore.com/fr/"],
        "OSM_refs": ["osm_way_139560714"],
    },
    {
        "id": "opcore_par3_chevilly_larue",
        "code": "PAR3",
        "locality": "Chevilly-Larue",
        "address": "61 Rue Julian Grimau, 94550 Chevilly-Larue, France",
        "technical_profile": {
            "published_surface_sqm": 10000,
            "facility_page_PUE": 1.36,
            "dashboard_PUE_category": 1.4,
            "dashboard_recent_TTM_approximate": "1_43_to_1_45",
            "dashboard_commission_year": 2012,
            "dashboard_total_capacity_mw_undefined_denominator": 6.9,
            "grid_context": "within_0_5_mile_of_225kV_Chevilly_Larue_substation",
            "utility_feeds": "two_12MW_feeds",
            "electrical_lineups": "four_Hexacore",
            "UPS": "N_plus_1",
            "generation": "continuous_low_voltage_N_plus_1_catcher",
            "published_fuel_autonomy_hours": 72,
            "published_cooling_mwf": "two_5_957",
            "cooling": "2N_central_and_N_plus_2_CRAH_closed_loop_dry_coolers_with_trim_chillers",
        },
        "publication_conflicts": [
            "facility_page_PUE_1_36_versus_dashboard_category_1_4_and_dynamic_TTM_around_1_43_to_1_45",
            "current_page_address_61_Rue_Julian_Grimau_versus_BSI_62_and_2025_legal_establishment_59",
        ],
        "extra_source_urls": ["https://pue.dc3.opcore.com/fr/"],
        "OSM_refs": ["osm_way_139560858"],
    },
    {
        "id": "opcore_par4_paris",
        "code": "PAR4",
        "locality": "Paris",
        "address": "58 Boulevard Lefebvre, 75015 Paris, France",
        "technical_profile": {
            "depth_below_ground_m": 26,
            "structure": "former_nuclear_fallout_shelter",
            "IT_rooms": 3,
            "meet_me_rooms": 3,
            "design": "Tier_III",
            "surface_sqm": "undisclosed",
            "PUE": "undisclosed",
            "utility_capacity": "undisclosed",
            "generation_and_fuel": "undisclosed",
            "cooling_capacity": "undisclosed",
            "cooling": "redundant_AC_and_cooling_with_nearby_heat_reuse",
            "fire_systems": ["VESDA", "Novec_1230"],
        },
        "publication_conflicts": [],
        "OSM_refs": [],
    },
    {
        "id": "opcore_par5_saint_ouen_l_aumone",
        "code": "PAR5",
        "locality": "Saint-Ouen-l'Aumone",
        "address": "25 Avenue de l'Eguillette, 95310 Saint-Ouen-l'Aumone, France",
        "technical_profile": {
            "facility_page_surface_sqm": 17000,
            "dashboard_surface_sqm": 20000,
            "facility_page_PUE_TTM": 1.18,
            "facility_page_PUE_at_70_percent_load": 1.15,
            "dashboard_PUE": 1.16,
            "dashboard_WUE": 0.25,
            "dashboard_commission_year": 2018,
            "dashboard_total_capacity_mw_undefined_denominator": 20.5,
            "utility_feeds": "two_24MW_feeds",
            "UPS_published_verbatim": "26N+1 Catcher or Hexacore or 2N",
            "power_redundancy_published_verbatim": "N & N+1",
            "generation": "prime_low_voltage_diesel_N_plus_1_catcher",
            "published_fuel_autonomy_hours": 50,
            "published_cooling_mwf": 23.4,
            "cooling": "direct_free_cooling_and_adiabatic_N_plus_2_fan_wall_hot_aisle",
            "private_vaults": 12,
        },
        "publication_conflicts": [
            "facility_page_17000sqm_versus_dashboard_20000sqm",
            "facility_page_PUE_1_18_versus_dashboard_1_16",
            "current_page_25_Avenue_de_l_Eguillette_versus_new_2026_legal_establishment_7_Rue_de_la_Patelle",
        ],
        "extra_source_urls": ["https://pue.dc5.opcore.com/en/", DC5_MRAE],
        "OSM_refs": ["osm_way_102449117"],
    },
]


POLAND = [
    {
        "id": "opcore_pl_katowice_gospodarcza",
        "code": "PL_KAT_GOSPODARCZA",
        "locality": "Katowice",
        "address": "Gospodarcza 12, Katowice, Poland",
        "technical_profile": {
            "physical_buildings": 2,
            "published_surface_sqm": 2200,
            "maximum_racks": 560,
            "power": "independent_electricity_distributors_dual_lines_gas_connection_redundant_UPS_and_generators",
            "fire": "gas_or_Inergen_and_VESDA",
            "network": "three_fiber_paths",
            "design": "Tier_or_Rated_3",
        },
    },
    {
        "id": "opcore_pl_katowice_ligocka",
        "code": "PL_KAT_LIGOCKA",
        "locality": "Katowice",
        "address": "Ligocka 103, Katowice, Poland",
        "technical_profile": {
            "published_surface_sqm": 475,
            "maximum_racks": 80,
            "power": "two_feeds_three_generators_redundant_UPS",
            "cooling": "chilled_water_with_free_cooling",
            "network": "three_fiber_paths",
        },
    },
    {
        "id": "opcore_pl_warsaw_annopol",
        "code": "PL_WAW_ANNOPOL",
        "locality": "Warsaw",
        "address": "Annopol 3, Warsaw, Poland",
        "technical_profile": {
            "published_surface_sqm_more_than": 1250,
            "published_office_sqm": 300,
            "maximum_racks": 385,
            "power": "independent_lines_plus_gas_redundant_UPS_and_generators",
            "cooling": "two_independent_precision_systems_one_with_free_cooling_and_air_air_recuperators",
            "published_PUE_less_than": 1.4,
            "design": "Tier_or_Rated_3",
        },
    },
    {
        "id": "opcore_pl_bytom_szymaly",
        "code": "PL_BYT_SZYMALY",
        "locality": "Bytom",
        "address": "Szymaly 153, Bytom, Poland",
        "technical_profile": {"published_surface_sqm": 750, "maximum_racks": 144, "monitoring": ["SCADA", "CCTV"], "power_detail": "undisclosed"},
    },
    {
        "id": "opcore_pl_gdansk_nowy_swiat",
        "code": "PL_GDN_NOWY_SWIAT",
        "locality": "Gdansk",
        "address": "Nowy Swiat 40, Gdansk, Poland",
        "technical_profile": {
            "published_surface_sqm": 502,
            "maximum_racks": 180,
            "structure": "room_in_room_fire_resistance",
            "power": "two_medium_voltage_lines_from_two_GPs_redundant_UPS_and_generators",
            "cooling": "redundant",
        },
    },
]


DEVELOPMENT = [
    {
        "id": "opcore_dc6_saint_ouen_l_aumone_development",
        "code": "DC6",
        "country_code": "FR",
        "locality": "Saint-Ouen-l'Aumone",
        "address": "6 Rue de la Patelle, 95310 Saint-Ouen-l'Aumone, France",
        "lifecycle": "permitted_or_public_inquiry_development_targeting_progressive_fitout_to_2031",
        "technical_profile": {
            "project": "rehabilitation_of_existing_warehouse",
            "parcel_sqm_source_conflict": [48695, 48979],
            "floor_area_sqm": 20465,
            "building_footprint_sqm_source_conflict": [17033, 17150, 17300, 21233],
            "IT_halls": 3,
            "IT_power_mw": 28.8,
            "grid_connection_mw": 40,
            "grid_delivery": "two_20kV_to_400V_delivery_stations",
            "maximum_annual_electricity_GWh": 314,
            "target_annual_electricity_GWh_at_70_percent": 210,
            "target_PUE_maximum": 1.2,
            "target_WUE_l_per_kWh": 0.003,
            "modules_at_full_build": {"ELEC": 36, "COOLING": 36, "GE": 36},
            "generators": "thirty_six_Himoinsa_Mitsubishi_S16R_PTA_3580kWth_1389kWe_PRP",
            "generator_total_thermal_mw": 128.9,
            "fuel": "HVO",
            "fuel_tanks": "thirty_six_9000L_7_2t_each",
            "total_fuel_m3": 324,
            "total_fuel_tonnes": 259.2,
            "batteries": "thirty_six_ELEC_modules_each_five_cabinets_seventeen_blocks_eight_batteries",
            "battery_units_at_full_build": 24480,
            "battery_blocks_at_full_build": 3060,
            "battery_charge_kw_source_values": [2313, 2763],
            "cooling": "thirty_six_chillers_dry_coolers_pumps_exchangers_buffers_and_132_FANWALL_units",
            "refrigerant": "HFO_R_1234ze",
            "refrigerant_total_kg_source_conflict": [4752, 9504],
            "emergency_water_storage_m3": 92,
            "photovoltaic_canopy_sqm": 556,
            "full_grid_and_thermal_build_target": 2031,
        },
        "publication_conflicts": [
            "battery_count_dossier_typo_560_per_module_versus_petitioner_confirmed_680",
            "battery_charge_total_2313kW_versus_2763kW",
            "refrigerant_132kg_versus_264kg_per_cooling_module",
            "generator_test_schedule_summary_versus_hearing_response",
            "parcel_and_building_footprint_values_vary_by_document_section",
        ],
        "source_urls": [DC6_REGISTER, DC6_REPORT, DC6_RESPONSE],
        "OSM_refs": ["osm_way_102446449", "osm_way_102465235", "osm_way_102453250", "osm_way_102453433", "osm_way_102467679"],
    },
    {
        "id": "opcore_montereau_vallee_de_la_seine_development",
        "code": "MONTEREAU_PROGRAM",
        "country_code": "FR",
        "locality": "Vernou-la-Celle-sur-Seine and La Grande-Paroisse",
        "address": "Former Montereau-Vallee-de-la-Seine thermal power plant, Seine-et-Marne, France",
        "lifecycle": "development_program_exclusive_negotiations_and_grid_capacity_secured",
        "technical_profile": {
            "former_site": "coal_thermal_power_plant_stopped_2004",
            "subscription_capacity_mw_more_than": 400,
            "OPCORE_current_Paris_area_secured_or_under_construction_mw": 730,
            "OPCORE_current_Paris_area_investment_EUR_billion": 4,
            "grid_context": "400kV_Montereau",
            "initial_commissioning_expected": 2027,
        },
        "publication_conflicts": ["do_not_allocate_entire_730MW_Paris_area_headline_to_Montereau_without_a_provider_bridge"],
        "source_urls": [EDF_MONTEREAU, OPCORE_HOME, OPCORE_EXPERTISE],
        "OSM_refs": [],
    },
]


OSM_CROSSWALK = {
    "osm_way_76727775": (["opcore_par1_bezons"], "exact_provider_code_and_locality_candidate"),
    "osm_way_139560714": (["opcore_par2_vitry_sur_seine"], "exact_provider_code_and_locality_candidate"),
    "osm_way_139560858": (["opcore_par3_chevilly_larue"], "exact_provider_code_and_locality_candidate"),
    "osm_way_102449117": (["opcore_par5_saint_ouen_l_aumone"], "exact_provider_code_and_locality_candidate"),
    "osm_way_102446449": (["opcore_dc6_saint_ouen_l_aumone_development"], "same_commune_and_DC6_label_but_regulatory_single_warehouse_scope_unresolved"),
    "osm_way_102465235": (["opcore_dc6_saint_ouen_l_aumone_development"], "same_commune_and_DC6_label_but_regulatory_single_warehouse_scope_unresolved"),
    "osm_way_102453250": (["opcore_dc6_saint_ouen_l_aumone_development"], "same_commune_and_DC6_label_but_regulatory_single_warehouse_scope_unresolved"),
    "osm_way_102453433": (["opcore_dc6_saint_ouen_l_aumone_development"], "same_commune_and_DC6_label_but_regulatory_single_warehouse_scope_unresolved"),
    "osm_way_102467679": (["opcore_dc6_saint_ouen_l_aumone_development"], "same_commune_and_DC6_label_but_regulatory_single_warehouse_scope_unresolved"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines() if line for row in [json.loads(line)]}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(FRANCE, start=1):
        extra = source.get("extra_source_urls", [])
        records.append({
            "id": source["id"],
            "object_type": "DataCenterFacilityEvidence",
            "source_order": order,
            "operator": "OPCORE",
            "asset_scope": "current_OPCORE_France_directory",
            "provider_label": source["code"],
            "country_code": "FR",
            "locality": source["locality"],
            "address": source["address"],
            "lifecycle": "operating_current_provider_page",
            "technical_profile": source["technical_profile"],
            "publication_conflicts": source["publication_conflicts"],
            "physical_GPU_or_accelerator_inventory": "undisclosed",
            "source_urls": [page(source["code"]), *extra],
            "OSM_refs": source["OSM_refs"],
            "accessed_on": accessed_on,
        })
    for order, source in enumerate(POLAND, start=len(records) + 1):
        records.append({
            "id": source["id"],
            "object_type": "DataCenterFacilityEvidence",
            "source_order": order,
            "operator": "Play_B2B_service_layer_over_Op_Core_Poland_passive_assets",
            "asset_scope": "current_Play_marketed_Poland_address",
            "provider_label": source["code"],
            "country_code": "PL",
            "locality": source["locality"],
            "address": source["address"],
            "lifecycle": "current_marketed_service_location",
            "technical_profile": source["technical_profile"],
            "publication_conflicts": [],
            "physical_GPU_or_accelerator_inventory": "undisclosed",
            "source_urls": [PLAY_DIRECTORY, P4_2025_REPORT],
            "OSM_refs": [],
            "accessed_on": accessed_on,
        })
    for source in DEVELOPMENT:
        records.append({
            "object_type": "DataCenterFacilityEvidence",
            "source_order": len(records) + 1,
            "operator": "OPCORE",
            "asset_scope": "development_project",
            "provider_label": source["code"],
            "physical_GPU_or_accelerator_inventory": "undisclosed",
            "accessed_on": accessed_on,
            **source,
        })
    assert len(records) == 14
    assert len({row["id"] for row in records}) == 14
    assert Counter(row["asset_scope"] for row in records) == {
        "current_OPCORE_France_directory": 7,
        "current_Play_marketed_Poland_address": 5,
        "development_project": 2,
    }
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_ref, (facility_refs, status) in OSM_CROSSWALK.items():
        source = osm[osm_ref]
        assert source.get("operator") == "OPCORE"
        rows.append({
            "osm_ref": osm_ref,
            "name": source.get("name"),
            "raw_operator": source.get("operator"),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_refs": facility_refs,
            "crosswalk_status": status,
            "source_url": source["source_url"],
            "boundary": "OSM geometry is not certified floor area, a provider building count, operating status, legal ownership, IT load or GPU inventory.",
        })
    assert len(rows) == 9
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    france = [row for row in records if row["asset_scope"] == "current_OPCORE_France_directory"]
    poland = [row for row in records if row["asset_scope"] == "current_Play_marketed_Poland_address"]
    sources = sorted({url for row in records for url in row["source_urls"]} | {
        OPCORE_HOME, OPCORE_DIRECTORY, OPCORE_AI_DESIGN, OPCORE_AI_READINESS,
        OPCORE_EXPERTISE, OPCORE_SOVEREIGNTY, INFRAVIA_PARTNERSHIP,
        INFRAVIA_CLOSE, ILIAD_2025_URD, RUBYPAYEUR, LEGAL_DIRECTORY,
    })
    return {
        "id": "opcore_official_facility_summary_2026_07_19",
        "object_type": "OPCOREPortfolioReconciliation",
        "accessed_on": accessed_on,
        "current_roster_reconciliation": {
            "OPCORE_France_directory_labels": len(france),
            "OPCORE_France_codes": [row["provider_label"] for row in france],
            "Play_Poland_marketed_addresses": len(poland),
            "Play_Poland_physical_buildings_minimum": 6,
            "France_legal_establishments_open": 10,
            "France_legal_establishments_total_including_closed": 11,
            "development_records": 2,
            "boundary": "Seven French provider pages, five Polish addresses, six Polish buildings, French legal establishments, development projects and OSM objects are different scopes and are not added into one facility count.",
        },
        "France_current_directory_scale": {
            "six_pages_with_numeric_surface_sqm_checksum": 50188,
            "PAR4_surface_sqm": "undisclosed",
            "published_feed_magnitude_mw_checksum_excluding_LYO1_and_PAR4": 130.4,
            "numeric_cooling_mwf_checksum_excluding_PAR1_ambiguous_and_PAR4_unknown": 46.314,
            "boundary": "Surface is provider-published facility area. Feed MW, dashboard total capacity, cooling MWf and IT MW use different denominators; none is a current utilized-load checksum.",
        },
        "Poland_current_marketing_scale": {
            "marketed_address_rows": 5,
            "physical_buildings_minimum": 6,
            "published_area_sqm_minimum_checksum": 5177,
            "published_maximum_rack_checksum": 1349,
            "asset_owner": "Op_Core_Poland_formerly_3S_Box",
            "service_operator": "Play_B2B_under_long_term_operating_arrangements",
            "boundary": "Warsaw area is greater than 1,250 square metres, so 5,177 is a lower-bound arithmetic check. Rack maxima are not installed, occupied, powered or billed racks.",
        },
        "DC5_regulatory_extension": {
            "operating_since": 2017,
            "parcel_hectares": 2.33,
            "building_footprint_sqm_approximate": 7500,
            "floor_area_sqm": 20486,
            "IT_room_total_after_project_source_conflict": [12, 14],
            "current_UPS_ASI": 32,
            "added_UPS_ASI": 16,
            "generator_total_after_extension": 27,
            "generator_thermal_mw_before_after": [49.5, 71.92],
            "high_voltage_transformer_total_after_extension": 27,
            "day_tank_total_m3": 27,
            "underground_fuel_storage_tonnes": 140.8,
            "annual_water_m3_before_after": [3659, 7870],
            "projected_annual_electricity_GWh_source_conflict": [24.775, 33.8],
            "target_PUE": 1.15,
            "boundary": "The environmental authority says actual load cannot be identified and questions several projections. Regulatory equipment totals and provider page values remain separate from current live IT load.",
        },
        "DC6_development": next(row["technical_profile"] for row in records if row["id"] == "opcore_dc6_saint_ouen_l_aumone_development") | {
            "AI_boundary": "OPCORE told the inquiry that DC6 is not specifically dimensioned for AI but is technically compatible; no installed accelerator inventory is disclosed.",
            "rack_boundary": "A theoretical 30,000-rack statement is power-constrained and lacks a density allocation; it is not a deployable or occupied rack count.",
        },
        "Paris_area_pipeline": {
            "current_OPCORE_headline_secured_or_under_construction_mw": 730,
            "current_OPCORE_headline_investment_EUR_billion": 4,
            "Montereau_subscription_capacity_mw_more_than": 400,
            "Montereau_initial_commissioning_expected": 2027,
            "DC6_grid_connection_mw": 40,
            "boundary": "No source allocates all 730 MW to Montereau or confirms whether the 40-MW DC6 connection is included. The residual is not reconstructed.",
        },
        "AI_and_accelerators": {
            "design_range": "external_1MW_power_and_cooling_modules_scale_1_to_250MW",
            "rack_density": "11_to_240kW_general_offer_and_200kW_plus_AI_racks",
            "readiness_examples": ["GB200", "GB300", "Vera_Rubin", "VR200", "TPU", "native_direct_liquid_cooling"],
            "physical_GPU_or_accelerator_count": "undisclosed",
            "accelerator_ledger_action": "no_row_because_readiness_and_NVIDIA_collaboration_do_not_disclose_a_physical_quantity_site_or_owner",
        },
        "energy_claim_conflict": {
            "homepage": "direct_EDF_agreement_low_carbon_nuclear_for_all_sites",
            "sovereignty_page": "no_PPA_or_long_commitment_client_specific_procurement_and_exclusively_renewable_since_2018",
            "facility_pages": "100_percent_low_carbon",
            "resolution": "retain_each_claim_by_page_and_access_date_without_treating_low_carbon_nuclear_and_renewable_as_synonyms",
        },
        "ownership_and_financials": {
            "legal_entity": "OP_CORE_SAS",
            "SIREN": "891405227",
            "capital_EUR": 32402978,
            "current_ownership": "50_percent_iliad_and_50_percent_InfraVia_Infrastructure_VI_funds",
            "transaction_enterprise_value_EUR_million": 860,
            "iliad_liquidity_from_transaction_EUR_million": 440,
            "bank_financing_investment_share_up_to_percent": 75,
            "FY2025_iliad_equity_accounted_affiliate_EUR_million": {"revenue": 69.883, "net_loss": -15.532, "gross_and_net_carrying_value": 52.942, "loans": 14.0},
            "FY2025_accounting_operating_profit": "undisclosed",
            "FY2024_secondary_filed_account_extraction_EUR": {"revenue": 60670974, "EBITDA": 20673829, "operating_profit_EBIT": 1550174, "net_loss": -5011289},
            "FY2023_secondary_filed_account_extraction_EUR": {"revenue": 28194220, "EBITDA": 11026722, "operating_profit_EBIT": 7132705, "net_profit": 4274672},
            "boundary": "FY2025 is the current equity-accounted affiliate perimeter. FY2024 exact income figures are a secondary rendering of filed accounts. Enterprise value, seller liquidity, carrying value and investment financing are not interchangeable.",
        },
        "public_map_crosswalk": {
            "related_OPCORE_OSM_objects": len(osm_rows),
            "current_France_facility_exact_candidates": 4,
            "DC6_labelled_unresolved_objects": 5,
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_rows), 3),
            "objects": osm_rows,
            "boundary": "The five DC6-labelled footprints are not counted as five additional current provider facilities or as a verified physical decomposition of the single-warehouse regulatory project.",
        },
        "unresolved_gaps": [
            "provider_bridge_between_seven_France_pages_ten_open_legal_establishments_and_historical_eight_France_sites",
            "exact_physical_building_property_and_lease_roster_in_France_and_Poland",
            "per_site_operating_energized_leased_utilized_customer_accepted_and_billed_IT_load",
            "PAR1_cooling_unit_resolution_and_PAR2_PAR3_PAR5_page_dashboard_conflict_resolution",
            "DC5_room_count_electricity_and_extension_scope_conflict_resolution",
            "DC6_final_permit_construction_energization_customer_acceptance_and_full_build_schedule",
            "730MW_Paris_area_project_allocation_grid_interconnection_and_financing_bridge",
            "physical_GPU_model_count_owner_site_delivery_power_draw_utilization_revenue_and_margin",
            "current_as_built_transformer_switchgear_busbar_PDU_UPS_battery_generator_fuel_chiller_CRAH_CDU_counts_ratings_OEMs_and_maintenance_state_by_operating_site",
            "OPCORE_FY2025_accounting_operating_profit_EBITDA_capex_debt_cash_flow_customer_concentration_site_economics_and_ROIC",
            "per_site_measured_PUE_WUE_energy_water_emissions_and_hourly_power_matching",
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
    summary = build_summary(records, osm_rows, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = args.output_dir / "opcore_official_facility_registry.jsonl"
    summary_path = args.output_dir / "opcore_official_facility_summary.json"
    registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
