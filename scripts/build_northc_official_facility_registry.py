#!/usr/bin/env python3
"""Build NorthC's official Northwest European facility-label registry.

NorthC's directory exposes 27 labels, while the March 2026 owner announcement
describes a 25-data-center network.  Basel 3 and Geneva are explicit future
developments, and several labels share one page, address, or capacity figure.
This builder keeps those scopes separate and joins the reviewed labels to the
local OSM baseline without treating a point or outline as an operating building.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path


DIRECTORY_URL = "https://www.northcdatacenters.com/en/northc-datacenters/"
ACQUISITION_URL = "https://www.northcdatacenters.com/en/news/antin-completes-acquisition-of-northc-datacenters/"
ALMERE_INCIDENT_URL = "https://www.northcdatacenters.com/en/news/fire-in-our-data-center-in-almere/"
EXPANSION_URL = "https://www.northcdatacenters.com/nieuws/update-uitbreidingen-datacenter-april26/"
GENEVA_URL = "https://www.northcdatacenters.com/en/news/northc-group-to-build-new-high-tech-data-center-in-geneva-switzerland/"
BASEL3_URL = "https://www.northcdatacenters.com/en/news/new-data-center-uptown-basel-campus/"
COLT_CLOSE_URL = "https://www.northcdatacenters.com/en/news/northc-completes-acquisition-of-six-data-centers-from-colt-technology-services/"
AI_CASE_URL = "https://www.northcdatacenters.com/en/cases/ai-startup-juvoly-relies-on-northc-for-sovereign-hosting/"
NVIDIA_DGX_URL = "https://docs.nvidia.com/dgx/dgxb200-user-guide/introduction-to-dgxb200.html"
LEGRAND_CASE_URL = "https://www.northcdatacenters.com/en/cases/legrand-and-northc-enable-ai-hpc/"
SUSTAINABILITY_URL = "https://www.northcdatacenters.com/en/sustainability/"


def facility(
    code: str,
    label: str,
    country_code: str,
    market: str,
    address: str,
    lifecycle: str,
    location_url: str,
    installed_electrical_mw: float | None = None,
    area_sqm: int | None = None,
    **extra: object,
) -> dict:
    return {
        "facility_code": code,
        "facility_label": label,
        "country_code": country_code,
        "market": market,
        "address": address,
        "lifecycle_as_of_2026_07_19": lifecycle,
        "location_url": location_url,
        "current_marketed_installed_electrical_capacity_mw": installed_electrical_mw,
        "published_area_sqm": area_sqm,
        **extra,
    }


FACILITIES = [
    facility("NL_AALSMEER", "Aalsmeer", "NL", "Aalsmeer", "Lakenblekerstraat 13, 1431 GE Aalsmeer", "operating", f"{DIRECTORY_URL}aalsmeer/", 14, 14700, equipment={"utility": "3 x 10 kV, N+1", "UPS": "dynamic rotary UPS, N+2", "cooling": "redundant chilled water free cooling with cooling towers, N+1"}),
    facility("NL_ALMERE", "Almere", "NL", "Almere", "Rondebeltweg 62, 1329 BG Almere", "operating_recovery_latest_public_status", f"{DIRECTORY_URL}almere/", 11, 26000, equipment={"utility": "150 kV with 2 x 150 kV transformers", "UPS": "dynamic rotary UPS, N+2", "cooling": "redundant chilled water free cooling with cooling towers, N+2"}, incident_boundary="A 7 May 2026 fire affected building 1. The latest public update dated 8 July said partial grid restoration and planned full grid reconnection on 17 July; no later public confirmation or final root-cause report was found by the access date."),
    facility("NL_AMSTERDAM", "Amsterdam", "NL", "Amsterdam", "Kabelweg 48a, 1014 BB Amsterdam", "operating", f"{DIRECTORY_URL}amsterdam/", 2.4, 5000),
    facility("NL_AMSTERDAM_2", "Amsterdam 2", "NL", "Amsterdam", "Stekkenbergweg 4, 1105 AJ Amsterdam", "operating_with_upgrade", f"{DIRECTORY_URL}amsterdam-2/", 3.44, equipment={"current_power": "single feeds; UPS 3.44 MW; Tier 2 generators 4 x 1.7 MVA", "current_cooling_density_w_per_m2": 866, "future_power": "distributed redundant N+1; UPS 3.8 MW", "future_cooling_density_w_per_m2": 1000}, future_marketed_capacity_mw=3.8, upgrade_timing="second 2 MW room targeted for 2027 H1"),
    facility("NL_OUDE_MEER", "Oude Meer", "NL", "Oude Meer", "Fokker Logistics Park, Gebouw 59, Fokkerweg 300, 1438 AN Oude Meer", "operating", f"{DIRECTORY_URL}oude-meer/", 4.8, 18000),
    facility("NL_DELFT", "Delft", "NL", "Delft", "Heertjeslaan 1, 2629 JG Delft", "operating", f"{DIRECTORY_URL}delft/", 1.5, 5000),
    facility("NL_ROTTERDAM_WAALHAVEN", "Rotterdam Waalhaven", "NL", "Rotterdam", "Anthony Fokkerweg 40, 3088 GG Rotterdam", "operating", f"{DIRECTORY_URL}rotterdam-waalhaven/", 0.5, 1000),
    facility("NL_ROTTERDAM_ZESTIENHOVEN_1", "Rotterdam Zestienhoven 1", "NL", "Rotterdam", "Tempelhof 5-11, 3045 PV Rotterdam", "operating", f"{DIRECTORY_URL}rotterdam-zestienhoven/", shared_page_group="rotterdam_zestienhoven_1_2", shared_page_capacity_mw=7.3, shared_page_area_sqm=10800),
    facility("NL_ROTTERDAM_ZESTIENHOVEN_2", "Rotterdam Zestienhoven 2", "NL", "Rotterdam", "Tempelhof 5-11, 3045 PV Rotterdam", "operating", f"{DIRECTORY_URL}rotterdam-zestienhoven/", shared_page_group="rotterdam_zestienhoven_1_2", shared_page_capacity_mw=7.3, shared_page_area_sqm=10800),
    facility("NL_EINDHOVEN_1", "Eindhoven 1", "NL", "Eindhoven", "High Tech Campus 53, 5656 AG Eindhoven", "operating", f"{DIRECTORY_URL}eindhoven/", 2.4, 2500, design_context="Tier 4 standards"),
    facility("NL_EINDHOVEN_2", "Eindhoven 2", "NL", "Eindhoven", "De Schakel 35, 5651 GH Eindhoven", "operating_with_recent_expansion_status_unconfirmed", f"{DIRECTORY_URL}eindhoven-2/", 4.5, 4000, expansion_boundary="A separate 1.5 MW expansion was expected at end-May 2026, but completion was not independently confirmed in the reviewed current evidence."),
    facility("NL_GRONINGEN_1", "Groningen 1", "NL", "Groningen", "Liverpoolweg 10, 9744 TW Groningen", "operating", f"{DIRECTORY_URL}groningen/", 1.2, shared_page_group="groningen_1_2", shared_page_area_sqm=5300, equipment={"utility": "2 x 20 kV, N+1 shared context", "UPS": "N+1", "generator": "2N", "cooling": "direct cooling; 7 LSV units with redundant cooling"}),
    facility("NL_GRONINGEN_2", "Groningen 2", "NL", "Groningen", "Liverpoolweg 10, 9744 TW Groningen", "operating", f"{DIRECTORY_URL}groningen/", 1.5, shared_page_group="groningen_1_2", shared_page_area_sqm=5300, equipment={"utility": "2 x 20 kV, N+1 shared context", "UPS": "N+1", "generator": "N+1 with one hydrogen fuel cell and one diesel generator", "cooling": "redundant chilled-water free cooling with four cooling systems, N+1"}),
    facility("NL_NIEUWEGEIN", "Nieuwegein", "NL", "Nieuwegein", "Frieslandhaven 6, 3433 PC Nieuwegein", "operating", f"{DIRECTORY_URL}nieuwegein/", 2.5, 8000),
    facility("DE_BERLIN_2", "Berlin 2", "DE", "Berlin", "Gradestraße 60, 12347 Berlin", "operating_with_upgrade", f"{DIRECTORY_URL}berlin-2/", 0.9, equipment={"current_power": "single feeds; factsheet lists UPS systems 4 MW and Tier 2 generators 2 x 2 MVA", "future_power": "distributed redundant feeds; UPS 5 MW; Tier 3 generators 3 x 2 MVA", "cooling_density_w_per_m2_current_to_future": [750, 2400]}, future_marketed_capacity_mw=4, source_anomaly="The factsheet's current 4 MW UPS figure exceeds its 0.9 MW installed-electrical headline and is retained without correction."),
    facility("DE_DUSSELDORF", "Düsseldorf", "DE", "Düsseldorf", "In der Steele 37A, 40559 Düsseldorf", "operating_with_upgrade", f"{DIRECTORY_URL}dusseldorf/", 1.3, equipment={"current_power": "single feeds; UPS 1 MW; Tier 2 generator 1 x 2.5 MVA", "future_power": "distributed redundant feeds; UPS 6 MW; Tier 3 generators 3 x 2.5 MVA", "cooling_density_w_per_m2_current_to_future": [750, 2400]}, future_marketed_capacity_mw=6),
    facility("DE_FRANKFURT_3", "Frankfurt 3", "DE", "Frankfurt", "Rüsselsheimer Straße 22, 60326 Frankfurt", "operating_with_upgrade", f"{DIRECTORY_URL}frankfurt-3/", 0.9, equipment={"current_power": "single feeds; UPS 2 MW; Tier 2 generators 2 x 2 MVA", "future_power": "distributed redundant feeds; UPS 2 MW; Tier 3 generators 2 x 2 MVA", "cooling_density_w_per_m2_current_to_future": [750, 2400]}, future_marketed_capacity_mw=1.3),
    facility("DE_HAMBURG", "Hamburg", "DE", "Hamburg", "Süderstraße 198, 20537 Hamburg", "operating_with_upgrade", f"{DIRECTORY_URL}hamburg/", 1.17, equipment={"current_power": "single feeds; Tier 2 generators 2 x 2 MVA", "future_power": "distributed redundant feeds; Tier 3 generators 4 x 2 MVA", "cooling_density_w_per_m2_current_to_future": [750, 2400]}, future_marketed_capacity_mw=4.1),
    facility("DE_MUNICH_1", "Munich 1", "DE", "Munich", "Balanstrasse 73 Building 23, 81541 Munich", "operating", f"{DIRECTORY_URL}munich/", 2, 5000),
    facility("DE_MUNICH_2", "Munich 2", "DE", "Munich", "Wamslerstraße 8, 81829 Munich", "operating_with_upgrade", f"{DIRECTORY_URL}munich-2/", 1.17, equipment={"current_power": "Tier 2 generators 2 x 2 MVA", "future_power": "Tier 3 generators 4 x 2 MVA"}, future_marketed_capacity_mw=4.5),
    facility("DE_NUREMBERG", "Nuremberg", "DE", "Nuremberg", "Am Tower 5, 90475 Nürnberg", "operating", f"{DIRECTORY_URL}nuremberg/", 6, 10500),
    facility("CH_BIEL", "Biel (Bern)", "CH", "Biel / Bern", "Tennisweg 6, 2504 Biel/Bienne", "operating", f"{DIRECTORY_URL}biel-bern/", 4, 3380, environmental_context={"marketed_PUE_below": 1.3, "cooling": "redundant chilled-water free cooling"}),
    facility("CH_BASEL_1", "Münchenstein (Basel) 1", "CH", "Basel", "Weidenstrasse 41, 4142 Münchenstein", "operating", f"{DIRECTORY_URL}muenchenstein-basel-1/", 6, 3500, equipment={"utility": "13.6 kV, 2N", "UPS": "2N", "generator": "N+1", "cooling": "redundant chilled-water free cooling with cooling towers, N+1", "high_density_kW": 22}, environmental_context={"marketed_PUE_below": 1.24}),
    facility("CH_BASEL_2", "Münchenstein (Basel) 2", "CH", "Basel", "Weidenstrasse 13, 4142 Münchenstein", "operating", f"{DIRECTORY_URL}muenchenstein-basel-2/", 0.6, 1000, equipment={"transformer": "1 x 630 kVA", "diesel_generators": "2 x 360 kW", "UPS": "2 independent systems, 2 x 324 kW", "cooling": "redundant chilled-water free cooling with cooling towers, N+1"}, environmental_context={"marketed_PUE_below": 1.35}),
    facility("CH_BASEL_3", "Münchenstein (Basel) 3", "CH", "Basel / Arlesheim", "Schorenweg 21, 4144 Arlesheim", "development", f"{DIRECTORY_URL}munchenstein-basel-3/", future_marketed_capacity_mw=7.5, development_context={"first_phase_IT_load_mw": 3, "construction_expected": "2026 H2", "availability_expected": 2027, "design_PUE_at_most": 1.2, "AI_HPC_and_heat_reuse_ready": True}, source_conflict="An earlier announcement described 6 MVA and a 2,500 sqm first phase; the later April 2026 update describes 3 MW IT load and 7.5 MW total. Units and dates remain separate."),
    facility("CH_WINTERTHUR", "Winterthur (Zurich)", "CH", "Winterthur / Zurich", "Theaterstrasse 15c, 8400 Winterthur", "operating", f"{DIRECTORY_URL}winterthur-zurich/", 1.8, 1100, equipment={"utility": "11 kV redundant supply", "transformers": "2 x 1,600 kVA, expandable to 4 x 1,600 kVA", "diesel_generators": "2 x 3,100 kVA", "UPS": "2 x 2 x 400 kVA, expandable to 2 x 5 x 400 kVA", "cooling": "chillers with liquid and air free cooling, N+1"}, environmental_context={"marketed_PUE_below": 1.35}),
    facility("CH_GENEVA", "Geneva", "CH", "Geneva / Meyrin", "Rte du Nant-d’Avril 152, 1217 Meyrin", "development", GENEVA_URL, area_sqm=5400, future_marketed_capacity_mw=4.5, development_context={"modules_mw": 1.5, "construction_start": "2026 Q1", "completion_expected": "2028 Q2", "power": "100% green electricity", "backup_generation": "HVO100", "cooling": "water-free and direct-to-chip liquid cooling ready", "heat_reuse": "nearby campus buildings and potential district-heating network"}),
]


OSM_TO_FACILITY = {
    "osm_way_1081882891": "CH_BIEL",
    "osm_way_750275669": "CH_BASEL_1",
    "osm_way_195293320": "DE_BERLIN_2",
    "osm_node_13574591148": "DE_DUSSELDORF",
    "osm_way_248865761": "DE_FRANKFURT_3",
    "osm_way_34990467": "DE_HAMBURG",
    "osm_node_13574491231": "DE_MUNICH_1",
    "osm_way_27100275": "DE_MUNICH_2",
    "osm_node_4242731538": "DE_NUREMBERG",
    "osm_way_1081886104": "NL_GRONINGEN_1",
    "osm_node_3918634315": "NL_EINDHOVEN_1",
    "osm_node_11426879977": "NL_EINDHOVEN_2",
    "osm_way_263802879": "NL_ALMERE",
    "osm_node_2765259404": "NL_AALSMEER",
    "osm_node_4177046902": "NL_DELFT",
    "osm_node_11386475042": "NL_OUDE_MEER",
    "osm_way_1205462692": "NL_ROTTERDAM_WAALHAVEN",
    "osm_node_2738247376": "NL_AMSTERDAM",
    "osm_node_13574644223": "NL_NIEUWEGEIN",
    "osm_node_13574615961": "NL_ROTTERDAM_ZESTIENHOVEN_1",
    "osm_node_2862656047": "NL_AMSTERDAM_2",
}


PORTFOLIO_CONTEXT = {
    "owner_reported_current_network_data_centers": 25,
    "directory_facility_labels": 27,
    "secured_gross_grid_capacity_mw_more_than": 140,
    "secured_grid_scope": "current facilities plus upcoming greenfield developments; not live, IT, leased, utilized or billed load",
    "customers_more_than": 1600,
    "former_Colt_sites_acquired": 6,
    "former_Colt_additional_capacity_mw_more_than": 25,
    "unlisted_development_context": {
        "Frankfurt_region_new_build_IT_load_mw": 16,
        "Frankfurt_new_build_data_centers": 3,
        "Berlin": "former Berliner Zeitung print facility redevelopment; permits and design in progress",
        "Aalsmeer_phase_2_mw": 2.4,
        "Aalsmeer_phase_2_connection_target": "2027 Q1",
        "Amsterdam_2_second_room_mw": 2,
        "Amsterdam_2_second_room_target": "2027 H1",
    },
    "accelerators": {
        "NorthC_owned_GPU_inventory": "undisclosed",
        "Juvoly_at_undisclosed_Rotterdam_facility": {"NVIDIA_DGX_B200_systems": 2, "B200_GPUs_per_system": 8, "derived_B200_GPU_count": 16, "derived_total_GPU_memory_GB": 2880, "hardware_owner": "Juvoly_customer"},
        "readiness_not_inventory": ["NVIDIA H100", "NVIDIA H200", "NVIDIA L40S", "NVIDIA DGX B200", "approximately 100 kW AI rack context"],
        "boundary": "The exact Rotterdam building, rack, network topology, utilization, power draw and NorthC service economics are undisclosed. Compatibility claims are not installed fleet counts.",
    },
    "environment": {
        "green_electricity_claim_percent": 100,
        "carbon_neutral_target_year": 2030,
        "current_fleet_measured_PUE_WUE_water_energy_and_emissions": "undisclosed",
        "dated_2019_PUE_baseline": 1.54,
        "2030_PUE_goal_below": 1.2,
        "heat_reuse_examples": ["Aalsmeer daycare, plant exporter and swimming pool", "Eindhoven High Tech Campus", "planned Rotterdam Schiebroek network for approximately 10,000 homes"],
        "Groningen_hydrogen_boundary": "A 500 kW fuel-cell module and one-hydrogen-plus-one-diesel N+1 topology are disclosed, but publications cite both 39 t and more than 78 t CO2 avoided under apparently different scopes; neither is silently selected as one result.",
    },
    "ownership_and_finance": {
        "current_completed_acquirer": "Antin Infrastructure Partners",
        "seller": "DWS and minority shareholders",
        "APG_stake_percent_agreed": 37.5,
        "APG_regulatory_clearance": "European Commission joint-control clearance in June 2026; exact stake closing not confirmed in reviewed sources",
        "transaction_price_and_enterprise_value": "undisclosed",
        "standalone_revenue_operating_profit_EBITDA_net_income_capex_debt_cash_flow": "undisclosed",
        "historical_DWS_financing_eur_million": [282, 125],
        "historical_financing_boundary": "The 2021 and 2023 financings cannot be added into current debt; the 2023 amount included cleaning down a EUR75m capex facility and EUR50m of near-term prefunding.",
    },
}


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_osm(path: Path) -> tuple[dict[str, dict], list[dict]]:
    by_id: dict[str, dict] = {}
    candidates: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        by_id[row["id"]] = row
        if "northc" in (row.get("operator") or "").casefold() or "northc" in (row.get("name") or "").casefold():
            candidates.append(row)
    return by_id, candidates


def build_records(osm_path: Path, accessed_on: str) -> tuple[list[dict], list[dict]]:
    osm, candidates = load_osm(osm_path)
    assert len(FACILITIES) == 27
    assert len({row["facility_code"] for row in FACILITIES}) == 27
    assert len(candidates) == 21, [row["id"] for row in candidates]
    assert set(OSM_TO_FACILITY) == {row["id"] for row in candidates}

    mapped: dict[str, list[dict]] = {}
    for object_id, code in OSM_TO_FACILITY.items():
        source = osm[object_id]
        mapping_boundary = "OSM point or footprint; not provider-certified lifecycle, capacity, ownership, tenant or revenue evidence."
        if object_id == "osm_way_750275669":
            mapping_boundary += " The outline is a shared Basel-area campus signal and is not allocated between Basel 1 and Basel 2."
        if object_id in {"osm_way_1081886104", "osm_node_13574615961"}:
            mapping_boundary += " The object represents a shared two-label page or campus and is attached once to avoid double counting."
        mapped.setdefault(code, []).append({
            "osm_object_id": object_id,
            "osm_name": source.get("name"),
            "osm_operator": source.get("operator"),
            "latitude": source["latitude"],
            "longitude": source["longitude"],
            "footprint_area_m2": source.get("footprint_area_m2"),
            "source_url": source["source_url"],
            "boundary": mapping_boundary,
        })

    common_sources = [DIRECTORY_URL, ACQUISITION_URL, ALMERE_INCIDENT_URL, EXPANSION_URL, GENEVA_URL, BASEL3_URL, COLT_CLOSE_URL, AI_CASE_URL, NVIDIA_DGX_URL, LEGRAND_CASE_URL, SUSTAINABILITY_URL]
    records = []
    for position, source in enumerate(FACILITIES, start=1):
        records.append({
            "id": f"northc_{source['facility_code'].lower()}",
            "object_type": "ProviderPublishedDataCenterFacilityLabel",
            "source_order": position,
            "operator": "NorthC",
            "record_granularity": "provider_facility_label_not_physical_building",
            **source,
            "osm_map_evidence": sorted(mapped.get(source["facility_code"], []), key=lambda row: row["osm_object_id"]),
            "portfolio_context": PORTFOLIO_CONTEXT,
            "source_urls": list(dict.fromkeys([source["location_url"], *common_sources])),
            "accessed_on": accessed_on,
        })
    return records, candidates


def current_capacity_checksum(records: list[dict]) -> float:
    individual = sum(row["current_marketed_installed_electrical_capacity_mw"] or 0 for row in records)
    shared: dict[str, float] = {}
    for row in records:
        if row.get("shared_page_capacity_mw") is not None:
            shared[row["shared_page_group"]] = row["shared_page_capacity_mw"]
    return round(individual + sum(shared.values()), 2)


def build_summary(records: list[dict], candidates: list[dict], accessed_on: str) -> dict:
    lifecycles = Counter(row["lifecycle_as_of_2026_07_19"] for row in records)
    countries = Counter(row["country_code"] for row in records)
    checksum = current_capacity_checksum(records)
    assert checksum == 82.88, checksum
    assert sum(len(row["osm_map_evidence"]) for row in records) == 21
    current_labels = [row for row in records if row["lifecycle_as_of_2026_07_19"] != "development"]
    return {
        "registry": "NorthC official Northwest European facility-label and OSM crosswalk",
        "official_directory_facility_labels": len(records),
        "owner_reported_current_network_data_centers": 25,
        "current_or_recovery_labels": len(current_labels),
        "explicit_development_labels": 2,
        "unique_official_location_or_development_pages": len({row["location_url"] for row in records}),
        "lifecycle_counts": dict(sorted(lifecycles.items())),
        "country_counts": dict(sorted(countries.items())),
        "current_directory_marketed_installed_electrical_capacity_checksum_mw": checksum,
        "capacity_checksum_boundary": "The 82.88 MW checksum de-duplicates shared Zestienhoven capacity and sums Groningen's disclosed 1.2/1.5 MW split. It is marketed installed electrical capacity, not IT load, live load, utilization or the more-than-140-MW secured gross-grid scope.",
        "related_osm_objects": len(candidates),
        "OSM_country_counts": dict(sorted(Counter((row.get("country_candidates") or [{}])[0].get("iso2") for row in candidates).items())),
        "labels_or_shared_groups_with_osm_evidence": sum(bool(row["osm_map_evidence"]) for row in records),
        "GPU_disclosure": PORTFOLIO_CONTEXT["accelerators"],
        "ownership_and_financial_boundary": PORTFOLIO_CONTEXT["ownership_and_finance"],
        "records_sha256": canonical_hash(records),
        "comparison_boundary": "Do not sum label, page, shared-campus, building, current, upgrade, development, gross-grid, apparent-power, installed-electrical, IT-load, GPU-readiness or customer-owned hardware measures.",
        "accessed_on": accessed_on,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, default=Path("life/imports/global_data_centers_20260717/osm_data_center_locations.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("life/imports/global_data_centers_20260717/northc_official_facility_registry.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("life/imports/global_data_centers_20260717/northc_official_facility_summary.json"))
    parser.add_argument("--accessed-on", default=dt.date.today().isoformat())
    args = parser.parse_args()

    records, candidates = build_records(args.osm, args.accessed_on)
    summary = build_summary(records, candidates, args.accessed_on)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "registry": str(args.registry), "summary": str(args.summary)}))


if __name__ == "__main__":
    main()
