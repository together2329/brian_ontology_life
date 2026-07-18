#!/usr/bin/env python3
"""Build KIO Data Centers' current facility, engineering and ownership registry.

KIO's July 2026 site publishes fifteen current Latin American location pages,
while older material says 40+ data centers or includes Spain.  Spain is now the
separate Kumo Networks business owned by El Corte Inglés.  This builder keeps
those scopes, site equipment nameplates, future projects, private-company
financial opacity and OSM geometries separate.  It never turns UPS/generator
ratings, renewable claims or AI-ready language into live IT load, GPU inventory
or recognized revenue.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


KIO_HOME = "https://kiodatacenters.com/en"
KIO_LOCATIONS = "https://kiodatacenters.com/en/locations"
KIO_ESG = "https://kiodatacenters.com/en/esg"
QRO2_OPENING = "https://kiodatacenters.com/en/newsroom/expansion/kio-data-centers-launches-qro2-expanding-mexicos-most-important-digital-hub-for-critical-industries"
GTM2_EXPANSION = "https://kiodatacenters.com/en/newsroom/expansion/kio-data-centers-will-invest-more-than-400-million-in-capex-in-the-region-and-quadruple-its-capacity-in-guatemala"
MEX8_CONSTRUCTION = "https://kiodatacenters.com/en/newsroom/expansion/kio-data-centers-boosts-cdmxs-digital-infrastructure-with-the-construction-of-mex8-its-new-data-center"
ISQ_ACTIVE = "https://isquaredcapital.com/txnm_status/active/page/5/"
ISQ_ACQUISITION = "https://www.businesswire.com/news/home/20211202005216/en/I-Squared-Capital-Acquires-KIO-Networks-a-Leading-Data-Center-and-Digital-Infrastructure-Service-Provider-in-Mexico-and-Central-America"
IFC_PROJECT = "https://disclosures.ifc.org/project-detail/SII/45608/project-kio"
KUMO_LOCATIONS = "https://kumonetworks.es/en/data-centers"
KUMO_MURCIA_SHEET = "https://www.kumonetworks.es/wp-content/uploads/2025/04/Datasheet-DC-Murcia-14-04-2025_compressed.pdf"
KUMO_VALENCIA_GENERATORS = "https://www.kumonetworks.es/la-estructura-del-cpd-tier-iv-de-paterna-ya-esta-terminada/"
KUMO_VALENCIA_COOLING = "https://www.kumonetworks.es/depositos-co2-centro-datos-refrigeracion/"
KUMO_VALENCIA_INVESTMENT = "https://kumonetworks.es/en-las-obras-de-nuestro-nuevo-centro-de-datos"
ECI_BUSINESS_LINES = "https://www.elcorteingles.es/informacioncorporativa/en/about-us/business-lines/"
ECI_FY2024_ACCOUNTS = "https://dam.elcorteingles.es/espacios/web-corporativa/doc-portal-2025-07-28-cuentas-anuales-consolidadas.pdf"
ECI_FY2025_RESULTS = "https://www.elcorteingles.es/informacioncorporativa/en/financial-information/group-figures/"


def location(slug: str) -> str:
    return f"https://kiodatacenters.com/en/locations/{slug}"


def spec_sheet(filename: str) -> str:
    return f"https://content.kiodatacenters.com/wp-content/uploads/2026/{filename}"


FACILITIES = [
    {
        "id": "kio_bog1_bogota",
        "code": "BOG1",
        "provider_label": "BOG | 1 Bogota",
        "country_code": "CO",
        "locality": "Bogota Free Trade Zone",
        "address": "Bogota Colombia Free Trade Zone",
        "official_page": location("bog-1-bogota"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_BOG1_ENG.pdf"),
        "technical_profile": {
            "current_page_data_hall_sqm": 1160,
            "structure": "four_story_dedicated_reinforced_anti_seismic_facility",
            "UPS": "three_500kVA_IT_branches_plus_three_600kVA_mechanical_branches",
            "electrical_redundancy": "N+1_distributed_parallel",
            "generators": "three_1650kW",
            "diesel_autonomy_hours_more_than": 40,
            "power_supply": "10MVA_34_5kV_medium_voltage_service_drop",
            "cooling": "indirect_free_cooling_N+1",
            "design_PUE": 1.4,
        },
        "publication_conflicts": [
            "current_page_1160sqm_initial_data_hall_versus_current_PDF_2352sqm_first_stage",
            "current_page_three_500kVA_IT_UPS_branches_versus_PDF_power_table_six_500kVA_IT_UPS",
            "current_PDF_5_8MW_IT_and_telecom_capacity_versus_older_2025_sheet_5_6MW",
        ],
        "OSM_refs": [],
    },
    {
        "id": "kio_sdo1_santo_domingo",
        "code": "SDO1",
        "provider_label": "SDO | 1 Santo Domingo",
        "country_code": "DO",
        "locality": "Santo Domingo",
        "address": "Free Trade Zone Las Americas, Santo Domingo, Dominican Republic",
        "official_page": location("sdo-1-dominican-republic"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_SDO1_ENG.pdf"),
        "technical_profile": {
            "data_hall_sqm": 223,
            "UPS": "two_275kVA",
            "electrical_redundancy": "2N",
            "generators": "two_450kW",
            "diesel_autonomy_days": 7,
            "power_supply": "13_2kV_medium_voltage_service_drop",
            "cooling": "2N_cold_aisle_containment",
            "average_PUE": 1.6,
        },
        "OSM_refs": [],
    },
    {
        "id": "kio_gtm1_guatemala",
        "code": "GTM1",
        "provider_label": "GTM | 1 Guatemala",
        "country_code": "GT",
        "locality": "Mixco, Guatemala City",
        "address": "8a Avenue 19-54, Condado el Naranjo, Zone 4 of Mixco, Guatemala",
        "official_page": location("guatemala-1"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_GTM1_ENG.pdf"),
        "technical_profile": {
            "data_hall_sqm": 174,
            "UPS": "two_250kVA",
            "electrical_redundancy": "2N",
            "generators": "two_450kW",
            "diesel_autonomy_days": 7,
            "power_supply": "13_2kV_medium_voltage_service_drop",
            "cooling": "twelve_units_four_redundant_indirect_free_cooling",
            "design_PUE": 1.6,
        },
        "OSM_refs": [],
    },
    {
        "id": "kio_pan1_panama",
        "code": "PAN1",
        "provider_label": "PAN | 1 Panama",
        "country_code": "PA",
        "locality": "Panama Pacifico",
        "address": "West Service Street, Building 3890, Panama Pacific International Business Park, Arraijan, Panama",
        "official_page": location("pan-1-panama"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_PAN1_ENG.pdf"),
        "technical_profile": {
            "data_halls": 2,
            "data_hall_sqm_each": 385,
            "data_hall_sqm": 770,
            "UPS": "four_625kVA",
            "electrical_redundancy": "2N",
            "generators": "four_1250kW",
            "diesel_autonomy_days": 7,
            "power_supply": "two_5MVA_23kV_medium_voltage_service_drops",
            "cooling": "twelve_units_four_redundant_cold_aisle_containment",
            "average_PUE": 1.8,
        },
        "OSM_refs": [],
    },
    {
        "id": "kio_mer1_merida",
        "code": "MER1",
        "provider_label": "MER | 1 Merida",
        "country_code": "MX",
        "locality": "Merida, Yucatan",
        "address": "Calle 19 #444, Ciudad Industrial, Merida, Yucatan, 97288",
        "official_page": location("mer-1-merida"),
        "spec_sheet": spec_sheet("03/SPEC-SHEET_MER1_ENG.pdf"),
        "technical_profile": {
            "ATOM_modular_rooms": 8,
            "data_hall_sqm": 89,
            "UPS": "six_109kVA",
            "electrical_redundancy": "2N",
            "generators": "two_500kW",
            "diesel_autonomy_days": 4,
            "power_supply": "single_13_2kV_medium_voltage_service_drop",
            "cooling": "free_cooling_support",
            "design_PUE": 2.1,
        },
        "OSM_refs": ["osm_way_1448297728"],
    },
    {
        "id": "kio_her1_hermosillo",
        "code": "HER1",
        "provider_label": "HER | 1 Hermosillo",
        "country_code": "MX",
        "locality": "Hermosillo, Sonora",
        "address": "Calle General Bernardo Reyes No. 98, Hermosillo, Sonora, 83190",
        "official_page": location("her-1-hermosillo"),
        "spec_sheet": spec_sheet("03/SPEC-SHEET_HER1_ENG.pdf"),
        "technical_profile": {
            "ATOM_modular_rooms": 7,
            "data_hall_sqm": 73,
            "UPS": "six_219_6kVA",
            "electrical_redundancy": "2N",
            "generators": "two_600kW",
            "diesel_autonomy_days": 3.5,
            "power_supply": "13_2kV_medium_voltage_service_drop",
            "cooling": "seventeen_units_seven_redundant",
            "design_PUE": 1.7,
        },
        "OSM_refs": ["osm_way_1448293080"],
    },
    {
        "id": "kio_mty1_monterrey",
        "code": "MTY1",
        "provider_label": "MTY | 1 Monterrey",
        "country_code": "MX",
        "locality": "San Pedro Garza Garcia, Monterrey",
        "address": "Av. Gomez Morin 350 Sur, 2nd floor, Valle Campestre, 66265, San Pedro Garza Garcia, NL",
        "official_page": location("mty-1"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MTY1_ENG.pdf"),
        "technical_profile": {
            "data_hall_sqm": 306,
            "UPS": "two_225kVA",
            "electrical_redundancy": "2N",
            "generators": "two_500kW",
            "diesel_autonomy_days": 4,
            "power_supply": "13_8kV_medium_voltage_service_drop",
            "cooling": "nine_units_three_redundant_cold_aisle_containment",
            "average_PUE": 1.7,
        },
        "OSM_refs": ["osm_way_1448291730"],
    },
    {
        "id": "kio_qro2_el_marques",
        "code": "QRO2",
        "provider_label": "QRO | 2 Queretaro",
        "country_code": "MX",
        "locality": "El Marques, Queretaro",
        "address": "Cerrada de la Princesa No. 4, Parque Industrial El Marques, Queretaro, 76246",
        "official_page": location("qro-2-el-marques"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_QRO2_ENG.pdf"),
        "technical_profile": {
            "current_page_data_hall_sqm": 3120,
            "current_IT_load_mw": 12,
            "IT_blocks": "five_2MW_plus_two_redundant_catcher_blocks",
            "expandable_IT_load_mw": 18,
            "electrical_redundancy": "concurrently_maintainable",
            "generators": "eight_3MW",
            "power_supply": "6MW_medium_voltage_plus_6MW_high_voltage_intake",
            "cooling": "thirty_chilled_water_units_two_redundant_air_cooled_chillers_free_cooling_closed_loop",
            "design_PUE": 1.5,
        },
        "publication_conflicts": [
            "current_page_3120sqm_versus_PDF_narrative_3114sqm_and_PDF_hall_rows_3226sqm",
            "PDF_narrative_eight_generators_versus_table_typo_88_two_catchers",
        ],
        "OSM_refs": ["osm_way_741133962"],
    },
    {
        "id": "kio_qro1_el_marques",
        "code": "QRO1",
        "provider_label": "QRO | 1 Queretaro",
        "country_code": "MX",
        "locality": "El Marques, Queretaro",
        "address": "Cerrada de la Princesa 4, Parque Industrial El Marques, Queretaro, 76246",
        "official_page": location("qro-1"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_QRO1_ENG-1.pdf"),
        "technical_profile": {
            "data_halls": 7,
            "data_hall_sqm": 5166,
            "UPS": "twenty_750kVA",
            "electrical_redundancy": "2N",
            "generators": "twelve_2000kW",
            "diesel_autonomy_days": 7,
            "power_supply": "two_14MVA_34_5kV_medium_voltage_service_drops",
            "cooling": "fifty_two_units_ten_redundant_indirect_free_cooling",
            "design_PUE": 1.7,
        },
        "OSM_refs": ["osm_way_741133962"],
    },
    {
        "id": "kio_mex6_lerma",
        "code": "MEX6",
        "provider_label": "MEX | 6 Lerma",
        "country_code": "MX",
        "locality": "Lerma, State of Mexico",
        "address": "Av. Libertad Oriente 415, San Miguel Chapultepec, Lerma, Estado de Mexico, 52240",
        "official_page": location("mex-6-lerma"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX6_ENG.pdf"),
        "technical_profile": {
            "data_halls": 4,
            "data_hall_sqm_each": 610,
            "data_hall_sqm": 2440,
            "UPS": "eight_900kW",
            "electrical_redundancy": "2N",
            "generators": "eight_2000kW",
            "diesel_autonomy_days": 6,
            "power_supply": "20MVA_23kV_medium_voltage_service_feed",
            "cooling": "N+2_controllers_and_2N_chillers",
            "PUE": "not_published_on_current_page",
        },
        "OSM_refs": ["osm_way_771466445"],
    },
    {
        "id": "kio_mex5_tultitlan",
        "code": "MEX5",
        "provider_label": "MEX | 5 Tultitlan",
        "country_code": "MX",
        "locality": "Tultitlan, State of Mexico",
        "address": "Blvd. Benito Juarez 20, corner Av. Lopez Portillo, San Mateo Cuautepec, Tultitlan, Estado de Mexico, 54948",
        "official_page": location("mexico-5-tultitlan"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX5_ENG.pdf"),
        "technical_profile": {
            "white_floor_sqm": 8000,
            "data_halls": 8,
            "data_hall_sqm": 6817,
            "UPS": "thirty_two_600kVA",
            "electrical_redundancy": "2N",
            "generators": "twelve_2400kW",
            "diesel_autonomy_days": 7,
            "power_supply": "two_7_5MVA_independent_critical_feeds_plus_2MVA_general_services",
            "cooling": "indirect_and_direct_free_cooling_highly_redundant",
            "design_PUE": 1.6,
        },
        "OSM_refs": ["osm_way_720313550"],
    },
    {
        "id": "kio_mex4_interlomas",
        "code": "MEX4",
        "provider_label": "MEX | 4 Interlomas",
        "country_code": "MX",
        "locality": "Huixquilucan, State of Mexico",
        "address": "Blvd. Magnocentro 6, Centro Urbano Interlomas, 52760 Huixquilucan, Estado de Mexico",
        "official_page": location("mex-4-interlomas"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX4_ENG.pdf"),
        "technical_profile": {
            "data_halls": 3,
            "data_hall_sqm": 3450,
            "UPS": "four_1000kVA",
            "electrical_redundancy": "2N",
            "generators": "four_2MW",
            "diesel_autonomy_days_up_to": 4,
            "power_supply": "one_3_5MVA_medium_voltage_service_drop",
            "cooling": "thirty_seven_units_ten_redundant_current_page_calls_scheme_N_plus_question_mark",
            "average_PUE": 1.8,
        },
        "publication_conflicts": ["current_page_literally_publishes_cooling_redundancy_as_N_plus_question_mark"],
        "OSM_refs": ["osm_way_830620671"],
    },
    {
        "id": "kio_mex3_santa_fe",
        "code": "MEX3",
        "provider_label": "MEX | 3 Santa Fe",
        "country_code": "MX",
        "locality": "Santa Fe, Mexico City",
        "address": "Alfonso Napoles Gandara 50 PB, Pena Blanca Santa Fe, Ciudad de Mexico, 01210",
        "official_page": location("mex-3-santa-fe"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX3_ENG.pdf"),
        "technical_profile": {
            "data_halls": 1,
            "data_hall_sqm": 902,
            "UPS": "four_225kVA_plus_two_130kVA",
            "electrical_redundancy": "2N",
            "generators": "two_1MW",
            "diesel_autonomy_days": 4,
            "power_supply": "23kV_medium_voltage_service_drop",
            "cooling": "N+1",
            "average_PUE": 1.7,
        },
        "OSM_refs": ["osm_way_1448283393"],
    },
    {
        "id": "kio_mex2_santa_fe",
        "code": "MEX2",
        "provider_label": "MEX | 2 Santa Fe",
        "country_code": "MX",
        "locality": "Santa Fe, Mexico City",
        "address": "Prolongacion Paseo de la Reforma 5396, Cuajimalpa, Ciudad de Mexico, 05000",
        "official_page": location("santa-fe-mex-2"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX2_ENG.pdf"),
        "technical_profile": {
            "current_page_data_halls": 2,
            "current_page_data_hall_sqm_each": 600,
            "current_page_data_hall_sqm": 1200,
            "UPS": "six_1000kVA",
            "electrical_redundancy": "2N",
            "generators": "2_5MW_rating_published_without_quantity_on_current_page",
            "diesel_autonomy_days": 7,
            "power_supply": "dual_5MVA_23kV_feeds",
            "cooling": "N+2_indirect_free_cooling",
            "current_page_design_PUE": 1.5,
        },
        "publication_conflicts": [
            "current_page_two_600sqm_halls_versus_PDF_five_rooms_1457sqm",
            "current_page_design_PUE_1_5_versus_PDF_1_6",
            "current_page_generator_quantity_absent_while_PDF_table_says_four_and_total_generator_capacity_2500kW",
        ],
        "OSM_refs": ["osm_way_1448065060"],
    },
    {
        "id": "kio_mex1_santa_fe",
        "code": "MEX1",
        "provider_label": "MEX | 1 Santa Fe",
        "country_code": "MX",
        "locality": "Santa Fe, Mexico City",
        "address": "Carretera Mexico-Toluca 5287, Lomas de Vista Hermosa, Cuajimalpa, CDMX",
        "official_page": location("santa-fe-1"),
        "spec_sheet": spec_sheet("06/SPEC-SHEET_MEX1_ENG.pdf"),
        "technical_profile": {
            "data_halls": 4,
            "data_hall_sqm_each": 650,
            "data_hall_sqm": 2600,
            "UPS": "eight_400kVA",
            "electrical_redundancy": "N+1",
            "generators": "four_1_5MW",
            "diesel_autonomy_days": 7,
            "power_supply": "dual_23kV_medium_voltage_feeds",
            "cooling": "N+2",
            "average_PUE": 1.7,
        },
        "OSM_refs": ["osm_way_1448061960"],
    },
]


OSM_CROSSWALK = {
    "osm_way_1448061960": (["kio_mex1_santa_fe"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_1448065060": (["kio_mex2_santa_fe"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_1448283393": (["kio_mex3_santa_fe"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_830620671": (["kio_mex4_interlomas"], "name_includes_office_and_current_KIO_facility"),
    "osm_way_720313550": (["kio_mex5_tultitlan"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_771466445": (["kio_mex6_lerma"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_1448293080": (["kio_her1_hermosillo"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_1448297728": (["kio_mer1_merida"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_1448291730": (["kio_mty1_monterrey"], "exact_name_and_coordinate_candidate_current_KIO_facility"),
    "osm_way_741133962": (["kio_qro1_el_marques", "kio_qro2_el_marques"], "one_OSM_campus_polygon_names_both_current_same_address_facilities"),
    "osm_way_1253983161": (["kumo_murcia"], "legacy_KIO_Networks_Espana_tag_current_Kumo_Networks_facility"),
    "osm_way_1253983162": (["kumo_valencia_paterna"], "legacy_KIO_Networks_Espana_tag_current_Kumo_Networks_facility"),
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def build_records(accessed_on: str) -> list[dict]:
    records = []
    for order, source in enumerate(FACILITIES, start=1):
        row = dict(source)
        row.update({
            "object_type": "KIOOfficialFacilityRecord",
            "source_order": order,
            "lifecycle_as_of_access": "operating_current_provider_location_roster",
            "facility_boundary": "One current location page is one marketed facility code; campus, building and data-hall counts remain separate.",
            "power_boundary": "IT load, utility MW/MVA, UPS and generator nameplates, expansion potential and live utilized or billed load remain separate.",
            "GPU_boundary": "AI-ready and high-density workload language does not establish a physical accelerator model, count, owner, host site, delivery state, power draw or utilization.",
            "source_urls": [KIO_LOCATIONS, source["official_page"], source["spec_sheet"]],
            "accessed_on": accessed_on,
        })
        records.append(row)
    assert len(records) == 15
    assert len({row["id"] for row in records}) == 15
    assert len({row["code"] for row in records}) == 15
    assert Counter(row["country_code"] for row in records) == {"MX": 11, "CO": 1, "DO": 1, "GT": 1, "PA": 1}
    assert sum((row["technical_profile"].get("data_hall_sqm") or row["technical_profile"].get("current_page_data_hall_sqm", 0)) for row in records) == 28490
    assert sum(len(row["OSM_refs"]) for row in records) == 11
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_id, (facility_refs, status) in OSM_CROSSWALK.items():
        source = osm[osm_id]
        operator = source.get("operator")
        assert operator in {"KIO", "KIO Networks España", None}
        rows.append({
            "osm_ref": osm_id,
            "name": source.get("name"),
            "raw_operator": operator,
            "website": source.get("website"),
            "country_codes": sorted({candidate["iso2"] for candidate in source.get("country_candidates", [])}),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_refs": facility_refs,
            "crosswalk_status": status,
            "boundary": "OSM geometry and legacy operator text do not prove current ownership, building count, lifecycle, floor area, load, equipment, GPU inventory or utilization.",
            "source_url": source["source_url"],
        })
    assert len(rows) == 12
    assert Counter(row["raw_operator"] for row in rows) == {"KIO": 9, "KIO Networks España": 2, None: 1}
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    sources = sorted({url for row in records for url in row["source_urls"]} | {
        KIO_HOME, KIO_ESG, QRO2_OPENING, GTM2_EXPANSION, MEX8_CONSTRUCTION,
        ISQ_ACTIVE, ISQ_ACQUISITION, IFC_PROJECT, KUMO_LOCATIONS,
        KUMO_MURCIA_SHEET, KUMO_VALENCIA_GENERATORS, KUMO_VALENCIA_COOLING,
        KUMO_VALENCIA_INVESTMENT, ECI_BUSINESS_LINES, ECI_FY2024_ACCOUNTS,
        ECI_FY2025_RESULTS,
    })
    return {
        "id": "kio_official_facility_summary_2026_07_19",
        "object_type": "KIOPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator": "KIO Data Centers / Sixsigma Networks Mexico",
        "current_provider_roster": {
            "location_pages": len(records),
            "countries": ["MX", "CO", "GT", "PA", "DO"],
            "country_distribution": dict(sorted(Counter(row["country_code"] for row in records).items())),
            "current_page_data_hall_sqm_checksum": 28490,
            "current_homepage_claim": "15_data_centers_across_five_Latin_American_countries",
            "current_location_page_codes": [row["code"] for row in records],
            "historical_scope_not_current": "older_material_said_40_plus_data_centers_17_cities_and_included_edge_sites_and_Spain",
            "boundary": "The current 15-page roster is a provider directory, not a physical-building census or an operating, energized, leased, utilized or billed MW total.",
        },
        "power_cooling_and_engineering": {
            "site_pages_with_UPS_or_IT_block_detail": 15,
            "site_pages_with_generator_detail": 15,
            "site_pages_with_feed_voltage_or_capacity_detail": 15,
            "site_pages_with_numeric_PUE": 14,
            "selected_high_scale_sites": {
                "QRO2": {"current_IT_load_mw": 12, "expandable_IT_load_mw": 18, "generators": "eight_3MW", "cooling": "thirty_chilled_water_units_two_redundant", "design_PUE": 1.5},
                "QRO1": {"UPS": "twenty_750kVA", "generators": "twelve_2MW", "utility": "two_14MVA_34_5kV_feeds", "data_hall_sqm": 5166},
                "MEX5": {"data_hall_sqm": 6817, "UPS": "thirty_two_600kVA", "generators": "twelve_2_4MW", "utility": "two_7_5MVA_critical_feeds_plus_2MVA_general"},
                "BOG1": {"current_PDF_IT_and_telecom_capacity_mw": 5.8, "current_PDF_adjacent_BOG2_potential_mw": 11.2, "utility": "10MVA_34_5kV", "generators": "three_1_65MW"},
            },
            "boundary": "Equipment ratings are nameplates and topology evidence, not actual load. MVA, utility MW, critical IT MW, generator MW, UPS kVA and future capacity are never added into one portfolio total.",
        },
        "publication_conflicts": {
            "BOG1": [
                "current_page_1160sqm_initial_hall_scope_versus_current_PDF_2352sqm_first_stage",
                "page_three_500kVA_IT_UPS_branches_versus_PDF_table_six",
                "current_PDF_5_8MW_versus_older_2025_sheet_5_6MW",
            ],
            "MEX2": ["page_two_halls_1200sqm_versus_PDF_five_rooms_1457sqm", "page_PUE_1_5_versus_PDF_1_6", "generator_quantity_and_total_rating_ambiguous"],
            "QRO2": ["page_3120sqm_versus_PDF_narrative_3114sqm_and_hall_rows_3226sqm", "PDF_table_88_generators_is_inconsistent_with_page_and_PDF_narrative_eight"],
            "MEX4": ["current_page_publishes_cooling_redundancy_as_N_plus_question_mark"],
            "renewable_energy": ["current_homepage_79_percent", "2025_Guatemala_release_more_than_90_percent_company_claim", "2023_BOG1_release_more_than_95_percent"],
            "resolution": "retain_publication_date_and_scope_without_silent_selection_or_false_precision",
        },
        "growth_pipeline": {
            "QRO2": {"opened": "2025-12-08", "IT_load_mw": 12, "QRO1_plus_QRO2_installed_capacity_mw_nearly": 19, "high_density_workloads": True},
            "GTM2": {"announced_construction": "2025-09-25", "initial_rooms": 2, "initial_room_kw_each": 500, "potential_rooms": 4, "potential_IT_load_mw": 2, "cabinet_density_kw_range": [5, 12], "target_PUE": 1.5, "target_renewable_percent_more_than": 80},
            "MEX8": {"announced_construction": "2026-03-09", "investment_USD_million": 70, "incremental_installed_capacity_mw": 4, "renewable_energy_percent": 79, "construction_jobs_direct_and_indirect": 3000},
            "regional_CAPEX_claim_USD_million_more_than": 400,
            "boundary": "The greater-than-USD400m regional CAPEX claim has no disclosed spend schedule, funding bridge or facility allocation. MEX8 and GTM2 are future projects and are excluded from the 15 current location pages.",
        },
        "AI_and_accelerators": {
            "evidence": ["GTM2_described_as_AI_ready", "QRO2_supports_high_density_workloads", "current_hyperscale_offer_supports_2MW_plus_deployments", "historical_Gcore_partner_offer_named_A100_and_H100"],
            "physical_KIO_owned_GPU_or_accelerator_count": "undisclosed",
            "manufacturer_model_owner_financier_exact_host_site_delivery_power_draw_and_utilization": "undisclosed",
            "accelerator_ledger_action": "no_row_because_no_source_discloses_a_physical_or_model_specific_quantity_allocated_to_KIO",
            "boundary": "A partner GPU service, AI-ready design and customer workload accommodation do not establish KIO-owned or installed accelerators.",
        },
        "ownership_and_financials": {
            "current_owner": "I_Squared_Capital_sponsored_funds",
            "acquisition_completed": "2021-12-02",
            "acquisition_price": "undisclosed",
            "acquisition_scope_capacity_mw_more_than": 20,
            "IFC_investment": {"status": "active", "approved_USD_million": 30.10, "signed": "2022-01-04", "invested": "2022-01-07", "instrument": "equity_in_acquisition_vehicle"},
            "KIO_standalone_current_revenue": "undisclosed",
            "KIO_standalone_current_operating_profit": "undisclosed",
            "KIO_standalone_current_EBITDA_capex_debt_cash_flow_and_ROIC": "undisclosed",
            "boundary": "IFC equity, acquisition capacity and announced CAPEX are not revenue, operating profit, valuation, debt or free cash flow. I Squared fund AUM is not KIO revenue.",
        },
        "Spain_legacy_and_Kumo_successor": {
            "current_company": "Kumo Networks S.A.U.",
            "former_name": "KIO Networks España S.A.",
            "current_owner": "El_Corte_Ingles_100_percent",
            "ownership_change": "El_Corte_Ingles_acquired_remaining_50_percent_on_2024_10_01",
            "current_operating_facilities": 2,
            "facilities": {
                "Murcia": {"opened": 2014, "technical_floor_phase_1_sqm": 172, "maximum_cabinets": 78, "stated_IT_capacity_kw": 528, "redundancy": "2N_Tier_IV", "UPS_capacity_kVA": 600, "transformer_capacity_kVA": 1600, "generators": "two_1_2MW_published_capacity_denominator_ambiguous", "diesel": "four_tanks_21000L_total_96_hours", "cooling": "eighteen_units_nine_redundant_528kW"},
                "Valencia_Paterna": {"inaugurated": "2026-06", "investment_EUR_million_more_than": 52, "generators": "two_units_published_2_5MW_denominator_ambiguous", "diesel_liters": 100000, "diesel_autonomy_days": 8, "geothermal_wells": 71, "CO2_storage_tanks": "two_9000L", "CO2_pumps": 10, "cooling": "closed_loop_CO2_with_geothermal_support"},
            },
            "financial_boundary": "El Corte Ingles FY2025 Surface Commercialization revenue EUR95m and EBITDA EUR58m include Kumo plus store and independent-space activity; neither figure is Kumo standalone revenue or profit.",
            "OSM_boundary": "Two OSM objects still say KIO Networks España but route to current Kumo, not to KIO's Latin American 15-site roster.",
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_rows),
            "current_KIO_related_objects": sum(row["raw_operator"] in {"KIO", None} for row in osm_rows),
            "legacy_Spain_objects_now_Kumo": sum(row["raw_operator"] == "KIO Networks España" for row in osm_rows),
            "current_KIO_facility_codes_matched": 11,
            "current_KIO_facility_codes_unmatched": 4,
            "unmatched_current_codes": ["BOG1", "SDO1", "GTM1", "PAN1"],
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_rows), 3),
            "objects": osm_rows,
            "boundary": "The one QRO OSM polygon names both QRO1 and QRO2. Object, facility-code, campus and building counts therefore cannot be substituted for one another.",
        },
        "unresolved_gaps": [
            "provider_resolution_of_current_page_and_PDF_conflicts",
            "per_site_energized_leased_utilized_customer_accepted_and_billed_IT_load",
            "complete_building_parcel_property_title_and_lease_roster",
            "current_as_built_substation_transformer_switchgear_busbar_PDU_UPS_battery_generator_fuel_chiller_CRAH_CDU_counts_ratings_topology_and_OEMs",
            "physical_GPU_model_count_owner_site_delivery_power_draw_utilization_customer_revenue_and_margin",
            "KIO_standalone_revenue_operating_profit_EBITDA_capex_debt_cash_flow_customer_concentration_site_economics_and_ROIC",
            "regional_400m_CAPEX_timing_funding_overlap_and_project_allocation",
            "per_site_measured_PUE_WUE_water_energy_emissions_and_hourly_renewable_matching",
            "four_current_facility_codes_without_exact_public_map_crosswalk",
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
    registry_path = args.output_dir / "kio_official_facility_registry.jsonl"
    summary_path = args.output_dir / "kio_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
