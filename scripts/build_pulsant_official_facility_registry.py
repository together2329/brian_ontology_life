#!/usr/bin/env python3
"""Build Pulsant's current facility, engineering, financial and OSM registry.

Pulsant publishes a clean fourteen-facility roster, but its current HTML cards,
downloadable data sheets, expansion announcements, statutory accounts and public
map objects use different measures and sometimes conflict.  This builder keeps
facility IT power, incoming MVA, available capacity, physical buildings, customer
hardware, group accounting and OSM geometries separate.  It does not infer live
load, GPU inventory or an as-built equipment bill of materials.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


COLOCATION = "https://www.pulsant.com/colocation"
ESG_2024 = "https://www.pulsant.com/hubfs/PUL168%20ESG%20document%202024%20-%20Final.pdf"
AI_INFERENCING = "https://www.pulsant.com/ai-inferencing"
MK_HIGH_DENSITY = "https://www.pulsant.com/milton-keynes-high-density"
MK_COMPLETION = "https://www.pulsant.com/knowledge-hub/announcements/uk-data-centre-operator-launches-high-density-facility-outside-london"
MANCHESTER_COMPLETION = "https://www.pulsant.com/knowledge-hub/announcements/pulsant-powers-up-the-manchester-digital-strategy"
MANCHESTER_INVESTMENT = "https://www.pulsant.com/knowledge-hub/announcements/pulsant-invests-4.5m-into-platformedge-in-manchester-data-centre"
ACQUISITION_COMPLETE = "https://www.pulsant.com/knowledge-hub/announcements/pulsant-completes-acquisition-of-two-data-centres-from-scc"
REFINANCING = "https://www.pulsant.com/knowledge-hub/announcements/pulsant-completes-five-year-refinancing"
EXPERIENCE_PROGRAMME = "https://www.pulsant.com/knowledge-hub/announcements/pulsant-completes-2m-uk-data-centre-investment-programme"
ANTIN_PORTFOLIO = "https://www.antin-ip.com/investments/pulsant"
ANTIN_ACQUISITION = "https://www.antin-ip.com/media/our-news/antin-infrastructure-partners-acquires-pulsant"
PULSANT_COMPANY = "https://find-and-update.company-information.service.gov.uk/company/03625971"
PULSANT_FY2024 = "https://find-and-update.company-information.service.gov.uk/company/03625971/filing-history/MzQ2OTgxNzgxNWFkaXF6a2N4/document?download=0&format=pdf"
MONCH_COMPANY = "https://find-and-update.company-information.service.gov.uk/company/13469899"
MONCH_FY2024 = "https://find-and-update.company-information.service.gov.uk/company/13469899/filing-history/MzQ2OTgxNzgxN2FkaXF6a2N4/document?format=pdf&download=0"
EDINBURGH_HOSTING_DISCLOSURE = "https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/documents/92903/182334399614577-service-definition-document-2022-05-10-1450.pdf"
LONDON_PROJECT = "https://www.dataprojex.pro/completed-projects/pulsant-data-center/"


def page(slug: str) -> str:
    return f"https://www.pulsant.com/{slug}"


def sheet(path: str) -> str:
    return f"https://www.pulsant.com/hubfs/{path}"


FACILITIES = [
    {
        "id": "pulsant_sc_1_edinburgh_south_gyle",
        "code": "SC-1",
        "provider_label": "Edinburgh South Gyle SC-1",
        "region": "Scotland",
        "locality": "Edinburgh",
        "address": "The Clocktower, South Gyle Crescent, Edinburgh EH12 9LB",
        "official_page": page("colocation/sc-1"),
        "data_sheet": sheet("Data%20Sheets/Edinburgh%20SC-1.pdf"),
        "current_card": {"building_sqm": 4648, "data_hall_sqm": 2628, "IT_power_mw": 3.4, "incoming_power_supplies": 2, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 6},
        "OSM_refs": ["osm_relation_18217492", "osm_way_37943653", "osm_way_37943663"],
    },
    {
        "id": "pulsant_sc_2_edinburgh_medway",
        "code": "SC-2",
        "provider_label": "Edinburgh SC-2",
        "region": "Scotland",
        "locality": "Edinburgh",
        "address": "7 Bankhead Medway, Sighthill Industrial Estate, Edinburgh EH11 4BY",
        "official_page": page("colocation-medway-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Edinburgh%20SC-2.pdf"),
        "current_card": {"building_sqm": 3121, "data_hall_sqm": 1449, "IT_power_mw": 2.16, "incoming_power_supplies": 2, "UPS": "N+1", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"building_sqm": 3131, "incoming_power_mva": 3.2},
        "publication_conflicts": ["current_HTML_building_3121_sqm_versus_data_sheet_3131_sqm"],
        "OSM_refs": ["osm_way_61123230"],
    },
    {
        "id": "pulsant_sc_3_edinburgh_newbridge",
        "code": "SC-3",
        "provider_label": "Edinburgh SC-3",
        "region": "Scotland",
        "locality": "Edinburgh",
        "address": "7 Claylands Road, Newbridge, Edinburgh EH28 8LF",
        "official_page": page("colocation-newbridge-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Edinburgh%20SC-3.pdf"),
        "current_card": {"building_sqm": 991, "data_hall_sqm": 630, "IT_power_mw": 1.3, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 2, "IT_power_mw": 0.64},
        "publication_conflicts": ["current_HTML_IT_power_1_3MW_versus_data_sheet_0_64MW"],
        "OSM_refs": ["osm_way_251948724"],
    },
    {
        "id": "pulsant_wm_1_birmingham",
        "code": "WM-1",
        "provider_label": "Birmingham WM-1",
        "region": "Midlands",
        "locality": "Birmingham",
        "address": "Westwood Avenue, Tyseley, Birmingham B11 3RZ",
        "official_page": page("colocation-birmingham-wm1"),
        "data_sheet": sheet("Data%20Sheets/Birmingham%20WM-1.pdf"),
        "current_card": {"building_sqm": 5007, "data_hall_sqm": 2405, "IT_power_mw": 2, "incoming_power_supplies": 2, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 8},
        "site_engineering": {"photovoltaic_kw": 650},
        "acquisition": "acquired_from_SCC_completed_2025_06_02",
        "OSM_refs": [],
    },
    {
        "id": "pulsant_yh_1_rotherham",
        "code": "YH-1",
        "provider_label": "Rotherham YH-1",
        "region": "Yorkshire",
        "locality": "Rotherham",
        "address": "Unit 1, Pioneer Close, Manvers, Rotherham S63 7JZ",
        "official_page": page("colocation-rotherham-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Rotherham%20YH-1.pdf"),
        "current_card": {"building_sqm": 2013, "data_hall_sqm": 343, "IT_power_mw": 0.18, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 2},
        "OSM_refs": [],
    },
    {
        "id": "pulsant_ne_1_newcastle_central",
        "code": "NE-1",
        "provider_label": "Newcastle NE-1",
        "region": "North East",
        "locality": "Newcastle upon Tyne",
        "address": "5 Bridge View, Stepney Lane, Newcastle upon Tyne NE1 6PN",
        "official_page": page("colocation-newcastle-central-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Newcastle%20NE-1.pdf"),
        "current_card": {"building_sqm": 557, "data_hall_sqm": 464, "IT_power_mw": 0.72, "incoming_power_supplies": None, "UPS": "N+1", "standby_power": "N", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 1.6, "UPS": "2N"},
        "publication_conflicts": ["current_HTML_UPS_N_plus_1_versus_data_sheet_2N"],
        "OSM_refs": [],
    },
    {
        "id": "pulsant_ne_2_newcastle_north_shields",
        "code": "NE-2",
        "provider_label": "Newcastle NE-2",
        "region": "North East",
        "locality": "North Shields",
        "address": "New York Way, North Shields, Tyne & Wear NE27 0QF",
        "official_page": page("colocation-newcastle-ne2"),
        "data_sheet": sheet("Data%20Sheets/Newcastle%20NE-2.pdf"),
        "current_card": {"building_sqm": 816, "data_hall_sqm": 374, "IT_power_mw": 0.25, "incoming_power_supplies": None, "UPS": "N", "standby_power": "N", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 0.8},
        "OSM_refs": [],
    },
    {
        "id": "pulsant_nw_1_manchester",
        "code": "NW-1",
        "provider_label": "Manchester NW-1",
        "region": "North West",
        "locality": "Trafford Park / Manchester",
        "address": "1-2 Ball Green, Cobra Court, Trafford Park M32 0QT",
        "official_page": page("colocation-manchester-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Manchester%20NW-1.pdf"),
        "current_card": {"building_sqm": 1200, "data_hall_sqm": 936, "IT_power_mw": 1, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 2},
        "expansion": {"investment_GBP_million": 4.5, "additional_IT_capacity_kw": 300, "additional_data_hall_sqm": 320, "data_hall": 4, "first_customer": "Dacoll", "completion_release": "2024-03-19"},
        "OSM_refs": [],
    },
    {
        "id": "pulsant_se_1_milton_keynes",
        "code": "SE-1",
        "provider_label": "Milton Keynes SE-1",
        "region": "South East",
        "locality": "Milton Keynes",
        "address": "St. Neots House, Rockingham Drive, Milton Keynes MK14 6LY",
        "official_page": page("colocation-milton-keynes-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Milton%20Keynes%20SE-1%20New%20Data%20Hall.pdf"),
        "current_card": {"building_sqm": 2027, "data_hall_sqm": 1116, "IT_power_mw": 2.2, "incoming_power_supplies": 2, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 3, "high_density_kw_per_rack_up_to": 40},
        "high_density_expansion": {"investment_GBP_million": 10, "expansion_mw": 1.2, "completed": "2026-02-09", "immediately_available_mw": 1.2, "dedicated_page_kw_per_rack_up_to": 20, "dedicated_page_card_note": "2.2MW_additional_600kW_being_fitted"},
        "publication_conflicts": ["new_data_hall_sheet_and_facility_page_40kW_density_versus_dedicated_high_density_page_20kW", "older_SE_1_sheet_1_59MW_versus_current_HTML_and_new_hall_sheet_2_2MW"],
        "OSM_refs": ["osm_way_460010262"],
    },
    {
        "id": "pulsant_se_2_maidenhead",
        "code": "SE-2",
        "provider_label": "Maidenhead SE-2",
        "region": "South East",
        "locality": "Maidenhead",
        "address": "Bluesquare House, Priors Way, Maidenhead SL6 2HP",
        "official_page": page("colocation-maidenhead-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Maidenhead%20SE-2.pdf"),
        "current_card": {"building_sqm": 941, "data_hall_sqm": 860, "IT_power_mw": 1, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 2},
        "OSM_refs": ["osm_way_49602062", "osm_way_49602063"],
    },
    {
        "id": "pulsant_se_3_reading_south",
        "code": "SE-3",
        "provider_label": "Reading SE-3",
        "region": "South East",
        "locality": "Reading",
        "address": "Unit 2, Smallmead Road, Reading RG2 0QS",
        "official_page": page("colocation-reading-south-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Reading%20SE-3.pdf"),
        "current_card": {"building_sqm": 2494, "data_hall_sqm": 1423, "IT_power_mw": 2.8, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 4, "PUE": 1.2},
        "OSM_refs": [],
    },
    {
        "id": "pulsant_se_4_reading_east",
        "code": "SE-4",
        "provider_label": "Reading SE-4",
        "region": "South East",
        "locality": "Reading",
        "address": "Suttons Business Park, Reading RG6 1AZ",
        "official_page": page("colocation-reading-east-datacentre"),
        "data_sheet": sheet("Data%20Sheets/Reading%20SE-4.pdf"),
        "current_card": {"building_sqm": 1500, "data_hall_sqm": 590, "IT_power_mw": 0.76, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 1.5},
        "OSM_refs": ["osm_way_63983065"],
    },
    {
        "id": "pulsant_ln_1_croydon",
        "code": "LN-1",
        "provider_label": "Croydon LN-1",
        "region": "London",
        "locality": "Croydon",
        "address": "Unit 1, 35 Imperial Way, Croydon CR0 4RR",
        "official_page": page("colocation-south-london-datacentre"),
        "data_sheet": sheet("Croydon%20LN-1%20Data%20Sheet.pdf"),
        "current_card": {"building_sqm": 3282, "data_hall_sqm": 1223, "IT_power_mw": 1.35, "incoming_power_supplies": None, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 4},
        "OSM_refs": ["osm_way_180779572"],
    },
    {
        "id": "pulsant_se_5_fareham",
        "code": "SE-5",
        "provider_label": "Fareham SE-5",
        "region": "South East",
        "locality": "Fareham",
        "address": "18 Brunel Way, Fareham, Hampshire PO15 5TX",
        "official_page": page("colocation-fareham-se5"),
        "data_sheet": sheet("Data%20Sheets/Fareham%20SE-5.pdf"),
        "current_card": {"building_sqm": 7880, "data_hall_sqm": 2685, "IT_power_mw": 3, "incoming_power_supplies": 2, "UPS": "2N", "standby_power": "N+1", "cooling": "N+1", "renewable_energy_percent": 100},
        "data_sheet_scope": {"incoming_power_mva": 5},
        "site_engineering": {"grid": "two_dedicated_secure_connections_to_diverse_substations_fed_from_132kV_grid", "electrical_distribution": "2N", "cooling_technology": "chilled_water"},
        "acquisition": "acquired_from_SCC_completed_2025_06_02",
        "OSM_refs": [],
    },
]


OSM_CROSSWALK = {
    "osm_relation_18217492": ("pulsant_sc_1_edinburgh_south_gyle", "named_campus_relation_same_facility_as_two_building_ways"),
    "osm_way_37943653": ("pulsant_sc_1_edinburgh_south_gyle", "exact_named_facility_building_candidate"),
    "osm_way_37943663": ("pulsant_sc_1_edinburgh_south_gyle", "exact_named_facility_building_candidate"),
    "osm_way_61123230": ("pulsant_sc_2_edinburgh_medway", "exact_named_facility_candidate"),
    "osm_way_251948724": ("pulsant_sc_3_edinburgh_newbridge", "exact_named_facility_candidate"),
    "osm_way_49602062": ("pulsant_se_2_maidenhead", "same_facility_multi_building_candidate"),
    "osm_way_49602063": ("pulsant_se_2_maidenhead", "same_facility_multi_building_candidate"),
    "osm_way_460010262": ("pulsant_se_1_milton_keynes", "exact_named_facility_candidate"),
    "osm_way_63983065": ("pulsant_se_4_reading_east", "exact_named_facility_candidate"),
    "osm_way_180779572": ("pulsant_ln_1_croydon", "exact_named_facility_candidate"),
    "osm_way_96173979": (None, "Reading_Pulsant_building_not_confidently_crosswalked_to_current_SE_3_or_SE_4_address"),
    "osm_node_13655340206": (None, "Stockton_on_Tees_operator_node_not_in_current_fourteen_facility_roster"),
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
            "object_type": "PulsantOfficialFacilityRecord",
            "source_order": order,
            "country_code": "GB",
            "lifecycle_as_of_access": "operating_current_provider_roster",
            "facility_boundary": "One current provider code is treated as one marketed facility; a facility can contain multiple buildings or map objects and neither is inferred where unpublished.",
            "power_boundary": "Current-card IT MW, data-sheet incoming MVA, available MW, expansion MW, redundancy nameplates and utilized or billed load remain separate.",
            "GPU_boundary": "High-density and GPU-accelerated services do not establish a physical accelerator count, model, owner, exact host site, power draw or utilization.",
            "source_urls": sorted({COLOCATION, source["official_page"], source["data_sheet"]}),
            "accessed_on": accessed_on,
        })
        records.append(row)

    assert len(records) == 14
    assert len({row["id"] for row in records}) == 14
    assert len({row["code"] for row in records}) == 14
    assert round(sum(row["current_card"]["IT_power_mw"] for row in records), 2) == 22.12
    assert sum(row["current_card"]["building_sqm"] for row in records) == 36477
    assert sum(row["current_card"]["data_hall_sqm"] for row in records) == 17126
    assert round(sum(row["data_sheet_scope"]["incoming_power_mva"] for row in records), 1) == 45.1
    assert Counter(row["current_card"]["cooling"] for row in records) == {"N+1": 14}
    assert Counter(row["current_card"]["renewable_energy_percent"] for row in records) == {100: 14}
    assert sum(len(row["OSM_refs"]) for row in records) == 10
    return records


def build_osm_crosswalk(osm: dict[str, dict]) -> list[dict]:
    rows = []
    for osm_id, (facility_ref, status) in OSM_CROSSWALK.items():
        source = osm[osm_id]
        operator = source.get("operator")
        assert operator == "Pulsant" or (operator is None and source.get("name", "").startswith("Pulsant"))
        rows.append({
            "osm_ref": osm_id,
            "name": source.get("name"),
            "raw_operator": operator,
            "website": source.get("website"),
            "country_codes": sorted({candidate["iso2"] for candidate in source.get("country_candidates", [])}),
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "footprint_area_m2": source.get("footprint_area_m2"),
            "facility_ref": facility_ref,
            "crosswalk_status": status,
            "boundary": "OSM geometry is public-map evidence, not provider confirmation of ownership, lifecycle, gross floor area, IT load, equipment, GPU inventory or utilization.",
            "source_url": source["source_url"],
        })
    assert len(rows) == 12
    assert Counter(row["raw_operator"] for row in rows) == {"Pulsant": 10, None: 2}
    assert sum(row["facility_ref"] is not None for row in rows) == 10
    return sorted(rows, key=lambda row: row["osm_ref"])


def build_summary(records: list[dict], osm_rows: list[dict], accessed_on: str) -> dict:
    sources = sorted({url for row in records for url in row["source_urls"]} | {
        ESG_2024, AI_INFERENCING, MK_HIGH_DENSITY, MK_COMPLETION,
        MANCHESTER_COMPLETION, MANCHESTER_INVESTMENT, ACQUISITION_COMPLETE,
        REFINANCING, EXPERIENCE_PROGRAMME, ANTIN_PORTFOLIO, ANTIN_ACQUISITION,
        PULSANT_COMPANY, PULSANT_FY2024, MONCH_COMPANY, MONCH_FY2024,
        EDINBURGH_HOSTING_DISCLOSURE, LONDON_PROJECT,
    })
    return {
        "id": "pulsant_official_facility_summary_2026_07_19",
        "object_type": "PulsantPortfolioReconciliation",
        "accessed_on": accessed_on,
        "operator": "Pulsant Limited",
        "current_provider_roster": {
            "operating_facilities": len(records),
            "countries": ["GB"],
            "provider_ownership_claim": "all_owned_operated_and_interconnected",
            "acquisition_bridge": {"prior_facilities": 12, "acquired_from_SCC": ["Birmingham WM-1", "Fareham SE-5"], "completion": "2025-06-02", "current_facilities": 14, "ESG_capacity_increase_approximately_percent": 35},
            "current_card_checksums": {"IT_power_mw": 22.12, "building_sqm": 36477, "data_hall_sqm": 17126},
            "data_sheet_incoming_power_mva_checksum": 45.1,
            "boundary": "Checksums are QA sums of current marketing cards or data sheets. IT MW is not energized, leased, utilized, customer-accepted or billed load; MVA is apparent incoming power and is not added to IT MW.",
        },
        "publication_conflicts": {
            "SC_2_building_sqm": {"current_HTML": 3121, "data_sheet": 3131},
            "SC_3_IT_power_mw": {"current_HTML": 1.3, "data_sheet": 0.64},
            "NE_1_UPS": {"current_HTML": "N+1", "data_sheet": "2N"},
            "SE_1_IT_power_mw": {"current_HTML_and_new_hall_sheet": 2.2, "older_sheet": 1.59},
            "SE_1_rack_density_kw_up_to": {"dedicated_high_density_page": 20, "current_facility_page_and_new_hall_sheet": 40},
            "resolution": "retain_each_publication_scope_without_silent_selection_or_addition",
        },
        "power_cooling_and_environment": {
            "current_cards": {"cooling_N_plus_1_facilities": 14, "renewable_energy_100_percent_facilities": 14, "UPS_distribution": dict(sorted(Counter(row["current_card"]["UPS"] for row in records).items())), "standby_distribution": dict(sorted(Counter(row["current_card"]["standby_power"] for row in records).items()))},
            "selected_site_engineering": {
                "Fareham_SE_5": {"incoming_power_mva": 5, "feeds": 2, "grid": "diverse_substations_fed_from_132kV", "distribution": "2N", "cooling": "chilled_water_N_plus_1"},
                "Birmingham_WM_1": {"incoming_power_mva": 8, "photovoltaic_kw": 650},
                "Reading_SE_3": {"incoming_power_mva": 4, "data_sheet_PUE": 1.2},
                "Milton_Keynes_SE_1": {"incoming_power_mva": 3, "current_card_IT_mw": 2.2, "completed_high_density_expansion_mw": 1.2},
            },
            "portfolio_2024": {"electricity_kwh": 78144241, "PUE": 1.501, "PUE_2023": 1.523, "efficiency_savings_mwh": 1139, "emissions_tCO2e": 31360, "emissions_change_since_2019_percent": -31, "renewable_electricity": "100_percent_where_Pulsant_procures_with_REGOs", "cooling_water": "most_sites_cooling_does_not_consume_water"},
            "targets": {"PUE_2030": 1.3, "net_zero": 2050, "absolute_emissions_reduction_2030_percent_from_2019": 50, "remove_FM_200_by": 2030},
            "historical_or_unallocated_equipment_evidence": {
                "Edinburgh_hosting_service_document": {"exact_current_facility_code": "not_stated", "power": "dual_independent_11kV_feeds", "UPS": "dual_battery_string_Chloride", "generators": ["Cummins_1_4MW_diesel", "Cummins_850kW_diesel"], "testing": "monthly", "cooling": "fivefold_redundant_air_handling_units", "boundary": "Third-party G-Cloud service document names Pulsant Edinburgh but not a current facility code or as-of equipment census."},
                "2013_North_and_South_London_project": {"project_value_GBP_million": 7, "facility_scope": "two_approximately_500sqm_data_centres", "UPS": "N_plus_1_with_2N_distribution", "cooling": "DX_N_plus_1", "generator_replacement": "930kVA_to_2250kVA_prime_containerized_with_24_hour_bulk_fuel", "boundary": "Historical contractor project spans North and South London and cannot be propagated to current LN-1 or the wider estate."},
            },
            "boundary": "Redundancy labels do not reveal unit counts, ratings, OEMs, battery chemistry or runtime. Selected site and historical facts are not a current estate-wide as-built BOM.",
        },
        "AI_and_accelerators": {
            "service": ["GPU_accelerated_IaaS", "customer_colocation_for_accelerated_hardware", "regional_AI_inference"],
            "high_density_site": "Milton_Keynes_SE_1",
            "physical_GPU_or_accelerator_count": "undisclosed",
            "manufacturer_model_owner_financier_exact_host_site_delivery_power_draw_and_utilization": "undisclosed",
            "accelerator_ledger_action": "no_row_because_no_source_discloses_a_physical_or_model_specific_quantity",
            "boundary": "AI-ready, GPU-accelerated IaaS and a high-density hall establish capability and service marketing, not installed accelerator inventory.",
        },
        "FY2024_financials": {
            "Pulsant_Limited_separate_company_GBP": {"turnover": 100194062, "gross_profit": 25810801, "operating_profit": 8350387, "profit_before_tax": 178384, "net_profit": 275136, "cash": 12146000, "net_assets": 86792000, "derived_operating_margin_percent": 8.33},
            "Monch_Topco_group_GBP": {"revenue": 100194000, "gross_profit": 25811000, "EBITDA_before_exceptional": 21230000, "normalized_EBITDA": 21291000, "derived_EBITDA_margin_percent": 21.19, "operating_loss": -23755000, "depreciation": 10199000, "amortisation": 33041000, "exceptional_costs": 1745000, "loss_before_tax": -29677000, "net_loss": -25732000, "tangible_asset_additions": 8808000, "cash": 12507000, "average_employees": 326},
            "accounting_boundary": "Pulsant Limited reports positive accounting operating profit, while the consolidated parent reports a loss after large acquisition-accounting amortisation, depreciation and exceptional costs. Neither statement isolates colocation, cloud, network or individual-site economics.",
            "current_period_gap": "FY2024 predates the June 2025 SCC acquisition; FY2025 Monch Topco accounts were not yet filed and are due 2026-09-30.",
        },
        "ownership_financing_and_outlook": {
            "owner": "Antin Infrastructure Partners Mid Cap Fund I",
            "acquired_by_Antin": 2021,
            "2025_refinancing_GBP_million": 187,
            "refinancing_term_years": 5,
            "accordion_capacity": "available_amount_undisclosed",
            "use_of_funds": ["future_acquisitions", "existing_portfolio_development", "network_and_platformEDGE_cloud_services", "operational_performance_and_resilience"],
            "current_investment_examples_GBP_million": {"Milton_Keynes_high_density": 10, "Manchester_data_hall": 4.5, "two_year_experience_programme": 2},
            "positive_signals": ["fourteen_owned_operated_interconnected_regional_sites", "positive_Pulsant_Limited_operating_profit", "group_EBITDA_growth_despite_flat_revenue", "completed_SCC_acquisition_and_Milton_Keynes_high_density_hall", "five_year_refinancing_supports_expansion", "portfolio_PUE_improvement"],
            "risks": ["private_group_and_2025_financial_opacity", "large_depreciation_amortisation_and_financing_costs", "no_site_utilization_or_customer_concentration", "power_price_and_grid_availability", "publication_drift_between_HTML_and_data_sheets", "no_GPU_inventory_or_AI_revenue_disclosure", "acquisition_integration_and_capex_execution"],
        },
        "public_map_crosswalk": {
            "related_OSM_objects": len(osm_rows),
            "operator_tagged_objects": sum(row["raw_operator"] == "Pulsant" for row in osm_rows),
            "name_or_website_only_objects": sum(row["raw_operator"] is None for row in osm_rows),
            "exact_or_same_facility_candidate_objects": sum(row["facility_ref"] is not None for row in osm_rows),
            "matched_current_facility_codes": 7,
            "unmatched_current_facility_codes": 7,
            "footprint_area_m2_checksum": round(sum(row["footprint_area_m2"] or 0 for row in osm_rows), 3),
            "objects": osm_rows,
            "boundary": "SC-1 and Maidenhead each have multiple OSM objects. OSM object count therefore cannot be used as a facility, building or provider-ownership count.",
        },
        "unresolved_gaps": [
            "current_HTML_data_sheet_and_older_sheet_publication_conflict_resolution",
            "per_site_energized_leased_utilized_customer_accepted_and_billed_IT_load",
            "complete_building_parcel_property_title_and_lease_roster",
            "per_site_substation_transformer_switchgear_busbar_PDU_UPS_battery_generator_fuel_runtime_chiller_CRAH_CRAC_CDU_counts_ratings_topology_and_OEMs",
            "physical_GPU_model_count_owner_site_delivery_power_draw_utilization_customer_revenue_and_margin",
            "colocation_cloud_network_and_AI_revenue_operating_profit_capex_cash_flow_customer_concentration_site_economics_and_ROIC",
            "FY2025_post_acquisition_group_accounts_and_pro_forma_bridge",
            "per_site_measured_PUE_WUE_water_energy_emissions_and_hourly_renewable_matching",
            "two_unmatched_OSM_objects_and_seven_current_facilities_without_exact_public_map_crosswalk",
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
    registry_path = args.output_dir / "pulsant_official_facility_registry.jsonl"
    summary_path = args.output_dir / "pulsant_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "OSM_objects": len(osm_rows), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
