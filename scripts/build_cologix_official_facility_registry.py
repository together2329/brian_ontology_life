#!/usr/bin/env python3
"""Build Cologix's current facility-code registry and OSM crosswalk.

The current directory exposes 49 code pages, while company headlines say 45+
data centers.  Several codes share one street address and market copy uses still
other counts, so this builder preserves provider codes instead of pretending
they are 49 distinct physical buildings.  Current facility, power and cooling
claims are kept as selected page facts; design, available, installed and live
load are never summed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY_URL = "https://cologix.com/data-centers/"
ABOUT_URL = "https://cologix.com/about-us/"
ESG_URL = "https://cologix.com/wp-content/uploads/2025/07/Cologix_24ESG_Report_FA_070725-compressed.pdf"
COEVO_URL = "https://cologix.com/news/coevolution-inc-selects-cologix-as-canadian-hub-to-expand-gpu-as-a-service-deployments/"
STONEPEAK_RECAP_URL = "https://cologix.com/news/stonepeak-successfully-completes-3-0-billion-equity-recapitalization-portfolio-company-cologix/"
STONEPEAK_PORTFOLIO_URL = "https://stonepeak.com/investments"
ABS_2025_URL = "https://cologix.com/news/cologix-closes-525-million-usd-asset-backed-securitization-to-support-ai-infrastructure-interconnection-and-growth/"
ABS_2023_URL = "https://cologix.com/news/cologix-closes-195m-cad-in-second-canadian-asset-backed-securitization-transaction-since-2022/"
LA_CAISSE_URL = "https://www.lacaisse.com/en/news/pressreleases/caisse-invests-cad-240-million-advance-cologixs-ai-ready-mtl8-data-centre"
JOHNSTOWN_URL = "https://cologix.com/news/cologix-expands-central-ohio-footprint-with-land-acquisition-for-new-ai-ready-800mw-data-center-campus/"
ASHBURN_GROWTH_URL = "https://cologix.com/news/cologix-expands-ashburn-presence-with-strategic-land-acquisition-supporting-5b-long-term-northern-virginia-growth-plan/"
TORONTO_ACQUISITION_URL = "https://cologix.com/news/cologix-expands-investment-in-toronto-with-acquisition-of-cim-groups-interest-in-tor4-and-strategic-facility-acquisition-of-cim-groups-105-clegg-data-center/"


def facility(
    code: str,
    market: str,
    region: str,
    country_code: str,
    address: str,
    facility_facts: list[str],
    power_facts: list[str],
    cooling_facts: list[str],
    **extra: object,
) -> dict:
    market_slug = {
        "Ashburn": "ashburn", "Calgary": "calgary", "Columbus": "columbus",
        "Dallas": "dallas", "Des Moines": "des-moines", "Jacksonville": "jacksonville",
        "Lakeland": "lakeland", "Minneapolis": "minneapolis", "Montréal": "montreal",
        "New Jersey": "new-jersey", "Silicon Valley": "silicon-valley",
        "Toronto": "toronto", "Vancouver": "vancouver",
    }[market]
    return {
        "facility_code": code,
        "market": market,
        "region": region,
        "country_code": country_code,
        "address": address,
        "facility_url": f"https://cologix.com/data-centers/{market_slug}/{code.lower()}/",
        "lifecycle_as_of_2026_07_19": "current_marketed_facility_code_page",
        "current_page_technical_specs": {
            "facility": facility_facts,
            "power": power_facts,
            "cooling": cooling_facts,
        },
        **extra,
    }


FACILITIES = [
    facility("ASH1", "Ashburn", "VA", "US", "21745 Beaumeade Circle, Ashburn, VA",
             ["455K sq ft", "3-story concrete-and-steel building", "dedicated halls and large-scale suites"],
             ["scalable distributed-redundant architecture", "large-footprint-ready configurations"],
             ["closed-loop energy-efficient cooling", "mechanical galleries outside data halls"]),
    facility("ASH2", "Ashburn", "VA", "US", "21673 Beaumeade Circle, Ashburn, VA",
             ["99K sq ft on current facility page"],
             ["51 MW site capacity", "block-redundant design", "N+1 1.5-MW UPS blocks"],
             ["liquid cooling with dry coolers", "air cooling available", "closed loop"],
             source_conflict="Other Cologix marketing described a 226K-sq-ft building; the current code page shows 99K sq ft, so neither is silently substituted."),
    facility("CGY1", "Calgary", "AB", "CA", "840 7th Avenue SW, Calgary, AB",
             ["3.7K sq ft data-center space", "1.1K sq ft office"],
             ["400 kW", "N+1 UPS", "A+B distribution", "N+1 standby"],
             ["fault-tolerant air conditioning"]),
    facility("COL1", "Columbus", "OH", "US", "535 Scherers Court, Columbus, OH",
             ["44K sq ft", "9-acre campus"],
             ["30 MW utility available onsite", "three diverse utility feeds with self-healing utility", "up to 64 kW per cabinet and 90 kW special racks", "N+1 or 2(N+1)", "seven-day onsite fuel"],
             ["N+1 cooling", "50-ton VFD CRAHs", "320 tons installed and expandable to 1,350 tons"]),
    facility("COL2", "Columbus", "OH", "US", "555 Scherers Court, Columbus, OH",
             ["44K sq ft"],
             ["30 MW utility available onsite", "three utility feeds", "up to 64 kW per cabinet", "seven-day onsite fuel"],
             ["2N towers and chiller", "700 tons"]),
    facility("COL3", "Columbus", "OH", "US", "585 Scherers Court, Columbus, OH",
             ["200K+ sq ft", "four halls up to 20 MW"],
             ["2N electrical and N+1 mechanical", "two discrete substations", "four 750-kVA Mitsubishi UPS per hall per side", "2-MW Caterpillar generators on each side", "72-hour fuel"],
             ["770 tons per hall", "Liebert DSE"]),
    facility("COL4", "Columbus", "OH", "US", "7500 Alta View, Columbus, OH",
             ["256K sq ft", "current page: three halls and up to 33 MW"],
             ["1.5-MW UPS blocks", "distributed-redundant design"],
             ["chilled-water system", "free cooling"],
             source_conflict="An older release described 36 MW and eight halls; current page says 33 MW and three halls. The site also backs a 2025 USD525M ABS, which is financing rather than revenue or asset value."),
    facility("COL5", "Columbus", "OH", "US", "6787 Green Meadows Drive, Columbus, OH",
             ["60K sq ft", "one hall", "future additional facility and 95-MW expansion context"],
             ["25 MW utility", "MTU and Mitsubishi UPS", "5-100 kW per cabinet", "AEP-substation redundant loop"],
             ["air and liquid cooling", "closed-loop system"]),
    facility("COL7", "Columbus", "OH", "US", "12017 Duncan Plains Road, Johnstown, OH 43031",
             ["120K sq ft", "three Scalelogix halls and one Digital Edge hall", "36-MW headline"],
             ["block-redundant design", "N+1 1.5-MW generator-capacity wording on page"],
             ["liquid-to-chip ready", "air-cooled chillers", "closed loop"]),
    facility("COL8", "Columbus", "OH", "US", "11719 Duncan Plains Road, Johnstown, OH 43031",
             ["25K sq ft plus configurable shell", "21-MW headline"],
             ["block-redundant design", "N+1 1.5-MW generator-capacity wording on page"],
             ["configurable 70-90% liquid-cooled mix", "90°F+ (32°C+) liquid-to-chip water", "closed loop"],
             capability_boundary="The liquid-cooled mix is a configurable design range, not commissioned liquid-cooled load."),
    facility("DAL1", "Dallas", "TX", "US", "1950 North Stemmons Freeway, Dallas, TX",
             ["28K sq ft in the Infomart"],
             ["up to 8 kW per cabinet", "three utility substations", "two ATS and two UPS", "backup generator", "N/A+B distribution"],
             ["280-ton N+1 CRAC"]),
    facility("DAL2", "Dallas", "TX", "US", "1950 North Stemmons Freeway, Dallas, TX",
             ["12K sq ft in the Infomart"],
             ["up to 15 kW per cabinet", "2N UPS and generator", "four feeds from three substations"],
             ["N+1 chilled-water and in-row cooling", "600+ tons"]),
    facility("DAL3", "Dallas", "TX", "US", "1950 North Stemmons Freeway, Dallas, TX",
             ["13K sq ft in the Infomart"],
             ["up to 15 kW per cabinet", "2N UPS and generator", "four feeds from three substations"],
             ["N+1 chilled-water and in-row cooling", "600+ tons"]),
    facility("DSM1", "Des Moines", "IA", "US", "606 Walnut Street, Des Moines, IA",
             ["4K+ sq ft across two suites"],
             ["600 kW utility"],
             ["chilled-water and air cooling"]),
    facility("DSM2", "Des Moines", "IA", "US", "1205 Technology Parkway, Cedar Falls, IA",
             ["24K gross sq ft", "6K sq ft colocation plus 10K expansion"],
             ["1 MW", "three 750-kW generators and UPS"],
             ["glycol cooling"]),
    facility("JAX1", "Jacksonville", "FL", "US", "421 West Church Street, Jacksonville, FL",
             ["11K sq ft"],
             ["5 kW+ per cabinet", "2N UPS", "N+1 generator", "separate utility feeds including hospital-priority feed", "ATS"],
             ["N+1 dry-cool chillers and CRAC"]),
    facility("JAX2", "Jacksonville", "FL", "US", "4800 Spring Park Road, Jacksonville, FL",
             ["125K sq ft"],
             ["2N UPS", "N+1 generator"],
             ["N+1 direct-expansion cooling"]),
    facility("LAK1", "Lakeland", "FL", "US", "2850 Interstate Drive, Lakeland, FL",
             ["105K+ sq ft", "medium- and high-density configurations"],
             ["diverse entrances", "multiple generators", "redundant UPS and ATS", "separate city power", "dual feeds and two substations"],
             ["chilled water", "N+1 perimeter CRAC"]),
    facility("MIN1", "Minneapolis", "MN", "US", "511 11th Avenue South, Minneapolis, MN",
             ["9.5K sq ft"],
             ["three grids", "2N utility and A+B UPS", "N or 2N generators", "one substation, two transformers and third failover transformer", "5 kW per cabinet"],
             ["seven CRACs", "N+1 chilled water"]),
    facility("MIN2", "Minneapolis", "MN", "US", "511 11th Avenue South, Minneapolis, MN",
             ["8K sq ft"],
             ["5+ kW per cabinet", "three grids", "N or 2N", "one substation, two transformers and failover transformer"],
             ["N+1 CRAC and chilled water"]),
    facility("MIN3", "Minneapolis", "MN", "US", "511 11th Avenue South, Minneapolis, MN",
             ["28K sq ft"],
             ["N or 2N UPS", "2N generators", "three grids", "N+1 ATS"],
             ["600-ton N+1 chilled water", "N+1 CRAH"]),
    facility("MIN4", "Minneapolis", "MN", "US", "511 11th Avenue South, Minneapolis, MN",
             ["16K sq ft"],
             ["3.4 MW", "2N UPS", "three grids", "minimum N+1"],
             ["N+1 cooling", "cold-aisle containment"]),
    facility("MIN5", "Minneapolis", "MN", "US", "511 11th Avenue South, Minneapolis, MN",
             ["10K sq ft"],
             ["1.5 MW", "block-redundant UPS", "three grids", "minimum N+1"],
             ["N+1 HVAC", "air-cooled chiller and fan wall"]),
    facility("MTL1", "Montréal", "QC", "CA", "625 Boulevard René-Lévesque West, Montréal, QC",
             ["5K sq ft"],
             ["100 W per sq ft", "one substation and entrance", "300-kW backup", "Hydro-Québec", "primary UPS"],
             ["80-ton N+1 DX CRAC"]),
    facility("MTL2", "Montréal", "QC", "CA", "3000 Boulevard René-Lévesque, Verdun, QC",
             ["12K sq ft"],
             ["150 W per sq ft", "one substation and entrance", "N+1 or 2N generator", "primary or A+B options"],
             ["285-ton N+1 DX CRAC"]),
    facility("MTL3", "Montréal", "QC", "CA", "1250 Boulevard René-Lévesque West, Montréal, QC",
             ["33K sq ft"],
             ["100+ W per sq ft", "Hydro-Québec", "three APC Symmetra 500-kVA and two Mitsubishi 500-kVA UPS"],
             ["600-ton N+1 chillers", "CRAC and in-row cooling"]),
    facility("MTL4", "Montréal", "QC", "CA", "7171 Rue Jean-Talon East, Montréal, QC",
             ["12K sq ft"],
             ["150+ W per sq ft", "2N UPS and generators", "three feeds and ATS"],
             ["hot-aisle and perimeter CRAC", "in-row high-density cooling", "redundant chilled loop"]),
    facility("MTL5", "Montréal", "QC", "CA", "2351 Boulevard Alfred-Nobel, Montréal, QC",
             ["5K sq ft"],
             ["150 W per sq ft", "Hydro-Québec", "150-kVA Mitsubishi UPS", "single entrance and ATS"],
             ["44-ton N+1 CRAC"]),
    facility("MTL6", "Montréal", "QC", "CA", "2341 Boulevard Alfred-Nobel, Montréal, QC",
             ["10K sq ft"],
             ["100 W per sq ft", "three UPS", "single entrance and ATS", "page also lists one 80-kVA Powerware and two 150-kVA GE units under Cooling"],
             ["20-ton cooling"],
             page_taxonomy_boundary="The current page places renewable-hydro and UPS details in its Cooling section; the registry preserves the facts but does not treat them as cooling equipment."),
    facility("MTL7", "Montréal", "QC", "CA", "1155 Boulevard Robert-Bourassa, Montréal, QC",
             ["26K sq ft"],
             ["100 W per sq ft", "Hydro-Québec", "six Mitsubishi 500-kV units as written on page", "diverse entrances and ATS"],
             ["690 tons", "N+1 free cooling"],
             unit_boundary="The page's 500-kV UPS wording may be a kVA typo; it is preserved rather than corrected without a primary revision."),
    facility("MTL8", "Montréal", "QC", "CA", "7350 Frederick-Banting Street, Montréal, QC",
             ["206K sq ft", "LEED Gold", "extreme-density configurations up to 30 kW on page"],
             ["21 MW", "N, N+1 or 2N distributed architecture", "N+1 mechanical", "Hydro-Québec"],
             ["DX and free cooling", "N+1 chiller"]),
    facility("MTL9", "Montréal", "QC", "CA", "2525 Rue Canadien, Drummondville, QC",
             ["120K+ sq ft"],
             ["25 MW", "Hydro-Québec", "static UPS", "2N distribution"],
             ["DX and free cooling", "N+1"]),
    facility("MTL10", "Montréal", "QC", "CA", "530 Rue Bériault Street, Longueuil, QC",
             ["180K+ sq ft"],
             ["35 MW", "renewable hydro", "static UPS", "2N distribution"],
             ["DX and free cooling", "N+1"]),
    facility("MTL11", "Montréal", "QC", "CA", "875 Rue Saint-Antoine, Montréal, QC",
             ["25K+ sq ft"],
             ["1 MW", "1-MW Caterpillar 3512 generator", "two UPS in N+1", "A+B distribution"],
             ["600-ton Trane N+1"]),
    facility("MTL12", "Montréal", "QC", "CA", "3000 René-Lévesque Boulevard, Verdun, QC",
             ["8K+ sq ft"],
             ["N+1 or 2N generator"],
             ["N+1 cooling"]),
    facility("NNJ2", "New Jersey", "NJ", "US", "9 Wing Drive, Cedar Knolls, NJ",
             ["50K sq ft"],
             ["multiple 2(N+1) systems", "onsite diesel", "up to 20 kW per rack"],
             ["N+1 cooling"]),
    facility("NNJ3", "New Jersey", "NJ", "US", "200 Webro Road, Parsippany, NJ",
             ["120K sq ft"],
             ["four independent N+1 systems", "two mirrored UPS and diesel rooms", "onsite JCP&L substation", "up to 20 kW per rack"],
             ["N+1 ambient-air system", "chimney cooling"]),
    facility("NNJ4", "New Jersey", "NJ", "US", "16 Wing Drive, Cedar Knolls, NJ",
             ["disaster-recovery workspace rather than a conventional data-hall card"],
             ["resilient power", "independent UPS and diesel systems"],
             ["independent cooling"]),
    facility("SV1", "Silicon Valley", "CA", "US", "2050 Martin Ave, Santa Clara, CA",
             ["84K sq ft", "5 acres"],
             ["9 MW", "N+1 UPS", "three utility feeds", "15-MW generator backup", "4-15 kW per cabinet"],
             ["N+1", "free cooling"]),
    facility("TOR1", "Toronto", "ON", "CA", "151 Front Street West, Toronto, ON",
             ["25K sq ft"],
             ["up to 15 kW per cabinet", "150 W per sq ft", "N or 2N", "diverse entrances and ATS"],
             ["Enwave Deep Lake Water Cooling", "N+1 in-row cooling", "3,000 tons"]),
    facility("TOR2", "Toronto", "ON", "CA", "905 King Street West, Toronto, ON",
             ["20K sq ft"],
             ["150 W per sq ft", "more than 8 kW per cabinet", "up to 2N UPS and generator", "multiple generators"],
             ["N+1 chillers and tower", "in-row and hot-aisle cooling"]),
    facility("TOR3", "Toronto", "ON", "CA", "905 King Street West, Toronto, ON",
             ["20K sq ft"],
             ["2 MW A+B", "150 W per sq ft", "more than 8 kW per cabinet", "up to 2N"],
             ["N+1 chillers and tower", "in-row and hot-aisle cooling"]),
    facility("TOR4", "Toronto", "ON", "CA", "105 Clegg Road, Building B, Markham, ON",
             ["50K sq ft on current page", "approximately 1,000 cabinets"],
             ["11 MW on current page", "distributed-redundant design", "multiple generators"],
             ["CRAC with containment"],
             source_conflict="A 2023 completion release said 15 MW, while the 2025 TOR4+TOR5 acquisition release said more than 90K sq ft and 14 MW combined. These dated scopes are not treated as additive."),
    facility("TOR5", "Toronto", "ON", "CA", "105 Clegg Road, Markham, ON",
             ["Tier III designed", "40K+ sq ft plus 80K-sq-ft expansion", "approximately 1,000 cabinets"],
             ["3 MW hydro", "2.2 MW UPS installed and 3 MW expansion context", "three 1,100-kW UPS with ten-minute batteries", "four 1.5-MW N+1 generators with five-day fuel"],
             ["N+1", "Liebert CRAC", "district-energy plan"]),
    facility("VAN1", "Vancouver", "BC", "CA", "555 West Hastings Street, Vancouver, BC",
             ["5K sq ft"],
             ["13.8-kV primary and standby feeders", "redundant UPS", "ATS"],
             ["CRAC and glycol in-row", "rooftop dry coolers", "N+1", "50 tons"]),
    facility("VAN2", "Vancouver", "BC", "CA", "1050 West Pender Street, Vancouver, BC",
             ["15K sq ft"],
             ["2 MW", "N or A+B 2N UPS", "N+1 generators", "ATS"],
             ["free-cooling CRAC DX economizers", "N+1", "180 tons"]),
    facility("VAN3", "Vancouver", "BC", "CA", "2828 Natal Street, Vancouver, BC",
             ["42K sq ft", "Tier III", "largest network-neutral facility in Vancouver per Cologix"],
             ["5 MW", "up to 4 kW per cabinet", "N+1 electrical and mechanical"],
             ["hot-aisle containment", "efficient air cooling"],
             AI_context={"customer": "Coevolution Inc. (CoEvo)", "service": "GPU-as-a-Service", "deployment_change": "December 2024 release said server capacity doubled", "GPU_models_counts_owner_and_utilization": "undisclosed", "boundary": "Named customer deployment does not establish Cologix-owned GPU inventory or a facility fleet total.", "source_url": COEVO_URL}),
    facility("VAN4", "Vancouver", "BC", "CA", "175 West Cordova Street, Vancouver, BC",
             ["68K sq ft across four floors"],
             ["4 MW", "generator and UPS", "3-10 kW per cabinet"],
             ["pumped refrigerant", "air-cooled chilled water"]),
    facility("VAN5", "Vancouver", "BC", "CA", "555 West Hastings Street, Vancouver, BC",
             ["10.8K sq ft"],
             ["APC Symmetra PX N+1"],
             ["glycol DX", "rooftop dry coolers", "N+1"]),
]


OSM_TO_FACILITY = {
    "osm_way_129730212": "TOR4",
    "osm_node_10151456045": "MTL9",
    "osm_node_13604170384": "VAN1",
    "osm_node_13604170383": "VAN2",
    "osm_way_154377787": "VAN3",
    "osm_node_12634611897": "VAN4",
    "osm_node_13604170385": "VAN5",
    "osm_way_497151852": "JAX1",
    "osm_way_1188715510": "ASH1",
    "osm_way_40608200": "SV1",
}
UNRESOLVED_OSM_IDS = {"osm_way_1420458489"}


PORTFOLIO_CONTEXT = {
    "current_directory_code_pages": 49,
    "company_headline_data_centers_more_than": 45,
    "strategic_edge_markets": 13,
    "hyperscale_capacity_facilities": 7,
    "customers": 2000,
    "networks_more_than": 725,
    "cloud_providers_more_than": 350,
    "cloud_onramps_more_than": 35,
    "roster_boundary": "The 49 code pages are provider labels, not 49 proven physical buildings. DAL1-3, MIN1-5, TOR2-3 and other codes share addresses; 45+ is a company headline rather than an exact current physical roster.",
    "market_count_conflicts": {
        "Montreal": "current directory lists MTL1-MTL12 while market narrative says approximately 1M sq ft across 11 data centers",
        "Vancouver": "current directory lists VAN1-VAN5 while market narrative says four downtown facilities",
        "Canada": "a 2025 release reported 22 Canadian data centers, 1.057M sq ft and 94 MW; the current directory has 23 Canadian code pages after Calgary entered the portfolio",
    },
    "AI_and_accelerators": {
        "Cologix_owned_GPU_inventory_by_model_site_and_utilization": "undisclosed",
        "named_customer_deployment": "CoEvo GPU-as-a-Service at VAN3; December 2024 release says server capacity doubled",
        "named_customer_GPU_models_and_counts": "undisclosed",
        "boundary": "AI-ready design, density, liquid-cooling capability and a tenant GPU service are not Cologix-owned accelerator inventory or installed fleet utilization.",
    },
    "environment_2024": {
        "fleet_average_PUE": 1.486,
        "fleet_average_WUE": 0.203,
        "total_energy_consumed_kWh": 472018921,
        "grid_electricity_percent": 100,
        "carbon_free_energy_percent": 65,
        "square_feet_under_management": 2671469,
        "Scope_1_tCO2e": 69.44,
        "Scope_2_location_based_tCO2e": 89403,
        "Scope_2_market_based_tCO2e": 89244,
        "Scope_3_five_reported_categories_tCO2e": 82821.16,
        "environmental_capex_USD_million_more_than": 16.5,
        "environment_related_investment_since_2016_USD_million": 48,
        "water_boundary": "Most locations use closed-loop systems and Cologix says it does not actively track total water withdrawal and consumption; WUE is partly estimated from bills and employee averages where detailed data is unavailable.",
        "carbon_free_boundary": "65% includes energy billing totals supplied from local grids related to hydro, solar, wind and nuclear; it is not a renewable-only or hourly-additional matching metric.",
    },
    "ownership_and_finance": {
        "current_owner_context": "Stonepeak-managed continuation vehicles and investors; Stonepeak lists Cologix as a current investment",
        "Stonepeak_initial_majority_investment": "March 2017",
        "historic_2022_equity_recapitalization_USD_billion": 3.0,
        "historic_recap_boundary": "transaction value, not current enterprise value, revenue or operating profit; Mubadala exited and Madison International Realty participated, but exact current stakes and full cap table are undisclosed",
        "financing_events": ["USD1.13B inaugural US ABS in Dec 2021", "CAD883M ABS in Feb 2022", "CAD195M notes in Apr 2023", "USD525M five-year ABS backed by COL4 in Jul 2025", "CAD240M La Caisse senior financing for MTL8 in Mar 2026"],
        "financing_boundary": "Transactions use different currencies, dates, collateral and refinancing contexts and cannot be summed into current debt, valuation, revenue or earnings.",
        "current_revenue_operating_income_EBITDA_capex_debt_cash_flow_occupancy_customer_concentration_and_site_economics": "undisclosed",
    },
    "expansion": {
        "Johnstown_Central_Ohio": "approximately 154 acres, eight planned AI-ready data centers, potential 800 MW and 2.0M sq ft at full build, first phase expected to begin in 2025 and more than USD7B planned investment",
        "Northern_Virginia": "38-acre Beaumeade Circle acquisition supporting a USD5B long-term growth plan",
        "boundary": "Land, full-build potential and investment plans are not commissioned capacity, utilized load, committed spend or revenue. COL7/COL8 are not assumed to exhaust or equal the eight-building Johnstown plan without an official crosswalk.",
    },
}


COMMON_SOURCES = [
    DIRECTORY_URL, ABOUT_URL, ESG_URL, COEVO_URL, STONEPEAK_RECAP_URL,
    STONEPEAK_PORTFOLIO_URL, ABS_2025_URL, ABS_2023_URL, LA_CAISSE_URL,
    JOHNSTOWN_URL, ASHBURN_GROWTH_URL, TORONTO_ACQUISITION_URL,
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        combined = f"{row.get('name') or ''} {row.get('operator') or ''}".casefold()
        if "cologix" in combined:
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(FACILITIES) == 49
    assert len({row["facility_code"] for row in FACILITIES}) == 49
    assert len(candidates) == 11, [row["id"] for row in candidates]
    assert set(OSM_TO_FACILITY) | UNRESOLVED_OSM_IDS == {row["id"] for row in candidates}

    mapped: dict[str, list[dict]] = {}
    for object_id, code in OSM_TO_FACILITY.items():
        source = osm[object_id]
        mapped.setdefault(code, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": "OSM point or geometry is public map evidence, not provider-certified ownership, lifecycle, capacity, tenancy, building granularity or financial data.",
        })

    records = []
    for position, source in enumerate(FACILITIES, start=1):
        records.append({
            "id": f"cologix_{source['facility_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterFacilityCode",
            "source_order": position,
            "operator": "Cologix",
            "record_granularity": "provider_facility_code_not_necessarily_one_physical_building",
            **source,
            "osm_map_evidence": sorted(mapped.get(source["facility_code"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source["facility_url"], *COMMON_SOURCES])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def build_summary(records: list[dict], candidates: list[dict], osm: Path, accessed_on: str) -> dict:
    by_id = {json.loads(line)["id"]: json.loads(line) for line in osm.read_text(encoding="utf-8").splitlines()}
    mapped_count = sum(len(row["osm_map_evidence"]) for row in records)
    assert mapped_count == 10
    unresolved = []
    for object_id in sorted(UNRESOLVED_OSM_IDS):
        row = by_id[object_id]
        unresolved.append({
            "osm_object_id": object_id,
            "osm_name": row.get("name"),
            "osm_operator": row.get("operator"),
            "source_url": row["source_url"],
            "reason": "Montréal H4S 2A1 market object cannot be assigned to a current facility code without an explicit provider crosswalk.",
        })
    return {
        "registry": "Cologix current official facility-code directory and OSM crosswalk",
        "current_official_code_pages": len(records),
        "company_headline_data_centers_more_than": 45,
        "market_counts": dict(sorted(Counter(row["market"] for row in records).items())),
        "country_counts": dict(sorted(Counter(row["country_code"] for row in records).items())),
        "related_OSM_objects": len(candidates),
        "mapped_OSM_objects": mapped_count,
        "facility_codes_with_OSM_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "unmatched_related_OSM_objects": unresolved,
        "portfolio_context": PORTFOLIO_CONTEXT,
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum provider codes, shared-address suites, current page MW, utility power, planned capacity, financing, customer GPUs or OSM objects into one physical-building, live-load, accelerator, debt, valuation or revenue total.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/cologix_official_facility_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/cologix_official_facility_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()
    records, candidates = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, args.osm, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
