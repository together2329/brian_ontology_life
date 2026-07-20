#!/usr/bin/env python3
"""Build Csquare's SEC facility-row registry and current spec-sheet crosswalk.

The July 2026 final prospectus exposes 64 site rows, while the current website
markets fewer facility groups and OSM maps individual points, footprints and
legacy names.  This builder preserves those three granularities and never turns
utility, UPS, generator, sellable-power or contracted-power values into one sum.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


FINAL_PROSPECTUS = "https://www.sec.gov/Archives/edgar/data/2105398/000110465926084293/tm264837-15_424b4.htm"
SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK0002105398.json"
FORM_8K = "https://www.sec.gov/Archives/edgar/data/2105398/000110465926084616/tm264837d22_8k.htm"
IPO_RELEASE = "https://investor.csquare.com/news-releases/news-release-details/csquare-announces-pricing-initial-public-offering"
INVESTOR_RELEASES = "https://investor.csquare.com/press-releases"
SITEMAP = "https://www.csquare.com/sitemap.xml"


def row(label: str, sellable_sq_ft: int, sold_sq_ft: int | None, sold_percent: float, tenure: str) -> dict:
    clean = label.rstrip("*")
    market, site_id = clean.split("–", 1)
    return {
        "prospectus_label": label,
        "market": market,
        "site_id": site_id,
        "sellable_capacity_sq_ft": sellable_sq_ft,
        "sold_capacity_sq_ft": sold_sq_ft,
        "reported_sold_capacity_percent": sold_percent,
        "property_tenure": tenure.lower(),
        "slated_for_closure": label.endswith("*"),
    }


# Exact transcription of the final prospectus site table as of March 31, 2026.
# The source total for Sold Capacity is one square foot above the row checksum;
# both values are retained in the generated summary rather than silently fixed.
SEC_SITE_ROWS = [
    row("Boston–BOS1_A", 26162, 7516, 28.7, "Owned"),
    row("Boston–BOS4_A", 38979, 12826, 32.9, "Owned"),
    row("Chicago–ORD2_A", 110151, 71858, 65.2, "Owned"),
    row("Chicago–ORD4_A", 110066, 82196, 74.7, "Owned"),
    row("Columbus–CMH1_A", 20469, 17803, 87.0, "Owned"),
    row("Dallas–DFW1_A", 142851, 79487, 55.6, "Owned"),
    row("Dallas–DFW2_A", 44215, 23763, 53.7, "Owned"),
    row("Dallas–DFW3_A", 61380, 39204, 63.9, "Owned"),
    row("Dallas–DFW4_A", 16000, 16000, 100.0, "Owned"),
    row("Dallas–DFW5_A", 16000, 16000, 100.0, "Owned"),
    row("Denver–DEN1_A", 41717, 28583, 68.5, "Owned"),
    row("Minneapolis–MSP1_A", 17476, 15171, 86.8, "Owned"),
    row("Montreal–YUL1_A", 9011, 7463, 82.8, "Owned"),
    row("Montreal–YUL1_B", 9053, 9053, 100.0, "Owned"),
    row("Montreal–YUL2_A", 77200, 77200, 100.0, "Owned"),
    row("N. Virginia–IAD2_A", 49427, 27518, 55.7, "Owned"),
    row("N. Virginia–IAD3_A", 26110, 12530, 48.0, "Owned"),
    row("Nashville–BNA1_A", 40000, None, 0.0, "Owned"),
    row("Nashville–BNA2_A", 10000, 10000, 100.0, "Owned"),
    row("Nashville–BNA2_B", 16000, 16000, 100.0, "Owned"),
    row("New Jersey–EWR2_A", 136502, 73378, 53.8, "Owned"),
    row("New Jersey–EWR5_A", 59407, 47886, 80.6, "Owned"),
    row("Phoenix–PHX3_A", 49827, 33501, 67.2, "Owned"),
    row("Raleigh–RDU1_A", 10000, 10000, 100.0, "Owned"),
    row("Raleigh–RDU1_B", 12212, 12212, 100.0, "Owned"),
    row("Seattle–SEA2_A", 30998, 19786, 63.8, "Owned"),
    row("Seattle–SEA3_A", 37843, 28791, 76.1, "Owned"),
    row("Silicon Valley–SFO1_A", 60982, 39592, 64.9, "Owned"),
    row("Silicon Valley–SFO1_B", 38634, 24669, 63.9, "Owned"),
    row("Silicon Valley–SFO2_A", 45481, 40897, 89.9, "Owned"),
    row("Silicon Valley–SFO2_B", 56289, 53431, 94.9, "Owned"),
    row("Silicon Valley–SFO4_B", 35754, 35754, 100.0, "Owned"),
    row("Silicon Valley–SFO9_A", 33154, 5500, 16.6, "Owned"),
    row("Toronto–YYZ3_A", 38633, 33163, 85.8, "Owned"),
    row("Tulsa–TUL1_A", 16000, 16000, 100.0, "Owned"),
    row("Albuquerque–ABQ1_A", 13005, 3140, 24.1, "Leased"),
    row("Atlanta–ATL1_A", 56857, 50641, 89.1, "Leased"),
    row("Atlanta–ATL1_D", 50443, 31036, 61.5, "Leased"),
    row("Boston–BOS1_B", 24544, 14793, 60.3, "Leased"),
    row("Chicago–ORD1_A", 33032, 16866, 51.1, "Leased"),
    row("Chicago–ORD1_B", 26191, 23853, 91.1, "Leased"),
    row("Denver–DEN2_A", 27359, 24256, 88.7, "Leased"),
    row("London–LHR2_A*", 5764, 3077, 53.4, "Leased"),
    row("London–LHR2_B*", 7640, 4424, 57.9, "Leased"),
    row("London–LHR3_A", 39764, 32093, 80.7, "Leased"),
    row("Los Angeles–LAX3_A", 74498, 28546, 38.3, "Leased"),
    row("Los Angeles–LAX4_A*", 22984, 4138, 18.0, "Leased"),
    row("Los Angeles–LAX5_A", 53543, 34998, 65.4, "Leased"),
    row("N. Virginia–IAD1_A", 48031, 22443, 46.7, "Leased"),
    row("N. Virginia–IAD1_B", 37878, 18777, 49.6, "Leased"),
    row("N. Virginia–IAD1_C", 57444, 34706, 60.4, "Leased"),
    row("N. Virginia–IAD4_A", 58939, 45844, 77.8, "Leased"),
    row("New Jersey–EWR2_C", 75556, 64238, 85.0, "Leased"),
    row("New Jersey–EWR3_A", 48111, 27875, 57.9, "Leased"),
    row("Phoenix–PHX1_A", 24960, 22628, 90.7, "Leased"),
    row("Phoenix–PHX1_B", 15786, 15575, 98.7, "Leased"),
    row("Phoenix–PHX2_A", 23536, 23536, 100.0, "Leased"),
    row("Seattle–SEA1_A", 36905, 12761, 34.6, "Leased"),
    row("Seattle–SEA1_B", 39936, 30963, 77.5, "Leased"),
    row("Silicon Valley–SFO3_A", 19958, 16533, 82.8, "Leased"),
    row("Silicon Valley–SFO4_A", 21724, 18856, 86.8, "Leased"),
    row("Tampa–TPA1_A", 19409, 8023, 41.3, "Leased"),
    row("Toronto–YYZ1_A", 25597, 18105, 70.7, "Leased"),
    row("Toronto–YYZ2_A", 37382, 29409, 78.7, "Leased"),
]


def pdf_url(code: str) -> str:
    return f"https://www.csquare.com/hubfs/Centersquare%20website/docs/Csquare-{code}-SpecSheet.pdf"


def group(
    group_id: str,
    sec_site_ids: list[str],
    address: str | list[str],
    published_area: int,
    area_unit: str,
    utility_mw: float | None,
    ups_mw: float,
    generator_mw: float | None,
    chilled_water: bool,
    pdf_code: str,
    **extra: object,
) -> dict:
    return {
        "marketed_group_id": group_id,
        "sec_site_ids": sec_site_ids,
        "provider_published_address": address,
        "provider_published_total_area": published_area,
        "provider_published_total_area_unit": area_unit,
        "provider_published_utility_capacity_mw": utility_mw,
        "provider_published_ups_capacity_mw": ups_mw,
        "provider_published_generator_capacity_mw": generator_mw,
        "provider_published_chilled_water": chilled_water,
        "provider_published_vesda": True,
        "provider_published_pre_action_dry_pipe": True,
        "spec_sheet_url": pdf_url(pdf_code),
        **extra,
    }


# Current 2026 spec sheets cover 36 facility groups.  A group can cover several
# SEC site rows or physical buildings, so the values below are never allocated
# across those rows and are not summed with the 389-MW Sellable Power Capacity.
MARKETED_GROUPS = [
    group("ABQ1", ["ABQ1_A"], "400 Tijeras Avenue Northwest, Albuquerque, NM 87102", 12921, "sq_ft", 8.6, 1.8, 5, True, "ABQ"),
    group("ATL1", ["ATL1_A", "ATL1_D"], ["375 Riverside Parkway #100, Lithia Springs, GA 30122", "375 Riverside Parkway #200, Lithia Springs, GA 30122"], 102421, "sq_ft", 81.5, 9.2, 23.5, True, "ATL"),
    group("BOS1", ["BOS1_A", "BOS1_B"], ["580 Winter Street, Waltham, MA 02451", "115 2nd Avenue, Waltham, MA 02451"], 50150, "sq_ft", 38.2, 6.1, 11, False, "BOS", cooling_note="Chilled-water language was not present in the reviewed BOS1 card; absence is not proof of no chilled-water system."),
    group("BOS4", ["BOS4_A"], "486 Arsenal Way, Watertown, MA 02472", 38977, "sq_ft", 19.1, 4, 14, True, "BOS"),
    group("ORD1", ["ORD1_A", "ORD1_B"], "350 E Cermak Road, Chicago, IL 60616", 58893, "sq_ft", 32.8, 8.8, 16, True, "ORD"),
    group("ORD2", ["ORD2_A"], "2425 Busse Road, Elk Grove Village, IL 60007", 111906, "sq_ft", 25.9, 12.7, 22.8, False, "ORD"),
    group("ORD4", ["ORD4_A"], "4513 Western Avenue, Lisle, IL 60532", 66875, "sq_ft", 88.9, 3.6, 14, False, "ORD"),
    group("CMH1", ["CMH1_A"], "8180 Green Meadows Drive, Lewis Center, OH 43035", 18704, "sq_ft", 35.8, 1.8, 3.8, True, "CMH"),
    group("DFW1", ["DFW1_A"], "14901 FAA Boulevard, Fort Worth, TX 76155", 133298, "sq_ft", 51.9, 16.4, 24, True, "DFW"),
    group("DFW2", ["DFW2_A"], "900 Guardians Way, Allen, TX 75013", 43366, "sq_ft", 8.6, 14, 14, False, "DFW", anomaly="The provider publishes 14 MW of UPS capacity versus 8.6 MW of utility capacity; both values are retained without reinterpretation."),
    group("DFW3", ["DFW3_A"], "11830 Webb Chapel Road, Dallas, TX 75234", 61348, "sq_ft", 18.3, 4.8, 10, False, "DFW"),
    group("DEN1", ["DEN1_A"], "9110-9180 Commerce Center Circle, Littleton, CO 80129", 41593, "sq_ft", 18.3, 9.2, 15, True, "DEN"),
    group("DEN2", ["DEN2_A"], "8534 Concord Center Drive, Englewood, CO 80112", 21938, "sq_ft", 27.4, 3.8, 6, True, "DEN"),
    group("LHR3", ["LHR3_A"], "Eskdale Road, Winnersh Triangle, Wokingham RG41 5TS, United Kingdom", 2071, "sq_m", 15, 4.3, 6.4, True, "LHR", ai_and_liquid_cooling_center_of_excellence=True),
    group("LAX3", ["LAX3_A"], "17836 Gillette Avenue, Irvine, CA 92614", 73952, "sq_ft", 24.9, 9.2, 16, True, "LAX"),
    group("LAX5", ["LAX5_A"], "2681 Kelvin Avenue, Irvine, CA 92614", 52470, "sq_ft", 17.3, 5.6, 12, False, "LAX"),
    group("MSP1", ["MSP1_A"], "4450 Dean Lakes Boulevard, Shakopee, MN 55379", 28900, "sq_ft", 19.1, 2.4, 3.6, False, "MSP", anomaly="The 2026 PDF says 28,900 square feet, the reviewed HTML said 29,800, and the SEC table uses a separate 17,476-square-foot sellable-capacity denominator."),
    group("EWR2", ["EWR2_A", "EWR2_C"], ["300 JFK Boulevard East, Weehawken, NJ 07086", "1919 Park Avenue, Weehawken, NJ 07086"], 199110, "sq_ft", 45.7, 20.7, 31, True, "EWR"),
    group("EWR3", ["EWR3_A"], "3 Corporate Place, Piscataway, NJ 08854", 47490, "sq_ft", 54.8, 8.1, 14, True, "EWR"),
    group("EWR5", ["EWR5_A"], "15 Enterprise Avenue North, Secaucus, NJ 07094", 48867, "sq_ft", 26.3, 11.6, 16, True, "EWR", anomaly="The 2026 PDF says 48,867 square feet, the reviewed HTML said 59,572, and the SEC table uses a separate 59,407-square-foot sellable-capacity denominator."),
    group("IAD1", ["IAD1_A", "IAD1_B", "IAD1_C"], ["45901 Nokes Boulevard, Sterling, VA 20166", "45845 Nokes Boulevard, Sterling, VA 20166", "21110 Ridgetop Circle, Sterling, VA 20166"], 141621, "sq_ft", 143.2, 19.8, 37.5, True, "IAD"),
    group("IAD2", ["IAD2_A"], "22810-22860 International Drive, Sterling, VA 20166", 48169, "sq_ft", 35.8, 8.5, 20, False, "IAD"),
    group("IAD3", ["IAD3_A"], "22995 Wilder Court, Dulles, VA 20166", 21643, "sq_ft", 23.9, 2.9, 4.5, True, "IAD"),
    group("IAD4", ["IAD4_A"], ["21571 Beaumeade Circle, Ashburn, VA 20147", "21561 Beaumeade Circle, Ashburn, VA 20147"], 57927, "sq_ft", 35.8, 16.8, 20, True, "IAD"),
    group("PHX1", ["PHX1_A", "PHX1_B"], "615 N 48th Street, Phoenix, AZ 85008", 40456, "sq_ft", None, 13.3, None, True, "PHX", anomaly="The current PDF leaves utility and generator capacity undisclosed; they are not inferred from UPS capacity."),
    group("PHX3", ["PHX3_A"], "1301 W University Drive, Mesa, AZ 85201", 50256, "sq_ft", 17.3, 8, 11.5, False, "PHX"),
    group("SEA1", ["SEA1_A", "SEA1_B"], ["12301 Tukwila International Boulevard, Tukwila, WA 98168", "3355 S 120th Place, Tukwila, WA 98168"], 75776, "sq_ft", 109, 10.8, 19.5, False, "SEA"),
    group("SEA2", ["SEA2_A"], "6101 S 180th Street, Tukwila, WA 98188", 29279, "sq_ft", 8.6, 2.9, 10, True, "SEA"),
    group("SEA3", ["SEA3_A"], "17300 Highway 99, Lynnwood, WA 98037", 21371, "sq_ft", 17.3, 1.8, 6, False, "SEA"),
    group("SFO1", ["SFO1_A", "SFO1_B"], ["2401 Walsh Avenue, Santa Clara, CA 95051", "2403 Walsh Avenue, Santa Clara, CA 95051"], 95981, "sq_ft", 34.5, 11.2, 17.5, False, "SFO"),
    group("SFO2", ["SFO2_A", "SFO2_B"], ["4700 Old Ironsides Drive, Santa Clara, CA 95054", "4650 Old Ironsides Drive, Santa Clara, CA 95054"], 100056, "sq_ft", 43.2, 14.1, 22.5, True, "SFO"),
    group("SFO3", ["SFO3_A"], "1400 Kifer Road, Sunnyvale, CA 94086", 19661, "sq_ft", 8.6, 3.2, 5, True, "SFO"),
    group("SFO4", ["SFO4_A", "SFO4_B"], ["1500 Space Park Drive, Santa Clara, CA 95054", "1550 Space Park Drive, Santa Clara, CA 95054"], 57450, "sq_ft", 43.1, 12.3, 20.5, True, "SFO"),
    group("TPA1", ["TPA1_A"], "9310 Florida Palm Drive, Tampa, FL 33619", 19245, "sq_ft", 9, 2.5, 9, True, "TPA"),
    group("YYZ1", ["YYZ1_A"], "6800 Millcreek Drive, Mississauga, ON L5N 4J9, Canada", 2368, "sq_m", 19.1, 3.2, 5.5, False, "YYZ"),
    group("YYZ2", ["YYZ2_A"], "4175 14th Avenue, Markham, ON L3R 5R5, Canada", 3450, "sq_m", 28.7, 4.3, 9, True, "YYZ"),
]


OSM_TO_GROUP = {
    "osm_way_1317915930": "IAD4", "osm_way_460175666": "IAD4", "osm_way_300163074": "IAD4",
    "osm_way_713410334": "ATL1", "osm_node_10910879065": "ORD1", "osm_way_377345296": "ORD2",
    "osm_way_52094270": "IAD1", "osm_way_52094269": "IAD1", "osm_way_52094294": "IAD1",
    "osm_way_273896089": "IAD2", "osm_way_273896102": "IAD2", "osm_way_273895868": "IAD3",
    "osm_way_530024353": "ORD4", "osm_way_396296733": "SEA3", "osm_way_193612533": "EWR5",
    "osm_way_543117031": "PHX3", "osm_way_254773897": "DFW2",
    "osm_way_322816286": "YYZ1", "osm_way_974334074": "YYZ2", "osm_way_279410762": "EWR2",
    "osm_way_25706343": "DFW1", "osm_way_523886201": "TPA1",
}


OSM_IDENTITY_NOTES = {
    "osm_way_1317915930": "Overall IAD4 footprint plus two sub-footprints map to one SEC site row; no extra legal site is invented.",
    "osm_way_396296733": "OSM calls the Lynnwood object SE1; current provider address and SEC roster support SEA3, so the legacy code is retained as an anomaly.",
    "osm_way_193612533": "OSM calls the Secaucus object NYC3; current provider address and SEC roster support EWR5.",
    "osm_way_543117031": "OSM calls the Mesa object PHX1; current provider address and SEC roster support PHX3.",
    "osm_way_254773897": "OSM retains the legacy Evoque Allen DA1 name; current provider address and SEC roster support DFW2.",
    "osm_way_279410762": "OSM retains a Cyxtera/Digital Realty name; city and address support the current EWR2 group, but ownership is not inferred from OSM.",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    operator_rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        source = json.loads(line)
        by_id[source["id"]] = source
        if source.get("operator") in {"Centersquare", "Cyxtera"}:
            operator_rows.append(source)
    return by_id, operator_rows


def country_code(site_id: str) -> str:
    if site_id.startswith(("YUL", "YYZ")):
        return "CA"
    if site_id.startswith("LHR"):
        return "GB"
    return "US"


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, operator_rows = load_osm(osm_path)
    assert len(operator_rows) == 22, len(operator_rows)
    assert set(OSM_TO_GROUP) == {source["id"] for source in operator_rows}
    groups = {source["marketed_group_id"]: source for source in MARKETED_GROUPS}
    site_to_group: dict[str, str] = {}
    for source in MARKETED_GROUPS:
        for site_id in source["sec_site_ids"]:
            assert site_id not in site_to_group, site_id
            site_to_group[site_id] = source["marketed_group_id"]
    group_osm: dict[str, list[dict]] = {}
    for object_id, group_id in OSM_TO_GROUP.items():
        source = osm[object_id]
        group_osm.setdefault(group_id, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "source_url": source["source_url"],
            "identity_note": OSM_IDENTITY_NOTES.get(object_id),
            "boundary": "Public map point or footprint; not provider-certified ownership, lifecycle, legal site count or capacity.",
        })
    group_heads = {source["sec_site_ids"][0] for source in MARKETED_GROUPS}
    records = []
    for position, source in enumerate(SEC_SITE_ROWS, start=1):
        site_id = source["site_id"]
        group_id = site_to_group.get(site_id)
        marketed_group = groups.get(group_id)
        record = {
            "id": f"csquare_{slug(site_id)}",
            "object_type": "SECDisclosedDataCenterSiteRow",
            "source_order": position,
            "operator": "Csquare, Inc.",
            **source,
            "country_code": country_code(site_id),
            "source_date": "2026-03-31",
            "record_granularity": "final_prospectus_site_row_not_proven_one_to_one_building_or_current_marketing_card",
            "sellable_capacity_definition": "Colocation space that is built out and available for sale, measured in square feet; it is not gross building area, occupied area, rack count or IT MW.",
            "marketed_group_ref": group_id,
            "marketed_group_details": marketed_group if site_id in group_heads else None,
            "marketed_group_scope_note": "Technical values apply to the provider's full marketed group and are not allocated to individual SEC rows." if marketed_group else "No current reviewed spec-sheet group was located for this SEC site row.",
            "osm_map_evidence_for_marketed_group": group_osm.get(group_id, []) if site_id in group_heads else [],
            "gpu_inventory": {
                "exact_installed_model_count_owner_site_allocation_delivery_state_utilization_power_draw_revenue_and_margin": "undisclosed",
                "boundary": "Customers deploy hardware. AI/HPC contract mix, rack-density capability and liquid-cooling capability do not establish a Csquare-owned physical GPU fleet.",
            },
            "source_urls": list(dict.fromkeys([FINAL_PROSPECTUS, SEC_SUBMISSIONS] + ([marketed_group["spec_sheet_url"]] if marketed_group else []))),
            "accessed_on": accessed_on,
        }
        records.append(record)
    return records, operator_rows


def build_summary(records: list[dict], operator_rows: list[dict], accessed_on: str) -> dict:
    sold_checksum = sum(row["sold_capacity_sq_ft"] or 0 for row in records)
    owned = [row for row in records if row["property_tenure"] == "owned"]
    leased = [row for row in records if row["property_tenure"] == "leased"]
    market_counts = Counter(row["market"] for row in records if not row["slated_for_closure"])
    expected_market_counts = {
        "Albuquerque": 1, "Atlanta": 2, "Boston": 3, "Chicago": 4, "Columbus": 1,
        "Dallas": 5, "Denver": 2, "London": 1, "Los Angeles": 2, "Minneapolis": 1,
        "Montreal": 3, "N. Virginia": 6, "Nashville": 3, "New Jersey": 4,
        "Phoenix": 4, "Raleigh": 2, "Seattle": 4, "Silicon Valley": 8,
        "Tampa": 1, "Toronto": 3, "Tulsa": 1,
    }
    assert dict(market_counts) == expected_market_counts, dict(market_counts)
    return {
        "schema_version": 1,
        "registry": "Csquare final-prospectus site-row registry with current spec-sheet and OSM crosswalk",
        "accessed_on": accessed_on,
        "identity_and_transaction": {
            "legal_name": "Csquare, Inc.",
            "ticker": "CSQR",
            "exchange": "NYSE",
            "initial_public_offering_priced_on": "2026-07-16",
            "initial_public_offering_closed_on": "2026-07-17",
            "shares_offered": 50000000,
            "price_per_share_usd": 21,
            "gross_proceeds_usd": 1050000000,
            "estimated_net_proceeds_usd": 1010000000,
            "brookfield_post_offering_voting_control_percent": 69.0,
            "boundary": "Net proceeds were primarily earmarked for debt repayment; the offering is not treated as data-center revenue or growth capex.",
            "sources": [FINAL_PROSPECTUS, FORM_8K, IPO_RELEASE],
        },
        "sec_site_rows": len(records),
        "continuing_site_rows_excluding_three_slated_closures": sum(not row["slated_for_closure"] for row in records),
        "slated_for_closure_site_ids": [row["site_id"] for row in records if row["slated_for_closure"]],
        "major_metropolitan_markets": len(market_counts),
        "continuing_site_rows_by_market": expected_market_counts,
        "tenure_counts": dict(sorted(Counter(row["property_tenure"] for row in records).items())),
        "owned_site_rows": len(owned),
        "leased_site_rows": len(leased),
        "reported_total_sellable_capacity_sq_ft": 2570759,
        "row_checksum_sellable_capacity_sq_ft": sum(row["sellable_capacity_sq_ft"] for row in records),
        "reported_total_sold_capacity_sq_ft": 1726865,
        "row_checksum_sold_capacity_sq_ft": sold_checksum,
        "sold_capacity_checksum_difference_sq_ft": 1726865 - sold_checksum,
        "reported_total_sold_capacity_percent": 67.2,
        "owned_reported_sellable_capacity_sq_ft": 1543983,
        "owned_row_checksum_sellable_capacity_sq_ft": sum(row["sellable_capacity_sq_ft"] for row in owned),
        "owned_reported_sold_capacity_sq_ft": 1044732,
        "owned_row_checksum_sold_capacity_sq_ft": sum(row["sold_capacity_sq_ft"] or 0 for row in owned),
        "leased_reported_sellable_capacity_sq_ft": 1026776,
        "leased_row_checksum_sellable_capacity_sq_ft": sum(row["sellable_capacity_sq_ft"] for row in leased),
        "leased_reported_sold_capacity_sq_ft": 682133,
        "leased_row_checksum_sold_capacity_sq_ft": sum(row["sold_capacity_sq_ft"] or 0 for row in leased),
        "capacity_as_of_2026_03_31": {
            "sellable_power_capacity_mw": 389,
            "contracted_power_capacity_mw": 392,
            "reported_contracted_power_sold_percent": 101,
            "boundary": "Sellable Power Capacity is installed critical IT load available for customer use and excludes development. Contracted Power Capacity and the 101% ratio reflect contracting, including overbooking, and are not physical utilization or actual load.",
        },
        "dated_power_history": {
            "2023": {"sellable_mw": 61, "contracted_mw": 48, "contracted_power_sold_percent": 78},
            "2024": {"sellable_mw": 297, "contracted_mw": 263, "contracted_power_sold_percent": 88},
            "2025": {"sellable_mw": 389, "contracted_mw": 376, "contracted_power_sold_percent": 97},
            "2026_Q1": {"sellable_mw": 389, "contracted_mw": 392, "contracted_power_sold_percent": 101},
        },
        "current_marketed_spec_sheet_groups": len(MARKETED_GROUPS),
        "current_marketed_group_ids": [row["marketed_group_id"] for row in MARKETED_GROUPS],
        "current_marketing_residual": {
            "legal_rows_without_reviewed_current_spec_group": [row["site_id"] for row in records if row["marketed_group_ref"] is None],
            "boundary": "The current spec sheets omit acquired Montreal, Nashville, Raleigh and Tulsa rows plus several facility IDs. Their omission is not treated as closure; only the prospectus asterisks establish the three reviewed closure states.",
        },
        "spec_sheet_power_boundary": "Utility, UPS and generator nameplates include different redundancy and service scopes, are not critical IT load, and are not summed across groups or added to 389 MW.",
        "osm_operator_tagged_objects": len(operator_rows),
        "osm_operator_label_counts": dict(sorted(Counter(row.get("operator") for row in operator_rows).items())),
        "osm_crosswalked_objects": len(OSM_TO_GROUP),
        "osm_crosswalked_marketed_groups": len(set(OSM_TO_GROUP.values())),
        "osm_boundary": "OSM points, overall footprints and sub-footprints can overlap; object count is not a facility or building count.",
        "ai_hpc_and_gpu_boundary": {
            "customers": "more_than_1700",
            "interconnection_products": "more_than_36600",
            "average_contracted_kw_per_rack": 7.6,
            "operated_deployments_up_to_kw_per_rack": 150,
            "design_capability_beyond_kw_per_rack": 250,
            "air_cooling_capability_up_to_kw_per_rack_approximate": 50,
            "liquid_cooling_capability_up_to_kw_per_rack_approximate": 250,
            "largest_2025_deals_ai_hpc_related_approximate_percent": 80,
            "q1_2026_mrr_ai_hpc_approximate_percent": 15,
            "company_ai_hpc_definition": "Known AI company, or more than 24 kW per rack, or management knows the deployment is AI-related.",
            "exact_installed_physical_gpu_inventory": "undisclosed",
            "warning": "The commercial AI/HPC classification is broader than verified GPU hardware and cannot be converted into GPU count, model, owner, utilization or site allocation.",
            "source": FINAL_PROSPECTUS,
        },
        "expansion_capacity": {
            "potential_existing_site_capacity_mw_approximate": 670,
            "equipment_optimization_mw_approximate": 330,
            "under_roof_expansion_mw_approximate": 340,
            "target_net_cost_usd_per_mw_range": [4000000, 8000000],
            "target_payback_years_less_than": 5,
            "boundary": "Potential and target measures are not energized, contracted, customer-accepted, utilized or revenue-generating capacity.",
        },
        "financial_profile_ref": "company_csquare",
        "portfolio_profile_ref": "dc_csquare_north_america_uk_portfolio",
        "source_urls": [FINAL_PROSPECTUS, SEC_SUBMISSIONS, FORM_8K, IPO_RELEASE, INVESTOR_RELEASES, SITEMAP],
        "records_sha256": canonical_hash(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("life/imports/global_data_centers_20260717"))
    args = parser.parse_args()
    records, operator_rows = build_records(args.osm, args.accessed_on)
    assert len(records) == 64
    assert len({row["site_id"] for row in records}) == 64
    assert len(MARKETED_GROUPS) == 36
    assert sum(row["sellable_capacity_sq_ft"] for row in records) == 2570759
    assert sum(row["sold_capacity_sq_ft"] or 0 for row in records) == 1726864
    assert Counter(row["property_tenure"] for row in records) == {"owned": 35, "leased": 29}
    summary = build_summary(records, operator_rows, args.accessed_on)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry_path = args.output_dir / "csquare_official_facility_registry.jsonl"
    summary_path = args.output_dir / "csquare_official_facility_summary.json"
    registry_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(registry_path), "summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
